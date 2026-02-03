"""
Skill Gap Analysis Service - ML-powered skill gap detection.

Analyzes the gap between a candidate's skills and job requirements:
1. Semantic skill matching (not just exact string matching)
2. Proficiency level detection
3. Skill category coverage
4. Learning recommendations
5. Alternative skills recognition
"""

import json
import logging
import re
import httpx
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime

from ..config import settings
from ..schemas.candidate import ParsedResume

logger = logging.getLogger("pathway.skill_gap")


# Skill synonyms and related skills for semantic matching
SKILL_SYNONYMS = {
    # Programming Languages
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "python": ["py", "python3"],
    "golang": ["go"],
    "c++": ["cpp", "cplusplus"],
    "c#": ["csharp", "dotnet", ".net"],

    # Web Frameworks
    "react": ["reactjs", "react.js", "react js"],
    "vue": ["vuejs", "vue.js", "vue js"],
    "angular": ["angularjs", "angular.js"],
    "next.js": ["nextjs", "next"],
    "node.js": ["nodejs", "node"],
    "express": ["expressjs", "express.js"],
    "django": ["django rest framework", "drf"],
    "flask": ["flask-restful"],
    "fastapi": ["fast api"],
    "spring": ["spring boot", "springboot"],

    # Databases
    "postgresql": ["postgres", "psql", "pg"],
    "mysql": ["mariadb"],
    "mongodb": ["mongo"],
    "redis": ["redis cache"],
    "elasticsearch": ["elastic", "es"],

    # Cloud & DevOps
    "aws": ["amazon web services", "amazon cloud"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure", "azure cloud"],
    "kubernetes": ["k8s"],
    "docker": ["containers", "containerization"],
    "ci/cd": ["continuous integration", "continuous deployment", "cicd"],

    # Data & ML
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "neural networks"],
    "tensorflow": ["tf"],
    "pytorch": ["torch"],
    "pandas": ["dataframes"],
    "scikit-learn": ["sklearn"],
    "natural language processing": ["nlp"],
    "computer vision": ["cv", "image recognition"],

    # Concepts
    "rest api": ["restful", "rest apis", "rest"],
    "graphql": ["graph ql"],
    "microservices": ["micro services", "micro-services"],
    "agile": ["scrum", "kanban"],
}

# Related/transferable skills
RELATED_SKILLS = {
    "python": ["java", "ruby", "javascript"],  # If they know Python, these are learnable
    "react": ["vue", "angular", "svelte"],
    "aws": ["gcp", "azure"],
    "postgresql": ["mysql", "oracle", "sql server"],
    "tensorflow": ["pytorch", "keras"],
    "kubernetes": ["docker swarm", "ecs", "nomad"],
}

# Skill categories for gap analysis
SKILL_CATEGORIES = {
    "programming_languages": {
        "skills": ["python", "javascript", "typescript", "java", "c++", "go", "rust", "c#", "ruby", "php", "swift", "kotlin"],
        "importance": "high",
        "description": "Core programming languages"
    },
    "frontend": {
        "skills": ["react", "vue", "angular", "html", "css", "tailwind", "sass", "webpack", "next.js"],
        "importance": "high",
        "description": "Frontend development"
    },
    "backend": {
        "skills": ["node.js", "django", "flask", "fastapi", "spring", "express", "rails", "laravel"],
        "importance": "high",
        "description": "Backend frameworks"
    },
    "databases": {
        "skills": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra", "sqlite"],
        "importance": "high",
        "description": "Database technologies"
    },
    "cloud_infrastructure": {
        "skills": ["aws", "gcp", "azure", "terraform", "cloudformation", "pulumi"],
        "importance": "medium",
        "description": "Cloud platforms and infrastructure"
    },
    "devops": {
        "skills": ["docker", "kubernetes", "jenkins", "github actions", "gitlab ci", "circleci", "ansible"],
        "importance": "medium",
        "description": "DevOps and CI/CD"
    },
    "data_ml": {
        "skills": ["machine learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "spark", "airflow"],
        "importance": "high",
        "description": "Data science and ML"
    },
    "soft_skills": {
        "skills": ["communication", "leadership", "teamwork", "problem solving", "project management"],
        "importance": "medium",
        "description": "Soft skills"
    }
}

# Proficiency level indicators
PROFICIENCY_INDICATORS = {
    "expert": {
        "years": 5,
        "keywords": ["expert", "architect", "lead", "principal", "senior", "designed", "built from scratch"],
        "score": 5
    },
    "advanced": {
        "years": 3,
        "keywords": ["advanced", "proficient", "extensive", "scaled", "optimized"],
        "score": 4
    },
    "intermediate": {
        "years": 1,
        "keywords": ["intermediate", "experienced", "worked with", "developed", "implemented"],
        "score": 3
    },
    "beginner": {
        "years": 0,
        "keywords": ["beginner", "familiar", "basic", "learning", "coursework", "exposure"],
        "score": 2
    },
    "none": {
        "years": 0,
        "keywords": [],
        "score": 0
    }
}


@dataclass
class SkillMatch:
    """Result of matching a candidate skill to a requirement."""
    requirement: str
    requirement_category: str
    matched: bool
    candidate_skill: Optional[str] = None  # The skill that matched
    match_type: str = "none"  # exact, synonym, related, partial, none
    proficiency_level: str = "none"  # expert, advanced, intermediate, beginner, none
    proficiency_score: int = 0  # 0-5
    evidence: List[str] = field(default_factory=list)  # Where this skill appears
    years_experience: Optional[float] = None


@dataclass
class SkillGapAnalysis:
    """Complete skill gap analysis result."""
    # Summary
    overall_match_score: float  # 0-100
    total_requirements: int
    matched_requirements: int
    critical_gaps: List[str]  # Missing high-importance skills

    # Detailed matches
    skill_matches: List[Dict[str, Any]]

    # Category analysis
    category_coverage: Dict[str, Dict[str, Any]]  # {category: {matched, total, score}}

    # Proficiency analysis
    proficiency_distribution: Dict[str, int]  # {level: count}
    avg_proficiency_score: float  # 0-5

    # Recommendations
    learning_priorities: List[Dict[str, Any]]  # Skills to learn with priority
    alternative_skills: List[Dict[str, Any]]  # Candidate skills that could substitute
    transferable_skills: List[str]  # Related skills that show potential

    # Strengths
    bonus_skills: List[str]  # Skills beyond requirements
    strongest_areas: List[str]


class SkillGapService:
    """Service for analyzing skill gaps between candidates and job requirements."""

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"

    def analyze_skill_gap(
        self,
        candidate_skills: List[str],
        job_requirements: List[str],
        parsed_resume: Optional[ParsedResume] = None,
        github_data: Optional[Dict[str, Any]] = None
    ) -> SkillGapAnalysis:
        """
        Analyze the gap between candidate skills and job requirements.

        Args:
            candidate_skills: List of candidate's skills
            job_requirements: List of required skills for the job
            parsed_resume: Optional parsed resume for context
            github_data: Optional GitHub data for additional skill evidence

        Returns:
            SkillGapAnalysis with detailed gap information
        """
        # Normalize all skills
        normalized_candidate_skills = self._normalize_skills(candidate_skills)
        normalized_requirements = self._normalize_skills(job_requirements)

        # Extract skills from resume context
        resume_context = self._extract_resume_context(parsed_resume) if parsed_resume else {}

        # Extract skills from GitHub
        github_skills = self._extract_github_skills(github_data) if github_data else set()

        # Combine all candidate skills
        all_candidate_skills = normalized_candidate_skills | github_skills

        # Analyze each requirement
        skill_matches = []
        matched_count = 0
        critical_gaps = []
        proficiency_counts = {"expert": 0, "advanced": 0, "intermediate": 0, "beginner": 0, "none": 0}
        total_proficiency = 0

        for req in normalized_requirements:
            match = self._match_skill(
                req,
                all_candidate_skills,
                resume_context,
                github_data
            )
            skill_matches.append(asdict(match))

            if match.matched:
                matched_count += 1
                proficiency_counts[match.proficiency_level] += 1
                total_proficiency += match.proficiency_score
            else:
                proficiency_counts["none"] += 1
                # Check if this is a critical gap
                category = self._get_skill_category(req)
                if category and SKILL_CATEGORIES.get(category, {}).get("importance") == "high":
                    critical_gaps.append(req)

        # Calculate category coverage
        category_coverage = self._analyze_category_coverage(
            normalized_requirements,
            skill_matches
        )

        # Calculate overall match score
        if normalized_requirements:
            base_match_score = (matched_count / len(normalized_requirements)) * 100
            # Adjust for proficiency
            avg_proficiency = total_proficiency / len(normalized_requirements) if normalized_requirements else 0
            proficiency_bonus = (avg_proficiency / 5) * 20  # Up to 20 points bonus
            overall_score = min(100, base_match_score * 0.8 + proficiency_bonus)
        else:
            overall_score = 100
            avg_proficiency = 0

        # Generate recommendations
        learning_priorities = self._generate_learning_priorities(
            skill_matches,
            critical_gaps
        )

        alternative_skills = self._find_alternative_skills(
            skill_matches,
            all_candidate_skills
        )

        transferable_skills = self._find_transferable_skills(
            all_candidate_skills,
            set(normalized_requirements)
        )

        # Find bonus skills
        bonus_skills = self._find_bonus_skills(
            all_candidate_skills,
            set(normalized_requirements)
        )

        # Identify strongest areas
        strongest_areas = self._identify_strongest_areas(
            skill_matches,
            proficiency_counts
        )

        return SkillGapAnalysis(
            overall_match_score=round(overall_score, 1),
            total_requirements=len(normalized_requirements),
            matched_requirements=matched_count,
            critical_gaps=critical_gaps[:5],  # Top 5 critical gaps
            skill_matches=skill_matches,
            category_coverage=category_coverage,
            proficiency_distribution=proficiency_counts,
            avg_proficiency_score=round(avg_proficiency, 2),
            learning_priorities=learning_priorities[:5],  # Top 5 priorities
            alternative_skills=alternative_skills[:5],
            transferable_skills=transferable_skills[:5],
            bonus_skills=bonus_skills[:10],
            strongest_areas=strongest_areas[:3]
        )

    def _normalize_skills(self, skills: List[str]) -> set:
        """Normalize skill names for comparison."""
        normalized = set()
        for skill in skills:
            if skill:
                # Lowercase and strip
                skill_lower = skill.lower().strip()
                # Remove common suffixes
                skill_lower = re.sub(r'\s*(experience|knowledge|skills?|proficiency)$', '', skill_lower)
                normalized.add(skill_lower)
        return normalized

    def _extract_resume_context(self, parsed_resume: ParsedResume) -> Dict[str, Any]:
        """Extract skill context from resume."""
        context = {
            "skill_mentions": {},  # skill -> [where mentioned]
            "years_by_skill": {},  # skill -> estimated years
        }

        # Extract from experience
        for exp in (parsed_resume.experience or []):
            exp_text = " ".join([
                exp.description or "",
                *[h for h in (exp.highlights or [])]
            ]).lower()

            # Calculate years for this experience
            years = self._estimate_years(exp.start_date, exp.end_date)

            # Find skills mentioned
            for category, cat_info in SKILL_CATEGORIES.items():
                for skill in cat_info["skills"]:
                    if skill in exp_text or self._skill_in_text(skill, exp_text):
                        if skill not in context["skill_mentions"]:
                            context["skill_mentions"][skill] = []
                        context["skill_mentions"][skill].append(f"experience:{exp.company or 'unknown'}")
                        context["years_by_skill"][skill] = context["years_by_skill"].get(skill, 0) + years

        # Extract from projects
        for proj in (parsed_resume.projects or []):
            proj_text = " ".join([
                proj.description or "",
                *[t for t in (proj.technologies or [])],
                *[h for h in (proj.highlights or [])]
            ]).lower()

            for category, cat_info in SKILL_CATEGORIES.items():
                for skill in cat_info["skills"]:
                    if skill in proj_text or self._skill_in_text(skill, proj_text):
                        if skill not in context["skill_mentions"]:
                            context["skill_mentions"][skill] = []
                        context["skill_mentions"][skill].append(f"project:{proj.name or 'unknown'}")

        return context

    def _extract_github_skills(self, github_data: Dict[str, Any]) -> set:
        """Extract skills from GitHub data."""
        skills = set()

        # From languages
        if github_data.get("languages"):
            for lang in github_data["languages"]:
                lang_lower = lang.lower()
                skills.add(lang_lower)

        # From repos
        for repo in (github_data.get("repos") or github_data.get("top_repos") or []):
            if repo.get("language"):
                skills.add(repo["language"].lower())

            # Parse topics/description for frameworks
            desc = (repo.get("description") or "").lower()
            for category, cat_info in SKILL_CATEGORIES.items():
                for skill in cat_info["skills"]:
                    if skill in desc:
                        skills.add(skill)

        return skills

    def _skill_in_text(self, skill: str, text: str) -> bool:
        """Check if skill or its synonyms are in text."""
        if skill in text:
            return True

        # Check synonyms
        synonyms = SKILL_SYNONYMS.get(skill, [])
        for syn in synonyms:
            if syn in text:
                return True

        return False

    def _match_skill(
        self,
        requirement: str,
        candidate_skills: set,
        resume_context: Dict[str, Any],
        github_data: Optional[Dict[str, Any]]
    ) -> SkillMatch:
        """Match a single requirement against candidate skills."""
        req_lower = requirement.lower()

        # Check for exact match
        if req_lower in candidate_skills:
            proficiency, score = self._determine_proficiency(req_lower, resume_context)
            evidence = resume_context.get("skill_mentions", {}).get(req_lower, [])
            years = resume_context.get("years_by_skill", {}).get(req_lower)

            return SkillMatch(
                requirement=requirement,
                requirement_category=self._get_skill_category(req_lower) or "other",
                matched=True,
                candidate_skill=req_lower,
                match_type="exact",
                proficiency_level=proficiency,
                proficiency_score=score,
                evidence=evidence,
                years_experience=years
            )

        # Check synonyms
        synonyms = SKILL_SYNONYMS.get(req_lower, [])
        for syn in synonyms:
            if syn in candidate_skills:
                proficiency, score = self._determine_proficiency(syn, resume_context)
                return SkillMatch(
                    requirement=requirement,
                    requirement_category=self._get_skill_category(req_lower) or "other",
                    matched=True,
                    candidate_skill=syn,
                    match_type="synonym",
                    proficiency_level=proficiency,
                    proficiency_score=score,
                    evidence=resume_context.get("skill_mentions", {}).get(syn, [])
                )

        # Check if requirement is a synonym of something candidate has
        for skill in candidate_skills:
            skill_synonyms = SKILL_SYNONYMS.get(skill, [])
            if req_lower in skill_synonyms:
                proficiency, score = self._determine_proficiency(skill, resume_context)
                return SkillMatch(
                    requirement=requirement,
                    requirement_category=self._get_skill_category(req_lower) or "other",
                    matched=True,
                    candidate_skill=skill,
                    match_type="synonym",
                    proficiency_level=proficiency,
                    proficiency_score=score,
                    evidence=resume_context.get("skill_mentions", {}).get(skill, [])
                )

        # Check for related skills
        for skill in candidate_skills:
            related = RELATED_SKILLS.get(skill, [])
            if req_lower in [r.lower() for r in related]:
                # Candidate has a related skill, partial match
                proficiency, score = self._determine_proficiency(skill, resume_context)
                # Reduce score for related match
                return SkillMatch(
                    requirement=requirement,
                    requirement_category=self._get_skill_category(req_lower) or "other",
                    matched=True,
                    candidate_skill=skill,
                    match_type="related",
                    proficiency_level=proficiency,
                    proficiency_score=max(1, score - 1),  # Reduce score
                    evidence=resume_context.get("skill_mentions", {}).get(skill, [])
                )

        # Check for partial match (skill contained in another)
        for skill in candidate_skills:
            if req_lower in skill or skill in req_lower:
                proficiency, score = self._determine_proficiency(skill, resume_context)
                return SkillMatch(
                    requirement=requirement,
                    requirement_category=self._get_skill_category(req_lower) or "other",
                    matched=True,
                    candidate_skill=skill,
                    match_type="partial",
                    proficiency_level=proficiency,
                    proficiency_score=max(1, score - 1),
                    evidence=resume_context.get("skill_mentions", {}).get(skill, [])
                )

        # No match found
        return SkillMatch(
            requirement=requirement,
            requirement_category=self._get_skill_category(req_lower) or "other",
            matched=False,
            match_type="none",
            proficiency_level="none",
            proficiency_score=0
        )

    def _determine_proficiency(
        self,
        skill: str,
        resume_context: Dict[str, Any]
    ) -> Tuple[str, int]:
        """Determine proficiency level for a skill."""
        years = resume_context.get("years_by_skill", {}).get(skill, 0)
        mentions = resume_context.get("skill_mentions", {}).get(skill, [])

        # Check years of experience
        if years >= 5:
            return "expert", 5
        elif years >= 3:
            return "advanced", 4
        elif years >= 1:
            return "intermediate", 3
        elif mentions:
            return "beginner", 2
        else:
            return "beginner", 1

    def _get_skill_category(self, skill: str) -> Optional[str]:
        """Get the category for a skill."""
        skill_lower = skill.lower()

        for category, cat_info in SKILL_CATEGORIES.items():
            if skill_lower in cat_info["skills"]:
                return category

            # Check synonyms
            for cat_skill in cat_info["skills"]:
                if skill_lower in SKILL_SYNONYMS.get(cat_skill, []):
                    return category

        return None

    def _analyze_category_coverage(
        self,
        requirements: set,
        skill_matches: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze coverage by skill category."""
        coverage = {}

        for category, cat_info in SKILL_CATEGORIES.items():
            category_reqs = [m for m in skill_matches if m["requirement_category"] == category]

            if not category_reqs:
                continue

            matched = sum(1 for m in category_reqs if m["matched"])
            total = len(category_reqs)
            avg_proficiency = (
                sum(m["proficiency_score"] for m in category_reqs if m["matched"]) / matched
                if matched > 0 else 0
            )

            coverage[category] = {
                "matched": matched,
                "total": total,
                "coverage_score": round((matched / total) * 100, 1) if total > 0 else 100,
                "avg_proficiency": round(avg_proficiency, 2),
                "importance": cat_info["importance"],
                "description": cat_info["description"]
            }

        return coverage

    def _estimate_years(self, start_date: Optional[str], end_date: Optional[str]) -> float:
        """Estimate years of experience from date strings."""
        if not start_date:
            return 0

        try:
            # Parse start year
            start_year = int(re.search(r'\d{4}', start_date).group()) if re.search(r'\d{4}', start_date) else datetime.now().year

            # Parse end year
            if end_date and end_date.lower() not in ["present", "current", "now", ""]:
                end_match = re.search(r'\d{4}', end_date)
                end_year = int(end_match.group()) if end_match else datetime.now().year
            else:
                end_year = datetime.now().year

            return max(0, end_year - start_year)
        except Exception:
            return 1  # Default to 1 year if parsing fails

    def _generate_learning_priorities(
        self,
        skill_matches: List[Dict[str, Any]],
        critical_gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized list of skills to learn."""
        priorities = []

        # First add critical gaps
        for gap in critical_gaps:
            category = self._get_skill_category(gap)
            priorities.append({
                "skill": gap,
                "priority": "critical",
                "reason": f"Required skill in {category or 'core'} category",
                "estimated_effort": self._estimate_learning_effort(gap)
            })

        # Then add other missing skills
        for match in skill_matches:
            if not match["matched"] and match["requirement"] not in critical_gaps:
                priorities.append({
                    "skill": match["requirement"],
                    "priority": "recommended",
                    "reason": f"Missing {match['requirement_category']} skill",
                    "estimated_effort": self._estimate_learning_effort(match["requirement"])
                })

        return priorities

    def _estimate_learning_effort(self, skill: str) -> str:
        """Estimate effort to learn a skill."""
        # Complex skills take longer
        complex_skills = {"kubernetes", "machine learning", "deep learning", "system design", "aws", "gcp"}
        medium_skills = {"docker", "react", "django", "postgresql"}

        if skill.lower() in complex_skills:
            return "high (3-6 months)"
        elif skill.lower() in medium_skills:
            return "medium (1-3 months)"
        else:
            return "low (1-4 weeks)"

    def _find_alternative_skills(
        self,
        skill_matches: List[Dict[str, Any]],
        candidate_skills: set
    ) -> List[Dict[str, Any]]:
        """Find candidate skills that could substitute for missing requirements."""
        alternatives = []

        for match in skill_matches:
            if not match["matched"]:
                req = match["requirement"].lower()

                # Check if candidate has related skills
                for skill in candidate_skills:
                    if req in RELATED_SKILLS.get(skill, []):
                        alternatives.append({
                            "missing_requirement": match["requirement"],
                            "alternative_skill": skill,
                            "transferability": "high",
                            "note": f"{skill} skills are transferable to {match['requirement']}"
                        })
                        break

        return alternatives

    def _find_transferable_skills(
        self,
        candidate_skills: set,
        requirements: set
    ) -> List[str]:
        """Find skills that demonstrate learning potential."""
        transferable = []

        for skill in candidate_skills:
            if skill not in requirements:
                related = RELATED_SKILLS.get(skill, [])
                for rel in related:
                    if rel.lower() in requirements:
                        transferable.append(skill)
                        break

        return list(set(transferable))

    def _find_bonus_skills(
        self,
        candidate_skills: set,
        requirements: set
    ) -> List[str]:
        """Find valuable skills beyond requirements."""
        bonus = []

        valuable_skills = {
            "kubernetes", "docker", "aws", "gcp", "azure",
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "react", "typescript", "rust", "go",
            "system design", "microservices", "graphql"
        }

        for skill in candidate_skills:
            if skill not in requirements and skill in valuable_skills:
                bonus.append(skill)

        return bonus

    def _identify_strongest_areas(
        self,
        skill_matches: List[Dict[str, Any]],
        proficiency_counts: Dict[str, int]
    ) -> List[str]:
        """Identify candidate's strongest skill areas."""
        # Group by category and find high proficiency matches
        category_strengths = {}

        for match in skill_matches:
            if match["matched"] and match["proficiency_score"] >= 4:
                category = match["requirement_category"]
                if category not in category_strengths:
                    category_strengths[category] = 0
                category_strengths[category] += 1

        # Sort by count and return top categories
        sorted_categories = sorted(
            category_strengths.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [f"{cat} ({count} advanced/expert skills)" for cat, count in sorted_categories[:3]]


# Singleton instance
skill_gap_service = SkillGapService()

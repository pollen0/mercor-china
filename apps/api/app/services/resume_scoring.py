"""
Resume Scoring Service - Mercor-level resume analysis and scoring.

This service provides comprehensive resume scoring with:
1. Experience relevance and progression analysis
2. Skill depth and match scoring
3. Education quality assessment
4. Project impact evaluation
5. Company tier classification
6. Role-fit predictions
7. Red flag detection

Usage:
    from app.services.resume_scoring import resume_scorer

    score = await resume_scorer.score_resume(
        parsed_resume=parsed_resume,
        target_vertical="engineering",
        target_role="software_engineer",
        job_requirements=["Python", "AWS", "3+ years"]
    )
"""

import json
import logging
import re
import httpx
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..config import settings
from ..schemas.candidate import ParsedResume

logger = logging.getLogger("pathway.resume_scoring")


# ============================================
# COMPANY TIER DATABASE
# ============================================

class CompanyTierLevel(str, Enum):
    """Company prestige tiers."""
    FAANG = "faang"           # Meta, Apple, Amazon, Netflix, Google, Microsoft
    TIER_1 = "tier_1"         # Top tech: Stripe, Uber, Airbnb, etc.
    UNICORN = "unicorn"       # Well-funded startups
    BIG_TECH = "big_tech"     # Large tech: IBM, Oracle, Salesforce
    FINANCE = "finance"       # Top finance: Goldman, JPM, etc.
    CONSULTING = "consulting" # MBB, Big 4
    STARTUP = "startup"       # Early-stage startups
    UNKNOWN = "unknown"


# Known company classifications
COMPANY_TIERS: Dict[str, CompanyTierLevel] = {
    # FAANG+
    "meta": CompanyTierLevel.FAANG,
    "facebook": CompanyTierLevel.FAANG,
    "apple": CompanyTierLevel.FAANG,
    "amazon": CompanyTierLevel.FAANG,
    "netflix": CompanyTierLevel.FAANG,
    "google": CompanyTierLevel.FAANG,
    "alphabet": CompanyTierLevel.FAANG,
    "microsoft": CompanyTierLevel.FAANG,

    # Tier 1
    "stripe": CompanyTierLevel.TIER_1,
    "uber": CompanyTierLevel.TIER_1,
    "lyft": CompanyTierLevel.TIER_1,
    "airbnb": CompanyTierLevel.TIER_1,
    "dropbox": CompanyTierLevel.TIER_1,
    "twitter": CompanyTierLevel.TIER_1,
    "x corp": CompanyTierLevel.TIER_1,
    "linkedin": CompanyTierLevel.TIER_1,
    "snapchat": CompanyTierLevel.TIER_1,
    "snap": CompanyTierLevel.TIER_1,
    "pinterest": CompanyTierLevel.TIER_1,
    "doordash": CompanyTierLevel.TIER_1,
    "instacart": CompanyTierLevel.TIER_1,
    "coinbase": CompanyTierLevel.TIER_1,
    "robinhood": CompanyTierLevel.TIER_1,
    "palantir": CompanyTierLevel.TIER_1,
    "databricks": CompanyTierLevel.TIER_1,
    "snowflake": CompanyTierLevel.TIER_1,
    "figma": CompanyTierLevel.TIER_1,
    "notion": CompanyTierLevel.TIER_1,
    "openai": CompanyTierLevel.TIER_1,
    "anthropic": CompanyTierLevel.TIER_1,
    "nvidia": CompanyTierLevel.TIER_1,
    "tesla": CompanyTierLevel.TIER_1,
    "spacex": CompanyTierLevel.TIER_1,
    "square": CompanyTierLevel.TIER_1,
    "block": CompanyTierLevel.TIER_1,
    "plaid": CompanyTierLevel.TIER_1,
    "ramp": CompanyTierLevel.TIER_1,
    "brex": CompanyTierLevel.TIER_1,
    "scale ai": CompanyTierLevel.TIER_1,
    "anduril": CompanyTierLevel.TIER_1,
    "discord": CompanyTierLevel.TIER_1,
    "reddit": CompanyTierLevel.TIER_1,
    "twitch": CompanyTierLevel.TIER_1,

    # Big Tech
    "ibm": CompanyTierLevel.BIG_TECH,
    "oracle": CompanyTierLevel.BIG_TECH,
    "salesforce": CompanyTierLevel.BIG_TECH,
    "adobe": CompanyTierLevel.BIG_TECH,
    "vmware": CompanyTierLevel.BIG_TECH,
    "cisco": CompanyTierLevel.BIG_TECH,
    "intel": CompanyTierLevel.BIG_TECH,
    "qualcomm": CompanyTierLevel.BIG_TECH,
    "amd": CompanyTierLevel.BIG_TECH,
    "sap": CompanyTierLevel.BIG_TECH,
    "intuit": CompanyTierLevel.BIG_TECH,
    "servicenow": CompanyTierLevel.BIG_TECH,
    "workday": CompanyTierLevel.BIG_TECH,
    "atlassian": CompanyTierLevel.BIG_TECH,

    # Finance
    "goldman sachs": CompanyTierLevel.FINANCE,
    "goldman": CompanyTierLevel.FINANCE,
    "morgan stanley": CompanyTierLevel.FINANCE,
    "jpmorgan": CompanyTierLevel.FINANCE,
    "jp morgan": CompanyTierLevel.FINANCE,
    "blackrock": CompanyTierLevel.FINANCE,
    "citadel": CompanyTierLevel.FINANCE,
    "two sigma": CompanyTierLevel.FINANCE,
    "jane street": CompanyTierLevel.FINANCE,
    "de shaw": CompanyTierLevel.FINANCE,
    "bridgewater": CompanyTierLevel.FINANCE,
    "point72": CompanyTierLevel.FINANCE,

    # Consulting
    "mckinsey": CompanyTierLevel.CONSULTING,
    "bain": CompanyTierLevel.CONSULTING,
    "bcg": CompanyTierLevel.CONSULTING,
    "boston consulting": CompanyTierLevel.CONSULTING,
    "deloitte": CompanyTierLevel.CONSULTING,
    "pwc": CompanyTierLevel.CONSULTING,
    "ey": CompanyTierLevel.CONSULTING,
    "ernst & young": CompanyTierLevel.CONSULTING,
    "kpmg": CompanyTierLevel.CONSULTING,
    "accenture": CompanyTierLevel.CONSULTING,
}


# Role level indicators
SENIORITY_KEYWORDS = {
    "intern": 0,
    "co-op": 0,
    "trainee": 0,
    "junior": 1,
    "associate": 1,
    "entry": 1,
    "mid": 2,
    "senior": 3,
    "staff": 4,
    "principal": 5,
    "lead": 4,
    "manager": 4,
    "director": 5,
    "vp": 6,
    "vice president": 6,
    "head": 5,
    "chief": 7,
    "cto": 7,
    "ceo": 7,
    "founder": 6,
    "co-founder": 6,
}


# ============================================
# SKILL TAXONOMY
# ============================================

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
        "rust", "swift", "kotlin", "ruby", "php", "scala", "r", "matlab", "julia"
    ],
    "web_frameworks": [
        "react", "vue", "angular", "next.js", "nextjs", "nuxt", "django", "flask",
        "fastapi", "express", "node.js", "nodejs", "spring", "rails", "laravel"
    ],
    "data_ml": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
        "numpy", "spark", "hadoop", "airflow", "dbt", "mlflow", "kubeflow"
    ],
    "databases": [
        "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
        "dynamodb", "cassandra", "neo4j", "sqlite", "oracle", "sql server"
    ],
    "cloud_devops": [
        "aws", "gcp", "azure", "kubernetes", "k8s", "docker", "terraform",
        "jenkins", "github actions", "circleci", "ansible", "prometheus", "grafana"
    ],
    "system_design": [
        "microservices", "distributed systems", "system design", "architecture",
        "scalability", "high availability", "load balancing", "caching"
    ],
}

# Skill proficiency indicators (based on context)
PROFICIENCY_INDICATORS = {
    "expert": ["expert", "led", "architected", "designed", "mentored", "trained"],
    "advanced": ["advanced", "extensive", "deep", "senior", "optimized", "scaled"],
    "intermediate": ["proficient", "experienced", "worked with", "developed", "built"],
    "beginner": ["familiar", "basic", "learning", "exposure", "coursework"],
}


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class ExperienceScore:
    """Detailed experience scoring."""
    company: str
    title: str
    company_tier: str
    seniority_level: int
    duration_months: int
    relevance_score: float  # 0-10
    impact_score: float  # 0-10
    quantified_achievements: List[str]
    technologies_used: List[str]
    is_current: bool


@dataclass
class SkillScore:
    """Skill with proficiency assessment."""
    skill: str
    category: str
    proficiency: str  # expert, advanced, intermediate, beginner
    evidence_strength: float  # 0-1
    mentioned_in: List[str]  # experience, projects, skills section


@dataclass
class ResumeScore:
    """Complete resume scoring result."""
    # Overall
    overall_score: float  # 0-100
    overall_grade: str  # A+, A, A-, B+, etc.

    # Dimension scores (0-100)
    experience_relevance: float
    experience_progression: float
    skill_depth: float
    education_quality: float
    project_impact: float

    # Confidence
    confidence: float  # 0-1
    data_completeness: float  # 0-1

    # Detailed analysis
    experience_analysis: List[Dict[str, Any]]
    companies_by_tier: Dict[str, List[str]]
    skill_analysis: Dict[str, Any]
    education_analysis: List[Dict[str, Any]]
    project_analysis: List[Dict[str, Any]]

    # Role fit
    role_fit_scores: Dict[str, float]  # {role: score}
    best_fit_roles: List[str]

    # Insights
    top_strengths: List[str]
    key_concerns: List[str]
    red_flags: List[Dict[str, Any]]

    # Quality signals
    quality_signals: Dict[str, Any]


# ============================================
# RESUME SCORER
# ============================================

class ResumeScorerService:
    """
    Comprehensive resume scoring service.
    Analyzes resumes for relevance, quality, and role fit.
    """

    # Base dimension weights (adjusted by role)
    BASE_WEIGHTS = {
        "experience_relevance": 0.30,
        "experience_progression": 0.15,
        "skill_depth": 0.25,
        "education_quality": 0.15,
        "project_impact": 0.15,
    }

    # Role-specific weight adjustments
    ROLE_WEIGHT_ADJUSTMENTS = {
        "software_engineer": {"skill_depth": 0.05, "project_impact": 0.05, "experience_relevance": -0.10},
        "data_scientist": {"skill_depth": 0.05, "education_quality": 0.05, "project_impact": -0.10},
        "product_manager": {"experience_relevance": 0.10, "skill_depth": -0.10},
        "ux_designer": {"project_impact": 0.10, "skill_depth": -0.05, "education_quality": -0.05},
        "ml_engineer": {"skill_depth": 0.10, "education_quality": 0.05, "experience_relevance": -0.15},
    }

    def __init__(self):
        self.anthropic_api_key = settings.anthropic_api_key
        self.claude_model = settings.claude_model
        self.anthropic_base_url = "https://api.anthropic.com/v1"

    async def score_resume(
        self,
        parsed_resume: ParsedResume,
        target_vertical: Optional[str] = None,
        target_role: Optional[str] = None,
        job_requirements: Optional[List[str]] = None,
        raw_text: Optional[str] = None,
    ) -> ResumeScore:
        """
        Score a resume comprehensively.

        Args:
            parsed_resume: Structured resume data
            target_vertical: engineering, data, business, design
            target_role: Specific role (software_engineer, data_scientist, etc.)
            job_requirements: Specific job requirements to match against
            raw_text: Original resume text (for additional analysis)

        Returns:
            ResumeScore with detailed analysis
        """
        # Analyze each component
        experience_analysis = self._analyze_experience(parsed_resume, target_role)
        skill_analysis = self._analyze_skills(parsed_resume, target_role, job_requirements)
        education_analysis = self._analyze_education(parsed_resume, target_role)
        project_analysis = self._analyze_projects(parsed_resume, target_role)
        quality_signals = self._analyze_quality_signals(parsed_resume, raw_text)

        # Calculate dimension scores
        experience_relevance = self._calculate_experience_relevance(
            experience_analysis, target_role, job_requirements
        )
        experience_progression = self._calculate_experience_progression(experience_analysis)
        skill_depth = self._calculate_skill_depth(skill_analysis, target_role, job_requirements)
        education_quality = self._calculate_education_quality(education_analysis, target_role)
        project_impact = self._calculate_project_impact(project_analysis, target_role)

        # Calculate role fit scores
        role_fit_scores = self._calculate_role_fit_scores(
            experience_analysis, skill_analysis, education_analysis, project_analysis
        )

        # Get weights for target role
        weights = self._get_weights_for_role(target_role)

        # Calculate overall score
        overall_score = (
            experience_relevance * weights["experience_relevance"] +
            experience_progression * weights["experience_progression"] +
            skill_depth * weights["skill_depth"] +
            education_quality * weights["education_quality"] +
            project_impact * weights["project_impact"]
        )

        # Calculate confidence and completeness
        data_completeness = self._calculate_data_completeness(parsed_resume)
        confidence = self._calculate_confidence(
            experience_analysis, skill_analysis, education_analysis, data_completeness
        )

        # Extract insights
        top_strengths = self._extract_strengths(
            experience_analysis, skill_analysis, education_analysis, project_analysis
        )
        key_concerns = self._extract_concerns(
            experience_analysis, skill_analysis, quality_signals
        )
        red_flags = self._detect_red_flags(
            parsed_resume, experience_analysis, quality_signals
        )

        # Determine best fit roles
        best_fit_roles = sorted(
            role_fit_scores.keys(),
            key=lambda r: role_fit_scores[r],
            reverse=True
        )[:3]

        # Group companies by tier
        companies_by_tier = self._group_companies_by_tier(experience_analysis)

        return ResumeScore(
            overall_score=round(overall_score, 1),
            overall_grade=self._score_to_grade(overall_score),
            experience_relevance=round(experience_relevance, 1),
            experience_progression=round(experience_progression, 1),
            skill_depth=round(skill_depth, 1),
            education_quality=round(education_quality, 1),
            project_impact=round(project_impact, 1),
            confidence=round(confidence, 2),
            data_completeness=round(data_completeness, 2),
            experience_analysis=[asdict(e) if hasattr(e, '__dataclass_fields__') else e for e in experience_analysis],
            companies_by_tier=companies_by_tier,
            skill_analysis=skill_analysis,
            education_analysis=education_analysis,
            project_analysis=project_analysis,
            role_fit_scores=role_fit_scores,
            best_fit_roles=best_fit_roles,
            top_strengths=top_strengths,
            key_concerns=key_concerns,
            red_flags=red_flags,
            quality_signals=quality_signals,
        )

    # ==========================================
    # EXPERIENCE ANALYSIS
    # ==========================================

    def _analyze_experience(
        self,
        parsed_resume: ParsedResume,
        target_role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Analyze work experience in detail."""
        analysis = []

        for exp in (parsed_resume.experience or []):
            # Classify company tier
            company_lower = (exp.company or "").lower()
            company_tier = CompanyTierLevel.UNKNOWN
            for name, tier in COMPANY_TIERS.items():
                if name in company_lower:
                    company_tier = tier
                    break

            # Determine seniority level
            title_lower = (exp.title or "").lower()
            seniority = 2  # Default to mid
            for keyword, level in SENIORITY_KEYWORDS.items():
                if keyword in title_lower:
                    seniority = max(seniority, level)

            # Calculate duration
            duration_months = self._calculate_duration(exp.start_date, exp.end_date)

            # Extract quantified achievements
            quantified = self._extract_quantified_achievements(exp.highlights or [])

            # Extract technologies
            technologies = self._extract_technologies_from_text(
                " ".join([exp.description or ""] + (exp.highlights or []))
            )

            # Calculate relevance score
            relevance = self._calculate_experience_item_relevance(
                exp, target_role, company_tier
            )

            # Calculate impact score
            impact = self._calculate_impact_score(quantified, exp.highlights or [])

            is_current = (exp.end_date or "").lower() in ["present", "current", "now", ""]

            analysis.append({
                "company": exp.company,
                "title": exp.title,
                "company_tier": company_tier.value,
                "seniority_level": seniority,
                "duration_months": duration_months,
                "relevance_score": relevance,
                "impact_score": impact,
                "quantified_achievements": quantified,
                "technologies_used": technologies,
                "is_current": is_current,
                "description": exp.description,
                "highlights": exp.highlights,
            })

        # Sort by recency (current first, then by start date)
        analysis.sort(key=lambda x: (not x["is_current"], -(x.get("duration_months") or 0)))

        return analysis

    def _calculate_duration(
        self,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> int:
        """Calculate duration in months between dates."""
        if not start_date:
            return 0

        try:
            # Parse start date
            start = self._parse_date(start_date)

            # Parse end date (or use now)
            if end_date and end_date.lower() not in ["present", "current", "now", ""]:
                end = self._parse_date(end_date)
            else:
                end = date.today()

            # Calculate months
            months = (end.year - start.year) * 12 + (end.month - start.month)
            return max(0, months)
        except Exception:
            return 0

    def _parse_date(self, date_str: str) -> date:
        """Parse various date formats."""
        date_str = date_str.strip()

        # Try various formats
        formats = [
            "%Y-%m",
            "%Y-%m-%d",
            "%m/%Y",
            "%B %Y",
            "%b %Y",
            "%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        # Default to January of year if only year
        if date_str.isdigit() and len(date_str) == 4:
            return date(int(date_str), 1, 1)

        raise ValueError(f"Cannot parse date: {date_str}")

    def _extract_quantified_achievements(self, highlights: List[str]) -> List[str]:
        """Extract achievements with quantifiable metrics."""
        quantified = []

        # Patterns for quantified achievements
        patterns = [
            r'\d+%',  # percentages
            r'\$\d+',  # dollar amounts
            r'\d+x',  # multipliers
            r'\d+\s*(users?|customers?|clients?)',  # user counts
            r'\d+\s*(million|billion|k|m|b)',  # large numbers
            r'reduced.*by\s*\d+',  # reductions
            r'increased.*by\s*\d+',  # increases
            r'improved.*\d+',  # improvements
            r'saved.*\d+',  # savings
            r'generated.*\d+',  # revenue generation
        ]

        for highlight in highlights:
            for pattern in patterns:
                if re.search(pattern, highlight.lower()):
                    quantified.append(highlight)
                    break

        return quantified

    def _extract_technologies_from_text(self, text: str) -> List[str]:
        """Extract technology keywords from text."""
        text_lower = text.lower()
        found = []

        for category, skills in SKILL_CATEGORIES.items():
            for skill in skills:
                # Check for skill with word boundaries
                if re.search(rf'\b{re.escape(skill)}\b', text_lower):
                    found.append(skill)

        return list(set(found))

    def _calculate_experience_item_relevance(
        self,
        exp,
        target_role: Optional[str],
        company_tier: CompanyTierLevel
    ) -> float:
        """Calculate relevance of a single experience item (0-10)."""
        score = 5.0  # Base score

        # Company tier bonus
        tier_bonuses = {
            CompanyTierLevel.FAANG: 2.0,
            CompanyTierLevel.TIER_1: 1.5,
            CompanyTierLevel.FINANCE: 1.5,
            CompanyTierLevel.BIG_TECH: 1.0,
            CompanyTierLevel.CONSULTING: 1.0,
            CompanyTierLevel.UNICORN: 0.8,
            CompanyTierLevel.STARTUP: 0.3,
        }
        score += tier_bonuses.get(company_tier, 0)

        # Role relevance (if target specified)
        if target_role:
            title_lower = (exp.title or "").lower()
            role_keywords = self._get_role_keywords(target_role)
            for keyword in role_keywords:
                if keyword in title_lower:
                    score += 1.0
                    break

        # Cap at 10
        return min(10.0, score)

    def _calculate_impact_score(
        self,
        quantified: List[str],
        highlights: List[str]
    ) -> float:
        """Calculate impact score based on achievements (0-10)."""
        score = 3.0  # Base score

        # Bonus for quantified achievements
        score += min(3.0, len(quantified) * 0.75)

        # Bonus for number of highlights
        score += min(2.0, len(highlights) * 0.4)

        # Bonus for action verbs
        action_verbs = ["led", "built", "designed", "architected", "launched", "scaled",
                       "optimized", "reduced", "increased", "improved", "managed", "directed"]
        for highlight in highlights:
            if any(verb in highlight.lower() for verb in action_verbs):
                score += 0.3

        return min(10.0, score)

    def _get_role_keywords(self, role: str) -> List[str]:
        """Get keywords associated with a role."""
        keywords = {
            "software_engineer": ["software", "engineer", "developer", "swe", "sde"],
            "frontend_engineer": ["frontend", "front-end", "ui", "react", "web"],
            "backend_engineer": ["backend", "back-end", "server", "api", "systems"],
            "fullstack_engineer": ["fullstack", "full-stack", "full stack"],
            "data_scientist": ["data scientist", "ml", "machine learning", "analytics"],
            "data_engineer": ["data engineer", "etl", "pipeline", "data infrastructure"],
            "ml_engineer": ["ml engineer", "machine learning", "ai", "deep learning"],
            "product_manager": ["product", "pm", "program manager"],
            "ux_designer": ["ux", "ui", "design", "user experience"],
        }
        return keywords.get(role, [role.replace("_", " ")])

    # ==========================================
    # SKILL ANALYSIS
    # ==========================================

    def _analyze_skills(
        self,
        parsed_resume: ParsedResume,
        target_role: Optional[str],
        job_requirements: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Analyze skills in detail."""
        # Collect all text for skill extraction
        all_text = " ".join([
            " ".join(parsed_resume.skills or []),
            " ".join([e.description or "" for e in (parsed_resume.experience or [])]),
            " ".join([h for e in (parsed_resume.experience or []) for h in (e.highlights or [])]),
            " ".join([p.description or "" for p in (parsed_resume.projects or [])]),
        ]).lower()

        # Extract and categorize skills
        skills_by_category: Dict[str, List[Dict[str, Any]]] = {}

        for category, category_skills in SKILL_CATEGORIES.items():
            skills_by_category[category] = []
            for skill in category_skills:
                if re.search(rf'\b{re.escape(skill)}\b', all_text):
                    # Determine proficiency based on context
                    proficiency = self._estimate_proficiency(skill, all_text)
                    evidence = self._find_skill_evidence(skill, parsed_resume)

                    skills_by_category[category].append({
                        "skill": skill,
                        "proficiency": proficiency,
                        "evidence_strength": len(evidence) / 3.0,  # Normalize
                        "mentioned_in": evidence,
                    })

        # Calculate requirement match
        requirement_match = {}
        if job_requirements:
            for req in job_requirements:
                req_lower = req.lower()
                matched = any(
                    skill["skill"] in req_lower or req_lower in skill["skill"]
                    for skills in skills_by_category.values()
                    for skill in skills
                )
                requirement_match[req] = matched

        return {
            "by_category": skills_by_category,
            "total_skills": sum(len(s) for s in skills_by_category.values()),
            "requirement_match": requirement_match,
            "match_rate": (
                sum(requirement_match.values()) / len(requirement_match)
                if requirement_match else 0
            ),
        }

    def _estimate_proficiency(self, skill: str, text: str) -> str:
        """Estimate skill proficiency from context."""
        skill_context = self._get_skill_context(skill, text)

        for proficiency, indicators in PROFICIENCY_INDICATORS.items():
            for indicator in indicators:
                if indicator in skill_context:
                    return proficiency

        # Default based on mention frequency
        count = text.count(skill)
        if count >= 5:
            return "advanced"
        elif count >= 2:
            return "intermediate"
        return "beginner"

    def _get_skill_context(self, skill: str, text: str, window: int = 50) -> str:
        """Get text context around skill mention."""
        text_lower = text.lower()
        idx = text_lower.find(skill)
        if idx == -1:
            return ""
        start = max(0, idx - window)
        end = min(len(text), idx + len(skill) + window)
        return text_lower[start:end]

    def _find_skill_evidence(self, skill: str, parsed_resume: ParsedResume) -> List[str]:
        """Find where skill is mentioned."""
        evidence = []

        if parsed_resume.skills and skill in " ".join(parsed_resume.skills).lower():
            evidence.append("skills_section")

        for exp in (parsed_resume.experience or []):
            exp_text = " ".join([exp.description or ""] + (exp.highlights or [])).lower()
            if skill in exp_text:
                evidence.append("experience")
                break

        for proj in (parsed_resume.projects or []):
            proj_text = " ".join([proj.description or ""] + (proj.technologies or [])).lower()
            if skill in proj_text:
                evidence.append("projects")
                break

        return evidence

    # ==========================================
    # EDUCATION ANALYSIS
    # ==========================================

    def _analyze_education(
        self,
        parsed_resume: ParsedResume,
        target_role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Analyze education in detail."""
        analysis = []

        # University tier mapping
        top_universities = {
            "stanford": 5,
            "mit": 5,
            "harvard": 5,
            "berkeley": 5,
            "cmu": 5,
            "carnegie mellon": 5,
            "princeton": 5,
            "yale": 5,
            "columbia": 4,
            "cornell": 4,
            "caltech": 5,
            "georgia tech": 4,
            "michigan": 4,
            "illinois": 4,
            "uiuc": 4,
            "ucla": 4,
            "uw": 4,
            "washington": 4,
            "purdue": 4,
            "ut austin": 4,
            "texas": 4,
        }

        for edu in (parsed_resume.education or []):
            institution_lower = (edu.institution or "").lower()

            # Determine tier
            tier = 3  # Default
            for name, t in top_universities.items():
                if name in institution_lower:
                    tier = t
                    break

            # Determine degree level
            degree_lower = (edu.degree or "").lower()
            degree_level = 1  # Default bachelor's
            if "phd" in degree_lower or "doctor" in degree_lower:
                degree_level = 3
            elif "master" in degree_lower or "mba" in degree_lower or "ms" in degree_lower:
                degree_level = 2

            # Parse GPA
            gpa = None
            if edu.gpa:
                try:
                    gpa = float(edu.gpa.split("/")[0].strip())
                except (ValueError, AttributeError):
                    pass

            # Relevance to role
            field_lower = (edu.field_of_study or "").lower()
            is_relevant = self._is_field_relevant(field_lower, target_role)

            analysis.append({
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "graduation_year": edu.end_date,
                "gpa": gpa,
                "tier": tier,
                "degree_level": degree_level,
                "is_relevant": is_relevant,
            })

        return analysis

    def _is_field_relevant(self, field: str, target_role: Optional[str]) -> bool:
        """Check if field of study is relevant to target role."""
        if not target_role:
            return True

        relevant_fields = {
            "software_engineer": ["computer science", "cs", "software", "engineering", "eecs"],
            "data_scientist": ["data science", "statistics", "math", "computer science", "economics"],
            "ml_engineer": ["computer science", "machine learning", "ai", "math", "statistics"],
            "product_manager": ["business", "mba", "computer science", "engineering"],
            "ux_designer": ["design", "hci", "human-computer", "psychology"],
        }

        for keyword in relevant_fields.get(target_role, []):
            if keyword in field:
                return True
        return False

    # ==========================================
    # PROJECT ANALYSIS
    # ==========================================

    def _analyze_projects(
        self,
        parsed_resume: ParsedResume,
        target_role: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Analyze projects in detail."""
        analysis = []

        for proj in (parsed_resume.projects or []):
            # Extract technologies
            technologies = proj.technologies or []
            if proj.description:
                technologies.extend(
                    self._extract_technologies_from_text(proj.description)
                )
            technologies = list(set(technologies))

            # Determine scope
            scope = "personal"
            desc_lower = (proj.description or "").lower()
            if "team" in desc_lower or "group" in desc_lower:
                scope = "team"
            elif "class" in desc_lower or "course" in desc_lower:
                scope = "class"
            elif "hackathon" in desc_lower:
                scope = "hackathon"

            # Calculate complexity score
            complexity = self._calculate_project_complexity(proj, technologies)

            # Check for impact indicators
            impact_indicators = self._extract_quantified_achievements(
                proj.highlights or [proj.description or ""]
            )

            analysis.append({
                "name": proj.name,
                "description": proj.description,
                "technologies": technologies,
                "highlights": proj.highlights,
                "scope": scope,
                "complexity_score": complexity,
                "impact_indicators": impact_indicators,
            })

        return analysis

    def _calculate_project_complexity(
        self,
        project,
        technologies: List[str]
    ) -> float:
        """Calculate project complexity (0-10)."""
        score = 3.0  # Base

        # Technology count bonus
        score += min(3.0, len(technologies) * 0.5)

        # Advanced tech bonus
        advanced_tech = ["kubernetes", "distributed", "machine learning", "ml",
                       "microservices", "scalability", "real-time"]
        for tech in technologies:
            if any(adv in tech.lower() for adv in advanced_tech):
                score += 0.5

        # Description length/detail bonus
        desc = project.description or ""
        if len(desc) > 200:
            score += 1.0

        return min(10.0, score)

    # ==========================================
    # SCORE CALCULATIONS
    # ==========================================

    def _calculate_experience_relevance(
        self,
        experience_analysis: List[Dict[str, Any]],
        target_role: Optional[str],
        job_requirements: Optional[List[str]]
    ) -> float:
        """Calculate experience relevance score (0-100)."""
        if not experience_analysis:
            return 30.0  # Low score for no experience

        # Weighted average of relevance scores (recent experience weighted more)
        total_weight = 0
        weighted_score = 0

        for i, exp in enumerate(experience_analysis):
            weight = 1.0 / (i + 1)  # Decreasing weight for older experience
            total_weight += weight
            weighted_score += exp["relevance_score"] * weight * 10  # Convert to 0-100

        if total_weight == 0:
            return 30.0

        base_score = weighted_score / total_weight

        # Bonus for total experience duration
        total_months = sum(e["duration_months"] for e in experience_analysis)
        if total_months >= 36:  # 3+ years
            base_score += 10
        elif total_months >= 24:  # 2+ years
            base_score += 5

        return min(100.0, base_score)

    def _calculate_experience_progression(
        self,
        experience_analysis: List[Dict[str, Any]]
    ) -> float:
        """Calculate experience progression score (0-100)."""
        if len(experience_analysis) < 2:
            return 50.0  # Neutral for single experience

        # Check for seniority progression
        seniority_levels = [e["seniority_level"] for e in experience_analysis]

        # Reverse because list is sorted by recency (most recent first)
        seniority_levels = seniority_levels[::-1]

        # Calculate progression
        progressions = 0
        regressions = 0

        for i in range(1, len(seniority_levels)):
            if seniority_levels[i] > seniority_levels[i-1]:
                progressions += 1
            elif seniority_levels[i] < seniority_levels[i-1]:
                regressions += 1

        score = 50.0  # Base

        # Bonus for progression
        score += progressions * 15

        # Penalty for regression
        score -= regressions * 10

        # Bonus for reaching senior levels
        max_level = max(seniority_levels) if seniority_levels else 0
        if max_level >= 4:  # Staff/Lead+
            score += 15
        elif max_level >= 3:  # Senior
            score += 10

        return max(0, min(100.0, score))

    def _calculate_skill_depth(
        self,
        skill_analysis: Dict[str, Any],
        target_role: Optional[str],
        job_requirements: Optional[List[str]]
    ) -> float:
        """Calculate skill depth score (0-100)."""
        score = 30.0  # Base

        # Total skills bonus
        total = skill_analysis.get("total_skills", 0)
        score += min(20, total * 2)

        # Requirement match bonus
        match_rate = skill_analysis.get("match_rate", 0)
        score += match_rate * 30

        # Category coverage bonus
        categories = skill_analysis.get("by_category", {})
        covered = sum(1 for skills in categories.values() if skills)
        score += covered * 5

        # Advanced proficiency bonus
        for skills in categories.values():
            for skill in skills:
                if skill.get("proficiency") in ["expert", "advanced"]:
                    score += 2

        return min(100.0, score)

    def _calculate_education_quality(
        self,
        education_analysis: List[Dict[str, Any]],
        target_role: Optional[str]
    ) -> float:
        """Calculate education quality score (0-100)."""
        if not education_analysis:
            return 30.0  # Low but not zero

        # Take best education
        best_edu = max(education_analysis, key=lambda e: (
            e.get("tier", 1) * 10 +
            e.get("degree_level", 1) * 5 +
            (e.get("gpa", 0) or 0) * 5 +
            (10 if e.get("is_relevant") else 0)
        ))

        score = 30.0  # Base

        # University tier bonus
        tier_bonus = {5: 30, 4: 20, 3: 10, 2: 5, 1: 0}
        score += tier_bonus.get(best_edu.get("tier", 1), 0)

        # Degree level bonus
        degree_bonus = {3: 20, 2: 10, 1: 0}  # PhD, Master's, Bachelor's
        score += degree_bonus.get(best_edu.get("degree_level", 1), 0)

        # GPA bonus
        gpa = best_edu.get("gpa")
        if gpa:
            if gpa >= 3.8:
                score += 15
            elif gpa >= 3.5:
                score += 10
            elif gpa >= 3.0:
                score += 5

        # Relevance bonus
        if best_edu.get("is_relevant"):
            score += 10

        return min(100.0, score)

    def _calculate_project_impact(
        self,
        project_analysis: List[Dict[str, Any]],
        target_role: Optional[str]
    ) -> float:
        """Calculate project impact score (0-100)."""
        if not project_analysis:
            return 40.0  # Projects are nice to have

        score = 30.0  # Base

        # Number of projects bonus
        score += min(20, len(project_analysis) * 5)

        # Complexity bonus
        avg_complexity = sum(p["complexity_score"] for p in project_analysis) / len(project_analysis)
        score += avg_complexity * 3

        # Impact indicators bonus
        total_impacts = sum(len(p["impact_indicators"]) for p in project_analysis)
        score += min(15, total_impacts * 5)

        return min(100.0, score)

    # ==========================================
    # ROLE FIT CALCULATIONS
    # ==========================================

    def _calculate_role_fit_scores(
        self,
        experience_analysis: List[Dict[str, Any]],
        skill_analysis: Dict[str, Any],
        education_analysis: List[Dict[str, Any]],
        project_analysis: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate fit scores for different roles."""
        roles = [
            "software_engineer", "frontend_engineer", "backend_engineer",
            "data_scientist", "data_engineer", "ml_engineer",
            "product_manager", "ux_designer"
        ]

        fit_scores = {}
        for role in roles:
            fit_scores[role] = self._calculate_single_role_fit(
                role, experience_analysis, skill_analysis, education_analysis, project_analysis
            )

        return fit_scores

    def _calculate_single_role_fit(
        self,
        role: str,
        experience_analysis: List[Dict[str, Any]],
        skill_analysis: Dict[str, Any],
        education_analysis: List[Dict[str, Any]],
        project_analysis: List[Dict[str, Any]]
    ) -> float:
        """Calculate fit for a single role (0-100)."""
        score = 50.0  # Base neutral score

        # Skill category bonuses by role
        role_skills = {
            "software_engineer": ["programming_languages", "web_frameworks", "databases", "cloud_devops"],
            "frontend_engineer": ["programming_languages", "web_frameworks"],
            "backend_engineer": ["programming_languages", "databases", "cloud_devops", "system_design"],
            "data_scientist": ["programming_languages", "data_ml", "databases"],
            "data_engineer": ["programming_languages", "databases", "cloud_devops", "data_ml"],
            "ml_engineer": ["programming_languages", "data_ml", "cloud_devops"],
            "product_manager": [],  # Less skill dependent
            "ux_designer": [],  # Less skill dependent
        }

        categories = skill_analysis.get("by_category", {})
        for cat in role_skills.get(role, []):
            if categories.get(cat):
                score += len(categories[cat]) * 3

        # Experience title match
        role_keywords = self._get_role_keywords(role)
        for exp in experience_analysis:
            title_lower = (exp.get("title") or "").lower()
            if any(kw in title_lower for kw in role_keywords):
                score += 10

        # Cap at 100
        return min(100.0, score)

    # ==========================================
    # HELPER METHODS
    # ==========================================

    def _get_weights_for_role(self, role: Optional[str]) -> Dict[str, float]:
        """Get dimension weights adjusted for role."""
        weights = self.BASE_WEIGHTS.copy()

        if role and role in self.ROLE_WEIGHT_ADJUSTMENTS:
            for dim, adjustment in self.ROLE_WEIGHT_ADJUSTMENTS[role].items():
                weights[dim] = weights.get(dim, 0) + adjustment

        # Normalize to sum to 1
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    def _calculate_data_completeness(self, parsed_resume: ParsedResume) -> float:
        """Calculate how complete the resume data is (0-1)."""
        checks = [
            bool(parsed_resume.name),
            bool(parsed_resume.email),
            bool(parsed_resume.skills and len(parsed_resume.skills) > 0),
            bool(parsed_resume.experience and len(parsed_resume.experience) > 0),
            bool(parsed_resume.education and len(parsed_resume.education) > 0),
        ]

        # Bonus for having projects
        if parsed_resume.projects and len(parsed_resume.projects) > 0:
            checks.append(True)
        else:
            checks.append(False)

        return sum(checks) / len(checks)

    def _calculate_confidence(
        self,
        experience_analysis: List[Dict[str, Any]],
        skill_analysis: Dict[str, Any],
        education_analysis: List[Dict[str, Any]],
        data_completeness: float
    ) -> float:
        """Calculate confidence in the score (0-1)."""
        confidence = data_completeness * 0.5

        # More experience = higher confidence
        if experience_analysis:
            confidence += min(0.3, len(experience_analysis) * 0.1)

        # More skills = higher confidence
        if skill_analysis.get("total_skills", 0) >= 5:
            confidence += 0.1

        # Education verified = higher confidence
        if education_analysis:
            confidence += 0.1

        return min(1.0, confidence)

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _extract_strengths(
        self,
        experience_analysis: List[Dict[str, Any]],
        skill_analysis: Dict[str, Any],
        education_analysis: List[Dict[str, Any]],
        project_analysis: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract top strengths from analysis."""
        strengths = []

        # Check for top company experience
        for exp in experience_analysis:
            if exp["company_tier"] in ["faang", "tier_1"]:
                strengths.append(f"Experience at {exp['company']}")
                break

        # Check for senior level
        max_seniority = max((e["seniority_level"] for e in experience_analysis), default=0)
        if max_seniority >= 4:
            strengths.append("Senior-level experience")

        # Check for strong skills
        if skill_analysis.get("total_skills", 0) >= 10:
            strengths.append("Diverse technical skill set")

        # Check for high requirement match
        if skill_analysis.get("match_rate", 0) >= 0.8:
            strengths.append("Strong match with job requirements")

        # Check for top education
        for edu in education_analysis:
            if edu.get("tier", 0) >= 4:
                strengths.append(f"Degree from {edu['institution']}")
                break

        # Check for quantified achievements
        all_achievements = [
            a for exp in experience_analysis
            for a in exp.get("quantified_achievements", [])
        ]
        if len(all_achievements) >= 3:
            strengths.append("Multiple quantified achievements")

        return strengths[:5]  # Top 5

    def _extract_concerns(
        self,
        experience_analysis: List[Dict[str, Any]],
        skill_analysis: Dict[str, Any],
        quality_signals: Dict[str, Any]
    ) -> List[str]:
        """Extract key concerns from analysis."""
        concerns = []

        # Check for gaps or short tenure
        for exp in experience_analysis:
            if exp["duration_months"] < 6 and not exp["is_current"]:
                concerns.append(f"Short tenure at {exp['company']} ({exp['duration_months']} months)")
                break

        # Check for low requirement match
        if skill_analysis.get("match_rate", 0) < 0.5:
            concerns.append("Low match with job requirements")

        # Check for missing key skills
        missing = [
            req for req, matched in skill_analysis.get("requirement_match", {}).items()
            if not matched
        ]
        if missing:
            concerns.append(f"Missing skills: {', '.join(missing[:3])}")

        # Check for limited experience
        total_months = sum(e["duration_months"] for e in experience_analysis)
        if total_months < 12:
            concerns.append("Limited work experience")

        return concerns[:5]  # Top 5

    def _detect_red_flags(
        self,
        parsed_resume: ParsedResume,
        experience_analysis: List[Dict[str, Any]],
        quality_signals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect potential red flags."""
        red_flags = []

        # Job hopping (multiple short stints)
        short_stints = sum(
            1 for exp in experience_analysis
            if exp["duration_months"] < 12 and not exp["is_current"]
        )
        if short_stints >= 2:
            red_flags.append({
                "type": "job_hopping",
                "description": f"{short_stints} positions held for less than a year",
                "severity": "medium"
            })

        # Employment gaps (simplified check)
        # Note: Would need date analysis for accurate gap detection

        # No contact info
        if not parsed_resume.email:
            red_flags.append({
                "type": "missing_contact",
                "description": "No email address provided",
                "severity": "low"
            })

        # Grammar/quality issues would need the raw text
        if quality_signals.get("potential_issues"):
            for issue in quality_signals["potential_issues"]:
                red_flags.append({
                    "type": "quality",
                    "description": issue,
                    "severity": "low"
                })

        return red_flags

    def _group_companies_by_tier(
        self,
        experience_analysis: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Group companies by tier."""
        by_tier: Dict[str, List[str]] = {}

        for exp in experience_analysis:
            tier = exp["company_tier"]
            if tier not in by_tier:
                by_tier[tier] = []
            if exp["company"] not in by_tier[tier]:
                by_tier[tier].append(exp["company"])

        return by_tier

    def _analyze_quality_signals(
        self,
        parsed_resume: ParsedResume,
        raw_text: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze resume quality signals."""
        signals = {
            "has_quantified_achievements": False,
            "action_verbs_count": 0,
            "formatting_consistent": True,  # Simplified
            "appropriate_length": True,
            "potential_issues": []
        }

        # Check for quantified achievements
        for exp in (parsed_resume.experience or []):
            for highlight in (exp.highlights or []):
                if re.search(r'\d+%|\$\d+|\d+x', highlight):
                    signals["has_quantified_achievements"] = True
                    break

        # Count action verbs
        action_verbs = ["led", "built", "designed", "developed", "managed", "created",
                       "implemented", "launched", "improved", "optimized", "scaled"]
        for exp in (parsed_resume.experience or []):
            for highlight in (exp.highlights or []):
                signals["action_verbs_count"] += sum(
                    1 for verb in action_verbs if verb in highlight.lower()
                )

        # Check length (if raw text available)
        if raw_text:
            word_count = len(raw_text.split())
            if word_count < 200:
                signals["appropriate_length"] = False
                signals["potential_issues"].append("Resume may be too brief")
            elif word_count > 1500:
                signals["potential_issues"].append("Resume may be too long")

        return signals


# Singleton instance
resume_scorer = ResumeScorerService()

"""
Matching service for scoring candidate-job fit.
Uses interview scores, resume data, GitHub signals, and job requirements to calculate match scores.

Enhanced with ML-powered features:
1. Semantic skill matching (synonyms, related skills)
2. GitHub signal integration (languages, contributions, repo quality)
3. Education quality scoring
4. Proficiency level detection
5. Growth trajectory analysis
"""

import json
import re
import httpx
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from ..config import settings
from ..schemas.candidate import ParsedResume


@dataclass
class MatchResult:
    """Result of matching a candidate to a job."""
    interview_score: float  # 0-10
    skills_match_score: float  # 0-10
    experience_match_score: float  # 0-10
    location_match: bool
    overall_match_score: float  # 0-100
    factors: dict
    ai_reasoning: str
    # Preference boost (optional, based on candidate preferences matching job)
    preference_boost: float = 0.0  # 0-30 (max +30 points)
    boosted_match_score: float = 0.0  # overall_match_score + preference_boost (capped at 100)


@dataclass
class EnhancedMatchResult(MatchResult):
    """Enhanced match result with ML-powered insights."""
    # Additional ML-powered scores
    github_signal_score: float = 0.0  # 0-10
    education_score: float = 0.0  # 0-10
    growth_trajectory_score: float = 0.0  # 0-10

    # Skill gap analysis
    skill_gap_summary: Dict[str, Any] = field(default_factory=dict)

    # Detailed insights
    top_strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)
    hiring_recommendation: str = ""
    confidence_score: float = 0.0  # 0-1


# Comprehensive skill synonyms for semantic matching
SKILL_SYNONYMS = {
    # Languages
    "javascript": ["js", "ecmascript", "es6", "es2015", "es2020"],
    "typescript": ["ts"],
    "python": ["py", "python3", "python2"],
    "golang": ["go"],
    "c++": ["cpp", "cplusplus", "c plus plus"],
    "c#": ["csharp", "dotnet", ".net", "c sharp"],
    "ruby": ["rb"],

    # Frameworks
    "react": ["reactjs", "react.js", "react js"],
    "vue": ["vuejs", "vue.js", "vue js", "vue 3"],
    "angular": ["angularjs", "angular.js", "angular 2+"],
    "next.js": ["nextjs", "next"],
    "node.js": ["nodejs", "node"],
    "express": ["expressjs", "express.js"],
    "django": ["django rest framework", "drf"],
    "flask": ["flask-restful"],
    "fastapi": ["fast api", "fast-api"],
    "spring": ["spring boot", "springboot", "spring framework"],

    # Databases
    "postgresql": ["postgres", "psql", "pg"],
    "mysql": ["mariadb", "percona"],
    "mongodb": ["mongo"],
    "redis": ["redis cache", "redis db"],
    "elasticsearch": ["elastic", "es", "opensearch"],
    "dynamodb": ["dynamo db", "aws dynamodb"],

    # Cloud
    "aws": ["amazon web services", "amazon cloud", "amazon aws"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure", "azure cloud"],
    "kubernetes": ["k8s", "kube"],
    "docker": ["containers", "containerization", "docker compose"],
    "terraform": ["tf", "terraform cloud"],

    # ML/AI
    "machine learning": ["ml", "machine-learning"],
    "deep learning": ["dl", "neural networks", "neural nets"],
    "tensorflow": ["tf", "tensor flow"],
    "pytorch": ["torch", "py torch"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "natural language processing": ["nlp", "text processing"],
    "computer vision": ["cv", "image recognition", "image processing"],

    # Concepts
    "rest api": ["restful", "rest apis", "rest", "restful api"],
    "graphql": ["graph ql", "gql"],
    "microservices": ["micro services", "micro-services"],
    "ci/cd": ["continuous integration", "continuous deployment", "cicd", "ci cd"],
    "agile": ["scrum", "kanban", "agile methodology"],
    "devops": ["dev ops", "sre", "site reliability"],
}

# Related/transferable skills
RELATED_SKILLS = {
    "python": ["java", "ruby", "javascript", "go"],
    "java": ["kotlin", "scala", "c#"],
    "react": ["vue", "angular", "svelte", "preact"],
    "vue": ["react", "angular", "svelte"],
    "angular": ["react", "vue", "typescript"],
    "aws": ["gcp", "azure", "cloudflare"],
    "gcp": ["aws", "azure"],
    "azure": ["aws", "gcp"],
    "postgresql": ["mysql", "oracle", "sql server", "mariadb"],
    "mysql": ["postgresql", "mariadb", "sql server"],
    "mongodb": ["couchdb", "dynamodb", "firebase"],
    "tensorflow": ["pytorch", "keras", "jax"],
    "pytorch": ["tensorflow", "keras", "jax"],
    "kubernetes": ["docker swarm", "ecs", "nomad", "mesos"],
    "docker": ["podman", "containerd"],
}

# Top tech companies for education/experience signals
TOP_COMPANIES = {
    "faang": ["meta", "facebook", "apple", "amazon", "netflix", "google", "alphabet", "microsoft"],
    "tier_1": ["stripe", "uber", "lyft", "airbnb", "dropbox", "twitter", "linkedin", "snap", "pinterest",
               "doordash", "instacart", "coinbase", "robinhood", "palantir", "databricks", "snowflake",
               "openai", "anthropic", "nvidia", "tesla", "spacex", "square", "block", "plaid", "ramp", "brex"],
}

# Top universities
TOP_UNIVERSITIES = {
    "tier_1": ["stanford", "mit", "harvard", "berkeley", "cmu", "carnegie mellon", "princeton", "yale", "caltech",
               "cornell", "georgia tech", "michigan", "umich", "columbia", "ucla"],
    "tier_2": ["illinois", "uiuc", "washington", "uw", "purdue", "ut austin", "texas", "usc", "duke",
               "northwestern", "brown", "penn", "upenn", "uc san diego", "ucsd", "umd", "maryland",
               "wisconsin", "uwisc", "ucsb", "santa barbara"],
}


class MatchingService:
    """Service for calculating candidate-job match scores with ML-powered enhancements."""

    # Base weights for overall score calculation
    BASE_WEIGHTS = {
        'interview_score': 0.35,  # 35% weight
        'skills_match': 0.25,  # 25% weight
        'experience_match': 0.15,  # 15% weight
        'github_signal': 0.10,  # 10% weight (new)
        'education': 0.10,  # 10% weight (new)
        'location_match': 0.05,  # 5% weight
    }

    # Weights for overall score calculation (legacy compatibility)
    WEIGHTS = {
        'interview_score': 0.40,  # 40% weight
        'skills_match': 0.25,  # 25% weight
        'experience_match': 0.20,  # 20% weight
        'location_match': 0.15,  # 15% weight
    }

    def __init__(self):
        # Claude API (exclusive - all AI uses Claude)
        self.api_key = settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"

    def calculate_skills_match(
        self,
        candidate_skills: list[str],
        job_requirements: list[str]
    ) -> tuple[float, dict]:
        """
        Calculate how well candidate skills match job requirements.

        Returns:
            Tuple of (score 0-10, details dict)
        """
        if not job_requirements:
            return 7.0, {"matched": [], "missing": [], "reason": "No specific requirements"}

        if not candidate_skills:
            return 3.0, {"matched": [], "missing": job_requirements, "reason": "No skills listed"}

        # Normalize for comparison
        candidate_lower = [s.lower().strip() for s in candidate_skills]
        requirements_lower = [r.lower().strip() for r in job_requirements]

        matched = []
        missing = []

        for req in requirements_lower:
            # Check for exact or partial match
            found = False
            for skill in candidate_lower:
                # Check if requirement is contained in skill or vice versa
                if req in skill or skill in req or self._fuzzy_match(req, skill):
                    matched.append(req)
                    found = True
                    break
            if not found:
                missing.append(req)

        # Calculate score
        total_reqs = len(requirements_lower)
        matched_count = len(matched)

        if total_reqs == 0:
            score = 7.0
        else:
            # Base score on match percentage
            match_pct = matched_count / total_reqs
            score = match_pct * 10

            # Bonus for having more skills than required
            if len(candidate_skills) > total_reqs:
                score = min(10.0, score + 0.5)

        return round(score, 1), {
            "matched": matched,
            "missing": missing,
            "match_percentage": round(match_pct * 100, 1) if total_reqs > 0 else 100
        }

    def _fuzzy_match(self, s1: str, s2: str) -> bool:
        """Simple fuzzy matching for skills."""
        # Common abbreviations and synonyms
        equivalents = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'react': 'reactjs',
            'vue': 'vuejs',
            'node': 'nodejs',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'db': 'database',
            'sql': 'database',
            'nosql': 'database',
        }

        s1_normalized = equivalents.get(s1, s1)
        s2_normalized = equivalents.get(s2, s2)

        return s1_normalized == s2_normalized

    def calculate_experience_match(
        self,
        candidate_experience: list[dict],
        job_title: str,
        job_vertical: Optional[str] = None
    ) -> tuple[float, dict]:
        """
        Calculate experience relevance score.

        Returns:
            Tuple of (score 0-10, details dict)
        """
        if not candidate_experience:
            return 3.0, {"years": 0, "relevant_roles": [], "reason": "No experience listed"}

        job_title_lower = job_title.lower()
        relevant_roles = []
        total_years = 0

        for exp in candidate_experience:
            title = exp.get('title', '').lower()
            company = exp.get('company', '')

            # Estimate tenure (simplified)
            start = exp.get('start_date', '')
            end = exp.get('end_date', 'Present')

            # Very simplified year calculation
            try:
                start_year = int(start[:4]) if start else 2020
                end_year = 2025 if end == 'Present' or not end else int(end[:4])
                years = max(0, end_year - start_year)
            except (ValueError, TypeError):
                years = 1

            total_years += years

            # Check relevance
            # Look for similar job titles or vertical keywords
            vertical_keywords = {
                'engineering': ['software', 'developer', 'engineer', 'programming', 'coding', 'backend', 'frontend', 'fullstack', 'devops'],
                'data': ['data', 'analytics', 'machine learning', 'ml', 'ai', 'statistics', 'python', 'sql'],
                'business': ['product', 'marketing', 'finance', 'consulting', 'strategy', 'operations', 'analyst'],
                'design': ['design', 'ux', 'ui', 'user experience', 'figma', 'prototype', 'visual']
            }

            is_relevant = False
            if any(word in title for word in job_title_lower.split()):
                is_relevant = True
            elif job_vertical and job_vertical in vertical_keywords:
                if any(kw in title for kw in vertical_keywords[job_vertical]):
                    is_relevant = True

            if is_relevant:
                relevant_roles.append({
                    'title': exp.get('title', ''),
                    'company': company,
                    'years': years
                })

        # Calculate score
        relevant_years = sum(r['years'] for r in relevant_roles)

        # Score based on relevant experience
        if relevant_years >= 5:
            score = 10.0
        elif relevant_years >= 3:
            score = 8.5
        elif relevant_years >= 1:
            score = 7.0
        elif total_years >= 3:
            score = 5.0  # Has experience but not directly relevant
        else:
            score = 3.0

        return round(score, 1), {
            "total_years": total_years,
            "relevant_years": relevant_years,
            "relevant_roles": relevant_roles[:3]  # Top 3
        }

    def calculate_location_match(
        self,
        candidate_location: Optional[str],
        job_location: Optional[str]
    ) -> tuple[bool, dict]:
        """
        Check if candidate location matches job location.

        Returns:
            Tuple of (matches: bool, details dict)
        """
        if not job_location:
            return True, {"reason": "Remote or no location requirement"}

        if not candidate_location:
            return False, {"reason": "Candidate location unknown"}

        # Normalize
        candidate_loc = candidate_location.lower().strip()
        job_loc = job_location.lower().strip()

        # Check for match (city or country level)
        if candidate_loc in job_loc or job_loc in candidate_loc:
            return True, {"reason": f"Location match: {candidate_location}"}

        # Check for remote/flexible
        if 'remote' in job_loc or 'flexible' in job_loc:
            return True, {"reason": "Remote work available"}

        return False, {"reason": f"Location mismatch: {candidate_location} vs {job_location}"}

    def calculate_preference_boost(
        self,
        candidate_preferences: Optional[dict],
        job_company_stage: Optional[str] = None,
        job_location: Optional[str] = None,
        job_industry: Optional[str] = None,
    ) -> Tuple[float, dict]:
        """
        Calculate preference boost based on candidate preferences matching job.

        Preference boost scoring:
        - Company stage match: +10 points
        - Location match: +10 points
        - Industry match: +10 points
        - Max boost: +30 points

        Args:
            candidate_preferences: Dict with company_stages, locations, industries
            job_company_stage: e.g., "seed", "series_a", "series_b", "growth", "public"
            job_location: e.g., "San Francisco", "Remote", "NYC"
            job_industry: e.g., "fintech", "ai", "climate", "healthcare"

        Returns:
            Tuple of (boost_points, details_dict)
        """
        if not candidate_preferences:
            return 0.0, {"reason": "No preferences set"}

        boost = 0.0
        details = {"matches": [], "no_matches": []}

        # Company stage match (+10 points)
        pref_stages = candidate_preferences.get("company_stages", [])
        if pref_stages and job_company_stage:
            job_stage_lower = job_company_stage.lower().replace(" ", "_").replace("-", "_")
            pref_stages_lower = [s.lower().replace(" ", "_").replace("-", "_") for s in pref_stages]
            if job_stage_lower in pref_stages_lower:
                boost += 10.0
                details["matches"].append(f"company_stage:{job_company_stage}")
            else:
                details["no_matches"].append("company_stage")

        # Location match (+10 points)
        pref_locations = candidate_preferences.get("locations", [])
        if pref_locations and job_location:
            job_loc_lower = job_location.lower()
            matched = False
            for pref_loc in pref_locations:
                pref_loc_lower = pref_loc.lower()
                # Check for matches (remote, city names, etc.)
                if pref_loc_lower in job_loc_lower or job_loc_lower in pref_loc_lower:
                    matched = True
                    break
                # Special case: "Remote" matches anything with "remote"
                if pref_loc_lower == "remote" and "remote" in job_loc_lower:
                    matched = True
                    break
            if matched:
                boost += 10.0
                details["matches"].append(f"location:{job_location}")
            else:
                details["no_matches"].append("location")

        # Industry match (+10 points)
        pref_industries = candidate_preferences.get("industries", [])
        if pref_industries and job_industry:
            job_ind_lower = job_industry.lower().replace(" ", "_").replace("-", "_")
            pref_industries_lower = [i.lower().replace(" ", "_").replace("-", "_") for i in pref_industries]
            if job_ind_lower in pref_industries_lower:
                boost += 10.0
                details["matches"].append(f"industry:{job_industry}")
            else:
                details["no_matches"].append("industry")

        details["total_boost"] = boost
        return boost, details

    async def calculate_match(
        self,
        interview_score: float,  # 0-10
        candidate_data: Optional[dict],  # Parsed resume data as dict
        job_title: str,
        job_requirements: list[str],
        job_location: Optional[str] = None,
        job_vertical: Optional[str] = None,
        # Preference boost params (new)
        candidate_preferences: Optional[dict] = None,
        job_company_stage: Optional[str] = None,
        job_industry: Optional[str] = None,
    ) -> MatchResult:
        """
        Calculate overall match score for a candidate-job pair.

        Args:
            interview_score: Score from completed interview (0-10)
            candidate_data: Parsed resume data dict
            job_title: Job title
            job_requirements: List of job requirements
            job_location: Job location
            job_vertical: 'engineering', 'data', 'business', 'design'
            candidate_preferences: Candidate's sharing_preferences dict
            job_company_stage: Company stage (seed, series_a, etc.)
            job_industry: Company industry (fintech, ai, etc.)

        Returns:
            MatchResult with all scoring details including preference boost
        """
        factors = {}

        # Interview score (already 0-10)
        interview_score = min(10.0, max(0.0, interview_score))
        factors['interview'] = {
            'score': interview_score,
            'weight': self.WEIGHTS['interview_score']
        }

        # Skills match
        candidate_skills = []
        if candidate_data and 'skills' in candidate_data:
            candidate_skills = candidate_data['skills']
        skills_score, skills_details = self.calculate_skills_match(candidate_skills, job_requirements)
        factors['skills'] = {
            'score': skills_score,
            'weight': self.WEIGHTS['skills_match'],
            'details': skills_details
        }

        # Experience match
        candidate_experience = []
        if candidate_data and 'experience' in candidate_data:
            candidate_experience = candidate_data['experience']
        experience_score, experience_details = self.calculate_experience_match(
            candidate_experience, job_title, job_vertical
        )
        factors['experience'] = {
            'score': experience_score,
            'weight': self.WEIGHTS['experience_match'],
            'details': experience_details
        }

        # Location match
        candidate_location = None
        if candidate_data and 'location' in candidate_data:
            candidate_location = candidate_data['location']
        location_match, location_details = self.calculate_location_match(candidate_location, job_location)
        location_score = 10.0 if location_match else 0.0
        factors['location'] = {
            'score': location_score,
            'match': location_match,
            'weight': self.WEIGHTS['location_match'],
            'details': location_details
        }

        # Calculate weighted overall score (0-100)
        overall_score = (
            interview_score * 10 * self.WEIGHTS['interview_score'] +
            skills_score * 10 * self.WEIGHTS['skills_match'] +
            experience_score * 10 * self.WEIGHTS['experience_match'] +
            location_score * 10 * self.WEIGHTS['location_match']
        )

        # Calculate preference boost (new)
        preference_boost, boost_details = self.calculate_preference_boost(
            candidate_preferences,
            job_company_stage,
            job_location,
            job_industry,
        )
        factors['preference_boost'] = boost_details

        # Apply boost (capped at 100)
        boosted_score = min(100.0, overall_score + preference_boost)

        # Generate reasoning
        ai_reasoning = self._generate_reasoning(
            interview_score, skills_score, experience_score, location_match, factors
        )

        # Add boost info to reasoning if applicable
        if preference_boost > 0:
            boost_matches = boost_details.get("matches", [])
            ai_reasoning = f"{ai_reasoning} Preference boost: +{int(preference_boost)} ({', '.join(boost_matches)})."

        return MatchResult(
            interview_score=interview_score,
            skills_match_score=skills_score,
            experience_match_score=experience_score,
            location_match=location_match,
            overall_match_score=round(overall_score, 1),
            factors=factors,
            ai_reasoning=ai_reasoning,
            preference_boost=preference_boost,
            boosted_match_score=round(boosted_score, 1),
        )

    def _generate_reasoning(
        self,
        interview_score: float,
        skills_score: float,
        experience_score: float,
        location_match: bool,
        factors: dict
    ) -> str:
        """Generate human-readable reasoning for the match score."""
        parts = []

        # Interview assessment
        if interview_score >= 8:
            parts.append("Excellent interview performance")
        elif interview_score >= 6:
            parts.append("Good interview performance")
        else:
            parts.append("Interview performance needs improvement")

        # Skills assessment
        if skills_score >= 8:
            parts.append("strong skills match")
        elif skills_score >= 5:
            parts.append("adequate skills coverage")
        else:
            skills_details = factors.get('skills', {}).get('details', {})
            missing = skills_details.get('missing', [])
            if missing:
                parts.append(f"missing some required skills ({', '.join(missing[:3])})")
            else:
                parts.append("skills gap identified")

        # Experience assessment
        if experience_score >= 8:
            parts.append("highly relevant experience")
        elif experience_score >= 5:
            parts.append("relevant background")
        else:
            parts.append("limited relevant experience")

        # Location
        if not location_match:
            parts.append("location may be a concern")

        return "; ".join(parts) + "."


    # ==========================================
    # ENHANCED ML-POWERED MATCHING
    # ==========================================

    async def calculate_enhanced_match(
        self,
        interview_score: float,
        candidate_data: Optional[dict],
        job_title: str,
        job_requirements: list[str],
        job_location: Optional[str] = None,
        job_vertical: Optional[str] = None,
        github_data: Optional[dict] = None,
        education_data: Optional[dict] = None,
        interview_history: Optional[list] = None,
    ) -> EnhancedMatchResult:
        """
        Calculate enhanced match score with ML-powered insights.

        Args:
            interview_score: Score from completed interview (0-10)
            candidate_data: Parsed resume data dict
            job_title: Job title
            job_requirements: List of job requirements
            job_location: Job location
            job_vertical: Vertical (engineering, data, etc.)
            github_data: GitHub profile data
            education_data: Education information
            interview_history: List of past interviews for trajectory

        Returns:
            EnhancedMatchResult with detailed insights
        """
        factors = {}

        # Interview score (already 0-10)
        interview_score = min(10.0, max(0.0, interview_score))
        factors['interview'] = {
            'score': interview_score,
            'weight': self.BASE_WEIGHTS['interview_score']
        }

        # Enhanced skills match with semantic matching
        candidate_skills = []
        if candidate_data and 'skills' in candidate_data:
            candidate_skills = candidate_data['skills']

        # Add GitHub languages as skills
        if github_data and github_data.get('languages'):
            github_langs = list(github_data['languages'].keys()) if isinstance(github_data['languages'], dict) else github_data['languages']
            candidate_skills = list(set(candidate_skills + [l.lower() for l in github_langs]))

        skills_score, skills_details = self.calculate_enhanced_skills_match(
            candidate_skills, job_requirements
        )
        factors['skills'] = {
            'score': skills_score,
            'weight': self.BASE_WEIGHTS['skills_match'],
            'details': skills_details
        }

        # Experience match
        candidate_experience = []
        if candidate_data and 'experience' in candidate_data:
            candidate_experience = candidate_data['experience']
        experience_score, experience_details = self.calculate_experience_match(
            candidate_experience, job_title, job_vertical
        )
        factors['experience'] = {
            'score': experience_score,
            'weight': self.BASE_WEIGHTS['experience_match'],
            'details': experience_details
        }

        # GitHub signal score (new)
        github_score, github_details = self.calculate_github_signal(github_data, job_vertical)
        factors['github'] = {
            'score': github_score,
            'weight': self.BASE_WEIGHTS['github_signal'],
            'details': github_details
        }

        # Education score (new)
        edu_score, edu_details = self.calculate_education_score(education_data, job_vertical)
        factors['education'] = {
            'score': edu_score,
            'weight': self.BASE_WEIGHTS['education'],
            'details': edu_details
        }

        # Location match
        candidate_location = None
        if candidate_data and 'location' in candidate_data:
            candidate_location = candidate_data['location']
        location_match, location_details = self.calculate_location_match(candidate_location, job_location)
        location_score = 10.0 if location_match else 0.0
        factors['location'] = {
            'score': location_score,
            'match': location_match,
            'weight': self.BASE_WEIGHTS['location_match'],
            'details': location_details
        }

        # Growth trajectory (if history available)
        trajectory_score, trajectory_details = self.calculate_growth_trajectory(interview_history)
        factors['trajectory'] = {
            'score': trajectory_score,
            'details': trajectory_details
        }

        # Calculate weighted overall score (0-100)
        overall_score = (
            interview_score * 10 * self.BASE_WEIGHTS['interview_score'] +
            skills_score * 10 * self.BASE_WEIGHTS['skills_match'] +
            experience_score * 10 * self.BASE_WEIGHTS['experience_match'] +
            github_score * 10 * self.BASE_WEIGHTS['github_signal'] +
            edu_score * 10 * self.BASE_WEIGHTS['education'] +
            location_score * 10 * self.BASE_WEIGHTS['location_match']
        )

        # Apply trajectory bonus
        if trajectory_score >= 8:
            overall_score = min(100, overall_score + 5)

        # Generate skill gap summary
        skill_gap_summary = self._generate_skill_gap_summary(skills_details)

        # Extract insights
        top_strengths = self._extract_strengths(factors)
        areas_for_growth = self._extract_growth_areas(factors, skills_details)

        # Generate hiring recommendation
        hiring_recommendation = self._generate_hiring_recommendation(
            overall_score, factors, skill_gap_summary
        )

        # Calculate confidence
        confidence = self._calculate_confidence(factors, candidate_data, github_data)

        # Generate reasoning
        ai_reasoning = self._generate_enhanced_reasoning(factors)

        return EnhancedMatchResult(
            interview_score=interview_score,
            skills_match_score=skills_score,
            experience_match_score=experience_score,
            location_match=location_match,
            overall_match_score=round(overall_score, 1),
            factors=factors,
            ai_reasoning=ai_reasoning,
            github_signal_score=github_score,
            education_score=edu_score,
            growth_trajectory_score=trajectory_score,
            skill_gap_summary=skill_gap_summary,
            top_strengths=top_strengths,
            areas_for_growth=areas_for_growth,
            hiring_recommendation=hiring_recommendation,
            confidence_score=confidence
        )

    def calculate_enhanced_skills_match(
        self,
        candidate_skills: list[str],
        job_requirements: list[str]
    ) -> tuple[float, dict]:
        """
        Enhanced skills matching with semantic understanding.

        Uses:
        - Exact matching
        - Synonym matching
        - Related skill detection
        - Partial matching
        """
        if not job_requirements:
            return 7.0, {"matched": [], "missing": [], "semantic_matches": [], "reason": "No specific requirements"}

        if not candidate_skills:
            return 3.0, {"matched": [], "missing": job_requirements, "semantic_matches": [], "reason": "No skills listed"}

        # Normalize skills
        candidate_lower = set(s.lower().strip() for s in candidate_skills)
        requirements_lower = [r.lower().strip() for r in job_requirements]

        matched = []
        semantic_matches = []
        related_matches = []
        missing = []

        for req in requirements_lower:
            match_type = None
            matched_skill = None

            # 1. Check for exact match
            if req in candidate_lower:
                match_type = "exact"
                matched_skill = req
            else:
                # 2. Check synonyms
                for candidate_skill in candidate_lower:
                    if self._is_synonym_match(req, candidate_skill):
                        match_type = "synonym"
                        matched_skill = candidate_skill
                        break

                # 3. Check for related skills
                if not match_type:
                    for candidate_skill in candidate_lower:
                        if self._is_related_skill(req, candidate_skill):
                            match_type = "related"
                            matched_skill = candidate_skill
                            break

                # 4. Check for partial match
                if not match_type:
                    for candidate_skill in candidate_lower:
                        if req in candidate_skill or candidate_skill in req:
                            match_type = "partial"
                            matched_skill = candidate_skill
                            break

            if match_type:
                if match_type == "exact":
                    matched.append(req)
                elif match_type in ["synonym", "partial"]:
                    semantic_matches.append({
                        "requirement": req,
                        "matched_by": matched_skill,
                        "match_type": match_type
                    })
                    matched.append(req)
                elif match_type == "related":
                    related_matches.append({
                        "requirement": req,
                        "related_skill": matched_skill,
                        "match_type": "related"
                    })
                    # Related skills count as partial match
                    matched.append(req)
            else:
                missing.append(req)

        # Calculate score
        total_reqs = len(requirements_lower)
        exact_matches = len(matched) - len(semantic_matches) - len(related_matches)
        semantic_count = len(semantic_matches)
        related_count = len(related_matches)

        if total_reqs == 0:
            score = 7.0
            match_pct = 100
        else:
            # Weighted matching score
            # Exact matches: full credit
            # Semantic matches: 90% credit
            # Related matches: 70% credit
            weighted_matches = exact_matches + (semantic_count * 0.9) + (related_count * 0.7)
            match_pct = (weighted_matches / total_reqs) * 100
            score = (weighted_matches / total_reqs) * 10

            # Bonus for having more skills than required
            if len(candidate_skills) > total_reqs:
                score = min(10.0, score + 0.5)

        return round(score, 1), {
            "matched": matched,
            "missing": missing,
            "semantic_matches": semantic_matches,
            "related_matches": related_matches,
            "match_percentage": round(match_pct, 1),
            "exact_match_count": exact_matches,
            "semantic_match_count": semantic_count,
            "related_match_count": related_count
        }

    def _is_synonym_match(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are synonyms."""
        # Direct fuzzy match
        if self._fuzzy_match(skill1, skill2):
            return True

        # Check comprehensive synonym list
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()

        # Check if skill2 is in skill1's synonyms
        synonyms1 = SKILL_SYNONYMS.get(skill1_lower, [])
        if skill2_lower in synonyms1:
            return True

        # Check if skill1 is in skill2's synonyms
        synonyms2 = SKILL_SYNONYMS.get(skill2_lower, [])
        if skill1_lower in synonyms2:
            return True

        # Check if they share the same canonical form
        for canonical, syns in SKILL_SYNONYMS.items():
            if skill1_lower in syns and skill2_lower in syns:
                return True
            if skill1_lower == canonical and skill2_lower in syns:
                return True
            if skill2_lower == canonical and skill1_lower in syns:
                return True

        return False

    def _is_related_skill(self, required: str, candidate_has: str) -> bool:
        """Check if candidate skill is related to required skill."""
        required_lower = required.lower()
        candidate_lower = candidate_has.lower()

        # Check if candidate has a related skill
        related = RELATED_SKILLS.get(candidate_lower, [])
        if required_lower in [r.lower() for r in related]:
            return True

        # Check reverse (required skill is related to what candidate has)
        for skill, related_list in RELATED_SKILLS.items():
            if required_lower == skill.lower():
                if candidate_lower in [r.lower() for r in related_list]:
                    return True

        return False

    def calculate_github_signal(
        self,
        github_data: Optional[dict],
        job_vertical: Optional[str] = None
    ) -> tuple[float, dict]:
        """
        Calculate GitHub signal score.

        Evaluates:
        - Language diversity and relevance
        - Contribution frequency
        - Repository quality
        - Open source participation
        """
        if not github_data:
            return 5.0, {"available": False, "reason": "No GitHub data"}

        score = 5.0  # Base score
        details = {"available": True}

        # Language analysis
        languages = github_data.get('languages', {})
        if languages:
            lang_count = len(languages) if isinstance(languages, dict) else len(languages)
            details['language_count'] = lang_count

            # Bonus for diverse languages
            if lang_count >= 5:
                score += 1.5
            elif lang_count >= 3:
                score += 1.0

            # Bonus for relevant languages
            relevant_langs = {
                'engineering': ['javascript', 'typescript', 'python', 'java', 'go', 'rust', 'c++'],
                'data': ['python', 'r', 'julia', 'sql', 'scala'],
            }
            if job_vertical and job_vertical in relevant_langs:
                lang_list = [l.lower() for l in (languages.keys() if isinstance(languages, dict) else languages)]
                matches = sum(1 for l in lang_list if l in relevant_langs[job_vertical])
                if matches >= 2:
                    score += 1.0

        # Contribution analysis
        contributions = github_data.get('total_contributions', 0)
        if contributions:
            details['contributions'] = contributions
            if contributions >= 1000:
                score += 2.0
            elif contributions >= 500:
                score += 1.5
            elif contributions >= 100:
                score += 1.0
            elif contributions >= 50:
                score += 0.5

        # Repository analysis
        repos = github_data.get('repos') or github_data.get('top_repos') or []
        if repos:
            details['repo_count'] = len(repos)

            # Check for repos with stars
            starred_repos = [r for r in repos if (r.get('stars') or r.get('stargazers_count', 0)) > 0]
            if starred_repos:
                total_stars = sum(r.get('stars') or r.get('stargazers_count', 0) for r in starred_repos)
                details['total_stars'] = total_stars
                if total_stars >= 100:
                    score += 1.5
                elif total_stars >= 10:
                    score += 0.5

        return min(10.0, round(score, 1)), details

    def calculate_education_score(
        self,
        education_data: Optional[dict],
        job_vertical: Optional[str] = None
    ) -> tuple[float, dict]:
        """
        Calculate education quality score.

        Evaluates:
        - University prestige
        - Degree relevance
        - GPA (if available)
        """
        if not education_data:
            return 5.0, {"available": False, "reason": "No education data"}

        score = 5.0  # Base score
        details = {"available": True}

        # University tier
        university = (education_data.get('university') or '').lower()
        details['university'] = education_data.get('university')

        university_tier = None
        for tier, schools in TOP_UNIVERSITIES.items():
            for school in schools:
                if school in university:
                    university_tier = tier
                    break
            if university_tier:
                break

        if university_tier == 'tier_1':
            score += 3.0
            details['university_tier'] = 'top'
        elif university_tier == 'tier_2':
            score += 2.0
            details['university_tier'] = 'excellent'
        else:
            details['university_tier'] = 'standard'

        # Major relevance
        major = (education_data.get('major') or '').lower()
        details['major'] = education_data.get('major')

        relevant_majors = {
            'engineering': ['computer science', 'cs', 'software', 'electrical', 'computer engineering'],
            'data': ['data science', 'statistics', 'math', 'computer science', 'economics', 'physics'],
            'business': ['business', 'mba', 'economics', 'finance', 'marketing'],
            'design': ['design', 'hci', 'human-computer', 'art', 'graphic'],
        }

        if job_vertical and job_vertical in relevant_majors:
            for relevant_major in relevant_majors[job_vertical]:
                if relevant_major in major:
                    score += 1.0
                    details['major_relevance'] = 'high'
                    break
        else:
            # Default check for technical majors
            if any(m in major for m in ['computer', 'engineering', 'science', 'math']):
                score += 0.5
                details['major_relevance'] = 'medium'

        # GPA
        gpa = education_data.get('gpa')
        if gpa:
            details['gpa'] = gpa
            if gpa >= 3.8:
                score += 1.0
            elif gpa >= 3.5:
                score += 0.5

        return min(10.0, round(score, 1)), details

    def calculate_growth_trajectory(
        self,
        interview_history: Optional[list]
    ) -> tuple[float, dict]:
        """
        Calculate growth trajectory score from interview history.

        Evaluates:
        - Score improvement over time
        - Consistency
        - Recent performance
        """
        if not interview_history or len(interview_history) < 2:
            return 5.0, {"available": False, "reason": "Insufficient history"}

        # Sort by date
        sorted_history = sorted(interview_history, key=lambda x: x.get('completed_at', ''))

        scores = [h.get('overall_score', 0) for h in sorted_history]
        details = {
            "available": True,
            "interview_count": len(scores),
            "first_score": scores[0],
            "latest_score": scores[-1],
        }

        # Calculate improvement
        improvement = scores[-1] - scores[0]
        details['total_improvement'] = round(improvement, 2)

        # Calculate trajectory score
        score = 5.0

        # Significant improvement bonus
        if improvement >= 2.0:
            score += 3.0
            details['trajectory'] = 'strong_growth'
        elif improvement >= 1.0:
            score += 2.0
            details['trajectory'] = 'good_growth'
        elif improvement >= 0.5:
            score += 1.0
            details['trajectory'] = 'moderate_growth'
        elif improvement >= 0:
            details['trajectory'] = 'stable'
        else:
            score -= 1.0
            details['trajectory'] = 'declining'

        # Consistency bonus (low variance)
        if len(scores) >= 3:
            avg = sum(scores) / len(scores)
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)
            if variance < 1.0:
                score += 1.0
                details['consistency'] = 'high'

        # Recent performance bonus
        if scores[-1] >= 8.0:
            score += 1.0
            details['recent_performance'] = 'excellent'
        elif scores[-1] >= 7.0:
            score += 0.5
            details['recent_performance'] = 'good'

        return min(10.0, round(score, 1)), details

    def _generate_skill_gap_summary(self, skills_details: dict) -> dict:
        """Generate a summary of skill gaps."""
        return {
            "match_percentage": skills_details.get("match_percentage", 0),
            "matched_count": len(skills_details.get("matched", [])),
            "missing_count": len(skills_details.get("missing", [])),
            "missing_skills": skills_details.get("missing", [])[:5],
            "semantic_matches": len(skills_details.get("semantic_matches", [])),
            "has_critical_gaps": len(skills_details.get("missing", [])) > 3
        }

    def _extract_strengths(self, factors: dict) -> list[str]:
        """Extract top strengths from factors."""
        strengths = []

        if factors.get('interview', {}).get('score', 0) >= 8:
            strengths.append("Excellent interview performance")

        if factors.get('skills', {}).get('score', 0) >= 8:
            strengths.append("Strong technical skills match")

        if factors.get('github', {}).get('score', 0) >= 8:
            details = factors.get('github', {}).get('details', {})
            if details.get('total_stars', 0) > 10:
                strengths.append("Active open source contributor")
            else:
                strengths.append("Strong GitHub presence")

        if factors.get('education', {}).get('score', 0) >= 8:
            details = factors.get('education', {}).get('details', {})
            if details.get('university_tier') == 'top':
                strengths.append(f"Top-tier university ({details.get('university', 'N/A')})")
            else:
                strengths.append("Strong educational background")

        if factors.get('experience', {}).get('score', 0) >= 8:
            strengths.append("Highly relevant work experience")

        if factors.get('trajectory', {}).get('score', 0) >= 8:
            strengths.append("Strong growth trajectory")

        return strengths[:5]

    def _extract_growth_areas(self, factors: dict, skills_details: dict) -> list[str]:
        """Extract areas for growth."""
        areas = []

        # Skill gaps
        missing = skills_details.get('missing', [])
        if missing:
            areas.append(f"Build skills in: {', '.join(missing[:3])}")

        if factors.get('interview', {}).get('score', 0) < 6:
            areas.append("Improve interview communication skills")

        if factors.get('github', {}).get('score', 0) < 5:
            areas.append("Increase GitHub activity and contributions")

        if factors.get('experience', {}).get('score', 0) < 5:
            areas.append("Gain more relevant work experience")

        return areas[:3]

    def _generate_hiring_recommendation(
        self,
        overall_score: float,
        factors: dict,
        skill_gap_summary: dict
    ) -> str:
        """Generate hiring recommendation."""
        if overall_score >= 85:
            return "Strong Hire - Exceptional candidate with excellent fit"
        elif overall_score >= 75:
            if skill_gap_summary.get('has_critical_gaps'):
                return "Hire - Strong candidate, minor skill gaps easily addressed"
            return "Hire - Well-qualified candidate"
        elif overall_score >= 65:
            return "Lean Hire - Good potential, some development needed"
        elif overall_score >= 55:
            return "Maybe - Consider if skills gaps can be addressed"
        else:
            return "No Hire - Significant gaps in requirements"

    def _calculate_confidence(
        self,
        factors: dict,
        candidate_data: Optional[dict],
        github_data: Optional[dict]
    ) -> float:
        """Calculate confidence score for the match result."""
        confidence = 0.5  # Base

        # More data = higher confidence
        if candidate_data:
            confidence += 0.2
        if github_data and github_data.get('languages'):
            confidence += 0.15
        if factors.get('education', {}).get('details', {}).get('available'):
            confidence += 0.1
        if factors.get('trajectory', {}).get('details', {}).get('available'):
            confidence += 0.05

        return min(1.0, round(confidence, 2))

    def _generate_enhanced_reasoning(self, factors: dict) -> str:
        """Generate comprehensive reasoning for the match score."""
        parts = []

        # Interview
        interview_score = factors.get('interview', {}).get('score', 0)
        if interview_score >= 8:
            parts.append("Excellent interview performance")
        elif interview_score >= 6:
            parts.append("Good interview performance")
        else:
            parts.append("Interview performance needs improvement")

        # Skills
        skills_score = factors.get('skills', {}).get('score', 0)
        skills_details = factors.get('skills', {}).get('details', {})
        if skills_score >= 8:
            parts.append("strong technical skills match")
        elif skills_score >= 6:
            semantic_count = len(skills_details.get('semantic_matches', []))
            if semantic_count > 0:
                parts.append(f"good skills coverage ({semantic_count} related skills)")
            else:
                parts.append("adequate skills coverage")
        else:
            missing = skills_details.get('missing', [])
            if missing:
                parts.append(f"missing key skills ({', '.join(missing[:2])})")

        # GitHub
        github_score = factors.get('github', {}).get('score', 0)
        if github_score >= 7:
            parts.append("strong GitHub presence")
        elif github_score < 5 and factors.get('github', {}).get('details', {}).get('available'):
            parts.append("limited GitHub activity")

        # Education
        edu_details = factors.get('education', {}).get('details', {})
        if edu_details.get('university_tier') == 'top':
            parts.append("top-tier education")

        # Trajectory
        trajectory_details = factors.get('trajectory', {}).get('details', {})
        if trajectory_details.get('trajectory') == 'strong_growth':
            parts.append("excellent growth trajectory")

        # Location
        if not factors.get('location', {}).get('match', True):
            parts.append("location may be a concern")

        return "; ".join(parts) + "."


# Global instance
matching_service = MatchingService()

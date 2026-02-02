"""
Matching service for scoring candidate-job fit.
Uses interview scores, resume data, and job requirements to calculate match scores.
"""

import json
import httpx
from typing import Optional
from dataclasses import dataclass
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


class MatchingService:
    """Service for calculating candidate-job match scores."""

    # Weights for overall score calculation
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

    async def calculate_match(
        self,
        interview_score: float,  # 0-10
        candidate_data: Optional[dict],  # Parsed resume data as dict
        job_title: str,
        job_requirements: list[str],
        job_location: Optional[str] = None,
        job_vertical: Optional[str] = None,
    ) -> MatchResult:
        """
        Calculate overall match score for a candidate-job pair.

        Args:
            interview_score: Score from completed interview (0-10)
            candidate_data: Parsed resume data dict
            job_title: Job title
            job_requirements: List of job requirements
            job_location: Job location
            job_vertical: 'new_energy' or 'sales'

        Returns:
            MatchResult with all scoring details
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

        # Generate reasoning
        ai_reasoning = self._generate_reasoning(
            interview_score, skills_score, experience_score, location_match, factors
        )

        return MatchResult(
            interview_score=interview_score,
            skills_match_score=skills_score,
            experience_match_score=experience_score,
            location_match=location_match,
            overall_match_score=round(overall_score, 1),
            factors=factors,
            ai_reasoning=ai_reasoning
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


# Global instance
matching_service = MatchingService()

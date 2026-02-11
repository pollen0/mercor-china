"""
Comprehensive Profile Scoring Service.

Computes candidate profile scores using all available data:
- Education: University tier, major rigor, GPA (adjusted), honors
- Technical: Skills depth, breadth, relevance, courses taken
- Experience: Company tier, role relevance, impact
- GitHub: Uses existing GitHubAnalysis scores
- Activities: Club prestige, role tier, awards

Replaces the old on-the-fly scoring with persistent, auditable scores.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.candidate import Candidate
from ..models.course import University, Course, CandidateTranscript
from ..models.major import Major
from ..models.activity import Club, CandidateActivity, CandidateAward
from ..models.github_analysis import GitHubAnalysis
from ..models.profile_score import CandidateProfileScore, SCORING_VERSION

logger = logging.getLogger("pathway.profile_scoring")


# Company tier mappings for experience scoring
TOP_COMPANIES = {
    "faang": ["meta", "facebook", "apple", "amazon", "netflix", "google", "alphabet", "microsoft"],
    "tier_1": ["stripe", "uber", "lyft", "airbnb", "dropbox", "twitter", "linkedin", "snap", "pinterest",
               "doordash", "instacart", "coinbase", "robinhood", "palantir", "databricks", "snowflake",
               "openai", "anthropic", "nvidia", "tesla", "spacex", "square", "block", "plaid", "ramp", "brex"],
    "tier_2": ["salesforce", "adobe", "oracle", "ibm", "cisco", "intel", "amd", "qualcomm", "vmware",
               "workday", "servicenow", "splunk", "twilio", "atlassian", "shopify", "square", "mongodb",
               "elastic", "datadog", "cloudflare", "figma", "notion", "airtable", "retool", "vercel"],
}


def clamp(value: float, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Clamp a value to the given range."""
    if value is None:
        return min_val
    return max(min_val, min(max_val, float(value)))


def weighted_average(breakdown: dict) -> float:
    """Calculate weighted average from a breakdown dict with score/weight pairs."""
    if not breakdown:
        return 5.0  # Default middle score

    total_weight = sum(item.get("weight", 0) for item in breakdown.values() if isinstance(item, dict))
    if total_weight == 0:
        return 5.0

    weighted_sum = sum(
        item.get("score", 5.0) * item.get("weight", 0)
        for item in breakdown.values()
        if isinstance(item, dict)
    )
    return clamp(weighted_sum / total_weight)


class ProfileScoringService:
    """
    Service for computing comprehensive candidate profile scores.

    Uses all available data to produce a fair, auditable score with
    detailed breakdowns explaining the rationale for each component.
    """

    # Component weights for overall score
    WEIGHTS = {
        "education": 0.25,
        "technical": 0.20,
        "experience": 0.20,
        "github": 0.15,
        "activities": 0.20,
    }

    def __init__(self, db: Session):
        self.db = db

    async def compute_score(self, candidate_id: str) -> CandidateProfileScore:
        """
        Compute comprehensive profile score for a candidate.

        Returns a CandidateProfileScore object with full breakdown and rationale.
        """
        candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        # Gather all data
        university = self._match_university(candidate)
        major = self._match_major(candidate, university)
        activities = self.db.query(CandidateActivity).filter(
            CandidateActivity.candidate_id == candidate_id
        ).all()
        awards = self.db.query(CandidateAward).filter(
            CandidateAward.candidate_id == candidate_id
        ).all()
        github_analysis = self.db.query(GitHubAnalysis).filter(
            GitHubAnalysis.candidate_id == candidate_id
        ).first()
        transcript = self.db.query(CandidateTranscript).filter(
            CandidateTranscript.candidate_id == candidate_id
        ).first()

        # Compute each component
        education_result = self._compute_education(candidate, university, major)
        technical_result = self._compute_technical(candidate, transcript)
        experience_result = self._compute_experience(candidate)
        github_result = self._compute_github(candidate, github_analysis)
        activities_result = self._compute_activities(activities, awards)

        # Calculate weighted total
        components = {
            "education": education_result,
            "technical": technical_result,
            "experience": experience_result,
            "github": github_result,
            "activities": activities_result,
        }

        total_score = sum(
            comp["score"] * self.WEIGHTS[name]
            for name, comp in components.items()
        )

        # Build raw inputs snapshot for debugging
        raw_inputs = {
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "university": candidate.university,
                "major": candidate.major,
                "gpa": candidate.gpa,
                "graduation_year": candidate.graduation_year,
            },
            "university_matched": university.id if university else None,
            "major_matched": major.id if major else None,
            "github_analysis_id": github_analysis.id if github_analysis else None,
            "activities_count": len(activities),
            "awards_count": len(awards),
        }

        # Create or update score record
        existing = self.db.query(CandidateProfileScore).filter(
            CandidateProfileScore.candidate_id == candidate_id
        ).first()

        if existing:
            score_record = existing
            score_record.total_score = round(total_score, 2)
            score_record.education_score = round(education_result["score"], 2)
            score_record.technical_score = round(technical_result["score"], 2)
            score_record.experience_score = round(experience_result["score"], 2)
            score_record.github_score = round(github_result["score"], 2)
            score_record.activities_score = round(activities_result["score"], 2)
            score_record.education_breakdown = education_result["breakdown"]
            score_record.technical_breakdown = technical_result["breakdown"]
            score_record.experience_breakdown = experience_result["breakdown"]
            score_record.github_breakdown = github_result["breakdown"]
            score_record.activities_breakdown = activities_result["breakdown"]
            score_record.scoring_version = SCORING_VERSION
            score_record.computed_at = datetime.utcnow()
            score_record.raw_inputs = raw_inputs
        else:
            score_record = CandidateProfileScore(
                id=f"cps_{uuid4().hex[:24]}",
                candidate_id=candidate_id,
                total_score=round(total_score, 2),
                education_score=round(education_result["score"], 2),
                technical_score=round(technical_result["score"], 2),
                experience_score=round(experience_result["score"], 2),
                github_score=round(github_result["score"], 2),
                activities_score=round(activities_result["score"], 2),
                education_breakdown=education_result["breakdown"],
                technical_breakdown=technical_result["breakdown"],
                experience_breakdown=experience_result["breakdown"],
                github_breakdown=github_result["breakdown"],
                activities_breakdown=activities_result["breakdown"],
                scoring_version=SCORING_VERSION,
                raw_inputs=raw_inputs,
            )
            self.db.add(score_record)

        self.db.commit()
        self.db.refresh(score_record)

        logger.info(f"Computed score for {candidate.name}: {score_record.total_score}")
        return score_record

    def _match_university(self, candidate: Candidate) -> Optional[University]:
        """Match candidate's university string to universities table."""
        # First check if already linked
        if candidate.university_id:
            return self.db.query(University).filter(University.id == candidate.university_id).first()

        if not candidate.university:
            return None

        uni_lower = candidate.university.lower().strip()

        # Try exact match on id
        uni = self.db.query(University).filter(University.id == uni_lower).first()
        if uni:
            # Update candidate with FK
            candidate.university_id = uni.id
            return uni

        # Try fuzzy match on name or short_name
        uni = self.db.query(University).filter(
            (func.lower(University.name).contains(uni_lower)) |
            (func.lower(University.short_name).contains(uni_lower)) |
            (func.lower(University.id).contains(uni_lower.replace("_", "").replace(" ", "")))
        ).first()

        if uni:
            candidate.university_id = uni.id
            return uni

        # Common mappings
        mappings = {
            "uc berkeley": "berkeley",
            "uc_berkeley": "berkeley",
            "cal": "berkeley",
            "uc san diego": "uc_san_diego",
            "ucsd": "uc_san_diego",
            "uc los angeles": "ucla",
            "uc davis": "uc_davis",
            "uc irvine": "uc_irvine",
            "uc santa barbara": "ucsb",
            "uc santa cruz": "ucsc",
            "university of illinois": "uiuc",
            "u of i": "uiuc",
            "university of michigan": "umich",
            "u of m": "umich",
            "university of washington": "uw",
            "georgia tech": "georgia_tech",
            "carnegie mellon": "cmu",
            "ut austin": "ut_austin",
            "university of texas": "ut_austin",
        }

        for pattern, uni_id in mappings.items():
            if pattern in uni_lower:
                uni = self.db.query(University).filter(University.id == uni_id).first()
                if uni:
                    candidate.university_id = uni.id
                    return uni

        return None

    def _match_major(self, candidate: Candidate, university: Optional[University]) -> Optional[Major]:
        """Match candidate's major string to majors table."""
        if candidate.major_id:
            return self.db.query(Major).filter(Major.id == candidate.major_id).first()

        if not candidate.major:
            return None

        major_lower = candidate.major.lower().strip()

        # If we have a matched university, try to find major at that school
        if university:
            major = self.db.query(Major).filter(
                Major.university_id == university.id,
                (func.lower(Major.name).contains(major_lower)) |
                (func.lower(Major.short_name) == major_lower)
            ).first()

            if major:
                candidate.major_id = major.id
                return major

        # Try generic match on common majors
        common_majors = {
            "eecs": ("engineering", True, True, 5, 9.5),
            "electrical engineering and computer science": ("engineering", True, True, 5, 9.5),
            "computer science": ("engineering", True, True, 5, 9.0),
            "cs": ("engineering", True, True, 5, 9.0),
            "computer engineering": ("engineering", True, True, 5, 8.5),
            "data science": ("engineering", True, True, 4, 8.0),
            "statistics": ("science", True, True, 4, 7.5),
            "mathematics": ("science", True, False, 4, 7.5),
            "physics": ("science", True, False, 4, 7.5),
            "electrical engineering": ("engineering", True, True, 4, 8.0),
            "mechanical engineering": ("engineering", True, False, 4, 7.5),
            "business": ("business", False, False, 3, 6.0),
            "economics": ("social_science", False, False, 3, 6.5),
            "finance": ("business", False, False, 3, 6.5),
        }

        for pattern, (category, is_stem, is_tech, tier, score) in common_majors.items():
            if pattern in major_lower:
                # Return a synthetic major-like object
                return type('Major', (), {
                    'id': None,
                    'name': candidate.major,
                    'short_name': pattern.upper(),
                    'rigor_tier': tier,
                    'rigor_score': score,
                    'is_stem': is_stem,
                    'is_technical': is_tech,
                    'field_category': category,
                    'average_gpa': None,
                })()

        return None

    def _compute_education(
        self,
        candidate: Candidate,
        university: Optional[University],
        major: Optional[Major]
    ) -> dict:
        """
        Compute education score with detailed breakdown.

        Sub-components:
        - GPA (25%): Adjusted for school/major difficulty
        - University Tier (30%): Based on CS ranking
        - Major Rigor (25%): STEM/technical majors score higher
        - Honors (20%): Awards, test scores, etc.
        """
        breakdown = {}

        # 1. GPA (25% weight)
        if candidate.gpa:
            base_gpa_score = (candidate.gpa / 4.0) * 10

            # Adjust for major difficulty if we have average GPA data
            if major and hasattr(major, 'average_gpa') and major.average_gpa:
                gpa_diff = candidate.gpa - major.average_gpa
                # +1 point for each 0.2 above average, -1 for each 0.2 below
                adjustment = gpa_diff * 5
                adjusted_score = clamp(base_gpa_score + adjustment)
                breakdown["gpa"] = {
                    "score": round(adjusted_score, 2),
                    "weight": 0.25,
                    "rationale": f"{candidate.gpa:.2f} GPA vs {major.average_gpa:.2f} avg for {major.short_name or major.name} ({'+' if gpa_diff >= 0 else ''}{gpa_diff:.2f})",
                    "data": {"raw_gpa": candidate.gpa, "major_avg": major.average_gpa}
                }
            else:
                breakdown["gpa"] = {
                    "score": round(base_gpa_score, 2),
                    "weight": 0.25,
                    "rationale": f"{candidate.gpa:.2f} GPA (no major avg data for adjustment)",
                    "data": {"raw_gpa": candidate.gpa}
                }
        else:
            breakdown["gpa"] = {
                "score": 5.0,
                "weight": 0.25,
                "rationale": "No GPA provided",
                "data": {}
            }

        # 2. University Tier (30% weight)
        if university:
            tier_scores = {1: 10.0, 2: 8.5, 3: 7.0, 4: 5.5, 5: 4.0}
            tier_score = tier_scores.get(university.tier, 5.0)
            breakdown["university"] = {
                "score": tier_score,
                "weight": 0.30,
                "rationale": f"{university.short_name} - Tier {university.tier}" + (f", CS #{university.cs_ranking}" if university.cs_ranking else ""),
                "data": {"university_id": university.id, "tier": university.tier, "cs_ranking": university.cs_ranking}
            }
        else:
            breakdown["university"] = {
                "score": 5.0,
                "weight": 0.30,
                "rationale": f"University not matched: {candidate.university or 'Not provided'}",
                "data": {"raw_university": candidate.university}
            }

        # 3. Major Rigor (25% weight)
        if major:
            breakdown["major"] = {
                "score": major.rigor_score if hasattr(major, 'rigor_score') else 5.0,
                "weight": 0.25,
                "rationale": f"{major.short_name or major.name} - Tier {major.rigor_tier}" + (" (STEM)" if major.is_stem else ""),
                "data": {"major_id": major.id if hasattr(major, 'id') else None, "rigor_tier": major.rigor_tier}
            }
        else:
            breakdown["major"] = {
                "score": 5.0,
                "weight": 0.25,
                "rationale": f"Major not matched: {candidate.major or 'Not provided'}",
                "data": {"raw_major": candidate.major}
            }

        # 4. Honors/Test Scores (20% weight)
        honors_score = 5.0
        honors_items = []

        # Check resume for honors
        if candidate.resume_parsed_data:
            awards = candidate.resume_parsed_data.get("awards", [])
            for award in awards:
                name = award.get("name", "").lower() if isinstance(award, dict) else str(award).lower()
                if any(h in name for h in ["valedictorian", "salutatorian", "summa cum laude", "magna cum laude"]):
                    honors_score = max(honors_score, 9.0)
                    honors_items.append(award.get("name", name) if isinstance(award, dict) else str(award))
                elif any(h in name for h in ["dean's list", "honor roll", "phi beta kappa"]):
                    honors_score = max(honors_score, 8.0)
                    honors_items.append(award.get("name", name) if isinstance(award, dict) else str(award))
                elif "sat" in name:
                    # Try to extract SAT score
                    try:
                        desc = award.get("description", "") if isinstance(award, dict) else ""
                        if desc and desc.isdigit():
                            sat = int(desc)
                            if sat >= 1550:
                                honors_score = max(honors_score, 9.5)
                            elif sat >= 1500:
                                honors_score = max(honors_score, 8.5)
                            elif sat >= 1400:
                                honors_score = max(honors_score, 7.5)
                            honors_items.append(f"SAT {sat}")
                    except (ValueError, TypeError):
                        pass
                elif "act" in name:
                    try:
                        desc = award.get("description", "") if isinstance(award, dict) else ""
                        if desc and desc.isdigit():
                            act = int(desc)
                            if act >= 35:
                                honors_score = max(honors_score, 9.5)
                            elif act >= 33:
                                honors_score = max(honors_score, 8.5)
                            elif act >= 30:
                                honors_score = max(honors_score, 7.5)
                            honors_items.append(f"ACT {act}")
                    except (ValueError, TypeError):
                        pass

        breakdown["honors"] = {
            "score": honors_score,
            "weight": 0.20,
            "rationale": ", ".join(honors_items) if honors_items else "No notable honors detected",
            "data": {"honors": honors_items}
        }

        return {
            "score": weighted_average(breakdown),
            "breakdown": breakdown
        }

    def _compute_technical(self, candidate: Candidate, transcript: Optional[CandidateTranscript]) -> dict:
        """
        Compute technical skills score.

        Sub-components:
        - Skill Breadth (25%): Number of distinct skill categories
        - Skill Depth (35%): Project complexity, frameworks used
        - Skill Relevance (25%): Relevance to target roles
        - Courses (15%): Technical courses taken
        """
        breakdown = {}
        parsed = candidate.resume_parsed_data or {}
        skills = parsed.get("skills", [])

        # 1. Skill Breadth (25% weight)
        skill_categories = set()
        category_map = {
            "python": "languages", "java": "languages", "javascript": "languages", "typescript": "languages",
            "c++": "languages", "c#": "languages", "go": "languages", "rust": "languages", "ruby": "languages",
            "react": "frontend", "vue": "frontend", "angular": "frontend", "html": "frontend", "css": "frontend",
            "node": "backend", "express": "backend", "django": "backend", "flask": "backend", "fastapi": "backend",
            "sql": "database", "postgresql": "database", "mysql": "database", "mongodb": "database", "redis": "database",
            "aws": "cloud", "gcp": "cloud", "azure": "cloud", "docker": "devops", "kubernetes": "devops",
            "tensorflow": "ml", "pytorch": "ml", "scikit": "ml", "pandas": "ml", "numpy": "ml",
            "git": "tools", "linux": "tools", "bash": "tools",
        }

        for skill in skills:
            skill_lower = skill.lower() if isinstance(skill, str) else ""
            for pattern, category in category_map.items():
                if pattern in skill_lower:
                    skill_categories.add(category)

        breadth_score = min(10, 5.0 + len(skill_categories) * 0.8)
        breakdown["skill_breadth"] = {
            "score": round(breadth_score, 2),
            "weight": 0.25,
            "rationale": f"{len(skill_categories)} skill categories ({', '.join(sorted(skill_categories)[:5])})",
            "data": {"categories": list(skill_categories), "count": len(skill_categories)}
        }

        # 2. Skill Depth (35% weight) - based on projects
        projects = parsed.get("projects", [])
        depth_score = 5.0

        if projects:
            # Check for complex technologies
            complex_tech = ["kubernetes", "tensorflow", "pytorch", "aws", "gcp", "microservices", "distributed"]
            total_tech_count = 0
            complex_count = 0

            for project in projects:
                techs = project.get("technologies", [])
                total_tech_count += len(techs)
                for tech in techs:
                    if any(ct in tech.lower() for ct in complex_tech):
                        complex_count += 1

            if len(projects) >= 3 and total_tech_count >= 10:
                depth_score = 8.5
            elif len(projects) >= 2 and total_tech_count >= 6:
                depth_score = 7.5
            elif len(projects) >= 1:
                depth_score = 6.5

            if complex_count >= 2:
                depth_score = min(10, depth_score + 1.0)

        breakdown["skill_depth"] = {
            "score": round(depth_score, 2),
            "weight": 0.35,
            "rationale": f"{len(projects)} projects with diverse tech stack" if projects else "No projects in resume",
            "data": {"project_count": len(projects)}
        }

        # 3. Skill Relevance (25% weight)
        relevance_score = 5.0
        relevant_skills = ["python", "java", "javascript", "react", "sql", "git", "aws", "docker"]
        relevant_count = sum(1 for s in skills if any(r in s.lower() for r in relevant_skills))

        if relevant_count >= 6:
            relevance_score = 9.0
        elif relevant_count >= 4:
            relevance_score = 7.5
        elif relevant_count >= 2:
            relevance_score = 6.0

        breakdown["skill_relevance"] = {
            "score": round(relevance_score, 2),
            "weight": 0.25,
            "rationale": f"{relevant_count} industry-relevant skills",
            "data": {"relevant_count": relevant_count, "total_skills": len(skills)}
        }

        # 4. Courses (15% weight)
        courses_score = 5.0
        if transcript and transcript.transcript_score:
            courses_score = transcript.transcript_score / 10  # Convert 0-100 to 0-10
            breakdown["courses"] = {
                "score": round(courses_score, 2),
                "weight": 0.15,
                "rationale": f"Transcript score: {transcript.transcript_score:.1f}",
                "data": {"transcript_score": transcript.transcript_score}
            }
        else:
            # Use courses from candidate profile
            course_count = len(candidate.courses) if candidate.courses else 0
            if course_count >= 10:
                courses_score = 7.5
            elif course_count >= 5:
                courses_score = 6.0

            breakdown["courses"] = {
                "score": round(courses_score, 2),
                "weight": 0.15,
                "rationale": f"{course_count} courses listed" if course_count > 0 else "No transcript data",
                "data": {"course_count": course_count}
            }

        return {
            "score": weighted_average(breakdown),
            "breakdown": breakdown
        }

    def _compute_experience(self, candidate: Candidate) -> dict:
        """
        Compute experience score.

        Sub-components:
        - Company Tier (35%): FAANG > Tier 1 startups > Others
        - Role Relevance (30%): SWE/DS roles vs unrelated
        - Impact (20%): Keywords indicating impact
        - Progression (15%): Growth over time
        """
        breakdown = {}
        parsed = candidate.resume_parsed_data or {}
        experiences = parsed.get("experience", [])

        if not experiences:
            return {
                "score": 5.0,
                "breakdown": {
                    "company_tier": {"score": 5.0, "weight": 0.35, "rationale": "No work experience listed"},
                    "role_relevance": {"score": 5.0, "weight": 0.30, "rationale": "No work experience listed"},
                    "impact": {"score": 5.0, "weight": 0.20, "rationale": "No work experience listed"},
                    "progression": {"score": 5.0, "weight": 0.15, "rationale": "No work experience listed"},
                }
            }

        # 1. Company Tier (35% weight)
        company_scores = []
        company_details = []
        for exp in experiences:
            company = (exp.get("company", "") or "").lower()
            score = 5.0

            if any(c in company for c in TOP_COMPANIES["faang"]):
                score = 10.0
                company_details.append(f"{exp.get('company')} (FAANG)")
            elif any(c in company for c in TOP_COMPANIES["tier_1"]):
                score = 9.0
                company_details.append(f"{exp.get('company')} (Tier 1)")
            elif any(c in company for c in TOP_COMPANIES["tier_2"]):
                score = 7.5
                company_details.append(f"{exp.get('company')} (Tier 2)")
            else:
                score = 5.5
                company_details.append(exp.get("company", "Unknown"))

            company_scores.append(score)

        avg_company = sum(company_scores) / len(company_scores) if company_scores else 5.0
        breakdown["company_tier"] = {
            "score": round(avg_company, 2),
            "weight": 0.35,
            "rationale": ", ".join(company_details[:3]),
            "data": {"companies": company_details}
        }

        # 2. Role Relevance (30% weight)
        relevant_roles = ["software", "engineer", "developer", "data", "ml", "machine learning",
                         "product", "design", "ux", "research", "intern"]
        role_scores = []

        for exp in experiences:
            title = (exp.get("title", "") or "").lower()
            if any(r in title for r in relevant_roles):
                role_scores.append(8.0)
            else:
                role_scores.append(5.0)

        avg_role = sum(role_scores) / len(role_scores) if role_scores else 5.0
        breakdown["role_relevance"] = {
            "score": round(avg_role, 2),
            "weight": 0.30,
            "rationale": f"{len([s for s in role_scores if s > 5])}/{len(experiences)} relevant roles",
            "data": {"relevant_count": len([s for s in role_scores if s > 5])}
        }

        # 3. Impact (20% weight)
        impact_keywords = ["led", "built", "launched", "increased", "reduced", "improved",
                          "architected", "designed", "scaled", "optimized", "automated"]
        impact_count = 0

        for exp in experiences:
            desc = (exp.get("description", "") or "").lower()
            highlights = exp.get("highlights", [])

            for keyword in impact_keywords:
                if keyword in desc:
                    impact_count += 1
                for h in highlights:
                    if keyword in h.lower():
                        impact_count += 1

        impact_score = min(10, 5.0 + impact_count * 0.5)
        breakdown["impact"] = {
            "score": round(impact_score, 2),
            "weight": 0.20,
            "rationale": f"{impact_count} impact indicators found",
            "data": {"impact_count": impact_count}
        }

        # 4. Progression (15% weight)
        progression_score = 5.0 + min(2.5, len(experiences) * 0.5)  # More experience = higher
        breakdown["progression"] = {
            "score": round(progression_score, 2),
            "weight": 0.15,
            "rationale": f"{len(experiences)} work experiences",
            "data": {"experience_count": len(experiences)}
        }

        return {
            "score": weighted_average(breakdown),
            "breakdown": breakdown
        }

    def _compute_github(self, candidate: Candidate, analysis: Optional[GitHubAnalysis]) -> dict:
        """
        Compute GitHub score using existing GitHubAnalysis.

        Uses the pre-computed scores from GitHubAnalysis if available.
        """
        if not analysis:
            if not candidate.github_username:
                return {
                    "score": 5.0,
                    "breakdown": {
                        "status": {"score": 5.0, "weight": 1.0, "rationale": "GitHub not connected"}
                    }
                }
            else:
                return {
                    "score": 5.0,
                    "breakdown": {
                        "status": {"score": 5.0, "weight": 1.0, "rationale": "GitHub connected but not analyzed"}
                    }
                }

        breakdown = {}

        # Use existing analysis scores (0-100 scale, convert to 0-10)
        if analysis.originality_score is not None:
            breakdown["originality"] = {
                "score": round(analysis.originality_score / 10, 2),
                "weight": 0.30,
                "rationale": f"Code originality: {analysis.originality_score:.0f}/100",
                "data": {"raw_score": analysis.originality_score}
            }

        if analysis.activity_score is not None:
            breakdown["activity"] = {
                "score": round(analysis.activity_score / 10, 2),
                "weight": 0.25,
                "rationale": f"Activity level: {analysis.activity_score:.0f}/100",
                "data": {"raw_score": analysis.activity_score}
            }

        if analysis.technical_depth_score is not None:
            breakdown["depth"] = {
                "score": round(analysis.technical_depth_score / 10, 2),
                "weight": 0.25,
                "rationale": f"Technical depth: {analysis.technical_depth_score:.0f}/100",
                "data": {"raw_score": analysis.technical_depth_score}
            }

        if analysis.collaboration_score is not None:
            breakdown["collaboration"] = {
                "score": round(analysis.collaboration_score / 10, 2),
                "weight": 0.20,
                "rationale": f"Collaboration: {analysis.collaboration_score:.0f}/100",
                "data": {"raw_score": analysis.collaboration_score}
            }

        # If no detailed scores, use overall
        if not breakdown and analysis.overall_score is not None:
            breakdown["overall"] = {
                "score": round(analysis.overall_score / 10, 2),
                "weight": 1.0,
                "rationale": f"Overall GitHub score: {analysis.overall_score:.0f}/100",
                "data": {"raw_score": analysis.overall_score}
            }

        return {
            "score": weighted_average(breakdown) if breakdown else 5.0,
            "breakdown": breakdown
        }

    def _compute_activities(self, activities: list, awards: list) -> dict:
        """
        Compute activities score from clubs and awards.

        Sub-components:
        - Clubs (60%): Prestige tier × role multiplier
        - Awards (40%): Academic and competition awards
        """
        breakdown = {}

        # 1. Clubs (60% weight)
        if activities:
            club_scores = []
            club_details = []

            role_multipliers = {1: 1.0, 2: 1.1, 3: 1.3, 4: 1.5, 5: 2.0}

            for activity in activities:
                base_score = 5.0
                role_mult = role_multipliers.get(activity.role_tier or 1, 1.0)

                if activity.club:
                    base_score = activity.club.prestige_score
                    club_details.append(f"{activity.club.short_name or activity.club.name} as {activity.role or 'Member'}")
                else:
                    # Estimate based on activity name
                    name_lower = (activity.activity_name or "").lower()
                    if any(h in name_lower for h in ["hkn", "upe", "tbp", "phi beta"]):
                        base_score = 9.0
                    elif any(h in name_lower for h in ["acm", "ieee", "consulting", "investment"]):
                        base_score = 7.5
                    club_details.append(f"{activity.activity_name} as {activity.role or 'Member'}")

                adjusted = min(10, base_score * role_mult)
                club_scores.append(adjusted)

            # Average of top 3
            top_scores = sorted(club_scores, reverse=True)[:3]
            clubs_avg = sum(top_scores) / len(top_scores) if top_scores else 5.0

            breakdown["clubs"] = {
                "score": round(clubs_avg, 2),
                "weight": 0.60,
                "rationale": ", ".join(club_details[:3]),
                "data": {"club_count": len(activities), "top_scores": top_scores}
            }
        else:
            breakdown["clubs"] = {
                "score": 5.0,
                "weight": 0.60,
                "rationale": "No club activities listed",
                "data": {}
            }

        # 2. Awards (40% weight)
        if awards:
            award_scores = []
            award_details = []

            for award in awards:
                tier_score = (award.prestige_tier or 2) * 2  # Tier 1-5 -> Score 2-10
                award_scores.append(min(10, tier_score))
                award_details.append(award.name)

            awards_avg = sum(award_scores) / len(award_scores)
            breakdown["awards"] = {
                "score": round(awards_avg, 2),
                "weight": 0.40,
                "rationale": ", ".join(award_details[:3]),
                "data": {"award_count": len(awards), "awards": award_details[:5]}
            }
        else:
            breakdown["awards"] = {
                "score": 5.0,
                "weight": 0.40,
                "rationale": "No awards listed",
                "data": {}
            }

        return {
            "score": weighted_average(breakdown),
            "breakdown": breakdown
        }


async def compute_all_scores(db: Session) -> dict:
    """
    Batch compute scores for all candidates.

    Returns summary of results.
    """
    service = ProfileScoringService(db)
    candidates = db.query(Candidate).all()

    results = {"success": 0, "failed": 0, "errors": []}

    for candidate in candidates:
        try:
            await service.compute_score(candidate.id)
            results["success"] += 1
        except Exception as e:
            logger.error(f"Failed to score {candidate.id}: {e}")
            results["failed"] += 1
            results["errors"].append({"candidate_id": candidate.id, "error": str(e)})

    return results

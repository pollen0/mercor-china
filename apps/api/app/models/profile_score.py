"""
CandidateProfileScore model for persistent scoring with detailed breakdowns.
Replaces on-the-fly scoring with stored, auditable scores.
"""

from sqlalchemy import Column, String, DateTime, Float, Index, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base


# Current scoring algorithm version - increment when formula changes
SCORING_VERSION = "2.0.0"


class CandidateProfileScore(Base):
    """
    Persistent profile score for a candidate with full breakdown and rationale.

    This replaces on-the-fly scoring with stored scores that include:
    - Component scores (education, technical, experience, github, activities)
    - Detailed breakdowns with rationale for each sub-component
    - Raw inputs snapshot for debugging
    - Version tracking for score comparisons over time
    """
    __tablename__ = "candidate_profile_scores"

    id = Column(String, primary_key=True)  # cps_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Overall score (0-10)
    total_score = Column(Float, nullable=True)

    # Component scores (0-10 each)
    education_score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    github_score = Column(Float, nullable=True)
    activities_score = Column(Float, nullable=True)

    # Detailed breakdowns with rationale (JSONB)
    # Format for each:
    # {
    #   "sub_component": {
    #     "score": 8.5,
    #     "weight": 0.25,
    #     "rationale": "Explanation of why this score was given",
    #     "data": {...}  # Optional: raw data used
    #   }
    # }
    education_breakdown = Column(JSONB, nullable=True)
    technical_breakdown = Column(JSONB, nullable=True)
    experience_breakdown = Column(JSONB, nullable=True)
    github_breakdown = Column(JSONB, nullable=True)
    activities_breakdown = Column(JSONB, nullable=True)

    # Metadata
    scoring_version = Column(String, nullable=True, default=SCORING_VERSION)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Debug data
    raw_inputs = Column(JSONB, nullable=True)  # Snapshot of all data used for scoring
    computation_log = Column(JSONB, nullable=True)  # Step-by-step computation log for debugging

    # Relationships
    candidate = relationship("Candidate", back_populates="profile_score")

    # Indexes
    __table_args__ = (
        Index('ix_candidate_profile_scores_candidate_id', 'candidate_id'),
        Index('ix_candidate_profile_scores_total_score', 'total_score'),
        UniqueConstraint('candidate_id', name='uq_candidate_profile_scores_candidate'),
    )

    def __repr__(self):
        return f"<CandidateProfileScore {self.candidate_id}: {self.total_score}>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "total_score": self.total_score,
            "education_score": self.education_score,
            "technical_score": self.technical_score,
            "experience_score": self.experience_score,
            "github_score": self.github_score,
            "activities_score": self.activities_score,
            "education_breakdown": self.education_breakdown,
            "technical_breakdown": self.technical_breakdown,
            "experience_breakdown": self.experience_breakdown,
            "github_breakdown": self.github_breakdown,
            "activities_breakdown": self.activities_breakdown,
            "scoring_version": self.scoring_version,
            "computed_at": self.computed_at.isoformat() if self.computed_at else None,
        }

    def get_breakdown_summary(self) -> dict:
        """Get a concise summary of the score breakdown."""
        summary = {
            "total": self.total_score,
            "components": {}
        }

        components = [
            ("education", self.education_score, self.education_breakdown),
            ("technical", self.technical_score, self.technical_breakdown),
            ("experience", self.experience_score, self.experience_breakdown),
            ("github", self.github_score, self.github_breakdown),
            ("activities", self.activities_score, self.activities_breakdown),
        ]

        for name, score, breakdown in components:
            if score is not None:
                summary["components"][name] = {
                    "score": score,
                    "rationale": self._extract_top_rationale(breakdown)
                }

        return summary

    def _extract_top_rationale(self, breakdown: dict) -> str:
        """Extract the most important rationale from a breakdown."""
        if not breakdown:
            return "No data available"

        # Get the highest weighted component's rationale
        top_item = max(
            breakdown.items(),
            key=lambda x: x[1].get("weight", 0) if isinstance(x[1], dict) else 0,
            default=(None, {})
        )

        if top_item[1] and isinstance(top_item[1], dict):
            return top_item[1].get("rationale", "")
        return ""

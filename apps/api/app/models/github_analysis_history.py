"""
GitHubAnalysisHistory model for tracking GitHub score changes over time.
Creates a snapshot each time GitHub is analyzed/refreshed.
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base


class GitHubAnalysisHistory(Base):
    """
    Tracks GitHub analysis snapshots for growth visualization.
    Each refresh creates a new history entry with deltas from previous.
    """
    __tablename__ = "github_analysis_history"

    id = Column(String, primary_key=True)  # gah_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    github_analysis_id = Column(String, ForeignKey("github_analyses.id", ondelete="SET NULL"), nullable=True)

    # Score snapshot (0-100)
    overall_score = Column(Float, nullable=True)
    originality_score = Column(Float, nullable=True)
    activity_score = Column(Float, nullable=True)
    depth_score = Column(Float, nullable=True)
    collaboration_score = Column(Float, nullable=True)

    # Metrics snapshot
    total_repos_analyzed = Column(Integer, nullable=True)
    total_commits_by_user = Column(Integer, nullable=True)
    primary_languages = Column(JSONB, nullable=True)  # [{language, proficiency, bytes}]

    # Deltas (change from previous analysis)
    score_delta = Column(Float, nullable=True)  # Overall score change
    repos_delta = Column(Integer, nullable=True)  # Repos analyzed change

    # Timestamp
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="github_analysis_history")
    github_analysis = relationship("GitHubAnalysis")

    __table_args__ = (
        Index('ix_github_analysis_history_candidate_id', 'candidate_id'),
        Index('ix_github_analysis_history_analyzed_at', 'analyzed_at'),
    )

    def __repr__(self):
        return f"<GitHubAnalysisHistory {self.id} score={self.overall_score} for {self.candidate_id}>"

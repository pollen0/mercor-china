"""
ResumeVersion model for tracking resume upload history.
Stores all resume versions instead of overwriting, enabling growth tracking.
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base


class ResumeVersion(Base):
    """
    Tracks each resume upload for a candidate.
    Previous versions are marked as non-current to preserve history.
    """
    __tablename__ = "resume_versions"

    id = Column(String, primary_key=True)  # rv_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)

    # Storage
    storage_key = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # Snapshots
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSONB, nullable=True)

    # Deltas (computed from previous version)
    skills_added = Column(JSONB, nullable=True)  # List of new skills
    skills_removed = Column(JSONB, nullable=True)  # List of removed skills
    projects_added = Column(Integer, nullable=True)  # Count of new projects
    experience_added = Column(Integer, nullable=True)  # Count of new experience entries

    # Status
    is_current = Column(Boolean, default=True, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="resume_versions")

    __table_args__ = (
        Index('ix_resume_versions_candidate_id', 'candidate_id'),
        Index('ix_resume_versions_is_current', 'is_current'),
        Index('ix_resume_versions_uploaded_at', 'uploaded_at'),
    )

    def __repr__(self):
        return f"<ResumeVersion {self.id} v{self.version_number} for {self.candidate_id}>"

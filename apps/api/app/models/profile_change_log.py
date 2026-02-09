"""
ProfileChangeLog model for tracking profile field changes.
Audit trail for GPA, major, education, and other key profile updates.
"""
from sqlalchemy import Column, String, DateTime, Index, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ProfileChangeType(str, enum.Enum):
    """Types of profile changes tracked."""
    GPA_UPDATE = "gpa_update"
    MAJOR_CHANGE = "major_change"
    UNIVERSITY_CHANGE = "university_change"
    GRADUATION_YEAR_CHANGE = "graduation_year_change"
    ACTIVITY_ADDED = "activity_added"
    ACTIVITY_REMOVED = "activity_removed"
    AWARD_ADDED = "award_added"
    AWARD_REMOVED = "award_removed"
    SKILLS_UPDATED = "skills_updated"
    OTHER = "other"


class ProfileChangeLog(Base):
    """
    Audit log for candidate profile changes.
    Tracks changes with old/new values and source of change.
    """
    __tablename__ = "profile_change_logs"

    id = Column(String, primary_key=True)  # pcl_{uuid}
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    # Change details
    change_type = Column(String, nullable=False)  # ProfileChangeType value
    field_name = Column(String, nullable=False)  # Specific field that changed
    old_value = Column(JSONB, nullable=True)  # Previous value (null for additions)
    new_value = Column(JSONB, nullable=True)  # New value (null for removals)

    # Source of change
    change_source = Column(String, nullable=True)  # "manual", "resume_parse", "transcript_verify"

    # Timestamp
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="profile_change_logs")

    __table_args__ = (
        Index('ix_profile_change_logs_candidate_id', 'candidate_id'),
        Index('ix_profile_change_logs_change_type', 'change_type'),
        Index('ix_profile_change_logs_changed_at', 'changed_at'),
    )

    def __repr__(self):
        return f"<ProfileChangeLog {self.id} {self.change_type} for {self.candidate_id}>"

"""
SelfSchedulingLink model for candidate self-scheduling.
Allows employers to create shareable links for candidates to book interviews.
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class SelfSchedulingLink(Base):
    """
    A shareable link that allows candidates to self-schedule interviews.
    Links can be associated with specific jobs and assigned interviewers.
    """
    __tablename__ = "self_scheduling_links"

    id = Column(String, primary_key=True)
    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)

    # Optional association with a specific job
    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)

    # Unique URL slug for the public link
    slug = Column(String, unique=True, nullable=False, index=True)

    # Display name for the link (e.g., "Engineering Phone Screen")
    name = Column(String, nullable=False)

    # Optional description shown to candidates
    description = Column(Text, nullable=True)

    # Interview duration in minutes
    duration_minutes = Column(Integer, default=30)

    # Assigned interviewers (JSON array of team_member_ids)
    # When booking, the system will select one based on availability and load balancing
    interviewer_ids = Column(JSON, nullable=False, default=list)

    # Buffer times around interviews
    buffer_before_minutes = Column(Integer, default=5)
    buffer_after_minutes = Column(Integer, default=5)

    # Booking constraints
    min_notice_hours = Column(Integer, default=24)  # Must book at least 24h in advance
    max_days_ahead = Column(Integer, default=14)    # Can book up to 14 days out

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Analytics
    view_count = Column(Integer, default=0)
    booking_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employer = relationship("Employer", backref="scheduling_links")
    job = relationship("Job", backref="scheduling_links")

    # Indexes
    __table_args__ = (
        Index("ix_scheduling_links_employer_id", "employer_id"),
        Index("ix_scheduling_links_employer_active", "employer_id", "is_active"),
        Index("ix_scheduling_links_job_id", "job_id"),
    )

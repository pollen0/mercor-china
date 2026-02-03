"""
Availability models for interviewer scheduling.
Includes recurring weekly availability and one-off exceptions.
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Date, Time, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class InterviewerAvailability(Base):
    """
    Recurring weekly availability for a team member.
    Defines when an interviewer is generally available for interviews.
    """
    __tablename__ = "interviewer_availability"

    id = Column(String, primary_key=True)
    team_member_id = Column(String, ForeignKey("employer_team_members.id", ondelete="CASCADE"), nullable=False)

    # Day of week (0 = Monday, 6 = Sunday)
    day_of_week = Column(Integer, nullable=False)

    # Time range for this availability slot
    start_time = Column(Time, nullable=False)  # e.g., 09:00
    end_time = Column(Time, nullable=False)    # e.g., 17:00

    # Timezone for interpreting the times
    timezone = Column(String, default="America/Los_Angeles")

    # Whether this slot is currently active
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    team_member = relationship("EmployerTeamMember", back_populates="availability_slots")

    # Indexes
    __table_args__ = (
        Index("ix_availability_team_member", "team_member_id"),
        Index("ix_availability_team_member_day", "team_member_id", "day_of_week"),
        Index("ix_availability_active", "team_member_id", "is_active"),
    )


class AvailabilityException(Base):
    """
    One-off exceptions to recurring availability.
    Can be used to block time (PTO, meetings) or add extra availability.
    """
    __tablename__ = "availability_exceptions"

    id = Column(String, primary_key=True)
    team_member_id = Column(String, ForeignKey("employer_team_members.id", ondelete="CASCADE"), nullable=False)

    # The specific date this exception applies to
    date = Column(Date, nullable=False)

    # If True, marks time as unavailable; if False, adds extra availability
    is_unavailable = Column(Boolean, default=True)

    # Time range (optional - if null, applies to whole day)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    # Optional reason for the exception
    reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    team_member = relationship("EmployerTeamMember", back_populates="availability_exceptions")

    # Indexes
    __table_args__ = (
        Index("ix_exception_team_member", "team_member_id"),
        Index("ix_exception_team_member_date", "team_member_id", "date"),
        Index("ix_exception_date_range", "date"),
    )

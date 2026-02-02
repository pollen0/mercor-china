"""
ScheduledInterview model for employer-candidate interview scheduling.
Stores calendar events with Google Meet links for scheduled interviews.
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class InterviewType(str, enum.Enum):
    """Types of interviews that can be scheduled."""
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURE_FIT = "culture_fit"
    FINAL = "final"
    OTHER = "other"


class ScheduledInterviewStatus(str, enum.Enum):
    """Status of a scheduled interview."""
    PENDING = "pending"  # Created but not yet confirmed
    CONFIRMED = "confirmed"  # Both parties confirmed
    COMPLETED = "completed"  # Interview took place
    CANCELLED = "cancelled"  # Interview was cancelled
    NO_SHOW = "no_show"  # Candidate or employer didn't show
    RESCHEDULED = "rescheduled"  # Interview was rescheduled (points to new interview)


class ScheduledInterview(Base):
    """
    Represents a scheduled interview between an employer and a candidate.
    Created when an employer schedules an interview via Google Calendar.
    """
    __tablename__ = "scheduled_interviews"

    id = Column(String, primary_key=True)

    # Relationships
    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)

    # Interview details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    interview_type = Column(Enum(InterviewType), default=InterviewType.OTHER)

    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    timezone = Column(String, default="America/Los_Angeles")

    # Google Calendar integration
    google_event_id = Column(String, nullable=True)  # Google Calendar event ID
    google_meet_link = Column(String, nullable=True)  # Google Meet URL
    calendar_link = Column(String, nullable=True)  # Link to view in Google Calendar

    # Additional attendees (e.g., other interviewers)
    additional_attendees = Column(JSON, nullable=True)  # List of email addresses

    # Status and notes
    status = Column(Enum(ScheduledInterviewStatus), default=ScheduledInterviewStatus.PENDING)
    employer_notes = Column(Text, nullable=True)  # Private notes from employer

    # If rescheduled, link to the new interview
    rescheduled_to_id = Column(String, ForeignKey("scheduled_interviews.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employer = relationship("Employer", backref="scheduled_interviews")
    candidate = relationship("Candidate", backref="scheduled_interviews")
    job = relationship("Job", backref="scheduled_interviews")
    rescheduled_to = relationship("ScheduledInterview", remote_side=[id], backref="rescheduled_from")

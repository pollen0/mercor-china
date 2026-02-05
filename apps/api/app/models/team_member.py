"""
EmployerTeamMember model for managing team members who can conduct interviews.
"""
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class TeamMemberRole(str, enum.Enum):
    """Roles for team members within an employer organization."""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"


class EmployerTeamMember(Base):
    """
    Represents a team member who can conduct interviews for an employer.
    Team members can have their own Google Calendar connected for scheduling.
    """
    __tablename__ = "employer_team_members"

    id = Column(String, primary_key=True)
    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)

    # Basic info
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(TeamMemberRole, values_callable=lambda x: [e.value for e in x]), default=TeamMemberRole.INTERVIEWER)
    is_active = Column(Boolean, default=True)

    # Google Calendar integration (separate from employer's calendar)
    google_calendar_connected = Column(Boolean, default=False)
    google_calendar_token = Column(String, nullable=True)  # Encrypted access token
    google_calendar_refresh_token = Column(String, nullable=True)  # Encrypted refresh token
    google_calendar_connected_at = Column(DateTime(timezone=True), nullable=True)

    # Interview capacity limits
    max_interviews_per_day = Column(Integer, default=4)
    max_interviews_per_week = Column(Integer, default=15)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employer = relationship("Employer", backref="team_members")
    availability_slots = relationship("InterviewerAvailability", back_populates="team_member", cascade="all, delete-orphan")
    availability_exceptions = relationship("AvailabilityException", back_populates="team_member", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_team_members_employer_id", "employer_id"),
        Index("ix_team_members_email", "email"),
        Index("ix_team_members_employer_active", "employer_id", "is_active"),
    )

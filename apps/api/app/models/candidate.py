from sqlalchemy import Column, String, DateTime, ARRAY, Text, Float, Integer, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base
from .employer import Vertical, RoleType
import enum


class VerticalProfileStatus(str, enum.Enum):
    """Status of a candidate's vertical profile."""
    PENDING = "pending"  # Profile created, interview not started
    IN_PROGRESS = "in_progress"  # Interview in progress
    COMPLETED = "completed"  # Interview completed and scored


class CandidateVerticalProfile(Base):
    """
    Represents a candidate's interview profile for a specific vertical.
    One interview per vertical - candidates complete ONE interview and get matched to ALL relevant jobs.
    """
    __tablename__ = "candidate_vertical_profiles"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    vertical = Column(Enum(Vertical), nullable=False)  # 'new_energy' or 'sales'
    role_type = Column(Enum(RoleType), nullable=False)  # e.g., 'battery_engineer'

    # Interview tracking
    interview_session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)
    interview_score = Column(Float, nullable=True)  # 0-10, latest score
    best_score = Column(Float, nullable=True)  # Highest score achieved across attempts
    status = Column(
        Enum(VerticalProfileStatus, values_callable=lambda x: [e.value for e in x]),
        default=VerticalProfileStatus.PENDING
    )

    # Retake tracking (Mercor-style: max 3 attempts)
    attempt_count = Column(Integer, default=0)  # Number of completed attempts
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When first completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="vertical_profiles")
    interview_session = relationship("InterviewSession", foreign_keys=[interview_session_id])
    matches = relationship("Match", back_populates="vertical_profile")

    # Unique: one profile per vertical per candidate
    __table_args__ = (UniqueConstraint('candidate_id', 'vertical', name='uq_candidate_vertical'),)


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    password_hash = Column(String, nullable=True)  # Nullable for WeChat-only users
    target_roles = Column(ARRAY(String), default=[])
    resume_url = Column(String, nullable=True)
    resume_raw_text = Column(Text, nullable=True)  # Raw extracted text from resume
    resume_parsed_data = Column(JSONB, nullable=True)  # Parsed structured data
    resume_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    wechat_open_id = Column(String, unique=True, nullable=True)
    wechat_union_id = Column(String, nullable=True)

    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    interview_sessions = relationship("InterviewSession", back_populates="candidate")
    matches = relationship("Match", back_populates="candidate")
    messages = relationship("Message", back_populates="candidate")
    vertical_profiles = relationship("CandidateVerticalProfile", back_populates="candidate")

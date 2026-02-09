from sqlalchemy import Column, String, DateTime, ARRAY, Text, Float, Integer, Boolean, ForeignKey, Enum, UniqueConstraint, Index
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
    Represents a student's current profile for a specific career vertical.
    Students can interview once per month per vertical to show progress.
    Best score is shown to employers, but full history is available.
    """
    __tablename__ = "candidate_vertical_profiles"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=False)  # 'engineering', 'data', 'business', 'design'
    role_type = Column(Enum(RoleType, values_callable=lambda x: [e.value for e in x]), nullable=False)  # e.g., 'software_engineer', 'data_analyst'

    # Current interview tracking (latest interview)
    interview_session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)
    interview_score = Column(Float, nullable=True)  # 0-10, latest score
    best_score = Column(Float, nullable=True)  # Highest score achieved (shown to employers)
    status = Column(
        Enum(VerticalProfileStatus, values_callable=lambda x: [e.value for e in x]),
        default=VerticalProfileStatus.PENDING
    )

    # Monthly interview tracking
    total_interviews = Column(Integer, default=0)  # Total interviews completed in this vertical
    last_interview_at = Column(DateTime(timezone=True), nullable=True)  # Last completed interview
    next_eligible_at = Column(DateTime(timezone=True), nullable=True)  # When can interview again (1 month cooldown)

    # Timestamps
    completed_at = Column(DateTime(timezone=True), nullable=True)  # When first completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="vertical_profiles")
    interview_session = relationship("InterviewSession", foreign_keys=[interview_session_id])
    matches = relationship("Match", back_populates="vertical_profile")

    # Unique: one profile per vertical per candidate
    # Indexes for common query patterns
    __table_args__ = (
        UniqueConstraint('candidate_id', 'vertical', name='uq_candidate_vertical'),
        Index('ix_candidate_vertical_profiles_best_score', 'best_score'),
        Index('ix_candidate_vertical_profiles_status', 'status'),
    )


class Candidate(Base):
    """
    Student user on the Pathway platform.
    Students interview monthly to show progress over time.
    """
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)  # Optional for students
    password_hash = Column(String, nullable=True)  # Nullable for GitHub OAuth users

    # Education Information
    university = Column(String, nullable=True)  # e.g., "Stanford University"
    major = Column(String, nullable=True)  # Primary major (kept for backwards compat)
    majors = Column(JSONB, nullable=True)  # List of majors for double/triple majors
    minors = Column(JSONB, nullable=True)  # List of minors
    certificates = Column(JSONB, nullable=True)  # List of certificates/concentrations
    graduation_year = Column(Integer, nullable=True)  # e.g., 2026
    gpa = Column(Float, nullable=True)  # Cumulative GPA, 0.0-4.0 scale
    major_gpa = Column(Float, nullable=True)  # Major-specific GPA (often higher for CS)
    courses = Column(JSONB, nullable=True)  # Array of current/past relevant courses

    # Transfer/AP credit tracking
    is_transfer = Column(Boolean, default=False)  # Is transfer student
    transfer_university = Column(String, nullable=True)  # Previous school if transfer
    ap_credits = Column(JSONB, nullable=True)  # List of AP credits: [{exam, score, units}]
    transfer_units = Column(Integer, nullable=True)  # Total transfer units

    # GitHub Integration
    github_username = Column(String, unique=True, nullable=True)
    github_access_token = Column(String, nullable=True)  # Encrypted OAuth token
    github_data = Column(JSONB, nullable=True)  # Cached GitHub profile data (repos, contributions, etc.)
    github_connected_at = Column(DateTime(timezone=True), nullable=True)

    # Profile
    target_roles = Column(ARRAY(String), nullable=True)  # No default for SQLite compatibility
    bio = Column(Text, nullable=True)  # Short bio/about me
    linkedin_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)

    # Resume
    resume_url = Column(String, nullable=True)
    resume_raw_text = Column(Text, nullable=True)  # Raw extracted text from resume
    resume_parsed_data = Column(JSONB, nullable=True)  # Parsed structured data
    resume_uploaded_at = Column(DateTime(timezone=True), nullable=True)

    # Transcript
    transcript_key = Column(String, nullable=True)  # Storage key for transcript PDF
    transcript_verification = Column(JSONB, nullable=True)  # Verification result details
    transcript_verification_status = Column(String, nullable=True)  # "verified", "warning", "suspicious"
    transcript_confidence_score = Column(Float, nullable=True)  # 0-100 confidence score

    # Email verification
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    password_reset_token = Column(String, nullable=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Google Calendar integration
    google_calendar_token = Column(String, nullable=True)  # Encrypted OAuth token
    google_calendar_refresh_token = Column(String, nullable=True)  # Encrypted refresh token
    google_calendar_connected_at = Column(DateTime(timezone=True), nullable=True)

    # Referral system
    referral_code = Column(String, unique=True, nullable=True)  # Unique code like "PATHWAY-ABC123"
    referred_by_id = Column(String, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)

    # Profile Sharing & Preferences (for GTM)
    opted_in_to_sharing = Column(Boolean, default=False, nullable=False)  # Consent to share profile with employers
    sharing_preferences = Column(JSONB, nullable=True)  # {company_stages, locations, industries, email_digest}

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    interview_sessions = relationship("InterviewSession", back_populates="candidate")
    matches = relationship("Match", back_populates="candidate")
    messages = relationship("Message", back_populates="candidate")
    vertical_profiles = relationship("CandidateVerticalProfile", back_populates="candidate")
    interview_history = relationship("InterviewHistoryEntry", back_populates="candidate")
    activities = relationship("CandidateActivity", back_populates="candidate", cascade="all, delete-orphan")
    awards = relationship("CandidateAward", back_populates="candidate", cascade="all, delete-orphan")
    profile_tokens = relationship("ProfileToken", back_populates="candidate", cascade="all, delete-orphan")

    # Indexes for common query patterns (talent pool filtering)
    __table_args__ = (
        Index('ix_candidates_university', 'university'),
        Index('ix_candidates_graduation_year', 'graduation_year'),
        Index('ix_candidates_gpa', 'gpa'),
    )


class InterviewHistoryEntry(Base):
    """
    Tracks each monthly interview attempt for progress visualization.
    Employers can see how students improve over time (2-4 years of college).
    """
    __tablename__ = "interview_history"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=False)
    role_type = Column(Enum(RoleType, values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Interview reference
    interview_session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)

    # Scores at time of interview
    overall_score = Column(Float, nullable=True)  # 0-10
    communication_score = Column(Float, nullable=True)  # 0-10
    problem_solving_score = Column(Float, nullable=True)  # 0-10
    technical_score = Column(Float, nullable=True)  # 0-10
    growth_mindset_score = Column(Float, nullable=True)  # 0-10
    culture_fit_score = Column(Float, nullable=True)  # 0-10

    # Context at time of interview (snapshot)
    education_snapshot = Column(JSONB, nullable=True)  # {university, major, year, gpa}
    github_snapshot = Column(JSONB, nullable=True)  # {repos, contributions, languages}

    # Month/Year for easy querying and display
    interview_month = Column(Integer, nullable=False)  # 1-12
    interview_year = Column(Integer, nullable=False)  # e.g., 2024

    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="interview_history")
    interview_session = relationship("InterviewSession", foreign_keys=[interview_session_id])

    # Unique: one interview per vertical per month
    __table_args__ = (
        UniqueConstraint('candidate_id', 'vertical', 'interview_month', 'interview_year',
                         name='uq_candidate_vertical_month'),
    )

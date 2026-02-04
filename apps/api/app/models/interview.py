from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum, Boolean, ARRAY, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base
from .employer import Vertical, RoleType


class InterviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONTACTED = "CONTACTED"  # Employer has reached out
    IN_REVIEW = "IN_REVIEW"  # Under active consideration
    WATCHLIST = "WATCHLIST"  # Tracking for future (e.g., promising freshmen/sophomores)
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING)
    is_practice = Column(Boolean, default=False)  # Practice mode flag
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Float, nullable=True)
    ai_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Vertical interview fields (for talent pool model)
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=True)  # 'new_energy' or 'sales'
    role_type = Column(Enum(RoleType, values_callable=lambda x: [e.value for e in x]), nullable=True)  # e.g., 'battery_engineer'
    is_vertical_interview = Column(Boolean, default=False)  # True for talent pool interviews

    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate", back_populates="interview_sessions")

    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    job = relationship("Job", back_populates="interview_sessions")

    responses = relationship("InterviewResponse", back_populates="session")


class InterviewResponse(Base):
    __tablename__ = "interview_responses"

    id = Column(String, primary_key=True)
    question_index = Column(Integer, nullable=False)
    question_text = Column(String, nullable=False)
    video_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
    transcription = Column(String, nullable=True)
    ai_score = Column(Float, nullable=True)
    ai_analysis = Column(String, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Scoring algorithm version tracking (for re-scoring when algorithm improves)
    scoring_algorithm_version = Column(String, nullable=True)  # e.g., "2.0.0"
    scored_at = Column(DateTime(timezone=True), nullable=True)  # When this was scored
    raw_score_data = Column(JSONB, nullable=True)  # Full scoring context for re-scoring

    # Follow-up question support
    is_followup = Column(Boolean, default=False)
    parent_response_id = Column(String, ForeignKey("interview_responses.id", ondelete="SET NULL"), nullable=True)

    # Question type: "video" (default) or "coding"
    question_type = Column(String, default="video")

    # Coding-specific fields (for question_type="coding")
    code_solution = Column(Text, nullable=True)  # Submitted code
    execution_status = Column(String, nullable=True)  # "success", "error", "timeout"
    test_results = Column(JSONB, nullable=True)  # [{name, passed, actual, expected, hidden}]
    execution_time_ms = Column(Integer, nullable=True)  # Total execution time

    session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    session = relationship("InterviewSession", back_populates="responses")

    # Self-referential relationship for follow-up responses
    parent_response = relationship("InterviewResponse", remote_side="InterviewResponse.id", backref="followup_responses")


class FollowupQueueStatus(str, enum.Enum):
    PENDING = "PENDING"
    ASKED = "ASKED"
    SKIPPED = "SKIPPED"


class FollowupQueue(Base):
    """Queue of generated follow-up questions for an interview session."""
    __tablename__ = "followup_queue"

    id = Column(String, primary_key=True)
    question_index = Column(Integer, nullable=False)  # Which base question this is for
    generated_questions = Column(ARRAY(String), nullable=False)  # List of follow-up questions
    selected_index = Column(Integer, nullable=True)  # Which follow-up was selected (if any)
    status = Column(Enum(FollowupQueueStatus), default=FollowupQueueStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    session = relationship("InterviewSession", backref="followup_queues")


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True)
    score = Column(Float, nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    ai_reasoning = Column(String, nullable=True)
    # Detailed match scores
    interview_score = Column(Float, nullable=True)  # Score from interview (0-10)
    skills_match_score = Column(Float, nullable=True)  # How well skills match job (0-10)
    experience_match_score = Column(Float, nullable=True)  # Experience relevance (0-10)
    location_match = Column(Boolean, nullable=True)  # Does location match?
    overall_match_score = Column(Float, nullable=True)  # Weighted total (0-100)
    factors = Column(Text, nullable=True)  # JSON with detailed scoring factors
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate", back_populates="matches")

    # Job can be null for talent pool matches (matched via vertical profile)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    job = relationship("Job", back_populates="matches")

    # Vertical profile link for talent pool model
    vertical_profile_id = Column(String, ForeignKey("candidate_vertical_profiles.id", ondelete="SET NULL"), nullable=True)
    vertical_profile = relationship("CandidateVerticalProfile", back_populates="matches")

from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class InterviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True)
    status = Column(Enum(InterviewStatus), default=InterviewStatus.PENDING)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_score = Column(Float, nullable=True)
    ai_summary = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate", back_populates="interview_sessions")

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
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

    session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    session = relationship("InterviewSession", back_populates="responses")


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True)
    score = Column(Float, nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    ai_reasoning = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate", back_populates="matches")

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    job = relationship("Job", back_populates="matches")

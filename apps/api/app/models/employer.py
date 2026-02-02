from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, ARRAY, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class Vertical(str, enum.Enum):
    """Career verticals for student job seekers - based on actual new grad job market."""
    SOFTWARE_ENGINEERING = "software_engineering"  # SWE, Embedded, QA - most common
    DATA = "data"  # Data Science, Analytics, ML, Data Engineering
    PRODUCT = "product"  # Product Management
    DESIGN = "design"  # UX/UI, Product Design
    FINANCE = "finance"  # Investment Banking, Finance Analyst


class RoleType(str, enum.Enum):
    """Specific entry-level role types within each vertical."""
    # Software Engineering Vertical (most common titles from 2026 job boards)
    SOFTWARE_ENGINEER = "software_engineer"  # Software Engineer I, Associate SWE
    EMBEDDED_ENGINEER = "embedded_engineer"  # Embedded Software Engineer
    QA_ENGINEER = "qa_engineer"  # Software Quality Engineer
    # Data Vertical
    DATA_ANALYST = "data_analyst"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    DATA_ENGINEER = "data_engineer"
    # Product Vertical
    PRODUCT_MANAGER = "product_manager"
    ASSOCIATE_PM = "associate_pm"
    # Design Vertical
    UX_DESIGNER = "ux_designer"
    UI_DESIGNER = "ui_designer"
    PRODUCT_DESIGNER = "product_designer"
    # Finance Vertical (Investment Banking & Finance)
    IB_ANALYST = "ib_analyst"  # Investment Banking Analyst
    FINANCE_ANALYST = "finance_analyst"
    EQUITY_RESEARCH = "equity_research"


class Employer(Base):
    __tablename__ = "employers"

    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    industry = Column(String, nullable=True)  # 'tech', 'finance', 'healthcare', etc.
    company_size = Column(String, nullable=True)  # 'startup', 'smb', 'enterprise'
    # Email verification
    is_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    password_reset_token = Column(String, nullable=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    jobs = relationship("Job", back_populates="employer")
    messages = relationship("Message", back_populates="employer")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    vertical = Column(Enum(Vertical), nullable=True)  # engineering, data, business, design
    role_type = Column(Enum(RoleType), nullable=True)  # Specific role within vertical
    requirements = Column(ARRAY(String), nullable=True)  # No default for SQLite compatibility
    location = Column(String, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    employer = relationship("Employer", back_populates="jobs")

    interview_sessions = relationship("InterviewSession", back_populates="job")
    matches = relationship("Match", back_populates="job")
    interview_questions = relationship("InterviewQuestion", back_populates="job")
    invite_tokens = relationship("InviteToken", back_populates="job")
    messages = relationship("Message", back_populates="job")


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    text_zh = Column(Text, nullable=True)  # Chinese translation
    category = Column(String, nullable=True)  # "behavioral", "technical", "culture"
    order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Question type: "video" (default) or "coding"
    question_type = Column(String, default="video")

    # Progressive difficulty system
    difficulty_level = Column(Integer, default=1)  # 1=foundational, 2=intermediate, 3=advanced
    vertical = Column(Enum(Vertical), nullable=True)  # Which vertical this question belongs to
    skill_tags = Column(ARRAY(String), nullable=True)  # e.g., ["system_design", "algorithms"]
    question_key = Column(String, nullable=True)  # Unique key for deduplication, e.g., "swe_l1_intro"

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    job = relationship("Job", back_populates="interview_questions")

    # Coding challenge reference (for question_type="coding")
    coding_challenge_id = Column(String, ForeignKey("coding_challenges.id", ondelete="SET NULL"), nullable=True)
    coding_challenge = relationship("CodingChallenge", back_populates="questions")


class CandidateQuestionHistory(Base):
    """Tracks which questions have been asked to each candidate to avoid repetition."""
    __tablename__ = "candidate_question_history"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    question_key = Column(String, nullable=False)  # The unique question identifier
    question_text = Column(Text, nullable=False)  # Store the actual question text
    vertical = Column(Enum(Vertical), nullable=True)
    difficulty_level = Column(Integer, default=1)
    category = Column(String, nullable=True)

    # Performance on this question
    score = Column(Float, nullable=True)  # 0-10 score received
    interview_session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)

    asked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", backref="question_history")


class InviteToken(Base):
    __tablename__ = "invite_tokens"

    id = Column(String, primary_key=True)
    token = Column(String, unique=True, nullable=False)
    max_uses = Column(Integer, default=0)  # 0 = unlimited
    used_count = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    job = relationship("Job", back_populates="invite_tokens")

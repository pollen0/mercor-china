from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, ARRAY, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class Vertical(str, enum.Enum):
    """Career verticals for student job seekers."""
    ENGINEERING = "engineering"  # Software Engineering, DevOps, etc.
    DATA = "data"  # Data Science, Analytics, ML
    BUSINESS = "business"  # Product, Marketing, Finance
    DESIGN = "design"  # UX/UI, Product Design


class RoleType(str, enum.Enum):
    """Specific entry-level role types within each vertical."""
    # Engineering Vertical
    SOFTWARE_ENGINEER = "software_engineer"
    BACKEND_ENGINEER = "backend_engineer"
    FRONTEND_ENGINEER = "frontend_engineer"
    FULLSTACK_ENGINEER = "fullstack_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    # Data Vertical
    DATA_ANALYST = "data_analyst"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    DATA_ENGINEER = "data_engineer"
    # Business Vertical
    PRODUCT_MANAGER = "product_manager"
    BUSINESS_ANALYST = "business_analyst"
    MARKETING_ASSOCIATE = "marketing_associate"
    FINANCE_ANALYST = "finance_analyst"
    CONSULTANT = "consultant"
    # Design Vertical
    UX_DESIGNER = "ux_designer"
    UI_DESIGNER = "ui_designer"
    PRODUCT_DESIGNER = "product_designer"


class Employer(Base):
    __tablename__ = "employers"

    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    industry = Column(String, nullable=True)  # 'new_energy', 'sales', 'tech', etc.
    company_size = Column(String, nullable=True)  # 'startup', 'smb', 'enterprise'
    # Email verification
    is_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    jobs = relationship("Job", back_populates="employer")
    messages = relationship("Message", back_populates="employer")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    vertical = Column(Enum(Vertical), nullable=True)  # 'new_energy' or 'sales'
    role_type = Column(Enum(RoleType), nullable=True)  # Specific role within vertical
    requirements = Column(ARRAY(String), default=[])
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

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    job = relationship("Job", back_populates="interview_questions")

    # Coding challenge reference (for question_type="coding")
    coding_challenge_id = Column(String, ForeignKey("coding_challenges.id", ondelete="SET NULL"), nullable=True)
    coding_challenge = relationship("CodingChallenge", back_populates="questions")


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

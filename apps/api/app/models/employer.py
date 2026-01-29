from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, ARRAY, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class Vertical(str, enum.Enum):
    """Industry verticals for job postings."""
    NEW_ENERGY = "new_energy"  # New Energy/EV industry
    SALES = "sales"  # General Sales/BD


class RoleType(str, enum.Enum):
    """Specific role types within each vertical."""
    # New Energy/EV Vertical
    BATTERY_ENGINEER = "battery_engineer"
    EMBEDDED_SOFTWARE = "embedded_software"
    AUTONOMOUS_DRIVING = "autonomous_driving"
    SUPPLY_CHAIN = "supply_chain"
    EV_SALES = "ev_sales"
    # Sales/BD Vertical
    SALES_REP = "sales_rep"
    BD_MANAGER = "bd_manager"
    ACCOUNT_MANAGER = "account_manager"


class Employer(Base):
    __tablename__ = "employers"

    id = Column(String, primary_key=True)
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    logo = Column(String, nullable=True)
    industry = Column(String, nullable=True)  # 'new_energy', 'sales', 'tech', etc.
    company_size = Column(String, nullable=True)  # 'startup', 'smb', 'enterprise'
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    jobs = relationship("Job", back_populates="employer")


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


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    text_zh = Column(Text, nullable=True)  # Chinese translation
    category = Column(String, nullable=True)  # "behavioral", "technical", "culture"
    order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=True)
    job = relationship("Job", back_populates="interview_questions")


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

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, ARRAY, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
import enum
from ..database import Base


# ==================== ORGANIZATION/TEAM ENUMS ====================

class OrganizationRole(str, enum.Enum):
    """Roles within an organization for team collaboration."""
    OWNER = "owner"  # Full access, billing, can delete org
    ADMIN = "admin"  # Manage members, jobs, settings
    RECRUITER = "recruiter"  # Manage jobs, candidates, contact
    HIRING_MANAGER = "hiring_manager"  # View candidates, leave feedback
    INTERVIEWER = "interviewer"  # View assigned candidates only


class InviteStatus(str, enum.Enum):
    """Status of organization invites."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


# ==================== VERTICAL/ROLE ENUMS ====================

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
    FRONTEND_ENGINEER = "frontend_engineer"  # Frontend Engineer
    BACKEND_ENGINEER = "backend_engineer"  # Backend Engineer
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
    # Business/Consulting Vertical
    CONSULTANT = "consultant"  # Strategy/Management Consultant
    MARKETING_ASSOCIATE = "marketing_associate"  # Marketing Associate
    BUSINESS_ANALYST = "business_analyst"  # Business Analyst


class Employer(Base):
    __tablename__ = "employers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)  # Employer's personal name
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

    # Google Calendar integration
    google_calendar_token = Column(String, nullable=True)
    google_calendar_refresh_token = Column(String, nullable=True)
    google_calendar_connected_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    jobs = relationship("Job", back_populates="employer")
    messages = relationship("Message", back_populates="employer")
    organization_memberships = relationship(
        "OrganizationMember",
        foreign_keys="OrganizationMember.employer_id",
        back_populates="employer",
        cascade="all, delete-orphan"
    )

    @property
    def organization(self):
        """Get the employer's primary organization (first membership)."""
        if self.organization_memberships:
            return self.organization_memberships[0].organization
        return None

    @property
    def organization_role(self):
        """Get the employer's role in their primary organization."""
        if self.organization_memberships:
            return self.organization_memberships[0].role
        return None


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=True)  # engineering, data, business, design
    role_type = Column(Enum(RoleType, values_callable=lambda x: [e.value for e in x]), nullable=True)  # Specific role within vertical
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
    category = Column(String, nullable=True)  # "behavioral", "technical", "culture"
    order = Column(Integer, default=0)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Question type: "video" (default) or "coding"
    question_type = Column(String, default="video")

    # Progressive difficulty system
    difficulty_level = Column(Integer, default=1)  # 1=foundational, 2=intermediate, 3=advanced
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=True)  # Which vertical this question belongs to
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
    vertical = Column(Enum(Vertical, values_callable=lambda x: [e.value for e in x]), nullable=True)
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


# ==================== ORGANIZATION/TEAM MODELS ====================

class Organization(Base):
    """
    Company/Organization entity for team collaboration.
    Multiple employers can belong to one organization.
    """
    __tablename__ = "organizations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # Company name
    slug = Column(String, unique=True, nullable=False)  # URL-friendly identifier
    logo_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)  # 'startup', 'smb', 'enterprise'
    description = Column(Text, nullable=True)

    # Settings
    settings = Column(JSONB, nullable=True)  # {require_approval_to_contact, etc.}

    # Plan/Billing (for future)
    plan = Column(String, default="free")  # 'free', 'pro', 'enterprise'
    plan_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    invites = relationship("OrganizationInvite", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    """
    Links employers to organizations with specific roles.
    """
    __tablename__ = "organization_members"

    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(OrganizationRole, values_callable=lambda x: [e.value for e in x]), default=OrganizationRole.RECRUITER)

    # Permissions override (optional fine-grained control)
    permissions = Column(JSONB, nullable=True)  # {can_contact: true, can_manage_jobs: false, etc.}

    invited_by_id = Column(String, ForeignKey("employers.id", ondelete="SET NULL"), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="members")
    employer = relationship("Employer", foreign_keys=[employer_id], back_populates="organization_memberships")
    invited_by = relationship("Employer", foreign_keys=[invited_by_id])


class OrganizationInvite(Base):
    """
    Pending invites to join an organization.
    """
    __tablename__ = "organization_invites"

    id = Column(String, primary_key=True)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)  # Email of person being invited
    role = Column(Enum(OrganizationRole, values_callable=lambda x: [e.value for e in x]), default=OrganizationRole.RECRUITER)
    token = Column(String, unique=True, nullable=False)  # Invite token for the link
    status = Column(Enum(InviteStatus, values_callable=lambda x: [e.value for e in x]), default=InviteStatus.PENDING)

    invited_by_id = Column(String, ForeignKey("employers.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="invites")
    invited_by = relationship("Employer", foreign_keys=[invited_by_id])

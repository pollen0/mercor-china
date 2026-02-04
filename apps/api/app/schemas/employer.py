from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class EmployerRegister(BaseModel):
    name: Optional[str] = None  # Employer's personal name
    company_name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters")
            if len(v) > 100:
                raise ValueError("Name cannot exceed 100 characters")
        return v

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Company name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Company name cannot exceed 100 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class EmployerLogin(BaseModel):
    email: EmailStr
    password: str


class EmployerUpdate(BaseModel):
    """Schema for updating employer profile."""
    name: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters")
            if len(v) > 100:
                raise ValueError("Name cannot exceed 100 characters")
        return v

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Company name must be at least 2 characters")
            if len(v) > 100:
                raise ValueError("Company name cannot exceed 100 characters")
        return v


class EmployerResponse(BaseModel):
    id: str
    name: Optional[str] = None  # Employer's personal name
    company_name: str
    email: str
    logo: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmployerWithToken(BaseModel):
    employer: EmployerResponse
    token: str
    token_type: str = "bearer"


class JobCreate(BaseModel):
    title: str
    description: str
    vertical: Optional[str] = None  # 'new_energy' or 'sales'
    role_type: Optional[str] = None  # Specific role within vertical
    requirements: list[str] = []
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    vertical: Optional[str] = None
    role_type: Optional[str] = None
    requirements: Optional[list[str]] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    vertical: Optional[str] = None
    role_type: Optional[str] = None
    requirements: Optional[list[str]] = None  # Optional for SQLite compatibility in tests
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    is_active: bool
    employer_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobList(BaseModel):
    jobs: list[JobResponse]
    total: int


class DashboardStats(BaseModel):
    total_interviews: int
    pending_review: int
    shortlisted: int
    rejected: int
    average_score: Optional[float] = None


# Contact Candidate schemas
class ContactRequest(BaseModel):
    subject: str
    body: str
    message_type: str = "custom"  # 'interview_request', 'rejection', 'shortlist_notice', 'custom'
    job_id: Optional[str] = None

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Subject must be at least 2 characters")
        if len(v) > 200:
            raise ValueError("Subject cannot exceed 200 characters")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Content must be at least 10 characters")
        if len(v) > 5000:
            raise ValueError("Content cannot exceed 5000 characters")
        return v


class MessageResponse(BaseModel):
    id: str
    subject: str
    body: str
    message_type: str
    employer_id: str
    candidate_id: str
    job_id: Optional[str] = None
    sent_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Bulk Actions schemas
class BulkActionRequest(BaseModel):
    interview_ids: list[str]
    action: str  # 'shortlist' or 'reject'

    @field_validator("interview_ids")
    @classmethod
    def validate_interview_ids(cls, v: list[str]) -> list[str]:
        if len(v) == 0:
            raise ValueError("Please select at least one interview")
        if len(v) > 100:
            raise ValueError("Cannot process more than 100 interviews at once")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ['shortlist', 'reject']:
            raise ValueError("Action must be 'shortlist' or 'reject'")
        return v


class BulkActionResult(BaseModel):
    success: bool
    processed: int
    failed: int
    errors: list[str] = []


# Match Alert schemas
class MatchAlertCandidate(BaseModel):
    id: str
    name: str
    email: str
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None


class MatchAlert(BaseModel):
    id: str
    candidate: MatchAlertCandidate
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    match_score: float
    interview_score: Optional[float] = None
    skills_match_score: Optional[float] = None
    status: str  # PENDING, CONTACTED, etc.
    created_at: datetime
    is_new: bool = True  # Unviewed by employer


class MatchAlertList(BaseModel):
    alerts: list[MatchAlert]
    total: int
    unread_count: int


# ==========================================
# SKILL GAP ANALYSIS SCHEMAS
# ==========================================

class SkillMatch(BaseModel):
    """Result of matching a candidate skill to a requirement."""
    requirement: str
    requirement_category: str
    matched: bool
    candidate_skill: Optional[str] = None
    match_type: str = "none"  # exact, synonym, related, partial, none
    proficiency_level: str = "none"  # expert, advanced, intermediate, beginner, none
    proficiency_score: int = 0  # 0-5
    evidence: list[str] = []
    years_experience: Optional[float] = None


class CategoryCoverage(BaseModel):
    """Coverage analysis for a skill category."""
    matched: int
    total: int
    coverage_score: float
    avg_proficiency: float
    importance: str  # high, medium, low
    description: str


class LearningPriority(BaseModel):
    """A skill to learn with priority."""
    skill: str
    priority: str  # critical, recommended, optional
    reason: str
    estimated_effort: str


class AlternativeSkill(BaseModel):
    """A candidate skill that could substitute for a missing requirement."""
    missing_requirement: str
    alternative_skill: str
    transferability: str  # high, medium, low
    note: str


class SkillGapAnalysisRequest(BaseModel):
    """Request to analyze skill gap for a candidate-job pair."""
    candidate_id: str
    job_id: Optional[str] = None
    job_requirements: Optional[list[str]] = None  # Required if job_id not provided


class SkillGapAnalysisResponse(BaseModel):
    """Complete skill gap analysis result."""
    # Summary
    overall_match_score: float  # 0-100
    total_requirements: int
    matched_requirements: int
    critical_gaps: list[str]

    # Detailed matches
    skill_matches: list[dict]

    # Category analysis
    category_coverage: dict[str, dict]

    # Proficiency analysis
    proficiency_distribution: dict[str, int]
    avg_proficiency_score: float

    # Recommendations
    learning_priorities: list[dict]
    alternative_skills: list[dict]
    transferable_skills: list[str]

    # Strengths
    bonus_skills: list[str]
    strongest_areas: list[str]


# ==========================================
# ENHANCED MATCHING SCHEMAS
# ==========================================

class EnhancedMatchRequest(BaseModel):
    """Request for enhanced ML-powered matching."""
    candidate_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    job_requirements: Optional[list[str]] = None
    job_vertical: Optional[str] = None
    include_skill_gap: bool = True


class EnhancedMatchResponse(BaseModel):
    """Enhanced match result with ML-powered insights."""
    # Core scores
    overall_match_score: float  # 0-100
    interview_score: float
    skills_match_score: float
    experience_match_score: float

    # ML-powered scores
    github_signal_score: float
    education_score: float
    growth_trajectory_score: float

    # Location
    location_match: bool

    # Detailed factors
    factors: dict

    # Skill gap summary
    skill_gap_summary: dict

    # Insights
    top_strengths: list[str]
    areas_for_growth: list[str]
    hiring_recommendation: str
    confidence_score: float

    # AI reasoning
    ai_reasoning: str


class CandidateRankingRequest(BaseModel):
    """Request to rank candidates for a job."""
    job_id: str
    limit: int = 20
    offset: int = 0
    min_score: float = 0.0
    include_skill_gap: bool = False


class RankedCandidate(BaseModel):
    """A candidate with ranking information."""
    candidate_id: str
    name: str
    email: str
    university: Optional[str] = None
    graduation_year: Optional[int] = None

    # Scores
    overall_match_score: float
    interview_score: Optional[float] = None
    skills_match_score: Optional[float] = None
    github_signal_score: Optional[float] = None

    # Quick insights
    top_strengths: list[str] = []
    skill_gaps: list[str] = []
    hiring_recommendation: str = ""


class CandidateRankingResponse(BaseModel):
    """Response with ranked candidates."""
    job_id: str
    job_title: str
    candidates: list[RankedCandidate]
    total: int
    average_match_score: float

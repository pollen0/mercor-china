from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Any
from datetime import datetime
import re


class CandidateCreate(BaseModel):
    """Request to create a new student account."""
    name: str
    email: EmailStr
    password: str
    # Optional education info (can be added later)
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 100:
            raise ValueError("Name cannot exceed 100 characters")
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

    @field_validator("graduation_year")
    @classmethod
    def validate_graduation_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            current_year = datetime.now().year
            # Allow recent graduates (previous year) and future graduates
            min_year = current_year - 1
            max_year = current_year + 6
            if v < min_year or v > max_year:
                raise ValueError(f"Graduation year must be between {min_year} and {max_year}")
        return v


class CandidateLogin(BaseModel):
    """Request for candidate login."""
    email: EmailStr
    password: str


class CandidateUpdate(BaseModel):
    """Request to update student profile."""
    name: Optional[str] = None
    phone: Optional[str] = None
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    courses: Optional[list[dict[str, Any]]] = None  # [{name, grade, semester}]
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: Optional[list[str]] = None

    @field_validator("gpa")
    @classmethod
    def validate_gpa(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            if v < 0.0 or v > 4.0:
                raise ValueError("GPA must be between 0.0 and 4.0")
        return v


class EducationInfo(BaseModel):
    """Student's education information."""
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    courses: Optional[list[dict[str, Any]]] = None


class GitHubInfo(BaseModel):
    """Student's GitHub profile information."""
    username: Optional[str] = None
    connected_at: Optional[datetime] = None
    top_repos: Optional[list[dict[str, Any]]] = None  # [{name, description, stars, language, url}]
    total_repos: Optional[int] = None
    total_contributions: Optional[int] = None
    languages: Optional[dict[str, int]] = None  # {language: bytes}


class CandidateResponse(BaseModel):
    """Public candidate/student response."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    target_roles: list[str] = []
    # Education
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    # Profile
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    # GitHub
    github_username: Optional[str] = None
    # Resume
    resume_url: Optional[str] = None
    # Timestamps
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateDetailResponse(BaseModel):
    """Detailed candidate response with all profile data."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    target_roles: list[str] = []
    # Education
    education: Optional[EducationInfo] = None
    # GitHub
    github: Optional[GitHubInfo] = None
    # Profile
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    # Resume
    resume_url: Optional[str] = None
    resume_parsed_data: Optional[dict[str, Any]] = None
    # Interview progress
    interview_count: Optional[int] = None
    best_scores: Optional[dict[str, float]] = None  # {vertical: score}
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CandidateList(BaseModel):
    candidates: list[CandidateResponse]
    total: int


# Resume parsing schemas
class ExperienceItem(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None  # "Present" for current job
    description: Optional[str] = None
    highlights: list[str] = []


class EducationItem(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None


class ProjectItem(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: list[str] = []
    highlights: list[str] = []


class ParsedResume(BaseModel):
    """Structured data extracted from a resume."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = []
    experience: list[ExperienceItem] = []
    education: list[EducationItem] = []
    projects: list[ProjectItem] = []
    languages: list[str] = []
    certifications: list[str] = []


class ResumeParseResult(BaseModel):
    """Response after uploading and parsing a resume."""
    success: bool
    message: str
    resume_url: Optional[str] = None
    parsed_data: Optional[ParsedResume] = None
    raw_text_preview: Optional[str] = None  # First 500 chars


class ResumeResponse(BaseModel):
    """Full resume data for a candidate."""
    candidate_id: str
    resume_url: Optional[str] = None
    raw_text: Optional[str] = None
    parsed_data: Optional[ParsedResume] = None
    uploaded_at: Optional[datetime] = None


class PersonalizedQuestion(BaseModel):
    """A personalized interview question based on resume."""
    text: str
    category: str  # behavioral, technical, experience
    based_on: str  # What resume element this is based on


# GitHub OAuth schemas
class GitHubAuthUrlResponse(BaseModel):
    """Response containing GitHub authorization URL."""
    auth_url: str
    state: str  # CSRF token


class GitHubCallbackRequest(BaseModel):
    """Request to complete GitHub OAuth with authorization code."""
    code: str
    state: Optional[str] = None  # For CSRF validation


class GitHubConnectResponse(BaseModel):
    """Response after successfully connecting GitHub."""
    success: bool
    message: str
    github_username: Optional[str] = None
    github_data: Optional[GitHubInfo] = None


class CandidateWithToken(BaseModel):
    """Candidate response with auth token (for login)."""
    candidate: CandidateResponse
    token: str
    token_type: str = "bearer"


# Sharing preferences schemas (GTM)
class SharingPreferences(BaseModel):
    """Student's preferences for profile sharing with employers."""
    company_stages: list[str] = []  # ["seed", "series_a", "series_b", "series_c_plus"]
    locations: list[str] = []  # ["remote", "sf", "nyc", "seattle", "austin", etc.]
    industries: list[str] = []  # ["fintech", "climate", "ai", "healthcare", etc.]
    email_digest: bool = True  # Receive weekly digest of companies who viewed profile


class SharingPreferencesUpdate(BaseModel):
    """Request to update sharing preferences."""
    opted_in_to_sharing: Optional[bool] = None
    company_stages: Optional[list[str]] = None
    locations: Optional[list[str]] = None
    industries: Optional[list[str]] = None
    email_digest: Optional[bool] = None


class SharingPreferencesResponse(BaseModel):
    """Response with student's current sharing preferences."""
    opted_in_to_sharing: bool
    preferences: Optional[SharingPreferences] = None

    class Config:
        from_attributes = True


# Interview progress schemas
class InterviewProgressEntry(BaseModel):
    """A single interview attempt in history."""
    month: int
    year: int
    vertical: str
    role_type: str
    overall_score: float
    communication_score: Optional[float] = None
    problem_solving_score: Optional[float] = None
    technical_score: Optional[float] = None
    growth_mindset_score: Optional[float] = None
    culture_fit_score: Optional[float] = None
    completed_at: datetime


class InterviewProgressResponse(BaseModel):
    """Student's interview progress over time."""
    candidate_id: str
    total_interviews: int
    best_scores: dict[str, float]  # {vertical: best_score}
    history: list[InterviewProgressEntry]
    next_eligible: Optional[dict[str, datetime]] = None  # {vertical: next_eligible_date}

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    target_roles: list[str] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError("姓名至少需要2个字符")
        if len(v) > 50:
            raise ValueError("姓名不能超过50个字符")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Accept Chinese mobile (1xxxxxxxxxx) or international format (+xx xxx...)
        # Strip spaces and dashes for validation
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        # Chinese mobile: 11 digits starting with 1
        # International: starts with + followed by 7-15 digits
        # General: 7-15 digits
        if not re.match(r"^(\+?\d{7,15}|1[3-9]\d{9})$", cleaned):
            raise ValueError("Please enter a valid phone number")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少需要8个字符")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含至少一个数字")
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含至少一个字母")
        return v


class CandidateLogin(BaseModel):
    """Request for candidate login."""
    email: EmailStr
    password: str


class CandidateResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    target_roles: list[str]
    resume_url: Optional[str] = None
    created_at: datetime

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
    text_zh: str
    category: str  # behavioral, technical, experience
    based_on: str  # What resume element this is based on


# WeChat OAuth schemas
class WeChatAuthUrlResponse(BaseModel):
    """Response containing WeChat authorization URL."""
    auth_url: str
    state: str  # CSRF token


class WeChatLoginRequest(BaseModel):
    """Request to complete WeChat login with authorization code."""
    code: str
    state: Optional[str] = None  # For CSRF validation
    is_mini_program: bool = False


class WeChatLoginResponse(BaseModel):
    """Response after successful WeChat login."""
    candidate: CandidateResponse
    token: str
    token_type: str = "bearer"
    is_new_user: bool  # True if this is a new registration


class CandidateWithToken(BaseModel):
    """Candidate response with auth token (for login)."""
    candidate: CandidateResponse
    token: str
    token_type: str = "bearer"

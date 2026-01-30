from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime


class EmployerRegister(BaseModel):
    company_name: str
    email: EmailStr
    password: str

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


class EmployerResponse(BaseModel):
    id: str
    company_name: str
    email: str
    logo: Optional[str] = None
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
    requirements: list[str]
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

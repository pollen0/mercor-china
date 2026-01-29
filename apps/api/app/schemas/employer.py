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
            raise ValueError("公司名称至少需要2个字符")
        if len(v) > 100:
            raise ValueError("公司名称不能超过100个字符")
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
            raise ValueError("主题至少需要2个字符")
        if len(v) > 200:
            raise ValueError("主题不能超过200个字符")
        return v

    @field_validator("body")
    @classmethod
    def validate_body(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("内容至少需要10个字符")
        if len(v) > 5000:
            raise ValueError("内容不能超过5000个字符")
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
            raise ValueError("请至少选择一个面试")
        if len(v) > 100:
            raise ValueError("一次最多处理100个面试")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ['shortlist', 'reject']:
            raise ValueError("操作必须是 'shortlist' 或 'reject'")
        return v


class BulkActionResult(BaseModel):
    success: bool
    processed: int
    failed: int
    errors: list[str] = []

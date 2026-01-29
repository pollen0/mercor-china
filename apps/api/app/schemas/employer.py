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

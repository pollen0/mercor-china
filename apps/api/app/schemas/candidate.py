from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
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
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("请输入有效的中国手机号码")
        return v


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

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class InterviewStatusEnum(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class MatchStatusEnum(str, Enum):
    PENDING = "PENDING"
    SHORTLISTED = "SHORTLISTED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


# Request schemas
class InterviewStart(BaseModel):
    candidate_id: str
    job_id: str


class ResponseSubmit(BaseModel):
    question_index: int
    video_key: Optional[str] = None  # If using direct upload URL


class InterviewComplete(BaseModel):
    pass  # No additional data needed


class InterviewStatusUpdate(BaseModel):
    status: MatchStatusEnum


# Response schemas
class QuestionInfo(BaseModel):
    index: int
    text: str
    text_zh: Optional[str] = None
    category: Optional[str] = None


class InterviewStartResponse(BaseModel):
    session_id: str
    questions: list[QuestionInfo]
    job_title: str
    company_name: str


class ResponseSubmitResult(BaseModel):
    response_id: str
    question_index: int
    status: str
    video_url: Optional[str] = None


class ScoreDetails(BaseModel):
    communication: float  # 沟通能力
    problem_solving: float  # 解决问题能力
    domain_knowledge: float  # 专业知识
    motivation: float  # 动机
    culture_fit: float  # 文化契合度
    overall: float
    analysis: str
    strengths: list[str]
    concerns: list[str]
    highlight_quotes: list[str] = []


class ResponseDetail(BaseModel):
    id: str
    question_index: int
    question_text: str
    video_url: Optional[str] = None
    transcription: Optional[str] = None
    ai_score: Optional[float] = None
    ai_analysis: Optional[str] = None
    score_details: Optional[ScoreDetails] = None
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewSessionResponse(BaseModel):
    id: str
    status: InterviewStatusEnum
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    candidate_id: str
    candidate_name: Optional[str] = None
    job_id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    responses: list[ResponseDetail] = []

    class Config:
        from_attributes = True


class InterviewResults(BaseModel):
    session_id: str
    status: InterviewStatusEnum
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    recommendation: Optional[str] = None
    overall_strengths: list[str] = []
    overall_concerns: list[str] = []
    responses: list[ResponseDetail] = []


class InterviewListResponse(BaseModel):
    interviews: list[InterviewSessionResponse]
    total: int


class UploadUrlResponse(BaseModel):
    upload_url: str
    storage_key: str
    expires_in: int


# Invite Token schemas
class InviteTokenCreate(BaseModel):
    job_id: str
    max_uses: int = 0  # 0 = unlimited
    expires_in_days: Optional[int] = None


class InviteTokenResponse(BaseModel):
    id: str
    token: str
    job_id: str
    job_title: Optional[str] = None
    max_uses: int
    used_count: int
    expires_at: Optional[datetime] = None
    is_active: bool
    invite_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class InviteTokenList(BaseModel):
    tokens: list[InviteTokenResponse]
    total: int


class InviteValidation(BaseModel):
    valid: bool
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    error: Optional[str] = None


# Self-registration schemas
class CandidateRegisterAndStart(BaseModel):
    name: str
    email: str
    phone: str
    invite_token: str

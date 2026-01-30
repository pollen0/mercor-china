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
    job_id: Optional[str] = None  # Optional - if not provided, general interview
    is_practice: bool = False  # Practice mode flag


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
    question_type: str = "video"  # "video" or "coding"
    coding_challenge_id: Optional[str] = None


class InterviewStartResponse(BaseModel):
    session_id: str
    questions: list[QuestionInfo]
    job_title: str
    company_name: str
    is_practice: bool = False


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
    is_practice: bool = False
    total_score: Optional[float] = None
    ai_summary: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    candidate_id: str
    candidate_name: Optional[str] = None
    job_id: Optional[str] = None
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


# Practice mode feedback
class PracticeFeedback(BaseModel):
    """Immediate feedback for practice mode responses."""
    response_id: str
    question_index: int
    score_details: ScoreDetails
    tips: list[str]  # Improvement tips
    sample_answer: Optional[str] = None  # Optional model answer


# Follow-up question schemas
class FollowupStatusEnum(str, Enum):
    PENDING = "PENDING"
    ASKED = "ASKED"
    SKIPPED = "SKIPPED"


class FollowupQueueItem(BaseModel):
    """Represents a queue of follow-up questions for a specific base question."""
    id: str
    session_id: str
    question_index: int  # Which base question this is for
    generated_questions: list[str]  # Follow-up questions
    selected_index: Optional[int] = None  # Which was selected
    status: FollowupStatusEnum

    class Config:
        from_attributes = True


class FollowupResponse(BaseModel):
    """Response when checking for available follow-ups."""
    has_followups: bool
    question_index: int
    followup_questions: list[str] = []
    queue_id: Optional[str] = None


class AskFollowupRequest(BaseModel):
    """Request to ask a specific follow-up question."""
    followup_index: int  # Which follow-up question to ask (0 or 1)


class FollowupQuestionInfo(BaseModel):
    """Information about a follow-up question being asked."""
    queue_id: str
    question_index: int
    followup_index: int
    question_text: str
    is_followup: bool = True


# ==================== VERTICAL INTERVIEW (TALENT POOL) SCHEMAS ====================

class VerticalInterviewStart(BaseModel):
    """Request to start a vertical interview for talent pool."""
    candidate_id: str
    vertical: str  # 'new_energy' or 'sales'
    role_type: str  # e.g., 'battery_engineer', 'sales_rep'


class VerticalProfileResponse(BaseModel):
    """Response for a candidate's vertical profile."""
    id: str
    vertical: str
    role_type: str
    status: str  # 'pending', 'in_progress', 'completed'
    interview_score: Optional[float] = None
    best_score: Optional[float] = None
    attempt_count: int = 0
    last_attempt_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    can_retake: bool = False  # True if attempts < 3 and 24h since last attempt
    next_retake_available_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VerticalProfileList(BaseModel):
    """List of candidate's vertical profiles."""
    profiles: list[VerticalProfileResponse]
    total: int


class TalentPoolCandidate(BaseModel):
    """Candidate info for talent pool browsing."""
    id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    vertical: str
    role_type: str
    interview_score: float
    best_score: float
    status: str
    completed_at: Optional[datetime] = None
    # Resume data
    skills: list[str] = []
    experience_years: Optional[int] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True


class TalentPoolResponse(BaseModel):
    """Response for talent pool browse."""
    candidates: list[TalentPoolCandidate]
    total: int


class MatchingJobResponse(BaseModel):
    """Job that matches a candidate's vertical profile."""
    job_id: str
    job_title: str
    company_name: str
    vertical: str
    role_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    match_score: Optional[float] = None

    class Config:
        from_attributes = True


class MatchingJobsResponse(BaseModel):
    """List of jobs matching a candidate's vertical profiles."""
    jobs: list[MatchingJobResponse]
    total: int

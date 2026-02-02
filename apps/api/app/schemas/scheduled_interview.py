"""
Pydantic schemas for scheduled interview endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# Enums matching the model
class InterviewTypeEnum(str):
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURE_FIT = "culture_fit"
    FINAL = "final"
    OTHER = "other"


class ScheduledInterviewStatusEnum(str):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


# Request schemas
class ScheduleInterviewRequest(BaseModel):
    """Request to schedule an interview with a candidate."""
    interview_type: str = Field(default="other", description="Type of interview")
    title: Optional[str] = Field(None, description="Custom title (auto-generated if not provided)")
    description: Optional[str] = Field(None, description="Interview description/agenda")
    scheduled_at: datetime = Field(..., description="Interview start time")
    duration_minutes: int = Field(default=30, ge=15, le=180, description="Duration in minutes")
    timezone: str = Field(default="America/Los_Angeles", description="Timezone for the event")
    job_id: Optional[str] = Field(None, description="Associated job ID")
    additional_attendees: Optional[List[EmailStr]] = Field(None, description="Additional interviewer emails")
    employer_notes: Optional[str] = Field(None, description="Private notes (not visible to candidate)")


class RescheduleInterviewRequest(BaseModel):
    """Request to reschedule an existing interview."""
    scheduled_at: datetime = Field(..., description="New interview start time")
    duration_minutes: Optional[int] = Field(None, ge=15, le=180, description="New duration (optional)")
    timezone: Optional[str] = Field(None, description="New timezone (optional)")
    reason: Optional[str] = Field(None, description="Reason for rescheduling")


class UpdateInterviewStatusRequest(BaseModel):
    """Request to update interview status."""
    status: str = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Notes about status change")


# Response schemas
class ScheduledInterviewResponse(BaseModel):
    """Response for a scheduled interview."""
    id: str
    employer_id: str
    candidate_id: str
    candidate_name: Optional[str] = None
    candidate_email: Optional[str] = None
    job_id: Optional[str] = None
    job_title: Optional[str] = None

    title: str
    description: Optional[str] = None
    interview_type: str

    scheduled_at: datetime
    duration_minutes: int
    timezone: str

    google_event_id: Optional[str] = None
    google_meet_link: Optional[str] = None
    calendar_link: Optional[str] = None

    additional_attendees: Optional[List[str]] = None
    status: str
    employer_notes: Optional[str] = None

    rescheduled_to_id: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScheduleInterviewSuccessResponse(BaseModel):
    """Success response after scheduling an interview."""
    success: bool = True
    interview: ScheduledInterviewResponse
    google_meet_link: Optional[str] = None
    calendar_link: Optional[str] = None
    message: str = "Interview scheduled successfully"


class ScheduledInterviewListResponse(BaseModel):
    """Response for listing scheduled interviews."""
    interviews: List[ScheduledInterviewResponse]
    total: int


class CancelInterviewResponse(BaseModel):
    """Response after cancelling an interview."""
    success: bool
    message: str
    interview_id: str


class RescheduleInterviewResponse(BaseModel):
    """Response after rescheduling an interview."""
    success: bool
    message: str
    old_interview: ScheduledInterviewResponse
    new_interview: ScheduledInterviewResponse

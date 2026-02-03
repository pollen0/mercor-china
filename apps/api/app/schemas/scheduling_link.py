"""
Pydantic schemas for self-scheduling link endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# Request schemas
class SchedulingLinkCreate(BaseModel):
    """Request to create a self-scheduling link."""
    name: str = Field(..., min_length=1, max_length=255, description="Name for the link")
    description: Optional[str] = Field(None, max_length=1000, description="Description shown to candidates")
    job_id: Optional[str] = Field(None, description="Associated job ID")
    duration_minutes: int = Field(default=30, ge=15, le=180, description="Interview duration")
    interviewer_ids: List[str] = Field(..., min_length=1, description="List of interviewer team member IDs")
    buffer_before_minutes: int = Field(default=5, ge=0, le=60, description="Buffer time before interviews")
    buffer_after_minutes: int = Field(default=5, ge=0, le=60, description="Buffer time after interviews")
    min_notice_hours: int = Field(default=24, ge=1, le=168, description="Minimum hours notice required")
    max_days_ahead: int = Field(default=14, ge=1, le=90, description="Maximum days ahead for booking")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration time")


class SchedulingLinkUpdate(BaseModel):
    """Request to update a scheduling link."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    interviewer_ids: Optional[List[str]] = Field(None, min_length=1)
    buffer_before_minutes: Optional[int] = Field(None, ge=0, le=60)
    buffer_after_minutes: Optional[int] = Field(None, ge=0, le=60)
    min_notice_hours: Optional[int] = Field(None, ge=1, le=168)
    max_days_ahead: Optional[int] = Field(None, ge=1, le=90)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class BookSlotRequest(BaseModel):
    """Request to book an interview slot."""
    slot_start: datetime = Field(..., description="Start time of the selected slot")
    candidate_name: str = Field(..., min_length=1, max_length=255, description="Candidate's name")
    candidate_email: EmailStr = Field(..., description="Candidate's email")
    candidate_phone: Optional[str] = Field(None, max_length=20, description="Candidate's phone number")
    candidate_notes: Optional[str] = Field(None, max_length=1000, description="Notes from candidate")
    timezone: str = Field(default="America/Los_Angeles", description="Candidate's timezone")


# Response schemas
class InterviewerInfo(BaseModel):
    """Basic interviewer information."""
    id: str
    name: str
    email: str


class SchedulingLinkResponse(BaseModel):
    """Response for a scheduling link."""
    id: str
    employer_id: str
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    slug: str
    name: str
    description: Optional[str] = None
    duration_minutes: int
    interviewer_ids: List[str]
    interviewers: Optional[List[InterviewerInfo]] = None
    buffer_before_minutes: int
    buffer_after_minutes: int
    min_notice_hours: int
    max_days_ahead: int
    is_active: bool
    expires_at: Optional[datetime] = None
    view_count: int
    booking_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Full URL for sharing
    public_url: Optional[str] = None

    class Config:
        from_attributes = True


class SchedulingLinkListResponse(BaseModel):
    """Response for listing scheduling links."""
    links: List[SchedulingLinkResponse]
    total: int


class PublicSchedulingLinkResponse(BaseModel):
    """Public-facing response for a scheduling link (no auth required)."""
    id: str
    name: str
    description: Optional[str] = None
    duration_minutes: int
    company_name: str
    company_logo: Optional[str] = None
    job_title: Optional[str] = None
    min_notice_hours: int
    max_days_ahead: int
    timezone: str = "America/Los_Angeles"


class TimeSlotPublic(BaseModel):
    """A time slot for public display."""
    start: datetime
    end: datetime


class PublicAvailableSlotsResponse(BaseModel):
    """Public response for available slots."""
    link: PublicSchedulingLinkResponse
    slots: List[TimeSlotPublic]
    timezone: str


class BookingConfirmation(BaseModel):
    """Response after successfully booking a slot."""
    success: bool = True
    message: str = "Interview scheduled successfully"
    interview_id: str
    scheduled_at: datetime
    duration_minutes: int
    google_meet_link: Optional[str] = None
    calendar_link: Optional[str] = None
    interviewer_name: Optional[str] = None
    confirmation_email_sent: bool = False


class BookingError(BaseModel):
    """Error response for booking failures."""
    success: bool = False
    error: str
    error_code: str  # "slot_taken", "invalid_slot", "link_expired", "link_inactive"

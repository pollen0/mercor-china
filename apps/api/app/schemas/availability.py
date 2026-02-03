"""
Pydantic schemas for availability management endpoints.
"""
from datetime import datetime, date as date_type, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# Request schemas
class AvailabilitySlotCreate(BaseModel):
    """A single availability slot for a day of the week."""
    day_of_week: int = Field(..., ge=0, le=6, description="Day of week (0=Monday, 6=Sunday)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v


class SetAvailabilityRequest(BaseModel):
    """Request to set recurring weekly availability."""
    slots: List[AvailabilitySlotCreate] = Field(..., description="List of availability slots")
    timezone: str = Field(default="America/Los_Angeles", description="Timezone for the availability")


class AvailabilityExceptionCreate(BaseModel):
    """Request to create an availability exception."""
    date: date_type = Field(..., description="Date of the exception")
    is_unavailable: bool = Field(default=True, description="True to block time, False to add availability")
    start_time: Optional[str] = Field(None, description="Start time in HH:MM format (null for whole day)")
    end_time: Optional[str] = Field(None, description="End time in HH:MM format (null for whole day)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for the exception")

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v


class GetSlotsRequest(BaseModel):
    """Request to get available slots for a date range."""
    start_date: date_type = Field(..., description="Start of date range")
    end_date: date_type = Field(..., description="End of date range")
    duration_minutes: int = Field(default=30, ge=15, le=180, description="Duration of slots needed")


# Response schemas
class AvailabilitySlotResponse(BaseModel):
    """Response for an availability slot."""
    id: str
    team_member_id: str
    day_of_week: int
    start_time: str
    end_time: str
    timezone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AvailabilityExceptionResponse(BaseModel):
    """Response for an availability exception."""
    id: str
    team_member_id: str
    date: date_type
    is_unavailable: bool
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    """Full availability response for a team member."""
    team_member_id: str
    timezone: str
    slots: List[AvailabilitySlotResponse]
    exceptions: List[AvailabilityExceptionResponse]


class TimeSlot(BaseModel):
    """A specific available time slot."""
    start: datetime
    end: datetime
    interviewer_id: str
    interviewer_name: Optional[str] = None


class AvailableSlotsResponse(BaseModel):
    """Response for available time slots."""
    slots: List[TimeSlot]
    timezone: str
    total: int


class ConflictInfo(BaseModel):
    """Information about a scheduling conflict."""
    interviewer_id: str
    interviewer_name: str
    conflict_type: str  # "calendar", "existing_interview", "unavailable", "exception"
    conflict_start: datetime
    conflict_end: datetime
    description: Optional[str] = None


class ConflictCheckResponse(BaseModel):
    """Response for conflict check."""
    has_conflicts: bool
    conflicts: List[ConflictInfo]
    suggested_alternatives: Optional[List[TimeSlot]] = None

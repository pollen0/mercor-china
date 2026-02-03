"""
Pydantic schemas for team member management endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class TeamMemberRoleEnum(str):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"


# Request schemas
class TeamMemberCreate(BaseModel):
    """Request to add a new team member."""
    email: EmailStr = Field(..., description="Team member's email address")
    name: str = Field(..., min_length=1, max_length=255, description="Team member's full name")
    role: str = Field(default="interviewer", description="Role within the organization")
    max_interviews_per_day: int = Field(default=4, ge=1, le=20, description="Maximum interviews per day")
    max_interviews_per_week: int = Field(default=15, ge=1, le=50, description="Maximum interviews per week")


class TeamMemberUpdate(BaseModel):
    """Request to update a team member."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None
    is_active: Optional[bool] = None
    max_interviews_per_day: Optional[int] = Field(None, ge=1, le=20)
    max_interviews_per_week: Optional[int] = Field(None, ge=1, le=50)


class CalendarConnectRequest(BaseModel):
    """Request to connect Google Calendar."""
    code: str = Field(..., description="OAuth authorization code")
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI used")


# Response schemas
class TeamMemberResponse(BaseModel):
    """Response for a team member."""
    id: str
    employer_id: str
    email: str
    name: str
    role: str
    is_active: bool
    google_calendar_connected: bool
    google_calendar_connected_at: Optional[datetime] = None
    max_interviews_per_day: int
    max_interviews_per_week: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed fields
    interviews_today: Optional[int] = None
    interviews_this_week: Optional[int] = None

    class Config:
        from_attributes = True


class TeamMemberListResponse(BaseModel):
    """Response for listing team members."""
    team_members: List[TeamMemberResponse]
    total: int


class TeamMemberWithLoadResponse(TeamMemberResponse):
    """Team member with current load information."""
    interviews_today: int = 0
    interviews_this_week: int = 0
    available_today: bool = True
    available_this_week: bool = True


class CalendarConnectResponse(BaseModel):
    """Response after connecting Google Calendar."""
    success: bool
    message: str
    connected_at: Optional[datetime] = None


class CalendarDisconnectResponse(BaseModel):
    """Response after disconnecting Google Calendar."""
    success: bool
    message: str

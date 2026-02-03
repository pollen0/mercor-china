"""
API endpoints for managing employer team members.
Includes CRUD operations, calendar connection, and availability management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, date, time
import uuid

from ..database import get_db
from ..models import Employer
from ..models.team_member import EmployerTeamMember, TeamMemberRole
from ..models.availability import InterviewerAvailability, AvailabilityException
from ..schemas.team_member import (
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamMemberResponse,
    TeamMemberListResponse,
    TeamMemberWithLoadResponse,
    CalendarConnectRequest,
    CalendarConnectResponse,
    CalendarDisconnectResponse,
)
from ..schemas.availability import (
    SetAvailabilityRequest,
    AvailabilityExceptionCreate,
    AvailabilitySlotResponse,
    AvailabilityExceptionResponse,
    AvailabilityResponse,
    AvailableSlotsResponse,
    GetSlotsRequest,
    TimeSlot as TimeSlotSchema,
)
from ..services.availability import availability_service
from ..services.calendar import calendar_service
from ..utils.auth import verify_token
from ..utils.rate_limit import limiter, RateLimits

import logging

logger = logging.getLogger("pathway.team_members")
router = APIRouter()


def generate_cuid(prefix: str = "tm") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


async def get_current_employer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Employer:
    """Dependency to get the current authenticated employer."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer_id = payload.get("sub")
    if not employer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token content",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return employer


# Team Member CRUD Operations

@router.post("", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    data: TeamMemberCreate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Add a new team member to the organization."""
    # Check if email already exists for this employer
    existing = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.employer_id == employer.id,
        EmployerTeamMember.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A team member with this email already exists"
        )

    team_member = EmployerTeamMember(
        id=generate_cuid("tm"),
        employer_id=employer.id,
        email=data.email,
        name=data.name,
        role=TeamMemberRole(data.role) if data.role in [r.value for r in TeamMemberRole] else TeamMemberRole.INTERVIEWER,
        max_interviews_per_day=data.max_interviews_per_day,
        max_interviews_per_week=data.max_interviews_per_week,
    )

    db.add(team_member)
    db.commit()
    db.refresh(team_member)

    return TeamMemberResponse(
        id=team_member.id,
        employer_id=team_member.employer_id,
        email=team_member.email,
        name=team_member.name,
        role=team_member.role.value,
        is_active=team_member.is_active,
        google_calendar_connected=team_member.google_calendar_connected,
        google_calendar_connected_at=team_member.google_calendar_connected_at,
        max_interviews_per_day=team_member.max_interviews_per_day,
        max_interviews_per_week=team_member.max_interviews_per_week,
        created_at=team_member.created_at,
        updated_at=team_member.updated_at,
    )


@router.get("", response_model=TeamMemberListResponse)
async def list_team_members(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """List all team members for the organization."""
    query = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.employer_id == employer.id
    )

    if not include_inactive:
        query = query.filter(EmployerTeamMember.is_active == True)

    team_members = query.order_by(EmployerTeamMember.created_at.desc()).all()

    return TeamMemberListResponse(
        team_members=[
            TeamMemberResponse(
                id=tm.id,
                employer_id=tm.employer_id,
                email=tm.email,
                name=tm.name,
                role=tm.role.value,
                is_active=tm.is_active,
                google_calendar_connected=tm.google_calendar_connected,
                google_calendar_connected_at=tm.google_calendar_connected_at,
                max_interviews_per_day=tm.max_interviews_per_day,
                max_interviews_per_week=tm.max_interviews_per_week,
                created_at=tm.created_at,
                updated_at=tm.updated_at,
            )
            for tm in team_members
        ],
        total=len(team_members),
    )


@router.get("/{team_member_id}", response_model=TeamMemberWithLoadResponse)
async def get_team_member(
    team_member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Get a specific team member with current load information."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    # Get current load
    load = availability_service.get_interviewer_load(db, team_member_id)

    return TeamMemberWithLoadResponse(
        id=team_member.id,
        employer_id=team_member.employer_id,
        email=team_member.email,
        name=team_member.name,
        role=team_member.role.value,
        is_active=team_member.is_active,
        google_calendar_connected=team_member.google_calendar_connected,
        google_calendar_connected_at=team_member.google_calendar_connected_at,
        max_interviews_per_day=team_member.max_interviews_per_day,
        max_interviews_per_week=team_member.max_interviews_per_week,
        created_at=team_member.created_at,
        updated_at=team_member.updated_at,
        interviews_today=load["today"],
        interviews_this_week=load["week"],
        available_today=load["today"] < load["max_today"],
        available_this_week=load["week"] < load["max_week"],
    )


@router.patch("/{team_member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    team_member_id: str,
    data: TeamMemberUpdate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Update a team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    if data.name is not None:
        team_member.name = data.name
    if data.role is not None:
        team_member.role = TeamMemberRole(data.role) if data.role in [r.value for r in TeamMemberRole] else team_member.role
    if data.is_active is not None:
        team_member.is_active = data.is_active
    if data.max_interviews_per_day is not None:
        team_member.max_interviews_per_day = data.max_interviews_per_day
    if data.max_interviews_per_week is not None:
        team_member.max_interviews_per_week = data.max_interviews_per_week

    db.commit()
    db.refresh(team_member)

    return TeamMemberResponse(
        id=team_member.id,
        employer_id=team_member.employer_id,
        email=team_member.email,
        name=team_member.name,
        role=team_member.role.value,
        is_active=team_member.is_active,
        google_calendar_connected=team_member.google_calendar_connected,
        google_calendar_connected_at=team_member.google_calendar_connected_at,
        max_interviews_per_day=team_member.max_interviews_per_day,
        max_interviews_per_week=team_member.max_interviews_per_week,
        created_at=team_member.created_at,
        updated_at=team_member.updated_at,
    )


@router.delete("/{team_member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team_member(
    team_member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Delete a team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    db.delete(team_member)
    db.commit()


# Google Calendar Connection

@router.get("/{team_member_id}/calendar/connect-url")
async def get_calendar_connect_url(
    team_member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Get the Google OAuth URL for connecting calendar."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    if not calendar_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Calendar integration is not configured"
        )

    # State includes team member ID for callback
    state = f"tm:{team_member_id}"
    oauth_url = calendar_service.get_oauth_url(state=state, is_employer=True)

    return {"url": oauth_url}


@router.post("/{team_member_id}/calendar/connect", response_model=CalendarConnectResponse)
async def connect_calendar(
    team_member_id: str,
    data: CalendarConnectRequest,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Complete Google Calendar connection with OAuth code."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    try:
        tokens = await calendar_service.exchange_code(data.code, is_employer=True)

        team_member.google_calendar_token = tokens["access_token"]
        team_member.google_calendar_refresh_token = tokens["refresh_token"]
        team_member.google_calendar_connected = True
        team_member.google_calendar_connected_at = datetime.utcnow()

        db.commit()

        return CalendarConnectResponse(
            success=True,
            message="Google Calendar connected successfully",
            connected_at=team_member.google_calendar_connected_at,
        )
    except Exception as e:
        logger.error(f"Failed to connect calendar: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect calendar: {str(e)}"
        )


@router.delete("/{team_member_id}/calendar", response_model=CalendarDisconnectResponse)
async def disconnect_calendar(
    team_member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Disconnect Google Calendar from team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    team_member.google_calendar_token = None
    team_member.google_calendar_refresh_token = None
    team_member.google_calendar_connected = False
    team_member.google_calendar_connected_at = None

    db.commit()

    return CalendarDisconnectResponse(
        success=True,
        message="Google Calendar disconnected successfully"
    )


# Availability Management

@router.get("/{team_member_id}/availability", response_model=AvailabilityResponse)
async def get_availability(
    team_member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Get recurring availability for a team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    slots = db.query(InterviewerAvailability).filter(
        InterviewerAvailability.team_member_id == team_member_id,
        InterviewerAvailability.is_active == True
    ).all()

    exceptions = db.query(AvailabilityException).filter(
        AvailabilityException.team_member_id == team_member_id,
        AvailabilityException.date >= date.today()
    ).all()

    timezone = slots[0].timezone if slots else "America/Los_Angeles"

    return AvailabilityResponse(
        team_member_id=team_member_id,
        timezone=timezone,
        slots=[
            AvailabilitySlotResponse(
                id=s.id,
                team_member_id=s.team_member_id,
                day_of_week=s.day_of_week,
                start_time=s.start_time.strftime("%H:%M"),
                end_time=s.end_time.strftime("%H:%M"),
                timezone=s.timezone,
                is_active=s.is_active,
                created_at=s.created_at,
            )
            for s in slots
        ],
        exceptions=[
            AvailabilityExceptionResponse(
                id=e.id,
                team_member_id=e.team_member_id,
                date=e.date,
                is_unavailable=e.is_unavailable,
                start_time=e.start_time.strftime("%H:%M") if e.start_time else None,
                end_time=e.end_time.strftime("%H:%M") if e.end_time else None,
                reason=e.reason,
                created_at=e.created_at,
            )
            for e in exceptions
        ],
    )


@router.put("/{team_member_id}/availability")
async def set_availability(
    team_member_id: str,
    data: SetAvailabilityRequest,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Set recurring weekly availability for a team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    # Delete existing availability
    db.query(InterviewerAvailability).filter(
        InterviewerAvailability.team_member_id == team_member_id
    ).delete()

    # Create new availability slots
    for slot in data.slots:
        start_time = datetime.strptime(slot.start_time, "%H:%M").time()
        end_time = datetime.strptime(slot.end_time, "%H:%M").time()

        avail = InterviewerAvailability(
            id=generate_cuid("av"),
            team_member_id=team_member_id,
            day_of_week=slot.day_of_week,
            start_time=start_time,
            end_time=end_time,
            timezone=data.timezone,
            is_active=True,
        )
        db.add(avail)

    db.commit()

    return {"success": True, "message": "Availability updated successfully"}


@router.post("/{team_member_id}/availability/exceptions", response_model=AvailabilityExceptionResponse)
async def create_availability_exception(
    team_member_id: str,
    data: AvailabilityExceptionCreate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Add an availability exception (block or add time)."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    start_time = datetime.strptime(data.start_time, "%H:%M").time() if data.start_time else None
    end_time = datetime.strptime(data.end_time, "%H:%M").time() if data.end_time else None

    exception = AvailabilityException(
        id=generate_cuid("ex"),
        team_member_id=team_member_id,
        date=data.date,
        is_unavailable=data.is_unavailable,
        start_time=start_time,
        end_time=end_time,
        reason=data.reason,
    )

    db.add(exception)
    db.commit()
    db.refresh(exception)

    return AvailabilityExceptionResponse(
        id=exception.id,
        team_member_id=exception.team_member_id,
        date=exception.date,
        is_unavailable=exception.is_unavailable,
        start_time=exception.start_time.strftime("%H:%M") if exception.start_time else None,
        end_time=exception.end_time.strftime("%H:%M") if exception.end_time else None,
        reason=exception.reason,
        created_at=exception.created_at,
    )


@router.delete("/{team_member_id}/availability/exceptions/{exception_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_availability_exception(
    team_member_id: str,
    exception_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Delete an availability exception."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    exception = db.query(AvailabilityException).filter(
        AvailabilityException.id == exception_id,
        AvailabilityException.team_member_id == team_member_id
    ).first()

    if not exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exception not found"
        )

    db.delete(exception)
    db.commit()


@router.get("/{team_member_id}/slots", response_model=AvailableSlotsResponse)
async def get_available_slots(
    team_member_id: str,
    start_date: date,
    end_date: date,
    duration_minutes: int = 30,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Get available time slots for a team member."""
    team_member = db.query(EmployerTeamMember).filter(
        EmployerTeamMember.id == team_member_id,
        EmployerTeamMember.employer_id == employer.id
    ).first()

    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member not found"
        )

    slots = availability_service.get_available_slots(
        db=db,
        team_member_ids=[team_member_id],
        duration_minutes=duration_minutes,
        start_date=start_date,
        end_date=end_date,
    )

    # Get timezone from availability settings
    avail = db.query(InterviewerAvailability).filter(
        InterviewerAvailability.team_member_id == team_member_id
    ).first()
    timezone = avail.timezone if avail else "America/Los_Angeles"

    return AvailableSlotsResponse(
        slots=[
            TimeSlotSchema(
                start=s.start,
                end=s.end,
                interviewer_id=s.interviewer_id,
                interviewer_name=s.interviewer_name,
            )
            for s in slots
        ],
        timezone=timezone,
        total=len(slots),
    )

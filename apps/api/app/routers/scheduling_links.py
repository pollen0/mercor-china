"""
API endpoints for self-scheduling links.
Includes CRUD operations for employers and public booking endpoints for candidates.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import Employer, Job
from ..models.team_member import EmployerTeamMember
from ..models.scheduling_link import SelfSchedulingLink
from ..schemas.scheduling_link import (
    SchedulingLinkCreate,
    SchedulingLinkUpdate,
    SchedulingLinkResponse,
    SchedulingLinkListResponse,
    PublicSchedulingLinkResponse,
    PublicAvailableSlotsResponse,
    TimeSlotPublic,
    BookSlotRequest,
    BookingConfirmation,
    BookingError,
    InterviewerInfo,
)
from ..services.self_scheduling import self_scheduling_service
from ..services.reminder_scheduler import reminder_scheduler
from ..services.email import email_service
from ..utils.auth import verify_token
from ..config import settings

import logging

logger = logging.getLogger("pathway.scheduling_links")
router = APIRouter()


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


def build_link_response(link: SelfSchedulingLink, db: Session) -> SchedulingLinkResponse:
    """Build a SchedulingLinkResponse from a SelfSchedulingLink model."""
    # Get job title if exists
    job_title = None
    if link.job_id:
        job = db.query(Job).filter(Job.id == link.job_id).first()
        if job:
            job_title = job.title

    # Get interviewer info
    interviewers = []
    for interviewer_id in link.interviewer_ids or []:
        member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == interviewer_id
        ).first()
        if member:
            interviewers.append(InterviewerInfo(
                id=member.id,
                name=member.name,
                email=member.email,
            ))

    public_url = f"{settings.frontend_url}/schedule/{link.slug}"

    return SchedulingLinkResponse(
        id=link.id,
        employer_id=link.employer_id,
        job_id=link.job_id,
        job_title=job_title,
        slug=link.slug,
        name=link.name,
        description=link.description,
        duration_minutes=link.duration_minutes,
        interviewer_ids=link.interviewer_ids or [],
        interviewers=interviewers,
        buffer_before_minutes=link.buffer_before_minutes,
        buffer_after_minutes=link.buffer_after_minutes,
        min_notice_hours=link.min_notice_hours,
        max_days_ahead=link.max_days_ahead,
        is_active=link.is_active,
        expires_at=link.expires_at,
        view_count=link.view_count,
        booking_count=link.booking_count,
        created_at=link.created_at,
        updated_at=link.updated_at,
        public_url=public_url,
    )


# Employer endpoints (authenticated)

@router.post("", response_model=SchedulingLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_scheduling_link(
    data: SchedulingLinkCreate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Create a new self-scheduling link."""
    try:
        link = self_scheduling_service.create_link(
            db=db,
            employer_id=employer.id,
            name=data.name,
            interviewer_ids=data.interviewer_ids,
            duration_minutes=data.duration_minutes,
            job_id=data.job_id,
            description=data.description,
            buffer_before_minutes=data.buffer_before_minutes,
            buffer_after_minutes=data.buffer_after_minutes,
            min_notice_hours=data.min_notice_hours,
            max_days_ahead=data.max_days_ahead,
            expires_at=data.expires_at,
        )
        return build_link_response(link, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=SchedulingLinkListResponse)
async def list_scheduling_links(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """List all scheduling links for the organization."""
    links = self_scheduling_service.list_links(
        db=db,
        employer_id=employer.id,
        include_inactive=include_inactive,
    )

    return SchedulingLinkListResponse(
        links=[build_link_response(link, db) for link in links],
        total=len(links),
    )


@router.get("/{link_id}", response_model=SchedulingLinkResponse)
async def get_scheduling_link(
    link_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Get a specific scheduling link."""
    link = db.query(SelfSchedulingLink).filter(
        SelfSchedulingLink.id == link_id,
        SelfSchedulingLink.employer_id == employer.id
    ).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling link not found"
        )

    return build_link_response(link, db)


@router.patch("/{link_id}", response_model=SchedulingLinkResponse)
async def update_scheduling_link(
    link_id: str,
    data: SchedulingLinkUpdate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Update a scheduling link."""
    try:
        update_data = data.model_dump(exclude_unset=True)
        link = self_scheduling_service.update_link(
            db=db,
            link_id=link_id,
            employer_id=employer.id,
            **update_data,
        )

        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduling link not found"
            )

        return build_link_response(link, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scheduling_link(
    link_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Delete a scheduling link."""
    success = self_scheduling_service.delete_link(
        db=db,
        link_id=link_id,
        employer_id=employer.id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling link not found"
        )


# Public endpoints (no auth required)

@router.get("/public/{slug}", response_model=PublicAvailableSlotsResponse)
async def get_public_scheduling_link(
    slug: str,
    db: Session = Depends(get_db),
):
    """Get public scheduling link info and available slots."""
    link = self_scheduling_service.get_link_by_slug(db, slug, increment_view=True)

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling link not found"
        )

    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This scheduling link is no longer active"
        )

    if link.expires_at and link.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This scheduling link has expired"
        )

    # Get public info
    public_info = self_scheduling_service.get_public_link_info(db, slug)

    if not public_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling link not found"
        )

    # Get available slots
    slots = self_scheduling_service.get_available_slots(db, link)

    return PublicAvailableSlotsResponse(
        link=PublicSchedulingLinkResponse(
            id=public_info["id"],
            name=public_info["name"],
            description=public_info["description"],
            duration_minutes=public_info["duration_minutes"],
            company_name=public_info["company_name"],
            company_logo=public_info["company_logo"],
            job_title=public_info["job_title"],
            min_notice_hours=public_info["min_notice_hours"],
            max_days_ahead=public_info["max_days_ahead"],
        ),
        slots=[
            TimeSlotPublic(start=s.start, end=s.end)
            for s in slots
        ],
        timezone="America/Los_Angeles",  # Default timezone
    )


@router.post("/public/{slug}/book")
async def book_slot(
    slug: str,
    data: BookSlotRequest,
    db: Session = Depends(get_db),
):
    """Book an interview slot (public endpoint for candidates)."""
    link = self_scheduling_service.get_link_by_slug(db, slug)

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduling link not found"
        )

    interview, error = self_scheduling_service.book_slot(
        db=db,
        link=link,
        slot_start=data.slot_start,
        candidate_name=data.candidate_name,
        candidate_email=data.candidate_email,
        candidate_phone=data.candidate_phone,
        candidate_notes=data.candidate_notes,
        timezone=data.timezone,
    )

    if error:
        # Determine error code
        error_code = "booking_failed"
        if "no longer available" in error.lower():
            error_code = "slot_taken"
        elif "expired" in error.lower():
            error_code = "link_expired"
        elif "active" in error.lower():
            error_code = "link_inactive"
        elif "notice" in error.lower() or "advance" in error.lower():
            error_code = "invalid_slot"

        return BookingError(
            success=False,
            error=error,
            error_code=error_code,
        )

    # Schedule reminders
    try:
        reminder_scheduler.schedule_reminders(
            db=db,
            interview_id=interview.id,
            scheduled_at=interview.scheduled_at,
        )
    except Exception as e:
        logger.error(f"Failed to schedule reminders: {e}")

    # Send confirmation email to candidate
    confirmation_sent = False
    try:
        employer = db.query(Employer).filter(Employer.id == link.employer_id).first()
        if employer:
            email_service.send_interview_scheduled_candidate(
                to_email=data.candidate_email,
                candidate_name=data.candidate_name,
                company_name=employer.company_name,
                interview_title=interview.title,
                scheduled_at=interview.scheduled_at,
                duration_minutes=interview.duration_minutes,
                google_meet_link=interview.google_meet_link,
            )
            confirmation_sent = True
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")

    # Get interviewer name if available
    interviewer_name = None
    if interview.additional_attendees:
        member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.email == interview.additional_attendees[0]
        ).first()
        if member:
            interviewer_name = member.name

    return BookingConfirmation(
        success=True,
        message="Interview scheduled successfully",
        interview_id=interview.id,
        scheduled_at=interview.scheduled_at,
        duration_minutes=interview.duration_minutes,
        google_meet_link=interview.google_meet_link,
        calendar_link=interview.calendar_link,
        interviewer_name=interviewer_name,
        confirmation_email_sent=confirmation_sent,
    )


# Panel coordination endpoints

@router.post("/find-panel-slots")
async def find_panel_slots(
    interviewer_ids: list[str],
    duration_minutes: int = 30,
    days_ahead: int = 14,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Find available slots where all specified interviewers are free."""
    from datetime import date, timedelta
    from ..services.panel_coordination import panel_coordination_service

    # Verify all interviewers belong to this employer
    for interviewer_id in interviewer_ids:
        member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == interviewer_id,
            EmployerTeamMember.employer_id == employer.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interviewer: {interviewer_id}"
            )

    start_date = date.today()
    end_date = start_date + timedelta(days=days_ahead)

    slots = panel_coordination_service.find_panel_availability(
        db=db,
        interviewer_ids=interviewer_ids,
        duration_minutes=duration_minutes,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "slots": [s.to_dict() for s in slots],
        "total": len(slots),
    }


@router.post("/check-conflicts")
async def check_conflicts(
    interviewer_ids: list[str],
    proposed_start: datetime,
    duration_minutes: int = 30,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer),
):
    """Check for scheduling conflicts at a proposed time."""
    from ..services.panel_coordination import panel_coordination_service

    # Verify all interviewers belong to this employer
    for interviewer_id in interviewer_ids:
        member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == interviewer_id,
            EmployerTeamMember.employer_id == employer.id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interviewer: {interviewer_id}"
            )

    conflicts = panel_coordination_service.detect_conflicts(
        db=db,
        interviewer_ids=interviewer_ids,
        proposed_start=proposed_start,
        duration_minutes=duration_minutes,
    )

    suggested_alternatives = []
    if conflicts:
        alternatives = panel_coordination_service.suggest_alternatives(
            db=db,
            interviewer_ids=interviewer_ids,
            original_time=proposed_start,
            duration_minutes=duration_minutes,
        )
        suggested_alternatives = [a.to_dict() for a in alternatives]

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": [c.to_dict() for c in conflicts],
        "suggested_alternatives": suggested_alternatives,
    }

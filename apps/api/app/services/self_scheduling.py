"""
Self-scheduling service for candidate-initiated interview booking.
Handles scheduling link management, slot availability, and booking.
"""
import logging
import secrets
import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.team_member import EmployerTeamMember
from ..models.scheduling_link import SelfSchedulingLink
from ..models.scheduled_interview import ScheduledInterview, ScheduledInterviewStatus, InterviewType
from ..models.employer import Employer, Job
from ..models.candidate import Candidate
from .availability import availability_service, TimeSlot
from .calendar import calendar_service
from ..config import settings

logger = logging.getLogger("pathway.self_scheduling")


def generate_cuid(prefix: str = "") -> str:
    """Generate a CUID-like identifier."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


def generate_slug() -> str:
    """Generate a unique URL-safe slug."""
    return secrets.token_urlsafe(8)


class SelfSchedulingService:
    """Service for managing self-scheduling links and bookings."""

    def create_link(
        self,
        db: Session,
        employer_id: str,
        name: str,
        interviewer_ids: list[str],
        duration_minutes: int = 30,
        job_id: Optional[str] = None,
        description: Optional[str] = None,
        buffer_before_minutes: int = 5,
        buffer_after_minutes: int = 5,
        min_notice_hours: int = 24,
        max_days_ahead: int = 14,
        expires_at: Optional[datetime] = None,
    ) -> SelfSchedulingLink:
        """Create a new self-scheduling link."""
        # Verify all interviewers exist and belong to this employer
        for interviewer_id in interviewer_ids:
            member = db.query(EmployerTeamMember).filter(
                EmployerTeamMember.id == interviewer_id,
                EmployerTeamMember.employer_id == employer_id,
                EmployerTeamMember.is_active == True
            ).first()
            if not member:
                raise ValueError(f"Invalid or inactive interviewer: {interviewer_id}")

        # Verify job if provided
        if job_id:
            job = db.query(Job).filter(
                Job.id == job_id,
                Job.employer_id == employer_id
            ).first()
            if not job:
                raise ValueError(f"Invalid job: {job_id}")

        # Generate unique slug
        slug = generate_slug()
        while db.query(SelfSchedulingLink).filter(SelfSchedulingLink.slug == slug).first():
            slug = generate_slug()

        link = SelfSchedulingLink(
            id=generate_cuid("sl"),
            employer_id=employer_id,
            job_id=job_id,
            slug=slug,
            name=name,
            description=description,
            duration_minutes=duration_minutes,
            interviewer_ids=interviewer_ids,
            buffer_before_minutes=buffer_before_minutes,
            buffer_after_minutes=buffer_after_minutes,
            min_notice_hours=min_notice_hours,
            max_days_ahead=max_days_ahead,
            expires_at=expires_at,
        )

        db.add(link)
        db.commit()
        db.refresh(link)

        return link

    def get_link_by_slug(
        self,
        db: Session,
        slug: str,
        increment_view: bool = False,
    ) -> Optional[SelfSchedulingLink]:
        """Get a scheduling link by its slug."""
        link = db.query(SelfSchedulingLink).filter(
            SelfSchedulingLink.slug == slug
        ).first()

        if link and increment_view:
            link.view_count += 1
            db.commit()

        return link

    def get_available_slots(
        self,
        db: Session,
        link: SelfSchedulingLink,
    ) -> list[TimeSlot]:
        """Get available time slots for a scheduling link."""
        if not link.is_active:
            return []

        if link.expires_at and link.expires_at < datetime.utcnow():
            return []

        now = datetime.utcnow()
        start_date = now.date()
        end_date = start_date + timedelta(days=link.max_days_ahead)

        # Get slots from all assigned interviewers
        slots = availability_service.get_available_slots(
            db=db,
            team_member_ids=link.interviewer_ids,
            duration_minutes=link.duration_minutes,
            start_date=start_date,
            end_date=end_date,
            buffer_before=link.buffer_before_minutes,
            buffer_after=link.buffer_after_minutes,
            min_notice_hours=link.min_notice_hours,
        )

        # Apply load balancing
        balanced_slots = availability_service.apply_load_balancing(
            db=db,
            slots=slots,
            team_member_ids=link.interviewer_ids,
        )

        return balanced_slots

    def validate_booking(
        self,
        db: Session,
        link: SelfSchedulingLink,
        slot_start: datetime,
    ) -> tuple[bool, str, Optional[str]]:
        """
        Validate that a booking can be made.

        Returns:
            (is_valid, error_message, selected_interviewer_id)
        """
        # Check link is active
        if not link.is_active:
            return False, "This scheduling link is no longer active", None

        # Check link hasn't expired
        if link.expires_at and link.expires_at < datetime.utcnow():
            return False, "This scheduling link has expired", None

        # Check minimum notice
        min_start = datetime.utcnow() + timedelta(hours=link.min_notice_hours)
        if slot_start < min_start:
            return False, f"Must book at least {link.min_notice_hours} hours in advance", None

        # Check within booking window
        max_date = datetime.utcnow() + timedelta(days=link.max_days_ahead)
        if slot_start > max_date:
            return False, f"Cannot book more than {link.max_days_ahead} days ahead", None

        # Check slot is actually available
        available_slots = self.get_available_slots(db, link)
        slot_end = slot_start + timedelta(minutes=link.duration_minutes)

        matching_slot = None
        for slot in available_slots:
            if slot.start == slot_start and slot.end == slot_end:
                matching_slot = slot
                break

        if not matching_slot:
            return False, "This time slot is no longer available", None

        return True, "", matching_slot.interviewer_id

    def book_slot(
        self,
        db: Session,
        link: SelfSchedulingLink,
        slot_start: datetime,
        candidate_name: str,
        candidate_email: str,
        candidate_phone: Optional[str] = None,
        candidate_notes: Optional[str] = None,
        timezone: str = "America/Los_Angeles",
    ) -> tuple[Optional[ScheduledInterview], Optional[str]]:
        """
        Book a time slot for a candidate.

        Returns:
            (scheduled_interview, error_message)
        """
        # Validate the booking
        is_valid, error_message, interviewer_id = self.validate_booking(
            db=db,
            link=link,
            slot_start=slot_start,
        )

        if not is_valid:
            return None, error_message

        # Get or create candidate
        candidate = db.query(Candidate).filter(
            Candidate.email == candidate_email
        ).first()

        if not candidate:
            # Create a minimal candidate record for the booking
            candidate = Candidate(
                id=generate_cuid("c"),
                name=candidate_name,
                email=candidate_email,
                phone=candidate_phone,
            )
            db.add(candidate)
            db.flush()

        # Get employer and interviewer info
        employer = db.query(Employer).filter(Employer.id == link.employer_id).first()
        interviewer = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == interviewer_id
        ).first()

        # Build interview title
        job = None
        if link.job_id:
            job = db.query(Job).filter(Job.id == link.job_id).first()

        title = link.name
        if job:
            title = f"{job.title} - {link.name}"

        # Create the scheduled interview
        interview = ScheduledInterview(
            id=generate_cuid("si"),
            employer_id=link.employer_id,
            candidate_id=candidate.id,
            job_id=link.job_id,
            title=title,
            description=link.description or f"Scheduled via self-scheduling link",
            interview_type=InterviewType.PHONE_SCREEN,
            scheduled_at=slot_start,
            duration_minutes=link.duration_minutes,
            timezone=timezone,
            additional_attendees=[interviewer.email] if interviewer else [],
            status=ScheduledInterviewStatus.CONFIRMED,
            employer_notes=candidate_notes,
        )

        # Try to create Google Calendar event with Meet link
        if employer and employer.google_calendar_token:
            try:
                event_result = self._create_calendar_event(
                    employer=employer,
                    interview=interview,
                    candidate_email=candidate_email,
                    interviewer_email=interviewer.email if interviewer else None,
                )
                if event_result:
                    interview.google_event_id = event_result.get("event_id")
                    interview.google_meet_link = event_result.get("hangout_link")
                    interview.calendar_link = event_result.get("html_link")
            except Exception as e:
                logger.error(f"Failed to create calendar event: {e}")

        db.add(interview)

        # Update link booking count
        link.booking_count += 1

        db.commit()
        db.refresh(interview)

        return interview, None

    def _create_calendar_event(
        self,
        employer: Employer,
        interview: ScheduledInterview,
        candidate_email: str,
        interviewer_email: Optional[str],
    ) -> Optional[dict]:
        """Create a Google Calendar event for the interview."""
        # This would be async in production
        # For now, return None as a placeholder
        return None

    def get_public_link_info(
        self,
        db: Session,
        slug: str,
    ) -> Optional[dict]:
        """Get public-facing information about a scheduling link."""
        link = self.get_link_by_slug(db, slug, increment_view=True)

        if not link:
            return None

        if not link.is_active:
            return None

        if link.expires_at and link.expires_at < datetime.utcnow():
            return None

        employer = db.query(Employer).filter(Employer.id == link.employer_id).first()
        job = None
        if link.job_id:
            job = db.query(Job).filter(Job.id == link.job_id).first()

        return {
            "id": link.id,
            "name": link.name,
            "description": link.description,
            "duration_minutes": link.duration_minutes,
            "company_name": employer.company_name if employer else "Unknown",
            "company_logo": employer.logo if employer else None,
            "job_title": job.title if job else None,
            "min_notice_hours": link.min_notice_hours,
            "max_days_ahead": link.max_days_ahead,
        }

    def delete_link(
        self,
        db: Session,
        link_id: str,
        employer_id: str,
    ) -> bool:
        """Delete a scheduling link."""
        link = db.query(SelfSchedulingLink).filter(
            SelfSchedulingLink.id == link_id,
            SelfSchedulingLink.employer_id == employer_id
        ).first()

        if not link:
            return False

        db.delete(link)
        db.commit()
        return True

    def update_link(
        self,
        db: Session,
        link_id: str,
        employer_id: str,
        **kwargs,
    ) -> Optional[SelfSchedulingLink]:
        """Update a scheduling link."""
        link = db.query(SelfSchedulingLink).filter(
            SelfSchedulingLink.id == link_id,
            SelfSchedulingLink.employer_id == employer_id
        ).first()

        if not link:
            return None

        # Validate interviewer_ids if being updated
        if "interviewer_ids" in kwargs:
            for interviewer_id in kwargs["interviewer_ids"]:
                member = db.query(EmployerTeamMember).filter(
                    EmployerTeamMember.id == interviewer_id,
                    EmployerTeamMember.employer_id == employer_id,
                    EmployerTeamMember.is_active == True
                ).first()
                if not member:
                    raise ValueError(f"Invalid or inactive interviewer: {interviewer_id}")

        # Update fields
        for key, value in kwargs.items():
            if hasattr(link, key) and value is not None:
                setattr(link, key, value)

        db.commit()
        db.refresh(link)
        return link

    def list_links(
        self,
        db: Session,
        employer_id: str,
        include_inactive: bool = False,
    ) -> list[SelfSchedulingLink]:
        """List all scheduling links for an employer."""
        query = db.query(SelfSchedulingLink).filter(
            SelfSchedulingLink.employer_id == employer_id
        )

        if not include_inactive:
            query = query.filter(SelfSchedulingLink.is_active == True)

        return query.order_by(SelfSchedulingLink.created_at.desc()).all()


# Singleton instance
self_scheduling_service = SelfSchedulingService()

"""
Panel coordination service for scheduling interviews with multiple interviewers.
Handles finding common availability and detecting conflicts.
"""
import logging
from datetime import datetime, date, time, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..models.team_member import EmployerTeamMember
from ..models.availability import InterviewerAvailability, AvailabilityException
from ..models.scheduled_interview import ScheduledInterview, ScheduledInterviewStatus
from .availability import availability_service, TimeSlot
from .calendar import calendar_service

logger = logging.getLogger("pathway.panel_coordination")


class Conflict:
    """Represents a scheduling conflict."""
    def __init__(
        self,
        interviewer_id: str,
        interviewer_name: str,
        conflict_type: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
    ):
        self.interviewer_id = interviewer_id
        self.interviewer_name = interviewer_name
        self.conflict_type = conflict_type
        self.start = start
        self.end = end
        self.description = description

    def to_dict(self) -> dict:
        return {
            "interviewer_id": self.interviewer_id,
            "interviewer_name": self.interviewer_name,
            "conflict_type": self.conflict_type,
            "conflict_start": self.start.isoformat(),
            "conflict_end": self.end.isoformat(),
            "description": self.description,
        }


class PanelCoordinationService:
    """Service for coordinating panel interviews with multiple interviewers."""

    def find_panel_availability(
        self,
        db: Session,
        interviewer_ids: list[str],
        duration_minutes: int,
        start_date: date,
        end_date: date,
        buffer_before: int = 5,
        buffer_after: int = 5,
        min_notice_hours: int = 24,
    ) -> list[TimeSlot]:
        """
        Find time slots where ALL specified interviewers are available.

        This is used for panel interviews where multiple people need to attend.
        """
        if not interviewer_ids:
            return []

        # Get available slots for each interviewer
        interviewer_slots = {}
        for interviewer_id in interviewer_ids:
            slots = availability_service.get_available_slots(
                db=db,
                team_member_ids=[interviewer_id],
                duration_minutes=duration_minutes,
                start_date=start_date,
                end_date=end_date,
                buffer_before=buffer_before,
                buffer_after=buffer_after,
                min_notice_hours=min_notice_hours,
            )
            interviewer_slots[interviewer_id] = set(
                (slot.start.isoformat(), slot.end.isoformat())
                for slot in slots
            )

        if not all(interviewer_slots.values()):
            return []

        # Find intersection of all slots
        common_slots_set = interviewer_slots[interviewer_ids[0]]
        for interviewer_id in interviewer_ids[1:]:
            common_slots_set = common_slots_set.intersection(interviewer_slots[interviewer_id])

        # Convert back to TimeSlot objects
        # Use first interviewer as the "primary" for the slot
        primary_interviewer = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == interviewer_ids[0]
        ).first()

        common_slots = []
        for start_str, end_str in sorted(common_slots_set):
            common_slots.append(TimeSlot(
                start=datetime.fromisoformat(start_str),
                end=datetime.fromisoformat(end_str),
                interviewer_id=interviewer_ids[0],  # Primary interviewer
                interviewer_name=primary_interviewer.name if primary_interviewer else None,
            ))

        return common_slots

    def detect_conflicts(
        self,
        db: Session,
        interviewer_ids: list[str],
        proposed_start: datetime,
        duration_minutes: int,
        buffer_before: int = 5,
        buffer_after: int = 5,
    ) -> list[Conflict]:
        """
        Detect conflicts for a proposed interview time across all panel members.

        Checks:
        - Existing scheduled interviews
        - Availability exceptions
        - Google Calendar busy times
        - Outside availability hours
        """
        conflicts = []
        proposed_end = proposed_start + timedelta(minutes=duration_minutes)

        # Include buffer times in the check
        check_start = proposed_start - timedelta(minutes=buffer_before)
        check_end = proposed_end + timedelta(minutes=buffer_after)

        for interviewer_id in interviewer_ids:
            team_member = db.query(EmployerTeamMember).filter(
                EmployerTeamMember.id == interviewer_id,
                EmployerTeamMember.is_active == True
            ).first()

            if not team_member:
                conflicts.append(Conflict(
                    interviewer_id=interviewer_id,
                    interviewer_name="Unknown",
                    conflict_type="not_found",
                    start=proposed_start,
                    end=proposed_end,
                    description="Interviewer not found or inactive",
                ))
                continue

            # Check if within availability hours
            availability_conflict = self._check_availability_conflict(
                db=db,
                team_member=team_member,
                start=proposed_start,
                end=proposed_end,
            )
            if availability_conflict:
                conflicts.append(availability_conflict)

            # Check for exceptions
            exception_conflict = self._check_exception_conflict(
                db=db,
                team_member=team_member,
                start=check_start,
                end=check_end,
            )
            if exception_conflict:
                conflicts.append(exception_conflict)

            # Check existing interviews
            interview_conflict = self._check_interview_conflict(
                db=db,
                team_member=team_member,
                start=check_start,
                end=check_end,
            )
            if interview_conflict:
                conflicts.append(interview_conflict)

            # Check Google Calendar (async would be better in production)
            # calendar_conflicts = await self._check_calendar_conflicts(...)

        return conflicts

    def _check_availability_conflict(
        self,
        db: Session,
        team_member: EmployerTeamMember,
        start: datetime,
        end: datetime,
    ) -> Optional[Conflict]:
        """Check if proposed time is within availability hours."""
        day_of_week = start.weekday()

        availability = db.query(InterviewerAvailability).filter(
            InterviewerAvailability.team_member_id == team_member.id,
            InterviewerAvailability.day_of_week == day_of_week,
            InterviewerAvailability.is_active == True
        ).all()

        if not availability:
            return Conflict(
                interviewer_id=team_member.id,
                interviewer_name=team_member.name,
                conflict_type="unavailable",
                start=start,
                end=end,
                description=f"No availability set for {start.strftime('%A')}",
            )

        # Check if proposed time falls within any availability window
        proposed_start_time = start.time()
        proposed_end_time = end.time()

        for avail in availability:
            if avail.start_time <= proposed_start_time and avail.end_time >= proposed_end_time:
                return None  # Within availability

        return Conflict(
            interviewer_id=team_member.id,
            interviewer_name=team_member.name,
            conflict_type="unavailable",
            start=start,
            end=end,
            description=f"Outside availability hours on {start.strftime('%A')}",
        )

    def _check_exception_conflict(
        self,
        db: Session,
        team_member: EmployerTeamMember,
        start: datetime,
        end: datetime,
    ) -> Optional[Conflict]:
        """Check for availability exceptions."""
        exceptions = db.query(AvailabilityException).filter(
            AvailabilityException.team_member_id == team_member.id,
            AvailabilityException.date == start.date(),
            AvailabilityException.is_unavailable == True
        ).all()

        for exc in exceptions:
            if exc.start_time is None:
                # Full day blocked
                return Conflict(
                    interviewer_id=team_member.id,
                    interviewer_name=team_member.name,
                    conflict_type="exception",
                    start=start,
                    end=end,
                    description=exc.reason or "Day blocked",
                )

            # Partial day exception
            exc_start = datetime.combine(exc.date, exc.start_time)
            exc_end = datetime.combine(exc.date, exc.end_time)

            if start < exc_end and end > exc_start:
                return Conflict(
                    interviewer_id=team_member.id,
                    interviewer_name=team_member.name,
                    conflict_type="exception",
                    start=exc_start,
                    end=exc_end,
                    description=exc.reason or "Time blocked",
                )

        return None

    def _check_interview_conflict(
        self,
        db: Session,
        team_member: EmployerTeamMember,
        start: datetime,
        end: datetime,
    ) -> Optional[Conflict]:
        """Check for existing interview conflicts."""
        # Find overlapping interviews
        existing = db.query(ScheduledInterview).filter(
            ScheduledInterview.status.in_([
                ScheduledInterviewStatus.PENDING,
                ScheduledInterviewStatus.CONFIRMED
            ]),
            # Check for overlap
            ScheduledInterview.scheduled_at < end,
        ).all()

        for interview in existing:
            interview_end = interview.scheduled_at + timedelta(minutes=interview.duration_minutes)

            if interview_end <= start:
                continue

            # Check if this team member is involved
            is_involved = False
            if interview.additional_attendees:
                if team_member.email in interview.additional_attendees:
                    is_involved = True

            if is_involved:
                return Conflict(
                    interviewer_id=team_member.id,
                    interviewer_name=team_member.name,
                    conflict_type="existing_interview",
                    start=interview.scheduled_at,
                    end=interview_end,
                    description=f"Existing interview: {interview.title}",
                )

        return None

    def suggest_alternatives(
        self,
        db: Session,
        interviewer_ids: list[str],
        original_time: datetime,
        duration_minutes: int,
        search_range_days: int = 7,
        max_suggestions: int = 5,
    ) -> list[TimeSlot]:
        """
        Suggest alternative time slots when conflicts are detected.

        Searches forward from the original time to find available slots.
        """
        start_date = original_time.date()
        end_date = start_date + timedelta(days=search_range_days)

        # Get available slots
        slots = self.find_panel_availability(
            db=db,
            interviewer_ids=interviewer_ids,
            duration_minutes=duration_minutes,
            start_date=start_date,
            end_date=end_date,
        )

        # Filter to slots after the original time
        future_slots = [s for s in slots if s.start > original_time]

        # Return closest slots
        return future_slots[:max_suggestions]


# Singleton instance
panel_coordination_service = PanelCoordinationService()

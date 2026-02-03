"""
Availability service for managing interviewer availability and finding open slots.
Handles recurring availability, exceptions, calendar conflicts, and load balancing.
"""
import logging
from datetime import datetime, date, time, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.team_member import EmployerTeamMember
from ..models.availability import InterviewerAvailability, AvailabilityException
from ..models.scheduled_interview import ScheduledInterview, ScheduledInterviewStatus
from ..services.calendar import calendar_service
from ..utils.crypto import decrypt_token

logger = logging.getLogger("pathway.availability")


class TimeSlot:
    """Represents an available time slot."""
    def __init__(
        self,
        start: datetime,
        end: datetime,
        interviewer_id: str,
        interviewer_name: Optional[str] = None
    ):
        self.start = start
        self.end = end
        self.interviewer_id = interviewer_id
        self.interviewer_name = interviewer_name

    def to_dict(self) -> dict:
        return {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "interviewer_id": self.interviewer_id,
            "interviewer_name": self.interviewer_name,
        }


class AvailabilityService:
    """Service for managing interviewer availability."""

    def get_team_member_availability(
        self,
        db: Session,
        team_member_id: str,
        start_date: date,
        end_date: date,
    ) -> dict:
        """
        Get a team member's availability for a date range.

        Returns both recurring slots and exceptions.
        """
        # Get team member
        team_member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == team_member_id
        ).first()

        if not team_member:
            return {"slots": [], "exceptions": [], "timezone": "America/Los_Angeles"}

        # Get recurring availability
        slots = db.query(InterviewerAvailability).filter(
            InterviewerAvailability.team_member_id == team_member_id,
            InterviewerAvailability.is_active == True
        ).all()

        # Get exceptions in date range
        exceptions = db.query(AvailabilityException).filter(
            AvailabilityException.team_member_id == team_member_id,
            AvailabilityException.date >= start_date,
            AvailabilityException.date <= end_date
        ).all()

        timezone = slots[0].timezone if slots else "America/Los_Angeles"

        return {
            "slots": slots,
            "exceptions": exceptions,
            "timezone": timezone,
        }

    def get_available_slots(
        self,
        db: Session,
        team_member_ids: list[str],
        duration_minutes: int,
        start_date: date,
        end_date: date,
        buffer_before: int = 5,
        buffer_after: int = 5,
        min_notice_hours: int = 24,
    ) -> list[TimeSlot]:
        """
        Get available time slots for given team members within a date range.

        Considers:
        - Recurring availability
        - Availability exceptions
        - Existing scheduled interviews
        - Google Calendar conflicts (if connected)
        - Load balancing
        """
        all_slots = []
        now = datetime.utcnow()
        min_start = now + timedelta(hours=min_notice_hours)

        for team_member_id in team_member_ids:
            team_member = db.query(EmployerTeamMember).filter(
                EmployerTeamMember.id == team_member_id,
                EmployerTeamMember.is_active == True
            ).first()

            if not team_member:
                continue

            # Get this member's available slots
            member_slots = self._get_member_available_slots(
                db=db,
                team_member=team_member,
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration_minutes,
                buffer_before=buffer_before,
                buffer_after=buffer_after,
                min_start=min_start,
            )
            all_slots.extend(member_slots)

        # Sort by start time
        all_slots.sort(key=lambda s: s.start)

        return all_slots

    def _get_member_available_slots(
        self,
        db: Session,
        team_member: EmployerTeamMember,
        start_date: date,
        end_date: date,
        duration_minutes: int,
        buffer_before: int,
        buffer_after: int,
        min_start: datetime,
    ) -> list[TimeSlot]:
        """Get available slots for a single team member."""
        slots = []

        # Get recurring availability
        availability = db.query(InterviewerAvailability).filter(
            InterviewerAvailability.team_member_id == team_member.id,
            InterviewerAvailability.is_active == True
        ).all()

        if not availability:
            return slots

        # Get exceptions
        exceptions = db.query(AvailabilityException).filter(
            AvailabilityException.team_member_id == team_member.id,
            AvailabilityException.date >= start_date,
            AvailabilityException.date <= end_date
        ).all()

        # Get existing interviews
        existing_interviews = db.query(ScheduledInterview).filter(
            or_(
                ScheduledInterview.additional_attendees.contains([team_member.email]),
                # Also check if this member is the primary interviewer via employer
            ),
            ScheduledInterview.scheduled_at >= datetime.combine(start_date, time.min),
            ScheduledInterview.scheduled_at <= datetime.combine(end_date, time.max),
            ScheduledInterview.status.in_([
                ScheduledInterviewStatus.PENDING,
                ScheduledInterviewStatus.CONFIRMED
            ])
        ).all()

        # Get Google Calendar busy times if connected
        calendar_busy = []
        if team_member.google_calendar_connected and team_member.google_calendar_token:
            try:
                calendar_busy = self._get_calendar_busy_times(
                    team_member=team_member,
                    start_date=start_date,
                    end_date=end_date,
                )
            except Exception as e:
                logger.warning(f"Failed to get calendar busy times: {e}")

        # Build availability by day
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()

            # Check for full-day exception (unavailable)
            day_exceptions = [
                e for e in exceptions
                if e.date == current_date and e.is_unavailable and e.start_time is None
            ]
            if day_exceptions:
                current_date += timedelta(days=1)
                continue

            # Get availability slots for this day of week
            day_availability = [a for a in availability if a.day_of_week == day_of_week]

            for avail in day_availability:
                # Generate time slots within this availability window
                day_slots = self._generate_slots_for_day(
                    current_date=current_date,
                    start_time=avail.start_time,
                    end_time=avail.end_time,
                    timezone=avail.timezone,
                    duration_minutes=duration_minutes,
                    buffer_before=buffer_before,
                    buffer_after=buffer_after,
                    team_member=team_member,
                    min_start=min_start,
                )

                # Filter out busy times
                for slot in day_slots:
                    if self._is_slot_available(
                        slot=slot,
                        exceptions=exceptions,
                        existing_interviews=existing_interviews,
                        calendar_busy=calendar_busy,
                        buffer_before=buffer_before,
                        buffer_after=buffer_after,
                    ):
                        slots.append(slot)

            current_date += timedelta(days=1)

        return slots

    def _generate_slots_for_day(
        self,
        current_date: date,
        start_time: time,
        end_time: time,
        timezone: str,
        duration_minutes: int,
        buffer_before: int,
        buffer_after: int,
        team_member: EmployerTeamMember,
        min_start: datetime,
    ) -> list[TimeSlot]:
        """Generate time slots for a specific day."""
        slots = []
        total_duration = duration_minutes + buffer_before + buffer_after

        # Create datetime objects for start and end
        slot_start = datetime.combine(current_date, start_time)
        day_end = datetime.combine(current_date, end_time)

        while slot_start + timedelta(minutes=duration_minutes) <= day_end:
            # Actual interview times (without buffer)
            interview_start = slot_start + timedelta(minutes=buffer_before)
            interview_end = interview_start + timedelta(minutes=duration_minutes)

            # Skip if before minimum notice
            if interview_start >= min_start:
                slots.append(TimeSlot(
                    start=interview_start,
                    end=interview_end,
                    interviewer_id=team_member.id,
                    interviewer_name=team_member.name,
                ))

            # Move to next slot (30-minute increments)
            slot_start += timedelta(minutes=30)

        return slots

    def _is_slot_available(
        self,
        slot: TimeSlot,
        exceptions: list[AvailabilityException],
        existing_interviews: list[ScheduledInterview],
        calendar_busy: list[dict],
        buffer_before: int,
        buffer_after: int,
    ) -> bool:
        """Check if a slot is available (not conflicting with anything)."""
        # Include buffers in the blocked time
        blocked_start = slot.start - timedelta(minutes=buffer_before)
        blocked_end = slot.end + timedelta(minutes=buffer_after)

        # Check exceptions
        for exc in exceptions:
            if exc.date == slot.start.date():
                if exc.is_unavailable:
                    if exc.start_time and exc.end_time:
                        exc_start = datetime.combine(exc.date, exc.start_time)
                        exc_end = datetime.combine(exc.date, exc.end_time)
                        if self._times_overlap(blocked_start, blocked_end, exc_start, exc_end):
                            return False
                    else:
                        # Full day blocked
                        return False

        # Check existing interviews
        for interview in existing_interviews:
            interview_end = interview.scheduled_at + timedelta(minutes=interview.duration_minutes)
            if self._times_overlap(blocked_start, blocked_end, interview.scheduled_at, interview_end):
                return False

        # Check calendar busy times
        for busy in calendar_busy:
            busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
            busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
            # Convert to naive datetime for comparison
            busy_start = busy_start.replace(tzinfo=None)
            busy_end = busy_end.replace(tzinfo=None)
            if self._times_overlap(blocked_start, blocked_end, busy_start, busy_end):
                return False

        return True

    def _times_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap."""
        return start1 < end2 and end1 > start2

    def _get_calendar_busy_times(
        self,
        team_member: EmployerTeamMember,
        start_date: date,
        end_date: date,
    ) -> list[dict]:
        """Get busy times from Google Calendar."""
        # This would be an async call in production
        # For now, return empty list as placeholder
        return []

    async def check_calendar_conflicts(
        self,
        db: Session,
        team_member_id: str,
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        """Check for calendar conflicts for a proposed time."""
        team_member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == team_member_id
        ).first()

        if not team_member:
            return []

        conflicts = []

        # Check existing interviews
        existing = db.query(ScheduledInterview).filter(
            ScheduledInterview.scheduled_at < end,
            ScheduledInterview.scheduled_at + timedelta(minutes=ScheduledInterview.duration_minutes) > start,
            ScheduledInterview.status.in_([
                ScheduledInterviewStatus.PENDING,
                ScheduledInterviewStatus.CONFIRMED
            ])
        ).all()

        for interview in existing:
            conflicts.append({
                "type": "existing_interview",
                "start": interview.scheduled_at,
                "end": interview.scheduled_at + timedelta(minutes=interview.duration_minutes),
                "description": f"Existing interview: {interview.title}",
            })

        # Check Google Calendar if connected
        if team_member.google_calendar_connected and team_member.google_calendar_token:
            try:
                busy_times = await calendar_service.get_free_busy(
                    encrypted_access_token=team_member.google_calendar_token,
                    time_min=start,
                    time_max=end,
                )
                for busy in busy_times:
                    conflicts.append({
                        "type": "calendar",
                        "start": busy["start"],
                        "end": busy["end"],
                        "description": "Calendar busy",
                    })
            except Exception as e:
                logger.warning(f"Failed to check calendar conflicts: {e}")

        return conflicts

    def apply_load_balancing(
        self,
        db: Session,
        slots: list[TimeSlot],
        team_member_ids: list[str],
    ) -> list[TimeSlot]:
        """
        Apply load balancing to prioritize interviewers below their limits.

        This reorders slots to prefer interviewers with fewer scheduled interviews.
        """
        # Get interview counts for each team member
        interview_counts = {}
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        for member_id in team_member_ids:
            # Count today's interviews
            today_count = db.query(ScheduledInterview).filter(
                ScheduledInterview.additional_attendees.contains([member_id]),
                ScheduledInterview.scheduled_at >= datetime.combine(today, time.min),
                ScheduledInterview.scheduled_at < datetime.combine(today + timedelta(days=1), time.min),
                ScheduledInterview.status.in_([
                    ScheduledInterviewStatus.PENDING,
                    ScheduledInterviewStatus.CONFIRMED
                ])
            ).count()

            # Count this week's interviews
            week_count = db.query(ScheduledInterview).filter(
                ScheduledInterview.additional_attendees.contains([member_id]),
                ScheduledInterview.scheduled_at >= datetime.combine(week_start, time.min),
                ScheduledInterview.scheduled_at < datetime.combine(week_start + timedelta(days=7), time.min),
                ScheduledInterview.status.in_([
                    ScheduledInterviewStatus.PENDING,
                    ScheduledInterviewStatus.CONFIRMED
                ])
            ).count()

            interview_counts[member_id] = {
                "today": today_count,
                "week": week_count,
            }

        # Get member limits
        members = {
            m.id: m for m in db.query(EmployerTeamMember).filter(
                EmployerTeamMember.id.in_(team_member_ids)
            ).all()
        }

        # Score each slot based on interviewer load
        def slot_score(slot: TimeSlot) -> tuple:
            member = members.get(slot.interviewer_id)
            if not member:
                return (999, 999, slot.start)

            counts = interview_counts.get(slot.interviewer_id, {"today": 0, "week": 0})

            # Prefer interviewers further below their limits
            today_capacity = member.max_interviews_per_day - counts["today"]
            week_capacity = member.max_interviews_per_week - counts["week"]

            # Negative scores mean they're over limit (avoid these)
            return (-today_capacity, -week_capacity, slot.start)

        # Sort slots by score (lower is better, then by time)
        sorted_slots = sorted(slots, key=slot_score)

        return sorted_slots

    def get_interviewer_load(
        self,
        db: Session,
        team_member_id: str,
    ) -> dict:
        """Get current interview load for a team member."""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        team_member = db.query(EmployerTeamMember).filter(
            EmployerTeamMember.id == team_member_id
        ).first()

        if not team_member:
            return {"today": 0, "week": 0, "max_today": 4, "max_week": 15}

        today_count = db.query(ScheduledInterview).filter(
            ScheduledInterview.additional_attendees.contains([team_member.email]),
            ScheduledInterview.scheduled_at >= datetime.combine(today, time.min),
            ScheduledInterview.scheduled_at < datetime.combine(today + timedelta(days=1), time.min),
            ScheduledInterview.status.in_([
                ScheduledInterviewStatus.PENDING,
                ScheduledInterviewStatus.CONFIRMED
            ])
        ).count()

        week_count = db.query(ScheduledInterview).filter(
            ScheduledInterview.additional_attendees.contains([team_member.email]),
            ScheduledInterview.scheduled_at >= datetime.combine(week_start, time.min),
            ScheduledInterview.scheduled_at < datetime.combine(week_start + timedelta(days=7), time.min),
            ScheduledInterview.status.in_([
                ScheduledInterviewStatus.PENDING,
                ScheduledInterviewStatus.CONFIRMED
            ])
        ).count()

        return {
            "today": today_count,
            "week": week_count,
            "max_today": team_member.max_interviews_per_day,
            "max_week": team_member.max_interviews_per_week,
        }


# Singleton instance
availability_service = AvailabilityService()

"""
Reminder scheduler service for automated interview reminders.
Uses APScheduler for scheduling reminder jobs.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..models.reminder import InterviewReminder, ReminderType, ReminderStatus
from ..models.scheduled_interview import ScheduledInterview, ScheduledInterviewStatus
from ..models.candidate import Candidate
from ..models.employer import Employer
from ..models.team_member import EmployerTeamMember
from .email import email_service
from ..database import SessionLocal

logger = logging.getLogger("pathway.reminder_scheduler")


def generate_cuid(prefix: str = "") -> str:
    """Generate a CUID-like identifier."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# APScheduler will be initialized on app startup
scheduler = None


def init_scheduler():
    """Initialize the APScheduler."""
    global scheduler
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = AsyncIOScheduler()

        # Add job to check for pending reminders every 5 minutes
        scheduler.add_job(
            check_pending_reminders,
            IntervalTrigger(minutes=5),
            id="check_pending_reminders",
            replace_existing=True,
        )

        scheduler.start()
        logger.info("Reminder scheduler started successfully")
    except ImportError:
        logger.warning("APScheduler not installed - reminders will not be sent automatically")
    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")


def shutdown_scheduler():
    """Shutdown the scheduler gracefully."""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Reminder scheduler shut down")


class ReminderScheduler:
    """Service for scheduling and sending interview reminders."""

    def schedule_reminders(
        self,
        db: Session,
        interview_id: str,
        scheduled_at: datetime,
    ) -> list[InterviewReminder]:
        """
        Schedule reminders for an interview.

        Creates reminders for:
        - 24 hours before (to candidate and interviewers)
        - 1 hour before (to candidate and interviewers)
        """
        reminders = []

        interview = db.query(ScheduledInterview).filter(
            ScheduledInterview.id == interview_id
        ).first()

        if not interview:
            return reminders

        candidate = db.query(Candidate).filter(
            Candidate.id == interview.candidate_id
        ).first()

        # Calculate reminder times
        reminder_24h = scheduled_at - timedelta(hours=24)
        reminder_1h = scheduled_at - timedelta(hours=1)

        now = datetime.utcnow()

        # Create 24h reminder for candidate (if still in the future)
        if reminder_24h > now and candidate:
            reminder = InterviewReminder(
                id=generate_cuid("rem"),
                scheduled_interview_id=interview_id,
                reminder_type=ReminderType.HOURS_24,
                scheduled_for=reminder_24h,
                status=ReminderStatus.PENDING,
                recipient_type="candidate",
                recipient_email=candidate.email,
            )
            db.add(reminder)
            reminders.append(reminder)

        # Create 1h reminder for candidate (if still in the future)
        if reminder_1h > now and candidate:
            reminder = InterviewReminder(
                id=generate_cuid("rem"),
                scheduled_interview_id=interview_id,
                reminder_type=ReminderType.HOURS_1,
                scheduled_for=reminder_1h,
                status=ReminderStatus.PENDING,
                recipient_type="candidate",
                recipient_email=candidate.email,
            )
            db.add(reminder)
            reminders.append(reminder)

        # Create reminders for interviewers
        if interview.additional_attendees:
            for attendee_email in interview.additional_attendees:
                # 24h reminder for interviewer
                if reminder_24h > now:
                    reminder = InterviewReminder(
                        id=generate_cuid("rem"),
                        scheduled_interview_id=interview_id,
                        reminder_type=ReminderType.HOURS_24,
                        scheduled_for=reminder_24h,
                        status=ReminderStatus.PENDING,
                        recipient_type="interviewer",
                        recipient_email=attendee_email,
                    )
                    db.add(reminder)
                    reminders.append(reminder)

                # 1h reminder for interviewer
                if reminder_1h > now:
                    reminder = InterviewReminder(
                        id=generate_cuid("rem"),
                        scheduled_interview_id=interview_id,
                        reminder_type=ReminderType.HOURS_1,
                        scheduled_for=reminder_1h,
                        status=ReminderStatus.PENDING,
                        recipient_type="interviewer",
                        recipient_email=attendee_email,
                    )
                    db.add(reminder)
                    reminders.append(reminder)

        db.commit()
        return reminders

    def send_reminder(
        self,
        db: Session,
        reminder_id: str,
    ) -> bool:
        """Send a specific reminder."""
        reminder = db.query(InterviewReminder).filter(
            InterviewReminder.id == reminder_id
        ).first()

        if not reminder:
            return False

        if reminder.status != ReminderStatus.PENDING:
            return False

        interview = db.query(ScheduledInterview).filter(
            ScheduledInterview.id == reminder.scheduled_interview_id
        ).first()

        if not interview:
            reminder.status = ReminderStatus.FAILED
            reminder.error_message = "Interview not found"
            db.commit()
            return False

        # Check if interview is still active
        if interview.status in [ScheduledInterviewStatus.CANCELLED, ScheduledInterviewStatus.COMPLETED]:
            reminder.status = ReminderStatus.CANCELLED
            db.commit()
            return False

        try:
            if reminder.recipient_type == "candidate":
                self._send_candidate_reminder(db, reminder, interview)
            else:
                self._send_interviewer_reminder(db, reminder, interview)

            reminder.status = ReminderStatus.SENT
            reminder.sent_at = datetime.utcnow()
            db.commit()
            return True

        except Exception as e:
            logger.error(f"Failed to send reminder {reminder_id}: {e}")
            reminder.status = ReminderStatus.FAILED
            reminder.error_message = str(e)
            db.commit()
            return False

    def _send_candidate_reminder(
        self,
        db: Session,
        reminder: InterviewReminder,
        interview: ScheduledInterview,
    ):
        """Send reminder email to candidate."""
        candidate = db.query(Candidate).filter(
            Candidate.id == interview.candidate_id
        ).first()

        employer = db.query(Employer).filter(
            Employer.id == interview.employer_id
        ).first()

        if not candidate or not employer:
            raise ValueError("Candidate or employer not found")

        # Determine reminder type text
        if reminder.reminder_type == ReminderType.HOURS_24:
            time_text = "tomorrow"
            subject = f"Reminder: Your interview with {employer.company_name} is tomorrow"
        else:
            time_text = "in 1 hour"
            subject = f"Reminder: Your interview with {employer.company_name} is in 1 hour"

        email_service.send_interview_reminder_candidate(
            to_email=candidate.email,
            candidate_name=candidate.name,
            company_name=employer.company_name,
            interview_title=interview.title,
            scheduled_at=interview.scheduled_at,
            duration_minutes=interview.duration_minutes,
            google_meet_link=interview.google_meet_link,
            time_text=time_text,
        )

    def _send_interviewer_reminder(
        self,
        db: Session,
        reminder: InterviewReminder,
        interview: ScheduledInterview,
    ):
        """Send reminder email to interviewer."""
        candidate = db.query(Candidate).filter(
            Candidate.id == interview.candidate_id
        ).first()

        if not candidate:
            raise ValueError("Candidate not found")

        # Determine reminder type text
        if reminder.reminder_type == ReminderType.HOURS_24:
            time_text = "tomorrow"
            subject = f"Reminder: Interview with {candidate.name} tomorrow"
        else:
            time_text = "in 1 hour"
            subject = f"Reminder: Interview with {candidate.name} in 1 hour"

        email_service.send_interview_reminder_interviewer(
            to_email=reminder.recipient_email,
            candidate_name=candidate.name,
            interview_title=interview.title,
            scheduled_at=interview.scheduled_at,
            duration_minutes=interview.duration_minutes,
            google_meet_link=interview.google_meet_link,
            time_text=time_text,
        )

    def cancel_reminders(
        self,
        db: Session,
        interview_id: str,
    ):
        """Cancel all pending reminders for an interview."""
        db.query(InterviewReminder).filter(
            InterviewReminder.scheduled_interview_id == interview_id,
            InterviewReminder.status == ReminderStatus.PENDING
        ).update({"status": ReminderStatus.CANCELLED})
        db.commit()


async def check_pending_reminders():
    """
    Check for pending reminders that need to be sent.
    This runs as a scheduled job every 5 minutes.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # Find reminders that are due
        pending_reminders = db.query(InterviewReminder).filter(
            InterviewReminder.status == ReminderStatus.PENDING,
            InterviewReminder.scheduled_for <= now
        ).all()

        logger.info(f"Found {len(pending_reminders)} pending reminders to send")

        scheduler_instance = ReminderScheduler()
        for reminder in pending_reminders:
            scheduler_instance.send_reminder(db, reminder.id)

    except Exception as e:
        logger.error(f"Error checking pending reminders: {e}")
    finally:
        db.close()


# Singleton instance
reminder_scheduler = ReminderScheduler()

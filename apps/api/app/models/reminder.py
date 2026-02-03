"""
InterviewReminder model for automated interview reminders.
Stores pending and sent reminders for scheduled interviews.
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..database import Base


class ReminderType(str, enum.Enum):
    """Types of interview reminders."""
    HOURS_24 = "24h"
    HOURS_1 = "1h"
    CUSTOM = "custom"


class ReminderStatus(str, enum.Enum):
    """Status of a reminder."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InterviewReminder(Base):
    """
    Represents a scheduled reminder for an interview.
    Created when interviews are scheduled, sent automatically by the reminder scheduler.
    """
    __tablename__ = "interview_reminders"

    id = Column(String, primary_key=True)

    # Link to the scheduled interview
    scheduled_interview_id = Column(
        String,
        ForeignKey("scheduled_interviews.id", ondelete="CASCADE"),
        nullable=False
    )

    # Reminder configuration
    reminder_type = Column(Enum(ReminderType), nullable=False)

    # When the reminder should be sent
    scheduled_for = Column(DateTime(timezone=True), nullable=False)

    # Current status
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING)

    # When it was actually sent (if sent)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Error message if sending failed
    error_message = Column(Text, nullable=True)

    # Recipient type (candidate or interviewer)
    recipient_type = Column(String, default="candidate")  # "candidate" or "interviewer"
    recipient_email = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    scheduled_interview = relationship("ScheduledInterview", backref="reminders")

    # Indexes for efficient reminder processing
    __table_args__ = (
        Index("ix_reminders_scheduled_interview", "scheduled_interview_id"),
        Index("ix_reminders_pending", "status", "scheduled_for"),
        Index("ix_reminders_scheduled_for", "scheduled_for"),
    )

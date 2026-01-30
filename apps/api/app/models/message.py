"""Message model for employer-candidate communication."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class MessageType(str, enum.Enum):
    INTERVIEW_REQUEST = "INTERVIEW_REQUEST"
    REJECTION = "REJECTION"
    SHORTLIST_NOTICE = "SHORTLIST_NOTICE"
    CUSTOM = "CUSTOM"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.CUSTOM)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

    employer_id = Column(String, ForeignKey("employers.id", ondelete="CASCADE"), nullable=False)
    employer = relationship("Employer", back_populates="messages")

    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    candidate = relationship("Candidate", back_populates="messages")

    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    job = relationship("Job", back_populates="messages")

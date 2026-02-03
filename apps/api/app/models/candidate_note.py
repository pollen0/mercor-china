"""
Candidate notes model for employer private notes on candidates.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class CandidateNote(Base):
    """Private notes that employers can add on candidates."""
    __tablename__ = "candidate_notes"

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    employer_id = Column(String(32), ForeignKey("employers.id"), nullable=False, index=True)
    candidate_id = Column(String(32), ForeignKey("candidates.id"), nullable=False, index=True)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    employer = relationship("Employer", backref="candidate_notes")
    candidate = relationship("Candidate", backref="employer_notes")

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class ReferralStatus(str, enum.Enum):
    """Status of a referral."""
    PENDING = "pending"  # Link shared but referee hasn't signed up
    REGISTERED = "registered"  # Referee created an account
    ONBOARDED = "onboarded"  # Referee completed profile (resume + one more item)
    INTERVIEWED = "interviewed"  # Referee completed first interview


class Referral(Base):
    """
    Tracks candidate-to-candidate referrals.
    Each candidate gets a unique referral_code on their Candidate record.
    When a new user signs up with that code, a Referral row is created.
    """
    __tablename__ = "referrals"

    id = Column(String, primary_key=True)
    referrer_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    referee_id = Column(String, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)
    referee_email = Column(String, nullable=True)  # Email the invite was sent to (before signup)
    status = Column(String, default=ReferralStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    converted_at = Column(DateTime(timezone=True), nullable=True)  # When referee hit target status

    # Relationships
    referrer = relationship("Candidate", foreign_keys=[referrer_id], backref="referrals_made")
    referee = relationship("Candidate", foreign_keys=[referee_id], backref="referred_by_entry")

    __table_args__ = (
        Index('ix_referrals_referrer_id', 'referrer_id'),
        Index('ix_referrals_referee_id', 'referee_id'),
        Index('ix_referrals_status', 'status'),
    )

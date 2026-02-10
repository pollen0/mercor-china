"""
Marketing/External Referrer model for tracking referrals from non-users.
Used for marketing interns, campus ambassadors, etc. who don't have accounts.
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base


class MarketingReferrer(Base):
    """
    External referrers who don't have platform accounts.
    Each gets a unique referral code to track their signups.
    """
    __tablename__ = "marketing_referrers"

    id = Column(String, primary_key=True)  # mr_{uuid}
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)  # Optional - for contact purposes
    role = Column(String, nullable=True)  # e.g., "Marketing Intern", "Campus Ambassador"
    referral_code = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String, nullable=True)  # Admin notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

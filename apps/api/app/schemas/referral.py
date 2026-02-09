from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReferralCodeResponse(BaseModel):
    """Response with the candidate's referral code and link."""
    referral_code: str
    referral_link: str


class ReferralStatsResponse(BaseModel):
    """Aggregated referral stats for a candidate."""
    referral_code: str
    referral_link: str
    total_referrals: int
    registered: int
    onboarded: int
    interviewed: int


class ReferralEntry(BaseModel):
    """A single referral in the list."""
    id: str
    referee_name: Optional[str] = None
    referee_email: Optional[str] = None
    status: str
    created_at: datetime
    converted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferralListResponse(BaseModel):
    """List of referrals for a candidate."""
    referrals: list[ReferralEntry]
    total: int

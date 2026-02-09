import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.candidate import Candidate
from ..schemas.referral import (
    ReferralCodeResponse,
    ReferralStatsResponse,
    ReferralEntry,
    ReferralListResponse,
)
from ..services.referral import get_or_create_referral_code, get_referral_stats, get_referral_list
from ..utils.auth import get_current_candidate
from ..config import settings

logger = logging.getLogger("pathway.referrals")
router = APIRouter()


@router.get("/me/code", response_model=ReferralCodeResponse)
async def get_my_referral_code(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Get or generate the current candidate's referral code and shareable link."""
    code = get_or_create_referral_code(candidate, db)
    frontend_url = settings.frontend_url.rstrip("/")
    return ReferralCodeResponse(
        referral_code=code,
        referral_link=f"{frontend_url}/register?ref={code}",
    )


@router.get("/me/stats", response_model=ReferralStatsResponse)
async def get_my_referral_stats(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Get referral statistics for the current candidate."""
    code = get_or_create_referral_code(candidate, db)
    stats = get_referral_stats(candidate.id, db)
    frontend_url = settings.frontend_url.rstrip("/")
    return ReferralStatsResponse(
        referral_code=code,
        referral_link=f"{frontend_url}/register?ref={code}",
        **stats,
    )


@router.get("/me/list", response_model=ReferralListResponse)
async def get_my_referrals(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Get the list of all referrals made by the current candidate."""
    referrals = get_referral_list(candidate.id, db)
    entries = []
    for r in referrals:
        referee_name = None
        referee_email = r.referee_email
        if r.referee:
            referee_name = r.referee.name
            referee_email = r.referee.email
        entries.append(ReferralEntry(
            id=r.id,
            referee_name=referee_name,
            referee_email=referee_email,
            status=r.status,
            created_at=r.created_at,
            converted_at=r.converted_at,
        ))
    return ReferralListResponse(referrals=entries, total=len(entries))

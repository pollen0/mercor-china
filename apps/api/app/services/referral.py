import logging
import uuid
import secrets
import string
from sqlalchemy.orm import Session
from ..models.candidate import Candidate
from ..models.referral import Referral, ReferralStatus

logger = logging.getLogger("pathway.referral")


def generate_referral_code() -> str:
    """Generate a unique referral code like PATHWAY-A3X7K9."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(chars) for _ in range(6))
    return f"PATHWAY-{suffix}"


def get_or_create_referral_code(candidate: Candidate, db: Session) -> str:
    """Get existing referral code or create one for the candidate."""
    if candidate.referral_code:
        return candidate.referral_code

    # Generate a unique code
    for _ in range(10):
        code = generate_referral_code()
        existing = db.query(Candidate).filter(Candidate.referral_code == code).first()
        if not existing:
            candidate.referral_code = code
            db.commit()
            db.refresh(candidate)
            return code

    raise RuntimeError("Failed to generate unique referral code")


def find_referrer_by_code(referral_code: str, db: Session) -> Candidate | None:
    """Look up the candidate who owns a referral code."""
    return db.query(Candidate).filter(Candidate.referral_code == referral_code).first()


def create_referral_on_signup(
    referrer: Candidate,
    referee: Candidate,
    db: Session,
) -> Referral:
    """Create a referral record when a new user signs up with a referral code."""
    referral = Referral(
        id=f"r{uuid.uuid4().hex[:24]}",
        referrer_id=referrer.id,
        referee_id=referee.id,
        referee_email=referee.email,
        status=ReferralStatus.REGISTERED,
    )
    db.add(referral)

    # Link the referee back to the referrer
    referee.referred_by_id = referrer.id
    db.commit()
    db.refresh(referral)
    return referral


def update_referral_status(
    referee_id: str,
    new_status: ReferralStatus,
    db: Session,
) -> Referral | None:
    """Update the referral status when the referee progresses (onboarded, interviewed)."""
    referral = db.query(Referral).filter(Referral.referee_id == referee_id).first()
    if not referral:
        return None

    # Only advance status, never go backwards
    status_order = [
        ReferralStatus.PENDING,
        ReferralStatus.REGISTERED,
        ReferralStatus.ONBOARDED,
        ReferralStatus.INTERVIEWED,
    ]
    current_idx = status_order.index(referral.status) if referral.status in status_order else 0
    new_idx = status_order.index(new_status) if new_status in status_order else 0

    if new_idx > current_idx:
        referral.status = new_status
        if new_status in (ReferralStatus.ONBOARDED, ReferralStatus.INTERVIEWED):
            from datetime import datetime, timezone
            referral.converted_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(referral)

    return referral


def get_referral_stats(candidate_id: str, db: Session) -> dict:
    """Get referral stats for a candidate."""
    referrals = db.query(Referral).filter(Referral.referrer_id == candidate_id).all()
    return {
        "total_referrals": len(referrals),
        "registered": sum(1 for r in referrals if r.status == ReferralStatus.REGISTERED),
        "onboarded": sum(1 for r in referrals if r.status == ReferralStatus.ONBOARDED),
        "interviewed": sum(1 for r in referrals if r.status == ReferralStatus.INTERVIEWED),
    }


def get_referral_list(candidate_id: str, db: Session) -> list[Referral]:
    """Get all referrals made by a candidate."""
    return (
        db.query(Referral)
        .filter(Referral.referrer_id == candidate_id)
        .order_by(Referral.created_at.desc())
        .all()
    )

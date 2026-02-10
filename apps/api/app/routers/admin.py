"""
Admin panel endpoints for system management.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel

from ..database import get_db
from ..models import (
    Candidate,
    Employer,
    Job,
    InterviewSession,
    InterviewStatus,
    Match,
    MatchStatus,
    MarketingReferrer,
)
from ..models.candidate import CandidateVerticalProfile
from ..models.referral import Referral
from ..utils.auth import get_current_employer
from ..config import settings

logger = logging.getLogger("pathway.admin")
router = APIRouter()


def generate_cuid(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:24]}" if prefix else uuid.uuid4().hex[:24]


# Admin password from environment variable


# Schemas
class AdminStats(BaseModel):
    total_candidates: int
    verified_candidates: int
    total_employers: int
    verified_employers: int
    total_jobs: int
    active_jobs: int
    total_interviews: int
    completed_interviews: int
    total_matches: int
    hired_count: int
    # Recent activity
    new_candidates_7d: int
    new_employers_7d: int
    new_interviews_7d: int


class CandidateAdmin(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    email_verified: bool = False
    interview_count: int = 0
    vertical_profile_count: int = 0
    has_resume: bool = False
    has_github: bool = False
    has_transcript: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class NudgeType(str):
    RESUME = "resume"
    GITHUB = "github"
    TRANSCRIPT = "transcript"


class NudgeRequest(BaseModel):
    nudge_type: str  # "resume", "github", or "transcript"


class EmployerAdmin(BaseModel):
    id: str
    company_name: str
    email: str
    is_verified: bool
    job_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class InterviewAdmin(BaseModel):
    id: str
    candidate_name: str
    candidate_email: str
    job_title: Optional[str]
    company_name: Optional[str]
    status: str
    total_score: Optional[float]
    is_practice: bool
    is_vertical_interview: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCandidateList(BaseModel):
    users: List[CandidateAdmin]
    total: int


class AdminEmployerList(BaseModel):
    users: List[EmployerAdmin]
    total: int


class AdminInterviewList(BaseModel):
    interviews: List[InterviewAdmin]
    total: int


# Helper to check admin access
def verify_admin(
    x_admin_password: str = Header(None, alias="X-Admin-Password"),
):
    """Verify admin access via password only - no employer login required."""
    if not settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin access not configured. Set ADMIN_PASSWORD environment variable."
        )
    if x_admin_password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Invalid or missing admin password."
        )
    return True


# Endpoints
@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get system-wide statistics."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    # Candidate stats
    total_candidates = db.query(func.count(Candidate.id)).scalar()
    verified_candidates = db.query(func.count(Candidate.id)).filter(
        Candidate.email_verified == True
    ).scalar()
    new_candidates_7d = db.query(func.count(Candidate.id)).filter(
        Candidate.created_at >= week_ago
    ).scalar()

    # Employer stats
    total_employers = db.query(func.count(Employer.id)).scalar()
    verified_employers = db.query(func.count(Employer.id)).filter(
        Employer.is_verified == True
    ).scalar()
    new_employers_7d = db.query(func.count(Employer.id)).filter(
        Employer.created_at >= week_ago
    ).scalar()

    # Job stats
    total_jobs = db.query(func.count(Job.id)).scalar()
    active_jobs = db.query(func.count(Job.id)).filter(Job.is_active == True).scalar()

    # Interview stats
    total_interviews = db.query(func.count(InterviewSession.id)).scalar()
    completed_interviews = db.query(func.count(InterviewSession.id)).filter(
        InterviewSession.status == InterviewStatus.COMPLETED
    ).scalar()
    new_interviews_7d = db.query(func.count(InterviewSession.id)).filter(
        InterviewSession.created_at >= week_ago
    ).scalar()

    # Match stats
    total_matches = db.query(func.count(Match.id)).scalar()
    hired_count = db.query(func.count(Match.id)).filter(
        Match.status == MatchStatus.HIRED
    ).scalar()

    return AdminStats(
        total_candidates=total_candidates or 0,
        verified_candidates=verified_candidates or 0,
        total_employers=total_employers or 0,
        verified_employers=verified_employers or 0,
        total_jobs=total_jobs or 0,
        active_jobs=active_jobs or 0,
        total_interviews=total_interviews or 0,
        completed_interviews=completed_interviews or 0,
        total_matches=total_matches or 0,
        hired_count=hired_count or 0,
        new_candidates_7d=new_candidates_7d or 0,
        new_employers_7d=new_employers_7d or 0,
        new_interviews_7d=new_interviews_7d or 0,
    )


@router.get("/candidates", response_model=AdminCandidateList)
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    verified_only: bool = False,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all candidates with admin details."""
    query = db.query(Candidate)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_term)) |
            (Candidate.email.ilike(search_term)) |
            (Candidate.phone.ilike(search_term))
        )

    if verified_only:
        query = query.filter(Candidate.email_verified == True)

    total = query.count()
    candidates = query.order_by(desc(Candidate.created_at)).offset(skip).limit(limit).all()

    result = []
    for c in candidates:
        interview_count = db.query(func.count(InterviewSession.id)).filter(
            InterviewSession.candidate_id == c.id
        ).scalar()
        profile_count = db.query(func.count(CandidateVerticalProfile.id)).filter(
            CandidateVerticalProfile.candidate_id == c.id
        ).scalar()

        result.append(CandidateAdmin(
            id=c.id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            email_verified=c.email_verified or False,
            interview_count=interview_count or 0,
            vertical_profile_count=profile_count or 0,
            has_resume=c.resume_url is not None,
            has_github=c.github_username is not None,
            has_transcript=c.transcript_key is not None,
            created_at=c.created_at,
        ))

    return AdminCandidateList(users=result, total=total)


@router.post("/candidates/{candidate_id}/nudge")
async def send_nudge_email(
    candidate_id: str,
    request: NudgeRequest,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Send a nudge email to a candidate to complete their profile."""
    from ..services.email import email_service

    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    nudge_type = request.nudge_type.lower()
    if nudge_type not in ["resume", "github", "transcript"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid nudge type. Must be 'resume', 'github', or 'transcript'"
        )

    # Check if they already have the requested item
    if nudge_type == "resume" and candidate.resume_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate already has a resume uploaded"
        )
    if nudge_type == "github" and candidate.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate already has GitHub connected"
        )
    if nudge_type == "transcript" and candidate.transcript_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate already has a transcript uploaded"
        )

    # Send nudge email
    email_id = email_service.send_profile_nudge(
        to=candidate.email,
        candidate_name=candidate.name,
        nudge_type=nudge_type,
    )

    if email_id:
        logger.info(f"Sent {nudge_type} nudge email to {candidate.email}")
        return {"success": True, "message": f"Nudge email sent to {candidate.email}"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )


@router.get("/employers", response_model=AdminEmployerList)
async def list_employers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    verified_only: bool = False,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all employers with admin details."""
    query = db.query(Employer)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Employer.company_name.ilike(search_term)) |
            (Employer.email.ilike(search_term))
        )

    if verified_only:
        query = query.filter(Employer.is_verified == True)

    total = query.count()
    employers = query.order_by(desc(Employer.created_at)).offset(skip).limit(limit).all()

    result = []
    for e in employers:
        job_count = db.query(func.count(Job.id)).filter(Job.employer_id == e.id).scalar()

        result.append(EmployerAdmin(
            id=e.id,
            company_name=e.company_name,
            email=e.email,
            is_verified=e.is_verified,
            job_count=job_count or 0,
            created_at=e.created_at,
        ))

    return AdminEmployerList(users=result, total=total)


@router.get("/interviews", response_model=AdminInterviewList)
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all interviews with admin details."""
    query = db.query(InterviewSession)

    if status_filter:
        try:
            status_enum = InterviewStatus(status_filter)
            query = query.filter(InterviewSession.status == status_enum)
        except ValueError:
            pass

    total = query.count()
    interviews = query.order_by(desc(InterviewSession.created_at)).offset(skip).limit(limit).all()

    result = []
    for i in interviews:
        candidate = i.candidate
        job = i.job

        result.append(InterviewAdmin(
            id=i.id,
            candidate_name=candidate.name if candidate else "Unknown",
            candidate_email=candidate.email if candidate else "Unknown",
            job_title=job.title if job else None,
            company_name=job.employer.company_name if job and job.employer else None,
            status=i.status.value if i.status else "UNKNOWN",
            total_score=i.total_score,
            is_practice=i.is_practice or False,
            is_vertical_interview=i.is_vertical_interview or False,
            created_at=i.created_at,
        ))

    return AdminInterviewList(interviews=result, total=total)


@router.patch("/candidates/{candidate_id}/verify")
async def toggle_candidate_verification(
    candidate_id: str,
    verified: bool,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Toggle candidate email verification status."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    candidate.email_verified = verified
    db.commit()

    return {"success": True, "verified": verified}


@router.patch("/employers/{employer_id}/verify")
async def toggle_employer_verification(
    employer_id: str,
    verified: bool,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Toggle employer verification status."""
    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    employer.is_verified = verified
    db.commit()

    return {"success": True, "verified": verified}


@router.delete("/candidates/{candidate_id}")
async def delete_candidate(
    candidate_id: str,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Delete a candidate account."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    db.delete(candidate)
    db.commit()

    logger.info(f"Admin {admin.email} deleted candidate {candidate_id}")
    return {"success": True, "deleted_id": candidate_id}


@router.delete("/employers/{employer_id}")
async def delete_employer(
    employer_id: str,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Delete an employer account."""
    if employer_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")

    db.delete(employer)
    db.commit()

    logger.info(f"Admin {admin.email} deleted employer {employer_id}")
    return {"success": True, "deleted_id": employer_id}


# ============================================================================
# PROFILE LINK GENERATION (GTM)
# ============================================================================

@router.post("/generate-batch-links")
async def generate_batch_profile_links(
    data: dict,
    admin: Employer = Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """
    Generate shareable profile links for multiple candidates at once.
    Used for GTM: Admin curates top candidates, generates links, sends to companies.

    Request body:
    {
      "candidate_ids": ["c1", "c2", "c3"],
      "expires_in_days": 7  // optional, defaults to 7
    }

    Returns array of links for all candidates.
    """
    from ..models.profile_token import ProfileToken
    from datetime import timedelta
    import secrets

    candidate_ids = data.get("candidate_ids", [])
    expires_in_days = data.get("expires_in_days", 7)

    if not candidate_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="candidate_ids is required"
        )

    if len(candidate_ids) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate more than 50 links at once"
        )

    # Verify all candidates exist and opted in
    candidates = db.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
    found_ids = {c.id for c in candidates}
    missing_ids = [cid for cid in candidate_ids if cid not in found_ids]

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidates not found: {', '.join(missing_ids)}"
        )

    # Check which candidates haven't opted in
    not_opted_in = [c.name for c in candidates if not c.opted_in_to_sharing]
    if not_opted_in:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"These candidates haven't opted in to sharing: {', '.join(not_opted_in)}"
        )

    # Generate tokens for all candidates
    results = []
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    for candidate in candidates:
        token = secrets.token_urlsafe(32)

        profile_token = ProfileToken(
            id=generate_cuid("pt"),
            token=token,
            candidate_id=candidate.id,
            created_by_id=admin.id,
            created_by_type="admin",
            expires_at=expires_at,
        )

        db.add(profile_token)

        results.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "token": token,
            "share_url": f"/talent/{candidate.id}?token={token}",
            "expires_at": expires_at.isoformat(),
        })

    db.commit()

    logger.info(f"Admin {admin.email} generated {len(results)} batch profile links")

    return {
        "success": True,
        "count": len(results),
        "expires_in_days": expires_in_days,
        "links": results,
    }


# ============= Referral Admin Endpoints =============

@router.get("/referrals")
async def get_admin_referrals(
    status_filter: Optional[str] = None,
    limit: int = Query(200, le=500),
    offset: int = 0,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get all referrals with referrer/referee details."""
    query = db.query(Referral)
    if status_filter:
        query = query.filter(Referral.status == status_filter)

    total = query.count()
    referrals = query.order_by(Referral.created_at.desc()).offset(offset).limit(limit).all()

    result = []
    for ref in referrals:
        referrer = db.query(Candidate).filter(Candidate.id == ref.referrer_id).first()
        referee = db.query(Candidate).filter(Candidate.id == ref.referee_id).first() if ref.referee_id else None

        result.append({
            "id": ref.id,
            "referrer_id": ref.referrer_id,
            "referrer_name": referrer.name if referrer else "Unknown",
            "referrer_email": referrer.email if referrer else "",
            "referee_id": ref.referee_id,
            "referee_name": referee.name if referee else ref.referee_email or "Pending",
            "referee_email": referee.email if referee else ref.referee_email or "",
            "status": ref.status,
            "created_at": ref.created_at.isoformat() if ref.created_at else None,
            "converted_at": ref.converted_at.isoformat() if ref.converted_at else None,
        })

    return {"referrals": result, "total": total}


@router.get("/referrals/leaderboard")
async def get_referral_leaderboard(
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get referral leaderboard — top referrers sorted by total referrals."""
    # Get all candidates who have made at least one referral
    referrer_stats = (
        db.query(
            Referral.referrer_id,
            func.count(Referral.id).label("total"),
            func.count(func.nullif(Referral.status != "registered", True)).label("registered"),
            func.count(func.nullif(Referral.status != "onboarded", True)).label("onboarded"),
            func.count(func.nullif(Referral.status != "interviewed", True)).label("interviewed"),
        )
        .group_by(Referral.referrer_id)
        .order_by(desc("total"))
        .all()
    )

    leaderboard = []
    for row in referrer_stats:
        candidate = db.query(Candidate).filter(Candidate.id == row.referrer_id).first()
        if candidate:
            leaderboard.append({
                "referrer_id": candidate.id,
                "referrer_name": candidate.name,
                "referrer_email": candidate.email,
                "referral_code": candidate.referral_code,
                "total_referrals": row.total,
                "registered": row.registered,
                "onboarded": row.onboarded,
                "interviewed": row.interviewed,
            })

    return {"leaderboard": leaderboard, "total_referrers": len(leaderboard)}


@router.get("/referrals/stats")
async def get_referral_stats(
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get overall referral program statistics."""
    total = db.query(Referral).count()
    pending = db.query(Referral).filter(Referral.status == "pending").count()
    registered = db.query(Referral).filter(Referral.status == "registered").count()
    onboarded = db.query(Referral).filter(Referral.status == "onboarded").count()
    interviewed = db.query(Referral).filter(Referral.status == "interviewed").count()
    unique_referrers = db.query(func.count(func.distinct(Referral.referrer_id))).scalar() or 0

    return {
        "total_referrals": total,
        "pending": pending,
        "registered": registered,
        "onboarded": onboarded,
        "interviewed": interviewed,
        "unique_referrers": unique_referrers,
        "conversion_rate": round(interviewed / total * 100, 1) if total > 0 else 0,
    }


# ============= Marketing Referrer Endpoints =============

class MarketingReferrerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    notes: Optional[str] = None


class MarketingReferrerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class MarketingReferrerResponse(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    referral_code: str
    referral_link: str
    is_active: bool
    notes: Optional[str] = None
    total_signups: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


def generate_marketing_referral_code(name: str) -> str:
    """Generate a unique referral code for a marketing referrer."""
    import secrets
    # Create a short name prefix (first 3 letters, uppercase)
    name_prefix = ''.join(c for c in name.upper() if c.isalpha())[:3]
    if len(name_prefix) < 3:
        name_prefix = name_prefix.ljust(3, 'X')
    # Add random suffix
    random_suffix = secrets.token_hex(3).upper()
    return f"MKT-{name_prefix}-{random_suffix}"


@router.post("/marketing-referrers", response_model=MarketingReferrerResponse)
async def create_marketing_referrer(
    data: MarketingReferrerCreate,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Create a new marketing referrer (non-user with referral tracking)."""
    from ..config import settings

    # Generate unique referral code
    referral_code = generate_marketing_referral_code(data.name)

    # Ensure uniqueness (retry if collision)
    while db.query(MarketingReferrer).filter(MarketingReferrer.referral_code == referral_code).first():
        referral_code = generate_marketing_referral_code(data.name)

    referrer = MarketingReferrer(
        id=generate_cuid("mr_"),
        name=data.name,
        email=data.email,
        role=data.role,
        notes=data.notes,
        referral_code=referral_code,
        is_active=True,
    )

    db.add(referrer)
    db.commit()
    db.refresh(referrer)

    logger.info(f"Created marketing referrer: {referrer.name} ({referral_code})")

    frontend_url = getattr(settings, 'frontend_url', 'https://pathway.careers')
    referral_link = f"{frontend_url}/register?ref={referral_code}"

    return MarketingReferrerResponse(
        id=referrer.id,
        name=referrer.name,
        email=referrer.email,
        role=referrer.role,
        referral_code=referrer.referral_code,
        referral_link=referral_link,
        is_active=referrer.is_active,
        notes=referrer.notes,
        total_signups=0,
        created_at=referrer.created_at,
    )


@router.get("/marketing-referrers")
async def list_marketing_referrers(
    include_inactive: bool = False,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """List all marketing referrers with their signup stats."""
    from ..config import settings

    query = db.query(MarketingReferrer)
    if not include_inactive:
        query = query.filter(MarketingReferrer.is_active == True)

    referrers = query.order_by(MarketingReferrer.created_at.desc()).all()

    frontend_url = getattr(settings, 'frontend_url', 'https://pathway.careers')

    result = []
    for ref in referrers:
        # Count signups attributed to this referrer
        signup_count = db.query(func.count(Candidate.id)).filter(
            Candidate.marketing_referrer_id == ref.id
        ).scalar() or 0

        result.append({
            "id": ref.id,
            "name": ref.name,
            "email": ref.email,
            "role": ref.role,
            "referral_code": ref.referral_code,
            "referral_link": f"{frontend_url}/register?ref={ref.referral_code}",
            "is_active": ref.is_active,
            "notes": ref.notes,
            "total_signups": signup_count,
            "created_at": ref.created_at.isoformat() if ref.created_at else None,
        })

    return {"marketing_referrers": result, "total": len(result)}


@router.get("/marketing-referrers/{referrer_id}")
async def get_marketing_referrer(
    referrer_id: str,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Get details of a specific marketing referrer including their referred candidates."""
    from ..config import settings

    referrer = db.query(MarketingReferrer).filter(MarketingReferrer.id == referrer_id).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Marketing referrer not found")

    # Get all candidates referred by this referrer
    referred_candidates = db.query(Candidate).filter(
        Candidate.marketing_referrer_id == referrer_id
    ).order_by(Candidate.created_at.desc()).all()

    frontend_url = getattr(settings, 'frontend_url', 'https://pathway.careers')

    candidates_data = []
    for c in referred_candidates:
        # Check profile completion
        has_resume = c.resume_url is not None
        has_github = c.github_username is not None
        has_transcript = c.transcript_key is not None
        has_interview = db.query(InterviewSession).filter(
            InterviewSession.candidate_id == c.id,
            InterviewSession.status == InterviewStatus.COMPLETED
        ).first() is not None

        candidates_data.append({
            "id": c.id,
            "name": c.name,
            "email": c.email,
            "has_resume": has_resume,
            "has_github": has_github,
            "has_transcript": has_transcript,
            "has_completed_interview": has_interview,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "referrer": {
            "id": referrer.id,
            "name": referrer.name,
            "email": referrer.email,
            "role": referrer.role,
            "referral_code": referrer.referral_code,
            "referral_link": f"{frontend_url}/register?ref={referrer.referral_code}",
            "is_active": referrer.is_active,
            "notes": referrer.notes,
            "created_at": referrer.created_at.isoformat() if referrer.created_at else None,
        },
        "referred_candidates": candidates_data,
        "total_signups": len(candidates_data),
    }


@router.patch("/marketing-referrers/{referrer_id}")
async def update_marketing_referrer(
    referrer_id: str,
    data: MarketingReferrerUpdate,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Update a marketing referrer (name, email, role, notes, or deactivate)."""
    referrer = db.query(MarketingReferrer).filter(MarketingReferrer.id == referrer_id).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Marketing referrer not found")

    if data.name is not None:
        referrer.name = data.name
    if data.email is not None:
        referrer.email = data.email
    if data.role is not None:
        referrer.role = data.role
    if data.notes is not None:
        referrer.notes = data.notes
    if data.is_active is not None:
        referrer.is_active = data.is_active

    db.commit()
    db.refresh(referrer)

    logger.info(f"Updated marketing referrer: {referrer.id}")

    return {"success": True, "referrer_id": referrer.id}


@router.delete("/marketing-referrers/{referrer_id}")
async def delete_marketing_referrer(
    referrer_id: str,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db),
):
    """Delete a marketing referrer (only if they have no referrals)."""
    referrer = db.query(MarketingReferrer).filter(MarketingReferrer.id == referrer_id).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Marketing referrer not found")

    # Check if there are any referrals
    referral_count = db.query(func.count(Candidate.id)).filter(
        Candidate.marketing_referrer_id == referrer_id
    ).scalar() or 0

    if referral_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete referrer with {referral_count} referrals. Deactivate instead."
        )

    db.delete(referrer)
    db.commit()

    logger.info(f"Deleted marketing referrer: {referrer_id}")

    return {"success": True, "deleted_id": referrer_id}

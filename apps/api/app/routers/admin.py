"""
Admin panel endpoints for system management.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
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
)
from ..models.candidate import CandidateVerticalProfile
from ..utils.auth import get_current_employer
from ..config import settings

logger = logging.getLogger("zhimian.admin")
router = APIRouter()

# Admin emails - in production, move this to database or env var
ADMIN_EMAILS = [
    "paul@getpasal.com",
    "admin@zhimian.ai",
]


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
    phone: str
    email_verified: bool
    interview_count: int
    vertical_profile_count: int
    created_at: datetime

    class Config:
        from_attributes = True


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


class AdminUserList(BaseModel):
    users: List[CandidateAdmin] | List[EmployerAdmin]
    total: int


class AdminInterviewList(BaseModel):
    interviews: List[InterviewAdmin]
    total: int


# Helper to check admin access
def verify_admin(employer: Employer = Depends(get_current_employer)):
    """Verify that the current user is an admin."""
    if employer.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return employer


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


@router.get("/candidates", response_model=AdminUserList)
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
            created_at=c.created_at,
        ))

    return AdminUserList(users=result, total=total)


@router.get("/employers", response_model=AdminUserList)
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

    return AdminUserList(users=result, total=total)


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

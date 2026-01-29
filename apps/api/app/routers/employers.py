from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import Optional
import uuid
import json

from ..database import get_db
from ..models import Employer, Job, InterviewSession, InterviewStatus, MatchStatus, Match, InviteToken, Vertical, RoleType
from ..schemas.employer import (
    EmployerRegister,
    EmployerLogin,
    EmployerResponse,
    EmployerWithToken,
    JobCreate,
    JobUpdate,
    JobResponse,
    JobList,
    DashboardStats,
)
from ..schemas.interview import (
    InterviewSessionResponse,
    InterviewListResponse,
    InterviewStatusUpdate,
    ResponseDetail,
    ScoreDetails,
    InviteTokenCreate,
    InviteTokenResponse,
    InviteTokenList,
)
from datetime import datetime, timedelta
import secrets
from ..utils.auth import create_access_token, verify_token, get_password_hash, verify_password
from ..services.storage import storage_service

router = APIRouter()


def generate_cuid(prefix: str = "e") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


async def get_current_employer(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Employer:
    """Dependency to get the current authenticated employer."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证方案",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer_id = payload.get("sub")
    if not employer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌内容",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="雇主不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return employer


@router.post("/register", response_model=EmployerWithToken, status_code=status.HTTP_201_CREATED)
async def register_employer(
    data: EmployerRegister,
    db: Session = Depends(get_db)
):
    """Register a new employer account."""
    # Check if email exists
    existing = db.query(Employer).filter(Employer.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    employer = Employer(
        id=generate_cuid("e"),
        company_name=data.company_name,
        email=data.email,
        password=get_password_hash(data.password),
        is_verified=False,
    )

    try:
        db.add(employer)
        db.commit()
        db.refresh(employer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    token = create_access_token({"sub": employer.id, "type": "employer"})

    return EmployerWithToken(
        employer=EmployerResponse.model_validate(employer),
        token=token,
    )


@router.post("/login", response_model=EmployerWithToken)
async def login_employer(
    data: EmployerLogin,
    db: Session = Depends(get_db)
):
    """Login as an employer."""
    employer = db.query(Employer).filter(Employer.email == data.email).first()

    if not employer or not verify_password(data.password, employer.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    token = create_access_token({"sub": employer.id, "type": "employer"})

    return EmployerWithToken(
        employer=EmployerResponse.model_validate(employer),
        token=token,
    )


@router.get("/me", response_model=EmployerResponse)
async def get_current_employer_profile(
    employer: Employer = Depends(get_current_employer)
):
    """Get the current employer's profile."""
    return employer


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the employer."""
    # Get all job IDs for this employer
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        return DashboardStats(
            total_interviews=0,
            pending_review=0,
            shortlisted=0,
            rejected=0,
            average_score=None,
        )

    # Count interviews by status
    total = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids)
    ).count()

    # Pending review = completed interviews that haven't been shortlisted or rejected
    completed_session_ids = db.query(InterviewSession.id).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.status == InterviewStatus.COMPLETED
    ).subquery()

    reviewed_session_ids = db.query(Match.candidate_id, Match.job_id).filter(
        Match.job_id.in_(job_ids),
        Match.status.in_([MatchStatus.SHORTLISTED, MatchStatus.REJECTED])
    ).subquery()

    # Count completed interviews minus reviewed ones
    total_completed = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.status == InterviewStatus.COMPLETED
    ).count()

    total_reviewed = db.query(Match).filter(
        Match.job_id.in_(job_ids),
        Match.status.in_([MatchStatus.SHORTLISTED, MatchStatus.REJECTED])
    ).count()

    pending = max(0, total_completed - total_reviewed)

    # Count matches by status
    shortlisted = db.query(Match).filter(
        Match.job_id.in_(job_ids),
        Match.status == MatchStatus.SHORTLISTED
    ).count()

    rejected = db.query(Match).filter(
        Match.job_id.in_(job_ids),
        Match.status == MatchStatus.REJECTED
    ).count()

    # Calculate average score
    avg_score = db.query(func.avg(InterviewSession.total_score)).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.total_score.isnot(None)
    ).scalar()

    return DashboardStats(
        total_interviews=total,
        pending_review=pending,
        shortlisted=shortlisted,
        rejected=rejected,
        average_score=round(avg_score, 2) if avg_score else None,
    )


# Job management
@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Create a new job posting."""
    # Parse vertical and role_type enums if provided
    vertical = None
    role_type = None

    if data.vertical:
        try:
            vertical = Vertical(data.vertical)
        except ValueError:
            pass  # Invalid vertical, leave as None

    if data.role_type:
        try:
            role_type = RoleType(data.role_type)
        except ValueError:
            pass  # Invalid role_type, leave as None

    job = Job(
        id=generate_cuid("j"),
        title=data.title,
        description=data.description,
        vertical=vertical,
        role_type=role_type,
        requirements=data.requirements,
        location=data.location,
        salary_min=data.salary_min,
        salary_max=data.salary_max,
        employer_id=employer.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("/jobs", response_model=JobList)
async def list_jobs(
    is_active: Optional[bool] = None,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List all jobs for the current employer."""
    query = db.query(Job).filter(Job.employer_id == employer.id)

    if is_active is not None:
        query = query.filter(Job.is_active == is_active)

    jobs = query.order_by(Job.created_at.desc()).all()

    return JobList(jobs=jobs, total=len(jobs))


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get a specific job."""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    return job


@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    data: JobUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update a job posting."""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete a job posting."""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    db.delete(job)
    db.commit()


# Interview management
@router.get("/interviews", response_model=InterviewListResponse)
async def list_interviews(
    skip: int = 0,
    limit: int = 20,
    job_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    min_score: Optional[float] = None,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List all interviews for the employer's jobs."""
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        return InterviewListResponse(interviews=[], total=0)

    query = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids)
    )

    if job_id:
        query = query.filter(InterviewSession.job_id == job_id)

    if status_filter:
        try:
            status_enum = InterviewStatus(status_filter)
            query = query.filter(InterviewSession.status == status_enum)
        except ValueError:
            pass

    if min_score is not None:
        query = query.filter(InterviewSession.total_score >= min_score)

    total = query.count()
    sessions = query.order_by(
        InterviewSession.created_at.desc()
    ).offset(skip).limit(limit).all()

    interviews = []
    for session in sessions:
        interviews.append(InterviewSessionResponse(
            id=session.id,
            status=session.status.value,
            total_score=session.total_score,
            ai_summary=session.ai_summary,
            started_at=session.started_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
            candidate_id=session.candidate_id,
            candidate_name=session.candidate.name,
            job_id=session.job_id,
            job_title=session.job.title,
            company_name=employer.company_name,
            responses=[],
        ))

    return InterviewListResponse(interviews=interviews, total=total)


@router.get("/interviews/{interview_id}", response_model=InterviewSessionResponse)
async def get_interview_detail(
    interview_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get detailed view of an interview."""
    job_ids = [job.id for job in employer.jobs]

    session = db.query(InterviewSession).filter(
        InterviewSession.id == interview_id,
        InterviewSession.job_id.in_(job_ids)
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试不存在"
        )

    # Build response details
    responses = []
    for resp in session.responses:
        video_url = None
        if resp.video_url:
            video_url = storage_service.get_signed_url(resp.video_url)

        score_details = None
        if resp.ai_analysis:
            try:
                analysis_data = json.loads(resp.ai_analysis)
                if "scores" in analysis_data:
                    scores = analysis_data["scores"]
                    score_details = ScoreDetails(
                        communication=scores.get("communication", 0),
                        problem_solving=scores.get("problem_solving", 0),
                        domain_knowledge=scores.get("domain_knowledge", 0),
                        motivation=scores.get("motivation", 0),
                        culture_fit=scores.get("culture_fit", 0),
                        overall=resp.ai_score or 0,
                        analysis=analysis_data.get("analysis", ""),
                        strengths=analysis_data.get("strengths", []),
                        concerns=analysis_data.get("concerns", []),
                        highlight_quotes=analysis_data.get("highlight_quotes", []),
                    )
            except json.JSONDecodeError:
                pass

        responses.append(ResponseDetail(
            id=resp.id,
            question_index=resp.question_index,
            question_text=resp.question_text,
            video_url=video_url,
            transcription=resp.transcription,
            ai_score=resp.ai_score,
            ai_analysis=resp.ai_analysis,
            score_details=score_details,
            duration_seconds=resp.duration_seconds,
            created_at=resp.created_at,
        ))

    return InterviewSessionResponse(
        id=session.id,
        status=session.status.value,
        total_score=session.total_score,
        ai_summary=session.ai_summary,
        started_at=session.started_at,
        completed_at=session.completed_at,
        created_at=session.created_at,
        candidate_id=session.candidate_id,
        candidate_name=session.candidate.name,
        job_id=session.job_id,
        job_title=session.job.title,
        company_name=employer.company_name,
        responses=sorted(responses, key=lambda x: x.question_index),
    )


@router.patch("/interviews/{interview_id}", response_model=InterviewSessionResponse)
async def update_interview_status(
    interview_id: str,
    data: InterviewStatusUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update interview status (shortlist/reject)."""
    job_ids = [job.id for job in employer.jobs]

    session = db.query(InterviewSession).filter(
        InterviewSession.id == interview_id,
        InterviewSession.job_id.in_(job_ids)
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试不存在"
        )

    # Create or update match record
    match = db.query(Match).filter(
        Match.candidate_id == session.candidate_id,
        Match.job_id == session.job_id
    ).first()

    if match:
        match.status = data.status
    else:
        match = Match(
            id=generate_cuid("m"),
            candidate_id=session.candidate_id,
            job_id=session.job_id,
            score=session.total_score or 0,
            status=data.status,
        )
        db.add(match)

    db.commit()

    # Return updated session
    return await get_interview_detail(interview_id, employer, db)


# ==================== INVITE TOKEN ENDPOINTS ====================

@router.post("/jobs/{job_id}/invites", response_model=InviteTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_invite_token(
    job_id: str,
    data: InviteTokenCreate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Create an invite token for a job."""
    # Verify job belongs to employer
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    # Generate token
    token = secrets.token_urlsafe(32)

    # Calculate expiration
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_in_days)

    invite = InviteToken(
        id=generate_cuid("inv"),
        token=token,
        job_id=job_id,
        max_uses=data.max_uses,
        expires_at=expires_at,
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    from ..config import settings
    invite_url = f"{settings.frontend_url}/interview/start?token={token}"

    return InviteTokenResponse(
        id=invite.id,
        token=invite.token,
        job_id=invite.job_id,
        job_title=job.title,
        max_uses=invite.max_uses,
        used_count=invite.used_count,
        expires_at=invite.expires_at,
        is_active=invite.is_active,
        invite_url=invite_url,
        created_at=invite.created_at,
    )


@router.get("/jobs/{job_id}/invites", response_model=InviteTokenList)
async def list_invite_tokens(
    job_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List all invite tokens for a job."""
    # Verify job belongs to employer
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    invites = db.query(InviteToken).filter(
        InviteToken.job_id == job_id
    ).order_by(InviteToken.created_at.desc()).all()

    from ..config import settings
    tokens = []
    for invite in invites:
        invite_url = f"{settings.frontend_url}/interview/start?token={invite.token}"
        tokens.append(InviteTokenResponse(
            id=invite.id,
            token=invite.token,
            job_id=invite.job_id,
            job_title=job.title,
            max_uses=invite.max_uses,
            used_count=invite.used_count,
            expires_at=invite.expires_at,
            is_active=invite.is_active,
            invite_url=invite_url,
            created_at=invite.created_at,
        ))

    return InviteTokenList(tokens=tokens, total=len(tokens))


@router.delete("/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite_token(
    invite_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Delete (deactivate) an invite token."""
    invite = db.query(InviteToken).filter(
        InviteToken.id == invite_id
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请链接不存在"
        )

    # Verify it belongs to employer's job
    job = db.query(Job).filter(
        Job.id == invite.job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此邀请链接"
        )

    invite.is_active = False
    db.commit()

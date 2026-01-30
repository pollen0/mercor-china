from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import Optional
import uuid
import json

from ..database import get_db
from ..models import Employer, Job, InterviewSession, InterviewStatus, MatchStatus, Match, InviteToken, Vertical, RoleType, Message, MessageType, Candidate, CandidateVerticalProfile, VerticalProfileStatus
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
    ContactRequest,
    MessageResponse,
    BulkActionRequest,
    BulkActionResult,
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
from fastapi.responses import StreamingResponse
import csv
import io
from datetime import datetime, timedelta
import secrets
from ..utils.auth import create_access_token, verify_token, get_password_hash, verify_password
from ..services.storage import storage_service
from ..services.cache import cache_service
from ..services.matching import matching_service
from ..utils.rate_limit import limiter, RateLimits

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
            detail="No authentication provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer_id = payload.get("sub")
    if not employer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token content",
            headers={"WWW-Authenticate": "Bearer"},
        )

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employer not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return employer


@router.post("/register", response_model=EmployerWithToken, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def register_employer(
    request: Request,
    data: EmployerRegister,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new employer account."""
    # Check if email exists
    existing = db.query(Employer).filter(Employer.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
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
            detail="An account with this email already exists"
        )

    # Send verification email
    from .auth import create_verification_for_employer
    create_verification_for_employer(employer, db, background_tasks)

    token = create_access_token({"sub": employer.id, "type": "employer"})

    return EmployerWithToken(
        employer=EmployerResponse.model_validate(employer),
        token=token,
    )


@router.post("/login", response_model=EmployerWithToken)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login_employer(
    request: Request,
    data: EmployerLogin,
    db: Session = Depends(get_db)
):
    """Login as an employer."""
    employer = db.query(Employer).filter(Employer.email == data.email).first()

    if not employer or not verify_password(data.password, employer.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
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
    # Check cache first
    cached_stats = cache_service.get_dashboard_stats(employer.id)
    if cached_stats:
        return DashboardStats(**cached_stats)

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

    # Count interviews by status (exclude practice interviews)
    total = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.is_practice == False
    ).count()

    # Pending review = completed interviews that haven't been shortlisted or rejected
    completed_session_ids = db.query(InterviewSession.id).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.status == InterviewStatus.COMPLETED,
        InterviewSession.is_practice == False
    ).subquery()

    reviewed_session_ids = db.query(Match.candidate_id, Match.job_id).filter(
        Match.job_id.in_(job_ids),
        Match.status.in_([MatchStatus.SHORTLISTED, MatchStatus.REJECTED])
    ).subquery()

    # Count completed interviews minus reviewed ones (exclude practice)
    total_completed = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.status == InterviewStatus.COMPLETED,
        InterviewSession.is_practice == False
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

    # Calculate average score (exclude practice)
    avg_score = db.query(func.avg(InterviewSession.total_score)).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.total_score.isnot(None),
        InterviewSession.is_practice == False
    ).scalar()

    stats = DashboardStats(
        total_interviews=total,
        pending_review=pending,
        shortlisted=shortlisted,
        rejected=rejected,
        average_score=round(avg_score, 2) if avg_score else None,
    )

    # Cache the stats
    cache_service.set_dashboard_stats(employer.id, stats.model_dump())

    return stats


# Job management
@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    background_tasks: BackgroundTasks,
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

    # Auto-match with talent pool candidates
    if vertical:
        from ..config import settings
        background_tasks.add_task(
            auto_match_job_with_talent_pool,
            job_id=job.id,
            db_url=settings.database_url,
        )

    return job


def auto_match_job_with_talent_pool(job_id: str, db_url: str):
    """
    Background task to auto-match a new job with candidates in the talent pool.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from ..services.matching import matching_service
    import json
    import uuid
    import asyncio

    def _run_async(coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    import logging
    logger = logging.getLogger("zhimian.employers")

    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job or not job.vertical or not job.is_active:
            return

        # Find all completed vertical profiles for this vertical
        profiles = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.vertical == job.vertical,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
        ).all()

        logger.info(f"Auto-matching job {job_id} with {len(profiles)} talent pool candidates")

        for profile in profiles:
            try:
                candidate = profile.candidate
                candidate_data = candidate.resume_parsed_data if candidate else None

                # Calculate match score
                match_result = _run_async(
                    matching_service.calculate_match(
                        interview_score=profile.best_score or profile.interview_score or 5.0,
                        candidate_data=candidate_data,
                        job_title=job.title,
                        job_requirements=job.requirements or [],
                        job_location=job.location,
                        job_vertical=job.vertical.value,
                    )
                )

                # Check for existing match
                existing_match = db.query(Match).filter(
                    Match.candidate_id == profile.candidate_id,
                    Match.job_id == job_id
                ).first()

                if not existing_match:
                    # Create new match
                    new_match = Match(
                        id=f"m{uuid.uuid4().hex[:24]}",
                        candidate_id=profile.candidate_id,
                        job_id=job_id,
                        vertical_profile_id=profile.id,
                        score=profile.best_score or profile.interview_score or 5.0,
                        interview_score=match_result.interview_score,
                        skills_match_score=match_result.skills_match_score,
                        experience_match_score=match_result.experience_match_score,
                        location_match=match_result.location_match,
                        overall_match_score=match_result.overall_match_score,
                        factors=json.dumps(match_result.factors, ensure_ascii=False),
                        ai_reasoning=match_result.ai_reasoning,
                    )
                    db.add(new_match)
                    logger.info(f"Created match for candidate {profile.candidate_id}, score: {match_result.overall_match_score}")

            except Exception as e:
                logger.error(f"Failed to create match for profile {profile.id}: {e}")

        db.commit()
        logger.info(f"Completed auto-matching for job {job_id}")

    except Exception as e:
        logger.error(f"Error in auto_match_job_with_talent_pool: {e}")
    finally:
        db.close()


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
            detail="Job not found"
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
            detail="Job not found"
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
            detail="Job not found"
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
    """List all interviews for the employer's jobs (excludes practice interviews)."""
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        return InterviewListResponse(interviews=[], total=0)

    # Filter out practice interviews - employers should not see them
    query = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.is_practice == False
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
            detail="Interview not found"
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
            detail="Interview not found"
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

    # Invalidate relevant caches
    cache_service.invalidate_dashboard(employer.id)
    cache_service.invalidate_top_candidates(session.job_id)

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
            detail="Job not found"
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
            detail="Job not found"
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
            detail="Invite link not found"
        )

    # Verify it belongs to employer's job
    job = db.query(Job).filter(
        Job.id == invite.job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this invite link"
        )

    invite.is_active = False
    db.commit()


# ==================== CONTACT CANDIDATE ENDPOINTS ====================

@router.post("/candidates/{candidate_id}/contact", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def contact_candidate(
    candidate_id: str,
    data: ContactRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Send a message to a candidate."""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # If job_id provided, verify it belongs to employer
    if data.job_id:
        job = db.query(Job).filter(
            Job.id == data.job_id,
            Job.employer_id == employer.id
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Job not found or access denied"
            )

    # Map message type
    message_type_map = {
        'interview_request': MessageType.INTERVIEW_REQUEST,
        'rejection': MessageType.REJECTION,
        'shortlist_notice': MessageType.SHORTLIST_NOTICE,
        'custom': MessageType.CUSTOM,
    }
    msg_type = message_type_map.get(data.message_type, MessageType.CUSTOM)

    # Create message
    message = Message(
        id=generate_cuid("msg"),
        subject=data.subject,
        body=data.body,
        message_type=msg_type,
        employer_id=employer.id,
        candidate_id=candidate_id,
        job_id=data.job_id,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    # Send email notification to candidate
    from ..services.email import email_service

    # Get job title if job_id provided
    job_title = None
    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if job:
            job_title = job.title

    # Only send email if candidate has a valid email
    if candidate.email and not candidate.email.endswith("@placeholder.local"):
        email_service.send_employer_message(
            candidate_email=candidate.email,
            candidate_name=candidate.name,
            employer_name=employer.company_name,
            subject=data.subject,
            body=data.body,
            job_title=job_title,
            message_type=data.message_type,
        )

    return message


# ==================== BULK ACTIONS ENDPOINTS ====================

@router.post("/interviews/bulk-action", response_model=BulkActionResult)
async def bulk_interview_action(
    data: BulkActionRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Perform bulk action on multiple interviews (shortlist or reject)."""
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not created any jobs yet"
        )

    processed = 0
    failed = 0
    errors = []

    # Determine the status to set
    new_status = MatchStatus.SHORTLISTED if data.action == 'shortlist' else MatchStatus.REJECTED

    for interview_id in data.interview_ids:
        try:
            # Get the interview
            session = db.query(InterviewSession).filter(
                InterviewSession.id == interview_id,
                InterviewSession.job_id.in_(job_ids),
                InterviewSession.is_practice == False
            ).first()

            if not session:
                errors.append(f"Interview {interview_id} not found or access denied")
                failed += 1
                continue

            # Create or update match record
            match = db.query(Match).filter(
                Match.candidate_id == session.candidate_id,
                Match.job_id == session.job_id
            ).first()

            if match:
                match.status = new_status
            else:
                match = Match(
                    id=generate_cuid("m"),
                    candidate_id=session.candidate_id,
                    job_id=session.job_id,
                    score=session.total_score or 0,
                    status=new_status,
                )
                db.add(match)

            processed += 1

        except Exception as e:
            errors.append(f"Error processing interview {interview_id}: {str(e)}")
            failed += 1

    db.commit()

    # Invalidate relevant caches
    cache_service.invalidate_dashboard(employer.id)
    # Invalidate top candidates for all affected jobs
    affected_job_ids = set()
    for interview_id in data.interview_ids:
        session = db.query(InterviewSession).filter(InterviewSession.id == interview_id).first()
        if session and session.job_id:
            affected_job_ids.add(session.job_id)
    for jid in affected_job_ids:
        cache_service.invalidate_top_candidates(jid)

    return BulkActionResult(
        success=failed == 0,
        processed=processed,
        failed=failed,
        errors=errors
    )


# ==================== EXPORT ENDPOINTS ====================

@router.get("/interviews/export")
async def export_interviews_csv(
    job_id: Optional[str] = None,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Export interviews to CSV format."""
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not created any jobs yet"
        )

    # Build query
    query = db.query(InterviewSession).filter(
        InterviewSession.job_id.in_(job_ids),
        InterviewSession.is_practice == False
    )

    if job_id:
        query = query.filter(InterviewSession.job_id == job_id)

    sessions = query.order_by(InterviewSession.created_at.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Candidate Name',
        'Email',
        'Phone',
        'Job Title',
        'Score',
        'Status',
        'Interview Date',
        'Completed Date'
    ])

    # Write data rows
    for session in sessions:
        # Get match status if exists
        match = db.query(Match).filter(
            Match.candidate_id == session.candidate_id,
            Match.job_id == session.job_id
        ).first()
        status_text = match.status.value if match else session.status.value

        writer.writerow([
            session.candidate.name,
            session.candidate.email,
            session.candidate.phone,
            session.job.title if session.job else 'N/A',
            f"{session.total_score:.2f}" if session.total_score else 'N/A',
            status_text,
            session.started_at.strftime('%Y-%m-%d %H:%M') if session.started_at else 'N/A',
            session.completed_at.strftime('%Y-%m-%d %H:%M') if session.completed_at else 'N/A'
        ])

    # Get the CSV content
    output.seek(0)
    csv_content = output.getvalue()

    # Generate filename
    from datetime import datetime
    filename = f"interviews_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== TOP CANDIDATES / MATCHING ENDPOINTS ====================

from pydantic import BaseModel as PydanticBaseModel


class MatchDetailResponse(PydanticBaseModel):
    id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    job_id: str
    job_title: str
    status: str
    interview_score: Optional[float] = None
    skills_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    location_match: Optional[bool] = None
    overall_match_score: Optional[float] = None
    ai_reasoning: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/jobs/{job_id}/top-candidates", response_model=list[MatchDetailResponse])
async def get_top_candidates(
    job_id: str,
    limit: int = 10,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get the top candidates for a specific job, sorted by match score."""
    # Verify job belongs to employer
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.employer_id == employer.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Try cache first
    cached = cache_service.get_top_candidates(job_id, limit)
    if cached:
        return [MatchDetailResponse(**c) for c in cached]

    # Get matches sorted by overall_match_score
    matches = db.query(Match).filter(
        Match.job_id == job_id,
        Match.status.in_([MatchStatus.PENDING, MatchStatus.SHORTLISTED])  # Exclude rejected
    ).order_by(
        Match.overall_match_score.desc().nulls_last(),
        Match.score.desc().nulls_last()
    ).limit(limit).all()

    results = []
    for match in matches:
        results.append(MatchDetailResponse(
            id=match.id,
            candidate_id=match.candidate_id,
            candidate_name=match.candidate.name,
            candidate_email=match.candidate.email,
            job_id=match.job_id,
            job_title=job.title,
            status=match.status.value,
            interview_score=match.interview_score,
            skills_match_score=match.skills_match_score,
            experience_match_score=match.experience_match_score,
            location_match=match.location_match,
            overall_match_score=match.overall_match_score,
            ai_reasoning=match.ai_reasoning,
            created_at=match.created_at,
        ))

    # Cache the results
    cache_service.set_top_candidates(job_id, [r.model_dump(mode="json") for r in results], limit)

    return results


@router.get("/top-candidates", response_model=dict)
async def get_all_top_candidates(
    limit: int = 5,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Get top candidates across all jobs for the employer.
    Returns a dict with job_id as keys and list of top matches as values.
    """
    results = {}

    for job in employer.jobs:
        if not job.is_active:
            continue

        matches = db.query(Match).filter(
            Match.job_id == job.id,
            Match.status.in_([MatchStatus.PENDING, MatchStatus.SHORTLISTED])
        ).order_by(
            Match.overall_match_score.desc().nulls_last(),
            Match.score.desc().nulls_last()
        ).limit(limit).all()

        if matches:
            results[job.id] = {
                "job_title": job.title,
                "candidates": [
                    {
                        "id": m.id,
                        "candidate_id": m.candidate_id,
                        "candidate_name": m.candidate.name,
                        "overall_match_score": m.overall_match_score,
                        "interview_score": m.interview_score,
                        "status": m.status.value,
                    }
                    for m in matches
                ]
            }

    return results


# ==================== TALENT POOL ENDPOINTS ====================

from pydantic import Field as PydanticField


class TalentPoolCandidate(PydanticBaseModel):
    """Candidate info for talent pool browsing."""
    profile_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    vertical: str
    role_type: str
    interview_score: Optional[float] = None
    best_score: Optional[float] = None
    status: str
    completed_at: Optional[datetime] = None
    # Resume data
    skills: list[str] = []
    experience_summary: Optional[str] = None
    location: Optional[str] = None

    class Config:
        from_attributes = True


class TalentPoolResponse(PydanticBaseModel):
    """Response for talent pool browse."""
    candidates: list[TalentPoolCandidate]
    total: int


@router.get("/talent-pool", response_model=TalentPoolResponse)
async def browse_talent_pool(
    vertical: Optional[str] = None,
    role_type: Optional[str] = None,
    min_score: float = 0.0,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Browse the talent pool - candidates who have completed vertical interviews.

    Filter by vertical, role type, minimum score, and search keywords.
    Search matches against skills, company names, and job titles in resume.
    Returns candidate profiles with interview scores and resume data.
    """
    from sqlalchemy import or_, cast, String
    from sqlalchemy.dialects.postgresql import JSONB

    # Build query for completed vertical profiles
    query = db.query(CandidateVerticalProfile).join(
        Candidate, CandidateVerticalProfile.candidate_id == Candidate.id
    ).filter(
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    )

    # Apply filters
    if vertical:
        try:
            vertical_enum = Vertical(vertical)
            query = query.filter(CandidateVerticalProfile.vertical == vertical_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid vertical: {vertical}"
            )

    if role_type:
        try:
            role_type_enum = RoleType(role_type)
            query = query.filter(CandidateVerticalProfile.role_type == role_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role type: {role_type}"
            )

    # Filter by minimum score (use best_score)
    if min_score > 0:
        query = query.filter(CandidateVerticalProfile.best_score >= min_score)

    # Full-text search on resume data
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        # Search in candidate name and resume JSON fields
        query = query.filter(
            or_(
                func.lower(Candidate.name).like(search_term),
                func.lower(cast(Candidate.resume_parsed_data, String)).like(search_term),
            )
        )

    # Get total count
    total = query.count()

    # Get profiles sorted by best score
    profiles = query.order_by(
        CandidateVerticalProfile.best_score.desc().nulls_last()
    ).offset(offset).limit(limit).all()

    # Build response
    candidates = []
    for profile in profiles:
        candidate = profile.candidate

        # Extract resume data
        skills = []
        experience_summary = None
        location = None

        if candidate.resume_parsed_data:
            parsed = candidate.resume_parsed_data
            skills = parsed.get("skills", [])[:10]  # Limit to 10 skills
            location = parsed.get("location")

            # Build experience summary
            experiences = parsed.get("experience", [])
            if experiences:
                latest = experiences[0]
                experience_summary = f"{latest.get('title', '')} at {latest.get('company', '')}"

        candidates.append(TalentPoolCandidate(
            profile_id=profile.id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            vertical=profile.vertical.value,
            role_type=profile.role_type.value,
            interview_score=profile.interview_score,
            best_score=profile.best_score,
            status=profile.status.value,
            completed_at=profile.completed_at,
            skills=skills,
            experience_summary=experience_summary,
            location=location,
        ))

    return TalentPoolResponse(candidates=candidates, total=total)


@router.get("/talent-pool/{profile_id}")
async def get_talent_profile_detail(
    profile_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of a talent pool candidate profile.
    Includes full resume data, interview details, and video playback URLs.
    """
    from ..models.interview import InterviewResponse

    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.id == profile_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    candidate = profile.candidate

    # Get interview session details if available
    interview_data = None
    interview_responses = []
    if profile.interview_session_id:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == profile.interview_session_id
        ).first()
        if session:
            # Get interview responses with video URLs
            responses = db.query(InterviewResponse).filter(
                InterviewResponse.session_id == session.id
            ).order_by(InterviewResponse.question_index).all()

            for resp in responses:
                video_url = None
                if resp.video_url:
                    video_url = storage_service.get_signed_url(resp.video_url)

                # Parse scoring dimensions from ai_analysis
                score_dimensions = None
                if resp.ai_analysis:
                    try:
                        analysis_data = json.loads(resp.ai_analysis)
                        if "scores" in analysis_data:
                            scores = analysis_data["scores"]
                            score_dimensions = {
                                "communication": scores.get("communication", 0),
                                "problem_solving": scores.get("problem_solving", 0),
                                "domain_knowledge": scores.get("domain_knowledge", 0),
                                "motivation": scores.get("motivation", 0),
                                "culture_fit": scores.get("culture_fit", 0),
                            }
                    except json.JSONDecodeError:
                        pass

                interview_responses.append({
                    "id": resp.id,
                    "question_index": resp.question_index,
                    "question_text": resp.question_text,
                    "question_type": resp.question_type,
                    "video_url": video_url,
                    "transcription": resp.transcription,
                    "ai_score": resp.ai_score,
                    "ai_analysis": resp.ai_analysis,
                    "score_dimensions": score_dimensions,
                    "duration_seconds": resp.duration_seconds,
                    "created_at": resp.created_at.isoformat() if resp.created_at else None,
                    # Coding-specific fields
                    "code_solution": resp.code_solution if resp.question_type == "coding" else None,
                    "test_results": resp.test_results if resp.question_type == "coding" else None,
                })

            interview_data = {
                "session_id": session.id,
                "total_score": session.total_score,
                "ai_summary": session.ai_summary,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "responses": interview_responses,
            }

    # Get current status with this employer (if any match exists)
    employer_status = None
    for job in employer.jobs:
        match = db.query(Match).filter(
            Match.candidate_id == candidate.id,
            Match.job_id == job.id
        ).first()
        if match:
            employer_status = {
                "match_id": match.id,
                "job_id": job.id,
                "job_title": job.title,
                "status": match.status.value,
            }
            break

    return {
        "profile": {
            "id": profile.id,
            "vertical": profile.vertical.value,
            "role_type": profile.role_type.value,
            "interview_score": profile.interview_score,
            "best_score": profile.best_score,
            "attempt_count": profile.attempt_count,
            "completed_at": profile.completed_at.isoformat() if profile.completed_at else None,
        },
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "resume_url": candidate.resume_url,
            "resume_data": candidate.resume_parsed_data,
        },
        "interview": interview_data,
        "employer_status": employer_status,
    }


class TalentPoolStatusUpdate(PydanticBaseModel):
    """Request body for updating talent pool candidate status."""
    status: str  # CONTACTED, IN_REVIEW, SHORTLISTED, REJECTED, HIRED
    job_id: Optional[str] = None  # Which job to associate with (optional)


@router.patch("/talent-pool/{profile_id}/status")
async def update_talent_pool_status(
    profile_id: str,
    data: TalentPoolStatusUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Update the status of a talent pool candidate for this employer.
    Creates or updates a Match record to track the status.
    """
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.id == profile_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    # Validate status
    try:
        new_status = MatchStatus(data.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {data.status}"
        )

    # If job_id provided, verify it belongs to employer
    job = None
    if data.job_id:
        job = db.query(Job).filter(
            Job.id == data.job_id,
            Job.employer_id == employer.id
        ).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Job not found or access denied"
            )
    else:
        # Use the first active job from this employer as default
        job = db.query(Job).filter(
            Job.employer_id == employer.id,
            Job.is_active == True
        ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please create a job first before updating candidate status"
        )

    # Find or create match record
    match = db.query(Match).filter(
        Match.candidate_id == profile.candidate_id,
        Match.job_id == job.id
    ).first()

    if match:
        match.status = new_status
        match.updated_at = func.now()
    else:
        match = Match(
            id=generate_cuid("m"),
            candidate_id=profile.candidate_id,
            job_id=job.id,
            vertical_profile_id=profile.id,
            score=profile.best_score or profile.interview_score or 5.0,
            status=new_status,
        )
        db.add(match)

    db.commit()
    db.refresh(match)

    return {
        "success": True,
        "match_id": match.id,
        "status": match.status.value,
        "job_id": job.id,
        "job_title": job.title,
    }


@router.post("/talent-pool/{profile_id}/contact")
async def contact_talent_pool_candidate(
    profile_id: str,
    data: ContactRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Contact a candidate from the talent pool.
    Sends email and automatically updates status to CONTACTED.
    """
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.id == profile_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    candidate = profile.candidate

    # Map message type
    message_type_map = {
        'interview_request': MessageType.INTERVIEW_REQUEST,
        'rejection': MessageType.REJECTION,
        'shortlist_notice': MessageType.SHORTLIST_NOTICE,
        'custom': MessageType.CUSTOM,
    }
    msg_type = message_type_map.get(data.message_type, MessageType.CUSTOM)

    # Create message record
    message = Message(
        id=generate_cuid("msg"),
        subject=data.subject,
        body=data.body,
        message_type=msg_type,
        employer_id=employer.id,
        candidate_id=candidate.id,
        job_id=data.job_id,
    )

    db.add(message)

    # Send email notification
    from ..services.email import email_service

    job_title = None
    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if job:
            job_title = job.title

    # Send email if candidate has valid email
    email_sent = False
    if candidate.email and not candidate.email.endswith("@placeholder.local"):
        result = email_service.send_employer_message(
            candidate_email=candidate.email,
            candidate_name=candidate.name,
            employer_name=employer.company_name,
            subject=data.subject,
            body=data.body,
            job_title=job_title,
            message_type=data.message_type,
        )
        email_sent = result is not None

    # Auto-update status to CONTACTED if not already in a further state
    job_id = data.job_id
    if not job_id:
        # Use first active job
        job = db.query(Job).filter(
            Job.employer_id == employer.id,
            Job.is_active == True
        ).first()
        if job:
            job_id = job.id

    if job_id:
        match = db.query(Match).filter(
            Match.candidate_id == candidate.id,
            Match.job_id == job_id
        ).first()

        if match:
            # Only update to CONTACTED if currently PENDING
            if match.status == MatchStatus.PENDING:
                match.status = MatchStatus.CONTACTED
        else:
            # Create new match with CONTACTED status
            match = Match(
                id=generate_cuid("m"),
                candidate_id=candidate.id,
                job_id=job_id,
                vertical_profile_id=profile.id,
                score=profile.best_score or profile.interview_score or 5.0,
                status=MatchStatus.CONTACTED,
            )
            db.add(match)

    db.commit()
    db.refresh(message)

    return {
        "success": True,
        "message_id": message.id,
        "email_sent": email_sent,
        "candidate_email": candidate.email if email_sent else None,
    }

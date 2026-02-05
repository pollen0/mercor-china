from fastapi import APIRouter, Depends, HTTPException, status, Header, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import Optional
from pydantic import BaseModel, Field
import uuid
import json

from ..database import get_db
from ..models import Employer, Job, InterviewSession, InterviewStatus, MatchStatus, Match, InviteToken, Vertical, RoleType, Message, MessageType, Candidate, CandidateVerticalProfile, VerticalProfileStatus
from ..models.employer import Organization, OrganizationMember, OrganizationInvite, OrganizationRole, InviteStatus
from ..models.activity import CandidateActivity, CandidateAward, Club
from ..schemas.employer import (
    EmployerRegister,
    EmployerLogin,
    EmployerUpdate,
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
    MatchAlert,
    MatchAlertCandidate,
    MatchAlertList,
    # Organization schemas
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    OrganizationList,
    OrganizationMemberResponse,
    OrganizationInviteCreate,
    OrganizationInviteResponse,
    OrganizationInviteAccept,
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
from ..utils.auth import create_access_token, create_token, create_token_pair, verify_token, verify_refresh_token, revoke_refresh_token, get_password_hash, verify_password, blacklist_token
from ..config import settings
from ..services.storage import storage_service
from ..services.cache import cache_service
from ..services.matching import matching_service
from ..utils.rate_limit import limiter, RateLimits
import logging

logger = logging.getLogger("pathway.employers")
router = APIRouter()
security = HTTPBearer()


def generate_cuid(prefix: str = "e") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# Staleness threshold for GitHub analysis (7 days)
GITHUB_ANALYSIS_STALE_DAYS = 7


async def trigger_github_analysis_if_stale(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    db: Session,
):
    """
    Check if a candidate's GitHub analysis is stale or missing and trigger a refresh.
    Called when an employer views a candidate's profile.
    """
    from ..models.github_analysis import GitHubAnalysis

    # Get the candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate or not candidate.github_access_token:
        return  # No GitHub connected, nothing to analyze

    # Check if analysis exists and is recent
    analysis = db.query(GitHubAnalysis).filter(
        GitHubAnalysis.candidate_id == candidate_id
    ).first()

    should_analyze = False
    if not analysis:
        # No analysis exists, trigger one
        should_analyze = True
        logger.info(f"No GitHub analysis exists for candidate {candidate_id}, triggering analysis")
    elif analysis.analyzed_at:
        # Check if analysis is stale
        stale_threshold = datetime.utcnow() - timedelta(days=GITHUB_ANALYSIS_STALE_DAYS)
        if analysis.analyzed_at < stale_threshold:
            should_analyze = True
            logger.info(f"GitHub analysis for candidate {candidate_id} is stale, triggering refresh")

    if should_analyze:
        # Import the background analysis function from candidates router
        from .candidates import run_github_analysis_background
        import asyncio

        background_tasks.add_task(
            asyncio.create_task,
            run_github_analysis_background(candidate_id)
        )


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
        name=data.name,
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

    # Generate token pair
    tokens = create_token_pair(subject=employer.id, token_type="employer")

    return EmployerWithToken(
        employer=EmployerResponse.model_validate(employer),
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=settings.jwt_expiry_hours * 3600,
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

    # Generate token pair
    tokens = create_token_pair(subject=employer.id, token_type="employer")

    return EmployerWithToken(
        employer=EmployerResponse.model_validate(employer),
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=settings.jwt_expiry_hours * 3600,
    )


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH_LOGIN)
async def refresh_employer_token(
    request: Request,
    refresh_token: str,
):
    """
    Get a new access token using a refresh token.

    This allows the frontend to maintain sessions without requiring re-login.
    The refresh token has a longer expiry (30 days) while access tokens expire in 1 hour.
    """
    from ..schemas.candidate import TokenRefreshResponse

    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Verify this is an employer token
    if payload.get("type") != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Generate new access token
    new_access_token = create_token(
        subject=user_id,
        token_type="employer",
    )

    return TokenRefreshResponse(
        token=new_access_token,
        expires_in=settings.jwt_expiry_hours * 3600,
    )


@router.post("/logout")
async def logout_employer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Logout an employer by invalidating their token.
    The token will be blacklisted and cannot be used again.
    """
    token = credentials.credentials
    success = blacklist_token(token)

    if success:
        return {"message": "Successfully logged out"}
    else:
        # Even if blacklisting fails (e.g., Redis down), return success
        # Client will clear their token anyway
        return {"message": "Logged out (token invalidation unavailable)"}


@router.get("/me", response_model=EmployerResponse)
async def get_current_employer_profile(
    employer: Employer = Depends(get_current_employer)
):
    """Get the current employer's profile."""
    return employer


@router.patch("/me", response_model=EmployerResponse)
async def update_current_employer_profile(
    data: EmployerUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update the current employer's profile."""
    # Update fields if provided
    if data.name is not None:
        employer.name = data.name
    if data.company_name is not None:
        employer.company_name = data.company_name
    if data.industry is not None:
        employer.industry = data.industry
    if data.company_size is not None:
        employer.company_size = data.company_size

    db.commit()
    db.refresh(employer)
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


@router.get("/match-alerts", response_model=MatchAlertList)
async def get_match_alerts(
    limit: int = 20,
    offset: int = 0,
    unread_only: bool = False,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get recent candidate matches/alerts for the employer."""
    # Get job IDs for this employer
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        return MatchAlertList(alerts=[], total=0, unread_count=0)

    # Build query for matches
    query = db.query(Match).filter(Match.job_id.in_(job_ids))

    # Optionally filter to only new/unviewed matches (PENDING status)
    if unread_only:
        query = query.filter(Match.status == MatchStatus.PENDING)

    # Get total count before pagination
    total = query.count()

    # Get unread count (matches with PENDING status)
    unread_count = db.query(Match).filter(
        Match.job_id.in_(job_ids),
        Match.status == MatchStatus.PENDING
    ).count()

    # Get matches with pagination, ordered by newest first
    matches = query.order_by(Match.created_at.desc()).offset(offset).limit(limit).all()

    # Build response
    alerts = []
    for match in matches:
        candidate = match.candidate
        job = match.job

        alerts.append(MatchAlert(
            id=match.id,
            candidate=MatchAlertCandidate(
                id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                university=candidate.university,
                major=candidate.major,
                graduation_year=candidate.graduation_year,
            ),
            job_id=job.id if job else None,
            job_title=job.title if job else None,
            match_score=match.overall_match_score or match.score,
            interview_score=match.interview_score,
            skills_match_score=match.skills_match_score,
            status=match.status.value,
            created_at=match.created_at,
            is_new=match.status == MatchStatus.PENDING,
        ))

    return MatchAlertList(alerts=alerts, total=total, unread_count=unread_count)


@router.post("/match-alerts/{match_id}/mark-viewed")
async def mark_match_viewed(
    match_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Mark a match alert as viewed (changes status from PENDING if still pending)."""
    # Verify the match belongs to one of the employer's jobs
    job_ids = [job.id for job in employer.jobs]

    match = db.query(Match).filter(
        Match.id == match_id,
        Match.job_id.in_(job_ids)
    ).first()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    # Only update if still in PENDING status
    # We don't want to downgrade a match that's already CONTACTED, SHORTLISTED, etc.
    if match.status == MatchStatus.PENDING:
        match.status = MatchStatus.IN_REVIEW
        db.commit()

    return {"success": True, "status": match.status.value}


class WatchlistCandidate(BaseModel):
    """Candidate on employer's watchlist."""
    candidate_id: str
    candidate_name: str
    candidate_email: str
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    vertical: Optional[str] = None
    best_score: Optional[float] = None
    profile_score: Optional[float] = None
    github_username: Optional[str] = None
    added_at: datetime
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    notes: Optional[str] = None


class WatchlistResponse(BaseModel):
    """Response for watchlist."""
    candidates: list[WatchlistCandidate]
    total: int


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_watchlist(
    graduation_year: Optional[int] = None,
    university: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Get candidates on the employer's watchlist.

    Watchlist is for tracking promising candidates (e.g., freshmen/sophomores)
    for future opportunities. Filter by graduation year or university.
    """
    # Get job IDs for this employer
    job_ids = [job.id for job in employer.jobs]

    if not job_ids:
        return WatchlistResponse(candidates=[], total=0)

    # Query watchlist matches
    query = db.query(Match).filter(
        Match.job_id.in_(job_ids),
        Match.status == MatchStatus.WATCHLIST
    ).join(
        Candidate, Match.candidate_id == Candidate.id
    )

    # Apply filters
    if graduation_year:
        query = query.filter(Candidate.graduation_year == graduation_year)
    if university:
        query = query.filter(Candidate.university.ilike(f"%{university}%"))

    # Get total count
    total = query.count()

    # Get paginated results ordered by when added (most recent first)
    matches = query.order_by(Match.updated_at.desc().nulls_last(), Match.created_at.desc()).offset(offset).limit(limit).all()

    # Build response
    candidates = []
    for match in matches:
        candidate = match.candidate
        job = match.job
        vertical_profile = match.vertical_profile

        candidates.append(WatchlistCandidate(
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            vertical=vertical_profile.vertical.value if vertical_profile else None,
            best_score=vertical_profile.best_score if vertical_profile else None,
            profile_score=match.score,
            github_username=candidate.github_username,
            added_at=match.updated_at or match.created_at,
            job_id=job.id if job else None,
            job_title=job.title if job else None,
            notes=match.ai_reasoning,  # Using ai_reasoning field for notes
        ))

    return WatchlistResponse(candidates=candidates, total=total)


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

    # Invalidate dashboard stats cache since job count changed
    cache_service.invalidate_dashboard(employer.id)

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
    logger = logging.getLogger("pathway.employers")

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

        # Get employer info for job details (company_stage, industry)
        employer = job.employer if job else None
        job_company_stage = getattr(employer, 'company_stage', None) if employer else None
        job_industry = getattr(employer, 'industry', None) if employer else None

        for profile in profiles:
            try:
                candidate = profile.candidate
                candidate_data = candidate.resume_parsed_data if candidate else None
                candidate_preferences = candidate.sharing_preferences if candidate else None

                # Calculate match score with preference boost
                match_result = _run_async(
                    matching_service.calculate_match(
                        interview_score=profile.best_score or profile.interview_score or 5.0,
                        candidate_data=candidate_data,
                        job_title=job.title,
                        job_requirements=job.requirements or [],
                        job_location=job.location,
                        job_vertical=job.vertical.value,
                        # Preference boost params
                        candidate_preferences=candidate_preferences,
                        job_company_stage=job_company_stage,
                        job_industry=job_industry,
                    )
                )

                # Check for existing match
                existing_match = db.query(Match).filter(
                    Match.candidate_id == profile.candidate_id,
                    Match.job_id == job_id
                ).first()

                if not existing_match:
                    # Create new match (use boosted score for ranking)
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
                        overall_match_score=match_result.boosted_match_score,  # Use boosted score
                        factors=json.dumps(match_result.factors, ensure_ascii=False),
                        ai_reasoning=match_result.ai_reasoning,
                    )
                    db.add(new_match)
                    boost_info = f" (boost: +{int(match_result.preference_boost)})" if match_result.preference_boost > 0 else ""
                    logger.info(f"Created match for candidate {profile.candidate_id}, score: {match_result.boosted_match_score}{boost_info}")

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

    # Invalidate dashboard stats cache
    cache_service.invalidate_dashboard(employer.id)

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

    # Invalidate dashboard stats cache
    cache_service.invalidate_dashboard(employer.id)


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
            job_title=session.job.title if session.job else None,
            company_name=employer.company_name,
            responses=[],
        ))

    return InterviewListResponse(interviews=interviews, total=total)


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
        job_title=session.job.title if session.job else None,
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
    # Invalidate top candidates for all affected jobs (only employer's own jobs)
    affected_job_ids = set()
    for interview_id in data.interview_ids:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == interview_id,
            InterviewSession.job_id.in_(job_ids)  # Security: only employer's jobs
        ).first()
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


# ==================== TOP CANDIDATES / MATCHING ENDPOINTS ====================

from pydantic import BaseModel as BaseModel


class MatchDetailResponse(BaseModel):
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


class CompletionStatus(BaseModel):
    """Status indicators for what the candidate has completed."""
    resume_uploaded: bool = False
    github_connected: bool = False
    interview_completed: bool = False
    education_filled: bool = False
    transcript_uploaded: bool = False


class ScoreBreakdown(BaseModel):
    """Score breakdown by category."""
    communication: Optional[float] = None
    problem_solving: Optional[float] = None
    domain_knowledge: Optional[float] = None
    motivation: Optional[float] = None
    culture_fit: Optional[float] = None
    # Profile-based scores (when no interview)
    technical_skills: Optional[float] = None
    experience_quality: Optional[float] = None
    education: Optional[float] = None
    github_activity: Optional[float] = None


class ActivitySummary(BaseModel):
    """Summary of a candidate's activity/club involvement."""
    name: str
    role: Optional[str] = None
    prestige_tier: Optional[int] = None  # 1-5 scale
    category: Optional[str] = None

    class Config:
        from_attributes = True


class AwardSummary(BaseModel):
    """Summary of a candidate's award."""
    name: str
    issuer: Optional[str] = None
    award_type: Optional[str] = None
    prestige_tier: Optional[int] = None  # 1-5 scale

    class Config:
        from_attributes = True


class CohortBadge(BaseModel):
    """Cohort comparison badge (e.g., 'Top 10% of Berkeley 2026')."""
    percentile: int  # 1-99, where candidate ranks
    top_percent: int  # Inverse of percentile (for "Top X%" display)
    cohort_label: str  # e.g., "Berkeley 2026"
    cohort_size: int  # Number of candidates in cohort
    badge_text: str  # Full display text, e.g., "Top 10% of Berkeley 2026"


class TalentPoolCandidate(BaseModel):
    """Candidate info for talent pool browsing."""
    profile_id: Optional[str] = None  # May be None for candidates without vertical profile
    candidate_id: str
    candidate_name: str
    candidate_email: str
    vertical: Optional[str] = None  # May be None for candidates without vertical profile
    role_type: Optional[str] = None
    interview_score: Optional[float] = None
    best_score: Optional[float] = None
    profile_score: Optional[float] = None  # Score based on resume/GitHub (pre-interview)
    status: str  # COMPLETED, IN_PROGRESS, PENDING, or PROFILE_ONLY
    completed_at: Optional[datetime] = None
    # Resume data
    skills: list[str] = []
    experience_summary: Optional[str] = None
    location: Optional[str] = None
    # Completion indicators
    completion_status: CompletionStatus = CompletionStatus()
    # Score breakdown
    score_breakdown: Optional[ScoreBreakdown] = None
    # Activities and awards
    activities: list[ActivitySummary] = []
    awards: list[AwardSummary] = []
    # Education info
    university: Optional[str] = None
    major: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    # GitHub info
    github_username: Optional[str] = None
    github_languages: list[str] = []  # Top languages
    # Cohort comparison (e.g., "Top 10% of Berkeley 2026")
    cohort_badge: Optional[CohortBadge] = None

    class Config:
        from_attributes = True


class TalentPoolResponse(BaseModel):
    """Response for talent pool browse."""
    candidates: list[TalentPoolCandidate]
    total: int


@router.get("/talent-pool", response_model=TalentPoolResponse)
async def browse_talent_pool(
    vertical: Optional[str] = None,
    role_type: Optional[str] = None,
    min_score: float = 0.0,
    search: Optional[str] = None,
    include_incomplete: bool = True,  # Include candidates with profile data but no completed interview
    limit: int = 20,
    offset: int = 0,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Browse the talent pool - candidates with profile data (resume, GitHub, education).

    Now includes candidates who have uploaded profile data even before completing interviews.
    Shows completion status indicators and profile-based scores.

    Filter by vertical, role type, minimum score, and search keywords.
    Search matches against skills, company names, and job titles in resume.
    Returns candidate profiles with interview scores, profile scores, and completion status.
    """
    from sqlalchemy import or_, cast, String, case
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.orm import joinedload
    from ..services.scoring import scoring_service
    from ..services.cohort import cohort_service

    candidates_result = []

    # Part 1: Get candidates with completed vertical profiles
    # Use joinedload to eagerly load the candidate relationship (avoid N+1)
    completed_query = db.query(CandidateVerticalProfile).join(
        Candidate, CandidateVerticalProfile.candidate_id == Candidate.id
    ).options(
        joinedload(CandidateVerticalProfile.candidate)
    ).filter(
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    )

    # Apply vertical filter
    if vertical:
        try:
            vertical_enum = Vertical(vertical)
            completed_query = completed_query.filter(CandidateVerticalProfile.vertical == vertical_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid vertical: {vertical}"
            )

    if role_type:
        try:
            role_type_enum = RoleType(role_type)
            completed_query = completed_query.filter(CandidateVerticalProfile.role_type == role_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role type: {role_type}"
            )

    # Filter by minimum score
    if min_score > 0:
        completed_query = completed_query.filter(CandidateVerticalProfile.best_score >= min_score)

    # Full-text search
    if search and search.strip():
        search_term = f"%{search.strip().lower()}%"
        completed_query = completed_query.filter(
            or_(
                func.lower(Candidate.name).like(search_term),
                func.lower(cast(Candidate.resume_parsed_data, String)).like(search_term),
            )
        )

    completed_profiles = completed_query.order_by(
        CandidateVerticalProfile.best_score.desc().nulls_last()
    ).all()

    # Track candidate IDs we've already added
    added_candidate_ids = set()

    # Batch pre-fetch activities and awards to avoid N+1 queries
    candidate_ids_for_batch = [p.candidate_id for p in completed_profiles]

    # Batch fetch all activities for these candidates (single query instead of N)
    activities_by_candidate: dict[str, list] = {}
    if candidate_ids_for_batch:
        all_activities = db.query(CandidateActivity).options(
            joinedload(CandidateActivity.club)
        ).filter(
            CandidateActivity.candidate_id.in_(candidate_ids_for_batch)
        ).order_by(
            CandidateActivity.activity_score.desc().nulls_last()
        ).all()

        for a in all_activities:
            if a.candidate_id not in activities_by_candidate:
                activities_by_candidate[a.candidate_id] = []
            # Limit to 5 per candidate
            if len(activities_by_candidate[a.candidate_id]) < 5:
                activities_by_candidate[a.candidate_id].append(a)

    # Batch fetch all awards for these candidates (single query instead of N)
    awards_by_candidate: dict[str, list] = {}
    if candidate_ids_for_batch:
        all_awards = db.query(CandidateAward).filter(
            CandidateAward.candidate_id.in_(candidate_ids_for_batch)
        ).order_by(
            CandidateAward.prestige_tier.desc().nulls_last()
        ).all()

        for a in all_awards:
            if a.candidate_id not in awards_by_candidate:
                awards_by_candidate[a.candidate_id] = []
            # Limit to 5 per candidate
            if len(awards_by_candidate[a.candidate_id]) < 5:
                awards_by_candidate[a.candidate_id].append(a)

    for profile in completed_profiles:
        candidate = profile.candidate
        added_candidate_ids.add(candidate.id)

        # Extract resume data
        skills = []
        experience_summary = None
        location = None

        if candidate.resume_parsed_data:
            parsed = candidate.resume_parsed_data
            skills = parsed.get("skills", [])[:10]
            location = parsed.get("location")
            experiences = parsed.get("experience", [])
            if experiences:
                latest = experiences[0]
                experience_summary = f"{latest.get('title', '')} at {latest.get('company', '')}"

        # Build completion status
        completion_status = CompletionStatus(
            resume_uploaded=candidate.resume_url is not None,
            github_connected=candidate.github_username is not None,
            interview_completed=True,  # They have a completed profile
            education_filled=candidate.university is not None or candidate.major is not None,
            transcript_uploaded=candidate.courses is not None and len(candidate.courses) > 0,
        )

        # Build score breakdown from interview data
        score_breakdown = None
        if profile.interview_session_id:
            session = db.query(InterviewSession).filter(
                InterviewSession.id == profile.interview_session_id
            ).first()
            if session and session.responses:
                # Aggregate scores from responses
                from ..models.interview import InterviewResponse
                responses = db.query(InterviewResponse).filter(
                    InterviewResponse.session_id == session.id
                ).all()
                if responses:
                    avg_scores = {"communication": [], "problem_solving": [], "domain_knowledge": [], "motivation": [], "culture_fit": []}
                    for resp in responses:
                        if resp.ai_analysis:
                            try:
                                analysis = json.loads(resp.ai_analysis) if isinstance(resp.ai_analysis, str) else resp.ai_analysis
                                scores = analysis.get("scores", {})
                                for dim in avg_scores:
                                    if dim in scores:
                                        avg_scores[dim].append(scores[dim] / 10 if scores[dim] > 10 else scores[dim])
                            except (json.JSONDecodeError, TypeError):
                                pass

                    score_breakdown = ScoreBreakdown(
                        communication=round(sum(avg_scores["communication"]) / len(avg_scores["communication"]), 2) if avg_scores["communication"] else None,
                        problem_solving=round(sum(avg_scores["problem_solving"]) / len(avg_scores["problem_solving"]), 2) if avg_scores["problem_solving"] else None,
                        domain_knowledge=round(sum(avg_scores["domain_knowledge"]) / len(avg_scores["domain_knowledge"]), 2) if avg_scores["domain_knowledge"] else None,
                        motivation=round(sum(avg_scores["motivation"]) / len(avg_scores["motivation"]), 2) if avg_scores["motivation"] else None,
                        culture_fit=round(sum(avg_scores["culture_fit"]) / len(avg_scores["culture_fit"]), 2) if avg_scores["culture_fit"] else None,
                    )

        # Get activities and awards from pre-fetched batch (avoids N+1)
        activities_list = activities_by_candidate.get(candidate.id, [])
        activities = [
            ActivitySummary(
                name=a.activity_name,
                role=a.role,
                prestige_tier=a.club.prestige_tier if a.club else None,
                category=a.club.category if a.club else None,
            )
            for a in activities_list
        ]

        awards_list = awards_by_candidate.get(candidate.id, [])
        awards = [
            AwardSummary(
                name=a.name,
                issuer=a.issuer,
                award_type=a.award_type,
                prestige_tier=a.prestige_tier,
            )
            for a in awards_list
        ]

        # Get GitHub languages
        github_languages = []
        if candidate.github_data:
            langs = candidate.github_data.get("languages", {})
            # Sort by bytes and take top 5
            github_languages = sorted(langs.keys(), key=lambda x: langs.get(x, 0), reverse=True)[:5]

        # Calculate cohort badge (e.g., "Top 10% of Berkeley 2026")
        cohort_badge = None
        if profile.best_score and candidate.university and candidate.graduation_year:
            badge_data = cohort_service.get_cohort_badge(
                score=profile.best_score,
                university=candidate.university,
                graduation_year=candidate.graduation_year,
                vertical=profile.vertical,
                db=db,
            )
            if badge_data:
                cohort_badge = CohortBadge(**badge_data)

        candidates_result.append(TalentPoolCandidate(
            profile_id=profile.id,
            candidate_id=candidate.id,
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            vertical=profile.vertical.value,
            role_type=profile.role_type.value,
            interview_score=profile.interview_score,
            best_score=profile.best_score,
            profile_score=None,  # Will be set from profile scoring
            status="completed",
            completed_at=profile.completed_at,
            skills=skills,
            experience_summary=experience_summary,
            location=location,
            completion_status=completion_status,
            score_breakdown=score_breakdown,
            activities=activities,
            awards=awards,
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            gpa=candidate.gpa,
            github_username=candidate.github_username,
            github_languages=github_languages,
            cohort_badge=cohort_badge,
        ))

    # Part 2: Get candidates with profile data but no completed interview
    if include_incomplete:
        # Query candidates who have uploaded resume OR connected GitHub
        # but don't have a completed vertical profile yet
        profile_only_query = db.query(Candidate).filter(
            or_(
                Candidate.resume_url.isnot(None),
                Candidate.github_username.isnot(None),
            )
        )

        # Only apply notin_ filter if we have candidates to exclude
        # (empty notin_ can cause issues with some databases)
        if added_candidate_ids:
            profile_only_query = profile_only_query.filter(
                Candidate.id.notin_(added_candidate_ids)
            )

        # Apply search filter
        if search and search.strip():
            search_term = f"%{search.strip().lower()}%"
            profile_only_query = profile_only_query.filter(
                or_(
                    func.lower(Candidate.name).like(search_term),
                    func.lower(cast(Candidate.resume_parsed_data, String)).like(search_term),
                )
            )

        profile_only_candidates = profile_only_query.order_by(
            Candidate.created_at.desc()
        ).all()

        # Batch pre-fetch data for incomplete candidates to avoid N+1 queries
        incomplete_candidate_ids = [c.id for c in profile_only_candidates]

        # Batch fetch all vertical profiles for these candidates
        profiles_by_candidate_incomplete: dict[str, CandidateVerticalProfile] = {}
        if incomplete_candidate_ids:
            all_profiles = db.query(CandidateVerticalProfile).filter(
                CandidateVerticalProfile.candidate_id.in_(incomplete_candidate_ids)
            ).all()
            for p in all_profiles:
                profiles_by_candidate_incomplete[p.candidate_id] = p

        # Batch fetch activities for incomplete candidates
        activities_by_candidate_incomplete: dict[str, list] = {}
        if incomplete_candidate_ids:
            all_activities = db.query(CandidateActivity).options(
                joinedload(CandidateActivity.club)
            ).filter(
                CandidateActivity.candidate_id.in_(incomplete_candidate_ids)
            ).order_by(
                CandidateActivity.activity_score.desc().nulls_last()
            ).all()

            for a in all_activities:
                if a.candidate_id not in activities_by_candidate_incomplete:
                    activities_by_candidate_incomplete[a.candidate_id] = []
                if len(activities_by_candidate_incomplete[a.candidate_id]) < 5:
                    activities_by_candidate_incomplete[a.candidate_id].append(a)

        # Batch fetch awards for incomplete candidates
        awards_by_candidate_incomplete: dict[str, list] = {}
        if incomplete_candidate_ids:
            all_awards = db.query(CandidateAward).filter(
                CandidateAward.candidate_id.in_(incomplete_candidate_ids)
            ).order_by(
                CandidateAward.prestige_tier.desc().nulls_last()
            ).all()

            for a in all_awards:
                if a.candidate_id not in awards_by_candidate_incomplete:
                    awards_by_candidate_incomplete[a.candidate_id] = []
                if len(awards_by_candidate_incomplete[a.candidate_id]) < 5:
                    awards_by_candidate_incomplete[a.candidate_id].append(a)

        for candidate in profile_only_candidates:
            # Get existing profile from batch (avoids N+1)
            existing_profile = profiles_by_candidate_incomplete.get(candidate.id)

            # Apply vertical filter if specified
            if vertical and existing_profile:
                try:
                    vertical_enum = Vertical(vertical)
                    if existing_profile.vertical != vertical_enum:
                        continue
                except ValueError:
                    pass

            # Extract resume data
            skills = []
            experience_summary = None
            location = None

            if candidate.resume_parsed_data:
                parsed = candidate.resume_parsed_data
                skills = parsed.get("skills", [])[:10]
                location = parsed.get("location")
                experiences = parsed.get("experience", [])
                if experiences:
                    latest = experiences[0]
                    experience_summary = f"{latest.get('title', '')} at {latest.get('company', '')}"

            # Build completion status
            completion_status = CompletionStatus(
                resume_uploaded=candidate.resume_url is not None,
                github_connected=candidate.github_username is not None,
                interview_completed=False,
                education_filled=candidate.university is not None or candidate.major is not None,
                transcript_uploaded=candidate.courses is not None and len(candidate.courses) > 0,
            )

            # Determine status
            status_str = "profile_only"
            if existing_profile:
                status_str = existing_profile.status.value if existing_profile.status else "pending"

            # Build profile-based score breakdown
            profile_score = None
            score_breakdown = None

            # Simple heuristic profile score (async scoring would be called separately)
            if candidate.resume_parsed_data or candidate.github_data:
                # Basic profile score calculation
                base_score = 5.0
                tech_skills = 5.0
                exp_quality = 5.0
                edu_score = 5.0
                github_score = 5.0

                if candidate.resume_parsed_data:
                    parsed = candidate.resume_parsed_data
                    skill_count = len(parsed.get("skills", []))
                    tech_skills = min(5.0 + skill_count * 0.3, 9.0)
                    exp_count = len(parsed.get("experience", []))
                    exp_quality = min(5.0 + exp_count * 1.0, 8.5)

                if candidate.gpa:
                    edu_score = max(1.0, min(5.0 + (candidate.gpa - 3.0) * 2, 9.5))

                if candidate.github_data:
                    repos = candidate.github_data.get("top_repos", candidate.github_data.get("repos", []))
                    contributions = candidate.github_data.get("total_contributions", candidate.github_data.get("totalContributions", 0))
                    github_score = min(5.0 + len(repos) * 0.2 + contributions * 0.01, 9.0)

                # Weighted average
                profile_score = round((tech_skills * 0.3 + exp_quality * 0.25 + edu_score * 0.25 + github_score * 0.2), 2)

                score_breakdown = ScoreBreakdown(
                    technical_skills=round(tech_skills, 2),
                    experience_quality=round(exp_quality, 2),
                    education=round(edu_score, 2),
                    github_activity=round(github_score, 2),
                )

            # Skip if min_score filter and profile_score is below
            if min_score > 0 and (profile_score is None or profile_score < min_score):
                continue

            # Get activities and awards from pre-fetched batch (avoids N+1)
            activities_list = activities_by_candidate_incomplete.get(candidate.id, [])
            activities = [
                ActivitySummary(
                    name=a.activity_name,
                    role=a.role,
                    prestige_tier=a.club.prestige_tier if a.club else None,
                    category=a.club.category if a.club else None,
                )
                for a in activities_list
            ]

            awards_list = awards_by_candidate_incomplete.get(candidate.id, [])
            awards = [
                AwardSummary(
                    name=a.name,
                    issuer=a.issuer,
                    award_type=a.award_type,
                    prestige_tier=a.prestige_tier,
                )
                for a in awards_list
            ]

            # Get GitHub languages
            github_languages = []
            if candidate.github_data:
                langs = candidate.github_data.get("languages", {})
                github_languages = sorted(langs.keys(), key=lambda x: langs.get(x, 0), reverse=True)[:5]

            candidates_result.append(TalentPoolCandidate(
                profile_id=existing_profile.id if existing_profile else None,
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                candidate_email=candidate.email,
                vertical=existing_profile.vertical.value if existing_profile else None,
                role_type=existing_profile.role_type.value if existing_profile else None,
                interview_score=None,
                best_score=None,
                profile_score=profile_score,
                status=status_str,
                completed_at=None,
                skills=skills,
                experience_summary=experience_summary,
                location=location,
                completion_status=completion_status,
                score_breakdown=score_breakdown,
                activities=activities,
                awards=awards,
                university=candidate.university,
                major=candidate.major,
                graduation_year=candidate.graduation_year,
                gpa=candidate.gpa,
                github_username=candidate.github_username,
                github_languages=github_languages,
            ))

    # Sort all candidates: completed interviews first (by best_score), then profile-only (by profile_score)
    def sort_key(c):
        if c.status == "completed":
            return (0, -(c.best_score or 0))
        else:
            return (1, -(c.profile_score or 0))

    candidates_result.sort(key=sort_key)

    # Apply pagination
    total = len(candidates_result)
    paginated = candidates_result[offset:offset + limit]

    return TalentPoolResponse(candidates=paginated, total=total)


@router.get("/talent-pool/candidate/{candidate_id}")
async def get_talent_candidate_detail(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of a talent pool candidate by candidate ID.
    Works for candidates with or without completed interviews.
    Includes full resume data, GitHub data, education, and any interview details.
    Automatically triggers GitHub analysis refresh if stale or missing.
    """
    from ..models.interview import InterviewResponse
    from ..services.scoring import scoring_service

    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Trigger GitHub analysis refresh if stale or missing
    await trigger_github_analysis_if_stale(candidate_id, background_tasks, db)

    # Check if they have any vertical profile
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == candidate_id
    ).order_by(CandidateVerticalProfile.best_score.desc().nulls_last()).first()

    # Build completion status
    completion_status = {
        "resume_uploaded": candidate.resume_url is not None,
        "github_connected": candidate.github_username is not None,
        "interview_completed": profile is not None and profile.status == VerticalProfileStatus.COMPLETED,
        "education_filled": candidate.university is not None or candidate.major is not None,
        "transcript_uploaded": candidate.courses is not None and len(candidate.courses) > 0,
    }

    # Get interview session details if available
    interview_data = None
    if profile and profile.interview_session_id:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == profile.interview_session_id
        ).first()
        if session:
            responses = db.query(InterviewResponse).filter(
                InterviewResponse.session_id == session.id
            ).order_by(InterviewResponse.question_index).all()

            interview_responses = []
            for resp in responses:
                video_url = None
                if resp.video_url:
                    video_url = storage_service.get_signed_url(resp.video_url)

                score_dimensions = None
                if resp.ai_analysis:
                    try:
                        analysis_data = json.loads(resp.ai_analysis) if isinstance(resp.ai_analysis, str) else resp.ai_analysis
                        if "scores" in analysis_data:
                            scores = analysis_data["scores"]
                            score_dimensions = {
                                "communication": scores.get("communication", 0),
                                "problem_solving": scores.get("problem_solving", 0),
                                "domain_knowledge": scores.get("domain_knowledge", 0),
                                "motivation": scores.get("motivation", 0),
                                "culture_fit": scores.get("culture_fit", 0),
                            }
                    except (json.JSONDecodeError, TypeError):
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

    # Calculate profile score if no interview
    profile_score_data = None
    if not (profile and profile.status == VerticalProfileStatus.COMPLETED):
        # Build education data
        education_data = {}
        if candidate.university:
            education_data["university"] = candidate.university
        if candidate.major:
            education_data["major"] = candidate.major
        if candidate.gpa:
            education_data["gpa"] = candidate.gpa
        if candidate.graduation_year:
            education_data["graduation_year"] = candidate.graduation_year
        if candidate.courses:
            education_data["courses"] = candidate.courses

        # Get profile score (use heuristic for now, async scoring would be called separately)
        if candidate.resume_parsed_data or candidate.github_data or education_data:
            base_score = 5.0
            breakdown = {}

            if candidate.resume_parsed_data:
                parsed = candidate.resume_parsed_data
                skill_count = len(parsed.get("skills", []))
                breakdown["technical_skills"] = min(5.0 + skill_count * 0.3, 9.0)
                exp_count = len(parsed.get("experience", []))
                breakdown["experience_quality"] = min(5.0 + exp_count * 1.0, 8.5)

            if candidate.gpa:
                breakdown["education"] = max(1.0, min(5.0 + (candidate.gpa - 3.0) * 2, 9.5))

            if candidate.github_data:
                repos = candidate.github_data.get("top_repos", candidate.github_data.get("repos", []))
                contributions = candidate.github_data.get("total_contributions", candidate.github_data.get("totalContributions", 0))
                breakdown["github_activity"] = min(5.0 + len(repos) * 0.2 + contributions * 0.01, 9.0)

            # Calculate weighted average
            weights = {"technical_skills": 0.3, "experience_quality": 0.25, "education": 0.25, "github_activity": 0.2}
            total_weight = sum(weights[k] for k in breakdown if k in weights)
            if total_weight > 0:
                profile_score = sum(breakdown.get(k, 5.0) * weights.get(k, 0) for k in weights) / total_weight

                # Generate strengths and concerns based on scores
                strengths = []
                concerns = []

                tech_score = breakdown.get("technical_skills", 5.0)
                if tech_score >= 7.5:
                    skill_count = len((candidate.resume_parsed_data or {}).get("skills", []))
                    strengths.append(f"Strong technical skill set ({skill_count} skills)")
                elif tech_score < 5.0:
                    concerns.append("Limited technical skills listed")

                exp_score = breakdown.get("experience_quality", 5.0)
                if exp_score >= 7.5:
                    exp_list = (candidate.resume_parsed_data or {}).get("experience", [])
                    if exp_list:
                        strengths.append(f"Solid work experience ({len(exp_list)} positions)")
                elif exp_score < 5.0:
                    concerns.append("Limited work experience")

                edu_score = breakdown.get("education", 5.0)
                if edu_score >= 8.0 and candidate.gpa:
                    strengths.append(f"Strong academic record (GPA: {candidate.gpa:.2f})")
                elif edu_score < 5.0:
                    concerns.append("Academic record could be stronger")

                github_score = breakdown.get("github_activity", 5.0)
                if github_score >= 7.0:
                    strengths.append("Active GitHub contributor")
                elif "github_activity" not in breakdown:
                    concerns.append("No GitHub profile connected")

                profile_score_data = {
                    "score": round(profile_score, 2),
                    "breakdown": {k: round(v, 2) for k, v in breakdown.items()},
                    "strengths": strengths,
                    "concerns": concerns,
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
            "id": profile.id if profile else None,
            "vertical": profile.vertical.value if profile else None,
            "role_type": profile.role_type.value if profile else None,
            "interview_score": profile.interview_score if profile else None,
            "best_score": profile.best_score if profile else None,
            "attempt_count": profile.attempt_count if profile else 0,
            "completed_at": profile.completed_at.isoformat() if profile and profile.completed_at else None,
            "status": profile.status.value if profile else "no_profile",
        },
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "university": candidate.university,
            "major": candidate.major,
            "graduation_year": candidate.graduation_year,
            "gpa": candidate.gpa,
            "resume_url": storage_service.get_signed_url(candidate.resume_url, expiration=3600) if candidate.resume_url and not candidate.resume_url.startswith('http') else candidate.resume_url,
            "resume_data": candidate.resume_parsed_data,
            "github_username": candidate.github_username,
            "github_data": candidate.github_data,
        },
        "completion_status": completion_status,
        "profile_score": profile_score_data,
        "interview": interview_data,
        "employer_status": employer_status,
    }


@router.get("/talent-pool/{profile_id}")
async def get_talent_profile_detail(
    profile_id: str,
    background_tasks: BackgroundTasks,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """
    Get detailed view of a talent pool candidate profile.
    Includes full resume data, interview details, and video playback URLs.
    Now also works for candidates without completed interviews.
    Automatically triggers GitHub analysis refresh if stale or missing.
    """
    from ..models.interview import InterviewResponse

    # Try to find by profile_id first
    # Security: Only return completed profiles to employers
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.id == profile_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).first()

    # If not found by profile_id, check if it's a candidate_id
    if not profile:
        candidate = db.query(Candidate).filter(Candidate.id == profile_id).first()
        if candidate:
            # Redirect to the candidate detail endpoint
            return await get_talent_candidate_detail(profile_id, background_tasks, employer, db)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found"
        )

    candidate = profile.candidate

    # Trigger GitHub analysis refresh if stale or missing
    await trigger_github_analysis_if_stale(candidate.id, background_tasks, db)

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

    # Build completion status
    completion_status = {
        "resume_uploaded": candidate.resume_url is not None,
        "github_connected": candidate.github_username is not None,
        "interview_completed": profile.status == VerticalProfileStatus.COMPLETED,
        "education_filled": candidate.university is not None or candidate.major is not None,
        "transcript_uploaded": candidate.courses is not None and len(candidate.courses) > 0,
    }

    # Build profile score if no completed interview
    profile_score = None
    if profile.status != VerticalProfileStatus.COMPLETED:
        breakdown = {}
        if candidate.resume_parsed_data:
            parsed = candidate.resume_parsed_data
            skill_count = len(parsed.get("skills", []))
            breakdown["technical_skills"] = min(5.0 + skill_count * 0.3, 9.0)
            exp_count = len(parsed.get("experience", []))
            breakdown["experience_quality"] = min(5.0 + exp_count * 1.0, 8.5)
        if candidate.gpa:
            breakdown["education"] = max(1.0, min(5.0 + (candidate.gpa - 3.0) * 2, 9.5))
        if candidate.github_data:
            repos = candidate.github_data.get("top_repos", candidate.github_data.get("repos", []))
            contributions = candidate.github_data.get("total_contributions", candidate.github_data.get("totalContributions", 0))
            breakdown["github_activity"] = min(5.0 + len(repos) * 0.2 + contributions * 0.01, 9.0)
        if breakdown:
            weights = {"technical_skills": 0.3, "experience_quality": 0.25, "education": 0.25, "github_activity": 0.2}
            total_weight = sum(weights.get(k, 0) for k in breakdown)
            if total_weight > 0:
                score = sum(breakdown.get(k, 5.0) * weights.get(k, 0) for k in weights) / total_weight

                # Generate strengths and concerns
                strengths = []
                concerns = []

                tech_score = breakdown.get("technical_skills", 5.0)
                if tech_score >= 7.5:
                    skill_count = len((candidate.resume_parsed_data or {}).get("skills", []))
                    strengths.append(f"Strong technical skill set ({skill_count} skills)")
                elif tech_score < 5.0:
                    concerns.append("Limited technical skills listed")

                exp_score = breakdown.get("experience_quality", 5.0)
                if exp_score >= 7.5:
                    exp_list = (candidate.resume_parsed_data or {}).get("experience", [])
                    if exp_list:
                        strengths.append(f"Solid work experience ({len(exp_list)} positions)")
                elif exp_score < 5.0:
                    concerns.append("Limited work experience")

                edu_score = breakdown.get("education", 5.0)
                if edu_score >= 8.0 and candidate.gpa:
                    strengths.append(f"Strong academic record (GPA: {candidate.gpa:.2f})")
                elif edu_score < 5.0:
                    concerns.append("Academic record could be stronger")

                github_score = breakdown.get("github_activity", 5.0)
                if github_score >= 7.0:
                    strengths.append("Active GitHub contributor")
                elif "github_activity" not in breakdown:
                    concerns.append("No GitHub profile connected")

                profile_score = {
                    "score": round(score, 2),
                    "breakdown": {k: round(v, 2) for k, v in breakdown.items()},
                    "strengths": strengths,
                    "concerns": concerns,
                }

    return {
        "profile": {
            "id": profile.id,
            "vertical": profile.vertical.value,
            "role_type": profile.role_type.value,
            "interview_score": profile.interview_score,
            "best_score": profile.best_score,
            "total_interviews": profile.total_interviews,
            "completed_at": profile.completed_at.isoformat() if profile.completed_at else None,
            "status": profile.status.value if profile.status else "pending",
        },
        "candidate": {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "university": candidate.university,
            "major": candidate.major,
            "graduation_year": candidate.graduation_year,
            "gpa": candidate.gpa,
            "resume_url": storage_service.get_signed_url(candidate.resume_url, expiration=3600) if candidate.resume_url and not candidate.resume_url.startswith('http') else candidate.resume_url,
            "resume_data": candidate.resume_parsed_data,
            "github_username": candidate.github_username,
            "github_data": candidate.github_data,
        },
        "completion_status": completion_status,
        "profile_score": profile_score,
        "interview": interview_data,
        "employer_status": employer_status,
    }


class TalentPoolStatusUpdate(BaseModel):
    """Request body for updating talent pool candidate status."""
    status: str  # CONTACTED, IN_REVIEW, WATCHLIST, SHORTLISTED, REJECTED, HIRED
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


# ============================================================================
# CANDIDATE NOTES
# ============================================================================

from ..models.candidate_note import CandidateNote
from pydantic import BaseModel, Field


class CandidateNoteCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CandidateNoteUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class CandidateNoteResponse(BaseModel):
    id: str
    employer_id: str
    candidate_id: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/candidates/{candidate_id}/notes")
async def list_candidate_notes(
    candidate_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    List all notes for a candidate by the current employer.
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    notes = db.query(CandidateNote).filter(
        CandidateNote.employer_id == employer.id,
        CandidateNote.candidate_id == candidate_id
    ).order_by(CandidateNote.created_at.desc()).all()

    return {
        "notes": [CandidateNoteResponse.model_validate(note) for note in notes],
        "total": len(notes),
    }


@router.post("/candidates/{candidate_id}/notes", response_model=CandidateNoteResponse)
async def create_candidate_note(
    candidate_id: str,
    data: CandidateNoteCreate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Add a private note on a candidate.
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    note = CandidateNote(
        employer_id=employer.id,
        candidate_id=candidate_id,
        content=data.content,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return CandidateNoteResponse.model_validate(note)


@router.put("/candidates/{candidate_id}/notes/{note_id}", response_model=CandidateNoteResponse)
async def update_candidate_note(
    candidate_id: str,
    note_id: str,
    data: CandidateNoteUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Update a note on a candidate.
    """
    note = db.query(CandidateNote).filter(
        CandidateNote.id == note_id,
        CandidateNote.employer_id == employer.id,
        CandidateNote.candidate_id == candidate_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    note.content = data.content
    db.commit()
    db.refresh(note)

    return CandidateNoteResponse.model_validate(note)


@router.delete("/candidates/{candidate_id}/notes/{note_id}")
async def delete_candidate_note(
    candidate_id: str,
    note_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Delete a note on a candidate.
    """
    note = db.query(CandidateNote).filter(
        CandidateNote.id == note_id,
        CandidateNote.employer_id == employer.id,
        CandidateNote.candidate_id == candidate_id
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    db.delete(note)
    db.commit()

    return {"success": True, "message": "Note deleted"}


# ============================================================================
# PROFILE SHARING (GTM)
# ============================================================================

@router.post("/talent-pool/{candidate_id}/generate-link")
async def generate_candidate_profile_link(
    candidate_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Generate a shareable magic link for a candidate's profile.
    Link expires in 7 days and tracks view count.

    Employers can share this link with team members or other stakeholders
    without requiring them to create accounts.
    """
    from ..models.profile_token import ProfileToken
    from datetime import timedelta
    import secrets

    # Verify candidate exists and opted in to sharing
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    if not candidate.opted_in_to_sharing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This candidate has not opted in to profile sharing"
        )

    # Generate secure random token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    # Create profile token
    profile_token = ProfileToken(
        id=generate_cuid("pt"),
        token=token,
        candidate_id=candidate_id,
        created_by_id=employer.id,
        created_by_type="employer",
        expires_at=expires_at,
    )

    db.add(profile_token)
    db.commit()
    db.refresh(profile_token)

    logger.info(f"Profile link generated: candidate={candidate_id}, employer={employer.id}, token={profile_token.id}")

    return {
        "success": True,
        "token": token,
        "candidate_id": candidate_id,
        "expires_at": expires_at.isoformat(),
        "share_url": f"/talent/{candidate_id}?token={token}",  # Frontend will prepend base URL
    }


@router.get("/talent-pool/{candidate_id}/profile-links")
async def get_candidate_profile_links(
    candidate_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Get all profile links generated by this employer for a candidate.
    Shows active and expired links with usage stats.
    """
    from ..models.profile_token import ProfileToken

    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get all tokens created by this employer for this candidate
    tokens = db.query(ProfileToken).filter(
        ProfileToken.candidate_id == candidate_id,
        ProfileToken.created_by_id == employer.id
    ).order_by(ProfileToken.created_at.desc()).all()

    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate.name,
        "links": [
            {
                "id": t.id,
                "token": t.token,
                "share_url": f"/talent/{candidate_id}?token={t.token}",
                "expires_at": t.expires_at.isoformat(),
                "is_expired": t.expires_at < datetime.utcnow(),
                "view_count": t.view_count,
                "last_viewed_at": t.last_viewed_at.isoformat() if t.last_viewed_at else None,
                "created_at": t.created_at.isoformat(),
            }
            for t in tokens
        ],
    }


# ============================================================================
# INTERVIEW SCHEDULING (Google Calendar Integration)
# ============================================================================

from ..models.scheduled_interview import ScheduledInterview, InterviewType, ScheduledInterviewStatus
from ..schemas.scheduled_interview import (
    ScheduleInterviewRequest,
    RescheduleInterviewRequest,
    ScheduledInterviewResponse,
    ScheduleInterviewSuccessResponse,
    ScheduledInterviewListResponse,
    CancelInterviewResponse,
    RescheduleInterviewResponse,
)
from ..services.calendar import calendar_service
from datetime import timezone as tz


def _build_interview_response(interview: ScheduledInterview, db: Session) -> ScheduledInterviewResponse:
    """Helper to build a ScheduledInterviewResponse from a model."""
    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    job = db.query(Job).filter(Job.id == interview.job_id).first() if interview.job_id else None

    return ScheduledInterviewResponse(
        id=interview.id,
        employer_id=interview.employer_id,
        candidate_id=interview.candidate_id,
        candidate_name=candidate.name if candidate else None,
        candidate_email=candidate.email if candidate else None,
        job_id=interview.job_id,
        job_title=job.title if job else None,
        title=interview.title,
        description=interview.description,
        interview_type=interview.interview_type.value if interview.interview_type else "other",
        scheduled_at=interview.scheduled_at,
        duration_minutes=interview.duration_minutes,
        timezone=interview.timezone,
        google_event_id=interview.google_event_id,
        google_meet_link=interview.google_meet_link,
        calendar_link=interview.calendar_link,
        additional_attendees=interview.additional_attendees,
        status=interview.status.value if interview.status else "pending",
        employer_notes=interview.employer_notes,
        rescheduled_to_id=interview.rescheduled_to_id,
        created_at=interview.created_at,
        updated_at=interview.updated_at,
    )


@router.post("/talent-pool/{profile_id}/schedule-interview", response_model=ScheduleInterviewSuccessResponse)
async def schedule_interview_with_candidate(
    profile_id: str,
    data: ScheduleInterviewRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Schedule an interview with a candidate from the talent pool.
    Creates a Google Calendar event with Google Meet link and sends invites.

    Requires the employer to have connected their Google Calendar.
    """
    # Check if employer has calendar connected
    if not employer.google_calendar_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect your Google Calendar first to schedule interviews"
        )

    # Find the candidate - try profile ID first, then candidate ID
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.id == profile_id
    ).first()

    if profile:
        candidate = profile.candidate
    else:
        # Try as candidate ID
        candidate = db.query(Candidate).filter(Candidate.id == profile_id).first()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )

    # Verify job belongs to employer if provided
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

    # Validate interview type
    try:
        interview_type = InterviewType(data.interview_type)
    except ValueError:
        interview_type = InterviewType.OTHER

    # Generate title if not provided
    title = data.title
    if not title:
        type_labels = {
            "phone_screen": "Phone Screen",
            "technical": "Technical Interview",
            "behavioral": "Behavioral Interview",
            "culture_fit": "Culture Fit Interview",
            "final": "Final Interview",
            "other": "Interview",
        }
        type_label = type_labels.get(data.interview_type, "Interview")
        title = f"{type_label} with {candidate.name} - {employer.company_name}"
        if job:
            title = f"{type_label}: {job.title} - {candidate.name}"

    # Build attendee list
    attendee_emails = [candidate.email]
    if data.additional_attendees:
        attendee_emails.extend(data.additional_attendees)

    # Calculate end time
    end_time = data.scheduled_at + timedelta(minutes=data.duration_minutes)

    # Build description
    description = data.description or ""
    if job:
        description = f"Position: {job.title}\n\n{description}"
    description = f"Interview scheduled via Pathway\n\nCandidate: {candidate.name}\nCompany: {employer.company_name}\n\n{description}"

    # Create Google Calendar event with Meet link
    google_event_id = None
    google_meet_link = None
    calendar_link = None

    try:
        event_result = await calendar_service.create_meeting_event(
            encrypted_access_token=employer.google_calendar_token,
            title=title,
            description=description,
            start_time=data.scheduled_at,
            end_time=end_time,
            attendee_emails=attendee_emails,
            timezone=data.timezone,
        )
        google_event_id = event_result.get("event_id")
        google_meet_link = event_result.get("hangout_link")
        calendar_link = event_result.get("html_link")
    except ValueError as e:
        # Token might be expired, try refreshing
        if "Invalid" in str(e) or "401" in str(e):
            if employer.google_calendar_refresh_token:
                try:
                    new_tokens = await calendar_service.refresh_access_token(
                        employer.google_calendar_refresh_token
                    )
                    employer.google_calendar_token = new_tokens["access_token"]
                    db.commit()

                    # Retry with new token
                    event_result = await calendar_service.create_meeting_event(
                        encrypted_access_token=employer.google_calendar_token,
                        title=title,
                        description=description,
                        start_time=data.scheduled_at,
                        end_time=end_time,
                        attendee_emails=attendee_emails,
                        timezone=data.timezone,
                    )
                    google_event_id = event_result.get("event_id")
                    google_meet_link = event_result.get("hangout_link")
                    calendar_link = event_result.get("html_link")
                except Exception as refresh_error:
                    logger.error(f"Failed to refresh token: {refresh_error}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Calendar authorization expired. Please reconnect your Google Calendar."
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Calendar authorization expired. Please reconnect your Google Calendar."
                )
        else:
            logger.error(f"Failed to create calendar event: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create calendar event: {str(e)}"
            )

    # Create scheduled interview record
    scheduled_interview = ScheduledInterview(
        id=generate_cuid("si"),
        employer_id=employer.id,
        candidate_id=candidate.id,
        job_id=data.job_id,
        title=title,
        description=data.description,
        interview_type=interview_type,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
        timezone=data.timezone,
        google_event_id=google_event_id,
        google_meet_link=google_meet_link,
        calendar_link=calendar_link,
        additional_attendees=data.additional_attendees,
        status=ScheduledInterviewStatus.PENDING,
        employer_notes=data.employer_notes,
    )

    db.add(scheduled_interview)
    db.commit()
    db.refresh(scheduled_interview)

    logger.info(f"Interview scheduled: {scheduled_interview.id} for candidate {candidate.id} by employer {employer.id}")

    return ScheduleInterviewSuccessResponse(
        success=True,
        interview=_build_interview_response(scheduled_interview, db),
        google_meet_link=google_meet_link,
        calendar_link=calendar_link,
        message="Interview scheduled successfully. Calendar invites have been sent.",
    )


@router.get("/scheduled-interviews", response_model=ScheduledInterviewListResponse)
async def list_scheduled_interviews(
    status_filter: Optional[str] = None,
    job_id: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    List all scheduled interviews for this employer.
    Can filter by status, job, and date range.
    """
    query = db.query(ScheduledInterview).filter(
        ScheduledInterview.employer_id == employer.id
    )

    # Apply filters
    if status_filter:
        try:
            status_enum = ScheduledInterviewStatus(status_filter)
            query = query.filter(ScheduledInterview.status == status_enum)
        except ValueError:
            pass  # Ignore invalid status

    if job_id:
        query = query.filter(ScheduledInterview.job_id == job_id)

    if from_date:
        query = query.filter(ScheduledInterview.scheduled_at >= from_date)

    if to_date:
        query = query.filter(ScheduledInterview.scheduled_at <= to_date)

    # Get total count
    total = query.count()

    # Order by scheduled time (upcoming first)
    interviews = query.order_by(ScheduledInterview.scheduled_at.desc()).offset(offset).limit(limit).all()

    return ScheduledInterviewListResponse(
        interviews=[_build_interview_response(i, db) for i in interviews],
        total=total,
    )


@router.get("/scheduled-interviews/{interview_id}", response_model=ScheduledInterviewResponse)
async def get_scheduled_interview(
    interview_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """Get details of a specific scheduled interview."""
    interview = db.query(ScheduledInterview).filter(
        ScheduledInterview.id == interview_id,
        ScheduledInterview.employer_id == employer.id,
    ).first()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled interview not found"
        )

    return _build_interview_response(interview, db)


@router.delete("/scheduled-interviews/{interview_id}", response_model=CancelInterviewResponse)
async def cancel_scheduled_interview(
    interview_id: str,
    notify_attendees: bool = True,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Cancel a scheduled interview.
    Deletes the Google Calendar event and notifies attendees.
    """
    interview = db.query(ScheduledInterview).filter(
        ScheduledInterview.id == interview_id,
        ScheduledInterview.employer_id == employer.id,
    ).first()

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled interview not found"
        )

    if interview.status == ScheduledInterviewStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already cancelled"
        )

    # Cancel Google Calendar event if exists
    if interview.google_event_id and employer.google_calendar_token:
        try:
            await calendar_service.cancel_event(
                encrypted_access_token=employer.google_calendar_token,
                event_id=interview.google_event_id,
                send_updates=notify_attendees,
            )
        except Exception as e:
            logger.warning(f"Failed to cancel calendar event: {e}")
            # Continue with database update even if calendar deletion fails

    # Update status
    interview.status = ScheduledInterviewStatus.CANCELLED
    db.commit()

    logger.info(f"Interview cancelled: {interview_id} by employer {employer.id}")

    return CancelInterviewResponse(
        success=True,
        message="Interview cancelled successfully",
        interview_id=interview_id,
    )


@router.post("/scheduled-interviews/{interview_id}/reschedule", response_model=RescheduleInterviewResponse)
async def reschedule_interview(
    interview_id: str,
    data: RescheduleInterviewRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Reschedule an existing interview.
    Creates a new calendar event, cancels the old one, and links them.
    """
    old_interview = db.query(ScheduledInterview).filter(
        ScheduledInterview.id == interview_id,
        ScheduledInterview.employer_id == employer.id,
    ).first()

    if not old_interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled interview not found"
        )

    if old_interview.status in [ScheduledInterviewStatus.CANCELLED, ScheduledInterviewStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reschedule a {old_interview.status.value} interview"
        )

    # Check calendar connection
    if not employer.google_calendar_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please connect your Google Calendar to reschedule"
        )

    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == old_interview.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Use new values or fall back to old ones
    duration = data.duration_minutes or old_interview.duration_minutes
    timezone_str = data.timezone or old_interview.timezone
    end_time = data.scheduled_at + timedelta(minutes=duration)

    # Build attendee list
    attendee_emails = [candidate.email]
    if old_interview.additional_attendees:
        attendee_emails.extend(old_interview.additional_attendees)

    # Update description with reschedule reason
    description = old_interview.description or ""
    if data.reason:
        description = f"[RESCHEDULED]\nReason: {data.reason}\n\n{description}"

    # Create new calendar event
    try:
        event_result = await calendar_service.create_meeting_event(
            encrypted_access_token=employer.google_calendar_token,
            title=old_interview.title,
            description=description,
            start_time=data.scheduled_at,
            end_time=end_time,
            attendee_emails=attendee_emails,
            timezone=timezone_str,
        )
    except ValueError as e:
        logger.error(f"Failed to create rescheduled calendar event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calendar event for rescheduled interview"
        )

    # Cancel old calendar event
    if old_interview.google_event_id:
        try:
            await calendar_service.cancel_event(
                encrypted_access_token=employer.google_calendar_token,
                event_id=old_interview.google_event_id,
                send_updates=True,
            )
        except Exception as e:
            logger.warning(f"Failed to cancel old calendar event: {e}")

    # Create new interview record
    new_interview = ScheduledInterview(
        id=generate_cuid("si"),
        employer_id=employer.id,
        candidate_id=old_interview.candidate_id,
        job_id=old_interview.job_id,
        title=old_interview.title,
        description=description,
        interview_type=old_interview.interview_type,
        scheduled_at=data.scheduled_at,
        duration_minutes=duration,
        timezone=timezone_str,
        google_event_id=event_result.get("event_id"),
        google_meet_link=event_result.get("hangout_link"),
        calendar_link=event_result.get("html_link"),
        additional_attendees=old_interview.additional_attendees,
        status=ScheduledInterviewStatus.PENDING,
        employer_notes=old_interview.employer_notes,
    )

    db.add(new_interview)

    # Update old interview
    old_interview.status = ScheduledInterviewStatus.RESCHEDULED
    old_interview.rescheduled_to_id = new_interview.id

    db.commit()
    db.refresh(new_interview)
    db.refresh(old_interview)

    logger.info(f"Interview rescheduled: {interview_id} -> {new_interview.id} by employer {employer.id}")

    return RescheduleInterviewResponse(
        success=True,
        message="Interview rescheduled successfully",
        old_interview=_build_interview_response(old_interview, db),
        new_interview=_build_interview_response(new_interview, db),
    )


# ============================================================================
# SKILL GAP ANALYSIS & ML-POWERED MATCHING
# ============================================================================

from ..services.skill_gap import skill_gap_service, SkillGapAnalysis
from ..schemas.employer import (
    SkillGapAnalysisRequest,
    SkillGapAnalysisResponse,
    EnhancedMatchRequest,
    EnhancedMatchResponse,
    CandidateRankingRequest,
    CandidateRankingResponse,
    RankedCandidate,
)
from dataclasses import asdict


@router.post("/skill-gap/analyze", response_model=SkillGapAnalysisResponse)
async def analyze_skill_gap(
    data: SkillGapAnalysisRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Analyze the skill gap between a candidate and job requirements.

    Returns detailed analysis including:
    - Overall match score
    - Skill-by-skill matching with proficiency levels
    - Category coverage
    - Learning priorities
    - Alternative/transferable skills
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get job requirements
    job_requirements = data.job_requirements
    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        job_requirements = job.required_skills or []

    if not job_requirements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No job requirements provided"
        )

    # Get candidate skills from resume
    candidate_skills = []
    parsed_resume = None

    if candidate.resume_parsed_data:
        try:
            resume_data = candidate.resume_parsed_data if isinstance(candidate.resume_parsed_data, dict) else json.loads(candidate.resume_parsed_data)
            candidate_skills = resume_data.get('skills', [])
            # Convert to ParsedResume for skill gap service
            from ..schemas.candidate import ParsedResume, ExperienceItem, ProjectItem
            parsed_resume = ParsedResume(
                name=resume_data.get('name'),
                email=resume_data.get('email'),
                skills=candidate_skills,
                experience=[
                    ExperienceItem(**exp) if isinstance(exp, dict) else exp
                    for exp in resume_data.get('experience', [])
                ],
                projects=[
                    ProjectItem(**proj) if isinstance(proj, dict) else proj
                    for proj in resume_data.get('projects', [])
                ],
            )
        except Exception as e:
            logger.warning(f"Failed to parse resume data: {e}")

    # Get GitHub data
    github_data = None
    if candidate.github_data:
        try:
            github_data = candidate.github_data if isinstance(candidate.github_data, dict) else json.loads(candidate.github_data)
        except Exception:
            pass

    # Run skill gap analysis
    analysis = skill_gap_service.analyze_skill_gap(
        candidate_skills=candidate_skills,
        job_requirements=job_requirements,
        parsed_resume=parsed_resume,
        github_data=github_data,
    )

    logger.info(f"Skill gap analysis: candidate={data.candidate_id}, score={analysis.overall_match_score}")

    return SkillGapAnalysisResponse(
        overall_match_score=analysis.overall_match_score,
        total_requirements=analysis.total_requirements,
        matched_requirements=analysis.matched_requirements,
        critical_gaps=analysis.critical_gaps,
        skill_matches=analysis.skill_matches,
        category_coverage=analysis.category_coverage,
        proficiency_distribution=analysis.proficiency_distribution,
        avg_proficiency_score=analysis.avg_proficiency_score,
        learning_priorities=analysis.learning_priorities,
        alternative_skills=analysis.alternative_skills,
        transferable_skills=analysis.transferable_skills,
        bonus_skills=analysis.bonus_skills,
        strongest_areas=analysis.strongest_areas,
    )


@router.post("/enhanced-match", response_model=EnhancedMatchResponse)
async def get_enhanced_match(
    data: EnhancedMatchRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Get ML-powered enhanced match score for a candidate-job pair.

    Includes:
    - Traditional scores (interview, skills, experience, location)
    - ML-powered scores (GitHub signal, education, growth trajectory)
    - Hiring recommendation
    - Top strengths and areas for growth
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get job info
    job_title = data.job_title or "Software Engineer"
    job_requirements = data.job_requirements or []
    job_vertical = data.job_vertical

    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if job:
            job_title = job.title
            job_requirements = job.required_skills or []
            job_vertical = job.vertical.value if job.vertical else None

    # Get candidate's interview score
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == data.candidate_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
    ).order_by(CandidateVerticalProfile.best_score.desc().nulls_last()).first()

    interview_score = profile.best_score if profile else 5.0

    # Get candidate data
    candidate_data = None
    if candidate.resume_parsed_data:
        try:
            candidate_data = candidate.resume_parsed_data if isinstance(candidate.resume_parsed_data, dict) else json.loads(candidate.resume_parsed_data)
        except Exception:
            pass

    # Get GitHub data
    github_data = None
    if candidate.github_data:
        try:
            github_data = candidate.github_data if isinstance(candidate.github_data, dict) else json.loads(candidate.github_data)
        except Exception:
            pass

    # Get education data
    education_data = {
        "university": candidate.university,
        "major": candidate.major,
        "gpa": candidate.gpa,
        "graduation_year": candidate.graduation_year,
    }

    # Get interview history for trajectory
    interview_history = []
    sessions = db.query(InterviewSession).filter(
        InterviewSession.candidate_id == data.candidate_id,
        InterviewSession.status == InterviewStatus.COMPLETED,
    ).order_by(InterviewSession.completed_at.asc()).all()

    for session in sessions:
        interview_history.append({
            "overall_score": session.total_score,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        })

    # Calculate enhanced match
    result = await matching_service.calculate_enhanced_match(
        interview_score=interview_score,
        candidate_data=candidate_data,
        job_title=job_title,
        job_requirements=job_requirements,
        job_location=None,  # Can be added later
        job_vertical=job_vertical,
        github_data=github_data,
        education_data=education_data,
        interview_history=interview_history,
    )

    logger.info(f"Enhanced match: candidate={data.candidate_id}, score={result.overall_match_score}")

    return EnhancedMatchResponse(
        overall_match_score=result.overall_match_score,
        interview_score=result.interview_score,
        skills_match_score=result.skills_match_score,
        experience_match_score=result.experience_match_score,
        github_signal_score=result.github_signal_score,
        education_score=result.education_score,
        growth_trajectory_score=result.growth_trajectory_score,
        location_match=result.location_match,
        factors=result.factors,
        skill_gap_summary=result.skill_gap_summary,
        top_strengths=result.top_strengths,
        areas_for_growth=result.areas_for_growth,
        hiring_recommendation=result.hiring_recommendation,
        confidence_score=result.confidence_score,
        ai_reasoning=result.ai_reasoning,
    )


@router.post("/candidates/rank", response_model=CandidateRankingResponse)
async def rank_candidates_for_job(
    data: CandidateRankingRequest,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Rank all candidates for a specific job using ML-powered matching.

    Returns candidates sorted by overall match score with quick insights.
    """
    # Get job
    job = db.query(Job).filter(
        Job.id == data.job_id,
        Job.employer_id == employer.id,
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Get candidates with completed interviews in relevant vertical
    candidates_query = db.query(Candidate).join(
        CandidateVerticalProfile,
        Candidate.id == CandidateVerticalProfile.candidate_id
    ).filter(
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
    )

    # Filter by vertical if job has one
    if job.vertical:
        candidates_query = candidates_query.filter(
            CandidateVerticalProfile.vertical == job.vertical
        )

    candidates = candidates_query.all()

    # Calculate match scores for each candidate
    ranked_candidates = []

    for candidate in candidates:
        # Get best interview score
        profile = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.candidate_id == candidate.id,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
        ).order_by(CandidateVerticalProfile.best_score.desc().nulls_last()).first()

        interview_score = profile.best_score if profile else 5.0

        # Get candidate data
        candidate_data = None
        if candidate.resume_parsed_data:
            try:
                candidate_data = candidate.resume_parsed_data if isinstance(candidate.resume_parsed_data, dict) else json.loads(candidate.resume_parsed_data)
            except Exception:
                pass

        # Get GitHub data
        github_data = None
        if candidate.github_data:
            try:
                github_data = candidate.github_data if isinstance(candidate.github_data, dict) else json.loads(candidate.github_data)
            except Exception:
                pass

        # Get education data
        education_data = {
            "university": candidate.university,
            "major": candidate.major,
            "gpa": candidate.gpa,
        }

        # Calculate enhanced match
        result = await matching_service.calculate_enhanced_match(
            interview_score=interview_score,
            candidate_data=candidate_data,
            job_title=job.title,
            job_requirements=job.required_skills or [],
            job_vertical=job.vertical.value if job.vertical else None,
            github_data=github_data,
            education_data=education_data,
            interview_history=None,  # Skip trajectory for bulk ranking
        )

        # Filter by minimum score
        if result.overall_match_score >= data.min_score:
            # Get skill gaps if requested
            skill_gaps = []
            if data.include_skill_gap:
                skill_gaps = result.skill_gap_summary.get('missing_skills', [])[:3]

            ranked_candidates.append(RankedCandidate(
                candidate_id=candidate.id,
                name=candidate.name,
                email=candidate.email,
                university=candidate.university,
                graduation_year=candidate.graduation_year,
                overall_match_score=result.overall_match_score,
                interview_score=interview_score,
                skills_match_score=result.skills_match_score,
                github_signal_score=result.github_signal_score,
                top_strengths=result.top_strengths[:2],
                skill_gaps=skill_gaps,
                hiring_recommendation=result.hiring_recommendation,
            ))

    # Sort by match score
    ranked_candidates.sort(key=lambda c: c.overall_match_score, reverse=True)

    # Apply pagination
    total = len(ranked_candidates)
    ranked_candidates = ranked_candidates[data.offset:data.offset + data.limit]

    # Calculate average score
    avg_score = sum(c.overall_match_score for c in ranked_candidates) / len(ranked_candidates) if ranked_candidates else 0

    logger.info(f"Ranked {total} candidates for job {data.job_id}")

    return CandidateRankingResponse(
        job_id=data.job_id,
        job_title=job.title,
        candidates=ranked_candidates,
        total=total,
        average_match_score=round(avg_score, 1),
    )


# ============================================================================
# ORGANIZATION ENDPOINTS
# ============================================================================

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from organization name."""
    import re
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = name.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug[:50]  # Limit length


@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Create a new organization and set the current employer as owner."""
    # Generate unique slug
    base_slug = generate_slug(data.name)
    slug = base_slug
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    org = Organization(
        id=generate_cuid("org"),
        name=data.name,
        slug=slug,
        website=data.website,
        industry=data.industry,
        company_size=data.company_size,
        description=data.description,
    )
    db.add(org)
    db.flush()

    # Add current employer as owner
    membership = OrganizationMember(
        id=generate_cuid("om"),
        organization_id=org.id,
        employer_id=employer.id,
        role=OrganizationRole.OWNER,
    )
    db.add(membership)
    db.commit()
    db.refresh(org)

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        created_at=org.created_at,
        member_count=1,
    )


@router.get("/organizations", response_model=OrganizationList)
async def list_my_organizations(
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List organizations the current employer belongs to."""
    memberships = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).all()

    organizations = []
    for m in memberships:
        org = m.organization
        member_count = db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org.id
        ).count()
        organizations.append(OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            logo_url=org.logo_url,
            website=org.website,
            industry=org.industry,
            company_size=org.company_size,
            description=org.description,
            plan=org.plan,
            created_at=org.created_at,
            member_count=member_count,
        ))

    return OrganizationList(organizations=organizations, total=len(organizations))


@router.get("/organizations/{org_id}", response_model=OrganizationDetailResponse)
async def get_organization(
    org_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Get organization details with members list."""
    # Verify membership
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found or you are not a member"
        )

    org = membership.organization

    # Get all members
    members = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id
    ).all()

    member_list = []
    for m in members:
        emp = m.employer
        member_list.append(OrganizationMemberResponse(
            id=m.id,
            employer_id=emp.id,
            employer_name=emp.name,
            employer_email=emp.email,
            role=m.role.value,
            joined_at=m.joined_at,
        ))

    return OrganizationDetailResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        created_at=org.created_at,
        member_count=len(members),
        members=member_list,
    )


@router.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Update organization details. Requires admin or owner role."""
    # Verify membership with admin/owner role
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id,
        OrganizationMember.role.in_([OrganizationRole.OWNER, OrganizationRole.ADMIN])
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this organization"
        )

    org = membership.organization

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)

    db.commit()
    db.refresh(org)

    member_count = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id
    ).count()

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        created_at=org.created_at,
        member_count=member_count,
    )


@router.post("/organizations/{org_id}/invites", response_model=OrganizationInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_to_organization(
    org_id: str,
    data: OrganizationInviteCreate,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Invite someone to join the organization. Requires admin or owner role."""
    # Verify membership with admin/owner role
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id,
        OrganizationMember.role.in_([OrganizationRole.OWNER, OrganizationRole.ADMIN])
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite members"
        )

    org = membership.organization

    # Check if already a member
    existing_member = db.query(OrganizationMember).join(Employer).filter(
        OrganizationMember.organization_id == org_id,
        Employer.email == data.email
    ).first()

    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This person is already a member of the organization"
        )

    # Check for existing pending invite
    existing_invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.organization_id == org_id,
        OrganizationInvite.email == data.email,
        OrganizationInvite.status == InviteStatus.PENDING
    ).first()

    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An invite is already pending for this email"
        )

    # Create invite
    invite = OrganizationInvite(
        id=generate_cuid("oi"),
        organization_id=org_id,
        email=data.email,
        role=OrganizationRole(data.role),
        token=secrets.token_urlsafe(32),
        invited_by_id=employer.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    # TODO: Send invite email

    return OrganizationInviteResponse(
        id=invite.id,
        organization_id=org_id,
        organization_name=org.name,
        email=invite.email,
        role=invite.role.value,
        status=invite.status.value,
        expires_at=invite.expires_at,
        created_at=invite.created_at,
    )


@router.get("/organizations/{org_id}/invites", response_model=list[OrganizationInviteResponse])
async def list_organization_invites(
    org_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """List pending invites for an organization. Requires admin or owner role."""
    # Verify membership with admin/owner role
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id,
        OrganizationMember.role.in_([OrganizationRole.OWNER, OrganizationRole.ADMIN])
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view invites"
        )

    org = membership.organization

    invites = db.query(OrganizationInvite).filter(
        OrganizationInvite.organization_id == org_id,
        OrganizationInvite.status == InviteStatus.PENDING
    ).order_by(OrganizationInvite.created_at.desc()).all()

    return [
        OrganizationInviteResponse(
            id=inv.id,
            organization_id=org_id,
            organization_name=org.name,
            email=inv.email,
            role=inv.role.value,
            status=inv.status.value,
            expires_at=inv.expires_at,
            created_at=inv.created_at,
        )
        for inv in invites
    ]


@router.post("/organizations/accept-invite", response_model=OrganizationResponse)
async def accept_organization_invite(
    data: OrganizationInviteAccept,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Accept an organization invite using the token."""
    invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.token == data.token,
        OrganizationInvite.status == InviteStatus.PENDING
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invite"
        )

    # Check if expired
    if invite.expires_at < datetime.utcnow():
        invite.status = InviteStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has expired"
        )

    # Check if email matches
    if invite.email.lower() != employer.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite was sent to a different email address"
        )

    # Check if already a member
    existing_member = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == invite.organization_id,
        OrganizationMember.employer_id == employer.id
    ).first()

    if existing_member:
        invite.status = InviteStatus.ACCEPTED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this organization"
        )

    # Create membership
    membership = OrganizationMember(
        id=generate_cuid("om"),
        organization_id=invite.organization_id,
        employer_id=employer.id,
        role=invite.role,
        invited_by_id=invite.invited_by_id,
    )
    db.add(membership)

    # Update invite status
    invite.status = InviteStatus.ACCEPTED
    invite.accepted_at = datetime.utcnow()

    db.commit()

    org = invite.organization
    member_count = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org.id
    ).count()

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        created_at=org.created_at,
        member_count=member_count,
    )


@router.delete("/organizations/{org_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    org_id: str,
    member_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Remove a member from the organization. Requires admin/owner role."""
    # Verify membership with admin/owner role
    current_membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id,
        OrganizationMember.role.in_([OrganizationRole.OWNER, OrganizationRole.ADMIN])
    ).first()

    if not current_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to remove members"
        )

    # Find member to remove
    target_member = db.query(OrganizationMember).filter(
        OrganizationMember.id == member_id,
        OrganizationMember.organization_id == org_id
    ).first()

    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Cannot remove owner (must transfer ownership first)
    if target_member.role == OrganizationRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the owner. Transfer ownership first."
        )

    db.delete(target_member)
    db.commit()


@router.delete("/organizations/{org_id}/invites/{invite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_organization_invite(
    org_id: str,
    invite_id: str,
    employer: Employer = Depends(get_current_employer),
    db: Session = Depends(get_db)
):
    """Cancel a pending invite. Requires admin/owner role."""
    # Verify membership with admin/owner role
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org_id,
        OrganizationMember.employer_id == employer.id,
        OrganizationMember.role.in_([OrganizationRole.OWNER, OrganizationRole.ADMIN])
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel invites"
        )

    invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.id == invite_id,
        OrganizationInvite.organization_id == org_id,
        OrganizationInvite.status == InviteStatus.PENDING
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )

    invite.status = InviteStatus.CANCELLED
    db.commit()

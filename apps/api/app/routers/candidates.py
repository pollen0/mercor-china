import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timedelta
import uuid

from ..database import get_db
from ..models.candidate import Candidate, CandidateVerticalProfile, VerticalProfileStatus
from ..models.employer import Job, Vertical, RoleType
from ..models.interview import Match, MatchStatus
from ..schemas.candidate import (
    CandidateCreate,
    CandidateLogin,
    CandidateUpdate,
    CandidateResponse,
    CandidateDetailResponse,
    CandidateList,
    CandidateWithToken,
    ResumeParseResult,
    ResumeResponse,
    ParsedResume,
    PersonalizedQuestion,
    GitHubAuthUrlResponse,
    GitHubCallbackRequest,
    GitHubConnectResponse,
    EducationInfo,
    GitHubInfo,
)
from ..services.resume import resume_service
from ..services.storage import storage_service
from ..utils.auth import create_token, get_current_candidate, get_current_employer, get_password_hash, verify_password
from ..utils.rate_limit import limiter, RateLimits
from ..config import settings

logger = logging.getLogger("pathway.candidates")
router = APIRouter()


def generate_cuid() -> str:
    return f"c{uuid.uuid4().hex[:24]}"


@router.post("/", response_model=CandidateWithToken, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new student on Pathway.
    """
    existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Hash the password
    password_hash = get_password_hash(candidate_data.password)

    candidate = Candidate(
        id=generate_cuid(),
        name=candidate_data.name,
        email=candidate_data.email,
        password_hash=password_hash,
        university=candidate_data.university,
        major=candidate_data.major,
        graduation_year=candidate_data.graduation_year,
        target_roles=[],
    )

    try:
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Send verification email
    from .auth import create_verification_for_candidate
    create_verification_for_candidate(candidate, db, background_tasks)

    # Generate token for immediate login after registration
    token = create_token(
        subject=candidate.id,
        token_type="candidate",
        expires_hours=settings.jwt_expiry_hours,
    )

    return CandidateWithToken(
        candidate=CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            target_roles=candidate.target_roles or [],
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            gpa=candidate.gpa,
            github_username=candidate.github_username,
            resume_url=candidate.resume_url,
            created_at=candidate.created_at,
        ),
        token=token,
    )


@router.post("/login", response_model=CandidateWithToken)
async def login_candidate(
    login_data: CandidateLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate a student with email and password.
    Returns student info with JWT token.
    """
    candidate = db.query(Candidate).filter(Candidate.email == login_data.email).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check if candidate has a password (might be GitHub-only user)
    if not candidate.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account was created with GitHub. Please login with GitHub."
        )

    # Verify password
    if not verify_password(login_data.password, candidate.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate token
    token = create_token(
        subject=candidate.id,
        token_type="candidate",
        expires_hours=settings.jwt_expiry_hours,
    )

    return CandidateWithToken(
        candidate=CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            target_roles=candidate.target_roles or [],
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            gpa=candidate.gpa,
            github_username=candidate.github_username,
            resume_url=candidate.resume_url,
            created_at=candidate.created_at,
        ),
        token=token,
    )


@router.get("/", response_model=CandidateList)
async def list_candidates(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    university: Optional[str] = None,
    graduation_year: Optional[int] = None,
    vertical: Optional[str] = None,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """List students in the talent pool (employer only)."""
    query = db.query(Candidate)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter)) |
            (Candidate.university.ilike(search_filter)) |
            (Candidate.major.ilike(search_filter))
        )

    if university:
        query = query.filter(Candidate.university.ilike(f"%{university}%"))

    if graduation_year:
        query = query.filter(Candidate.graduation_year == graduation_year)

    # TODO: Filter by vertical (needs join with vertical profiles)

    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

    return CandidateList(candidates=candidates, total=total)


@router.get("/me", response_model=CandidateResponse)
async def get_current_candidate_profile(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the current authenticated student's profile."""
    return CandidateResponse(
        id=current_candidate.id,
        name=current_candidate.name,
        email=current_candidate.email,
        phone=current_candidate.phone,
        target_roles=current_candidate.target_roles or [],
        university=current_candidate.university,
        major=current_candidate.major,
        graduation_year=current_candidate.graduation_year,
        gpa=current_candidate.gpa,
        bio=current_candidate.bio,
        linkedin_url=current_candidate.linkedin_url,
        portfolio_url=current_candidate.portfolio_url,
        github_username=current_candidate.github_username,
        resume_url=current_candidate.resume_url,
        created_at=current_candidate.created_at,
    )


@router.patch("/me", response_model=CandidateResponse)
async def update_my_profile(
    update_data: CandidateUpdate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Update the current student's profile."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        if hasattr(current_candidate, field):
            setattr(current_candidate, field, value)

    db.commit()
    db.refresh(current_candidate)

    return CandidateResponse(
        id=current_candidate.id,
        name=current_candidate.name,
        email=current_candidate.email,
        phone=current_candidate.phone,
        target_roles=current_candidate.target_roles or [],
        university=current_candidate.university,
        major=current_candidate.major,
        graduation_year=current_candidate.graduation_year,
        gpa=current_candidate.gpa,
        bio=current_candidate.bio,
        linkedin_url=current_candidate.linkedin_url,
        portfolio_url=current_candidate.portfolio_url,
        github_username=current_candidate.github_username,
        resume_url=current_candidate.resume_url,
        created_at=current_candidate.created_at,
    )


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
async def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """Get a student's full profile (employer only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    # Build education info
    education = EducationInfo(
        university=candidate.university,
        major=candidate.major,
        graduation_year=candidate.graduation_year,
        gpa=candidate.gpa,
        courses=candidate.courses,
    ) if candidate.university else None

    # Build GitHub info
    github = None
    if candidate.github_username:
        github_data = candidate.github_data or {}
        github = GitHubInfo(
            username=candidate.github_username,
            connected_at=candidate.github_connected_at,
            top_repos=github_data.get("top_repos"),
            total_repos=github_data.get("total_repos"),
            total_contributions=github_data.get("total_contributions"),
            languages=github_data.get("languages"),
        )

    # Get interview stats
    profiles = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == candidate_id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).all()

    interview_count = len(profiles)
    best_scores = {p.vertical.value: p.best_score for p in profiles if p.best_score}

    return CandidateDetailResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        target_roles=candidate.target_roles or [],
        education=education,
        github=github,
        bio=candidate.bio,
        linkedin_url=candidate.linkedin_url,
        portfolio_url=candidate.portfolio_url,
        resume_url=candidate.resume_url,
        resume_parsed_data=candidate.resume_parsed_data,
        interview_count=interview_count,
        best_scores=best_scores,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
    )


# ==================== RESUME ENDPOINTS ====================

@router.post("/{candidate_id}/resume", response_model=ResumeParseResult)
@limiter.limit(RateLimits.AI_RESUME_PARSE)
async def upload_resume(
    request: Request,
    candidate_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Upload and parse a student's resume.
    Supports PDF and DOCX formats.
    """
    # Verify candidate is uploading their own resume
    if current_candidate.id != candidate_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload your own resume"
        )

    candidate = current_candidate

    # Validate file type
    filename = file.filename or "resume"
    if not (filename.lower().endswith('.pdf') or filename.lower().endswith('.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a PDF or DOCX file"
        )

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    # Check file size (max 10MB)
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size cannot exceed 10MB"
        )

    # Extract text from resume
    try:
        raw_text = await resume_service.extract_text(file_bytes, filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from resume. Please ensure it's not a scanned image."
        )

    # Upload resume file to storage
    try:
        extension = "pdf" if filename.lower().endswith('.pdf') else "docx"
        content_type = "application/pdf" if extension == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        storage_key = f"resumes/{candidate_id}/{uuid.uuid4().hex[:8]}.{extension}"

        # Upload to R2
        from io import BytesIO
        storage_service.client.upload_fileobj(
            BytesIO(file_bytes),
            storage_service.client._bucket_name if hasattr(storage_service.client, '_bucket_name') else "pathway-videos",
            storage_key,
            ExtraArgs={"ContentType": content_type}
        )
        resume_url = storage_key
    except Exception as e:
        logger.error(f"Resume upload error for student {candidate_id}: {e}")
        resume_url = None  # Continue without storage

    # Parse resume with AI
    try:
        parsed_data = await resume_service.parse_resume(raw_text)
    except Exception as e:
        logger.error(f"Resume AI parsing error for student {candidate_id}: {e}")
        parsed_data = ParsedResume()

    # Update candidate record
    candidate.resume_url = resume_url
    candidate.resume_raw_text = raw_text
    candidate.resume_parsed_data = parsed_data.model_dump() if parsed_data else None
    candidate.resume_uploaded_at = datetime.utcnow()

    # Auto-update candidate name if parsed and missing
    if parsed_data.name and not candidate.name:
        candidate.name = parsed_data.name

    db.commit()

    return ResumeParseResult(
        success=True,
        message="Resume uploaded and parsed successfully",
        resume_url=resume_url,
        parsed_data=parsed_data,
        raw_text_preview=raw_text[:500] if raw_text else None
    )


@router.get("/me/resume", response_model=ResumeResponse)
async def get_my_resume(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the current student's resume."""
    parsed_data = None
    if current_candidate.resume_parsed_data:
        try:
            parsed_data = ParsedResume(**current_candidate.resume_parsed_data)
        except Exception:
            pass

    return ResumeResponse(
        candidate_id=current_candidate.id,
        resume_url=current_candidate.resume_url,
        raw_text=current_candidate.resume_raw_text,
        parsed_data=parsed_data,
        uploaded_at=current_candidate.resume_uploaded_at
    )


@router.delete("/me/resume")
async def delete_my_resume(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Delete the current student's resume."""
    current_candidate.resume_url = None
    current_candidate.resume_raw_text = None
    current_candidate.resume_parsed_data = None
    current_candidate.resume_uploaded_at = None

    db.commit()

    return {"success": True, "message": "Resume deleted successfully"}


@router.get("/{candidate_id}/resume", response_model=ResumeResponse)
async def get_resume(
    candidate_id: str,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """Get the parsed resume data for a student (employer only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    parsed_data = None
    if candidate.resume_parsed_data:
        try:
            parsed_data = ParsedResume(**candidate.resume_parsed_data)
        except Exception:
            pass

    return ResumeResponse(
        candidate_id=candidate_id,
        resume_url=candidate.resume_url,
        raw_text=candidate.resume_raw_text,
        parsed_data=parsed_data,
        uploaded_at=candidate.resume_uploaded_at
    )


@router.get("/{candidate_id}/resume/personalized-questions", response_model=list[PersonalizedQuestion])
async def get_personalized_questions(
    candidate_id: str,
    job_id: Optional[str] = None,
    num_questions: int = 3,
    db: Session = Depends(get_db)
):
    """
    Generate personalized interview questions based on the student's resume.
    Optionally provide a job_id for more targeted questions.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    if not candidate.resume_parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student has not uploaded a resume"
        )

    # Get parsed resume
    try:
        parsed_resume = ParsedResume(**candidate.resume_parsed_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume data"
        )

    # Get job info if provided
    job_title = None
    job_requirements = None
    if job_id:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job_title = job.title
            job_requirements = job.requirements

    # Generate personalized questions
    questions = await resume_service.generate_personalized_questions(
        parsed_resume=parsed_resume,
        job_title=job_title,
        job_requirements=job_requirements,
        num_questions=num_questions
    )

    return questions


# ==================== GITHUB OAUTH ENDPOINTS ====================
# TODO: Implement GitHub OAuth for connecting GitHub profiles

@router.get("/auth/github/url", response_model=GitHubAuthUrlResponse)
async def get_github_auth_url(
    redirect_uri: Optional[str] = None,
):
    """
    Get GitHub authorization URL for connecting GitHub account.
    """
    # TODO: Implement GitHub OAuth
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub OAuth not yet implemented"
    )


@router.post("/auth/github/callback", response_model=GitHubConnectResponse)
async def github_callback(
    data: GitHubCallbackRequest,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Complete GitHub OAuth and connect to user profile.
    """
    # TODO: Implement GitHub OAuth callback
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GitHub OAuth not yet implemented"
    )


# ==================== VERTICAL PROFILE ENDPOINTS ====================

from pydantic import BaseModel as PydanticBaseModel

# Monthly interview cooldown (30 days)
MONTHLY_COOLDOWN_DAYS = 30


class VerticalProfileResponse(PydanticBaseModel):
    """Response for a student's vertical profile."""
    id: str
    vertical: str
    role_type: str
    status: str
    interview_score: Optional[float] = None
    best_score: Optional[float] = None
    total_interviews: int = 0
    last_interview_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    can_interview: bool = False
    next_interview_available_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VerticalProfileList(PydanticBaseModel):
    """List of student's vertical profiles."""
    profiles: list[VerticalProfileResponse]
    total: int


class MatchingJobResponse(PydanticBaseModel):
    """Job that matches a student's vertical profile."""
    job_id: str
    job_title: str
    company_name: str
    vertical: str
    role_type: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    match_score: Optional[float] = None
    match_status: Optional[str] = None

    class Config:
        from_attributes = True


class MatchingJobsResponse(PydanticBaseModel):
    """List of jobs matching a student's vertical profiles."""
    jobs: list[MatchingJobResponse]
    total: int


@router.get("/me/verticals", response_model=VerticalProfileList)
async def get_my_vertical_profiles(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get the current student's vertical profiles.
    Shows interview status and scores for each vertical.
    Students can interview once per month per vertical.
    """
    profiles = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == current_candidate.id
    ).order_by(CandidateVerticalProfile.created_at.desc()).all()

    result = []
    for profile in profiles:
        # Calculate monthly interview eligibility
        can_interview = False
        next_interview_at = None

        if profile.status == VerticalProfileStatus.COMPLETED:
            if profile.last_interview_at:
                cooldown_end = profile.last_interview_at + timedelta(days=MONTHLY_COOLDOWN_DAYS)
                if datetime.utcnow() >= cooldown_end:
                    can_interview = True
                else:
                    next_interview_at = cooldown_end
            else:
                can_interview = True
        elif profile.status == VerticalProfileStatus.PENDING:
            can_interview = True

        result.append(VerticalProfileResponse(
            id=profile.id,
            vertical=profile.vertical.value,
            role_type=profile.role_type.value,
            status=profile.status.value,
            interview_score=profile.interview_score,
            best_score=profile.best_score,
            total_interviews=profile.total_interviews or 0,
            last_interview_at=profile.last_interview_at,
            completed_at=profile.completed_at,
            can_interview=can_interview,
            next_interview_available_at=next_interview_at,
        ))

    return VerticalProfileList(profiles=result, total=len(result))


@router.get("/me/matching-jobs", response_model=MatchingJobsResponse)
async def get_my_matching_jobs(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get jobs matching the student's completed vertical profiles.
    Only shows jobs where the student has a completed vertical interview.
    """
    # Get candidate's completed vertical profiles
    completed_profiles = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == current_candidate.id,
        CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
    ).all()

    if not completed_profiles:
        return MatchingJobsResponse(jobs=[], total=0)

    # Get verticals the candidate has completed
    completed_verticals = [p.vertical for p in completed_profiles]

    # Find active jobs matching these verticals
    jobs = db.query(Job).filter(
        Job.is_active == True,
        Job.vertical.in_(completed_verticals)
    ).order_by(Job.created_at.desc()).all()

    result = []
    for job in jobs:
        # Check if there's an existing match for this job
        match = db.query(Match).filter(
            Match.candidate_id == current_candidate.id,
            Match.job_id == job.id
        ).first()

        # Find the profile for this job's vertical
        profile = next((p for p in completed_profiles if p.vertical == job.vertical), None)

        result.append(MatchingJobResponse(
            job_id=job.id,
            job_title=job.title,
            company_name=job.employer.company_name,
            vertical=job.vertical.value if job.vertical else "",
            role_type=job.role_type.value if job.role_type else None,
            location=job.location,
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            match_score=match.overall_match_score if match else (profile.best_score * 10 if profile else None),
            match_status=match.status.value if match else None,
        ))

    return MatchingJobsResponse(jobs=result, total=len(result))


@router.get("/me/verticals/{vertical}", response_model=VerticalProfileResponse)
async def get_my_vertical_profile(
    vertical: str,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get a specific vertical profile for the current student.
    """
    try:
        vertical_enum = Vertical(vertical)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid vertical: {vertical}. Valid options: engineering, data, business, design"
        )

    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == current_candidate.id,
        CandidateVerticalProfile.vertical == vertical_enum
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found for this vertical"
        )

    # Calculate monthly interview eligibility
    can_interview = False
    next_interview_at = None

    if profile.status == VerticalProfileStatus.COMPLETED:
        if profile.last_interview_at:
            cooldown_end = profile.last_interview_at + timedelta(days=MONTHLY_COOLDOWN_DAYS)
            if datetime.utcnow() >= cooldown_end:
                can_interview = True
            else:
                next_interview_at = cooldown_end
        else:
            can_interview = True
    elif profile.status == VerticalProfileStatus.PENDING:
        can_interview = True

    return VerticalProfileResponse(
        id=profile.id,
        vertical=profile.vertical.value,
        role_type=profile.role_type.value,
        status=profile.status.value,
        interview_score=profile.interview_score,
        best_score=profile.best_score,
        total_interviews=profile.total_interviews or 0,
        last_interview_at=profile.last_interview_at,
        completed_at=profile.completed_at,
        can_interview=can_interview,
        next_interview_available_at=next_interview_at,
    )

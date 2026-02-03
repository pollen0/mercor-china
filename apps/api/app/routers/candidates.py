import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel as PydanticBaseModel
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
    SharingPreferences,
    SharingPreferencesUpdate,
    SharingPreferencesResponse,
)
from ..services.resume import resume_service
from ..services.storage import storage_service
from ..utils.auth import create_token, get_current_candidate, get_current_employer, get_password_hash, verify_password
from ..utils.rate_limit import limiter, RateLimits
from ..utils.crypto import encrypt_token, decrypt_token
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
        target_roles=None,  # Use None for SQLite compatibility in tests
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

    # Send verification email (non-blocking - don't fail registration if email fails)
    try:
        from .auth import create_verification_for_candidate
        create_verification_for_candidate(candidate, db, background_tasks)
    except Exception as e:
        logger.warning(f"Failed to send verification email for {candidate.email}: {e}")

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
    from ..utils.sanitize import sanitize_name, sanitize_text_content, sanitize_url, sanitize_string

    update_dict = update_data.model_dump(exclude_unset=True)

    # Sanitize string fields to prevent XSS
    sanitize_fields = {
        'name': sanitize_name,
        'phone': lambda x: sanitize_string(x, allow_newlines=False, max_length=20),
        'university': lambda x: sanitize_string(x, allow_newlines=False, max_length=200),
        'major': lambda x: sanitize_string(x, allow_newlines=False, max_length=200),
        'bio': sanitize_text_content,
        'linkedin_url': sanitize_url,
        'portfolio_url': sanitize_url,
    }

    for field, value in update_dict.items():
        if hasattr(current_candidate, field):
            # Apply sanitization if available
            if field in sanitize_fields and value is not None:
                value = sanitize_fields[field](value)
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

    # Get filename
    filename = file.filename or "resume"

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    # Comprehensive file validation (extension, size, and magic bytes)
    from ..utils.file_validation import validate_resume_file
    is_valid, error = validate_resume_file(file_bytes, filename)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
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

        # Upload to R2 using settings for bucket name
        from io import BytesIO
        from ..config import settings
        storage_service.client.upload_fileobj(
            BytesIO(file_bytes),
            settings.r2_bucket_name,
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

    # Sanitize parsed data and raw text to prevent XSS
    from ..utils.sanitize import sanitize_resume_data, sanitize_text_content, sanitize_name

    sanitized_raw_text = sanitize_text_content(raw_text)
    sanitized_parsed_data = sanitize_resume_data(parsed_data.model_dump()) if parsed_data else None

    # Update candidate record with sanitized data
    candidate.resume_url = resume_url
    candidate.resume_raw_text = sanitized_raw_text
    candidate.resume_parsed_data = sanitized_parsed_data
    candidate.resume_uploaded_at = datetime.utcnow()

    # Auto-update candidate name if parsed and missing
    if parsed_data.name and not candidate.name:
        candidate.name = sanitize_name(parsed_data.name)

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


# ==================== TRANSCRIPT ENDPOINTS ====================

@router.post("/{candidate_id}/transcript")
@limiter.limit(RateLimits.AI_RESUME_PARSE)
async def upload_transcript(
    request: Request,
    candidate_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Upload and parse a student's unofficial transcript.
    Extracts course names, grades, and other academic data.
    """
    # Verify candidate is uploading their own transcript
    if current_candidate.id != candidate_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only upload your own transcript"
        )

    candidate = current_candidate

    # Get filename
    filename = file.filename or "transcript.pdf"

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {str(e)}"
        )

    # Comprehensive file validation (extension, size, and magic bytes)
    from ..utils.file_validation import validate_transcript_file
    is_valid, error = validate_transcript_file(file_bytes, filename)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Extract text from transcript
    try:
        raw_text = await resume_service.extract_text(file_bytes, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse transcript: {str(e)}"
        )

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from transcript. Please ensure it's not a scanned image."
        )

    # Upload transcript file to storage
    transcript_url = None
    try:
        storage_key = f"transcripts/{candidate_id}/{uuid.uuid4().hex[:8]}.pdf"

        # Upload to R2 using settings for bucket name
        from io import BytesIO
        from ..config import settings
        storage_service.client.upload_fileobj(
            BytesIO(file_bytes),
            settings.r2_bucket_name,
            storage_key,
            ExtraArgs={"ContentType": "application/pdf"}
        )
        transcript_url = storage_key
    except Exception as e:
        logger.error(f"Transcript upload error for student {candidate_id}: {e}")
        transcript_url = None  # Continue without storage

    # Parse transcript with AI (using a modified prompt for transcripts)
    try:
        parsed_data = await parse_transcript(raw_text)
    except Exception as e:
        logger.error(f"Transcript parsing error: {e}")
        parsed_data = None

    # Store parsed transcript data in the courses field
    if parsed_data:
        candidate.courses = parsed_data.get("courses", [])
        if parsed_data.get("gpa"):
            candidate.gpa = parsed_data.get("gpa")
        db.commit()

    return {
        "success": True,
        "message": "Transcript uploaded and parsed successfully",
        "parsed_data": parsed_data,
        "transcript_url": transcript_url
    }


async def parse_transcript(raw_text: str) -> dict:
    """
    Parse transcript text using AI to extract courses and grades.
    Uses Claude as primary, DeepSeek as fallback.
    """
    import httpx
    import json
    from ..config import settings

    system_prompt = """You are an expert at parsing academic transcripts. Extract course information from the transcript.
Be accurate and only include information clearly stated. Respond in valid JSON format only."""

    user_prompt = f"""Parse this transcript and extract course information:

TRANSCRIPT TEXT:
{raw_text[:10000]}

Respond with JSON in this format:
{{
    "gpa": 3.5,
    "courses": [
        {{
            "code": "CS 101",
            "name": "Introduction to Computer Science",
            "grade": "A",
            "credits": 3,
            "semester": "Fall 2023"
        }}
    ],
    "total_credits": 60,
    "university": "University Name"
}}"""

    # Try Claude first (faster and more accurate)
    if settings.anthropic_api_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": settings.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.claude_model,
                        "max_tokens": 3000,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ]
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["content"][0]["text"]

                # Extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                return json.loads(content.strip())
        except Exception as e:
            logger.warning(f"Claude transcript parsing failed, trying DeepSeek: {e}")

    # Fallback to DeepSeek
    if settings.deepseek_api_key:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.deepseek_base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 3000,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.error(f"DeepSeek transcript parsing error: {e}")

    return {"courses": [], "gpa": None}


# ==================== GITHUB OAUTH ENDPOINTS ====================

from ..services.github import github_service
from ..utils.csrf import generate_csrf_token, validate_csrf_token

@router.get("/auth/github/url", response_model=GitHubAuthUrlResponse)
async def get_github_auth_url(
    redirect_uri: Optional[str] = None,
):
    """
    Get GitHub authorization URL for connecting GitHub account.
    """
    if not github_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured"
        )

    # Generate CSRF state token with proper storage
    state = generate_csrf_token(oauth_type="github")

    # Default redirect URI
    from ..config import settings
    if not redirect_uri:
        redirect_uri = f"{settings.frontend_url}/auth/github/callback"

    auth_url = github_service.get_auth_url(
        redirect_uri=redirect_uri,
        state=state,
    )

    return GitHubAuthUrlResponse(
        auth_url=auth_url,
        state=state,
    )


@router.post("/auth/github/callback", response_model=GitHubConnectResponse)
async def github_callback(
    data: GitHubCallbackRequest,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Complete GitHub OAuth and connect to user profile.
    Requires authenticated candidate to connect their GitHub account.
    """
    if not github_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth is not configured"
        )

    # Validate CSRF state token
    if not data.state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state token. Please restart the OAuth flow."
        )

    if not validate_csrf_token(data.state, expected_type="github"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token. Please restart the OAuth flow."
        )

    try:
        # Exchange code for access token
        access_token = await github_service.exchange_code_for_token(data.code)

        # Get full GitHub profile
        github_data = await github_service.get_full_profile(access_token)

        # Check if GitHub account is already connected to another user
        existing = db.query(Candidate).filter(
            Candidate.github_username == github_data["username"],
            Candidate.id != current_candidate.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This GitHub account is already connected to another user"
            )

        # Sanitize GitHub data before storage to prevent XSS
        from ..utils.sanitize import sanitize_github_data, sanitize_string
        sanitized_github_data = sanitize_github_data(github_data)

        # Update candidate with sanitized GitHub data
        current_candidate.github_username = sanitize_string(github_data["username"], allow_newlines=False, max_length=100)
        current_candidate.github_access_token = encrypt_token(access_token)  # Encrypted for security
        current_candidate.github_data = sanitized_github_data
        current_candidate.github_connected_at = datetime.utcnow()

        db.commit()

        return GitHubConnectResponse(
            success=True,
            message="GitHub account connected successfully",
            github_username=github_data["username"],
            github_data=GitHubInfo(
                username=github_data["username"],
                connected_at=current_candidate.github_connected_at,
                top_repos=github_data.get("top_repos"),
                total_repos=github_data.get("public_repos"),
                total_contributions=github_data.get("total_contributions"),
                languages=github_data.get("languages"),
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect GitHub: {str(e)}"
        )


@router.delete("/me/github")
async def disconnect_github(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Disconnect GitHub account from student profile.
    """
    if not current_candidate.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub account connected"
        )

    current_candidate.github_username = None
    current_candidate.github_access_token = None
    current_candidate.github_data = None
    current_candidate.github_connected_at = None

    db.commit()

    return {"success": True, "message": "GitHub account disconnected"}


@router.get("/me/github", response_model=GitHubInfo)
async def get_my_github(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Get current student's connected GitHub info.
    """
    if not current_candidate.github_username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GitHub account connected"
        )

    github_data = current_candidate.github_data or {}

    return GitHubInfo(
        username=current_candidate.github_username,
        connected_at=current_candidate.github_connected_at,
        top_repos=github_data.get("top_repos"),
        total_repos=github_data.get("public_repos"),
        total_contributions=github_data.get("total_contributions"),
        languages=github_data.get("languages"),
    )


@router.post("/me/github/refresh")
async def refresh_github_data(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Refresh GitHub profile data from the API.
    """
    if not current_candidate.github_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub account connected"
        )

    try:
        # Decrypt the stored token before using it
        decrypted_token = decrypt_token(current_candidate.github_access_token)
        github_data = await github_service.get_full_profile(decrypted_token)

        current_candidate.github_data = github_data
        db.commit()

        return {
            "success": True,
            "message": "GitHub data refreshed",
            "github_data": GitHubInfo(
                username=github_data["username"],
                connected_at=current_candidate.github_connected_at,
                top_repos=github_data.get("top_repos"),
                total_repos=github_data.get("public_repos"),
                total_contributions=github_data.get("total_contributions"),
                languages=github_data.get("languages"),
            ),
        }

    except Exception as e:
        logger.error(f"GitHub refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to refresh GitHub data. You may need to reconnect your account."
        )


# ==================== GITHUB ANALYSIS ENDPOINTS ====================

from ..services.github_analysis import github_analysis_service, GitHubProfileAnalysis
from ..models.github_analysis import GitHubAnalysis

class GitHubAnalysisResponse(PydanticBaseModel):
    """Response for GitHub analysis results."""
    overall_score: float
    originality_score: float
    activity_score: float
    depth_score: float
    collaboration_score: float

    total_repos_analyzed: int
    total_commits: int
    total_lines_added: int

    personal_projects: int
    class_projects: int
    ai_assisted_repos: int

    organic_code_ratio: float
    has_tests: bool
    has_ci_cd: bool

    primary_languages: list[dict]
    flags: list[dict]
    requires_review: bool

    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/me/github/analyze", response_model=GitHubAnalysisResponse)
@limiter.limit(RateLimits.AI_RESUME_PARSE)  # Rate limit since it makes many API calls
async def analyze_github_profile(
    request: Request,
    background_tasks: BackgroundTasks,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Perform deep analysis of the student's GitHub profile.
    Analyzes contribution patterns, code origin, project types, etc.
    This is computationally intensive and makes many GitHub API calls.
    """
    if not current_candidate.github_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub account connected"
        )

    try:
        # Decrypt the stored token before using it
        decrypted_token = decrypt_token(current_candidate.github_access_token)

        # Perform the analysis
        analysis = await github_analysis_service.analyze_profile(
            access_token=decrypted_token,
            username=current_candidate.github_username,
            include_private=True,
            max_repos=15,  # Limit for rate limiting
        )

        # Store analysis in database
        existing_analysis = db.query(GitHubAnalysis).filter(
            GitHubAnalysis.candidate_id == current_candidate.id
        ).first()

        if existing_analysis:
            # Update existing
            existing_analysis.overall_score = analysis.overall_score
            existing_analysis.originality_score = analysis.originality_score
            existing_analysis.activity_score = analysis.activity_score
            existing_analysis.depth_score = analysis.depth_score
            existing_analysis.collaboration_score = analysis.collaboration_score
            existing_analysis.total_repos_analyzed = analysis.total_repos_analyzed
            existing_analysis.total_commits_by_user = analysis.total_commits_by_user
            existing_analysis.total_lines_added = analysis.total_lines_added
            existing_analysis.total_lines_removed = analysis.total_lines_removed
            existing_analysis.personal_projects_count = analysis.personal_projects_count
            existing_analysis.class_projects_count = analysis.class_projects_count
            existing_analysis.fork_contributions_count = analysis.fork_contributions_count
            existing_analysis.organic_code_ratio = analysis.organic_code_ratio
            existing_analysis.ai_assisted_repos = analysis.ai_assisted_repos
            existing_analysis.has_tests = analysis.has_tests
            existing_analysis.has_ci_cd = analysis.has_ci_cd
            existing_analysis.has_documentation = analysis.has_documentation
            existing_analysis.primary_languages = analysis.primary_languages
            existing_analysis.flags = analysis.flags
            existing_analysis.requires_review = analysis.requires_review
            existing_analysis.repo_analyses = analysis.repo_analyses
            existing_analysis.analyzed_at = datetime.utcnow()
        else:
            # Create new
            new_analysis = GitHubAnalysis(
                id=f"gha_{uuid.uuid4().hex[:16]}",
                candidate_id=current_candidate.id,
                overall_score=analysis.overall_score,
                originality_score=analysis.originality_score,
                activity_score=analysis.activity_score,
                depth_score=analysis.depth_score,
                collaboration_score=analysis.collaboration_score,
                total_repos_analyzed=analysis.total_repos_analyzed,
                total_commits_by_user=analysis.total_commits_by_user,
                total_lines_added=analysis.total_lines_added,
                total_lines_removed=analysis.total_lines_removed,
                personal_projects_count=analysis.personal_projects_count,
                class_projects_count=analysis.class_projects_count,
                fork_contributions_count=analysis.fork_contributions_count,
                organic_code_ratio=analysis.organic_code_ratio,
                ai_assisted_repos=analysis.ai_assisted_repos,
                has_tests=analysis.has_tests,
                has_ci_cd=analysis.has_ci_cd,
                has_documentation=analysis.has_documentation,
                primary_languages=analysis.primary_languages,
                flags=analysis.flags,
                requires_review=analysis.requires_review,
                repo_analyses=analysis.repo_analyses,
            )
            db.add(new_analysis)

        db.commit()

        return GitHubAnalysisResponse(
            overall_score=analysis.overall_score,
            originality_score=analysis.originality_score,
            activity_score=analysis.activity_score,
            depth_score=analysis.depth_score,
            collaboration_score=analysis.collaboration_score,
            total_repos_analyzed=analysis.total_repos_analyzed,
            total_commits=analysis.total_commits_by_user,
            total_lines_added=analysis.total_lines_added,
            personal_projects=analysis.personal_projects_count,
            class_projects=analysis.class_projects_count,
            ai_assisted_repos=analysis.ai_assisted_repos,
            organic_code_ratio=analysis.organic_code_ratio,
            has_tests=analysis.has_tests,
            has_ci_cd=analysis.has_ci_cd,
            primary_languages=analysis.primary_languages,
            flags=analysis.flags,
            requires_review=analysis.requires_review,
            analyzed_at=datetime.utcnow(),
        )

    except Exception as e:
        logger.error(f"GitHub analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze GitHub profile: {str(e)}"
        )


@router.get("/me/github/analysis", response_model=Optional[GitHubAnalysisResponse])
async def get_github_analysis(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get the stored GitHub analysis for the current student.
    Returns None if analysis hasn't been performed yet.
    """
    analysis = db.query(GitHubAnalysis).filter(
        GitHubAnalysis.candidate_id == current_candidate.id
    ).first()

    if not analysis:
        return None

    return GitHubAnalysisResponse(
        overall_score=analysis.overall_score or 0,
        originality_score=analysis.originality_score or 0,
        activity_score=analysis.activity_score or 0,
        depth_score=analysis.depth_score or 0,
        collaboration_score=analysis.collaboration_score or 0,
        total_repos_analyzed=analysis.total_repos_analyzed or 0,
        total_commits=analysis.total_commits_by_user or 0,
        total_lines_added=analysis.total_lines_added or 0,
        personal_projects=analysis.personal_projects_count or 0,
        class_projects=analysis.class_projects_count or 0,
        ai_assisted_repos=analysis.ai_assisted_repos or 0,
        organic_code_ratio=analysis.organic_code_ratio or 0,
        has_tests=analysis.has_tests or False,
        has_ci_cd=analysis.has_ci_cd or False,
        primary_languages=analysis.primary_languages or [],
        flags=analysis.flags or [],
        requires_review=analysis.requires_review or False,
        analyzed_at=analysis.analyzed_at,
    )


# ==================== VERTICAL PROFILE ENDPOINTS ====================

# Monthly interview cooldown (30 days)
MONTHLY_COOLDOWN_DAYS = 30


class VerticalProfileResponse(PydanticBaseModel):
    """Response for a student's vertical profile."""
    id: str
    vertical: str
    role_type: str
    status: str
    interview_session_id: Optional[str] = None  # Current/last interview session ID
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
            interview_session_id=profile.interview_session_id,
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
        interview_session_id=profile.interview_session_id,
        interview_score=profile.interview_score,
        best_score=profile.best_score,
        total_interviews=profile.total_interviews or 0,
        last_interview_at=profile.last_interview_at,
        completed_at=profile.completed_at,
        can_interview=can_interview,
        next_interview_available_at=next_interview_at,
    )


# ============================================================================
# PROFILE SCORING
# ============================================================================

from ..services.scoring import scoring_service


class ProfileScoreResponse(PydanticBaseModel):
    """Response for profile scoring."""
    profile_score: Optional[float] = None
    breakdown: dict = {}
    strengths: list[str] = []
    gaps: list[str] = []
    summary: str = ""
    completeness: int = 0
    algorithm_version: str = ""

    class Config:
        from_attributes = True


@router.get("/me/profile-score", response_model=ProfileScoreResponse)
async def get_my_profile_score(
    vertical: Optional[str] = None,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get an AI-generated profile score for the current student.
    Scores based on resume, GitHub, and education data.
    This provides an initial assessment before completing an interview.
    """
    # Build education data
    education_data = None
    if current_candidate.university:
        education_data = {
            "university": current_candidate.university,
            "major": current_candidate.major,
            "graduation_year": current_candidate.graduation_year,
            "gpa": current_candidate.gpa,
            "courses": current_candidate.courses,
        }

    # Get resume data
    resume_data = current_candidate.resume_parsed_data

    # Get GitHub data
    github_data = current_candidate.github_data

    # Check if we have any data to score
    if not any([resume_data, github_data, education_data]):
        return ProfileScoreResponse(
            profile_score=None,
            completeness=0,
            summary="Please complete your profile (upload resume, connect GitHub, or add education info) to receive a profile score.",
            algorithm_version="2.0.0",
        )

    try:
        result = await scoring_service.score_profile(
            resume_data=resume_data,
            github_data=github_data,
            education_data=education_data,
            vertical=vertical,
        )

        return ProfileScoreResponse(
            profile_score=result.get("profile_score"),
            breakdown=result.get("breakdown", {}),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            summary=result.get("summary", ""),
            completeness=result.get("completeness", 0),
            algorithm_version=result.get("algorithm_version", ""),
        )

    except Exception as e:
        logger.error(f"Profile scoring error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score profile: {str(e)}"
        )


@router.post("/{candidate_id}/profile-score", response_model=ProfileScoreResponse)
async def get_candidate_profile_score(
    candidate_id: str,
    vertical: Optional[str] = None,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """
    Get an AI-generated profile score for a specific candidate (employer only).
    Useful for employers to quickly assess candidates in the talent pool.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Build education data
    education_data = None
    if candidate.university:
        education_data = {
            "university": candidate.university,
            "major": candidate.major,
            "graduation_year": candidate.graduation_year,
            "gpa": candidate.gpa,
            "courses": candidate.courses,
        }

    # Get resume data
    resume_data = candidate.resume_parsed_data

    # Get GitHub data
    github_data = candidate.github_data

    # Check if we have any data to score
    if not any([resume_data, github_data, education_data]):
        return ProfileScoreResponse(
            profile_score=None,
            completeness=0,
            summary="Candidate has not completed their profile yet.",
            algorithm_version="2.0.0",
        )

    try:
        result = await scoring_service.score_profile(
            resume_data=resume_data,
            github_data=github_data,
            education_data=education_data,
            vertical=vertical,
        )

        return ProfileScoreResponse(
            profile_score=result.get("profile_score"),
            breakdown=result.get("breakdown", {}),
            strengths=result.get("strengths", []),
            gaps=result.get("gaps", []),
            summary=result.get("summary", ""),
            completeness=result.get("completeness", 0),
            algorithm_version=result.get("algorithm_version", ""),
        )

    except Exception as e:
        logger.error(f"Profile scoring error for {candidate_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to score profile: {str(e)}"
        )


# ============================================================================
# SHARING PREFERENCES (GTM)
# ============================================================================

@router.get("/me/sharing-preferences", response_model=SharingPreferencesResponse)
async def get_sharing_preferences(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get the current student's profile sharing preferences.
    Used to control which employers can see their profile.
    """
    preferences = None
    if current_candidate.sharing_preferences:
        preferences = SharingPreferences(**current_candidate.sharing_preferences)

    return SharingPreferencesResponse(
        opted_in_to_sharing=current_candidate.opted_in_to_sharing,
        preferences=preferences
    )


@router.patch("/me/sharing-preferences", response_model=SharingPreferencesResponse)
async def update_sharing_preferences(
    preferences_update: SharingPreferencesUpdate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Update the current student's profile sharing preferences.

    Students can control:
    - Whether to opt in to profile sharing (opted_in_to_sharing)
    - Which company stages they're interested in (seed, series_a, etc.)
    - Preferred locations (remote, sf, nyc, etc.)
    - Industries of interest (fintech, climate, ai, etc.)
    - Email digest notifications
    """
    try:
        # Update opt-in status if provided
        if preferences_update.opted_in_to_sharing is not None:
            current_candidate.opted_in_to_sharing = preferences_update.opted_in_to_sharing

        # Update sharing preferences JSONB
        current_prefs = current_candidate.sharing_preferences or {}

        if preferences_update.company_stages is not None:
            current_prefs["company_stages"] = preferences_update.company_stages

        if preferences_update.locations is not None:
            current_prefs["locations"] = preferences_update.locations

        if preferences_update.industries is not None:
            current_prefs["industries"] = preferences_update.industries

        if preferences_update.email_digest is not None:
            current_prefs["email_digest"] = preferences_update.email_digest

        current_candidate.sharing_preferences = current_prefs
        db.commit()
        db.refresh(current_candidate)

        logger.info(f"Updated sharing preferences for candidate {current_candidate.id}")

        # Build response
        preferences = SharingPreferences(**current_candidate.sharing_preferences) if current_candidate.sharing_preferences else None

        return SharingPreferencesResponse(
            opted_in_to_sharing=current_candidate.opted_in_to_sharing,
            preferences=preferences
        )

    except Exception as e:
        logger.error(f"Error updating sharing preferences: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update sharing preferences"
        )


# ============================================================================
# SKILL GAP ANALYSIS FOR CANDIDATES
# ============================================================================

from ..services.skill_gap import skill_gap_service


class CandidateSkillGapRequest(PydanticBaseModel):
    """Request for candidate's skill gap analysis."""
    job_id: Optional[str] = None
    job_requirements: Optional[list[str]] = None  # If no job_id provided


class CandidateSkillGapResponse(PydanticBaseModel):
    """Skill gap analysis for a candidate."""
    overall_match_score: float
    total_requirements: int
    matched_requirements: int
    critical_gaps: list[str]
    proficiency_distribution: dict[str, int]
    avg_proficiency_score: float
    learning_priorities: list[dict]
    bonus_skills: list[str]
    strongest_areas: list[str]


@router.post("/me/skill-gap", response_model=CandidateSkillGapResponse)
async def get_my_skill_gap(
    data: CandidateSkillGapRequest,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Analyze the current student's skill gap against a job or custom requirements.

    Returns:
    - Overall match score
    - Critical skill gaps
    - Learning priorities with estimated effort
    - Strongest areas
    """
    from ..models import Job

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
            detail="Please provide job_id or job_requirements"
        )

    # Get candidate skills
    candidate_skills = []
    parsed_resume = None

    if current_candidate.resume_parsed_data:
        try:
            import json
            resume_data = current_candidate.resume_parsed_data if isinstance(current_candidate.resume_parsed_data, dict) else json.loads(current_candidate.resume_parsed_data)
            candidate_skills = resume_data.get('skills', [])

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
    if current_candidate.github_data:
        try:
            import json
            github_data = current_candidate.github_data if isinstance(current_candidate.github_data, dict) else json.loads(current_candidate.github_data)
        except Exception:
            pass

    # Run skill gap analysis
    analysis = skill_gap_service.analyze_skill_gap(
        candidate_skills=candidate_skills,
        job_requirements=job_requirements,
        parsed_resume=parsed_resume,
        github_data=github_data,
    )

    logger.info(f"Candidate skill gap analysis: candidate={current_candidate.id}, score={analysis.overall_match_score}")

    return CandidateSkillGapResponse(
        overall_match_score=analysis.overall_match_score,
        total_requirements=analysis.total_requirements,
        matched_requirements=analysis.matched_requirements,
        critical_gaps=analysis.critical_gaps,
        proficiency_distribution=analysis.proficiency_distribution,
        avg_proficiency_score=analysis.avg_proficiency_score,
        learning_priorities=analysis.learning_priorities,
        bonus_skills=analysis.bonus_skills,
        strongest_areas=analysis.strongest_areas,
    )

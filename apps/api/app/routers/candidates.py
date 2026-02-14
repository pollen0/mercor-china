import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel as PydanticBaseModel
import uuid
import re

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
from ..services.growth_tracking import growth_tracking_service
from ..utils.auth import create_token, create_token_pair, verify_refresh_token, revoke_refresh_token, get_current_candidate, get_current_employer, get_password_hash, verify_password, blacklist_token
from ..utils.rate_limit import limiter, RateLimits
from ..utils.crypto import encrypt_token, decrypt_token
from ..config import settings

logger = logging.getLogger("pathway.candidates")
router = APIRouter()


def generate_cuid() -> str:
    return f"c{uuid.uuid4().hex[:24]}"


@router.post("/", response_model=CandidateWithToken, status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimits.AUTH_REGISTER)
async def create_candidate(
    request: Request,
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
        phone=candidate_data.phone,
        password_hash=password_hash,
        university=candidate_data.university,
        major=candidate_data.major,
        graduation_year=candidate_data.graduation_year,
        target_roles=candidate_data.target_roles if candidate_data.target_roles else None,
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

    # Process referral code if provided
    if candidate_data.referral_code:
        ref_code = candidate_data.referral_code.strip().upper()
        try:
            # Check if it's a marketing referrer code (starts with MKT-)
            if ref_code.startswith("MKT-"):
                from ..models import MarketingReferrer
                marketing_referrer = db.query(MarketingReferrer).filter(
                    MarketingReferrer.referral_code == ref_code,
                    MarketingReferrer.is_active == True
                ).first()
                if marketing_referrer:
                    candidate.marketing_referrer_id = marketing_referrer.id
                    db.commit()
                    logger.info(f"Marketing referral recorded: {marketing_referrer.name} -> {candidate.id}")
            else:
                # Standard candidate-to-candidate referral
                from ..services.referral import find_referrer_by_code, create_referral_on_signup
                referrer = find_referrer_by_code(candidate_data.referral_code, db)
                if referrer and referrer.id != candidate.id:
                    create_referral_on_signup(referrer, candidate, db)
                    logger.info(f"Referral recorded: {referrer.id} -> {candidate.id}")
        except Exception as e:
            logger.warning(f"Failed to process referral code for {candidate.email}: {e}")

    # Send verification email (non-blocking - don't fail registration if email fails)
    try:
        from .auth import create_verification_for_candidate
        create_verification_for_candidate(candidate, db, background_tasks)
    except Exception as e:
        logger.warning(f"Failed to send verification email for {candidate.email}: {e}")

    # Generate token pair for immediate login after registration
    tokens = create_token_pair(subject=candidate.id, token_type="candidate")

    return CandidateWithToken(
        candidate=CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            target_roles=candidate.target_roles or [],
            email_verified=candidate.email_verified if candidate.email_verified is not None else False,
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            gpa=candidate.gpa,
            github_username=candidate.github_username,
            resume_url=candidate.resume_url,
            created_at=candidate.created_at,
        ),
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=settings.jwt_expiry_hours * 3600,
    )


@router.post("/login", response_model=CandidateWithToken)
@limiter.limit(RateLimits.AUTH_LOGIN)
async def login_candidate(
    request: Request,
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

    # Generate token pair
    tokens = create_token_pair(subject=candidate.id, token_type="candidate")

    return CandidateWithToken(
        candidate=CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            target_roles=candidate.target_roles or [],
            email_verified=candidate.email_verified if candidate.email_verified is not None else False,
            university=candidate.university,
            major=candidate.major,
            graduation_year=candidate.graduation_year,
            gpa=candidate.gpa,
            github_username=candidate.github_username,
            resume_url=candidate.resume_url,
            created_at=candidate.created_at,
        ),
        token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        expires_in=settings.jwt_expiry_hours * 3600,
    )


@router.post("/refresh")
@limiter.limit(RateLimits.AUTH_LOGIN)  # Same rate limit as login
async def refresh_candidate_token(
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

    # Verify this is a candidate token
    if payload.get("type") != "candidate":
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
        token_type="candidate",
    )

    return TokenRefreshResponse(
        token=new_access_token,
        expires_in=settings.jwt_expiry_hours * 3600,
    )


@router.post("/logout")
async def logout_candidate(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    Logout a candidate by invalidating their token.
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

    # Filter by vertical (join with vertical profiles)
    if vertical:
        try:
            vertical_enum = Vertical(vertical)
            query = query.join(
                CandidateVerticalProfile,
                CandidateVerticalProfile.candidate_id == Candidate.id
            ).filter(
                CandidateVerticalProfile.vertical == vertical_enum,
                CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid vertical: {vertical}"
            )

    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

    return CandidateList(candidates=candidates, total=total)


@router.get("/me", response_model=CandidateResponse)
async def get_current_candidate_profile(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the current authenticated student's profile."""
    # Generate a signed URL for the resume if it's a storage key
    resume_url = current_candidate.resume_url
    if resume_url and not resume_url.startswith('http'):
        try:
            resume_url = storage_service.get_signed_url(resume_url, expiration=3600)
        except Exception:
            pass

    return CandidateResponse(
        id=current_candidate.id,
        name=current_candidate.name,
        email=current_candidate.email,
        phone=current_candidate.phone,
        target_roles=current_candidate.target_roles or [],
        email_verified=current_candidate.email_verified if current_candidate.email_verified is not None else False,
        university=current_candidate.university,
        major=current_candidate.major,
        graduation_year=current_candidate.graduation_year,
        gpa=current_candidate.gpa,
        bio=current_candidate.bio,
        linkedin_url=current_candidate.linkedin_url,
        portfolio_url=current_candidate.portfolio_url,
        github_username=current_candidate.github_username,
        resume_url=resume_url,
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

    # Generate a signed URL for the resume if it's a storage key
    resume_url = current_candidate.resume_url
    if resume_url and not resume_url.startswith('http'):
        try:
            resume_url = storage_service.get_signed_url(resume_url, expiration=3600)
        except Exception:
            pass

    return CandidateResponse(
        id=current_candidate.id,
        name=current_candidate.name,
        email=current_candidate.email,
        phone=current_candidate.phone,
        target_roles=current_candidate.target_roles or [],
        email_verified=current_candidate.email_verified if current_candidate.email_verified is not None else False,
        university=current_candidate.university,
        major=current_candidate.major,
        graduation_year=current_candidate.graduation_year,
        gpa=current_candidate.gpa,
        bio=current_candidate.bio,
        linkedin_url=current_candidate.linkedin_url,
        portfolio_url=current_candidate.portfolio_url,
        github_username=current_candidate.github_username,
        resume_url=resume_url,
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
            total_repos=github_data.get("public_repos"),
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

def _match_club(activity_name: str, db: Session) -> tuple:
    """Try to match an activity name to a known club. Returns (club, score) or (None, 3.0)."""
    from sqlalchemy import func as sqlfunc

    name_lower = activity_name.lower().strip()

    # 1. SQL-level search: exact short_name match or name containment
    club = db.query(Club).filter(
        (sqlfunc.lower(Club.name).contains(name_lower)) |
        (sqlfunc.lower(Club.short_name) == name_lower)
    ).first()

    if club:
        return club, club.prestige_score

    # 2. Reverse: check if any club name is contained within the activity name (limited query)
    candidates = db.query(Club).filter(
        sqlfunc.length(Club.name) >= 4  # Skip very short names to avoid false matches
    ).limit(200).all()

    for c in candidates:
        if c.name.lower() in name_lower or (c.short_name and c.short_name.lower() in name_lower):
            return c, c.prestige_score
        if c.aliases:
            for alias in c.aliases:
                if isinstance(alias, str) and alias.lower() in name_lower:
                    return c, c.prestige_score

    return None, 3.0


def _get_role_tier_for_populate(role: str | None) -> int:
    """Determine role tier from role title."""
    if not role:
        return 1
    role_lower = role.lower()
    if any(x in role_lower for x in ["president", "founder", "ceo", "director"]):
        return 5
    if any(x in role_lower for x in ["vice president", "vp", "executive", "chair", "head"]):
        return 4
    if any(x in role_lower for x in ["officer", "lead", "manager", "coordinator", "captain"]):
        return 3
    if any(x in role_lower for x in ["mentor", "tutor", "developer", "designer", "analyst"]):
        return 2
    return 1


def _get_role_multiplier_for_populate(role: str | None) -> float:
    """Get score multiplier based on role."""
    tier = _get_role_tier_for_populate(role)
    return {1: 1.0, 2: 1.1, 3: 1.25, 4: 1.4, 5: 1.5}.get(tier, 1.0)


def _estimate_award_tier_for_populate(name: str, issuer: str | None) -> int:
    """Estimate prestige tier for an award based on keywords."""
    name_lower = name.lower()
    issuer_lower = (issuer or "").lower()

    if any(x in name_lower for x in ["national", "international", "goldwater", "fulbright", "rhodes", "marshall"]):
        return 5
    if any(x in name_lower for x in ["scholarship", "fellowship"]):
        if any(x in issuer_lower for x in ["google", "microsoft", "facebook", "meta", "apple", "amazon"]):
            return 5
        return 4
    if any(x in name_lower for x in ["first place", "1st place", "grand prize", "winner"]):
        return 4
    if any(x in name_lower for x in ["dean's list", "honors", "cum laude", "phi beta kappa", "magna", "summa"]):
        return 3
    if any(x in name_lower for x in ["award", "recognition", "certificate", "finalist", "semifinalist"]):
        return 2
    return 1


def _auto_populate_from_resume(candidate_id: str, parsed_data: ParsedResume, db: Session) -> None:
    """
    Auto-populate CandidateActivity and CandidateAward records from parsed resume data.
    Uses case-insensitive name matching to prevent duplicates.
    Includes club matching and scoring for activities, prestige estimation for awards.
    """
    if not parsed_data:
        return

    # Get existing activities and awards for de-duplication
    existing_activities = db.query(CandidateActivity).filter(
        CandidateActivity.candidate_id == candidate_id
    ).all()
    existing_activity_names = {a.activity_name.lower() for a in existing_activities}

    existing_awards = db.query(CandidateAward).filter(
        CandidateAward.candidate_id == candidate_id
    ).all()
    existing_award_names = {a.name.lower() for a in existing_awards}

    # Create new activities with scoring (skip duplicates)
    activities_created = 0
    for activity in parsed_data.activities:
        if activity.name.lower() not in existing_activity_names:
            # Try to match with a known club
            club, base_score = _match_club(activity.name, db)
            role_multiplier = _get_role_multiplier_for_populate(activity.role)
            activity_score = min(10.0, base_score * role_multiplier)
            role_tier = _get_role_tier_for_populate(activity.role)

            new_activity = CandidateActivity(
                id=f"act_{uuid.uuid4().hex[:16]}",
                candidate_id=candidate_id,
                club_id=club.id if club else None,
                activity_name=activity.name,
                organization=activity.organization,
                role=activity.role,
                role_tier=role_tier,
                description=activity.description,
                start_date=activity.start_date,
                end_date=activity.end_date,
                activity_score=activity_score,
            )
            db.add(new_activity)
            existing_activity_names.add(activity.name.lower())
            activities_created += 1

    # Create new awards with prestige estimation (skip duplicates)
    awards_created = 0
    for award in parsed_data.awards:
        if award.name.lower() not in existing_award_names:
            prestige_tier = _estimate_award_tier_for_populate(award.name, award.issuer)

            new_award = CandidateAward(
                id=f"awd_{uuid.uuid4().hex[:16]}",
                candidate_id=candidate_id,
                name=award.name,
                issuer=award.issuer,
                date=award.date,
                prestige_tier=prestige_tier,
                description=award.description,
            )
            db.add(new_award)
            existing_award_names.add(award.name.lower())
            awards_created += 1

    if activities_created > 0 or awards_created > 0:
        db.commit()
        logger.info(f"Auto-populated {activities_created} activities and {awards_created} awards for candidate {candidate_id}")


async def _enrich_activities_awards_background(candidate_id: str, university: str | None) -> None:
    """
    Background task: Use Claude to assess notability/prestige of activities and awards.
    Updates the DB records with AI-assessed prestige tiers, scores, and descriptions.
    """
    from ..database import SessionLocal

    db = SessionLocal()
    try:
        # Get all activities and awards for this candidate
        activities = db.query(CandidateActivity).filter(
            CandidateActivity.candidate_id == candidate_id
        ).all()
        awards = db.query(CandidateAward).filter(
            CandidateAward.candidate_id == candidate_id
        ).all()

        if not activities and not awards:
            return

        # Build input for AI enrichment
        activity_dicts = [
            {
                "activity_name": a.activity_name,
                "role": a.role,
                "organization": a.organization,
                "description": a.description,
            }
            for a in activities
        ]
        award_dicts = [
            {
                "name": a.name,
                "issuer": a.issuer,
                "date": a.date,
                "description": a.description,
            }
            for a in awards
        ]

        # Call Claude for enrichment
        result = await resume_service.enrich_activities_and_awards(
            activity_dicts, award_dicts, university
        )

        # Update activities with AI assessments
        enriched_activities = result.get("enriched_activities", [])
        for enrichment in enriched_activities:
            idx = enrichment.get("index")
            if idx is not None and 0 <= idx < len(activities):
                activity = activities[idx]
                # Only upgrade scores from AI if they differ from the keyword default
                ai_score = enrichment.get("activity_score")
                if ai_score is not None:
                    activity.activity_score = min(10.0, float(ai_score) * _get_role_multiplier_for_populate(activity.role))
                # Add enhanced description if original was empty/vague
                enhanced_desc = enrichment.get("enhanced_description")
                if enhanced_desc and (not activity.description or len(activity.description) < 20):
                    activity.description = enhanced_desc

        # Update awards with AI assessments
        enriched_awards = result.get("enriched_awards", [])
        for enrichment in enriched_awards:
            idx = enrichment.get("index")
            if idx is not None and 0 <= idx < len(awards):
                award = awards[idx]
                ai_tier = enrichment.get("prestige_tier")
                if ai_tier is not None:
                    award.prestige_tier = int(ai_tier)
                ai_type = enrichment.get("award_type")
                if ai_type:
                    award.award_type = ai_type
                enhanced_desc = enrichment.get("enhanced_description")
                if enhanced_desc and (not award.description or len(award.description) < 20):
                    award.description = enhanced_desc

        db.commit()
        logger.info(f"AI enriched {len(enriched_activities)} activities and {len(enriched_awards)} awards for candidate {candidate_id}")

    except Exception as e:
        logger.error(f"Activity/award AI enrichment failed for {candidate_id}: {e}")
        db.rollback()
    finally:
        db.close()


@router.post("/{candidate_id}/resume", response_model=ResumeParseResult)
@limiter.limit(RateLimits.AI_RESUME_PARSE)
async def upload_resume(
    request: Request,
    candidate_id: str,
    background_tasks: BackgroundTasks,
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
    parse_warning = None
    try:
        parsed_data = await resume_service.parse_resume(raw_text)
        # Check if parsing returned meaningful data
        if parsed_data and not any([
            parsed_data.name,
            parsed_data.email,
            parsed_data.education,
            parsed_data.experience,
            parsed_data.skills,
        ]):
            parse_warning = "Resume was uploaded but AI could not extract structured data. The raw text is still available."
            logger.warning(f"Resume parsing returned empty data for student {candidate_id}")
    except Exception as e:
        logger.error(f"Resume AI parsing error for student {candidate_id}: {e}")
        parsed_data = ParsedResume()
        parse_warning = f"Resume uploaded but parsing failed: {str(e)[:100]}. Please try again or upload a different format."

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

    # Track resume version for growth tracking
    if resume_url:
        try:
            growth_tracking_service.create_resume_version(
                db=db,
                candidate_id=candidate_id,
                storage_key=resume_url,
                raw_text=sanitized_raw_text,
                parsed_data=sanitized_parsed_data,
                original_filename=filename,
                file_size_bytes=len(file_bytes) if file_bytes else None,
            )
        except Exception as e:
            logger.warning(f"Failed to create resume version for {candidate_id}: {e}")

    # Auto-populate activities and awards from parsed resume
    _auto_populate_from_resume(candidate_id, parsed_data, db)

    # Run AI enrichment for activities/awards in background
    if parsed_data.activities or parsed_data.awards:
        background_tasks.add_task(
            _enrich_activities_awards_background,
            candidate_id,
            candidate.university,
        )

    # Re-run matching in background (updates match scores with new resume data)
    from ..services.tasks import rematch_candidate_after_profile_update
    background_tasks.add_task(
        rematch_candidate_after_profile_update,
        candidate_id,
        str(settings.database_url),
    )

    # Generate a signed URL for the resume if we have a storage key
    signed_resume_url = resume_url
    if resume_url and not resume_url.startswith('http'):
        try:
            signed_resume_url = storage_service.get_signed_url(resume_url, expiration=3600)
        except Exception as e:
            logger.warning(f"Failed to generate signed URL for resume: {e}")

    return ResumeParseResult(
        success=True,
        message=parse_warning or "Resume uploaded and parsed successfully",
        resume_url=signed_resume_url,
        parsed_data=parsed_data,
        raw_text_preview=raw_text[:500] if raw_text else None,
        parse_warning=parse_warning,
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
        except Exception as e:
            logger.warning(f"Failed to reconstruct parsed resume data: {e}")

    # Generate a signed URL if we have a storage key
    resume_url = current_candidate.resume_url
    if resume_url and not resume_url.startswith('http'):
        try:
            resume_url = storage_service.get_signed_url(resume_url, expiration=3600)
        except Exception as e:
            logger.warning(f"Failed to generate signed URL for resume: {e}")

    return ResumeResponse(
        candidate_id=current_candidate.id,
        resume_url=resume_url,
        raw_text=current_candidate.resume_raw_text,
        parsed_data=parsed_data,
        uploaded_at=current_candidate.resume_uploaded_at
    )


@router.get("/me/resume/url")
async def get_resume_url(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get a fresh signed URL for viewing the student's resume."""
    if not current_candidate.resume_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded"
        )

    try:
        signed_url = storage_service.get_signed_url(
            current_candidate.resume_url,
            expiration=3600
        )
        return {
            "resume_url": signed_url,
            "expires_in": 3600
        }
    except Exception as e:
        logger.error(f"Failed to generate signed URL for resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate resume URL"
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
        except Exception as e:
            logger.warning(f"Failed to reconstruct parsed resume data for {candidate_id}: {e}")

    # Generate a signed URL if we have a storage key
    resume_url = candidate.resume_url
    if resume_url and not resume_url.startswith('http'):
        try:
            resume_url = storage_service.get_signed_url(resume_url, expiration=3600)
        except Exception as e:
            logger.warning(f"Failed to generate signed URL for resume: {e}")

    return ResumeResponse(
        candidate_id=candidate_id,
        resume_url=resume_url,
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
    background_tasks: BackgroundTasks,
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
    transcript_key = None
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
        transcript_key = storage_key
        # Generate a signed URL valid for 24 hours (86400 seconds)
        transcript_url = storage_service.get_signed_url(storage_key, expiration=86400)
    except Exception as e:
        logger.error(f"Transcript upload error for student {candidate_id}: {e}")
        transcript_key = None
        transcript_url = None

    # Parse transcript with AI (using a modified prompt for transcripts)
    parse_warning = None
    try:
        parsed_data = await parse_transcript(raw_text)
        # Check if parsing returned meaningful data
        if parsed_data and not parsed_data.get("courses") and not parsed_data.get("gpa"):
            parse_warning = "Transcript was uploaded but AI could not extract course data. Please ensure this is a valid academic transcript."
            logger.warning(f"Transcript parsing returned empty data for student {candidate_id}")
    except Exception as e:
        logger.error(f"Transcript parsing error: {e}")
        parsed_data = None
        parse_warning = f"Transcript uploaded but parsing failed: {str(e)[:100]}. Please try a different format or clearer scan."

    # Extract PDF metadata for verification
    pdf_metadata = None
    try:
        from ..services.transcript import transcript_service
        pdf_metadata = transcript_service.extract_pdf_metadata(file_bytes)
    except Exception as e:
        logger.warning(f"Failed to extract PDF metadata: {e}")

    # Run transcript verification
    verification_result = None
    try:
        from ..services.transcript_verification import transcript_verification_service
        verification_result = transcript_verification_service.verify_transcript(
            parsed_transcript=parsed_data or {},
            pdf_metadata=pdf_metadata,
            graduation_year=candidate.graduation_year,
        )
        logger.info(f"Transcript verification for {candidate_id}: status={verification_result.status}, score={verification_result.confidence_score}")
    except Exception as e:
        logger.error(f"Transcript verification error: {e}")

    # Store parsed transcript data in the courses field
    if parsed_data:
        candidate.courses = parsed_data.get("courses", [])
        if parsed_data.get("gpa"):
            candidate.gpa = parsed_data.get("gpa")

    # Store transcript storage key for later retrieval
    if transcript_key:
        candidate.transcript_key = transcript_key

    # Store verification results
    if verification_result:
        candidate.transcript_verification = {
            "status": verification_result.status,
            "confidence_score": verification_result.confidence_score,
            "flags": [
                {
                    "code": f.code,
                    "severity": f.severity,
                    "message": f.message,
                    "details": f.details,
                }
                for f in verification_result.flags
            ],
            "checks_performed": verification_result.checks_performed,
            "summary": verification_result.summary,
        }
        candidate.transcript_verification_status = verification_result.status
        candidate.transcript_confidence_score = verification_result.confidence_score

    db.commit()

    # Run matching in background if all prerequisites are met (resume + transcript + GitHub)
    if candidate.resume_url and candidate.transcript_key and candidate.github_username:
        from ..services.tasks import rematch_candidate_after_profile_update
        background_tasks.add_task(
            rematch_candidate_after_profile_update,
            candidate_id,
            str(settings.database_url),
        )

    # Build verification response
    verification_response = None
    if verification_result:
        verification_response = {
            "status": verification_result.status,
            "confidence_score": verification_result.confidence_score,
            "summary": verification_result.summary,
            "flags": [
                {
                    "code": f.code,
                    "severity": f.severity,
                    "message": f.message,
                }
                for f in verification_result.flags
            ],
        }

    return {
        "success": True,
        "message": parse_warning or "Transcript uploaded and parsed successfully",
        "parsed_data": parsed_data,
        "transcript_url": transcript_url,
        "transcript_key": transcript_key,
        "verification": verification_response,
        "parse_warning": parse_warning,
    }


@router.get("/me/transcript/url")
async def get_transcript_url(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Get a fresh signed URL for viewing the student's transcript.
    Returns a URL valid for 1 hour.
    """
    if not current_candidate.transcript_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transcript uploaded"
        )

    try:
        # Generate a signed URL valid for 1 hour
        signed_url = storage_service.get_signed_url(
            current_candidate.transcript_key,
            expiration=3600
        )
        return {
            "transcript_url": signed_url,
            "transcript_key": current_candidate.transcript_key
        }
    except Exception as e:
        logger.error(f"Failed to generate transcript URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate transcript URL"
        )


@router.delete("/me/transcript")
async def delete_transcript(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Delete the current student's transcript."""
    if current_candidate.transcript_key:
        try:
            # Try to delete from storage (use generic delete_object for non-video files)
            await storage_service.delete_object(current_candidate.transcript_key)
        except Exception as e:
            logger.warning(f"Failed to delete transcript from storage: {e}")

    current_candidate.transcript_key = None
    db.commit()

    return {"success": True, "message": "Transcript deleted successfully"}


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


# ==================== ACTIVITIES ENDPOINTS ====================

from ..models.activity import CandidateActivity, CandidateAward, Club

class ActivityCreate(PydanticBaseModel):
    activity_name: str
    organization: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ActivityResponse(PydanticBaseModel):
    id: str
    activity_name: str
    organization: Optional[str]
    role: Optional[str]
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    created_at: Optional[datetime]

class AwardCreate(PydanticBaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None

class AwardResponse(PydanticBaseModel):
    id: str
    name: str
    issuer: Optional[str]
    date: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]


@router.get("/me/activities", response_model=list[ActivityResponse])
async def get_my_activities(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Get all activities for the current candidate."""
    activities = db.query(CandidateActivity).filter(
        CandidateActivity.candidate_id == current_candidate.id
    ).order_by(CandidateActivity.created_at.desc()).all()

    return [ActivityResponse(
        id=a.id,
        activity_name=a.activity_name,
        organization=a.organization,
        role=a.role,
        description=a.description,
        start_date=a.start_date,
        end_date=a.end_date,
        created_at=a.created_at,
    ) for a in activities]


@router.post("/me/activities", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Create a new activity for the current candidate."""
    activity = CandidateActivity(
        id=f"act_{uuid.uuid4().hex[:16]}",
        candidate_id=current_candidate.id,
        activity_name=activity_data.activity_name,
        organization=activity_data.organization,
        role=activity_data.role,
        description=activity_data.description,
        start_date=activity_data.start_date,
        end_date=activity_data.end_date,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    return ActivityResponse(
        id=activity.id,
        activity_name=activity.activity_name,
        organization=activity.organization,
        role=activity.role,
        description=activity.description,
        start_date=activity.start_date,
        end_date=activity.end_date,
        created_at=activity.created_at,
    )


@router.put("/me/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: str,
    activity_data: ActivityCreate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Update an existing activity."""
    activity = db.query(CandidateActivity).filter(
        CandidateActivity.id == activity_id,
        CandidateActivity.candidate_id == current_candidate.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity.activity_name = activity_data.activity_name
    activity.organization = activity_data.organization
    activity.role = activity_data.role
    activity.description = activity_data.description
    activity.start_date = activity_data.start_date
    activity.end_date = activity_data.end_date

    db.commit()
    db.refresh(activity)

    return ActivityResponse(
        id=activity.id,
        activity_name=activity.activity_name,
        organization=activity.organization,
        role=activity.role,
        description=activity.description,
        start_date=activity.start_date,
        end_date=activity.end_date,
        created_at=activity.created_at,
    )


@router.delete("/me/activities/{activity_id}")
async def delete_activity(
    activity_id: str,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Delete an activity."""
    activity = db.query(CandidateActivity).filter(
        CandidateActivity.id == activity_id,
        CandidateActivity.candidate_id == current_candidate.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db.delete(activity)
    db.commit()

    return {"success": True, "message": "Activity deleted"}


# ==================== AWARDS ENDPOINTS ====================

@router.get("/me/awards", response_model=list[AwardResponse])
async def get_my_awards(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Get all awards for the current candidate."""
    awards = db.query(CandidateAward).filter(
        CandidateAward.candidate_id == current_candidate.id
    ).order_by(CandidateAward.created_at.desc()).all()

    return [AwardResponse(
        id=a.id,
        name=a.name,
        issuer=a.issuer,
        date=a.date,
        description=a.description,
        created_at=a.created_at,
    ) for a in awards]


@router.post("/me/awards", response_model=AwardResponse)
async def create_award(
    award_data: AwardCreate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Create a new award for the current candidate."""
    award = CandidateAward(
        id=f"awd_{uuid.uuid4().hex[:16]}",
        candidate_id=current_candidate.id,
        name=award_data.name,
        issuer=award_data.issuer,
        date=award_data.date,
        description=award_data.description,
    )
    db.add(award)
    db.commit()
    db.refresh(award)

    return AwardResponse(
        id=award.id,
        name=award.name,
        issuer=award.issuer,
        date=award.date,
        description=award.description,
        created_at=award.created_at,
    )


@router.put("/me/awards/{award_id}", response_model=AwardResponse)
async def update_award(
    award_id: str,
    award_data: AwardCreate,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Update an existing award."""
    award = db.query(CandidateAward).filter(
        CandidateAward.id == award_id,
        CandidateAward.candidate_id == current_candidate.id
    ).first()

    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    award.name = award_data.name
    award.issuer = award_data.issuer
    award.date = award_data.date
    award.description = award_data.description

    db.commit()
    db.refresh(award)

    return AwardResponse(
        id=award.id,
        name=award.name,
        issuer=award.issuer,
        date=award.date,
        description=award.description,
        created_at=award.created_at,
    )


@router.delete("/me/awards/{award_id}")
async def delete_award(
    award_id: str,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Delete an award."""
    award = db.query(CandidateAward).filter(
        CandidateAward.id == award_id,
        CandidateAward.candidate_id == current_candidate.id
    ).first()

    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    db.delete(award)
    db.commit()

    return {"success": True, "message": "Award deleted"}


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
    background_tasks: BackgroundTasks,
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

        # Trigger background GitHub analysis automatically
        import asyncio
        background_tasks.add_task(
            asyncio.create_task,
            run_github_analysis_background(current_candidate.id)
        )
        logger.info(f"Scheduled background GitHub analysis for candidate {current_candidate.id}")

        # Run matching in background if all prerequisites are met (resume + transcript + GitHub)
        if current_candidate.resume_url and current_candidate.transcript_key and current_candidate.github_username:
            from ..services.tasks import rematch_candidate_after_profile_update
            background_tasks.add_task(
                rematch_candidate_after_profile_update,
                current_candidate.id,
                str(settings.database_url),
            )

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

        # Sanitize GitHub data before storage to prevent XSS (same as OAuth callback)
        from ..utils.sanitize import sanitize_github_data
        sanitized_github_data = sanitize_github_data(github_data)

        current_candidate.github_data = sanitized_github_data
        db.commit()

        return {
            "success": True,
            "message": "GitHub data refreshed",
            "github_data": GitHubInfo(
                username=sanitized_github_data["username"],
                connected_at=current_candidate.github_connected_at,
                top_repos=sanitized_github_data.get("top_repos"),
                total_repos=sanitized_github_data.get("public_repos"),
                total_contributions=sanitized_github_data.get("total_contributions"),
                languages=sanitized_github_data.get("languages"),
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


async def run_github_analysis_background(candidate_id: str):
    """
    Background task to run GitHub analysis for a candidate.
    Called automatically after GitHub OAuth connect.
    """
    from ..database import SessionLocal
    import asyncio

    logger.info(f"Starting background GitHub analysis for candidate {candidate_id}")

    db = SessionLocal()
    try:
        # Fetch candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate or not candidate.github_access_token:
            logger.warning(f"Cannot run analysis: candidate {candidate_id} not found or no GitHub token")
            return

        # Decrypt the stored token
        decrypted_token = decrypt_token(candidate.github_access_token)

        # Perform the analysis
        analysis = await github_analysis_service.analyze_profile(
            access_token=decrypted_token,
            username=candidate.github_username,
            include_private=True,
            max_repos=15,
        )

        # Store analysis in database
        existing_analysis = db.query(GitHubAnalysis).filter(
            GitHubAnalysis.candidate_id == candidate_id
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
                candidate_id=candidate_id,
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

        # Create growth tracking snapshot
        try:
            db_analysis = db.query(GitHubAnalysis).filter(
                GitHubAnalysis.candidate_id == candidate_id
            ).first()
            if db_analysis:
                growth_tracking_service.create_github_analysis_snapshot(
                    db=db,
                    candidate_id=candidate_id,
                    analysis=db_analysis,
                )
        except Exception as e:
            logger.warning(f"Failed to create GitHub analysis snapshot for {candidate_id}: {e}")

        logger.info(f"Completed background GitHub analysis for candidate {candidate_id}, score={analysis.overall_score}")

    except Exception as e:
        logger.error(f"Background GitHub analysis failed for {candidate_id}: {e}")
        db.rollback()
    finally:
        db.close()


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

        # Create growth tracking snapshot
        try:
            db_analysis = db.query(GitHubAnalysis).filter(
                GitHubAnalysis.candidate_id == current_candidate.id
            ).first()
            if db_analysis:
                growth_tracking_service.create_github_analysis_snapshot(
                    db=db,
                    candidate_id=current_candidate.id,
                    analysis=db_analysis,
                )
        except Exception as e:
            logger.warning(f"Failed to create GitHub analysis snapshot: {e}")

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


class OpportunityJobResponse(PydanticBaseModel):
    """A job opportunity with eligibility info for the student."""
    job_id: str
    job_title: str
    company_name: str
    company_logo: Optional[str] = None
    vertical: str
    role_type: Optional[str] = None
    location: Optional[str] = None
    eligible: bool
    reason: Optional[str] = None


class OpportunitiesResponse(PydanticBaseModel):
    """All active jobs grouped by student eligibility."""
    eligible_jobs: list[OpportunityJobResponse]
    not_eligible_jobs: list[OpportunityJobResponse]
    total_eligible: int
    total_not_eligible: int
    total: int


def _check_education_requirement(job: Job) -> Optional[str]:
    """Check if job title indicates an advanced degree requirement."""
    title_lower = job.title.lower()
    if "phd" in title_lower or "ph.d" in title_lower:
        return "PhD required"
    if "mba" in title_lower:
        return "MBA required"
    if "master" in title_lower and "master" not in title_lower.replace("master's", "").replace("masters", ""):
        return "Master's degree required"
    # Check for explicit "Master's" or "Masters" in title
    if re.search(r"\bmaster'?s?\b", title_lower):
        return "Master's degree required"
    return None


def _check_graduation_year(job: Job, candidate: Candidate) -> Optional[str]:
    """Check if job targets specific graduation years that don't match the candidate."""
    if not candidate.graduation_year:
        return None

    title = job.title
    # Match patterns like "Summer 2026", "Fall 2025", "Class of 2025", "2026 Graduates"
    year_patterns = re.findall(r'(?:summer|fall|spring|winter|class of|graduating)\s*(\d{4})|(\d{4})\s*(?:graduate|grad|intern)', title, re.IGNORECASE)
    years = set()
    for groups in year_patterns:
        for y in groups:
            if y:
                years.add(int(y))

    if years and candidate.graduation_year not in years:
        year_list = ", ".join(str(y) for y in sorted(years))
        return f"Targets {year_list} graduates"

    return None


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


@router.get("/me/opportunities", response_model=OpportunitiesResponse)
async def get_my_opportunities(
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get all active jobs grouped by the student's eligibility.
    Eligible = student has uploaded resume, transcript, and connected GitHub.
    """
    # Check the three profile prerequisites
    has_resume = bool(current_candidate.resume_url)
    has_transcript = bool(current_candidate.transcript_key)
    has_github = bool(current_candidate.github_username)
    profile_complete = has_resume and has_transcript and has_github

    # Build missing items list for reason strings
    missing_items = []
    if not has_resume:
        missing_items.append("resume")
    if not has_transcript:
        missing_items.append("transcript")
    if not has_github:
        missing_items.append("GitHub")

    # Query ALL active jobs with employer eagerly loaded
    jobs = db.query(Job).options(
        joinedload(Job.employer)
    ).filter(
        Job.is_active == True,
    ).order_by(Job.created_at.desc()).all()

    eligible_jobs = []
    not_eligible_jobs = []

    for job in jobs:
        job_response = OpportunityJobResponse(
            job_id=job.id,
            job_title=job.title,
            company_name=job.employer.company_name if job.employer else "Unknown",
            company_logo=job.employer.logo if job.employer else None,
            vertical=job.vertical.value if job.vertical else "",
            role_type=job.role_type.value if job.role_type else None,
            location=job.location,
            eligible=False,
            reason=None,
        )

        # Profile prerequisites gate (resume + transcript + GitHub)
        if not profile_complete:
            job_response.reason = f"Upload your {', '.join(missing_items)}"
            not_eligible_jobs.append(job_response)
            continue

        # Check education requirement
        edu_reason = _check_education_requirement(job)
        if edu_reason:
            job_response.reason = edu_reason
            not_eligible_jobs.append(job_response)
            continue

        # Check graduation year
        grad_reason = _check_graduation_year(job, current_candidate)
        if grad_reason:
            job_response.reason = grad_reason
            not_eligible_jobs.append(job_response)
            continue

        # All checks passed
        job_response.eligible = True
        eligible_jobs.append(job_response)

    return OpportunitiesResponse(
        eligible_jobs=eligible_jobs,
        not_eligible_jobs=not_eligible_jobs,
        total_eligible=len(eligible_jobs),
        total_not_eligible=len(not_eligible_jobs),
        total=len(jobs),
    )


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


@router.post("/me/skill-gap", response_model=CandidateSkillGapResponse, include_in_schema=False)
async def get_my_skill_gap(
    data: CandidateSkillGapRequest,
    current_candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Internal: Skill gap analysis is employer-only data.
    This endpoint is deprecated for students. Use employer endpoints instead.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Skill gap analysis is available to employers only"
    )
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

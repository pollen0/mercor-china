import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime
import uuid
import json

from ..database import get_db
from ..models.candidate import Candidate
from ..models.employer import Job
from ..schemas.candidate import (
    CandidateCreate,
    CandidateResponse,
    CandidateList,
    ResumeParseResult,
    ResumeResponse,
    ParsedResume,
    PersonalizedQuestion,
    WeChatAuthUrlResponse,
    WeChatLoginRequest,
    WeChatLoginResponse,
)
from ..services.resume import resume_service
from ..services.storage import storage_service
from ..services.wechat import wechat_service
from ..utils.auth import create_token, get_current_candidate, get_current_employer
from ..utils.rate_limit import limiter, RateLimits
from ..config import settings

logger = logging.getLogger("zhimian.candidates")
router = APIRouter()


def generate_cuid() -> str:
    return f"c{uuid.uuid4().hex[:24]}"


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Candidate).filter(Candidate.email == candidate_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    candidate = Candidate(
        id=generate_cuid(),
        name=candidate_data.name,
        email=candidate_data.email,
        phone=candidate_data.phone,
        target_roles=candidate_data.target_roles,
    )

    try:
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    return candidate


@router.get("/", response_model=CandidateList)
async def list_candidates(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """List candidates (employer only)."""
    query = db.query(Candidate)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter))
        )

    total = query.count()
    candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()

    return CandidateList(candidates=candidates, total=total)


@router.get("/me", response_model=CandidateResponse)
async def get_current_candidate_profile(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the current authenticated candidate's profile."""
    return current_candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """Get a candidate by ID (employer only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人不存在"
        )

    return candidate


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
    Upload and parse a candidate's resume.
    Supports PDF and DOCX formats.
    Candidate can only upload their own resume.
    """
    # Verify candidate is uploading their own resume
    if current_candidate.id != candidate_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能上传自己的简历"
        )

    candidate = current_candidate

    # Validate file type
    filename = file.filename or "resume"
    if not (filename.lower().endswith('.pdf') or filename.lower().endswith('.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传PDF或DOCX格式的简历"
        )

    # Read file content
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件读取失败: {str(e)}"
        )

    # Check file size (max 10MB)
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件大小不能超过10MB"
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
            detail=f"简历解析失败: {str(e)}"
        )

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法从简历中提取文本，请确保文件不是扫描件或图片格式"
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
            storage_service.client._bucket_name if hasattr(storage_service.client, '_bucket_name') else "zhimian-videos",
            storage_key,
            ExtraArgs={"ContentType": content_type}
        )
        resume_url = storage_key
    except Exception as e:
        logger.error(f"Resume upload error for candidate {candidate_id}: {e}")
        resume_url = None  # Continue without storage

    # Parse resume with AI
    try:
        parsed_data = await resume_service.parse_resume(raw_text)
    except Exception as e:
        logger.error(f"Resume AI parsing error for candidate {candidate_id}: {e}")
        parsed_data = ParsedResume()

    # Update candidate record
    candidate.resume_url = resume_url
    candidate.resume_raw_text = raw_text
    candidate.resume_parsed_data = parsed_data.model_dump() if parsed_data else None
    candidate.resume_uploaded_at = datetime.utcnow()

    # Auto-update candidate name/email/phone if parsed and missing
    if parsed_data.name and not candidate.name:
        candidate.name = parsed_data.name
    if parsed_data.email and not candidate.email:
        candidate.email = parsed_data.email
    if parsed_data.phone and not candidate.phone:
        candidate.phone = parsed_data.phone

    db.commit()

    return ResumeParseResult(
        success=True,
        message="简历上传解析成功",
        resume_url=resume_url,
        parsed_data=parsed_data,
        raw_text_preview=raw_text[:500] if raw_text else None
    )


@router.get("/me/resume", response_model=ResumeResponse)
async def get_my_resume(
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the current authenticated candidate's resume."""
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


@router.get("/{candidate_id}/resume", response_model=ResumeResponse)
async def get_resume(
    candidate_id: str,
    db: Session = Depends(get_db),
    _employer = Depends(get_current_employer),
):
    """Get the parsed resume data for a candidate (employer only)."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人不存在"
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
    Generate personalized interview questions based on the candidate's resume.
    Optionally provide a job_id for more targeted questions.
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人不存在"
        )

    if not candidate.resume_parsed_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="候选人尚未上传简历"
        )

    # Get parsed resume
    try:
        parsed_resume = ParsedResume(**candidate.resume_parsed_data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="简历数据解析失败"
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


# ==================== WECHAT OAUTH ENDPOINTS ====================

@router.get("/auth/wechat/url", response_model=WeChatAuthUrlResponse)
@limiter.limit(RateLimits.AUTH_WECHAT)
async def get_wechat_auth_url(
    request: Request,
    redirect_uri: Optional[str] = None,
):
    """
    Get WeChat authorization URL for web login.

    Args:
        redirect_uri: Optional custom redirect URI (defaults to frontend callback)

    Returns:
        WeChat authorization URL and CSRF state token
    """
    if not wechat_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="微信登录未配置"
        )

    # Generate CSRF state token
    import secrets
    state = secrets.token_urlsafe(16)

    # Default redirect URI
    if not redirect_uri:
        redirect_uri = f"{settings.frontend_url}/auth/wechat/callback"

    auth_url = wechat_service.get_web_auth_url(
        redirect_uri=redirect_uri,
        state=state,
    )

    return WeChatAuthUrlResponse(
        auth_url=auth_url,
        state=state,
    )


@router.post("/auth/wechat/login", response_model=WeChatLoginResponse)
@limiter.limit(RateLimits.AUTH_WECHAT)
async def wechat_login(
    request: Request,
    data: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Complete WeChat OAuth login.

    Exchange authorization code for user info and create/login candidate.

    Args:
        data: WeChat authorization code and optional state for CSRF validation

    Returns:
        Candidate info with JWT token
    """
    if not wechat_service.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="微信登录未配置"
        )

    # Exchange code for user info
    try:
        wechat_user = await wechat_service.authenticate(
            code=data.code,
            is_mini_program=data.is_mini_program,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"微信授权失败: {str(e)}"
        )

    # Check if user exists
    candidate = db.query(Candidate).filter(
        Candidate.wechat_open_id == wechat_user.openid
    ).first()

    is_new_user = False

    if candidate:
        # Existing user - update info if available
        if wechat_user.nickname and not candidate.name:
            candidate.name = wechat_user.nickname
        if wechat_user.unionid:
            candidate.wechat_union_id = wechat_user.unionid
        db.commit()
    else:
        # New user - create candidate
        is_new_user = True

        # Generate placeholder email if not available
        placeholder_email = f"wx_{wechat_user.openid[:16]}@wechat.placeholder"

        candidate = Candidate(
            id=generate_cuid(),
            name=wechat_user.nickname or "微信用户",
            email=placeholder_email,
            phone="",  # Will need to be updated later
            wechat_open_id=wechat_user.openid,
            wechat_union_id=wechat_user.unionid,
            target_roles=[],
        )

        try:
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
        except IntegrityError:
            db.rollback()
            # Race condition - user was created by another request
            candidate = db.query(Candidate).filter(
                Candidate.wechat_open_id == wechat_user.openid
            ).first()
            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败，请重试"
                )
            is_new_user = False

    # Generate JWT token for candidate
    token = create_token(
        subject=candidate.id,
        token_type="candidate",
        expires_hours=settings.jwt_expiry_hours,
    )

    return WeChatLoginResponse(
        candidate=CandidateResponse(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone or "",
            target_roles=candidate.target_roles or [],
            resume_url=candidate.resume_url,
            created_at=candidate.created_at,
        ),
        token=token,
        is_new_user=is_new_user,
    )


@router.post("/auth/wechat/mini-program", response_model=WeChatLoginResponse)
async def wechat_mini_program_login(
    js_code: str,
    db: Session = Depends(get_db)
):
    """
    WeChat Mini Program login using js_code from wx.login().

    Args:
        js_code: Code returned from wx.login() in Mini Program

    Returns:
        Candidate info with JWT token
    """
    # Reuse the main login endpoint with is_mini_program=True
    return await wechat_login(
        data=WeChatLoginRequest(code=js_code, is_mini_program=True),
        db=db,
    )

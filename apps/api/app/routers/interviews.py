from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
import json

from ..database import get_db
from ..models import (
    InterviewSession,
    InterviewResponse,
    InterviewQuestion,
    Candidate,
    Job,
    InterviewStatus,
    InviteToken,
)
from ..schemas.interview import (
    InterviewStart,
    ResponseSubmit,
    InterviewStartResponse,
    ResponseSubmitResult,
    InterviewSessionResponse,
    InterviewResults,
    InterviewListResponse,
    QuestionInfo,
    ResponseDetail,
    ScoreDetails,
    UploadUrlResponse,
    InviteTokenCreate,
    InviteTokenResponse,
    InviteTokenList,
    InviteValidation,
    CandidateRegisterAndStart,
)
from ..services.storage import storage_service
from ..services.tasks import process_interview_response, generate_interview_summary, send_completion_emails

router = APIRouter()


def generate_cuid(prefix: str = "i") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(
    data: InterviewStart,
    db: Session = Depends(get_db)
):
    """Start a new interview session."""
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == data.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="候选人不存在"
        )

    # Verify job exists
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )

    # Check for existing active interview
    existing = db.query(InterviewSession).filter(
        InterviewSession.candidate_id == data.candidate_id,
        InterviewSession.job_id == data.job_id,
        InterviewSession.status.in_([InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS])
    ).first()

    if existing:
        # Return existing session
        questions = db.query(InterviewQuestion).filter(
            (InterviewQuestion.job_id == data.job_id) |
            (InterviewQuestion.is_default == True)
        ).order_by(InterviewQuestion.order).all()

        return InterviewStartResponse(
            session_id=existing.id,
            questions=[
                QuestionInfo(
                    index=i,
                    text=q.text,
                    text_zh=q.text_zh,
                    category=q.category,
                )
                for i, q in enumerate(questions)
            ],
            job_title=job.title,
            company_name=job.employer.company_name,
        )

    # Create new session
    session = InterviewSession(
        id=generate_cuid(),
        status=InterviewStatus.IN_PROGRESS,
        started_at=datetime.utcnow(),
        candidate_id=data.candidate_id,
        job_id=data.job_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Get questions
    questions = db.query(InterviewQuestion).filter(
        (InterviewQuestion.job_id == data.job_id) |
        (InterviewQuestion.is_default == True)
    ).order_by(InterviewQuestion.order).all()

    # If no questions exist, seed defaults
    if not questions:
        from ..schemas.question import DEFAULT_QUESTIONS
        for q_data in DEFAULT_QUESTIONS:
            question = InterviewQuestion(
                id=f"q{uuid.uuid4().hex[:24]}",
                text=q_data["text"],
                text_zh=q_data["text_zh"],
                category=q_data["category"],
                order=q_data["order"],
                is_default=True,
                job_id=None,
            )
            db.add(question)
            questions.append(question)
        db.commit()

    return InterviewStartResponse(
        session_id=session.id,
        questions=[
            QuestionInfo(
                index=i,
                text=q.text,
                text_zh=q.text_zh,
                category=q.category,
            )
            for i, q in enumerate(questions)
        ],
        job_title=job.title,
        company_name=job.employer.company_name,
    )


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview(session_id: str, db: Session = Depends(get_db)):
    """Get interview session details."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
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
                    score_details = ScoreDetails(
                        relevance=analysis_data["scores"]["relevance"],
                        clarity=analysis_data["scores"]["clarity"],
                        depth=analysis_data["scores"]["depth"],
                        communication=analysis_data["scores"]["communication"],
                        job_fit=analysis_data["scores"]["job_fit"],
                        overall=resp.ai_score or 0,
                        analysis=analysis_data.get("analysis", ""),
                        strengths=analysis_data.get("strengths", []),
                        improvements=analysis_data.get("improvements", []),
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
        company_name=session.job.employer.company_name,
        responses=sorted(responses, key=lambda x: x.question_index),
    )


@router.get("/{session_id}/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    session_id: str,
    question_index: int,
    db: Session = Depends(get_db)
):
    """Get a presigned URL for direct video upload."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试已完成或已取消"
        )

    upload_url, storage_key = storage_service.get_upload_url(session_id, question_index)

    return UploadUrlResponse(
        upload_url=upload_url,
        storage_key=storage_key,
        expires_in=3600,
    )


@router.post("/{session_id}/response", response_model=ResponseSubmitResult)
async def submit_response(
    session_id: str,
    question_index: int,
    background_tasks: BackgroundTasks,
    video: Optional[UploadFile] = File(None),
    video_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Submit a video response for a question.
    Either upload a video file or provide a video_key from direct upload.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试已完成或已取消"
        )

    # Get question text
    questions = db.query(InterviewQuestion).filter(
        (InterviewQuestion.job_id == session.job_id) |
        (InterviewQuestion.is_default == True)
    ).order_by(InterviewQuestion.order).all()

    if question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="问题索引无效"
        )

    question = questions[question_index]

    # Handle video upload or key
    storage_key = video_key
    if video and not video_key:
        content = await video.read()
        storage_key = await storage_service.upload_video_bytes(
            data=content,
            session_id=session_id,
            question_index=question_index,
        )

    if not storage_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供视频文件或视频key"
        )

    # Check for existing response
    existing_response = db.query(InterviewResponse).filter(
        InterviewResponse.session_id == session_id,
        InterviewResponse.question_index == question_index
    ).first()

    if existing_response:
        # Update existing response
        existing_response.video_url = storage_key
        existing_response.transcription = None
        existing_response.ai_score = None
        existing_response.ai_analysis = None
        response = existing_response
    else:
        # Create new response
        response = InterviewResponse(
            id=f"r{uuid.uuid4().hex[:24]}",
            question_index=question_index,
            question_text=question.text_zh or question.text,
            video_url=storage_key,
            session_id=session_id,
        )
        db.add(response)

    db.commit()
    db.refresh(response)

    # Queue background processing
    from ..config import settings
    background_tasks.add_task(
        process_interview_response,
        response_id=response.id,
        video_key=storage_key,
        job_title=session.job.title,
        job_requirements=session.job.requirements or [],
        db_url=settings.database_url,
        question_text=question.text_zh or question.text,
    )

    return ResponseSubmitResult(
        response_id=response.id,
        question_index=question_index,
        status="processing",
        video_url=storage_service.get_signed_url(storage_key),
    )


@router.post("/{session_id}/complete", response_model=InterviewResults)
async def complete_interview(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Mark interview as complete and trigger final scoring."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    if session.status == InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试已完成"
        )

    # Update session status
    session.status = InterviewStatus.COMPLETED
    session.completed_at = datetime.utcnow()

    # Calculate total score from responses
    responses = db.query(InterviewResponse).filter(
        InterviewResponse.session_id == session_id
    ).all()

    scored_responses = [r for r in responses if r.ai_score is not None]
    if scored_responses:
        session.total_score = sum(r.ai_score for r in scored_responses) / len(scored_responses)

    db.commit()

    # Queue background tasks for summary generation and emails
    from ..config import settings
    background_tasks.add_task(
        generate_interview_summary,
        session_id=session_id,
        db_url=settings.database_url,
    )
    background_tasks.add_task(
        send_completion_emails,
        session_id=session_id,
        db_url=settings.database_url,
    )

    db.refresh(session)

    # Build response
    response_details = []
    for resp in responses:
        video_url = None
        if resp.video_url:
            video_url = storage_service.get_signed_url(resp.video_url)

        response_details.append(ResponseDetail(
            id=resp.id,
            question_index=resp.question_index,
            question_text=resp.question_text,
            video_url=video_url,
            transcription=resp.transcription,
            ai_score=resp.ai_score,
            ai_analysis=resp.ai_analysis,
            duration_seconds=resp.duration_seconds,
            created_at=resp.created_at,
        ))

    summary_data = {}
    if session.ai_summary:
        try:
            summary_data = json.loads(session.ai_summary)
        except json.JSONDecodeError:
            pass

    return InterviewResults(
        session_id=session.id,
        status=session.status.value,
        total_score=session.total_score,
        ai_summary=summary_data.get("summary"),
        recommendation=summary_data.get("recommendation"),
        overall_strengths=summary_data.get("overall_strengths", []),
        overall_improvements=summary_data.get("overall_improvements", []),
        responses=sorted(response_details, key=lambda x: x.question_index),
    )


@router.get("/{session_id}/results", response_model=InterviewResults)
async def get_interview_results(session_id: str, db: Session = Depends(get_db)):
    """Get the final results of a completed interview."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    responses = db.query(InterviewResponse).filter(
        InterviewResponse.session_id == session_id
    ).order_by(InterviewResponse.question_index).all()

    response_details = []
    for resp in responses:
        video_url = None
        if resp.video_url:
            video_url = storage_service.get_signed_url(resp.video_url)

        score_details = None
        if resp.ai_analysis:
            try:
                analysis_data = json.loads(resp.ai_analysis)
                if "scores" in analysis_data:
                    score_details = ScoreDetails(
                        relevance=analysis_data["scores"]["relevance"],
                        clarity=analysis_data["scores"]["clarity"],
                        depth=analysis_data["scores"]["depth"],
                        communication=analysis_data["scores"]["communication"],
                        job_fit=analysis_data["scores"]["job_fit"],
                        overall=resp.ai_score or 0,
                        analysis=analysis_data.get("analysis", ""),
                        strengths=analysis_data.get("strengths", []),
                        improvements=analysis_data.get("improvements", []),
                    )
            except json.JSONDecodeError:
                pass

        response_details.append(ResponseDetail(
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

    summary_data = {}
    if session.ai_summary:
        try:
            summary_data = json.loads(session.ai_summary)
        except json.JSONDecodeError:
            pass

    return InterviewResults(
        session_id=session.id,
        status=session.status.value,
        total_score=session.total_score,
        ai_summary=summary_data.get("summary"),
        recommendation=summary_data.get("recommendation"),
        overall_strengths=summary_data.get("overall_strengths", []),
        overall_improvements=summary_data.get("overall_improvements", []),
        responses=response_details,
    )


# ==================== INVITE TOKEN ENDPOINTS ====================

def generate_invite_token() -> str:
    """Generate a secure invite token."""
    import secrets
    return secrets.token_urlsafe(32)


@router.get("/invite/validate/{token}", response_model=InviteValidation)
async def validate_invite_token(token: str, db: Session = Depends(get_db)):
    """Validate an invite token and return job details."""
    invite = db.query(InviteToken).filter(
        InviteToken.token == token,
        InviteToken.is_active == True
    ).first()

    if not invite:
        return InviteValidation(valid=False, error="Invalid or expired invite link")

    # Check expiration
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        return InviteValidation(valid=False, error="This invite link has expired")

    # Check max uses
    if invite.max_uses > 0 and invite.used_count >= invite.max_uses:
        return InviteValidation(valid=False, error="This invite link has reached its usage limit")

    return InviteValidation(
        valid=True,
        job_id=invite.job_id,
        job_title=invite.job.title,
        company_name=invite.job.employer.company_name,
    )


@router.post("/invite/register-and-start", response_model=InterviewStartResponse)
async def register_and_start_interview(
    data: CandidateRegisterAndStart,
    db: Session = Depends(get_db)
):
    """
    Self-registration flow: Register candidate and start interview in one step.
    Used with invite tokens.
    """
    # Validate invite token
    invite = db.query(InviteToken).filter(
        InviteToken.token == data.invite_token,
        InviteToken.is_active == True
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired invite link"
        )

    # Check expiration
    if invite.expires_at and invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite link has expired"
        )

    # Check max uses
    if invite.max_uses > 0 and invite.used_count >= invite.max_uses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite link has reached its usage limit"
        )

    # Check if candidate exists by email
    candidate = db.query(Candidate).filter(Candidate.email == data.email).first()

    if not candidate:
        # Create new candidate
        candidate = Candidate(
            id=generate_cuid("c"),
            name=data.name,
            email=data.email,
            phone=data.phone,
            target_roles=[],
        )
        db.add(candidate)
        db.flush()
    else:
        # Update existing candidate's info
        candidate.name = data.name
        candidate.phone = data.phone

    # Check for existing active interview
    existing = db.query(InterviewSession).filter(
        InterviewSession.candidate_id == candidate.id,
        InterviewSession.job_id == invite.job_id,
        InterviewSession.status.in_([InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS])
    ).first()

    if existing:
        # Return existing session
        questions = db.query(InterviewQuestion).filter(
            (InterviewQuestion.job_id == invite.job_id) |
            (InterviewQuestion.is_default == True)
        ).order_by(InterviewQuestion.order).all()

        db.commit()

        return InterviewStartResponse(
            session_id=existing.id,
            questions=[
                QuestionInfo(
                    index=i,
                    text=q.text,
                    text_zh=q.text_zh,
                    category=q.category,
                )
                for i, q in enumerate(questions)
            ],
            job_title=invite.job.title,
            company_name=invite.job.employer.company_name,
        )

    # Create new session
    session = InterviewSession(
        id=generate_cuid("i"),
        status=InterviewStatus.IN_PROGRESS,
        started_at=datetime.utcnow(),
        candidate_id=candidate.id,
        job_id=invite.job_id,
    )
    db.add(session)

    # Increment invite usage
    invite.used_count += 1

    db.commit()
    db.refresh(session)

    # Get questions
    questions = db.query(InterviewQuestion).filter(
        (InterviewQuestion.job_id == invite.job_id) |
        (InterviewQuestion.is_default == True)
    ).order_by(InterviewQuestion.order).all()

    # If no questions exist, seed defaults
    if not questions:
        from ..schemas.question import DEFAULT_QUESTIONS
        for q_data in DEFAULT_QUESTIONS:
            question = InterviewQuestion(
                id=generate_cuid("q"),
                text=q_data["text"],
                text_zh=q_data["text_zh"],
                category=q_data["category"],
                order=q_data["order"],
                is_default=True,
                job_id=None,
            )
            db.add(question)
            questions.append(question)
        db.commit()

    return InterviewStartResponse(
        session_id=session.id,
        questions=[
            QuestionInfo(
                index=i,
                text=q.text,
                text_zh=q.text_zh,
                category=q.category,
            )
            for i, q in enumerate(questions)
        ],
        job_title=invite.job.title,
        company_name=invite.job.employer.company_name,
    )

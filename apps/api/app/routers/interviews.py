import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
import json

from ..database import get_db
from ..utils.rate_limit import limiter, RateLimits
from ..utils.auth import get_current_candidate
from ..models import (
    InterviewSession,
    InterviewResponse,
    InterviewQuestion,
    Candidate,
    Job,
    InterviewStatus,
    InviteToken,
    FollowupQueue,
    FollowupQueueStatus,
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
    PracticeFeedback,
    FollowupResponse,
    AskFollowupRequest,
    FollowupQuestionInfo,
)
from ..services.storage import storage_service
from ..services.tasks import process_interview_response, generate_interview_summary, send_completion_emails, process_match_after_interview
from ..services.scoring import scoring_service
from ..services.transcription import transcription_service
from ..services.cache import cache_service

logger = logging.getLogger("zhimian.interviews")
router = APIRouter()


def generate_cuid(prefix: str = "i") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


@router.post("/start", response_model=InterviewStartResponse)
@limiter.limit(RateLimits.INTERVIEW_START)
async def start_interview(
    request: Request,
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

    # If job_id provided, verify job exists
    job = None
    job_title = "General Interview" if not data.is_practice else "Practice Interview"
    company_name = "ZhiMian"

    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="职位不存在"
            )
        job_title = job.title if not data.is_practice else f"Practice: {job.title}"
        company_name = job.employer.company_name

    # For practice mode, always create new session (no reuse)
    # For real interviews, check for existing active interview
    existing = None
    if not data.is_practice:
        existing_query = db.query(InterviewSession).filter(
            InterviewSession.candidate_id == data.candidate_id,
            InterviewSession.is_practice == False,
            InterviewSession.status.in_([InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS])
        )
        if data.job_id:
            existing_query = existing_query.filter(InterviewSession.job_id == data.job_id)
        else:
            existing_query = existing_query.filter(InterviewSession.job_id.is_(None))

        existing = existing_query.first()

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
            job_title=job_title,
            company_name=company_name,
            is_practice=existing.is_practice,
        )

    # Create new session
    session = InterviewSession(
        id=generate_cuid(),
        status=InterviewStatus.IN_PROGRESS,
        is_practice=data.is_practice,
        started_at=datetime.utcnow(),
        candidate_id=data.candidate_id,
        job_id=data.job_id,  # Can be None for general interview
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Get questions (default questions for general interview)
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
        job_title=job_title,
        company_name=company_name,
        is_practice=session.is_practice,
    )


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview(
    session_id: str,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get interview session details (candidate only - their own sessions)."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    # Try cache first for completed interviews
    cached = cache_service.get_interview_session(session_id)
    if cached and cached.get("status") == InterviewStatus.COMPLETED.value:
        return InterviewSessionResponse(**cached)

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

    response_data = InterviewSessionResponse(
        id=session.id,
        status=session.status.value,
        is_practice=session.is_practice,
        total_score=session.total_score,
        ai_summary=session.ai_summary,
        started_at=session.started_at,
        completed_at=session.completed_at,
        created_at=session.created_at,
        candidate_id=session.candidate_id,
        candidate_name=session.candidate.name,
        job_id=session.job_id,
        job_title=session.job.title if session.job else "Practice Interview",
        company_name=session.job.employer.company_name if session.job else "ZhiMian",
        responses=sorted(responses, key=lambda x: x.question_index),
    )

    # Cache completed interviews (they don't change)
    if session.status == InterviewStatus.COMPLETED:
        cache_service.set_interview_session(session_id, response_data.model_dump(mode="json"))

    return response_data


@router.get("/{session_id}/upload-url", response_model=UploadUrlResponse)
@limiter.limit(RateLimits.INTERVIEW_SUBMIT)
async def get_upload_url(
    request: Request,
    session_id: str,
    question_index: int,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
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

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
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
@limiter.limit(RateLimits.INTERVIEW_SUBMIT)
async def submit_response(
    request: Request,
    session_id: str,
    question_index: int,
    background_tasks: BackgroundTasks,
    video: Optional[UploadFile] = File(None),
    video_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
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

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
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
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
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

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    if session.status == InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试已完成"
        )

    # Invalidate any existing cache for this session
    cache_service.invalidate_interview(session_id)

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

    # Queue background tasks for summary generation, emails, and match calculation
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
    # Calculate match score after interview
    background_tasks.add_task(
        process_match_after_interview,
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
async def get_interview_results(
    session_id: str,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """Get the final results of a completed interview (candidate only)."""
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
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


# ==================== PRACTICE MODE ENDPOINTS ====================

@router.get("/{session_id}/practice-feedback/{response_id}", response_model=PracticeFeedback)
async def get_practice_feedback(
    session_id: str,
    response_id: str,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Get immediate feedback for a practice mode response.
    This endpoint performs synchronous scoring and returns detailed feedback.
    """
    # Get session and verify it's a practice session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    if not session.is_practice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="此端点仅适用于练习模式"
        )

    # Get the response
    response = db.query(InterviewResponse).filter(
        InterviewResponse.id == response_id,
        InterviewResponse.session_id == session_id
    ).first()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="回答不存在"
        )

    # Check if already scored
    if response.ai_score is not None and response.ai_analysis:
        try:
            analysis_data = json.loads(response.ai_analysis)
            return PracticeFeedback(
                response_id=response.id,
                question_index=response.question_index,
                score_details=ScoreDetails(
                    communication=analysis_data["scores"]["communication"] / 10,
                    problem_solving=analysis_data["scores"]["problem_solving"] / 10,
                    domain_knowledge=analysis_data["scores"]["domain_knowledge"] / 10,
                    motivation=analysis_data["scores"]["motivation"] / 10,
                    culture_fit=analysis_data["scores"]["culture_fit"] / 10,
                    overall=response.ai_score,
                    analysis=analysis_data.get("analysis", ""),
                    strengths=analysis_data.get("strengths", []),
                    concerns=analysis_data.get("concerns", []),
                    highlight_quotes=analysis_data.get("highlight_quotes", []),
                ),
                tips=analysis_data.get("tips", []),
                sample_answer=analysis_data.get("sample_answer"),
            )
        except (json.JSONDecodeError, KeyError):
            pass  # Re-score if parsing fails

    # Get transcription if not available
    if not response.transcription:
        if not response.video_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="视频尚未上传"
            )
        # Download video and transcribe
        try:
            video_bytes = await storage_service.download_video(response.video_url)
            transcription = await transcription_service.transcribe_bytes(video_bytes)
            response.transcription = transcription
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"转录失败: {str(e)}"
            )

    # Get job info for context
    job_title = "General"
    job_requirements = []
    if session.job:
        job_title = session.job.title
        job_requirements = session.job.requirements or []

    # Get immediate feedback
    try:
        feedback = await scoring_service.get_immediate_feedback(
            question=response.question_text,
            transcript=response.transcription,
            job_title=job_title,
            job_requirements=job_requirements,
            language="zh"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评分失败: {str(e)}"
        )

    score_result = feedback["score_result"]

    # Store the analysis for future retrieval
    analysis_data = {
        "scores": {
            "communication": int(score_result.communication * 10),
            "problem_solving": int(score_result.problem_solving * 10),
            "domain_knowledge": int(score_result.domain_knowledge * 10),
            "motivation": int(score_result.motivation * 10),
            "culture_fit": int(score_result.culture_fit * 10),
        },
        "analysis": score_result.analysis,
        "strengths": score_result.strengths,
        "concerns": score_result.concerns,
        "tips": feedback.get("tips", []),
        "sample_answer": feedback.get("sample_answer"),
    }

    response.ai_score = score_result.overall
    response.ai_analysis = json.dumps(analysis_data, ensure_ascii=False)
    db.commit()

    return PracticeFeedback(
        response_id=response.id,
        question_index=response.question_index,
        score_details=ScoreDetails(
            communication=score_result.communication,
            problem_solving=score_result.problem_solving,
            domain_knowledge=score_result.domain_knowledge,
            motivation=score_result.motivation,
            culture_fit=score_result.culture_fit,
            overall=score_result.overall,
            analysis=score_result.analysis,
            strengths=score_result.strengths,
            concerns=score_result.concerns,
            highlight_quotes=[],
        ),
        tips=feedback.get("tips", []),
        sample_answer=feedback.get("sample_answer"),
    )


# ==================== FOLLOW-UP QUESTION ENDPOINTS ====================

@router.get("/{session_id}/followup", response_model=FollowupResponse)
async def get_followup_questions(
    session_id: str,
    question_index: int,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Check if follow-up questions are available for a given question.
    Call this after submitting a response to see if AI generated follow-ups.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    # Don't show follow-ups for practice mode
    if session.is_practice:
        return FollowupResponse(
            has_followups=False,
            question_index=question_index,
            followup_questions=[],
        )

    # Check for pending follow-up queue
    queue = db.query(FollowupQueue).filter(
        FollowupQueue.session_id == session_id,
        FollowupQueue.question_index == question_index,
        FollowupQueue.status == FollowupQueueStatus.PENDING
    ).first()

    if not queue or not queue.generated_questions:
        return FollowupResponse(
            has_followups=False,
            question_index=question_index,
            followup_questions=[],
        )

    return FollowupResponse(
        has_followups=True,
        question_index=question_index,
        followup_questions=queue.generated_questions,
        queue_id=queue.id,
    )


@router.post("/{session_id}/followup/ask", response_model=FollowupQuestionInfo)
async def ask_followup(
    session_id: str,
    data: AskFollowupRequest,
    question_index: int,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Ask a specific follow-up question. This marks the follow-up as asked
    and returns the question info so the candidate can record their response.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    if session.is_practice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="练习模式不支持追问"
        )

    # Get the follow-up queue
    queue = db.query(FollowupQueue).filter(
        FollowupQueue.session_id == session_id,
        FollowupQueue.question_index == question_index,
        FollowupQueue.status == FollowupQueueStatus.PENDING
    ).first()

    if not queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有可用的追问问题"
        )

    if data.followup_index >= len(queue.generated_questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="追问索引无效"
        )

    # Mark as asked
    queue.selected_index = data.followup_index
    queue.status = FollowupQueueStatus.ASKED
    db.commit()

    return FollowupQuestionInfo(
        queue_id=queue.id,
        question_index=question_index,
        followup_index=data.followup_index,
        question_text=queue.generated_questions[data.followup_index],
        is_followup=True,
    )


@router.post("/{session_id}/followup/skip")
async def skip_followup(
    session_id: str,
    question_index: int,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Skip the follow-up questions and proceed to the next main question.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    # Mark any pending follow-up as skipped
    queue = db.query(FollowupQueue).filter(
        FollowupQueue.session_id == session_id,
        FollowupQueue.question_index == question_index,
        FollowupQueue.status == FollowupQueueStatus.PENDING
    ).first()

    if queue:
        queue.status = FollowupQueueStatus.SKIPPED
        db.commit()

    return {"status": "skipped", "question_index": question_index}


@router.post("/{session_id}/followup/response", response_model=ResponseSubmitResult)
async def submit_followup_response(
    session_id: str,
    queue_id: str,
    background_tasks: BackgroundTasks,
    video: Optional[UploadFile] = File(None),
    video_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Submit a video response for a follow-up question.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="面试会话不存在"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此面试会话"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="面试已完成或已取消"
        )

    # Get the follow-up queue
    queue = db.query(FollowupQueue).filter(
        FollowupQueue.id == queue_id,
        FollowupQueue.session_id == session_id,
        FollowupQueue.status == FollowupQueueStatus.ASKED
    ).first()

    if not queue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="追问问题不存在或未被选中"
        )

    # Get the parent response (the original answer to the base question)
    parent_response = db.query(InterviewResponse).filter(
        InterviewResponse.session_id == session_id,
        InterviewResponse.question_index == queue.question_index,
        InterviewResponse.is_followup == False
    ).first()

    if not parent_response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原始回答不存在"
        )

    # Handle video upload
    storage_key = video_key
    if video and not video_key:
        content = await video.read()
        # Use a distinct key for follow-up responses
        storage_key = await storage_service.upload_video_bytes(
            data=content,
            session_id=session_id,
            question_index=queue.question_index,
            suffix="_followup"
        )

    if not storage_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="必须提供视频文件或视频key"
        )

    # Create the follow-up response
    followup_response = InterviewResponse(
        id=f"r{uuid.uuid4().hex[:24]}",
        question_index=queue.question_index,  # Same index as parent
        question_text=queue.generated_questions[queue.selected_index],
        video_url=storage_key,
        session_id=session_id,
        is_followup=True,
        parent_response_id=parent_response.id,
    )
    db.add(followup_response)
    db.commit()
    db.refresh(followup_response)

    # Queue background processing
    from ..config import settings
    background_tasks.add_task(
        process_interview_response,
        response_id=followup_response.id,
        video_key=storage_key,
        job_title=session.job.title if session.job else "General",
        job_requirements=session.job.requirements or [] if session.job else [],
        db_url=settings.database_url,
        question_text=followup_response.question_text,
    )

    return ResponseSubmitResult(
        response_id=followup_response.id,
        question_index=queue.question_index,
        status="processing",
        video_url=storage_service.get_signed_url(storage_key),
    )


# ==================== INVITE TOKEN ENDPOINTS ====================

def generate_invite_token() -> str:
    """Generate a secure invite token."""
    import secrets
    return secrets.token_urlsafe(32)


@router.get("/invite/validate/{token}", response_model=InviteValidation)
@limiter.limit("10/minute")
async def validate_invite_token(request: Request, token: str, db: Session = Depends(get_db)):
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

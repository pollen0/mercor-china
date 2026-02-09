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
    CodingChallenge,
    CandidateVerticalProfile,
    VerticalProfileStatus,
    Vertical,
    RoleType,
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
    VerticalInterviewStart,
    VerticalProfileResponse,
)
from ..schemas.coding_challenge import (
    CodeSubmitRequest,
    CodeExecutionResponse,
    CodingFeedback,
    CodingQuestionInfo,
)
from ..services.storage import storage_service
from ..services.tasks import process_interview_response, generate_interview_summary, send_completion_emails, process_match_after_interview, process_coding_response
from ..services.scoring import scoring_service
from ..services.transcription import transcription_service
from ..services.cache import cache_service
from ..services.code_execution import code_execution_service

logger = logging.getLogger("pathway.interviews")
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
            detail="Candidate not found"
        )

    # If job_id provided, verify job exists
    job = None
    job_title = "General Interview" if not data.is_practice else "Practice Interview"
    company_name = "Pathway"

    if data.job_id:
        job = db.query(Job).filter(Job.id == data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
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
                    category=q.category,
                    question_type=q.question_type or "video",
                    coding_challenge_id=q.coding_challenge_id,
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

    # Get questions - prefer job-specific, fall back to defaults
    if data.job_id:
        # For job-specific interviews, use job questions first
        job_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.job_id == data.job_id
        ).order_by(InterviewQuestion.order).all()

        if job_questions:
            base_questions = job_questions
        else:
            # No job-specific questions, use defaults
            base_questions = db.query(InterviewQuestion).filter(
                InterviewQuestion.is_default == True
            ).order_by(InterviewQuestion.order).all()
    else:
        # General interview - use defaults
        base_questions = db.query(InterviewQuestion).filter(
            InterviewQuestion.is_default == True
        ).order_by(InterviewQuestion.order).all()

    # If no questions exist, seed defaults
    if not base_questions:
        from ..schemas.question import DEFAULT_QUESTIONS
        for q_data in DEFAULT_QUESTIONS:
            question = InterviewQuestion(
                id=f"q{uuid.uuid4().hex[:24]}",
                text=q_data["text"],
                category=q_data["category"],
                order=q_data["order"],
                is_default=True,
                job_id=None,
            )
            db.add(question)
            base_questions.append(question)
        db.commit()

    # Build question list - start with base questions
    question_list = []
    for i, q in enumerate(base_questions[:2]):  # Take first 2 base questions
        question_list.append(QuestionInfo(
            index=i,
            text=q.text,
            category=q.category,
            question_type=q.question_type or "video",
            coding_challenge_id=q.coding_challenge_id,
        ))

    # Generate ADAPTIVE personalized questions using ALL available candidate data
    # Priority: Resume + GitHub + Transcript for comprehensive personalization
    personalized_questions = []
    has_adaptive_data = (
        candidate.resume_parsed_data or
        candidate.github_data or
        candidate.courses
    )

    if has_adaptive_data and not data.is_practice:
        try:
            from ..services.resume import resume_service
            from ..schemas.candidate import ParsedResume
            from ..models.course import CandidateTranscript

            # Build comprehensive candidate context for adaptive questions
            candidate_context = {
                "name": candidate.name,
                "university": candidate.university,
                "major": candidate.major,
                "majors": candidate.majors,  # Double majors
                "graduation_year": candidate.graduation_year,
                "gpa": candidate.gpa,
            }

            # Add resume data if available
            parsed_resume = None
            if candidate.resume_parsed_data:
                parsed_resume = ParsedResume(**candidate.resume_parsed_data)
                candidate_context["resume"] = {
                    "skills": parsed_resume.skills,
                    "experiences": [
                        {"title": exp.title, "company": exp.company, "highlights": exp.highlights[:2]}
                        for exp in (parsed_resume.experiences or [])[:3]
                    ],
                    "projects": [
                        {"name": proj.name, "technologies": proj.technologies}
                        for proj in (parsed_resume.projects or [])[:3]
                    ],
                }

            # Add GitHub data if available (NEW - makes interviews adaptive to coding experience)
            if candidate.github_data:
                github = candidate.github_data
                candidate_context["github"] = {
                    "username": candidate.github_username,
                    "top_languages": list(github.get("languages", {}).keys())[:5],
                    "total_repos": len(github.get("repos", [])),
                    "top_repos": [
                        {"name": r.get("name"), "language": r.get("language"), "stars": r.get("stars", 0)}
                        for r in sorted(github.get("repos", []), key=lambda x: x.get("stars", 0), reverse=True)[:3]
                    ],
                    "contributions": github.get("totalContributions", 0),
                }

            # Add transcript/courses data if available (NEW - makes interviews adaptive to coursework)
            transcript = db.query(CandidateTranscript).filter(
                CandidateTranscript.candidate_id == candidate.id
            ).first()

            if transcript and transcript.parsed_courses:
                # Get top/hardest courses for context
                hard_courses = [
                    c for c in transcript.parsed_courses
                    if c.get("grade") in ("A+", "A", "A-") and c.get("code")
                ][:5]
                candidate_context["transcript"] = {
                    "gpa": transcript.cumulative_gpa,
                    "technical_gpa": transcript.major_gpa,
                    "transcript_score": transcript.transcript_score,
                    "top_courses": [c.get("code") for c in hard_courses],
                    "total_units": transcript.total_units,
                }
            elif candidate.courses:
                candidate_context["courses"] = candidate.courses[:10]

            job_title_for_questions = job.title if job else None
            job_requirements = job.requirements if job else None

            # Generate adaptive questions using full context
            personalized_questions = await resume_service.generate_adaptive_questions(
                candidate_context=candidate_context,
                parsed_resume=parsed_resume,
                job_title=job_title_for_questions,
                job_requirements=job_requirements,
                num_questions=3,
            )

            # Add personalized questions to the list
            for pq in personalized_questions:
                question_list.append(QuestionInfo(
                    index=len(question_list),
                    text=pq.text,
                    category=pq.category,
                    question_type="video",
                    coding_challenge_id=None,
                ))

            logger.info(f"Generated {len(personalized_questions)} ADAPTIVE questions for candidate {candidate.id} "
                       f"(resume: {bool(candidate.resume_parsed_data)}, github: {bool(candidate.github_data)}, "
                       f"transcript: {bool(transcript)})")
        except Exception as e:
            logger.error(f"Failed to generate adaptive questions: {e}")
            # Fall back to remaining base questions
            for i, q in enumerate(base_questions[2:], start=len(question_list)):
                question_list.append(QuestionInfo(
                    index=i,
                    text=q.text,
                    category=q.category,
                    question_type=q.question_type or "video",
                    coding_challenge_id=q.coding_challenge_id,
                ))

    # If no personalized questions were generated, use remaining base questions
    if not personalized_questions:
        for i, q in enumerate(base_questions[2:], start=len(question_list)):
            question_list.append(QuestionInfo(
                index=i,
                text=q.text,
                category=q.category,
                question_type=q.question_type or "video",
                coding_challenge_id=q.coding_challenge_id,
            ))

    return InterviewStartResponse(
        session_id=session.id,
        questions=question_list,
        job_title=job_title,
        company_name=company_name,
        is_practice=session.is_practice,
    )


# ==================== VERTICAL INTERVIEW (TALENT POOL) ENDPOINTS ====================

# Technical roles that require coding challenges (US college market)
TECHNICAL_ROLES = {
    'software_engineer', 'frontend_engineer', 'backend_engineer',
    'fullstack_engineer', 'mobile_engineer', 'devops_engineer',
    'data_engineer', 'ml_engineer'
}

# Monthly interview cooldown (30 days between interviews per vertical)
MONTHLY_COOLDOWN_DAYS = 30


@router.post("/start-vertical", response_model=InterviewStartResponse)
@limiter.limit(RateLimits.INTERVIEW_START)
async def start_vertical_interview(
    request: Request,
    data: VerticalInterviewStart,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Start a vertical interview for the talent pool.

    This creates a ONE-TIME interview per vertical that enters the candidate
    into the talent pool. Candidates can retake up to 3 times with 24h cooldown.
    """
    from ..schemas.question import get_questions_for_role
    from datetime import timedelta

    # Use authenticated candidate - ignore candidate_id from request body
    candidate = current_candidate

    # Enforce email verification before interviews
    if not candidate.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before starting an interview. Check your inbox for a verification link."
        )

    # Parse and validate vertical and role_type
    try:
        vertical = Vertical(data.vertical)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid vertical: {data.vertical}. Valid options: engineering, data, business, design"
        )

    try:
        role_type = RoleType(data.role_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role type: {data.role_type}"
        )

    # Check for existing vertical profile
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == candidate.id,
        CandidateVerticalProfile.vertical == vertical
    ).first()

    if profile:
        # Check if there's an in-progress interview
        if profile.status == VerticalProfileStatus.IN_PROGRESS:
            # Return existing session
            existing_session = db.query(InterviewSession).filter(
                InterviewSession.id == profile.interview_session_id
            ).first()

            # Auto-expire stale sessions (older than 2 hours with no responses)
            if existing_session and existing_session.status == InterviewStatus.IN_PROGRESS:
                session_age = datetime.utcnow() - (existing_session.created_at.replace(tzinfo=None) if existing_session.created_at.tzinfo else existing_session.created_at)
                response_count = db.query(InterviewResponse).filter(
                    InterviewResponse.session_id == existing_session.id
                ).count()
                if session_age.total_seconds() > 7200 and response_count == 0:
                    # Stale session — expire it so candidate can start fresh
                    existing_session.status = InterviewStatus.CANCELLED
                    profile.status = VerticalProfileStatus.PENDING
                    profile.interview_session_id = None
                    db.commit()
                    logger.info(f"Auto-expired stale session {existing_session.id} for candidate {candidate.id}")
                    # Fall through to create new session below

            if existing_session and existing_session.status == InterviewStatus.IN_PROGRESS:
                # Retrieve the questions that were already recorded for this session
                from ..models.employer import CandidateQuestionHistory

                recorded_questions = db.query(CandidateQuestionHistory).filter(
                    CandidateQuestionHistory.interview_session_id == existing_session.id,
                    CandidateQuestionHistory.candidate_id == candidate.id
                ).order_by(CandidateQuestionHistory.asked_at).all()

                question_list = []
                for i, qh in enumerate(recorded_questions):
                    question_list.append(QuestionInfo(
                        index=i,
                        text=qh.question_text,
                        category=qh.category,
                        question_type="video",
                        coding_challenge_id=None,
                    ))

                # If no recorded questions found, fall back to static questions
                if not question_list:
                    questions = get_questions_for_role(vertical.value, role_type.value)
                    for i, q in enumerate(questions):
                        question_list.append(QuestionInfo(
                            index=i,
                            text=q["text"],
                            category=q.get("category"),
                            question_type="video",
                            coding_challenge_id=None,
                        ))

                # Add coding challenge for technical roles
                if role_type.value in TECHNICAL_ROLES:
                    coding_challenge = db.query(CodingChallenge).first()  # Get any challenge for now
                    if coding_challenge:
                        question_list.append(QuestionInfo(
                            index=len(question_list),
                            text=f"Coding Challenge: {coding_challenge.title}",
                            category="coding",
                            question_type="coding",
                            coding_challenge_id=coding_challenge.id,
                        ))

                return InterviewStartResponse(
                    session_id=existing_session.id,
                    questions=question_list,
                    job_title=f"{vertical.value.replace('_', ' ').title()} - {role_type.value.replace('_', ' ').title()}",
                    company_name="Pathway Talent Pool",
                    is_practice=False,
                )

        # Check monthly interview eligibility (30-day cooldown)
        if profile.status == VerticalProfileStatus.COMPLETED:
            last_interview = profile.last_interview_at or profile.last_attempt_at
            if last_interview:
                cooldown_end = last_interview + timedelta(days=MONTHLY_COOLDOWN_DAYS)
                if datetime.utcnow() < cooldown_end:
                    days_remaining = (cooldown_end - datetime.utcnow()).days + 1
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"You can interview again in {days_remaining} days. Next available: {cooldown_end.strftime('%B %d, %Y')}"
                    )

    # Import progressive question system
    from ..services.progressive_questions import (
        get_candidate_interview_history,
        generate_progressive_questions,
        record_questions_asked,
    )

    # Get candidate's interview history (previous topics, scores, weak areas)
    interview_history = get_candidate_interview_history(db, candidate.id, vertical)

    logger.info(f"Candidate interview history: interviews={interview_history['interview_count']}, "
               f"best_score={interview_history.get('best_score')}, "
               f"topics_asked={len(interview_history.get('topics_asked', []))}, "
               f"weak_areas={interview_history.get('weak_areas', [])}")

    # Generate PROGRESSIVE personalized questions using AI
    # This considers: resume, GitHub, transcript, AND past interview performance
    progressive_questions = []

    try:
        # Use AI to generate questions that:
        # 1. Avoid topics already asked in previous interviews
        # 2. Push difficulty based on past performance
        # 3. Probe deeper into weak areas to test improvement
        # 4. Personalize based on candidate's profile data
        progressive_questions = await generate_progressive_questions(
            db=db,
            candidate=candidate,
            vertical=vertical,
            role_type=role_type,
            num_questions=5,  # All 5 questions are AI-generated
        )

        logger.info(f"Generated {len(progressive_questions)} PROGRESSIVE questions - "
                   f"candidate: {candidate.id}, vertical: {vertical.value}, "
                   f"interview_count: {interview_history['interview_count']}, "
                   f"recommended_difficulty: {interview_history.get('recommended_difficulty', 1)}, "
                   f"avoiding_topics: {interview_history.get('topics_asked', [])}")

    except Exception as e:
        logger.error(f"Failed to generate progressive questions: {e}")
        # Fallback to static questions from templates
        from ..schemas.question import get_questions_for_role
        base_questions = get_questions_for_role(vertical.value, role_type.value)
        progressive_questions = [
            {
                "text": q["text"],
                "category": q.get("category"),
                "topic": q.get("question_key", "general"),
            }
            for q in base_questions[:5]
        ]

    # Create new interview session with AI-generated questions stored
    session = InterviewSession(
        id=generate_cuid("i"),
        status=InterviewStatus.IN_PROGRESS,
        is_practice=False,
        is_vertical_interview=True,
        vertical=vertical,
        role_type=role_type,
        started_at=datetime.utcnow(),
        candidate_id=candidate.id,
        job_id=None,  # No specific job for talent pool interviews
        questions_data=progressive_questions,  # Store AI-generated questions on session
    )
    db.add(session)
    db.flush()  # Get session ID

    # Create or update vertical profile
    if not profile:
        profile = CandidateVerticalProfile(
            id=generate_cuid("vp"),
            candidate_id=candidate.id,
            vertical=vertical,
            role_type=role_type,
            interview_session_id=session.id,
            status=VerticalProfileStatus.IN_PROGRESS,
            total_interviews=0,
        )
        db.add(profile)
    else:
        # Update for retake
        profile.interview_session_id = session.id
        profile.role_type = role_type  # Allow changing role within vertical on retake
        profile.status = VerticalProfileStatus.IN_PROGRESS

    db.commit()
    db.refresh(session)

    # Build question list from progressive AI-generated questions
    question_list = []

    for i, q in enumerate(progressive_questions):
        # Handle both dict format (from AI) and object format (fallback)
        if isinstance(q, dict):
            question_list.append(QuestionInfo(
                index=i,
                text=q.get("text", ""),
                category=q.get("category"),
                question_type="video",
                coding_challenge_id=None,
            ))
        else:
            # Object with attributes (from legacy format)
            question_list.append(QuestionInfo(
                index=i,
                text=getattr(q, 'text', str(q)),
                category=getattr(q, 'category', None),
                question_type="video",
                coding_challenge_id=None,
            ))

    # Add coding challenge for technical roles
    if role_type.value in TECHNICAL_ROLES:
        coding_challenge = db.query(CodingChallenge).first()  # Get any challenge
        if coding_challenge:
            question_list.append(QuestionInfo(
                index=len(question_list),
                text=f"Coding Challenge: {coding_challenge.title}",
                category="coding",
                question_type="coding",
                coding_challenge_id=coding_challenge.id,
            ))

    # Record the questions asked to prevent future repetition
    try:
        record_questions_asked(
            db=db,
            candidate_id=candidate.id,
            session_id=session.id,
            questions=progressive_questions,
            vertical=vertical,
        )
        logger.info(f"Recorded {len(progressive_questions)} questions for candidate {candidate.id}")
    except Exception as e:
        logger.error(f"Failed to record questions: {e}")
        # Non-critical, continue even if recording fails

    return InterviewStartResponse(
        session_id=session.id,
        questions=question_list,
        job_title=f"{vertical.value.replace('_', ' ').title()} - {role_type.value.replace('_', ' ').title()}",
        company_name="Pathway Talent Pool",
        is_practice=False,
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
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
                # Check for new ScoreDetails format
                if "communication" in analysis_data and "problem_solving" in analysis_data:
                    score_details = ScoreDetails(
                        communication=analysis_data["communication"],
                        problem_solving=analysis_data["problem_solving"],
                        domain_knowledge=analysis_data["domain_knowledge"],
                        motivation=analysis_data["motivation"],
                        culture_fit=analysis_data["culture_fit"],
                        overall=analysis_data.get("overall", resp.ai_score or 0),
                        analysis=analysis_data.get("analysis", ""),
                        strengths=analysis_data.get("strengths", []),
                        concerns=analysis_data.get("concerns", []),
                        highlight_quotes=analysis_data.get("highlight_quotes", []),
                    )
            except (json.JSONDecodeError, KeyError):
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

    # Build questions from session's stored AI-generated questions
    session_questions = []
    if session.questions_data:
        for i, q in enumerate(session.questions_data):
            if isinstance(q, dict):
                session_questions.append(QuestionInfo(
                    index=i,
                    text=q.get("text", ""),
                    category=q.get("category"),
                    question_type=q.get("question_type", "video"),
                    coding_challenge_id=q.get("coding_challenge_id"),
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
        company_name=session.job.employer.company_name if session.job else "Pathway",
        responses=sorted(responses, key=lambda x: x.question_index),
        questions=session_questions,
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed or cancelled"
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed or cancelled"
        )

    # Get question text - prefer AI-generated questions stored on the session
    question_text = None
    if session.questions_data and question_index < len(session.questions_data):
        q = session.questions_data[question_index]
        question_text = q.get("text", "") if isinstance(q, dict) else str(q)

    if not question_text:
        # Legacy fallback: fetch from static questions table
        questions = db.query(InterviewQuestion).filter(
            (InterviewQuestion.job_id == session.job_id) |
            (InterviewQuestion.is_default == True)
        ).order_by(InterviewQuestion.order).all()

        if question_index < len(questions):
            question_text = questions[question_index].text
        else:
            question_text = f"Question {question_index + 1}"

    # Create a simple object to carry the text
    class _QuestionRef:
        def __init__(self, text: str):
            self.text = text
    question = _QuestionRef(question_text)

    # Handle video upload or key
    storage_key = video_key
    if video and not video_key:
        content = await video.read()
        filename = video.filename or "video.webm"

        # Validate video file (extension, size, and magic bytes)
        from ..utils.file_validation import validate_video_file
        is_valid, error = validate_video_file(content, filename)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        storage_key = await storage_service.upload_video_bytes(
            data=content,
            session_id=session_id,
            question_index=question_index,
        )

    if not storage_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide video file or video key"
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
            question_text=question.text,  # Use English text for US market
            video_url=storage_key,
            session_id=session_id,
        )
        db.add(response)

    db.commit()
    db.refresh(response)

    # Queue background processing
    from ..config import settings
    # For vertical interviews, there may not be a specific job
    job_title = session.job.title if session.job else (session.vertical.value.title() if session.vertical else "General Interview")
    job_requirements = (session.job.requirements or []) if session.job else []
    background_tasks.add_task(
        process_interview_response,
        response_id=response.id,
        video_key=storage_key,
        job_title=job_title,
        job_requirements=job_requirements,
        db_url=settings.database_url,
        question_text=question.text,  # Use English text for US market
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
    from sqlalchemy import text

    # Use SELECT ... FOR UPDATE to prevent race conditions on concurrent completion calls
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).with_for_update().first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.status == InterviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed"
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

    # Update CandidateVerticalProfile if this is a vertical interview
    if session.is_vertical_interview and session.candidate_id:
        from datetime import timedelta
        vertical_profile = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.candidate_id == session.candidate_id,
            CandidateVerticalProfile.interview_session_id == session.id,
        ).first()

        if vertical_profile:
            vertical_profile.status = VerticalProfileStatus.COMPLETED
            vertical_profile.interview_score = session.total_score
            vertical_profile.last_interview_at = datetime.utcnow()
            vertical_profile.total_interviews = (vertical_profile.total_interviews or 0) + 1
            vertical_profile.next_eligible_at = datetime.utcnow() + timedelta(days=30)

            # Update best_score if this is a new high
            if session.total_score is not None:
                if vertical_profile.best_score is None or session.total_score > vertical_profile.best_score:
                    vertical_profile.best_score = session.total_score

            # Set completed_at only on first completion
            if vertical_profile.completed_at is None:
                vertical_profile.completed_at = datetime.utcnow()

            logger.info(f"Updated vertical profile {vertical_profile.id} to COMPLETED with score {session.total_score}")

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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
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
                # Check for new ScoreDetails format
                if "communication" in analysis_data and "problem_solving" in analysis_data:
                    score_details = ScoreDetails(
                        communication=analysis_data["communication"],
                        problem_solving=analysis_data["problem_solving"],
                        domain_knowledge=analysis_data["domain_knowledge"],
                        motivation=analysis_data["motivation"],
                        culture_fit=analysis_data["culture_fit"],
                        overall=analysis_data.get("overall", resp.ai_score or 0),
                        analysis=analysis_data.get("analysis", ""),
                        strengths=analysis_data.get("strengths", []),
                        concerns=analysis_data.get("concerns", []),
                        highlight_quotes=analysis_data.get("highlight_quotes", []),
                    )
            except (json.JSONDecodeError, KeyError):
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if not session.is_practice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for practice mode"
        )

    # Get the response
    response = db.query(InterviewResponse).filter(
        InterviewResponse.id == response_id,
        InterviewResponse.session_id == session_id
    ).first()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
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
                detail="Video not yet uploaded"
            )
        # Download video and transcribe
        try:
            video_bytes = await storage_service.download_video(response.video_url)
            transcription = await transcription_service.transcribe_bytes(video_bytes)
            response.transcription = transcription
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transcription failed: {str(e)}"
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
            detail=f"Scoring failed: {str(e)}"
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.is_practice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Follow-up questions not supported in practice mode"
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
            detail="No follow-up questions available"
        )

    if data.followup_index >= len(queue.generated_questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid follow-up question index"
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
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
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed or cancelled"
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
            detail="Follow-up question not found or not selected"
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
            detail="Original response not found"
        )

    # Handle video upload
    storage_key = video_key
    if video and not video_key:
        content = await video.read()
        filename = video.filename or "video.webm"

        # Validate video file (extension, size, and magic bytes)
        from ..utils.file_validation import validate_video_file
        is_valid, error = validate_video_file(content, filename)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

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
            detail="Must provide video file or video key"
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
            target_roles=None,  # None for SQLite compatibility in tests
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
                    category=q.category,
                    question_type=q.question_type or "video",
                    coding_challenge_id=q.coding_challenge_id,
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
                category=q.category,
                question_type=q.question_type or "video",
                coding_challenge_id=q.coding_challenge_id,
            )
            for i, q in enumerate(questions)
        ],
        job_title=invite.job.title,
        company_name=invite.job.employer.company_name,
    )


# ==================== CODING CHALLENGE ENDPOINTS ====================

@router.post("/{session_id}/code-response", response_model=CodeExecutionResponse)
@limiter.limit(RateLimits.INTERVIEW_SUBMIT)
async def submit_code_response(
    request: Request,
    session_id: str,
    question_index: int,
    data: CodeSubmitRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Submit a coding challenge response.

    This endpoint:
    1. Validates the session and question
    2. Creates/updates an InterviewResponse record
    3. Queues background execution and scoring
    4. Returns immediately with processing status
    """
    # Validate session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    if session.status not in [InterviewStatus.PENDING, InterviewStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview is already completed or cancelled"
        )

    # Get the question at this index
    questions = db.query(InterviewQuestion).filter(
        (InterviewQuestion.job_id == session.job_id) |
        (InterviewQuestion.is_default == True)
    ).order_by(InterviewQuestion.order).all()

    if question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question index"
        )

    question = questions[question_index]

    # Verify this is a coding question
    if question.question_type != "coding":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This question is not a coding challenge"
        )

    # Get the coding challenge
    if not question.coding_challenge_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coding question configuration error: no challenge linked"
        )

    challenge = db.query(CodingChallenge).filter(
        CodingChallenge.id == question.coding_challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding challenge not found"
        )

    # Check for existing response
    existing_response = db.query(InterviewResponse).filter(
        InterviewResponse.session_id == session_id,
        InterviewResponse.question_index == question_index
    ).first()

    if existing_response:
        # Update existing response
        existing_response.code_solution = data.code
        existing_response.execution_status = "processing"
        existing_response.test_results = None
        existing_response.ai_score = None
        existing_response.ai_analysis = None
        response = existing_response
    else:
        # Create new response
        response = InterviewResponse(
            id=generate_cuid("r"),
            question_index=question_index,
            question_text=challenge.title,  # Use English text for US market
            question_type="coding",
            code_solution=data.code,
            execution_status="processing",
            session_id=session_id,
        )
        db.add(response)

    db.commit()
    db.refresh(response)

    # Queue background processing
    from ..config import settings
    background_tasks.add_task(
        process_coding_response,
        response_id=response.id,
        code=data.code,
        challenge_id=challenge.id,
        db_url=settings.database_url,
        is_practice=session.is_practice,
    )

    return CodeExecutionResponse(
        response_id=response.id,
        question_index=question_index,
        status="processing",
    )


@router.get("/{session_id}/code-response/{response_id}", response_model=CodingFeedback)
async def get_code_response_status(
    session_id: str,
    response_id: str,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Get the status/results of a coding challenge submission.

    Poll this endpoint to check if code execution and scoring is complete.
    """
    # Validate session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    # Get the response
    response = db.query(InterviewResponse).filter(
        InterviewResponse.id == response_id,
        InterviewResponse.session_id == session_id
    ).first()

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found"
        )

    if response.question_type != "coding":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This response is not a coding question response"
        )

    # Parse test results
    test_results = response.test_results or []
    passed_count = sum(1 for t in test_results if t.get("passed", False))
    total_count = len(test_results)

    # Parse analysis data for feedback
    analysis_data = {}
    if response.ai_analysis:
        try:
            analysis_data = json.loads(response.ai_analysis)
        except json.JSONDecodeError:
            pass

    return CodingFeedback(
        response_id=response.id,
        question_index=response.question_index,
        execution_status=response.execution_status or "processing",
        test_results=[
            {
                "name": t.get("name", f"Test {i+1}"),
                "passed": t.get("passed", False),
                "actual": t.get("actual", ""),
                "expected": t.get("expected", ""),
                "hidden": t.get("hidden", False),
                "error": t.get("error"),
            }
            for i, t in enumerate(test_results)
        ],
        passed_count=passed_count,
        total_count=total_count,
        execution_time_ms=response.execution_time_ms or 0,
        ai_score=response.ai_score,
        analysis=analysis_data.get("analysis"),
        strengths=analysis_data.get("strengths", []),
        concerns=analysis_data.get("concerns", []),
        tips=analysis_data.get("tips", []),
        suggested_approach=analysis_data.get("suggested_approach"),
        time_complexity=analysis_data.get("time_complexity"),
        optimal_complexity=analysis_data.get("optimal_complexity"),
    )


@router.get("/{session_id}/coding-challenge/{question_index}", response_model=CodingQuestionInfo)
async def get_coding_challenge(
    session_id: str,
    question_index: int,
    db: Session = Depends(get_db),
    current_candidate: Candidate = Depends(get_current_candidate),
):
    """
    Get the coding challenge details for a specific question.
    """
    # Validate session
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )

    # Verify candidate owns this session
    if session.candidate_id != current_candidate.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this interview session"
        )

    # Get questions
    questions = db.query(InterviewQuestion).filter(
        (InterviewQuestion.job_id == session.job_id) |
        (InterviewQuestion.is_default == True)
    ).order_by(InterviewQuestion.order).all()

    if question_index >= len(questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid question index"
        )

    question = questions[question_index]

    if question.question_type != "coding":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This question is not a coding challenge"
        )

    # Get the challenge
    challenge = None
    if question.coding_challenge_id:
        challenge = db.query(CodingChallenge).filter(
            CodingChallenge.id == question.coding_challenge_id
        ).first()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding challenge not found"
        )

    # Build response with challenge info (hide test case expected values for hidden tests)
    visible_test_cases = []
    for tc in challenge.test_cases:
        if not tc.get("hidden", False):
            visible_test_cases.append(tc)
        else:
            # Include hidden test with masked expected value
            visible_test_cases.append({
                "input": tc.get("input"),
                "expected": "[hidden]",
                "hidden": True,
                "name": tc.get("name", "Hidden test"),
            })

    from ..schemas.coding_challenge import CodingChallengeResponse

    return CodingQuestionInfo(
        index=question_index,
        text=question.text,
        category=question.category,
        question_type="coding",
        coding_challenge=CodingChallengeResponse(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            starter_code=challenge.starter_code,
            test_cases=visible_test_cases,
            time_limit_seconds=challenge.time_limit_seconds,
            difficulty=challenge.difficulty,
            created_at=challenge.created_at,
        ),
    )

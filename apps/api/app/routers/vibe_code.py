"""
API endpoints for Vibe Code Session management.

Student endpoints return qualitative feedback only (archetype, strengths, weaknesses).
Employer/profile endpoints return full numerical scores + evidence.

Students should NOT see their builder score - only employers see scores.
"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models.candidate import Candidate
from ..models.vibe_code_session import VibeCodeSession
from ..schemas.vibe_code import (
    VibeCodeSessionUpload,
    VibeCodeRawUpload,
    VibeCodeStudentResponse,
    VibeCodeStudentUploadResponse,
    VibeCodeStudentSessionList,
    VibeCodeSessionResponse,
    VibeCodeUploadResponse,
    VibeCodeSessionList,
    VibeCodeSessionDetail,
    VibeCodeScores,
    VibeCodeProfileSummary,
)
from ..services.vibe_code_analysis import vibe_code_service
from ..utils.auth import get_current_candidate, get_current_employer
from ..utils.rate_limit import limiter, RateLimits

logger = logging.getLogger("pathway.vibe_code")
router = APIRouter()


def generate_cuid() -> str:
    return f"vcs{uuid.uuid4().hex[:22]}"


# ============================================================================
# RESPONSE BUILDERS
# ============================================================================

def _session_to_student_response(session: VibeCodeSession) -> VibeCodeStudentResponse:
    """Convert to student-facing response (archetype + strengths, NO numerical scores)."""
    return VibeCodeStudentResponse(
        id=session.id,
        candidate_id=session.candidate_id,
        title=session.title,
        description=session.description,
        source=session.source or "other",
        project_url=session.project_url,
        message_count=session.message_count,
        word_count=session.word_count,
        analysis_status=session.analysis_status or "pending",
        builder_archetype=session.builder_archetype,
        strengths=session.strengths,
        notable_patterns=session.notable_patterns,
        uploaded_at=session.uploaded_at,
        analyzed_at=session.analyzed_at,
    )


def _session_to_employer_response(session: VibeCodeSession) -> VibeCodeSessionResponse:
    """Convert to employer-facing response (full scores + metadata)."""
    scores = None
    if session.builder_score is not None:
        scores = VibeCodeScores(
            direction=session.direction_score,
            design_thinking=session.design_thinking_score,
            iteration_quality=session.iteration_quality_score,
            product_sense=session.product_sense_score,
            ai_leadership=session.ai_leadership_score,
        )

    return VibeCodeSessionResponse(
        id=session.id,
        candidate_id=session.candidate_id,
        title=session.title,
        description=session.description,
        source=session.source or "other",
        project_url=session.project_url,
        message_count=session.message_count,
        word_count=session.word_count,
        analysis_status=session.analysis_status or "pending",
        builder_score=session.builder_score,
        scores=scores,
        analysis_summary=session.analysis_summary,
        strengths=session.strengths,
        weaknesses=session.weaknesses,
        notable_patterns=session.notable_patterns,
        builder_archetype=session.builder_archetype,
        scoring_model=session.scoring_model,
        scoring_version=session.scoring_version,
        uploaded_at=session.uploaded_at,
        analyzed_at=session.analyzed_at,
    )


# ============================================================================
# BACKGROUND ANALYSIS
# ============================================================================

async def _run_analysis(session_id: str, db_url: str):
    """
    Background task to analyze a vibe code session.
    Creates its own DB session since background tasks outlive the request.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        session = db.query(VibeCodeSession).filter(VibeCodeSession.id == session_id).first()
        if not session:
            logger.error(f"Vibe code session {session_id} not found for analysis")
            return

        session.analysis_status = "analyzing"
        db.commit()

        result = await vibe_code_service.analyze_session(
            session_content=session.session_content,
            source=session.source or "other",
            title=session.title or "",
            description=session.description or "",
        )

        session.builder_score = result.builder_score
        session.direction_score = result.direction
        session.design_thinking_score = result.design_thinking
        session.iteration_quality_score = result.iteration_quality
        session.product_sense_score = result.product_sense
        session.ai_leadership_score = result.ai_leadership
        session.analysis_summary = result.summary
        session.strengths = result.strengths
        session.weaknesses = result.weaknesses
        session.notable_patterns = result.notable_patterns
        session.builder_archetype = result.builder_archetype
        session.analysis_details = result.details
        session.scoring_model = result.scoring_model
        session.scoring_version = result.scoring_version
        session.analysis_status = "completed"
        session.analyzed_at = datetime.utcnow()

        db.commit()
        logger.info(f"Vibe code analysis completed for session {session_id}: score={result.builder_score}")

    except Exception as e:
        logger.error(f"Vibe code analysis failed for session {session_id}: {e}")
        try:
            session = db.query(VibeCodeSession).filter(VibeCodeSession.id == session_id).first()
            if session:
                session.analysis_status = "failed"
                session.analysis_error = str(e)[:500]
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def _create_session_from_content(
    candidate_id: str,
    raw_content: str,
    title: str | None,
    description: str | None,
    source: str | None,
    project_url: str | None,
    db: Session,
) -> VibeCodeSession:
    """Shared logic for creating a session from uploaded content."""
    processed = vibe_code_service.preprocess_upload(raw_content)

    existing = db.query(VibeCodeSession).filter(
        VibeCodeSession.candidate_id == candidate_id,
        VibeCodeSession.content_hash == processed["content_hash"],
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This session has already been uploaded"
        )

    resolved_source = source or processed["source"]

    session = VibeCodeSession(
        id=generate_cuid(),
        candidate_id=candidate_id,
        title=title,
        description=description,
        source=resolved_source,
        project_url=project_url,
        session_content=processed["session_content"],
        content_hash=processed["content_hash"],
        message_count=processed["message_count"],
        word_count=processed["word_count"],
        analysis_status="pending",
    )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


# ============================================================================
# STUDENT ENDPOINTS (qualitative feedback only - NO scores)
# ============================================================================

@router.post("/sessions", response_model=VibeCodeStudentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_session(
    upload: VibeCodeSessionUpload,
    background_tasks: BackgroundTasks,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Upload an AI coding session log for analysis.

    Accepts raw text or JSON session exports from Cursor, Claude Code, Copilot, etc.
    The session is preprocessed (secrets redacted, format normalized) and then
    analyzed asynchronously by Claude to produce qualitative feedback.

    Note: Students see qualitative feedback only. Numerical scores are visible
    to employers through the talent pool.
    """
    session = _create_session_from_content(
        candidate_id=candidate.id,
        raw_content=upload.session_content,
        title=upload.title,
        description=upload.description,
        source=upload.source,
        project_url=upload.project_url,
        db=db,
    )

    from ..config import settings
    background_tasks.add_task(_run_analysis, session.id, settings.database_url)

    return VibeCodeStudentUploadResponse(
        success=True,
        message="Session uploaded successfully. Analysis will complete in 30-60 seconds.",
        session=_session_to_student_response(session),
    )


@router.post("/sessions/raw", response_model=VibeCodeStudentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_session_raw(
    upload: VibeCodeRawUpload,
    background_tasks: BackgroundTasks,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Simplified upload endpoint for CLI piping.

    Usage from terminal:
        claude export --format json | curl -X POST \\
          -H "Authorization: Bearer YOUR_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d @- https://pathway.careers/api/vibe-code/sessions/raw

    Or with a file:
        curl -X POST \\
          -H "Authorization: Bearer YOUR_TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"session_content": "'"$(cat session.json)"'"}' \\
          https://pathway.careers/api/vibe-code/sessions/raw
    """
    session = _create_session_from_content(
        candidate_id=candidate.id,
        raw_content=upload.session_content,
        title=upload.title,
        description=None,
        source=upload.source,
        project_url=None,
        db=db,
    )

    from ..config import settings
    background_tasks.add_task(_run_analysis, session.id, settings.database_url)

    return VibeCodeStudentUploadResponse(
        success=True,
        message="Session uploaded via CLI. Analysis will complete in 30-60 seconds.",
        session=_session_to_student_response(session),
    )


@router.get("/sessions", response_model=VibeCodeStudentSessionList)
async def list_sessions(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    List all vibe code sessions for the current student.
    Returns qualitative feedback only - no numerical scores.
    """
    sessions = db.query(VibeCodeSession).filter(
        VibeCodeSession.candidate_id == candidate.id
    ).order_by(desc(VibeCodeSession.uploaded_at)).all()

    return VibeCodeStudentSessionList(
        sessions=[_session_to_student_response(s) for s in sessions],
        total=len(sessions),
    )


@router.get("/sessions/{session_id}", response_model=VibeCodeStudentResponse)
async def get_session(
    session_id: str,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """
    Get a specific vibe code session (student view - no scores).
    """
    session = db.query(VibeCodeSession).filter(
        VibeCodeSession.id == session_id,
        VibeCodeSession.candidate_id == candidate.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return _session_to_student_response(session)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Delete a vibe code session."""
    session = db.query(VibeCodeSession).filter(
        VibeCodeSession.id == session_id,
        VibeCodeSession.candidate_id == candidate.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()


@router.post("/sessions/{session_id}/reanalyze", response_model=VibeCodeStudentResponse)
async def reanalyze_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    """Re-trigger analysis for a session (e.g., after a failed analysis)."""
    session = db.query(VibeCodeSession).filter(
        VibeCodeSession.id == session_id,
        VibeCodeSession.candidate_id == candidate.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.analysis_status == "analyzing":
        raise HTTPException(status_code=400, detail="Analysis is already in progress")

    session.analysis_status = "pending"
    session.analysis_error = None
    db.commit()

    from ..config import settings
    background_tasks.add_task(_run_analysis, session.id, settings.database_url)

    return _session_to_student_response(session)


# ============================================================================
# EMPLOYER / PROFILE ENDPOINTS (full scores visible)
# ============================================================================

@router.get("/profile/{candidate_id}", response_model=VibeCodeProfileSummary)
async def get_candidate_vibe_profile(
    candidate_id: str,
    employer=Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Get a summary of a candidate's vibe code profile.
    Used by employers in the talent pool to see builder quality at a glance.
    Includes numerical scores - this is the employer-facing view.
    Requires employer authentication.
    """
    sessions = db.query(VibeCodeSession).filter(
        VibeCodeSession.candidate_id == candidate_id,
        VibeCodeSession.analysis_status == "completed",
    ).order_by(desc(VibeCodeSession.builder_score)).all()

    if not sessions:
        return VibeCodeProfileSummary(total_sessions=0)

    scores = [s.builder_score for s in sessions if s.builder_score is not None]
    archetypes = [s.builder_archetype for s in sessions if s.builder_archetype]
    sources = list(set(s.source for s in sessions if s.source))

    all_strengths = []
    for s in sessions:
        if s.strengths:
            all_strengths.extend(s.strengths)
    seen = set()
    top_strengths = []
    for strength in all_strengths:
        key = strength.lower().strip()
        if key not in seen:
            seen.add(key)
            top_strengths.append(strength)
        if len(top_strengths) >= 5:
            break

    primary_archetype = max(set(archetypes), key=archetypes.count) if archetypes else None

    return VibeCodeProfileSummary(
        total_sessions=len(sessions),
        best_builder_score=max(scores) if scores else None,
        avg_builder_score=round(sum(scores) / len(scores), 2) if scores else None,
        primary_archetype=primary_archetype,
        top_strengths=top_strengths,
        sources_used=sources,
    )


@router.get("/employer/sessions/{candidate_id}", response_model=VibeCodeSessionList)
async def get_candidate_sessions_employer(
    candidate_id: str,
    employer=Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Get all sessions for a candidate with full scores (employer-only).
    Requires employer authentication.
    """
    sessions = db.query(VibeCodeSession).filter(
        VibeCodeSession.candidate_id == candidate_id,
        VibeCodeSession.analysis_status == "completed",
    ).order_by(desc(VibeCodeSession.builder_score)).all()

    completed = [s for s in sessions if s.builder_score is not None]
    best_score = max((s.builder_score for s in completed), default=None)

    return VibeCodeSessionList(
        sessions=[_session_to_employer_response(s) for s in sessions],
        total=len(sessions),
        best_builder_score=best_score,
    )


@router.get("/employer/sessions/{candidate_id}/{session_id}", response_model=VibeCodeSessionDetail)
async def get_session_detail_employer(
    candidate_id: str,
    session_id: str,
    employer=Depends(get_current_employer),
    db: Session = Depends(get_db),
):
    """
    Get detailed view of a specific session with full scores and evidence (employer-only).
    """
    session = db.query(VibeCodeSession).filter(
        VibeCodeSession.id == session_id,
        VibeCodeSession.candidate_id == candidate_id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    scores = None
    if session.builder_score is not None:
        scores = VibeCodeScores(
            direction=session.direction_score,
            design_thinking=session.design_thinking_score,
            iteration_quality=session.iteration_quality_score,
            product_sense=session.product_sense_score,
            ai_leadership=session.ai_leadership_score,
        )

    return VibeCodeSessionDetail(
        id=session.id,
        candidate_id=session.candidate_id,
        title=session.title,
        description=session.description,
        source=session.source or "other",
        project_url=session.project_url,
        message_count=session.message_count,
        word_count=session.word_count,
        analysis_status=session.analysis_status or "pending",
        builder_score=session.builder_score,
        scores=scores,
        analysis_summary=session.analysis_summary,
        strengths=session.strengths,
        weaknesses=session.weaknesses,
        notable_patterns=session.notable_patterns,
        builder_archetype=session.builder_archetype,
        analysis_details=session.analysis_details,
        scoring_model=session.scoring_model,
        scoring_version=session.scoring_version,
        uploaded_at=session.uploaded_at,
        analyzed_at=session.analyzed_at,
    )

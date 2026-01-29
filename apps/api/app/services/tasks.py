"""
Background task processing for interview responses.
Uses synchronous functions compatible with FastAPI's BackgroundTasks.
"""
import asyncio
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

from .transcription import transcription_service
from .scoring import scoring_service
from .email import email_service


def _run_async(coro):
    """Helper to run async code in sync context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a new loop in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


def process_interview_response(
    response_id: str,
    video_key: str,
    job_title: str,
    job_requirements: list[str],
    db_url: str,
    question_text: str,
):
    """
    Process a single interview response: transcribe and score.
    This is a synchronous function for use with FastAPI BackgroundTasks.
    """
    from ..models import InterviewResponse

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        response = db.query(InterviewResponse).filter(
            InterviewResponse.id == response_id
        ).first()

        if not response:
            print(f"Response {response_id} not found")
            return

        # Transcribe
        try:
            transcript = _run_async(
                transcription_service.transcribe_from_key(video_key)
            )
            response.transcription = transcript
            db.commit()
        except Exception as e:
            print(f"Transcription failed for {response_id}: {e}")
            response.transcription = f"[Transcription failed: {str(e)}]"
            db.commit()
            return

        # Score
        try:
            score_result = _run_async(
                scoring_service.analyze_response(
                    question=question_text,
                    transcript=transcript,
                    job_title=job_title,
                    job_requirements=job_requirements,
                )
            )
            response.ai_score = score_result.overall
            response.ai_analysis = json.dumps({
                "analysis": score_result.analysis,
                "strengths": score_result.strengths,
                "improvements": score_result.improvements,
                "scores": {
                    "relevance": score_result.relevance,
                    "clarity": score_result.clarity,
                    "depth": score_result.depth,
                    "communication": score_result.communication,
                    "job_fit": score_result.job_fit,
                }
            }, ensure_ascii=False)
            db.commit()
            print(f"Successfully processed response {response_id}, score: {score_result.overall}")
        except Exception as e:
            print(f"Scoring failed for {response_id}: {e}")
            response.ai_analysis = json.dumps({"error": str(e)}, ensure_ascii=False)
            db.commit()

    except Exception as e:
        print(f"Error processing response {response_id}: {e}")
    finally:
        db.close()


def generate_interview_summary(
    session_id: str,
    db_url: str,
):
    """
    Generate AI summary for a completed interview.
    """
    from ..models import InterviewSession, InterviewResponse

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            print(f"Session {session_id} not found")
            return

        responses = db.query(InterviewResponse).filter(
            InterviewResponse.session_id == session_id
        ).all()

        scored_responses = [r for r in responses if r.ai_score is not None]

        if not scored_responses:
            print(f"No scored responses for session {session_id}")
            return

        # Build response data for summary
        response_data = []
        for r in responses:
            response_data.append({
                "question": r.question_text,
                "transcript": r.transcription or "",
                "score": r.ai_score,
            })

        try:
            summary = _run_async(
                scoring_service.generate_summary(
                    responses=response_data,
                    job_title=session.job.title,
                    job_requirements=session.job.requirements or [],
                )
            )

            session.ai_summary = json.dumps({
                "summary": summary.summary,
                "recommendation": summary.recommendation,
                "overall_strengths": summary.overall_strengths,
                "overall_improvements": summary.overall_improvements,
            }, ensure_ascii=False)
            session.total_score = summary.total_score
            db.commit()
            print(f"Generated summary for session {session_id}")
        except Exception as e:
            print(f"Failed to generate summary for {session_id}: {e}")

    finally:
        db.close()


def send_completion_emails(
    session_id: str,
    db_url: str,
):
    """
    Send email notifications when interview is complete.
    """
    from ..models import InterviewSession

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            return

        # Email to employer
        employer = session.job.employer
        if employer.email:
            email_service.send_interview_complete_to_employer(
                employer_email=employer.email,
                employer_name=employer.company_name,
                candidate_name=session.candidate.name,
                job_title=session.job.title,
                interview_id=session_id,
                score=session.total_score,
            )

        # Email to candidate
        candidate = session.candidate
        if candidate.email and not candidate.email.endswith("@placeholder.local"):
            email_service.send_interview_complete_to_candidate(
                candidate_email=candidate.email,
                candidate_name=candidate.name,
                job_title=session.job.title,
                company_name=employer.company_name,
            )

    finally:
        db.close()

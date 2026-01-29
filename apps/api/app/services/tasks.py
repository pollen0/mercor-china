"""
Background task processing for interview responses.
Uses synchronous functions compatible with FastAPI's BackgroundTasks.
"""
import asyncio
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

from .transcription import transcription_service
from .scoring import scoring_service
from .email import email_service
from .matching import matching_service

logger = logging.getLogger("zhimian.tasks")


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
    generate_followups: bool = True,
):
    """
    Process a single interview response: transcribe, score, and optionally generate follow-ups.
    This is a synchronous function for use with FastAPI BackgroundTasks.
    """
    from ..models import InterviewResponse, InterviewSession, FollowupQueue
    import uuid

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        response = db.query(InterviewResponse).filter(
            InterviewResponse.id == response_id
        ).first()

        if not response:
            logger.warning(f"Response {response_id} not found")
            return

        # Get session to check if practice mode
        session = response.session
        is_practice = session.is_practice if session else False
        is_followup = response.is_followup

        # Transcribe
        try:
            transcript = _run_async(
                transcription_service.transcribe_from_key(video_key)
            )
            response.transcription = transcript
            db.commit()
        except Exception as e:
            logger.error(f"Transcription failed for {response_id}: {e}")
            response.transcription = f"[Transcription failed: {str(e)}]"
            db.commit()
            return

        # Score (with or without follow-up generation)
        try:
            # Only generate follow-ups for non-practice, non-followup responses
            should_generate_followups = (
                generate_followups and
                not is_practice and
                not is_followup
            )

            if should_generate_followups:
                # Score AND generate follow-up questions
                score_result, followup_questions = _run_async(
                    scoring_service.analyze_and_generate_followups(
                        question=question_text,
                        transcript=transcript,
                        job_title=job_title,
                        job_requirements=job_requirements,
                    )
                )

                # Store follow-up questions in queue if any were generated
                if followup_questions:
                    followup_queue = FollowupQueue(
                        id=f"fq{uuid.uuid4().hex[:22]}",
                        session_id=session.id,
                        question_index=response.question_index,
                        generated_questions=followup_questions,
                    )
                    db.add(followup_queue)
                    logger.info(f"Generated {len(followup_questions)} follow-up questions for response {response_id}")
            else:
                # Just score without follow-ups
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
                "concerns": score_result.concerns,
                "highlight_quotes": score_result.highlight_quotes,
                "scores": {
                    "communication": score_result.communication,
                    "problem_solving": score_result.problem_solving,
                    "domain_knowledge": score_result.domain_knowledge,
                    "motivation": score_result.motivation,
                    "culture_fit": score_result.culture_fit,
                }
            }, ensure_ascii=False)
            db.commit()
            logger.info(f"Successfully processed response {response_id}, score: {score_result.overall}")
        except Exception as e:
            logger.error(f"Scoring failed for {response_id}: {e}")
            response.ai_analysis = json.dumps({"error": str(e)}, ensure_ascii=False)
            db.commit()

    except Exception as e:
        logger.error(f"Error processing response {response_id}: {e}")
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
            logger.warning(f"Session {session_id} not found")
            return

        responses = db.query(InterviewResponse).filter(
            InterviewResponse.session_id == session_id
        ).all()

        scored_responses = [r for r in responses if r.ai_score is not None]

        if not scored_responses:
            logger.warning(f"No scored responses for session {session_id}")
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
                "overall_concerns": summary.overall_concerns,
            }, ensure_ascii=False)
            session.total_score = summary.total_score
            db.commit()
            logger.info(f"Generated summary for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to generate summary for {session_id}: {e}")

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


def process_match_after_interview(
    session_id: str,
    db_url: str,
):
    """
    Calculate and store match score after an interview is completed.
    This creates/updates the Match record with detailed scoring.
    """
    from ..models import InterviewSession, Match, Candidate
    import uuid

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()

        if not session:
            logger.warning(f"Session {session_id} not found")
            return

        # Skip practice interviews
        if session.is_practice:
            logger.debug(f"Skipping match for practice session {session_id}")
            return

        if not session.job:
            logger.warning(f"No job associated with session {session_id}")
            return

        # Get candidate resume data
        candidate = session.candidate
        candidate_data = candidate.resume_parsed_data if candidate else None

        # Calculate match
        try:
            match_result = _run_async(
                matching_service.calculate_match(
                    interview_score=session.total_score or 5.0,  # Default to 5 if not scored
                    candidate_data=candidate_data,
                    job_title=session.job.title,
                    job_requirements=session.job.requirements or [],
                    job_location=session.job.location,
                    job_vertical=session.job.vertical.value if session.job.vertical else None,
                )
            )

            # Create or update match record
            match = db.query(Match).filter(
                Match.candidate_id == session.candidate_id,
                Match.job_id == session.job_id
            ).first()

            if match:
                # Update existing match
                match.score = session.total_score or 0
                match.interview_score = match_result.interview_score
                match.skills_match_score = match_result.skills_match_score
                match.experience_match_score = match_result.experience_match_score
                match.location_match = match_result.location_match
                match.overall_match_score = match_result.overall_match_score
                match.factors = json.dumps(match_result.factors, ensure_ascii=False)
                match.ai_reasoning = match_result.ai_reasoning
            else:
                # Create new match
                match = Match(
                    id=f"m{uuid.uuid4().hex[:24]}",
                    candidate_id=session.candidate_id,
                    job_id=session.job_id,
                    score=session.total_score or 0,
                    interview_score=match_result.interview_score,
                    skills_match_score=match_result.skills_match_score,
                    experience_match_score=match_result.experience_match_score,
                    location_match=match_result.location_match,
                    overall_match_score=match_result.overall_match_score,
                    factors=json.dumps(match_result.factors, ensure_ascii=False),
                    ai_reasoning=match_result.ai_reasoning,
                )
                db.add(match)

            db.commit()
            logger.info(f"Processed match for session {session_id}, score: {match_result.overall_match_score}")

        except Exception as e:
            logger.error(f"Failed to calculate match for {session_id}: {e}")

    finally:
        db.close()

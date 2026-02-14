"""
Background task processing for interview responses.
Uses synchronous functions compatible with FastAPI's BackgroundTasks.
"""
import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional, Callable, Any

from .transcription import transcription_service
from .scoring import scoring_service
from .email import email_service
from .matching import matching_service
from .code_execution import code_execution_service

logger = logging.getLogger("pathway.tasks")


def with_retry(max_retries: int = 3, base_delay: float = 1.0, task_name: str = None):
    """
    Decorator that adds retry logic with exponential backoff to background tasks.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles with each retry)
        task_name: Name of the task for logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            name = task_name or func.__name__
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"[{name}] Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        # Final attempt failed - log full details for debugging
                        logger.error(
                            f"[{name}] FAILED after {max_retries + 1} attempts. "
                            f"Error: {e}\n"
                            f"Args: {args}\n"
                            f"Kwargs: {kwargs}\n"
                            f"Traceback: {traceback.format_exc()}"
                        )
            return None  # Return None instead of raising to avoid crashing background worker
        return wrapper
    return decorator


def log_task_failure(task_name: str, session_id: str, error: Exception, context: dict = None):
    """
    Log a task failure with full context for debugging and potential manual retry.
    """
    logger.error(
        f"BACKGROUND_TASK_FAILURE | task={task_name} | session_id={session_id} | "
        f"error={str(error)} | context={json.dumps(context or {})} | "
        f"traceback={traceback.format_exc()}"
    )


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
        transcript = None
        transcription_failed = False
        try:
            transcript = _run_async(
                transcription_service.transcribe_from_key(video_key)
            )
            response.transcription = transcript
            db.commit()
        except Exception as e:
            logger.error(f"Transcription failed for {response_id}: {e}")
            response.transcription = f"[Transcription failed: {str(e)}]"
            transcription_failed = True
            db.commit()
            # Don't return - continue to set a default score so interview can complete

        # If transcription failed, set default score and mark as needing review
        if transcription_failed or not transcript:
            response.ai_score = 5.0  # Neutral score - requires human review
            response.ai_analysis = json.dumps({
                "error": "Transcription failed - default score applied",
                "analysis": "Unable to analyze response due to transcription failure. This response requires manual review.",
                "strengths": [],
                "concerns": ["Transcription failed - unable to evaluate content"],
                "highlight_quotes": [],
                "scores": {
                    "communication": 5.0,
                    "problem_solving": 5.0,
                    "domain_knowledge": 5.0,
                    "motivation": 5.0,
                    "culture_fit": 5.0,
                },
                "requires_review": True,
            }, ensure_ascii=False)
            response.scoring_algorithm_version = "1.0.0-fallback"
            response.scored_at = datetime.utcnow()
            db.commit()
            logger.warning(f"Applied fallback score for response {response_id} due to transcription failure")
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
            # Store scoring version for future re-scoring capability
            response.scoring_algorithm_version = getattr(score_result, 'algorithm_version', '1.0.0')
            response.scored_at = datetime.utcnow()
            response.raw_score_data = {
                "question": question_text,
                "transcript": transcript[:2000] if transcript else None,  # Truncate for storage
                "job_title": job_title,
                "job_requirements": job_requirements,
                "vertical": getattr(score_result, 'vertical', None),
            }
            db.commit()
            logger.info(f"Successfully processed response {response_id}, score: {score_result.overall}, "
                       f"version: {response.scoring_algorithm_version}")
        except Exception as e:
            logger.error(f"Scoring failed for {response_id}: {e}")
            response.ai_analysis = json.dumps({"error": str(e)}, ensure_ascii=False)
            db.commit()

    except Exception as e:
        logger.error(f"Error processing response {response_id}: {e}")
    finally:
        db.close()


@with_retry(max_retries=3, base_delay=2.0, task_name="generate_interview_summary")
def generate_interview_summary(
    session_id: str,
    db_url: str,
):
    """
    Generate AI summary for a completed interview.
    Retries up to 3 times on failure.
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

        # Handle vertical interviews (no job) vs job-specific interviews
        job_title = "General Interview"
        job_requirements = []
        if session.job:
            job_title = session.job.title
            job_requirements = session.job.requirements or []
        elif session.is_vertical_interview and session.vertical:
            job_title = f"{session.vertical.value.replace('_', ' ').title()} Interview"

        summary = _run_async(
            scoring_service.generate_summary(
                responses=response_data,
                job_title=job_title,
                job_requirements=job_requirements,
            )
        )

        session.ai_summary = json.dumps({
            "summary": summary.summary,
            "recommendation": summary.recommendation,
            "overall_strengths": summary.overall_strengths,
            "overall_concerns": summary.overall_concerns,
            "overall_improvements": getattr(summary, 'overall_improvements', []),
        }, ensure_ascii=False)
        session.total_score = summary.total_score
        db.commit()
        logger.info(f"Generated summary for session {session_id}")

    finally:
        db.close()


@with_retry(max_retries=3, base_delay=2.0, task_name="send_completion_emails")
def send_completion_emails(
    session_id: str,
    db_url: str,
):
    """
    Send email notifications when interview is complete.
    Retries up to 3 times on failure.
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
            logger.warning(f"[send_completion_emails] Session {session_id} not found")
            return

        # Handle vertical interviews (no job) vs job-specific interviews
        if session.job:
            # Job-specific interview - email both employer and candidate
            employer = session.job.employer
            job_title = session.job.title
            company_name = employer.company_name

            # Email to employer
            if employer.email:
                try:
                    email_service.send_interview_complete_to_employer(
                        employer_email=employer.email,
                        employer_name=company_name,
                        candidate_name=session.candidate.name,
                        job_title=job_title,
                        interview_id=session_id,
                        score=session.total_score,
                    )
                    logger.info(f"Sent employer completion email for session {session_id}")
                except Exception as e:
                    log_task_failure("send_completion_emails.employer", session_id, e, {
                        "employer_email": employer.email,
                    })
                    raise  # Re-raise to trigger retry

            # Email to candidate
            candidate = session.candidate
            if candidate.email and not candidate.email.endswith("@placeholder.local"):
                try:
                    email_service.send_interview_complete_to_candidate(
                        candidate_email=candidate.email,
                        candidate_name=candidate.name,
                        job_title=job_title,
                        company_name=company_name,
                    )
                    logger.info(f"Sent candidate completion email for session {session_id}")
                except Exception as e:
                    log_task_failure("send_completion_emails.candidate", session_id, e, {
                        "candidate_email": candidate.email,
                    })
                    raise  # Re-raise to trigger retry

        else:
            # Vertical interview - only email candidate
            candidate = session.candidate
            if candidate.email and not candidate.email.endswith("@placeholder.local"):
                vertical_name = session.vertical.value.replace('_', ' ').title() if session.vertical else "General"
                try:
                    email_service.send_interview_complete_to_candidate(
                        candidate_email=candidate.email,
                        candidate_name=candidate.name,
                        job_title=f"{vertical_name} Interview",
                        company_name="Pathway",
                    )
                    logger.info(f"Sent vertical interview completion email for session {session_id}")
                except Exception as e:
                    log_task_failure("send_completion_emails.candidate_vertical", session_id, e, {
                        "candidate_email": candidate.email,
                    })
                    raise  # Re-raise to trigger retry

    finally:
        db.close()


@with_retry(max_retries=3, base_delay=2.0, task_name="process_match_after_interview")
def process_match_after_interview(
    session_id: str,
    db_url: str,
):
    """
    Calculate and store match score after an interview is completed.
    This creates/updates the Match record with detailed scoring.
    Retries up to 3 times on failure.

    For vertical (talent pool) interviews:
    - Updates the CandidateVerticalProfile
    - Auto-matches to all active jobs in that vertical
    """
    from ..models import InterviewSession, Match, Candidate, CandidateVerticalProfile, VerticalProfileStatus, Job
    from datetime import datetime
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

        # Handle vertical (talent pool) interviews
        if session.is_vertical_interview:
            _process_vertical_interview_completion(session, db)
            return

        # Handle job-specific interviews (existing logic)
        if not session.job:
            logger.warning(f"No job associated with session {session_id}")
            return

        # Get candidate resume data
        candidate = session.candidate
        candidate_data = candidate.resume_parsed_data if candidate else None

        # Calculate match
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
        log_task_failure("process_match_after_interview", session_id, e, {
            "job_id": session.job_id if session else None,
            "candidate_id": session.candidate_id if session else None,
        })
        raise  # Re-raise to trigger retry

    finally:
        db.close()


def _process_vertical_interview_completion(session, db):
    """
    Process completion of a vertical (talent pool) interview.

    1. Update the CandidateVerticalProfile with score and status
    2. Find all active jobs matching this vertical
    3. Create Match records for auto-surfacing
    """
    from ..models import CandidateVerticalProfile, VerticalProfileStatus, Job, Match
    from datetime import datetime
    import uuid

    # Find the vertical profile for this session
    profile = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.interview_session_id == session.id
    ).first()

    if not profile:
        # Try to find by candidate and vertical
        profile = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.candidate_id == session.candidate_id,
            CandidateVerticalProfile.vertical == session.vertical
        ).first()

    if not profile:
        logger.warning(f"No vertical profile found for session {session.id}")
        return

    # Update profile with score
    interview_score = session.total_score or 5.0
    now = datetime.utcnow()

    profile.interview_score = interview_score
    profile.status = VerticalProfileStatus.COMPLETED
    profile.completed_at = now

    # Update monthly interview tracking
    profile.last_interview_at = now
    profile.total_interviews = (profile.total_interviews or 0) + 1
    # Set next eligible date (30 days from now for monthly interviews)
    from datetime import timedelta
    profile.next_eligible_at = now + timedelta(days=30)

    # Keep backward compatibility with older column names
    if hasattr(profile, 'last_attempt_at'):
        profile.last_attempt_at = now
    if hasattr(profile, 'attempt_count'):
        profile.attempt_count = (profile.attempt_count or 0) + 1

    # Update best score if this is better
    if profile.best_score is None or interview_score > profile.best_score:
        profile.best_score = interview_score

    db.commit()
    logger.info(f"Updated vertical profile {profile.id} with score {interview_score}, "
               f"total_interviews: {profile.total_interviews}, next_eligible: {profile.next_eligible_at}")

    # Update question scores for progressive question tracking
    try:
        from .progressive_questions import update_question_scores

        # Get individual response scores to update question history
        responses = session.responses if hasattr(session, 'responses') else []
        question_scores = {}
        for i, resp in enumerate(responses):
            if resp.ai_score is not None:
                question_scores[i] = resp.ai_score

        if question_scores:
            update_question_scores(db, session.id, question_scores)
            logger.info(f"Updated {len(question_scores)} question scores for session {session.id}")
    except Exception as e:
        logger.error(f"Failed to update question scores: {e}")
        # Non-critical, continue with match processing

    # Find all active jobs matching this vertical
    matching_jobs = db.query(Job).filter(
        Job.is_active == True,
        Job.vertical == session.vertical
    ).all()

    logger.info(f"Found {len(matching_jobs)} active jobs for vertical {session.vertical.value}")

    # Get candidate resume data for matching
    candidate = session.candidate
    candidate_data = candidate.resume_parsed_data if candidate else None

    # Create/update matches for all matching jobs
    for job in matching_jobs:
        try:
            # Calculate match score
            match_result = _run_async(
                matching_service.calculate_match(
                    interview_score=profile.best_score or interview_score,
                    candidate_data=candidate_data,
                    job_title=job.title,
                    job_requirements=job.requirements or [],
                    job_location=job.location,
                    job_vertical=job.vertical.value if job.vertical else None,
                )
            )

            # Check for existing match
            existing_match = db.query(Match).filter(
                Match.candidate_id == session.candidate_id,
                Match.job_id == job.id
            ).first()

            if existing_match:
                # Update existing match
                existing_match.score = profile.best_score or interview_score
                existing_match.interview_score = match_result.interview_score
                existing_match.skills_match_score = match_result.skills_match_score
                existing_match.experience_match_score = match_result.experience_match_score
                existing_match.location_match = match_result.location_match
                existing_match.overall_match_score = match_result.overall_match_score
                existing_match.factors = json.dumps(match_result.factors, ensure_ascii=False)
                existing_match.ai_reasoning = match_result.ai_reasoning
                existing_match.vertical_profile_id = profile.id
            else:
                # Create new match
                new_match = Match(
                    id=f"m{uuid.uuid4().hex[:24]}",
                    candidate_id=session.candidate_id,
                    job_id=job.id,
                    vertical_profile_id=profile.id,
                    score=profile.best_score or interview_score,
                    interview_score=match_result.interview_score,
                    skills_match_score=match_result.skills_match_score,
                    experience_match_score=match_result.experience_match_score,
                    location_match=match_result.location_match,
                    overall_match_score=match_result.overall_match_score,
                    factors=json.dumps(match_result.factors, ensure_ascii=False),
                    ai_reasoning=match_result.ai_reasoning,
                )
                db.add(new_match)

            logger.info(f"Created/updated match for job {job.id}, score: {match_result.overall_match_score}")

        except Exception as e:
            logger.error(f"Failed to create match for job {job.id}: {e}")

    db.commit()
    logger.info(f"Completed vertical interview processing for session {session.id}")


@with_retry(max_retries=2, base_delay=2.0, task_name="rematch_candidate_after_profile_update")
def rematch_candidate_after_profile_update(
    candidate_id: str,
    db_url: str,
):
    """
    Re-run matching for a candidate after profile update (resume, transcript, or GitHub).
    Requires all three prerequisites: resume, transcript, and GitHub connected.
    Matches against ALL active jobs. If the candidate has completed vertical interviews,
    those scores are used; otherwise profile-only matching runs (no interview score).
    """
    from ..models import CandidateVerticalProfile, VerticalProfileStatus, Job, Match, Candidate
    from datetime import datetime
    import uuid

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            logger.warning(f"[rematch] Candidate {candidate_id} not found")
            return

        # Check prerequisites: resume + transcript + GitHub
        has_resume = bool(candidate.resume_url)
        has_transcript = bool(candidate.transcript_key)
        has_github = bool(candidate.github_username)

        if not (has_resume and has_transcript and has_github):
            missing = []
            if not has_resume:
                missing.append("resume")
            if not has_transcript:
                missing.append("transcript")
            if not has_github:
                missing.append("GitHub")
            logger.debug(f"[rematch] Candidate {candidate_id} missing: {', '.join(missing)} — skipping matching")
            return

        # Find completed vertical profiles (optional — used for interview scores if available)
        profiles = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.candidate_id == candidate_id,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED
        ).all()

        # Build vertical → profile map for interview scores
        vertical_profile_map = {}
        for profile in profiles:
            vertical_profile_map[profile.vertical] = profile

        candidate_data = candidate.resume_parsed_data
        candidate_preferences = candidate.sharing_preferences if hasattr(candidate, 'sharing_preferences') else None
        total_created = 0
        total_updated = 0

        # Match against ALL active jobs
        all_jobs = db.query(Job).filter(Job.is_active == True).all()

        for job in all_jobs:
            try:
                # Get employer info for preference boost
                employer = job.employer
                job_company_stage = getattr(employer, 'company_stage', None) if employer else None
                job_industry = getattr(employer, 'industry', None) if employer else None

                # Use interview score from matching vertical profile if available
                profile = vertical_profile_map.get(job.vertical)
                interview_score = None
                if profile:
                    interview_score = profile.best_score or profile.interview_score

                match_result = _run_async(
                    matching_service.calculate_match(
                        interview_score=interview_score,
                        candidate_data=candidate_data,
                        job_title=job.title,
                        job_requirements=job.requirements or [],
                        job_location=job.location,
                        job_vertical=job.vertical.value if job.vertical else None,
                        candidate_preferences=candidate_preferences,
                        job_company_stage=job_company_stage,
                        job_industry=job_industry,
                    )
                )

                # Check for existing match
                existing_match = db.query(Match).filter(
                    Match.candidate_id == candidate_id,
                    Match.job_id == job.id
                ).first()

                score_val = interview_score or 5.0

                if existing_match:
                    existing_match.score = score_val
                    existing_match.interview_score = match_result.interview_score
                    existing_match.skills_match_score = match_result.skills_match_score
                    existing_match.experience_match_score = match_result.experience_match_score
                    existing_match.location_match = match_result.location_match
                    existing_match.overall_match_score = match_result.boosted_match_score
                    existing_match.factors = json.dumps(match_result.factors, ensure_ascii=False)
                    existing_match.ai_reasoning = match_result.ai_reasoning
                    if profile:
                        existing_match.vertical_profile_id = profile.id
                    total_updated += 1
                else:
                    new_match = Match(
                        id=f"m{uuid.uuid4().hex[:24]}",
                        candidate_id=candidate_id,
                        job_id=job.id,
                        vertical_profile_id=profile.id if profile else None,
                        score=score_val,
                        interview_score=match_result.interview_score,
                        skills_match_score=match_result.skills_match_score,
                        experience_match_score=match_result.experience_match_score,
                        location_match=match_result.location_match,
                        overall_match_score=match_result.boosted_match_score,
                        factors=json.dumps(match_result.factors, ensure_ascii=False),
                        ai_reasoning=match_result.ai_reasoning,
                    )
                    db.add(new_match)
                    total_created += 1

            except Exception as e:
                logger.error(f"[rematch] Failed to match candidate {candidate_id} with job {job.id}: {e}")

        db.commit()
        logger.info(
            f"[rematch] Candidate {candidate_id}: {total_created} matches created, "
            f"{total_updated} updated across {len(all_jobs)} jobs"
        )

    except Exception as e:
        logger.error(f"[rematch] Error for candidate {candidate_id}: {e}")
        raise
    finally:
        db.close()


def process_coding_response(
    response_id: str,
    code: str,
    challenge_id: str,
    db_url: str,
    is_practice: bool = False,
):
    """
    Process a coding challenge response: execute code, run tests, and score.
    This is a synchronous function for use with FastAPI BackgroundTasks.

    Args:
        response_id: ID of the InterviewResponse record
        code: The submitted Python code
        challenge_id: ID of the CodingChallenge
        db_url: Database URL for creating a new session
        is_practice: Whether this is a practice mode submission
    """
    from ..models import InterviewResponse, CodingChallenge

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get the response record
        response = db.query(InterviewResponse).filter(
            InterviewResponse.id == response_id
        ).first()

        if not response:
            logger.warning(f"Response {response_id} not found")
            return

        # Get the coding challenge
        challenge = db.query(CodingChallenge).filter(
            CodingChallenge.id == challenge_id
        ).first()

        if not challenge:
            logger.error(f"Coding challenge {challenge_id} not found")
            response.execution_status = "error"
            response.ai_analysis = json.dumps({"error": "Challenge not found"}, ensure_ascii=False)
            db.commit()
            return

        # Execute the code against test cases
        try:
            exec_result = _run_async(
                code_execution_service.execute_python(
                    code=code,
                    test_cases=challenge.test_cases,
                    time_limit_seconds=challenge.time_limit_seconds
                )
            )

            # Update response with execution results
            response.execution_status = "success" if exec_result.success else "error"
            response.test_results = exec_result.test_results
            response.execution_time_ms = exec_result.execution_time_ms
            db.commit()

            logger.info(
                f"Executed code for response {response_id}: "
                f"{sum(1 for t in exec_result.test_results if t['passed'])}/{len(exec_result.test_results)} tests passed"
            )

        except Exception as e:
            logger.error(f"Code execution failed for {response_id}: {e}")
            response.execution_status = "error"
            response.test_results = []
            response.ai_analysis = json.dumps({"error": f"Execution failed: {str(e)}"}, ensure_ascii=False)
            db.commit()
            return

        # Score the response with AI
        try:
            # Get problem description for scoring context
            problem_desc = challenge.problem_description

            if is_practice:
                # Get detailed feedback for practice mode
                feedback = _run_async(
                    scoring_service.get_coding_immediate_feedback(
                        problem_description=problem_desc,
                        code=code,
                        test_results=exec_result.test_results,
                        language="en"
                    )
                )
                score_result = feedback["score_result"]

                # Store analysis with extra practice feedback
                analysis_data = {
                    "analysis": score_result.analysis,
                    "strengths": score_result.strengths,
                    "concerns": score_result.concerns,
                    "highlight_quotes": score_result.highlight_quotes,
                    "scores": {
                        "problem_solving": score_result.problem_solving,
                        "communication": score_result.communication,
                        "domain_knowledge": score_result.domain_knowledge,
                        "motivation": score_result.motivation,
                        "culture_fit": score_result.culture_fit,
                    },
                    "tips": feedback.get("tips", []),
                    "suggested_approach": feedback.get("suggested_approach"),
                    "time_complexity": feedback.get("time_complexity"),
                    "optimal_complexity": feedback.get("optimal_complexity"),
                }
            else:
                # Standard scoring for real interviews
                score_result = _run_async(
                    scoring_service.score_coding_response(
                        problem_description=problem_desc,
                        code=code,
                        test_results=exec_result.test_results,
                        language="en"
                    )
                )

                analysis_data = {
                    "analysis": score_result.analysis,
                    "strengths": score_result.strengths,
                    "concerns": score_result.concerns,
                    "highlight_quotes": score_result.highlight_quotes,
                    "scores": {
                        "problem_solving": score_result.problem_solving,
                        "communication": score_result.communication,
                        "domain_knowledge": score_result.domain_knowledge,
                        "motivation": score_result.motivation,
                        "culture_fit": score_result.culture_fit,
                    },
                }

            response.ai_score = score_result.overall
            response.ai_analysis = json.dumps(analysis_data, ensure_ascii=False)
            db.commit()

            logger.info(f"Scored coding response {response_id}: {score_result.overall}")

        except Exception as e:
            logger.error(f"Scoring failed for coding response {response_id}: {e}")
            # Still keep the execution results even if scoring fails
            response.ai_analysis = json.dumps({"error": f"Scoring failed: {str(e)}"}, ensure_ascii=False)
            db.commit()

    except Exception as e:
        logger.error(f"Error processing coding response {response_id}: {e}")
    finally:
        db.close()

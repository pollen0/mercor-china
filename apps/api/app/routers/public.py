"""
Public endpoints that don't require authentication.
Used for shareable candidate profiles via magic links.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models.candidate import Candidate, CandidateVerticalProfile, InterviewHistoryEntry
from ..models.profile_token import ProfileToken
from ..schemas.profile_token import PublicCandidateProfile

logger = logging.getLogger("pathway.public")
router = APIRouter()


@router.get("/talent/{candidate_id}", response_model=PublicCandidateProfile)
async def get_public_candidate_profile(
    candidate_id: str,
    token: str,
    db: Session = Depends(get_db),
):
    """
    Get a candidate's public profile using a magic link token.
    No authentication required, but requires valid token.

    Redacts sensitive information (email, phone).
    Tracks view count for analytics.
    """
    # Validate token
    profile_token = db.query(ProfileToken).filter(
        ProfileToken.token == token,
        ProfileToken.candidate_id == candidate_id
    ).first()

    if not profile_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired token"
        )

    # Check if token expired
    if profile_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This link has expired"
        )

    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Check if candidate opted in to sharing
    if not candidate.opted_in_to_sharing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This candidate's profile is not available for sharing"
        )

    # Update token usage tracking
    profile_token.view_count += 1
    profile_token.last_viewed_at = datetime.utcnow()
    db.commit()

    # Get best scores by vertical
    vertical_profiles = db.query(CandidateVerticalProfile).filter(
        CandidateVerticalProfile.candidate_id == candidate_id
    ).all()

    best_scores = {}
    for profile in vertical_profiles:
        if profile.best_score:
            best_scores[profile.vertical.value] = profile.best_score

    # Get interview history for progress chart
    history_entries = db.query(InterviewHistoryEntry).filter(
        InterviewHistoryEntry.candidate_id == candidate_id
    ).order_by(InterviewHistoryEntry.completed_at).all()

    interview_history = []
    for entry in history_entries:
        interview_history.append({
            "month": entry.interview_month,
            "year": entry.interview_year,
            "vertical": entry.vertical.value,
            "role_type": entry.role_type.value if entry.role_type else None,
            "overall_score": entry.overall_score,
            "communication_score": entry.communication_score,
            "problem_solving_score": entry.problem_solving_score,
            "technical_score": entry.technical_score,
            "growth_mindset_score": entry.growth_mindset_score,
            "culture_fit_score": entry.culture_fit_score,
            "completed_at": entry.completed_at.isoformat() if entry.completed_at else None,
        })

    logger.info(f"Public profile viewed: candidate={candidate_id}, token={profile_token.id}, views={profile_token.view_count}")

    # Return public profile (sensitive info redacted)
    return PublicCandidateProfile(
        id=candidate.id,
        name=candidate.name,
        university=candidate.university,
        major=candidate.major,
        majors=candidate.majors,
        minors=candidate.minors,
        graduation_year=candidate.graduation_year,
        gpa=candidate.gpa,
        github_username=candidate.github_username,
        github_data=candidate.github_data,
        bio=candidate.bio,
        linkedin_url=candidate.linkedin_url,
        portfolio_url=candidate.portfolio_url,
        target_roles=candidate.target_roles or [],
        best_scores=best_scores,
        interview_history=interview_history,
        resume_url=candidate.resume_url,
    )

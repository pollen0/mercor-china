from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProfileTokenCreate(BaseModel):
    """Request to create a profile token."""
    candidate_id: str
    expires_in_days: Optional[int] = 7  # Default 7 days


class ProfileTokenResponse(BaseModel):
    """Response with profile token details."""
    id: str
    token: str
    candidate_id: str
    expires_at: datetime
    view_count: int
    last_viewed_at: Optional[datetime] = None
    created_at: datetime
    # Construct full URL on frontend

    class Config:
        from_attributes = True


class PublicCandidateProfile(BaseModel):
    """Public candidate profile (redacted sensitive info)."""
    id: str
    name: str
    # Education
    university: Optional[str] = None
    major: Optional[str] = None
    majors: Optional[list[str]] = None
    minors: Optional[list[str]] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    # GitHub (public info only)
    github_username: Optional[str] = None
    github_data: Optional[dict] = None  # Repos, languages, contributions
    # Profile
    bio: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_roles: list[str] = []
    # Interview scores (best scores by vertical)
    best_scores: Optional[dict[str, float]] = None  # {vertical: score}
    interview_history: Optional[list[dict]] = None  # Monthly progress data
    # Resume (URL only, no raw text)
    resume_url: Optional[str] = None
    # NO EMAIL, NO PHONE (redacted for privacy)

    class Config:
        from_attributes = True

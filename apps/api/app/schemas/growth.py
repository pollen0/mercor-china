"""
Pydantic schemas for growth tracking API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GrowthTimelineSummary(BaseModel):
    """Summary statistics for the growth timeline."""
    total_interviews: int = Field(description="Total number of interviews completed")
    interview_score_change: Optional[float] = Field(None, description="Score change from first to latest interview")
    github_connected: bool = Field(description="Whether GitHub is connected")
    github_score_change: Optional[float] = Field(None, description="GitHub score change over time")
    resume_versions_count: int = Field(description="Number of resume versions")
    skills_growth_count: int = Field(description="Total new skills added across all resume versions")


class GrowthTimelineEvent(BaseModel):
    """A single event in the growth timeline."""
    event_type: str = Field(description="Type of event: interview, resume, github, profile")
    event_date: Optional[str] = Field(None, description="ISO datetime of the event")
    title: str = Field(description="Event title")
    subtitle: Optional[str] = Field(None, description="Additional detail")
    delta: Optional[float] = Field(None, description="Change/delta value (if applicable)")
    icon: str = Field(description="Icon identifier: interview, document, github, profile")


class GrowthTimelineResponse(BaseModel):
    """Response for growth timeline API."""
    candidate_id: str
    candidate_name: str
    summary: GrowthTimelineSummary
    events: List[GrowthTimelineEvent]

    model_config = {"from_attributes": True}


class ResumeVersionResponse(BaseModel):
    """Response for a single resume version."""
    id: str
    version_number: int
    original_filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    skills_added: Optional[List[str]] = None
    skills_removed: Optional[List[str]] = None
    projects_added: Optional[int] = None
    experience_added: Optional[int] = None
    is_current: bool
    uploaded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GitHubAnalysisHistoryResponse(BaseModel):
    """Response for a single GitHub analysis history entry."""
    id: str
    overall_score: Optional[float] = None
    originality_score: Optional[float] = None
    activity_score: Optional[float] = None
    depth_score: Optional[float] = None
    collaboration_score: Optional[float] = None
    total_repos_analyzed: Optional[int] = None
    total_commits_by_user: Optional[int] = None
    score_delta: Optional[float] = None
    repos_delta: Optional[int] = None
    analyzed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProfileChangeLogResponse(BaseModel):
    """Response for a single profile change log entry."""
    id: str
    change_type: str
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    change_source: Optional[str] = None
    changed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

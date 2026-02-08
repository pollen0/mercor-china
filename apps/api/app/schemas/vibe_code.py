"""
Pydantic schemas for Vibe Code Session upload and analysis.
"""
from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime


class VibeCodeSessionUpload(BaseModel):
    """Request to upload an AI coding session log."""
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None  # cursor, claude_code, copilot, chatgpt, other (auto-detected if omitted)
    project_url: Optional[str] = None
    session_content: str  # The raw session log text or JSON

    @field_validator("session_content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Session content must be at least 50 characters")
        if len(v) > 5_000_000:  # 5MB text limit
            raise ValueError("Session content exceeds 5MB limit")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        valid_sources = {"cursor", "claude_code", "copilot", "chatgpt", "other"}
        if v is not None and v not in valid_sources:
            raise ValueError(f"Source must be one of: {', '.join(valid_sources)}")
        return v


class VibeCodeScores(BaseModel):
    """Breakdown of builder score dimensions."""
    direction: Optional[float] = None
    design_thinking: Optional[float] = None
    iteration_quality: Optional[float] = None
    product_sense: Optional[float] = None
    ai_leadership: Optional[float] = None


class VibeCodeSessionResponse(BaseModel):
    """Response for a single vibe code session."""
    id: str
    candidate_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    source: str
    project_url: Optional[str] = None
    message_count: Optional[int] = None
    word_count: Optional[int] = None

    # Analysis
    analysis_status: str
    builder_score: Optional[float] = None
    scores: Optional[VibeCodeScores] = None
    analysis_summary: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    notable_patterns: Optional[list[str]] = None
    builder_archetype: Optional[str] = None

    # Metadata
    scoring_model: Optional[str] = None
    scoring_version: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VibeCodeUploadResponse(BaseModel):
    """Response after uploading a session."""
    success: bool
    message: str
    session: VibeCodeSessionResponse


class VibeCodeSessionList(BaseModel):
    """List of vibe code sessions for a candidate."""
    sessions: list[VibeCodeSessionResponse]
    total: int
    best_builder_score: Optional[float] = None


class VibeCodeSessionDetail(BaseModel):
    """Detailed view of a session including analysis evidence."""
    id: str
    candidate_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    source: str
    project_url: Optional[str] = None
    message_count: Optional[int] = None
    word_count: Optional[int] = None

    # Analysis
    analysis_status: str
    builder_score: Optional[float] = None
    scores: Optional[VibeCodeScores] = None
    analysis_summary: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    notable_patterns: Optional[list[str]] = None
    builder_archetype: Optional[str] = None
    analysis_details: Optional[dict[str, Any]] = None  # Full evidence for employers

    # Metadata
    scoring_model: Optional[str] = None
    scoring_version: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VibeCodeProfileSummary(BaseModel):
    """Summary of a candidate's vibe code profile for talent pool display."""
    total_sessions: int = 0
    best_builder_score: Optional[float] = None
    avg_builder_score: Optional[float] = None
    primary_archetype: Optional[str] = None
    top_strengths: list[str] = []
    sources_used: list[str] = []

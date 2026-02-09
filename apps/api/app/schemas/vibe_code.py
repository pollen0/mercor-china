"""
Pydantic schemas for Vibe Code Session upload and analysis.

Students see qualitative feedback only (archetype, strengths, areas to improve).
Employers see numerical scores through the talent pool / profile endpoints.
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


class VibeCodeRawUpload(BaseModel):
    """Simplified upload for CLI piping - just raw content + optional metadata."""
    session_content: str
    title: Optional[str] = None
    source: Optional[str] = None

    @field_validator("session_content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if len(v.strip()) < 50:
            raise ValueError("Session content must be at least 50 characters")
        if len(v) > 5_000_000:
            raise ValueError("Session content exceeds 5MB limit")
        return v


# ============================================================================
# STUDENT-FACING RESPONSES (no numerical scores)
# ============================================================================

class VibeCodeStudentResponse(BaseModel):
    """
    Student-facing session response.
    Shows builder archetype and strengths (qualitative growth signals).
    NO numerical scores — those are employer-only.
    """
    id: str
    candidate_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    source: str
    project_url: Optional[str] = None
    message_count: Optional[int] = None
    word_count: Optional[int] = None

    # Analysis status
    analysis_status: str

    # Qualitative feedback for student (no scores)
    builder_archetype: Optional[str] = None  # "architect", "iterative_builder", etc.
    strengths: Optional[list[str]] = None  # What they did well
    notable_patterns: Optional[list[str]] = None  # Interesting behaviors observed

    # Timestamps
    uploaded_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VibeCodeStudentUploadResponse(BaseModel):
    """Response after uploading a session (student-facing)."""
    success: bool
    message: str
    session: VibeCodeStudentResponse


class VibeCodeStudentSessionList(BaseModel):
    """List of vibe code sessions for a student (no scores)."""
    sessions: list[VibeCodeStudentResponse]
    total: int


# ============================================================================
# EMPLOYER-FACING RESPONSES (full scores + evidence)
# ============================================================================

class VibeCodeScores(BaseModel):
    """Breakdown of builder score dimensions (employer-only)."""
    direction: Optional[float] = None
    design_thinking: Optional[float] = None
    iteration_quality: Optional[float] = None
    product_sense: Optional[float] = None
    ai_leadership: Optional[float] = None


class VibeCodeSessionResponse(BaseModel):
    """Full session response with scores (employer-facing)."""
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
    """Response after uploading a session (employer-facing, legacy compat)."""
    success: bool
    message: str
    session: VibeCodeSessionResponse


class VibeCodeSessionList(BaseModel):
    """List of vibe code sessions with scores (employer-facing)."""
    sessions: list[VibeCodeSessionResponse]
    total: int
    best_builder_score: Optional[float] = None


class VibeCodeSessionDetail(BaseModel):
    """Detailed view of a session including analysis evidence (employer-facing)."""
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
    """Summary of a candidate's vibe code profile for talent pool display (employer-facing)."""
    total_sessions: int = 0
    best_builder_score: Optional[float] = None
    avg_builder_score: Optional[float] = None
    primary_archetype: Optional[str] = None
    top_strengths: list[str] = []
    sources_used: list[str] = []

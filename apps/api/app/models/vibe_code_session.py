"""
Vibe Code Session models for storing and analyzing AI coding session logs.

Students upload their Cursor, Claude Code, or Copilot session exports.
Claude AI analyzes the sessions to assess how the student uses AI as a tool -
whether they lead with intent and design thinking, or just let AI drive.
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base
import enum


class SessionSource(str, enum.Enum):
    """Supported AI coding tool sources."""
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    COPILOT = "copilot"
    CHATGPT = "chatgpt"
    OTHER = "other"


class AnalysisStatus(str, enum.Enum):
    """Status of the session analysis."""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class VibeCodeSession(Base):
    """
    Stores an uploaded AI coding session and its analysis results.

    Students upload exported session logs from tools like Cursor or Claude Code.
    Claude Opus/Sonnet analyzes the interaction patterns to produce a "Builder Score"
    that reveals how the student thinks and builds with AI.
    """
    __tablename__ = "vibe_code_sessions"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    # Session metadata
    title = Column(String, nullable=True)  # Student-provided title (e.g., "Built a REST API")
    description = Column(Text, nullable=True)  # Optional description of what they built
    source = Column(String, nullable=False, default="other")  # cursor, claude_code, copilot, chatgpt, other
    project_url = Column(String, nullable=True)  # Optional link to the resulting project/repo

    # Raw session data (stored as text, redacted of secrets)
    session_content = Column(Text, nullable=False)  # The uploaded session log (redacted)
    content_hash = Column(String, nullable=True)  # SHA-256 hash to detect duplicate uploads
    message_count = Column(Integer, nullable=True)  # Number of user<->AI exchanges
    word_count = Column(Integer, nullable=True)  # Total word count of the session

    # Analysis status
    analysis_status = Column(String, default="pending")  # pending, analyzing, completed, failed
    analysis_error = Column(Text, nullable=True)  # Error message if analysis failed

    # ======== BUILDER SCORE (0-10 scale) ========
    # Overall composite score
    builder_score = Column(Float, nullable=True)

    # Dimension scores (0-10 each)
    direction_score = Column(Float, nullable=True)  # Clear intent, specific instructions, not vague
    design_thinking_score = Column(Float, nullable=True)  # Discusses architecture, tradeoffs, UX before code
    iteration_quality_score = Column(Float, nullable=True)  # Debugs thoughtfully vs blindly pasting errors
    product_sense_score = Column(Float, nullable=True)  # Mentions users, edge cases, accessibility
    ai_leadership_score = Column(Float, nullable=True)  # Leads the AI vs deferring all decisions

    # ======== AI ANALYSIS OUTPUT ========
    analysis_summary = Column(Text, nullable=True)  # 2-3 sentence summary of builder quality
    strengths = Column(JSONB, nullable=True)  # ["Clear architectural direction", "Tests edge cases"]
    weaknesses = Column(JSONB, nullable=True)  # ["Rarely questions AI output", "No error handling"]
    notable_patterns = Column(JSONB, nullable=True)  # ["Draws diagrams before coding", "Uses TDD"]
    builder_archetype = Column(String, nullable=True)  # "architect", "iterative_builder", "ai_dependent", etc.

    # Detailed breakdown for employers
    analysis_details = Column(JSONB, nullable=True)  # Full structured analysis from Claude

    # Scoring metadata
    scoring_model = Column(String, nullable=True)  # Which Claude model scored this
    scoring_version = Column(String, nullable=True)  # Algorithm version

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", backref="vibe_code_sessions")

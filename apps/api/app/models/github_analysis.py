"""
GitHub Analysis models for storing detailed code contribution analysis.
Analyzes repos for authenticity, contribution patterns, and code quality signals.
"""
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base
import enum


class ProjectType(str, enum.Enum):
    """Classification of project origin/type."""
    PERSONAL = "personal"           # Self-initiated project
    CLASS_ASSIGNMENT = "class"      # Course homework/project
    HACKATHON = "hackathon"         # Built at hackathon
    TUTORIAL = "tutorial"           # Following a tutorial
    FORK_CONTRIBUTION = "fork"      # Forked and contributed
    ORGANIZATION = "organization"   # Part of org (internship/job)
    UNKNOWN = "unknown"


class CodeOriginSignal(str, enum.Enum):
    """Signals about code origin/authenticity."""
    ORGANIC = "organic"                 # Normal development pattern
    AI_ASSISTED = "ai_assisted"         # Shows signs of AI assistance
    HEAVILY_AI_GENERATED = "ai_heavy"   # Likely mostly AI-generated
    TEMPLATE_BASED = "template"         # Started from template/boilerplate
    COPIED = "copied"                   # Potentially copied from elsewhere


class GitHubAnalysis(Base):
    """
    Comprehensive GitHub profile analysis for a candidate.
    Stores computed metrics, not raw data (for privacy).
    """
    __tablename__ = "github_analyses"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Overall Scores (0-100)
    overall_score = Column(Float, nullable=True)
    originality_score = Column(Float, nullable=True)      # How much is their own work
    activity_score = Column(Float, nullable=True)         # Consistency of contributions
    depth_score = Column(Float, nullable=True)            # Complexity and quality
    collaboration_score = Column(Float, nullable=True)    # Team/PR experience

    # Aggregate Stats
    total_repos_analyzed = Column(Integer, default=0)
    total_commits_by_user = Column(Integer, default=0)
    total_lines_added = Column(Integer, default=0)
    total_lines_removed = Column(Integer, default=0)
    total_prs_opened = Column(Integer, default=0)
    total_prs_reviewed = Column(Integer, default=0)

    # Contribution Patterns
    avg_commits_per_week = Column(Float, nullable=True)
    longest_streak_days = Column(Integer, default=0)
    active_months_last_year = Column(Integer, default=0)
    weekend_commit_ratio = Column(Float, nullable=True)   # % of commits on weekends

    # Language Proficiency (computed bytes → proficiency levels)
    primary_languages = Column(JSONB, nullable=True)  # [{"language": "Python", "proficiency": "advanced", "bytes": 50000}]

    # Project Classification Summary
    personal_projects_count = Column(Integer, default=0)
    class_projects_count = Column(Integer, default=0)
    fork_contributions_count = Column(Integer, default=0)
    org_projects_count = Column(Integer, default=0)

    # Code Origin Signals
    organic_code_ratio = Column(Float, nullable=True)     # % of code that appears hand-written
    ai_assisted_repos = Column(Integer, default=0)        # Repos with AI-generation signals
    template_based_repos = Column(Integer, default=0)     # Repos from templates

    # Quality Signals
    has_tests = Column(Boolean, default=False)            # Any repo with tests
    has_ci_cd = Column(Boolean, default=False)            # Any repo with CI/CD
    has_documentation = Column(Boolean, default=False)    # Any repo with README > 500 chars
    code_review_participation = Column(Boolean, default=False)

    # Red Flags (for human review)
    flags = Column(JSONB, nullable=True)  # [{"type": "bulk_commit", "repo": "...", "detail": "50 files in 1 commit"}]
    requires_review = Column(Boolean, default=False)

    # Detailed repo analyses (stored for reference)
    repo_analyses = Column(JSONB, nullable=True)  # Array of RepoAnalysis objects

    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", backref="github_analysis")


class RepoAnalysisSchema:
    """
    Schema for individual repository analysis (stored as JSON in repo_analyses).
    Not a database table - just defines the structure.
    """
    # Example structure:
    # {
    #     "repo_name": "my-project",
    #     "repo_url": "https://github.com/user/my-project",
    #     "is_fork": false,
    #     "is_private": false,
    #
    #     "project_type": "personal",
    #     "code_origin": "organic",
    #     "confidence": 0.85,
    #
    #     "user_commits": 45,
    #     "total_commits": 50,
    #     "contribution_ratio": 0.90,
    #     "lines_added": 2500,
    #     "lines_removed": 800,
    #
    #     "collaborators": ["other_user"],
    #     "user_is_primary_author": true,
    #
    #     "languages": {"Python": 15000, "JavaScript": 5000},
    #     "primary_language": "Python",
    #
    #     "first_commit_date": "2024-01-15",
    #     "last_commit_date": "2024-06-20",
    #     "development_span_days": 156,
    #     "commit_frequency": "regular",  # sporadic, regular, burst
    #
    #     "has_readme": true,
    #     "readme_quality": "good",  # none, minimal, good, excellent
    #     "has_tests": true,
    #     "has_ci": false,
    #
    #     "signals": {
    #         "class_project_indicators": ["name contains 'hw'", "has rubric.md"],
    #         "ai_generation_indicators": ["50 files in first commit"],
    #         "quality_indicators": ["has tests", "meaningful commits"]
    #     },
    #
    #     "score_contribution": {
    #         "originality": 8.5,
    #         "depth": 7.0,
    #         "activity": 9.0
    #     }
    # }
    pass

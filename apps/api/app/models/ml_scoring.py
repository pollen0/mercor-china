"""
ML Scoring Models - Data infrastructure for model fine-tuning.

This module provides the database schema for:
1. Capturing all scoring events (interviews, resumes, GitHub, transcripts)
2. Storing human labels for training data
3. Tracking hiring outcomes for calibration
4. Managing ML experiments and A/B tests

Design Philosophy:
- Every scoring event is logged for future training
- Human labels provide ground truth
- Outcomes enable calibration against real-world results
- Version everything for reproducibility
"""

from sqlalchemy import (
    Column, String, DateTime, Float, Integer, Boolean,
    ForeignKey, Enum, Text, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


# ============================================
# ENUMS
# ============================================

class ScoringEventType(str, enum.Enum):
    """Types of scoring events we capture."""
    INTERVIEW_RESPONSE = "interview_response"
    INTERVIEW_SESSION = "interview_session"
    RESUME = "resume"
    GITHUB_PROFILE = "github_profile"
    GITHUB_REPO = "github_repo"
    TRANSCRIPT = "transcript"
    UNIFIED_SCORE = "unified_score"
    CODING_CHALLENGE = "coding_challenge"


class LabelSource(str, enum.Enum):
    """Source of human labels."""
    INTERNAL_QA = "internal_qa"          # Internal quality team
    EMPLOYER_FEEDBACK = "employer"        # Employer ratings
    EXPERT_REVIEW = "expert"              # Domain expert
    CANDIDATE_SELF = "candidate_self"     # Candidate self-assessment
    CROWDSOURCE = "crowdsource"           # Third-party labeling


class OutcomeType(str, enum.Enum):
    """Types of candidate outcomes."""
    HIRED = "hired"
    OFFER_EXTENDED = "offer_extended"
    OFFER_DECLINED = "offer_declined"
    REJECTED_TECHNICAL = "rejected_technical"
    REJECTED_CULTURAL = "rejected_cultural"
    REJECTED_EXPERIENCE = "rejected_experience"
    REJECTED_OTHER = "rejected_other"
    GHOSTED = "ghosted"
    STILL_INTERVIEWING = "still_interviewing"
    WITHDREW = "withdrew"


class OutcomeStage(str, enum.Enum):
    """Stage at which outcome occurred."""
    RESUME_SCREEN = "resume_screen"
    PHONE_SCREEN = "phone_screen"
    TECHNICAL_INTERVIEW = "technical_interview"
    ONSITE = "onsite"
    FINAL_ROUND = "final_round"
    OFFER = "offer"
    UNKNOWN = "unknown"


class CompanyTier(str, enum.Enum):
    """Company prestige tiers for outcome calibration."""
    FAANG = "faang"              # Meta, Apple, Amazon, Netflix, Google
    TIER_1 = "tier_1"            # Top tech (Microsoft, Stripe, etc.)
    UNICORN = "unicorn"          # Well-funded startups
    SERIES_B_C = "series_b_c"    # Mid-stage startups
    SERIES_A = "series_a"        # Early-stage startups
    SMB = "smb"                  # Small/medium business
    UNKNOWN = "unknown"


class ExperimentStatus(str, enum.Enum):
    """Status of ML experiments."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"


# ============================================
# SCORING EVENTS - Main training data
# ============================================

class ScoringEvent(Base):
    """
    Captures every scoring event for future model training.
    This is the primary source of training data.
    """
    __tablename__ = "scoring_events"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # What was scored
    event_type = Column(Enum(ScoringEventType), nullable=False, index=True)

    # Links to source entities
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String, ForeignKey("interview_sessions.id", ondelete="SET NULL"), nullable=True)
    response_id = Column(String, ForeignKey("interview_responses.id", ondelete="SET NULL"), nullable=True)

    # Input data (for reproducing the scoring)
    input_data = Column(JSONB, nullable=False)  # The actual content scored
    input_hash = Column(String(64), nullable=True, index=True)  # SHA256 for dedup
    input_tokens = Column(Integer, nullable=True)  # Token count of input

    # Context at scoring time
    context_data = Column(JSONB, nullable=True)  # Job requirements, vertical, role, etc.

    # Scoring algorithm info
    algorithm_version = Column(String(20), nullable=False, index=True)
    model_used = Column(String(100), nullable=True)  # 'claude-3-opus', 'gpt-4', etc.
    prompt_version = Column(String(20), nullable=True)  # Version of prompt template

    # Scoring output
    raw_scores = Column(JSONB, nullable=False)  # All dimension scores
    overall_score = Column(Float, nullable=True, index=True)
    confidence = Column(Float, nullable=True)  # Model's confidence (0-1)

    # Rich analysis output
    analysis_text = Column(Text, nullable=True)  # Generated analysis
    strengths = Column(JSONB, nullable=True)  # List of strengths
    concerns = Column(JSONB, nullable=True)  # List of concerns
    highlights = Column(JSONB, nullable=True)  # Notable quotes/examples

    # Processing metadata
    processing_time_ms = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    api_cost_usd = Column(Float, nullable=True)  # Estimated API cost

    # Error tracking
    had_error = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Classification
    vertical = Column(String(50), nullable=True, index=True)
    role_type = Column(String(50), nullable=True, index=True)

    # For experiments
    experiment_id = Column(String, ForeignKey("ml_experiments.id", ondelete="SET NULL"), nullable=True)
    variant = Column(String(50), nullable=True)  # 'control', 'treatment_a', etc.

    __table_args__ = (
        Index('ix_scoring_events_candidate_type', 'candidate_id', 'event_type'),
        Index('ix_scoring_events_version_type', 'algorithm_version', 'event_type'),
        Index('ix_scoring_events_created', 'created_at'),
    )


# ============================================
# HUMAN LABELS - Ground truth for training
# ============================================

class ScoringLabel(Base):
    """
    Human labels for scoring events - ground truth for training.
    Multiple labelers can label the same event for inter-rater reliability.
    """
    __tablename__ = "scoring_labels"

    id = Column(String, primary_key=True)
    scoring_event_id = Column(String, ForeignKey("scoring_events.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Labeler info
    labeler_id = Column(String, nullable=True)  # User ID if internal
    labeler_source = Column(Enum(LabelSource), nullable=False)
    labeler_expertise = Column(String(100), nullable=True)  # 'senior_engineer', 'recruiter'
    labeler_vertical = Column(String(50), nullable=True)  # Their domain expertise

    # Human scores (same dimensions as AI)
    human_scores = Column(JSONB, nullable=False)  # {communication: 8.5, ...}
    human_overall = Column(Float, nullable=True)

    # Qualitative feedback
    label_notes = Column(Text, nullable=True)
    disagreement_reasons = Column(ARRAY(String), nullable=True)  # Why human disagreed
    ai_score_seen = Column(Boolean, default=False)  # Did they see AI score first?

    # Specific corrections
    corrections = Column(JSONB, nullable=True)  # {field: 'strengths', original: [...], corrected: [...]}

    # Label quality metadata
    time_spent_seconds = Column(Integer, nullable=True)
    confidence = Column(String(20), nullable=True)  # 'high', 'medium', 'low'
    difficulty = Column(String(20), nullable=True)  # How hard was this to label?

    # Validation
    is_validated = Column(Boolean, default=False)  # Reviewed by senior labeler
    validated_by = Column(String, nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_labels_event', 'scoring_event_id'),
        Index('ix_labels_source', 'labeler_source'),
    )


class LabelingTask(Base):
    """
    Queue of scoring events waiting for human labels.
    Enables systematic labeling workflow.
    """
    __tablename__ = "labeling_tasks"

    id = Column(String, primary_key=True)
    scoring_event_id = Column(String, ForeignKey("scoring_events.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Task metadata
    priority = Column(Integer, default=0)  # Higher = more urgent
    reason = Column(String(100), nullable=True)  # 'high_variance', 'edge_case', 'random_sample'

    # Assignment
    assigned_to = Column(String, nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)

    # Completion
    status = Column(String(20), default='pending')  # 'pending', 'in_progress', 'completed', 'skipped'
    completed_at = Column(DateTime(timezone=True), nullable=True)
    label_id = Column(String, ForeignKey("scoring_labels.id", ondelete="SET NULL"), nullable=True)

    # Requirements
    min_labels_needed = Column(Integer, default=1)
    current_label_count = Column(Integer, default=0)

    __table_args__ = (
        Index('ix_labeling_tasks_status', 'status', 'priority'),
    )


# ============================================
# CANDIDATE OUTCOMES - For calibration
# ============================================

class CandidateOutcome(Base):
    """
    Tracks real-world hiring outcomes for score calibration.
    Links scores to actual results (hired/rejected).
    """
    __tablename__ = "candidate_outcomes"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # What happened
    outcome_type = Column(Enum(OutcomeType), nullable=False, index=True)
    outcome_stage = Column(Enum(OutcomeStage), nullable=True)

    # Employer context
    employer_id = Column(String, ForeignKey("employers.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    company_name = Column(String, nullable=True)
    company_tier = Column(Enum(CompanyTier), default=CompanyTier.UNKNOWN)

    # Role context
    role_title = Column(String, nullable=True)
    role_level = Column(String, nullable=True)  # 'intern', 'new_grad', 'junior', etc.
    vertical = Column(String(50), nullable=True)
    role_type = Column(String(50), nullable=True)

    # Timing
    outcome_date = Column(DateTime(timezone=True), nullable=True)
    days_from_first_interview = Column(Integer, nullable=True)
    days_from_application = Column(Integer, nullable=True)

    # Scores at time of outcome (snapshot)
    pathway_score_at_outcome = Column(Float, nullable=True)  # Our score when they applied
    interview_score_at_outcome = Column(Float, nullable=True)
    github_score_at_outcome = Column(Float, nullable=True)
    transcript_score_at_outcome = Column(Float, nullable=True)
    resume_score_at_outcome = Column(Float, nullable=True)

    # Offer details (if hired)
    offer_details = Column(JSONB, nullable=True)  # {level, base, equity, bonus, location}

    # Rejection details
    rejection_reason = Column(String(100), nullable=True)
    rejection_feedback = Column(Text, nullable=True)

    # Employer feedback (if available)
    employer_rating = Column(Float, nullable=True)  # 1-5
    employer_notes = Column(Text, nullable=True)
    would_interview_again = Column(Boolean, nullable=True)

    # Verification
    is_verified = Column(Boolean, default=False)  # Confirmed by candidate/employer
    verification_source = Column(String(50), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_outcomes_candidate', 'candidate_id'),
        Index('ix_outcomes_type', 'outcome_type'),
        Index('ix_outcomes_company_tier', 'company_tier'),
    )


# ============================================
# DETAILED ANALYSIS STORAGE
# ============================================

class InterviewTranscriptML(Base):
    """
    Full interview transcripts with ML-ready features.
    Stores embeddings for similarity search.
    """
    __tablename__ = "interview_transcripts_ml"

    id = Column(String, primary_key=True)
    response_id = Column(String, ForeignKey("interview_responses.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Raw content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=True)  # 'behavioral', 'technical', 'situational'
    response_text = Column(Text, nullable=False)  # Full transcript

    # Structured extraction
    key_claims = Column(JSONB, nullable=True)  # Factual claims for verification
    technical_terms = Column(JSONB, nullable=True)  # Technical vocabulary used
    named_entities = Column(JSONB, nullable=True)  # Companies, technologies, people

    # Structure analysis
    structure_analysis = Column(JSONB, nullable=True)  # {
        # has_star_format: bool,
        # has_clear_example: bool,
        # answer_completeness: 0-1,
        # relevance_to_question: 0-1,
        # specificity_level: 'vague' | 'specific' | 'detailed'
    # }

    # Linguistic features
    linguistic_features = Column(JSONB, nullable=True)  # {
        # filler_word_count: int,
        # filler_word_ratio: float,
        # average_sentence_length: float,
        # vocabulary_richness: float,
        # hedging_phrases: int,
        # confidence_indicators: int
    # }

    # Audio features (if available from video)
    audio_features = Column(JSONB, nullable=True)  # {
        # speaking_rate_wpm: float,
        # pause_count: int,
        # average_pause_duration: float,
        # volume_variation: float,
        # pitch_variation: float
    # }

    # Embeddings for similarity search
    embedding_model = Column(String(100), nullable=True)  # 'text-embedding-3-large'
    embedding_vector = Column(JSONB, nullable=True)  # Store as JSON array for now
    # Note: For production, use pgvector: embedding_vector = Column(Vector(1536))

    # Metadata
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    language = Column(String(10), default='en')

    # Classification
    vertical = Column(String(50), nullable=True)
    role_type = Column(String(50), nullable=True)

    __table_args__ = (
        Index('ix_transcripts_candidate', 'candidate_id'),
        Index('ix_transcripts_response', 'response_id'),
    )


class GitHubAnalysisML(Base):
    """
    Detailed GitHub analysis for ML training.
    Stores repo-level and commit-level features.
    """
    __tablename__ = "github_analysis_ml"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    github_username = Column(String(100), nullable=False)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Profile-level data
    profile_data = Column(JSONB, nullable=True)  # {
        # followers, following, public_repos, created_at,
        # bio, company, location, hireable
    # }

    # Contribution patterns
    contribution_data = Column(JSONB, nullable=True)  # {
        # total_contributions_year: int,
        # longest_streak: int,
        # current_streak: int,
        # contribution_calendar: [...],
        # peak_activity_day: str,
        # consistency_score: 0-100
    # }

    # Repo-level analysis (top N repos)
    repos_analyzed = Column(JSONB, nullable=True)  # [{
        # name, description, stars, forks, language,
        # created_at, last_commit_at, commit_count,
        # user_commits, user_lines_added, user_lines_deleted,
        # is_fork, fork_ahead_by, fork_behind_by,
        # has_tests, has_ci, has_docs, has_license,
        # project_type: 'personal' | 'class' | 'hackathon' | 'tutorial',
        # authenticity_signals: [...],
        # code_quality_sample: {...}
    # }]

    # Code quality analysis (sampled from commits)
    code_quality_samples = Column(JSONB, nullable=True)  # [{
        # repo, file_path, language,
        # snippet, snippet_hash,
        # quality_indicators: {
        #   naming_convention: 'good' | 'poor',
        #   has_comments: bool,
        #   error_handling: 'thorough' | 'basic' | 'none',
        #   design_patterns: [...],
        #   code_smells: [...]
        # }
    # }]

    # Language proficiency
    language_proficiencies = Column(JSONB, nullable=True)  # [{
        # language, bytes, percentage,
        # repo_count, proficiency: 'advanced' | 'intermediate' | 'beginner',
        # years_active, complexity_samples: [...]
    # }]

    # Collaboration signals
    collaboration_data = Column(JSONB, nullable=True)  # {
        # prs_opened, prs_merged, prs_reviewed,
        # issues_opened, issues_closed,
        # review_comments_given,
        # review_quality_samples: [...],
        # orgs_contributed_to: [...]
    # }

    # Skill evolution over time
    skill_evolution = Column(JSONB, nullable=True)  # {
        # languages_by_year: {...},
        # complexity_trend: 'increasing' | 'stable' | 'decreasing',
        # activity_trend: 'increasing' | 'stable' | 'decreasing',
        # notable_growth_periods: [...]
    # }

    # Authenticity analysis
    authenticity_analysis = Column(JSONB, nullable=True)  # {
        # overall_authenticity_score: 0-100,
        # ai_generation_probability: 0-1,
        # red_flags: [...],
        # green_flags: [...],
        # requires_manual_review: bool,
        # review_reasons: [...]
    # }

    # Aggregated scores
    overall_score = Column(Float, nullable=True)
    originality_score = Column(Float, nullable=True)
    activity_score = Column(Float, nullable=True)
    depth_score = Column(Float, nullable=True)
    collaboration_score = Column(Float, nullable=True)
    code_quality_score = Column(Float, nullable=True)

    # Algorithm tracking
    algorithm_version = Column(String(20), nullable=True)

    __table_args__ = (
        Index('ix_github_ml_candidate', 'candidate_id'),
        Index('ix_github_ml_username', 'github_username'),
    )


class ResumeAnalysisML(Base):
    """
    Detailed resume analysis for ML training.
    Stores structured extraction and scoring features.
    """
    __tablename__ = "resume_analysis_ml"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Source info
    resume_url = Column(String, nullable=True)
    resume_hash = Column(String(64), nullable=True)  # For dedup
    file_type = Column(String(20), nullable=True)  # 'pdf', 'docx'

    # Raw extraction
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSONB, nullable=True)  # Full parsed resume

    # Experience analysis
    experience_analysis = Column(JSONB, nullable=True)  # [{
        # company, company_tier, title, start_date, end_date,
        # duration_months, is_current,
        # responsibilities: [...],
        # achievements: [...],
        # quantified_impacts: [...],  # "increased revenue 20%"
        # technologies_used: [...],
        # role_progression_score: 0-10
    # }]

    # Company tiers identified
    companies_by_tier = Column(JSONB, nullable=True)  # {
        # faang: [...], tier_1: [...], unicorn: [...], ...
    # }

    # Education analysis
    education_analysis = Column(JSONB, nullable=True)  # [{
        # institution, institution_tier, degree, field,
        # gpa, gpa_scale, graduation_year,
        # honors: [...], relevant_coursework: [...]
    # }]

    # Skills analysis
    skills_analysis = Column(JSONB, nullable=True)  # {
        # technical: [{skill, proficiency, evidence_strength}],
        # frameworks: [...],
        # tools: [...],
        # soft_skills: [...],
        # skill_depth_scores: {...}
    # }

    # Project analysis
    projects_analysis = Column(JSONB, nullable=True)  # [{
        # name, description, technologies,
        # scope: 'personal' | 'team' | 'class' | 'hackathon',
        # complexity_score: 0-10,
        # impact_indicators: [...],
        # github_link: str
    # }]

    # Quality signals
    quality_signals = Column(JSONB, nullable=True)  # {
        # has_quantified_achievements: bool,
        # action_verbs_count: int,
        # grammar_issues: [...],
        # formatting_score: 0-10,
        # appropriate_length: bool,
        # keyword_density: {...}
    # }

    # Red flags
    red_flags = Column(JSONB, nullable=True)  # [{
        # type: 'gap' | 'short_tenure' | 'inconsistency' | ...,
        # description: str,
        # severity: 'low' | 'medium' | 'high'
    # }]

    # Role fit analysis (per target role)
    role_fit_scores = Column(JSONB, nullable=True)  # {
        # software_engineer: {score: 85, reasons: [...]},
        # data_scientist: {score: 72, reasons: [...]},
        # ...
    # }

    # Aggregated scores
    overall_score = Column(Float, nullable=True)
    experience_relevance_score = Column(Float, nullable=True)
    experience_progression_score = Column(Float, nullable=True)
    skill_depth_score = Column(Float, nullable=True)
    education_quality_score = Column(Float, nullable=True)
    project_impact_score = Column(Float, nullable=True)

    # Algorithm tracking
    algorithm_version = Column(String(20), nullable=True)

    __table_args__ = (
        Index('ix_resume_ml_candidate', 'candidate_id'),
    )


class TranscriptAnalysisML(Base):
    """
    Enhanced transcript analysis for ML training.
    Stores detailed academic performance features.
    """
    __tablename__ = "transcript_analysis_ml"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    transcript_id = Column(String, ForeignKey("candidate_transcripts.id", ondelete="SET NULL"), nullable=True)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # University context
    university_data = Column(JSONB, nullable=True)  # {
        # name, tier, cs_ranking,
        # grade_inflation_factor, grading_difficulty,
        # known_for: [...],  # 'systems', 'AI', 'theory'
    # }

    # Course-by-course analysis
    course_analysis = Column(JSONB, nullable=True)  # [{
        # code, name, grade, gpa_value, units,
        # semester, student_year,
        # difficulty_score, typical_gpa,
        # performance_percentile_estimate,
        # is_technical, is_required, is_graduate,
        # relevance_to_roles: {...}
    # }]

    # Semester progression
    semester_progression = Column(JSONB, nullable=True)  # [{
        # semester, year, student_year,
        # units, gpa, technical_gpa,
        # course_count, hard_course_count,
        # workload_intensity: 0-10
    # }]

    # Grade distribution
    grade_distribution = Column(JSONB, nullable=True)  # {
        # A_plus: 5, A: 12, A_minus: 8, ...
        # technical_distribution: {...},
        # non_technical_distribution: {...}
    # }

    # Comparative metrics
    comparative_metrics = Column(JSONB, nullable=True)  # {
        # gpa_percentile_at_school: 0-100,
        # gpa_percentile_cross_school: 0-100,
        # rigor_percentile: 0-100,
        # peer_comparison_sample: [...]
    # }

    # Achievement patterns
    achievement_patterns = Column(JSONB, nullable=True)  # {
        # perfect_grades_in_hard_courses: [...],
        # grad_courses_as_undergrad: [...],
        # multiple_hard_courses_same_semester: [...],
        # improvement_breakthroughs: [...]
    # }

    # Risk patterns
    risk_patterns = Column(JSONB, nullable=True)  # {
        # retakes: [...],
        # withdrawals: [...],
        # semester_below_threshold: [...],
        # declining_trend_semesters: [...]
    # }

    # Major/minor analysis
    program_analysis = Column(JSONB, nullable=True)  # {
        # declared_majors: [...],
        # declared_minors: [...],
        # major_gpa: float,
        # major_rigor_score: 0-10,
        # interdisciplinary_score: 0-10
    # }

    # Aggregated scores
    overall_score = Column(Float, nullable=True)
    rigor_score = Column(Float, nullable=True)
    performance_score = Column(Float, nullable=True)
    trajectory_score = Column(Float, nullable=True)
    workload_score = Column(Float, nullable=True)
    achievement_score = Column(Float, nullable=True)

    # Adjusted scores (accounting for school difficulty)
    adjusted_gpa = Column(Float, nullable=True)
    adjusted_percentile = Column(Float, nullable=True)

    # Algorithm tracking
    algorithm_version = Column(String(20), nullable=True)

    __table_args__ = (
        Index('ix_transcript_ml_candidate', 'candidate_id'),
    )


# ============================================
# UNIFIED SCORES
# ============================================

class UnifiedCandidateScore(Base):
    """
    Combines all signals into a unified candidate score.
    Tracks how component scores contribute to final score.
    """
    __tablename__ = "unified_candidate_scores"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Target role context
    vertical = Column(String(50), nullable=True)
    role_type = Column(String(50), nullable=True)

    # Component scores (0-100)
    interview_score = Column(Float, nullable=True)
    interview_weight = Column(Float, nullable=True)
    interview_confidence = Column(Float, nullable=True)

    github_score = Column(Float, nullable=True)
    github_weight = Column(Float, nullable=True)
    github_confidence = Column(Float, nullable=True)

    transcript_score = Column(Float, nullable=True)
    transcript_weight = Column(Float, nullable=True)
    transcript_confidence = Column(Float, nullable=True)

    resume_score = Column(Float, nullable=True)
    resume_weight = Column(Float, nullable=True)
    resume_confidence = Column(Float, nullable=True)

    # Final unified score
    overall_score = Column(Float, nullable=False)
    overall_grade = Column(String(5), nullable=True)  # A+, A, A-, B+, etc.
    overall_confidence = Column(Float, nullable=True)  # 0-1

    # Data completeness
    data_completeness = Column(Float, nullable=True)  # 0-1
    signals_available = Column(JSONB, nullable=True)  # {interview: true, github: true, ...}

    # Role fit predictions
    role_fit_scores = Column(JSONB, nullable=True)  # {role: score, ...}
    best_fit_roles = Column(ARRAY(String), nullable=True)

    # Insights
    top_strengths = Column(JSONB, nullable=True)  # [{area, description}, ...]
    key_concerns = Column(JSONB, nullable=True)  # [{area, description}, ...]
    hiring_recommendation = Column(String(50), nullable=True)  # 'strong_yes', 'yes', 'maybe', 'no'

    # Percentile (if enough data)
    percentile = Column(Float, nullable=True)  # 0-100
    percentile_cohort = Column(String(100), nullable=True)  # "Engineering 2025 grads"

    # Algorithm tracking
    algorithm_version = Column(String(20), nullable=True)

    __table_args__ = (
        Index('ix_unified_scores_candidate', 'candidate_id'),
        Index('ix_unified_scores_overall', 'overall_score'),
    )


# ============================================
# ML EXPERIMENTS & A/B TESTS
# ============================================

class MLExperiment(Base):
    """
    Tracks ML experiments for algorithm improvements.
    Enables A/B testing of different scoring approaches.
    """
    __tablename__ = "ml_experiments"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Experiment info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)

    # What's being tested
    experiment_type = Column(String(50), nullable=False)  # 'scoring_algorithm', 'prompt', 'weights'
    target_component = Column(String(50), nullable=True)  # 'interview', 'resume', etc.

    # Variants
    control_config = Column(JSONB, nullable=False)  # {version: ..., prompt: ..., weights: ...}
    treatment_configs = Column(JSONB, nullable=False)  # [{name: 'treatment_a', ...}, ...]

    # Traffic allocation
    traffic_allocation = Column(JSONB, nullable=True)  # {control: 0.5, treatment_a: 0.5}

    # Targeting
    target_verticals = Column(ARRAY(String), nullable=True)  # Null = all
    target_roles = Column(ARRAY(String), nullable=True)

    # Status
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Results
    sample_size = Column(Integer, default=0)
    results = Column(JSONB, nullable=True)  # Per-variant metrics
    statistical_analysis = Column(JSONB, nullable=True)  # p-values, confidence intervals

    # Decision
    winner = Column(String(50), nullable=True)  # 'control', 'treatment_a', 'inconclusive'
    decision_notes = Column(Text, nullable=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index('ix_experiments_status', 'status'),
        Index('ix_experiments_type', 'experiment_type'),
    )


class MLTrainingRun(Base):
    """
    Tracks model training runs for reproducibility.
    """
    __tablename__ = "ml_training_runs"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # What was trained
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'classifier', 'regressor', 'ranker'
    target_component = Column(String(50), nullable=True)  # 'interview_scorer', 'resume_ranker'

    # Base model (for fine-tuning)
    base_model = Column(String(100), nullable=True)  # 'gpt-4', 'claude-3-opus'

    # Training data
    training_data_query = Column(Text, nullable=True)  # SQL/filter used
    training_samples = Column(Integer, nullable=True)
    validation_samples = Column(Integer, nullable=True)
    test_samples = Column(Integer, nullable=True)

    # Data filters
    data_filters = Column(JSONB, nullable=True)  # {min_labels: 1, verticals: [...]}

    # Hyperparameters
    hyperparameters = Column(JSONB, nullable=True)

    # Training metrics
    training_metrics = Column(JSONB, nullable=True)  # {loss: [...], accuracy: [...]}

    # Evaluation metrics
    eval_metrics = Column(JSONB, nullable=True)  # {
        # accuracy, f1, precision, recall,
        # mae, mse, correlation,
        # human_agreement_rate,
        # outcome_prediction_auc
    # }

    # Comparison to baseline
    baseline_comparison = Column(JSONB, nullable=True)  # {metric: {baseline: x, new: y, delta: z}}

    # Artifacts
    model_artifact_path = Column(String, nullable=True)  # S3/R2 path
    model_size_mb = Column(Float, nullable=True)

    # Deployment
    is_deployed = Column(Boolean, default=False)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    deployed_as_version = Column(String(20), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    __table_args__ = (
        Index('ix_training_runs_model', 'model_name'),
        Index('ix_training_runs_deployed', 'is_deployed'),
    )


# ============================================
# CALIBRATION DATA
# ============================================

class ScoreCalibration(Base):
    """
    Calibration data mapping scores to outcomes.
    Used to adjust scores based on real-world results.
    """
    __tablename__ = "score_calibrations"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # What this calibration is for
    vertical = Column(String(50), nullable=True)
    role_type = Column(String(50), nullable=True)
    company_tier = Column(Enum(CompanyTier), nullable=True)

    # Score ranges and their outcomes
    calibration_data = Column(JSONB, nullable=False)  # [{
        # score_min: 7.0, score_max: 7.5,
        # sample_size: 150,
        # hire_rate: 0.35,
        # avg_days_to_hire: 45,
        # companies: [...],
        # typical_levels: [...]
    # }]

    # Statistical confidence
    total_samples = Column(Integer, nullable=True)
    confidence_level = Column(Float, nullable=True)

    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Version
    algorithm_version = Column(String(20), nullable=True)

    __table_args__ = (
        Index('ix_calibrations_vertical_role', 'vertical', 'role_type'),
    )

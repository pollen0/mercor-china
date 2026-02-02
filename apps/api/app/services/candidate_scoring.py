"""
Unified Candidate Scoring Service - Mercor-Competitive Implementation.

Aggregates all signals (interview, GitHub, transcript, resume) into a comprehensive
candidate score with enterprise-grade features:

- Multi-dimensional scoring with confidence intervals
- Cross-signal validation and red flag detection
- Percentile rankings against candidate pool
- Role-specific fit predictions
- Growth trajectory analysis
- Employer-facing hiring recommendations
- Full ML pipeline integration for future model training

The weights are dynamically adjusted based on available signals and data quality.
"""

import logging
import statistics
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.candidate import Candidate, CandidateVerticalProfile
from ..models.interview import InterviewSession
from ..models.github_analysis import GitHubAnalysis
from ..models.course import CandidateTranscript
from ..models.ml_scoring import (
    UnifiedCandidateScore as UnifiedScoreDB,
    ScoringEventType
)

logger = logging.getLogger("pathway.candidate_scoring")


@dataclass
class ComponentScore:
    """Individual component score with comprehensive metadata."""
    score: float  # 0-100
    weight: float  # How much this contributes (0-1)
    confidence: float  # How reliable is this score (0-1)
    available: bool  # Is this data available
    breakdown: dict = field(default_factory=dict)
    strengths: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    # New fields for enhanced scoring
    sub_scores: dict = field(default_factory=dict)  # Detailed sub-dimension scores
    signals: list[dict] = field(default_factory=list)  # Raw signals extracted
    percentile: Optional[float] = None  # Percentile for this component
    trend: Optional[str] = None  # "improving", "stable", "declining"


@dataclass
class RoleFitPrediction:
    """Role fit prediction with confidence interval."""
    role: str
    score: float
    confidence_low: float  # 95% CI lower bound
    confidence_high: float  # 95% CI upper bound
    match_reasons: list[str]
    gap_areas: list[str]
    recommendation: str  # "strong_fit", "good_fit", "potential_fit", "weak_fit"


@dataclass
class HiringRecommendation:
    """Employer-facing hiring recommendation."""
    overall_recommendation: str  # "strong_yes", "yes", "maybe", "no", "strong_no"
    confidence: float
    summary: str
    key_selling_points: list[str]
    potential_risks: list[str]
    interview_focus_areas: list[str]
    comparison_to_cohort: str
    time_sensitivity: Optional[str] = None  # "high" if candidate likely to get offers


@dataclass
class GrowthTrajectory:
    """Candidate's growth analysis over time."""
    trajectory_score: float  # 0-100
    trend: str  # "accelerating", "steady", "plateauing", "declining"
    velocity: float  # Rate of improvement
    consistency: float  # How consistent is improvement
    predicted_6mo_score: float
    predicted_12mo_score: float
    key_growth_areas: list[str]
    stagnant_areas: list[str]


@dataclass
class RedFlag:
    """Detected red flag with severity and context."""
    category: str  # "authenticity", "consistency", "performance", "behavior"
    severity: str  # "critical", "warning", "info"
    description: str
    evidence: list[str]
    mitigating_factors: list[str]
    recommended_action: str


@dataclass
class UnifiedCandidateScore:
    """Complete unified scoring result with enterprise-grade features."""
    # Overall score (0-100)
    overall_score: float
    overall_grade: str  # A+, A, A-, B+, etc.
    score_confidence_interval: tuple[float, float]  # 95% CI

    # Component scores
    interview: ComponentScore
    github: ComponentScore
    transcript: ComponentScore
    resume: ComponentScore

    # Combined insights
    top_strengths: list[str]
    key_concerns: list[str]

    # Fit scores for specific roles/verticals
    role_fit_scores: dict[str, float]  # {"software_engineer": 85, "data_scientist": 78}
    role_fit_predictions: list[RoleFitPrediction]  # Detailed predictions

    # Quality indicators
    data_completeness: float  # 0-1, how much data we have
    confidence: float  # 0-1, how confident in overall score

    # Enhanced features
    percentile: Optional[float] = None
    percentile_by_vertical: dict = field(default_factory=dict)
    percentile_by_school: dict = field(default_factory=dict)

    # Hiring recommendation
    hiring_recommendation: Optional[HiringRecommendation] = None

    # Growth analysis
    growth_trajectory: Optional[GrowthTrajectory] = None

    # Red flags
    red_flags: list[RedFlag] = field(default_factory=list)

    # Cross-signal validation
    signal_consistency_score: float = 0.0  # How consistent are signals across sources
    cross_validation_notes: list[str] = field(default_factory=list)

    # Competitive positioning
    similar_candidates_count: int = 0
    competitive_advantages: list[str] = field(default_factory=list)
    market_demand_score: float = 0.0  # How in-demand is this profile

    # Metadata
    scored_at: datetime = field(default_factory=datetime.utcnow)
    scoring_version: str = "2.0"
    ml_features: dict = field(default_factory=dict)  # Features for ML training


class CandidateScoringService:
    """
    Mercor-Competitive Unified Candidate Scoring Service.

    Features:
    - Dynamic weight algorithm with role/vertical optimization
    - Multi-source signal validation and red flag detection
    - Percentile calculations against candidate pool
    - Role-fit predictions with confidence intervals
    - Growth trajectory analysis
    - Employer-facing hiring recommendations
    - Full ML pipeline integration

    Dynamic Weight Algorithm:
    - Base weights are adjusted based on data availability and quality
    - If a signal is missing, its weight is redistributed proportionally
    - High-confidence signals get slight weight boost
    - Signals with red flags get increased scrutiny

    Base Weights:
    - Interview: 40% (most direct signal of candidate quality)
    - GitHub: 25% (shows actual coding ability and patterns)
    - Transcript: 20% (academic rigor and performance)
    - Resume: 15% (context and presentation)

    These shift based on:
    - Role type (technical roles weight GitHub/Transcript more)
    - Career stage (new grads weight transcript more)
    - Data availability (missing signals redistribute)
    """

    BASE_WEIGHTS = {
        "interview": 0.40,
        "github": 0.25,
        "transcript": 0.20,
        "resume": 0.15
    }

    # Role-specific weight adjustments
    ROLE_WEIGHT_ADJUSTMENTS = {
        # Technical roles increase GitHub weight
        "software_engineer": {"github": 0.10, "interview": -0.05, "transcript": -0.05},
        "frontend_engineer": {"github": 0.08, "interview": -0.03, "transcript": -0.05},
        "backend_engineer": {"github": 0.10, "interview": -0.05, "transcript": -0.05},
        "fullstack_engineer": {"github": 0.10, "interview": -0.05, "transcript": -0.05},
        "mobile_engineer": {"github": 0.08, "interview": -0.03, "transcript": -0.05},
        "devops_engineer": {"github": 0.12, "interview": -0.07, "transcript": -0.05},
        "ml_engineer": {"github": 0.05, "transcript": 0.05, "interview": -0.05, "resume": -0.05},
        "data_scientist": {"transcript": 0.05, "github": 0.05, "interview": -0.05, "resume": -0.05},
        "data_analyst": {"transcript": 0.08, "interview": -0.03, "resume": -0.05},
        "data_engineer": {"github": 0.08, "transcript": 0.02, "interview": -0.05, "resume": -0.05},
        # Non-technical roles decrease GitHub weight
        "product_manager": {"github": -0.15, "interview": 0.10, "resume": 0.05},
        "business_analyst": {"github": -0.15, "interview": 0.08, "transcript": 0.07},
        "marketing_associate": {"github": -0.20, "interview": 0.12, "resume": 0.08},
        "finance_analyst": {"github": -0.15, "transcript": 0.10, "interview": 0.05},
        "consultant": {"github": -0.18, "interview": 0.12, "resume": 0.06},
        "ux_designer": {"github": -0.10, "interview": 0.05, "resume": 0.05},
        "ui_designer": {"github": -0.12, "interview": 0.05, "resume": 0.07},
        "product_designer": {"github": -0.10, "interview": 0.05, "resume": 0.05},
    }

    # Market demand factors (how competitive is hiring for this role)
    ROLE_DEMAND_FACTORS = {
        "software_engineer": 1.2,
        "ml_engineer": 1.4,
        "data_scientist": 1.3,
        "devops_engineer": 1.25,
        "backend_engineer": 1.15,
        "frontend_engineer": 1.1,
        "fullstack_engineer": 1.15,
        "product_manager": 1.1,
        "data_analyst": 1.0,
        "ux_designer": 1.05,
    }

    # Score thresholds for recommendations
    RECOMMENDATION_THRESHOLDS = {
        "strong_yes": 85,
        "yes": 75,
        "maybe": 65,
        "no": 50,
        # Below 50 is "strong_no"
    }

    def __init__(self):
        self._percentile_cache = {}
        self._cache_expiry = datetime.utcnow()

    def calculate_unified_score(
        self,
        candidate: Candidate,
        db: Session,
        role_type: Optional[str] = None,
        vertical: Optional[str] = None,
        include_percentiles: bool = True,
        include_recommendations: bool = True,
        include_growth_analysis: bool = True,
        store_for_ml: bool = True
    ) -> UnifiedCandidateScore:
        """
        Calculate unified candidate score aggregating all available signals.

        This is the main entry point for comprehensive candidate evaluation,
        integrating all scoring dimensions with enterprise-grade features.

        Args:
            candidate: The candidate to score
            db: Database session
            role_type: Target role (affects weight distribution)
            vertical: Target vertical (engineering, data, business, design)
            include_percentiles: Calculate percentile rankings
            include_recommendations: Generate hiring recommendations
            include_growth_analysis: Analyze growth trajectory
            store_for_ml: Store results for ML training

        Returns:
            UnifiedCandidateScore with comprehensive breakdown
        """
        # Fetch all available data with enhanced analysis
        interview_score = self._get_interview_score(candidate, db, vertical)
        github_score = self._get_github_score(candidate, db)
        transcript_score = self._get_transcript_score(candidate, db)
        resume_score = self._get_resume_score(candidate, db)

        # Calculate dynamic weights
        weights = self._calculate_dynamic_weights(
            interview=interview_score,
            github=github_score,
            transcript=transcript_score,
            resume=resume_score,
            role_type=role_type
        )

        # Apply weights to get overall score
        overall = 0.0
        total_weight = 0.0
        total_confidence = 0.0
        score_variance = 0.0

        components = [
            ("interview", interview_score),
            ("github", github_score),
            ("transcript", transcript_score),
            ("resume", resume_score)
        ]

        available_scores = []
        for name, component in components:
            if component.available:
                weight = weights.get(name, 0)
                component.weight = weight
                overall += component.score * weight
                total_weight += weight
                total_confidence += component.confidence * weight
                available_scores.append(component.score)

        # Normalize if weights don't sum to 1
        if total_weight > 0:
            overall = overall / total_weight
            avg_confidence = total_confidence / total_weight
        else:
            overall = 0
            avg_confidence = 0

        # Calculate confidence interval based on score variance and confidence
        if len(available_scores) >= 2:
            score_variance = statistics.stdev(available_scores)
        ci_margin = (1 - avg_confidence) * 15 + score_variance * 0.5
        confidence_interval = (
            max(0, round(overall - ci_margin, 1)),
            min(100, round(overall + ci_margin, 1))
        )

        # Calculate data completeness with quality weighting
        completeness_weights = {"interview": 0.35, "github": 0.25, "transcript": 0.20, "resume": 0.20}
        data_completeness = sum(
            completeness_weights[name] * (1 if comp.available else 0) * comp.confidence
            for name, comp in components
        )

        # Detect red flags across all signals
        red_flags = self._detect_red_flags(
            candidate, interview_score, github_score, transcript_score, resume_score
        )

        # Cross-signal validation
        signal_consistency, cross_validation_notes = self._validate_cross_signals(
            interview_score, github_score, transcript_score, resume_score
        )

        # Aggregate strengths and concerns (prioritized)
        all_strengths = []
        all_concerns = []
        for _, component in components:
            if component.available:
                all_strengths.extend([(s, component.score) for s in component.strengths[:3]])
                all_concerns.extend([(c, 100 - component.score) for c in component.concerns[:2]])

        # Sort by associated score/severity
        all_strengths.sort(key=lambda x: x[1], reverse=True)
        all_concerns.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate and extract
        seen_strengths = set()
        top_strengths = []
        for s, _ in all_strengths:
            if s not in seen_strengths:
                seen_strengths.add(s)
                top_strengths.append(s)
            if len(top_strengths) >= 5:
                break

        seen_concerns = set()
        key_concerns = []
        for c, _ in all_concerns:
            if c not in seen_concerns:
                seen_concerns.add(c)
                key_concerns.append(c)
            if len(key_concerns) >= 3:
                break

        # Calculate role-specific fit scores
        role_fit_scores = self._calculate_role_fit_scores(
            interview_score, github_score, transcript_score, resume_score
        )

        # Generate detailed role fit predictions
        role_fit_predictions = self._generate_role_fit_predictions(
            role_fit_scores, interview_score, github_score, transcript_score, resume_score, role_type
        )

        # Convert to letter grade
        grade = self._score_to_grade(overall)

        # Calculate percentiles if requested
        percentile = None
        percentile_by_vertical = {}
        percentile_by_school = {}
        similar_candidates_count = 0

        if include_percentiles:
            percentile_data = self._calculate_percentiles(
                candidate, overall, db, vertical
            )
            percentile = percentile_data.get("overall")
            percentile_by_vertical = percentile_data.get("by_vertical", {})
            percentile_by_school = percentile_data.get("by_school", {})
            similar_candidates_count = percentile_data.get("similar_count", 0)

        # Generate hiring recommendation
        hiring_recommendation = None
        if include_recommendations:
            hiring_recommendation = self._generate_hiring_recommendation(
                overall, avg_confidence, top_strengths, key_concerns, red_flags,
                role_fit_predictions, percentile, signal_consistency, role_type
            )

        # Analyze growth trajectory
        growth_trajectory = None
        if include_growth_analysis:
            growth_trajectory = self._analyze_growth_trajectory(candidate, db)

        # Calculate competitive positioning
        competitive_advantages = self._identify_competitive_advantages(
            interview_score, github_score, transcript_score, resume_score, percentile
        )

        # Calculate market demand score
        market_demand = self.ROLE_DEMAND_FACTORS.get(role_type, 1.0) if role_type else 1.0

        # Prepare ML features for training
        ml_features = self._extract_ml_features(
            candidate, interview_score, github_score, transcript_score, resume_score,
            overall, role_type, vertical
        )

        result = UnifiedCandidateScore(
            overall_score=round(overall, 1),
            overall_grade=grade,
            score_confidence_interval=confidence_interval,
            interview=interview_score,
            github=github_score,
            transcript=transcript_score,
            resume=resume_score,
            top_strengths=top_strengths,
            key_concerns=key_concerns,
            role_fit_scores=role_fit_scores,
            role_fit_predictions=role_fit_predictions,
            data_completeness=round(data_completeness, 2),
            confidence=round(avg_confidence, 2),
            percentile=percentile,
            percentile_by_vertical=percentile_by_vertical,
            percentile_by_school=percentile_by_school,
            hiring_recommendation=hiring_recommendation,
            growth_trajectory=growth_trajectory,
            red_flags=red_flags,
            signal_consistency_score=round(signal_consistency, 2),
            cross_validation_notes=cross_validation_notes,
            similar_candidates_count=similar_candidates_count,
            competitive_advantages=competitive_advantages,
            market_demand_score=round(market_demand, 2),
            scored_at=datetime.utcnow(),
            scoring_version="2.0",
            ml_features=ml_features
        )

        # Store for ML training if requested
        if store_for_ml:
            self._store_for_ml_training(candidate, result, db, role_type, vertical)

        return result

    def _get_interview_score(
        self,
        candidate: Candidate,
        db: Session,
        vertical: Optional[str] = None
    ) -> ComponentScore:
        """Get interview component score with multi-rater analysis."""
        # Get best vertical profile score
        query = db.query(CandidateVerticalProfile).filter(
            CandidateVerticalProfile.candidate_id == candidate.id,
            CandidateVerticalProfile.status == "completed"
        )

        if vertical:
            query = query.filter(CandidateVerticalProfile.vertical == vertical)

        profile = query.order_by(CandidateVerticalProfile.best_score.desc()).first()

        if not profile or profile.best_score is None:
            return ComponentScore(
                score=0,
                weight=0,
                confidence=0,
                available=False,
                breakdown={"note": "No completed interview"}
            )

        # Convert 0-10 interview score to 0-100
        score = profile.best_score * 10

        # Get detailed breakdown if available
        session = db.query(InterviewSession).filter(
            InterviewSession.id == profile.interview_session_id
        ).first()

        breakdown = {}
        strengths = []
        concerns = []
        signals = []
        sub_scores = {}

        if session and session.ai_summary:
            try:
                import json
                summary = json.loads(session.ai_summary) if isinstance(session.ai_summary, str) else session.ai_summary
                strengths = summary.get("overall_strengths", [])[:4]
                concerns = summary.get("overall_concerns", [])[:3]

                # Extract dimension scores if available
                dimension_scores = summary.get("dimension_scores", {})
                if dimension_scores:
                    sub_scores = {
                        "communication": dimension_scores.get("communication", 0) * 10,
                        "problem_solving": dimension_scores.get("problem_solving", 0) * 10,
                        "domain_knowledge": dimension_scores.get("domain_knowledge", 0) * 10,
                        "motivation": dimension_scores.get("motivation", 0) * 10,
                        "culture_fit": dimension_scores.get("culture_fit", 0) * 10,
                    }

            except Exception as e:
                logger.debug(f"Error parsing interview summary: {e}")

        # Try to get enhanced ML analysis with multi-rater scores
        try:
            from ..models.ml_scoring import InterviewTranscriptML

            ml_analysis = db.query(InterviewTranscriptML).filter(
                InterviewTranscriptML.interview_session_id == session.id if session else None
            ).order_by(InterviewTranscriptML.analyzed_at.desc()).first()

            if ml_analysis:
                # Add multi-rater scores
                breakdown["multi_rater_scores"] = ml_analysis.multi_rater_scores
                breakdown["rater_agreement"] = ml_analysis.inter_rater_agreement
                breakdown["behavioral_signals"] = ml_analysis.behavioral_signals

                # Use calibrated score if available
                if ml_analysis.calibrated_score:
                    score = ml_analysis.calibrated_score * 10  # Convert to 0-100

                # Enhanced sub-scores from multi-rater
                if ml_analysis.dimension_scores:
                    for dim, dim_score in ml_analysis.dimension_scores.items():
                        if isinstance(dim_score, (int, float)):
                            sub_scores[dim] = dim_score * 10

                # Extract behavioral signals as structured signals
                if ml_analysis.behavioral_signals:
                    bs = ml_analysis.behavioral_signals

                    # Filler word rate
                    filler_rate = bs.get("filler_word_rate", 0)
                    if filler_rate > 0.05:
                        signals.append({
                            "type": "behavioral",
                            "severity": "medium" if filler_rate < 0.1 else "high",
                            "description": f"High filler word rate ({filler_rate:.1%})",
                            "evidence": [f"Filler words per minute: {filler_rate * 60:.1f}"],
                            "mitigating": ["May indicate nervousness, not lack of knowledge"],
                            "action": "Assess underlying knowledge in technical screen"
                        })

                    # Confidence indicators
                    confidence_level = bs.get("confidence_level", "medium")
                    if confidence_level == "low":
                        signals.append({
                            "type": "behavioral",
                            "severity": "medium",
                            "description": "Low confidence indicators detected",
                            "evidence": bs.get("hedging_phrases", [])[:3],
                            "mitigating": ["May be interview anxiety"],
                            "action": "Create comfortable environment in next round"
                        })

                # Inter-rater agreement affects confidence
                if ml_analysis.inter_rater_agreement and ml_analysis.inter_rater_agreement >= 0.8:
                    strengths.append("Consistent performance across evaluation criteria")

        except Exception as e:
            logger.debug(f"Enhanced interview data not available: {e}")

        breakdown["best_score"] = profile.best_score
        breakdown["total_interviews"] = profile.total_interviews
        breakdown["vertical"] = profile.vertical.value if profile.vertical else None

        # Confidence based on number of interviews and rater agreement
        base_confidence = min(1.0, 0.5 + profile.total_interviews * 0.1)

        # Boost confidence if multi-rater analysis available
        rater_agreement = breakdown.get("rater_agreement")
        if rater_agreement:
            base_confidence = min(1.0, base_confidence + (rater_agreement - 0.5) * 0.2)

        return ComponentScore(
            score=score,
            weight=self.BASE_WEIGHTS["interview"],
            confidence=base_confidence,
            available=True,
            breakdown=breakdown,
            strengths=strengths[:4],
            concerns=concerns[:3],
            sub_scores=sub_scores,
            signals=signals
        )

    def _get_github_score(self, candidate: Candidate, db: Session) -> ComponentScore:
        """Get GitHub component score with enhanced analysis."""
        analysis = db.query(GitHubAnalysis).filter(
            GitHubAnalysis.candidate_id == candidate.id
        ).first()

        if not analysis or analysis.overall_score is None:
            # Check if GitHub is at least connected
            if candidate.github_username:
                return ComponentScore(
                    score=0,
                    weight=0,
                    confidence=0,
                    available=False,
                    breakdown={"note": "GitHub connected but not analyzed"}
                )
            return ComponentScore(
                score=0,
                weight=0,
                confidence=0,
                available=False,
                breakdown={"note": "GitHub not connected"}
            )

        score = analysis.overall_score  # Already 0-100

        # Enhanced sub-scores breakdown
        sub_scores = {
            "originality": analysis.originality_score or 0,
            "activity": analysis.activity_score or 0,
            "depth": analysis.depth_score or 0,
            "collaboration": analysis.collaboration_score or 0,
        }

        breakdown = {
            "originality": analysis.originality_score,
            "activity": analysis.activity_score,
            "depth": analysis.depth_score,
            "collaboration": analysis.collaboration_score,
            "total_repos": analysis.total_repos_analyzed,
            "total_commits": analysis.total_commits_by_user,
        }

        # Try to get enhanced analysis data if available
        try:
            from ..models.ml_scoring import GitHubAnalysisML

            ml_analysis = db.query(GitHubAnalysisML).filter(
                GitHubAnalysisML.candidate_id == candidate.id
            ).order_by(GitHubAnalysisML.analyzed_at.desc()).first()

            if ml_analysis:
                # Add enhanced metrics
                breakdown["code_quality_score"] = ml_analysis.code_quality_score
                breakdown["documentation_score"] = ml_analysis.documentation_score
                breakdown["testing_score"] = ml_analysis.testing_score
                breakdown["complexity_score"] = ml_analysis.complexity_score
                breakdown["pr_quality_score"] = ml_analysis.pr_quality_score
                breakdown["skill_growth_rate"] = ml_analysis.skill_growth_rate
                breakdown["authenticity_flags"] = ml_analysis.authenticity_flags
                breakdown["languages"] = ml_analysis.primary_languages

                sub_scores["code_quality"] = ml_analysis.code_quality_score or 0
                sub_scores["documentation"] = ml_analysis.documentation_score or 0
                sub_scores["testing"] = ml_analysis.testing_score or 0
        except Exception as e:
            logger.debug(f"Enhanced GitHub data not available: {e}")

        strengths = []
        concerns = []

        # Analyze strengths
        if analysis.originality_score and analysis.originality_score >= 80:
            strengths.append("High code originality")
        elif analysis.originality_score and analysis.originality_score >= 70:
            strengths.append("Good code originality")

        if analysis.depth_score and analysis.depth_score >= 80:
            strengths.append("Deep technical projects")
        elif analysis.depth_score and analysis.depth_score >= 70:
            strengths.append("Solid technical depth")

        if analysis.activity_score and analysis.activity_score >= 80:
            strengths.append("Consistent GitHub activity")

        if analysis.collaboration_score and analysis.collaboration_score >= 80:
            strengths.append("Strong open source collaboration")

        # Check for code quality from enhanced analysis
        code_quality = breakdown.get("code_quality_score")
        if code_quality and code_quality >= 80:
            strengths.append("Excellent code quality")

        testing_score = breakdown.get("testing_score")
        if testing_score and testing_score >= 70:
            strengths.append("Good testing practices")

        # Analyze concerns
        if analysis.originality_score and analysis.originality_score < 40:
            concerns.append("Low code originality - may be tutorial code")

        if analysis.activity_score and analysis.activity_score < 30:
            concerns.append("Limited recent GitHub activity")

        # Check for authenticity flags
        auth_flags = breakdown.get("authenticity_flags", [])
        if auth_flags:
            for flag in auth_flags[:2]:
                if isinstance(flag, dict):
                    concerns.append(flag.get("message", str(flag)))
                elif isinstance(flag, str):
                    concerns.append(flag)

        # Legacy flags from original analysis
        if analysis.flags:
            for flag in analysis.flags[:2]:
                if isinstance(flag, dict):
                    msg = flag.get("message", str(flag))
                    if msg not in concerns:
                        concerns.append(msg)
                elif isinstance(flag, str) and flag not in concerns:
                    concerns.append(flag)

        # Confidence based on amount of data
        repos_factor = min(1.0, (analysis.total_repos_analyzed or 0) / 10)
        commits_factor = min(1.0, (analysis.total_commits_by_user or 0) / 100)
        base_confidence = 0.5 + (repos_factor + commits_factor) / 4

        # Boost confidence if enhanced analysis available
        if breakdown.get("code_quality_score"):
            base_confidence = min(1.0, base_confidence + 0.1)

        return ComponentScore(
            score=score,
            weight=self.BASE_WEIGHTS["github"],
            confidence=base_confidence,
            available=True,
            breakdown=breakdown,
            strengths=strengths[:4],
            concerns=concerns[:3],
            sub_scores=sub_scores
        )

    def _get_transcript_score(self, candidate: Candidate, db: Session) -> ComponentScore:
        """Get transcript component score with calibration."""
        transcript = db.query(CandidateTranscript).filter(
            CandidateTranscript.candidate_id == candidate.id
        ).first()

        if not transcript or transcript.transcript_score is None:
            return ComponentScore(
                score=0,
                weight=0,
                confidence=0,
                available=False,
                breakdown={"note": "Transcript not analyzed"}
            )

        score = transcript.transcript_score  # Already 0-100

        # Enhanced sub-scores
        sub_scores = {
            "course_rigor": transcript.course_rigor_score or 0,
            "performance": transcript.performance_score or 0,
            "trajectory": transcript.trajectory_score or 0,
            "load": transcript.load_score or 0,
        }

        breakdown = {
            "course_rigor": transcript.course_rigor_score,
            "performance": transcript.performance_score,
            "trajectory": transcript.trajectory_score,
            "load": transcript.load_score,
            "gpa": transcript.cumulative_gpa,
            "technical_gpa": transcript.major_gpa,
            "semesters_analyzed": transcript.semesters_analyzed,
        }

        strengths = []
        concerns = []

        # Try to get enhanced ML analysis with calibration
        try:
            from ..models.ml_scoring import TranscriptAnalysisML

            ml_analysis = db.query(TranscriptAnalysisML).filter(
                TranscriptAnalysisML.candidate_id == candidate.id
            ).order_by(TranscriptAnalysisML.analyzed_at.desc()).first()

            if ml_analysis:
                # Add calibrated data
                breakdown["adjusted_gpa"] = ml_analysis.adjusted_gpa
                breakdown["grade_inflation_factor"] = ml_analysis.grade_inflation_factor
                breakdown["cross_school_percentile"] = ml_analysis.cross_school_percentile
                breakdown["difficulty_adjustment"] = ml_analysis.difficulty_adjustment
                breakdown["hardest_courses"] = ml_analysis.hardest_courses
                breakdown["grade_trend"] = ml_analysis.grade_trend

                sub_scores["adjusted_gpa_score"] = (ml_analysis.adjusted_gpa / 4.0 * 100) if ml_analysis.adjusted_gpa else 0

                # Use adjusted score if available
                if ml_analysis.calibrated_score:
                    score = ml_analysis.calibrated_score

                # Enhanced strengths/concerns from ML analysis
                if ml_analysis.cross_school_percentile and ml_analysis.cross_school_percentile >= 80:
                    strengths.append(f"Top {100 - ml_analysis.cross_school_percentile:.0f}% across similar schools")

                if ml_analysis.grade_trend == "improving":
                    strengths.append("Strong upward grade trajectory")
                elif ml_analysis.grade_trend == "declining":
                    concerns.append("Declining grade trajectory")

                hardest = ml_analysis.hardest_courses or []
                if len(hardest) >= 3:
                    strengths.append("Tackled challenging coursework")

        except Exception as e:
            logger.debug(f"Enhanced transcript data not available: {e}")

        # Standard strengths/concerns from transcript
        if transcript.score_breakdown:
            base_strengths = transcript.score_breakdown.get("strengths", [])
            base_concerns = transcript.score_breakdown.get("concerns", [])
            # Add only unique ones
            for s in base_strengths[:2]:
                if s not in strengths:
                    strengths.append(s)
            for c in base_concerns[:2]:
                if c not in concerns:
                    concerns.append(c)

        # Analyze individual components
        if transcript.course_rigor_score and transcript.course_rigor_score >= 80:
            if "rigorous coursework" not in " ".join(strengths).lower():
                strengths.append("Rigorous course selection")

        if transcript.trajectory_score and transcript.trajectory_score >= 80:
            if "trajectory" not in " ".join(strengths).lower():
                strengths.append("Consistent grade improvement")

        if transcript.cumulative_gpa and transcript.cumulative_gpa >= 3.7:
            strengths.append(f"Strong GPA ({transcript.cumulative_gpa:.2f})")

        if transcript.cumulative_gpa and transcript.cumulative_gpa < 2.5:
            concerns.append(f"Low GPA ({transcript.cumulative_gpa:.2f})")

        if transcript.trajectory_score and transcript.trajectory_score < 30:
            if "declining" not in " ".join(concerns).lower():
                concerns.append("Grades declining over time")

        # Confidence based on amount of data
        semesters = transcript.semesters_analyzed or 0
        courses_factor = min(1.0, semesters / 6)
        base_confidence = 0.6 + courses_factor * 0.4

        # Boost confidence if calibrated data available
        if breakdown.get("adjusted_gpa"):
            base_confidence = min(1.0, base_confidence + 0.1)

        return ComponentScore(
            score=score,
            weight=self.BASE_WEIGHTS["transcript"],
            confidence=base_confidence,
            available=True,
            breakdown=breakdown,
            strengths=strengths[:4],
            concerns=concerns[:3],
            sub_scores=sub_scores
        )

    def _get_resume_score(self, candidate: Candidate, db: Session) -> ComponentScore:
        """
        Get resume component score using enhanced resume scoring service.
        Integrates with the comprehensive resume_scoring.py service.
        """
        if not candidate.resume_parsed_data:
            return ComponentScore(
                score=0,
                weight=0,
                confidence=0,
                available=False,
                breakdown={"note": "Resume not uploaded or parsed"}
            )

        try:
            # Try to use enhanced resume scoring service
            from .resume_scoring import resume_scoring_service

            # Get the target role if available from vertical profile
            target_role = None
            profile = db.query(CandidateVerticalProfile).filter(
                CandidateVerticalProfile.candidate_id == candidate.id
            ).first()
            if profile and profile.role_type:
                target_role = profile.role_type.value if hasattr(profile.role_type, 'value') else profile.role_type

            # Get comprehensive resume score
            result = resume_scoring_service.score_resume(
                parsed_resume=candidate.resume_parsed_data,
                target_role=target_role
            )

            # Map to ComponentScore
            sub_scores = {
                "experience_relevance": result.get("dimension_scores", {}).get("experience_relevance", 50),
                "experience_progression": result.get("dimension_scores", {}).get("experience_progression", 50),
                "skill_depth": result.get("dimension_scores", {}).get("skill_depth", 50),
                "education_quality": result.get("dimension_scores", {}).get("education_quality", 50),
                "project_impact": result.get("dimension_scores", {}).get("project_impact", 50),
            }

            breakdown = {
                "experience_count": len(result.get("experience_analysis", {}).get("companies", [])),
                "skills_count": len(result.get("skill_analysis", {}).get("matched_skills", [])),
                "projects_count": len(candidate.resume_parsed_data.get("projects", [])),
                "company_tiers": result.get("experience_analysis", {}).get("company_tiers", {}),
                "years_experience": result.get("experience_analysis", {}).get("total_years", 0),
                "skill_depth_scores": result.get("skill_analysis", {}).get("depth_by_category", {}),
                "dimension_scores": sub_scores,
            }

            strengths = result.get("strengths", [])
            concerns = result.get("concerns", [])

            # Calculate confidence based on data quality
            data = candidate.resume_parsed_data
            experience = data.get("experience", [])
            skills = data.get("skills", [])
            projects = data.get("projects", [])

            data_quality = 0.5
            if len(experience) >= 2:
                data_quality += 0.15
            if len(skills) >= 5:
                data_quality += 0.15
            if len(projects) >= 2:
                data_quality += 0.1
            if data.get("education"):
                data_quality += 0.1

            return ComponentScore(
                score=result.get("overall_score", 50),
                weight=self.BASE_WEIGHTS["resume"],
                confidence=min(1.0, data_quality),
                available=True,
                breakdown=breakdown,
                strengths=strengths[:4],
                concerns=concerns[:3],
                sub_scores=sub_scores
            )

        except ImportError:
            logger.warning("Resume scoring service not available, using fallback")
        except Exception as e:
            logger.warning(f"Error using resume scoring service: {e}, using fallback")

        # Fallback to basic scoring
        data = candidate.resume_parsed_data
        score = 50  # Base score

        strengths = []
        concerns = []

        # Experience section (up to +20)
        experience = data.get("experience", [])
        if len(experience) >= 2:
            score += 15
            strengths.append(f"{len(experience)} work experiences")
        elif len(experience) >= 1:
            score += 10

        # Education section (up to +15)
        education = data.get("education", [])
        if education:
            score += 10
            if any(e.get("gpa") for e in education):
                score += 5

        # Skills section (up to +10)
        skills = data.get("skills", [])
        if len(skills) >= 5:
            score += 10
            strengths.append(f"{len(skills)} skills listed")
        elif len(skills) >= 3:
            score += 5

        # Projects section (up to +10)
        projects = data.get("projects", [])
        if len(projects) >= 2:
            score += 10
            strengths.append(f"{len(projects)} projects")
        elif len(projects) >= 1:
            score += 5

        # Contact info (up to +5)
        if data.get("email") and data.get("phone"):
            score += 5

        breakdown = {
            "experience_count": len(experience),
            "education_count": len(education),
            "skills_count": len(skills),
            "projects_count": len(projects),
            "has_contact_info": bool(data.get("email"))
        }

        if not experience:
            concerns.append("No work experience listed")
        if not skills:
            concerns.append("No skills section")

        return ComponentScore(
            score=min(100, score),
            weight=self.BASE_WEIGHTS["resume"],
            confidence=0.7,
            available=True,
            breakdown=breakdown,
            strengths=strengths,
            concerns=concerns
        )

    def _calculate_dynamic_weights(
        self,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore,
        role_type: Optional[str] = None
    ) -> dict[str, float]:
        """
        Calculate dynamic weights based on data availability and role.
        """
        weights = dict(self.BASE_WEIGHTS)

        # Apply role-specific adjustments
        if role_type and role_type in self.ROLE_WEIGHT_ADJUSTMENTS:
            adjustments = self.ROLE_WEIGHT_ADJUSTMENTS[role_type]
            for component, adj in adjustments.items():
                weights[component] = max(0, weights[component] + adj)

        # Redistribute weights from unavailable components
        available = {
            "interview": interview.available,
            "github": github.available,
            "transcript": transcript.available,
            "resume": resume.available
        }

        total_available_weight = sum(weights[k] for k, v in available.items() if v)
        unavailable_weight = sum(weights[k] for k, v in available.items() if not v)

        if total_available_weight > 0 and unavailable_weight > 0:
            # Redistribute proportionally
            redistribution_factor = 1 + (unavailable_weight / total_available_weight)
            for component, is_available in available.items():
                if is_available:
                    weights[component] *= redistribution_factor
                else:
                    weights[component] = 0

        # Normalize to sum to 1
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        # Slight boost for high-confidence signals
        confidence_boost = 0.05
        components = {
            "interview": interview,
            "github": github,
            "transcript": transcript,
            "resume": resume
        }

        for component, data in components.items():
            if data.available and data.confidence >= 0.8:
                boost = confidence_boost * (data.confidence - 0.7)
                weights[component] += boost

        # Re-normalize
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}

        return weights

    def _calculate_role_fit_scores(
        self,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore
    ) -> dict[str, float]:
        """
        Calculate fit scores for different roles.
        Higher GitHub scores favor technical roles.
        Higher interview scores favor communication-heavy roles.
        """
        scores = {}

        # Get raw scores (default to 50 if not available)
        i_score = interview.score if interview.available else 50
        g_score = github.score if github.available else 50
        t_score = transcript.score if transcript.available else 50
        r_score = resume.score if resume.available else 50

        # Technical roles (heavy GitHub/Transcript)
        for role in ["software_engineer", "backend_engineer", "fullstack_engineer"]:
            scores[role] = g_score * 0.35 + t_score * 0.25 + i_score * 0.30 + r_score * 0.10

        # Data roles (balanced)
        for role in ["data_scientist", "ml_engineer", "data_analyst"]:
            scores[role] = g_score * 0.25 + t_score * 0.30 + i_score * 0.30 + r_score * 0.15

        # Business roles (heavy interview)
        for role in ["product_manager", "business_analyst", "consultant"]:
            scores[role] = i_score * 0.45 + r_score * 0.25 + t_score * 0.20 + g_score * 0.10

        # Design roles (balanced)
        for role in ["ux_designer", "ui_designer", "product_designer"]:
            scores[role] = i_score * 0.40 + r_score * 0.30 + g_score * 0.15 + t_score * 0.15

        return {k: round(v, 1) for k, v in scores.items()}

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 97:
            return "A+"
        elif score >= 93:
            return "A"
        elif score >= 90:
            return "A-"
        elif score >= 87:
            return "B+"
        elif score >= 83:
            return "B"
        elif score >= 80:
            return "B-"
        elif score >= 77:
            return "C+"
        elif score >= 73:
            return "C"
        elif score >= 70:
            return "C-"
        elif score >= 67:
            return "D+"
        elif score >= 63:
            return "D"
        elif score >= 60:
            return "D-"
        else:
            return "F"

    # ==========================================================================
    # RED FLAG DETECTION
    # ==========================================================================

    def _detect_red_flags(
        self,
        candidate: Candidate,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore
    ) -> list[RedFlag]:
        """Detect red flags across all scoring signals."""
        flags = []

        # Check for authenticity concerns in GitHub
        if github.available:
            gh_breakdown = github.breakdown
            originality = gh_breakdown.get("originality", 100)

            if originality < 40:
                flags.append(RedFlag(
                    category="authenticity",
                    severity="critical",
                    description="Low code originality detected",
                    evidence=[
                        f"Originality score: {originality}/100",
                        "High similarity to tutorial code or AI-generated patterns"
                    ],
                    mitigating_factors=[
                        "Could be learning projects",
                        "May have legitimate forks"
                    ],
                    recommended_action="Request live coding assessment"
                ))

            # Check for suspicious activity patterns
            if gh_breakdown.get("activity", 0) < 20 and gh_breakdown.get("total_commits", 0) > 500:
                flags.append(RedFlag(
                    category="authenticity",
                    severity="warning",
                    description="Unusual commit pattern",
                    evidence=[
                        "High commit count but low activity score",
                        "May indicate bulk/automated commits"
                    ],
                    mitigating_factors=["Could be from active OSS maintenance"],
                    recommended_action="Review commit history in interview"
                ))

        # Check for consistency between resume and other signals
        if resume.available and interview.available:
            resume_exp_count = resume.breakdown.get("experience_count", 0)
            interview_score = interview.score

            # Strong resume but weak interview is a yellow flag
            if resume.score > 80 and interview_score < 60:
                flags.append(RedFlag(
                    category="consistency",
                    severity="warning",
                    description="Resume quality doesn't match interview performance",
                    evidence=[
                        f"Resume score: {resume.score:.0f}",
                        f"Interview score: {interview_score:.0f}"
                    ],
                    mitigating_factors=[
                        "May have interview anxiety",
                        "Resume may be professionally edited"
                    ],
                    recommended_action="Conduct additional technical screen"
                ))

        # Check for transcript concerns
        if transcript.available:
            tr_breakdown = transcript.breakdown
            gpa = tr_breakdown.get("gpa", 4.0)
            trajectory = tr_breakdown.get("trajectory", 50)

            if gpa and gpa < 2.5:
                flags.append(RedFlag(
                    category="performance",
                    severity="warning",
                    description="Low academic performance",
                    evidence=[f"GPA: {gpa:.2f}"],
                    mitigating_factors=[
                        "May have improved recently",
                        "May have worked during school"
                    ],
                    recommended_action="Discuss academic journey in interview"
                ))

            if trajectory < 30:
                flags.append(RedFlag(
                    category="performance",
                    severity="warning",
                    description="Declining academic trajectory",
                    evidence=["Grade trajectory shows decline over time"],
                    mitigating_factors=["May have taken harder courses"],
                    recommended_action="Understand context of academic changes"
                ))

        # Check for behavioral concerns from interview
        if interview.available:
            signals = interview.signals
            for signal in signals:
                if signal.get("type") == "behavioral" and signal.get("severity") == "high":
                    flags.append(RedFlag(
                        category="behavior",
                        severity="warning",
                        description=signal.get("description", "Behavioral concern detected"),
                        evidence=signal.get("evidence", []),
                        mitigating_factors=signal.get("mitigating", []),
                        recommended_action=signal.get("action", "Follow up in next interview")
                    ))

        return flags

    # ==========================================================================
    # CROSS-SIGNAL VALIDATION
    # ==========================================================================

    def _validate_cross_signals(
        self,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore
    ) -> tuple[float, list[str]]:
        """
        Validate consistency across different scoring signals.
        Returns consistency score (0-1) and notes about discrepancies.
        """
        notes = []
        consistency_scores = []

        available_scores = []
        if interview.available:
            available_scores.append(("interview", interview.score))
        if github.available:
            available_scores.append(("github", github.score))
        if transcript.available:
            available_scores.append(("transcript", transcript.score))
        if resume.available:
            available_scores.append(("resume", resume.score))

        if len(available_scores) < 2:
            return 1.0, ["Insufficient data for cross-validation"]

        # Calculate pairwise consistency
        scores_only = [s for _, s in available_scores]
        if len(scores_only) >= 2:
            mean_score = statistics.mean(scores_only)
            stdev = statistics.stdev(scores_only) if len(scores_only) > 1 else 0

            # Consistency is inverse of coefficient of variation
            if mean_score > 0:
                cv = stdev / mean_score
                base_consistency = max(0, 1 - cv)
            else:
                base_consistency = 0.5
        else:
            base_consistency = 1.0

        consistency_scores.append(base_consistency)

        # Check specific cross-validations
        # GitHub vs Interview (technical skills)
        if github.available and interview.available:
            diff = abs(github.score - interview.score)
            if diff > 30:
                lower = "GitHub" if github.score < interview.score else "Interview"
                higher = "Interview" if lower == "GitHub" else "GitHub"
                notes.append(f"Large gap between {lower} ({min(github.score, interview.score):.0f}) and {higher} ({max(github.score, interview.score):.0f})")
                consistency_scores.append(max(0, 1 - diff / 50))

        # Transcript vs GitHub (for technical roles)
        if transcript.available and github.available:
            tr_tech = transcript.breakdown.get("technical_gpa", transcript.breakdown.get("gpa", 3.0))
            gh_depth = github.breakdown.get("depth", 50)

            # Convert GPA to 0-100 scale
            tr_score_normalized = (tr_tech / 4.0) * 100 if tr_tech else 50
            if abs(tr_score_normalized - gh_depth) > 35:
                notes.append("Discrepancy between academic rigor and GitHub project depth")
                consistency_scores.append(0.7)

        # Resume claims vs evidence
        if resume.available and github.available:
            resume_skills = resume.breakdown.get("skills_count", 0)
            gh_repos = github.breakdown.get("total_repos", 0)

            # Many skills claimed but few repos
            if resume_skills > 10 and gh_repos < 3:
                notes.append("Many skills listed but limited GitHub evidence")
                consistency_scores.append(0.75)

        # Calculate final consistency score
        final_consistency = statistics.mean(consistency_scores) if consistency_scores else 0.5

        if final_consistency > 0.85:
            notes.insert(0, "Strong consistency across all signals")
        elif final_consistency < 0.6:
            notes.insert(0, "Notable inconsistencies detected - recommend deeper evaluation")

        return final_consistency, notes

    # ==========================================================================
    # ROLE FIT PREDICTIONS
    # ==========================================================================

    def _generate_role_fit_predictions(
        self,
        role_fit_scores: dict[str, float],
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore,
        target_role: Optional[str] = None
    ) -> list[RoleFitPrediction]:
        """Generate detailed role fit predictions with confidence intervals."""
        predictions = []

        # Define role requirements
        role_requirements = {
            "software_engineer": {
                "primary": ["github", "interview"],
                "secondary": ["transcript"],
                "key_skills": ["coding", "problem_solving", "system_design"],
                "key_traits": ["technical_depth", "collaboration"]
            },
            "ml_engineer": {
                "primary": ["github", "transcript"],
                "secondary": ["interview"],
                "key_skills": ["python", "ml_frameworks", "math"],
                "key_traits": ["analytical", "research_oriented"]
            },
            "data_scientist": {
                "primary": ["transcript", "github"],
                "secondary": ["interview"],
                "key_skills": ["statistics", "python", "sql"],
                "key_traits": ["analytical", "communication"]
            },
            "product_manager": {
                "primary": ["interview", "resume"],
                "secondary": ["transcript"],
                "key_skills": ["communication", "strategy", "analytics"],
                "key_traits": ["leadership", "customer_focus"]
            },
            "ux_designer": {
                "primary": ["interview", "resume"],
                "secondary": ["github"],
                "key_skills": ["design_thinking", "user_research", "prototyping"],
                "key_traits": ["creativity", "empathy"]
            }
        }

        # If target role specified, prioritize it
        roles_to_analyze = list(role_fit_scores.keys())
        if target_role and target_role in roles_to_analyze:
            roles_to_analyze.remove(target_role)
            roles_to_analyze.insert(0, target_role)

        for role in roles_to_analyze[:5]:  # Top 5 roles
            score = role_fit_scores.get(role, 50)
            reqs = role_requirements.get(role, {
                "primary": ["interview"],
                "secondary": ["github", "transcript"],
                "key_skills": [],
                "key_traits": []
            })

            # Calculate confidence interval based on data quality for this role
            primary_available = sum(1 for c in reqs["primary"] if self._component_available(c, interview, github, transcript, resume))
            secondary_available = sum(1 for c in reqs["secondary"] if self._component_available(c, interview, github, transcript, resume))

            data_quality = (primary_available / max(1, len(reqs["primary"])) * 0.7 +
                          secondary_available / max(1, len(reqs["secondary"])) * 0.3)

            ci_margin = (1 - data_quality) * 15 + 5  # Base margin of 5
            confidence_low = max(0, score - ci_margin)
            confidence_high = min(100, score + ci_margin)

            # Determine match reasons and gaps
            match_reasons = []
            gap_areas = []

            if github.available and github.score >= 70:
                match_reasons.append("Strong technical foundation (GitHub)")
            if interview.available and interview.score >= 75:
                match_reasons.append("Excellent interview performance")
            if transcript.available and transcript.score >= 80:
                match_reasons.append("Strong academic record")

            if github.available and github.score < 50 and "github" in reqs["primary"]:
                gap_areas.append("Technical portfolio needs strengthening")
            if interview.available and interview.score < 60 and "interview" in reqs["primary"]:
                gap_areas.append("Interview skills need development")

            # Determine recommendation
            if score >= 85:
                recommendation = "strong_fit"
            elif score >= 70:
                recommendation = "good_fit"
            elif score >= 55:
                recommendation = "potential_fit"
            else:
                recommendation = "weak_fit"

            predictions.append(RoleFitPrediction(
                role=role,
                score=round(score, 1),
                confidence_low=round(confidence_low, 1),
                confidence_high=round(confidence_high, 1),
                match_reasons=match_reasons[:3],
                gap_areas=gap_areas[:2],
                recommendation=recommendation
            ))

        return predictions

    def _component_available(
        self,
        component_name: str,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore
    ) -> bool:
        """Check if a component is available."""
        mapping = {
            "interview": interview,
            "github": github,
            "transcript": transcript,
            "resume": resume
        }
        return mapping.get(component_name, ComponentScore(0, 0, 0, False)).available

    # ==========================================================================
    # PERCENTILE CALCULATIONS
    # ==========================================================================

    def _calculate_percentiles(
        self,
        candidate: Candidate,
        overall_score: float,
        db: Session,
        vertical: Optional[str] = None
    ) -> dict:
        """Calculate percentile rankings against candidate pool."""
        result = {
            "overall": None,
            "by_vertical": {},
            "by_school": {},
            "similar_count": 0
        }

        try:
            # Get all scored candidates
            from ..models.ml_scoring import UnifiedCandidateScore as UnifiedScoreDB

            # Overall percentile
            total_count = db.query(func.count(UnifiedScoreDB.id)).filter(
                UnifiedScoreDB.overall_score.isnot(None)
            ).scalar() or 0

            below_count = db.query(func.count(UnifiedScoreDB.id)).filter(
                UnifiedScoreDB.overall_score < overall_score
            ).scalar() or 0

            if total_count > 0:
                result["overall"] = round((below_count / total_count) * 100, 1)

            # Percentile by vertical
            if vertical:
                vertical_count = db.query(func.count(UnifiedScoreDB.id)).filter(
                    UnifiedScoreDB.vertical == vertical,
                    UnifiedScoreDB.overall_score.isnot(None)
                ).scalar() or 0

                vertical_below = db.query(func.count(UnifiedScoreDB.id)).filter(
                    UnifiedScoreDB.vertical == vertical,
                    UnifiedScoreDB.overall_score < overall_score
                ).scalar() or 0

                if vertical_count > 0:
                    result["by_vertical"][vertical] = round((vertical_below / vertical_count) * 100, 1)

            # Percentile by school (if available)
            if candidate.university:
                school_count = db.query(func.count(UnifiedScoreDB.id)).join(
                    Candidate, UnifiedScoreDB.candidate_id == Candidate.id
                ).filter(
                    Candidate.university == candidate.university,
                    UnifiedScoreDB.overall_score.isnot(None)
                ).scalar() or 0

                school_below = db.query(func.count(UnifiedScoreDB.id)).join(
                    Candidate, UnifiedScoreDB.candidate_id == Candidate.id
                ).filter(
                    Candidate.university == candidate.university,
                    UnifiedScoreDB.overall_score < overall_score
                ).scalar() or 0

                if school_count > 0:
                    result["by_school"][candidate.university] = round((school_below / school_count) * 100, 1)

            # Count similar candidates (within 5 points)
            result["similar_count"] = db.query(func.count(UnifiedScoreDB.id)).filter(
                and_(
                    UnifiedScoreDB.overall_score >= overall_score - 5,
                    UnifiedScoreDB.overall_score <= overall_score + 5,
                    UnifiedScoreDB.candidate_id != candidate.id
                )
            ).scalar() or 0

        except Exception as e:
            logger.warning(f"Error calculating percentiles: {e}")

        return result

    # ==========================================================================
    # HIRING RECOMMENDATIONS
    # ==========================================================================

    def _generate_hiring_recommendation(
        self,
        overall_score: float,
        confidence: float,
        strengths: list[str],
        concerns: list[str],
        red_flags: list[RedFlag],
        role_predictions: list[RoleFitPrediction],
        percentile: Optional[float],
        signal_consistency: float,
        target_role: Optional[str] = None
    ) -> HiringRecommendation:
        """Generate employer-facing hiring recommendation."""

        # Determine overall recommendation
        critical_flags = [f for f in red_flags if f.severity == "critical"]
        warning_flags = [f for f in red_flags if f.severity == "warning"]

        # Start with score-based recommendation
        if overall_score >= self.RECOMMENDATION_THRESHOLDS["strong_yes"]:
            base_rec = "strong_yes"
        elif overall_score >= self.RECOMMENDATION_THRESHOLDS["yes"]:
            base_rec = "yes"
        elif overall_score >= self.RECOMMENDATION_THRESHOLDS["maybe"]:
            base_rec = "maybe"
        elif overall_score >= self.RECOMMENDATION_THRESHOLDS["no"]:
            base_rec = "no"
        else:
            base_rec = "strong_no"

        # Adjust for red flags
        rec_order = ["strong_yes", "yes", "maybe", "no", "strong_no"]
        rec_idx = rec_order.index(base_rec)

        if critical_flags:
            rec_idx = min(rec_idx + 2, 4)  # Downgrade by 2 levels
        elif len(warning_flags) >= 2:
            rec_idx = min(rec_idx + 1, 4)  # Downgrade by 1 level

        # Boost for high consistency
        if signal_consistency > 0.9 and confidence > 0.8:
            rec_idx = max(rec_idx - 1, 0)  # Upgrade by 1 level

        final_recommendation = rec_order[rec_idx]

        # Generate summary
        summary_parts = []
        if final_recommendation in ["strong_yes", "yes"]:
            summary_parts.append(f"Strong candidate with overall score of {overall_score:.0f}")
            if percentile and percentile >= 80:
                summary_parts.append(f"Top {100 - percentile:.0f}% of candidate pool")
        elif final_recommendation == "maybe":
            summary_parts.append(f"Moderate candidate (score: {overall_score:.0f}) with mixed signals")
        else:
            summary_parts.append(f"Below-threshold candidate (score: {overall_score:.0f})")

        if critical_flags:
            summary_parts.append(f"Has {len(critical_flags)} critical concern(s) requiring attention")

        summary = ". ".join(summary_parts) + "."

        # Key selling points
        selling_points = []
        if percentile and percentile >= 90:
            selling_points.append(f"Top {100 - percentile:.0f}% performer")
        selling_points.extend(strengths[:3])

        # Potential risks
        risks = []
        for flag in red_flags[:2]:
            risks.append(flag.description)
        risks.extend(concerns[:2])

        # Interview focus areas
        focus_areas = []
        for flag in red_flags:
            if flag.recommended_action:
                focus_areas.append(flag.recommended_action)

        if target_role:
            role_pred = next((p for p in role_predictions if p.role == target_role), None)
            if role_pred:
                focus_areas.extend([f"Assess: {gap}" for gap in role_pred.gap_areas[:2]])

        # Comparison to cohort
        if percentile:
            if percentile >= 90:
                cohort_comparison = "Exceptional - top 10% of candidates"
            elif percentile >= 75:
                cohort_comparison = "Strong - top quartile performer"
            elif percentile >= 50:
                cohort_comparison = "Average - middle of the pack"
            elif percentile >= 25:
                cohort_comparison = "Below average - bottom quartile"
            else:
                cohort_comparison = "Weak - bottom 25% of candidates"
        else:
            cohort_comparison = "Unable to compare - insufficient pool data"

        # Time sensitivity (high for strong candidates)
        time_sensitivity = None
        if final_recommendation in ["strong_yes", "yes"] and percentile and percentile >= 80:
            time_sensitivity = "high"

        return HiringRecommendation(
            overall_recommendation=final_recommendation,
            confidence=confidence,
            summary=summary,
            key_selling_points=selling_points[:4],
            potential_risks=risks[:3],
            interview_focus_areas=list(dict.fromkeys(focus_areas))[:4],
            comparison_to_cohort=cohort_comparison,
            time_sensitivity=time_sensitivity
        )

    # ==========================================================================
    # GROWTH TRAJECTORY ANALYSIS
    # ==========================================================================

    def _analyze_growth_trajectory(
        self,
        candidate: Candidate,
        db: Session
    ) -> Optional[GrowthTrajectory]:
        """Analyze candidate's growth over time based on interview history."""
        try:
            # Get interview history
            profiles = db.query(CandidateVerticalProfile).filter(
                CandidateVerticalProfile.candidate_id == candidate.id
            ).all()

            if not profiles:
                return None

            # Collect all scores with timestamps
            all_scores = []
            for profile in profiles:
                if profile.interview_history:
                    for entry in profile.interview_history:
                        if isinstance(entry, dict) and entry.get("score") and entry.get("completed_at"):
                            try:
                                score = float(entry["score"])
                                timestamp = entry["completed_at"]
                                if isinstance(timestamp, str):
                                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                                all_scores.append((timestamp, score))
                            except (ValueError, TypeError):
                                continue

            if len(all_scores) < 2:
                return None

            # Sort by time
            all_scores.sort(key=lambda x: x[0])

            # Calculate trajectory metrics
            scores_only = [s for _, s in all_scores]
            recent_scores = scores_only[-3:] if len(scores_only) >= 3 else scores_only
            early_scores = scores_only[:3] if len(scores_only) >= 3 else scores_only

            avg_recent = statistics.mean(recent_scores)
            avg_early = statistics.mean(early_scores)
            overall_change = avg_recent - avg_early

            # Calculate velocity (improvement rate)
            time_span = (all_scores[-1][0] - all_scores[0][0]).days
            if time_span > 0:
                velocity = overall_change / (time_span / 30)  # Per month
            else:
                velocity = 0

            # Determine trend
            if velocity > 0.5:
                trend = "accelerating"
            elif velocity > 0.1:
                trend = "steady"
            elif velocity > -0.1:
                trend = "plateauing"
            else:
                trend = "declining"

            # Calculate consistency (inverse of variance)
            if len(scores_only) >= 3:
                variance = statistics.variance(scores_only)
                consistency = max(0, 1 - min(1, variance / 100))
            else:
                consistency = 0.5

            # Project future scores
            current_avg = statistics.mean(scores_only[-2:]) if len(scores_only) >= 2 else scores_only[-1]
            predicted_6mo = min(100, current_avg + velocity * 6)
            predicted_12mo = min(100, current_avg + velocity * 12)

            # Identify growth and stagnant areas
            key_growth = []
            stagnant = []

            if velocity > 0:
                key_growth.append("Overall interview performance improving")
            if trend == "accelerating":
                key_growth.append("Rate of improvement is increasing")

            if trend in ["plateauing", "declining"]:
                stagnant.append("Interview scores have plateaued")

            # Calculate trajectory score (0-100)
            trajectory_score = 50  # Base
            trajectory_score += velocity * 10  # Velocity bonus
            trajectory_score += (consistency - 0.5) * 20  # Consistency bonus
            if trend == "accelerating":
                trajectory_score += 15
            elif trend == "declining":
                trajectory_score -= 15

            trajectory_score = max(0, min(100, trajectory_score))

            return GrowthTrajectory(
                trajectory_score=round(trajectory_score, 1),
                trend=trend,
                velocity=round(velocity, 2),
                consistency=round(consistency, 2),
                predicted_6mo_score=round(predicted_6mo, 1),
                predicted_12mo_score=round(predicted_12mo, 1),
                key_growth_areas=key_growth,
                stagnant_areas=stagnant
            )

        except Exception as e:
            logger.warning(f"Error analyzing growth trajectory: {e}")
            return None

    # ==========================================================================
    # COMPETITIVE POSITIONING
    # ==========================================================================

    def _identify_competitive_advantages(
        self,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore,
        percentile: Optional[float]
    ) -> list[str]:
        """Identify candidate's competitive advantages."""
        advantages = []

        # High performers in each area
        if github.available and github.score >= 85:
            advantages.append("Exceptional GitHub portfolio")
        if interview.available and interview.score >= 85:
            advantages.append("Outstanding interview performance")
        if transcript.available and transcript.score >= 85:
            advantages.append("Top-tier academic record")

        # Specific sub-dimension strengths
        if github.available:
            if github.breakdown.get("originality", 0) >= 90:
                advantages.append("Highly original code")
            if github.breakdown.get("depth", 0) >= 90:
                advantages.append("Deep technical projects")
            if github.breakdown.get("collaboration", 0) >= 90:
                advantages.append("Strong OSS collaboration")

        if transcript.available:
            if transcript.breakdown.get("course_rigor", 0) >= 90:
                advantages.append("Extremely rigorous coursework")
            if transcript.breakdown.get("trajectory", 0) >= 85:
                advantages.append("Strong upward grade trajectory")

        # Overall positioning
        if percentile and percentile >= 95:
            advantages.insert(0, "Top 5% of all candidates")
        elif percentile and percentile >= 90:
            advantages.insert(0, "Top 10% performer")

        # Unique combinations
        if (github.available and github.score >= 75 and
            interview.available and interview.score >= 75 and
            transcript.available and transcript.score >= 75):
            advantages.append("Well-rounded profile across all dimensions")

        return advantages[:5]

    # ==========================================================================
    # ML FEATURE EXTRACTION
    # ==========================================================================

    def _extract_ml_features(
        self,
        candidate: Candidate,
        interview: ComponentScore,
        github: ComponentScore,
        transcript: ComponentScore,
        resume: ComponentScore,
        overall_score: float,
        role_type: Optional[str],
        vertical: Optional[str]
    ) -> dict:
        """Extract features for ML model training."""
        features = {
            # Target
            "overall_score": overall_score,

            # Component scores
            "interview_score": interview.score if interview.available else None,
            "interview_confidence": interview.confidence if interview.available else None,
            "github_score": github.score if github.available else None,
            "github_confidence": github.confidence if github.available else None,
            "transcript_score": transcript.score if transcript.available else None,
            "transcript_confidence": transcript.confidence if transcript.available else None,
            "resume_score": resume.score if resume.available else None,
            "resume_confidence": resume.confidence if resume.available else None,

            # Sub-scores from GitHub
            "github_originality": github.breakdown.get("originality") if github.available else None,
            "github_activity": github.breakdown.get("activity") if github.available else None,
            "github_depth": github.breakdown.get("depth") if github.available else None,
            "github_collaboration": github.breakdown.get("collaboration") if github.available else None,
            "github_total_repos": github.breakdown.get("total_repos") if github.available else None,
            "github_total_commits": github.breakdown.get("total_commits") if github.available else None,

            # Sub-scores from transcript
            "transcript_rigor": transcript.breakdown.get("course_rigor") if transcript.available else None,
            "transcript_performance": transcript.breakdown.get("performance") if transcript.available else None,
            "transcript_trajectory": transcript.breakdown.get("trajectory") if transcript.available else None,
            "transcript_gpa": transcript.breakdown.get("gpa") if transcript.available else None,
            "transcript_technical_gpa": transcript.breakdown.get("technical_gpa") if transcript.available else None,

            # Resume features
            "resume_experience_count": resume.breakdown.get("experience_count") if resume.available else None,
            "resume_skills_count": resume.breakdown.get("skills_count") if resume.available else None,
            "resume_projects_count": resume.breakdown.get("projects_count") if resume.available else None,

            # Data availability
            "has_interview": interview.available,
            "has_github": github.available,
            "has_transcript": transcript.available,
            "has_resume": resume.available,
            "data_completeness": sum([interview.available, github.available, transcript.available, resume.available]) / 4,

            # Context
            "role_type": role_type,
            "vertical": vertical,
            "university": candidate.university,
            "graduation_year": candidate.graduation_year,
            "major": candidate.major,

            # Computed features
            "score_variance": None,
            "max_component_score": None,
            "min_component_score": None,
        }

        # Calculate computed features
        available_scores = [
            s for s in [
                interview.score if interview.available else None,
                github.score if github.available else None,
                transcript.score if transcript.available else None,
                resume.score if resume.available else None
            ] if s is not None
        ]

        if available_scores:
            features["max_component_score"] = max(available_scores)
            features["min_component_score"] = min(available_scores)
            if len(available_scores) >= 2:
                features["score_variance"] = statistics.variance(available_scores)

        return features

    # ==========================================================================
    # ML DATA STORAGE
    # ==========================================================================

    def _store_for_ml_training(
        self,
        candidate: Candidate,
        score: 'UnifiedCandidateScore',
        db: Session,
        role_type: Optional[str],
        vertical: Optional[str]
    ):
        """Store scoring result for ML training pipeline."""
        try:
            # Import ML data pipeline
            from .ml_data_pipeline import ml_data_pipeline

            # Store unified score
            ml_data_pipeline.store_unified_score(
                db=db,
                candidate_id=str(candidate.id),
                overall_score=score.overall_score,
                interview_score=score.interview.score if score.interview.available else None,
                github_score=score.github.score if score.github.available else None,
                transcript_score=score.transcript.score if score.transcript.available else None,
                resume_score=score.resume.score if score.resume.available else None,
                role_type=role_type,
                vertical=vertical,
                confidence=score.confidence,
                feature_vector=score.ml_features,
                scoring_version=score.scoring_version
            )

            # Log scoring event
            ml_data_pipeline.log_scoring_event(
                db=db,
                candidate_id=str(candidate.id),
                event_type=ScoringEventType.UNIFIED_SCORE,
                input_data={
                    "role_type": role_type,
                    "vertical": vertical,
                    "data_completeness": score.data_completeness
                },
                output_data={
                    "overall_score": score.overall_score,
                    "grade": score.overall_grade,
                    "confidence": score.confidence
                },
                model_version=score.scoring_version,
                confidence=score.confidence
            )

        except Exception as e:
            logger.warning(f"Error storing ML training data: {e}")

    # ==========================================================================
    # BATCH SCORING
    # ==========================================================================

    def batch_score_candidates(
        self,
        candidate_ids: list[str],
        db: Session,
        role_type: Optional[str] = None,
        vertical: Optional[str] = None
    ) -> dict[str, UnifiedCandidateScore]:
        """Score multiple candidates efficiently."""
        results = {}

        for candidate_id in candidate_ids:
            try:
                candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
                if candidate:
                    results[candidate_id] = self.calculate_unified_score(
                        candidate, db, role_type, vertical,
                        include_percentiles=False,  # Calculate at end for efficiency
                        store_for_ml=False  # Batch store after
                    )
            except Exception as e:
                logger.error(f"Error scoring candidate {candidate_id}: {e}")
                continue

        # Calculate percentiles for batch
        if results:
            scores = [r.overall_score for r in results.values()]
            for cid, result in results.items():
                below = sum(1 for s in scores if s < result.overall_score)
                result.percentile = round((below / len(scores)) * 100, 1)

        return results

    # ==========================================================================
    # SCORING COMPARISON
    # ==========================================================================

    def compare_candidates(
        self,
        candidate_ids: list[str],
        db: Session,
        role_type: Optional[str] = None
    ) -> dict:
        """Compare multiple candidates for a role."""
        scores = self.batch_score_candidates(candidate_ids, db, role_type)

        if not scores:
            return {"error": "No candidates could be scored"}

        # Rank candidates
        ranked = sorted(
            [(cid, score) for cid, score in scores.items()],
            key=lambda x: x[1].overall_score,
            reverse=True
        )

        # Build comparison matrix
        comparison = {
            "ranking": [
                {
                    "rank": i + 1,
                    "candidate_id": cid,
                    "overall_score": score.overall_score,
                    "grade": score.overall_grade,
                    "recommendation": score.hiring_recommendation.overall_recommendation if score.hiring_recommendation else None,
                    "top_strength": score.top_strengths[0] if score.top_strengths else None,
                    "key_concern": score.key_concerns[0] if score.key_concerns else None
                }
                for i, (cid, score) in enumerate(ranked)
            ],
            "dimension_leaders": {
                "interview": max(ranked, key=lambda x: x[1].interview.score if x[1].interview.available else 0)[0],
                "github": max(ranked, key=lambda x: x[1].github.score if x[1].github.available else 0)[0],
                "transcript": max(ranked, key=lambda x: x[1].transcript.score if x[1].transcript.available else 0)[0],
                "resume": max(ranked, key=lambda x: x[1].resume.score if x[1].resume.available else 0)[0]
            },
            "score_spread": {
                "highest": ranked[0][1].overall_score if ranked else 0,
                "lowest": ranked[-1][1].overall_score if ranked else 0,
                "average": statistics.mean([s.overall_score for _, s in ranked]) if ranked else 0
            },
            "full_scores": scores
        }

        return comparison


# Global instance
candidate_scoring_service = CandidateScoringService()

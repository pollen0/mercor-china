"""
ML Data Pipeline Service

Captures all scoring events for model training and provides utilities for:
1. Logging scoring events with full context
2. Requesting human labels for training data
3. Recording hiring outcomes for calibration
4. Exporting training datasets
5. Managing experiments and A/B tests

Usage:
    from app.services.ml_data_pipeline import ml_pipeline

    # Log a scoring event
    await ml_pipeline.log_scoring_event(
        event_type=ScoringEventType.INTERVIEW_RESPONSE,
        candidate_id="...",
        input_data={"question": "...", "transcript": "..."},
        scores={"communication": 8.5, ...},
        overall_score=8.2,
        model_used="claude-sonnet-4-5-20250929",
        algorithm_version="2.1.0"
    )

    # Record an outcome
    await ml_pipeline.record_outcome(
        candidate_id="...",
        outcome_type=OutcomeType.HIRED,
        employer_id="...",
        company_tier=CompanyTier.TIER_1
    )
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.ml_scoring import (
    ScoringEventType, LabelSource, OutcomeType, OutcomeStage, CompanyTier,
    ExperimentStatus, ScoringEvent, ScoringLabel, LabelingTask, CandidateOutcome,
    InterviewTranscriptML, GitHubAnalysisML, ResumeAnalysisML, TranscriptAnalysisML,
    UnifiedCandidateScore, MLExperiment, MLTrainingRun, ScoreCalibration
)


class MLDataPipeline:
    """
    Central service for ML data collection and management.
    All scoring operations should flow through this service.
    """

    # Current algorithm versions
    INTERVIEW_ALGORITHM_VERSION = "2.1.0"
    RESUME_ALGORITHM_VERSION = "1.0.0"
    GITHUB_ALGORITHM_VERSION = "1.0.0"
    TRANSCRIPT_ALGORITHM_VERSION = "1.0.0"
    UNIFIED_ALGORITHM_VERSION = "1.0.0"

    def __init__(self):
        self._active_experiments: Dict[str, MLExperiment] = {}

    # ==========================================
    # SCORING EVENT LOGGING
    # ==========================================

    async def log_scoring_event(
        self,
        db: AsyncSession,
        event_type: ScoringEventType,
        input_data: Dict[str, Any],
        scores: Dict[str, float],
        overall_score: Optional[float] = None,
        model_used: Optional[str] = None,
        algorithm_version: Optional[str] = None,
        candidate_id: Optional[str] = None,
        session_id: Optional[str] = None,
        response_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
        analysis_text: Optional[str] = None,
        strengths: Optional[List[str]] = None,
        concerns: Optional[List[str]] = None,
        highlights: Optional[List[str]] = None,
        processing_time_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        api_cost_usd: Optional[float] = None,
        confidence: Optional[float] = None,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        had_error: bool = False,
        error_message: Optional[str] = None,
    ) -> ScoringEvent:
        """
        Log a scoring event for future training.

        This should be called after every scoring operation.
        """
        # Generate input hash for deduplication
        input_json = json.dumps(input_data, sort_keys=True)
        input_hash = hashlib.sha256(input_json.encode()).hexdigest()

        # Determine algorithm version
        if algorithm_version is None:
            algorithm_version = self._get_default_version(event_type)

        # Check for active experiments
        experiment_id = None
        variant = None
        active_exp = await self._get_active_experiment(db, event_type, vertical, role_type)
        if active_exp:
            experiment_id = active_exp.id
            variant = self._assign_variant(active_exp, candidate_id)

        event = ScoringEvent(
            id=str(uuid.uuid4()),
            event_type=event_type,
            candidate_id=candidate_id,
            session_id=session_id,
            response_id=response_id,
            input_data=input_data,
            input_hash=input_hash,
            input_tokens=input_tokens,
            context_data=context_data,
            algorithm_version=algorithm_version,
            model_used=model_used,
            prompt_version=None,  # TODO: Track prompt versions
            raw_scores=scores,
            overall_score=overall_score,
            confidence=confidence,
            analysis_text=analysis_text,
            strengths=strengths,
            concerns=concerns,
            highlights=highlights,
            processing_time_ms=processing_time_ms,
            output_tokens=output_tokens,
            api_cost_usd=api_cost_usd,
            had_error=had_error,
            error_message=error_message,
            vertical=vertical,
            role_type=role_type,
            experiment_id=experiment_id,
            variant=variant,
        )

        db.add(event)
        await db.commit()
        await db.refresh(event)

        # Check if this should be queued for labeling
        await self._maybe_queue_for_labeling(db, event)

        return event

    async def log_interview_response(
        self,
        db: AsyncSession,
        candidate_id: str,
        session_id: str,
        response_id: str,
        question_text: str,
        transcript: str,
        scores: Dict[str, float],
        overall_score: float,
        analysis: str,
        model_used: str,
        vertical: str,
        role_type: str,
        processing_time_ms: int,
        **kwargs
    ) -> ScoringEvent:
        """Convenience method for logging interview response scores."""
        return await self.log_scoring_event(
            db=db,
            event_type=ScoringEventType.INTERVIEW_RESPONSE,
            candidate_id=candidate_id,
            session_id=session_id,
            response_id=response_id,
            input_data={
                "question_text": question_text,
                "transcript": transcript,
            },
            scores=scores,
            overall_score=overall_score,
            analysis_text=analysis,
            model_used=model_used,
            vertical=vertical,
            role_type=role_type,
            processing_time_ms=processing_time_ms,
            **kwargs
        )

    async def log_resume_score(
        self,
        db: AsyncSession,
        candidate_id: str,
        resume_text: str,
        parsed_data: Dict[str, Any],
        scores: Dict[str, float],
        overall_score: float,
        role_fit_scores: Dict[str, float],
        model_used: str,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        **kwargs
    ) -> ScoringEvent:
        """Convenience method for logging resume scores."""
        return await self.log_scoring_event(
            db=db,
            event_type=ScoringEventType.RESUME,
            candidate_id=candidate_id,
            input_data={
                "resume_text": resume_text,
                "parsed_data": parsed_data,
            },
            context_data={
                "role_fit_scores": role_fit_scores,
            },
            scores=scores,
            overall_score=overall_score,
            model_used=model_used,
            vertical=vertical,
            role_type=role_type,
            **kwargs
        )

    async def log_github_score(
        self,
        db: AsyncSession,
        candidate_id: str,
        github_username: str,
        profile_data: Dict[str, Any],
        repos_analyzed: List[Dict[str, Any]],
        scores: Dict[str, float],
        overall_score: float,
        authenticity_analysis: Dict[str, Any],
        **kwargs
    ) -> ScoringEvent:
        """Convenience method for logging GitHub scores."""
        return await self.log_scoring_event(
            db=db,
            event_type=ScoringEventType.GITHUB_PROFILE,
            candidate_id=candidate_id,
            input_data={
                "github_username": github_username,
                "profile_data": profile_data,
                "repos_analyzed": repos_analyzed,
            },
            context_data={
                "authenticity_analysis": authenticity_analysis,
            },
            scores=scores,
            overall_score=overall_score,
            **kwargs
        )

    async def log_transcript_score(
        self,
        db: AsyncSession,
        candidate_id: str,
        university: str,
        courses: List[Dict[str, Any]],
        scores: Dict[str, float],
        overall_score: float,
        comparative_metrics: Dict[str, Any],
        **kwargs
    ) -> ScoringEvent:
        """Convenience method for logging transcript scores."""
        return await self.log_scoring_event(
            db=db,
            event_type=ScoringEventType.TRANSCRIPT,
            candidate_id=candidate_id,
            input_data={
                "university": university,
                "courses": courses,
            },
            context_data={
                "comparative_metrics": comparative_metrics,
            },
            scores=scores,
            overall_score=overall_score,
            **kwargs
        )

    # ==========================================
    # DETAILED ANALYSIS STORAGE
    # ==========================================

    async def store_interview_transcript_ml(
        self,
        db: AsyncSession,
        response_id: str,
        candidate_id: str,
        question_text: str,
        response_text: str,
        structure_analysis: Optional[Dict[str, Any]] = None,
        linguistic_features: Optional[Dict[str, Any]] = None,
        audio_features: Optional[Dict[str, Any]] = None,
        key_claims: Optional[List[str]] = None,
        technical_terms: Optional[List[str]] = None,
        named_entities: Optional[List[str]] = None,
        embedding_vector: Optional[List[float]] = None,
        embedding_model: Optional[str] = None,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        duration_seconds: Optional[int] = None,
    ) -> InterviewTranscriptML:
        """Store detailed interview transcript for ML training."""
        transcript = InterviewTranscriptML(
            id=str(uuid.uuid4()),
            response_id=response_id,
            candidate_id=candidate_id,
            question_text=question_text,
            response_text=response_text,
            structure_analysis=structure_analysis,
            linguistic_features=linguistic_features,
            audio_features=audio_features,
            key_claims=key_claims,
            technical_terms=technical_terms,
            named_entities=named_entities,
            embedding_vector=embedding_vector,
            embedding_model=embedding_model,
            word_count=len(response_text.split()) if response_text else 0,
            character_count=len(response_text) if response_text else 0,
            duration_seconds=duration_seconds,
            vertical=vertical,
            role_type=role_type,
        )
        db.add(transcript)
        await db.commit()
        return transcript

    async def store_github_analysis_ml(
        self,
        db: AsyncSession,
        candidate_id: str,
        github_username: str,
        profile_data: Dict[str, Any],
        repos_analyzed: List[Dict[str, Any]],
        contribution_data: Dict[str, Any],
        code_quality_samples: List[Dict[str, Any]],
        language_proficiencies: List[Dict[str, Any]],
        collaboration_data: Dict[str, Any],
        skill_evolution: Dict[str, Any],
        authenticity_analysis: Dict[str, Any],
        scores: Dict[str, float],
        overall_score: float,
    ) -> GitHubAnalysisML:
        """Store detailed GitHub analysis for ML training."""
        analysis = GitHubAnalysisML(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            github_username=github_username,
            profile_data=profile_data,
            repos_analyzed=repos_analyzed,
            contribution_data=contribution_data,
            code_quality_samples=code_quality_samples,
            language_proficiencies=language_proficiencies,
            collaboration_data=collaboration_data,
            skill_evolution=skill_evolution,
            authenticity_analysis=authenticity_analysis,
            overall_score=overall_score,
            originality_score=scores.get("originality"),
            activity_score=scores.get("activity"),
            depth_score=scores.get("depth"),
            collaboration_score=scores.get("collaboration"),
            code_quality_score=scores.get("code_quality"),
            algorithm_version=self.GITHUB_ALGORITHM_VERSION,
        )
        db.add(analysis)
        await db.commit()
        return analysis

    async def store_resume_analysis_ml(
        self,
        db: AsyncSession,
        candidate_id: str,
        raw_text: str,
        parsed_data: Dict[str, Any],
        experience_analysis: List[Dict[str, Any]],
        companies_by_tier: Dict[str, List[str]],
        education_analysis: List[Dict[str, Any]],
        skills_analysis: Dict[str, Any],
        projects_analysis: List[Dict[str, Any]],
        quality_signals: Dict[str, Any],
        red_flags: List[Dict[str, Any]],
        role_fit_scores: Dict[str, Dict[str, Any]],
        scores: Dict[str, float],
        overall_score: float,
        resume_url: Optional[str] = None,
    ) -> ResumeAnalysisML:
        """Store detailed resume analysis for ML training."""
        # Generate resume hash for dedup
        resume_hash = hashlib.sha256(raw_text.encode()).hexdigest() if raw_text else None

        analysis = ResumeAnalysisML(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            resume_url=resume_url,
            resume_hash=resume_hash,
            raw_text=raw_text,
            parsed_data=parsed_data,
            experience_analysis=experience_analysis,
            companies_by_tier=companies_by_tier,
            education_analysis=education_analysis,
            skills_analysis=skills_analysis,
            projects_analysis=projects_analysis,
            quality_signals=quality_signals,
            red_flags=red_flags,
            role_fit_scores=role_fit_scores,
            overall_score=overall_score,
            experience_relevance_score=scores.get("experience_relevance"),
            experience_progression_score=scores.get("experience_progression"),
            skill_depth_score=scores.get("skill_depth"),
            education_quality_score=scores.get("education_quality"),
            project_impact_score=scores.get("project_impact"),
            algorithm_version=self.RESUME_ALGORITHM_VERSION,
        )
        db.add(analysis)
        await db.commit()
        return analysis

    async def store_transcript_analysis_ml(
        self,
        db: AsyncSession,
        candidate_id: str,
        transcript_id: Optional[str],
        university_data: Dict[str, Any],
        course_analysis: List[Dict[str, Any]],
        semester_progression: List[Dict[str, Any]],
        grade_distribution: Dict[str, Any],
        comparative_metrics: Dict[str, Any],
        achievement_patterns: Dict[str, Any],
        risk_patterns: Dict[str, Any],
        program_analysis: Dict[str, Any],
        scores: Dict[str, float],
        overall_score: float,
        adjusted_gpa: Optional[float] = None,
        adjusted_percentile: Optional[float] = None,
    ) -> TranscriptAnalysisML:
        """Store detailed transcript analysis for ML training."""
        analysis = TranscriptAnalysisML(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            transcript_id=transcript_id,
            university_data=university_data,
            course_analysis=course_analysis,
            semester_progression=semester_progression,
            grade_distribution=grade_distribution,
            comparative_metrics=comparative_metrics,
            achievement_patterns=achievement_patterns,
            risk_patterns=risk_patterns,
            program_analysis=program_analysis,
            overall_score=overall_score,
            rigor_score=scores.get("rigor"),
            performance_score=scores.get("performance"),
            trajectory_score=scores.get("trajectory"),
            workload_score=scores.get("workload"),
            achievement_score=scores.get("achievement"),
            adjusted_gpa=adjusted_gpa,
            adjusted_percentile=adjusted_percentile,
            algorithm_version=self.TRANSCRIPT_ALGORITHM_VERSION,
        )
        db.add(analysis)
        await db.commit()
        return analysis

    # ==========================================
    # HUMAN LABELING
    # ==========================================

    async def request_human_label(
        self,
        db: AsyncSession,
        scoring_event_id: str,
        priority: int = 0,
        reason: str = "manual_request",
        min_labels_needed: int = 1,
    ) -> LabelingTask:
        """Queue a scoring event for human labeling."""
        task = LabelingTask(
            id=str(uuid.uuid4()),
            scoring_event_id=scoring_event_id,
            priority=priority,
            reason=reason,
            min_labels_needed=min_labels_needed,
            status="pending",
        )
        db.add(task)
        await db.commit()
        return task

    async def submit_human_label(
        self,
        db: AsyncSession,
        scoring_event_id: str,
        human_scores: Dict[str, float],
        human_overall: Optional[float] = None,
        labeler_id: Optional[str] = None,
        labeler_source: LabelSource = LabelSource.INTERNAL_QA,
        labeler_expertise: Optional[str] = None,
        label_notes: Optional[str] = None,
        disagreement_reasons: Optional[List[str]] = None,
        time_spent_seconds: Optional[int] = None,
        confidence: Optional[str] = None,
        ai_score_seen: bool = False,
    ) -> ScoringLabel:
        """Submit a human label for a scoring event."""
        label = ScoringLabel(
            id=str(uuid.uuid4()),
            scoring_event_id=scoring_event_id,
            labeler_id=labeler_id,
            labeler_source=labeler_source,
            labeler_expertise=labeler_expertise,
            human_scores=human_scores,
            human_overall=human_overall,
            label_notes=label_notes,
            disagreement_reasons=disagreement_reasons,
            time_spent_seconds=time_spent_seconds,
            confidence=confidence,
            ai_score_seen=ai_score_seen,
        )
        db.add(label)

        # Update labeling task if exists
        result = await db.execute(
            select(LabelingTask).where(
                LabelingTask.scoring_event_id == scoring_event_id,
                LabelingTask.status.in_(["pending", "in_progress"])
            )
        )
        task = result.scalar_one_or_none()
        if task:
            task.current_label_count += 1
            if task.current_label_count >= task.min_labels_needed:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
            task.label_id = label.id

        await db.commit()
        return label

    async def get_labeling_queue(
        self,
        db: AsyncSession,
        limit: int = 50,
        labeler_expertise: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get pending labeling tasks with their scoring events."""
        query = select(LabelingTask, ScoringEvent).join(
            ScoringEvent, LabelingTask.scoring_event_id == ScoringEvent.id
        ).where(
            LabelingTask.status == "pending"
        ).order_by(
            LabelingTask.priority.desc(),
            LabelingTask.created_at.asc()
        ).limit(limit)

        result = await db.execute(query)
        tasks = []
        for task, event in result:
            tasks.append({
                "task_id": task.id,
                "event_id": event.id,
                "event_type": event.event_type.value,
                "input_data": event.input_data,
                "ai_scores": event.raw_scores,
                "ai_overall": event.overall_score,
                "analysis": event.analysis_text,
                "vertical": event.vertical,
                "role_type": event.role_type,
                "priority": task.priority,
                "reason": task.reason,
            })
        return tasks

    # ==========================================
    # OUTCOME TRACKING
    # ==========================================

    async def record_outcome(
        self,
        db: AsyncSession,
        candidate_id: str,
        outcome_type: OutcomeType,
        employer_id: Optional[str] = None,
        job_id: Optional[str] = None,
        company_name: Optional[str] = None,
        company_tier: CompanyTier = CompanyTier.UNKNOWN,
        outcome_stage: Optional[OutcomeStage] = None,
        role_title: Optional[str] = None,
        role_level: Optional[str] = None,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        outcome_date: Optional[datetime] = None,
        offer_details: Optional[Dict[str, Any]] = None,
        rejection_reason: Optional[str] = None,
        rejection_feedback: Optional[str] = None,
        employer_rating: Optional[float] = None,
        employer_notes: Optional[str] = None,
    ) -> CandidateOutcome:
        """Record a hiring outcome for calibration."""
        # Get current scores for snapshot
        scores = await self._get_candidate_scores_snapshot(db, candidate_id)

        outcome = CandidateOutcome(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            outcome_type=outcome_type,
            outcome_stage=outcome_stage,
            employer_id=employer_id,
            job_id=job_id,
            company_name=company_name,
            company_tier=company_tier,
            role_title=role_title,
            role_level=role_level,
            vertical=vertical,
            role_type=role_type,
            outcome_date=outcome_date or datetime.utcnow(),
            pathway_score_at_outcome=scores.get("unified"),
            interview_score_at_outcome=scores.get("interview"),
            github_score_at_outcome=scores.get("github"),
            transcript_score_at_outcome=scores.get("transcript"),
            resume_score_at_outcome=scores.get("resume"),
            offer_details=offer_details,
            rejection_reason=rejection_reason,
            rejection_feedback=rejection_feedback,
            employer_rating=employer_rating,
            employer_notes=employer_notes,
        )
        db.add(outcome)
        await db.commit()
        return outcome

    async def _get_candidate_scores_snapshot(
        self,
        db: AsyncSession,
        candidate_id: str
    ) -> Dict[str, float]:
        """Get current scores for a candidate."""
        scores = {}

        # Get latest unified score
        result = await db.execute(
            select(UnifiedCandidateScore).where(
                UnifiedCandidateScore.candidate_id == candidate_id
            ).order_by(
                UnifiedCandidateScore.created_at.desc()
            ).limit(1)
        )
        unified = result.scalar_one_or_none()
        if unified:
            scores["unified"] = unified.overall_score
            scores["interview"] = unified.interview_score
            scores["github"] = unified.github_score
            scores["transcript"] = unified.transcript_score
            scores["resume"] = unified.resume_score

        return scores

    # ==========================================
    # UNIFIED SCORE STORAGE
    # ==========================================

    async def store_unified_score(
        self,
        db: AsyncSession,
        candidate_id: str,
        overall_score: float,
        overall_grade: str,
        interview_score: Optional[float] = None,
        interview_weight: Optional[float] = None,
        interview_confidence: Optional[float] = None,
        github_score: Optional[float] = None,
        github_weight: Optional[float] = None,
        github_confidence: Optional[float] = None,
        transcript_score: Optional[float] = None,
        transcript_weight: Optional[float] = None,
        transcript_confidence: Optional[float] = None,
        resume_score: Optional[float] = None,
        resume_weight: Optional[float] = None,
        resume_confidence: Optional[float] = None,
        overall_confidence: Optional[float] = None,
        data_completeness: Optional[float] = None,
        signals_available: Optional[Dict[str, bool]] = None,
        role_fit_scores: Optional[Dict[str, float]] = None,
        best_fit_roles: Optional[List[str]] = None,
        top_strengths: Optional[List[Dict[str, str]]] = None,
        key_concerns: Optional[List[Dict[str, str]]] = None,
        hiring_recommendation: Optional[str] = None,
        percentile: Optional[float] = None,
        percentile_cohort: Optional[str] = None,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
    ) -> UnifiedCandidateScore:
        """Store a unified candidate score."""
        score = UnifiedCandidateScore(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            vertical=vertical,
            role_type=role_type,
            interview_score=interview_score,
            interview_weight=interview_weight,
            interview_confidence=interview_confidence,
            github_score=github_score,
            github_weight=github_weight,
            github_confidence=github_confidence,
            transcript_score=transcript_score,
            transcript_weight=transcript_weight,
            transcript_confidence=transcript_confidence,
            resume_score=resume_score,
            resume_weight=resume_weight,
            resume_confidence=resume_confidence,
            overall_score=overall_score,
            overall_grade=overall_grade,
            overall_confidence=overall_confidence,
            data_completeness=data_completeness,
            signals_available=signals_available,
            role_fit_scores=role_fit_scores,
            best_fit_roles=best_fit_roles,
            top_strengths=top_strengths,
            key_concerns=key_concerns,
            hiring_recommendation=hiring_recommendation,
            percentile=percentile,
            percentile_cohort=percentile_cohort,
            algorithm_version=self.UNIFIED_ALGORITHM_VERSION,
        )
        db.add(score)
        await db.commit()

        # Also log as scoring event for training
        await self.log_scoring_event(
            db=db,
            event_type=ScoringEventType.UNIFIED_SCORE,
            candidate_id=candidate_id,
            input_data={
                "interview_score": interview_score,
                "github_score": github_score,
                "transcript_score": transcript_score,
                "resume_score": resume_score,
            },
            context_data={
                "weights": {
                    "interview": interview_weight,
                    "github": github_weight,
                    "transcript": transcript_weight,
                    "resume": resume_weight,
                },
                "signals_available": signals_available,
            },
            scores={
                "interview": interview_score or 0,
                "github": github_score or 0,
                "transcript": transcript_score or 0,
                "resume": resume_score or 0,
            },
            overall_score=overall_score,
            confidence=overall_confidence,
            vertical=vertical,
            role_type=role_type,
        )

        return score

    # ==========================================
    # TRAINING DATA EXPORT
    # ==========================================

    async def export_training_dataset(
        self,
        db: AsyncSession,
        event_type: Optional[ScoringEventType] = None,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        min_labels: int = 0,
        include_outcomes: bool = False,
        algorithm_version: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10000,
    ) -> List[Dict[str, Any]]:
        """
        Export training dataset with optional labels and outcomes.

        Returns a list of records with:
        - input_data: The original input
        - ai_scores: AI-generated scores
        - human_scores: Human labels (if available)
        - outcome: Hiring outcome (if available and requested)
        """
        # Build query
        query = select(ScoringEvent)

        conditions = []
        if event_type:
            conditions.append(ScoringEvent.event_type == event_type)
        if vertical:
            conditions.append(ScoringEvent.vertical == vertical)
        if role_type:
            conditions.append(ScoringEvent.role_type == role_type)
        if algorithm_version:
            conditions.append(ScoringEvent.algorithm_version == algorithm_version)
        if start_date:
            conditions.append(ScoringEvent.created_at >= start_date)
        if end_date:
            conditions.append(ScoringEvent.created_at <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(ScoringEvent.created_at.desc()).limit(limit)

        result = await db.execute(query)
        events = result.scalars().all()

        # Build dataset
        dataset = []
        for event in events:
            record = {
                "event_id": event.id,
                "event_type": event.event_type.value,
                "candidate_id": event.candidate_id,
                "created_at": event.created_at.isoformat() if event.created_at else None,
                "input_data": event.input_data,
                "context_data": event.context_data,
                "ai_scores": event.raw_scores,
                "ai_overall": event.overall_score,
                "ai_analysis": event.analysis_text,
                "ai_confidence": event.confidence,
                "model_used": event.model_used,
                "algorithm_version": event.algorithm_version,
                "vertical": event.vertical,
                "role_type": event.role_type,
            }

            # Get human labels
            if min_labels >= 0:
                labels_result = await db.execute(
                    select(ScoringLabel).where(
                        ScoringLabel.scoring_event_id == event.id
                    )
                )
                labels = labels_result.scalars().all()

                if len(labels) >= min_labels:
                    record["human_labels"] = [
                        {
                            "labeler_source": l.labeler_source.value if l.labeler_source else None,
                            "labeler_expertise": l.labeler_expertise,
                            "scores": l.human_scores,
                            "overall": l.human_overall,
                            "notes": l.label_notes,
                            "disagreement_reasons": l.disagreement_reasons,
                            "confidence": l.confidence,
                        }
                        for l in labels
                    ]

                    # Calculate average human score
                    if labels:
                        all_overall = [l.human_overall for l in labels if l.human_overall is not None]
                        if all_overall:
                            record["human_avg_overall"] = sum(all_overall) / len(all_overall)

            # Get outcome if requested
            if include_outcomes and event.candidate_id:
                outcome_result = await db.execute(
                    select(CandidateOutcome).where(
                        CandidateOutcome.candidate_id == event.candidate_id
                    ).order_by(
                        CandidateOutcome.outcome_date.desc()
                    ).limit(1)
                )
                outcome = outcome_result.scalar_one_or_none()
                if outcome:
                    record["outcome"] = {
                        "type": outcome.outcome_type.value if outcome.outcome_type else None,
                        "stage": outcome.outcome_stage.value if outcome.outcome_stage else None,
                        "company_tier": outcome.company_tier.value if outcome.company_tier else None,
                        "role_level": outcome.role_level,
                        "employer_rating": outcome.employer_rating,
                    }

            dataset.append(record)

        return dataset

    async def get_calibration_data(
        self,
        db: AsyncSession,
        vertical: Optional[str] = None,
        role_type: Optional[str] = None,
        company_tier: Optional[CompanyTier] = None,
        min_samples: int = 10,
    ) -> Dict[str, Any]:
        """
        Get calibration data mapping scores to outcomes.

        Returns score ranges and their corresponding hire rates.
        """
        # Build query for outcomes with scores
        query = select(CandidateOutcome).where(
            CandidateOutcome.pathway_score_at_outcome.isnot(None),
            CandidateOutcome.outcome_type.in_([
                OutcomeType.HIRED,
                OutcomeType.REJECTED_TECHNICAL,
                OutcomeType.REJECTED_CULTURAL,
                OutcomeType.REJECTED_EXPERIENCE,
                OutcomeType.REJECTED_OTHER,
            ])
        )

        if vertical:
            query = query.where(CandidateOutcome.vertical == vertical)
        if role_type:
            query = query.where(CandidateOutcome.role_type == role_type)
        if company_tier:
            query = query.where(CandidateOutcome.company_tier == company_tier)

        result = await db.execute(query)
        outcomes = result.scalars().all()

        if len(outcomes) < min_samples:
            return {"error": "Insufficient data", "sample_count": len(outcomes)}

        # Group by score ranges
        score_buckets = {}
        bucket_size = 0.5  # 0.5 point buckets

        for outcome in outcomes:
            score = outcome.pathway_score_at_outcome
            bucket = round(score / bucket_size) * bucket_size

            if bucket not in score_buckets:
                score_buckets[bucket] = {"hired": 0, "rejected": 0, "total": 0}

            score_buckets[bucket]["total"] += 1
            if outcome.outcome_type == OutcomeType.HIRED:
                score_buckets[bucket]["hired"] += 1
            else:
                score_buckets[bucket]["rejected"] += 1

        # Calculate hire rates
        calibration = []
        for score, counts in sorted(score_buckets.items()):
            if counts["total"] >= 5:  # Minimum samples per bucket
                calibration.append({
                    "score_center": score,
                    "score_min": score - bucket_size / 2,
                    "score_max": score + bucket_size / 2,
                    "sample_size": counts["total"],
                    "hire_count": counts["hired"],
                    "hire_rate": counts["hired"] / counts["total"],
                })

        return {
            "total_samples": len(outcomes),
            "vertical": vertical,
            "role_type": role_type,
            "company_tier": company_tier.value if company_tier else None,
            "calibration_data": calibration,
        }

    # ==========================================
    # EXPERIMENTS
    # ==========================================

    async def create_experiment(
        self,
        db: AsyncSession,
        name: str,
        experiment_type: str,
        control_config: Dict[str, Any],
        treatment_configs: List[Dict[str, Any]],
        description: Optional[str] = None,
        hypothesis: Optional[str] = None,
        target_component: Optional[str] = None,
        target_verticals: Optional[List[str]] = None,
        target_roles: Optional[List[str]] = None,
        traffic_allocation: Optional[Dict[str, float]] = None,
    ) -> MLExperiment:
        """Create a new A/B test experiment."""
        experiment = MLExperiment(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            hypothesis=hypothesis,
            experiment_type=experiment_type,
            target_component=target_component,
            control_config=control_config,
            treatment_configs=treatment_configs,
            target_verticals=target_verticals,
            target_roles=target_roles,
            traffic_allocation=traffic_allocation or {"control": 0.5},
            status=ExperimentStatus.DRAFT,
        )
        db.add(experiment)
        await db.commit()
        return experiment

    async def start_experiment(
        self,
        db: AsyncSession,
        experiment_id: str
    ) -> MLExperiment:
        """Start an experiment."""
        result = await db.execute(
            select(MLExperiment).where(MLExperiment.id == experiment_id)
        )
        experiment = result.scalar_one_or_none()
        if experiment:
            experiment.status = ExperimentStatus.RUNNING
            experiment.started_at = datetime.utcnow()
            await db.commit()
        return experiment

    async def end_experiment(
        self,
        db: AsyncSession,
        experiment_id: str,
        winner: Optional[str] = None,
        decision_notes: Optional[str] = None,
    ) -> MLExperiment:
        """End an experiment and record results."""
        result = await db.execute(
            select(MLExperiment).where(MLExperiment.id == experiment_id)
        )
        experiment = result.scalar_one_or_none()
        if experiment:
            experiment.status = ExperimentStatus.COMPLETED
            experiment.ended_at = datetime.utcnow()
            experiment.winner = winner
            experiment.decision_notes = decision_notes

            # Calculate results
            experiment.results = await self._calculate_experiment_results(
                db, experiment_id
            )
            experiment.sample_size = sum(
                r.get("sample_size", 0)
                for r in (experiment.results or {}).values()
            )

            await db.commit()
        return experiment

    async def _calculate_experiment_results(
        self,
        db: AsyncSession,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Calculate results for an experiment."""
        result = await db.execute(
            select(
                ScoringEvent.variant,
                func.count(ScoringEvent.id).label("count"),
                func.avg(ScoringEvent.overall_score).label("avg_score"),
                func.stddev(ScoringEvent.overall_score).label("stddev_score"),
            ).where(
                ScoringEvent.experiment_id == experiment_id
            ).group_by(
                ScoringEvent.variant
            )
        )

        results = {}
        for row in result:
            results[row.variant or "unknown"] = {
                "sample_size": row.count,
                "avg_score": float(row.avg_score) if row.avg_score else None,
                "stddev_score": float(row.stddev_score) if row.stddev_score else None,
            }

        return results

    # ==========================================
    # INTERNAL HELPERS
    # ==========================================

    def _get_default_version(self, event_type: ScoringEventType) -> str:
        """Get default algorithm version for event type."""
        versions = {
            ScoringEventType.INTERVIEW_RESPONSE: self.INTERVIEW_ALGORITHM_VERSION,
            ScoringEventType.INTERVIEW_SESSION: self.INTERVIEW_ALGORITHM_VERSION,
            ScoringEventType.RESUME: self.RESUME_ALGORITHM_VERSION,
            ScoringEventType.GITHUB_PROFILE: self.GITHUB_ALGORITHM_VERSION,
            ScoringEventType.GITHUB_REPO: self.GITHUB_ALGORITHM_VERSION,
            ScoringEventType.TRANSCRIPT: self.TRANSCRIPT_ALGORITHM_VERSION,
            ScoringEventType.UNIFIED_SCORE: self.UNIFIED_ALGORITHM_VERSION,
            ScoringEventType.CODING_CHALLENGE: self.INTERVIEW_ALGORITHM_VERSION,
        }
        return versions.get(event_type, "1.0.0")

    async def _get_active_experiment(
        self,
        db: AsyncSession,
        event_type: ScoringEventType,
        vertical: Optional[str],
        role_type: Optional[str],
    ) -> Optional[MLExperiment]:
        """Get active experiment for this scoring context."""
        # Map event type to component
        component = event_type.value.split("_")[0]  # e.g., "interview" from "interview_response"

        query = select(MLExperiment).where(
            MLExperiment.status == ExperimentStatus.RUNNING,
            or_(
                MLExperiment.target_component == component,
                MLExperiment.target_component.is_(None)
            )
        )

        result = await db.execute(query)
        experiments = result.scalars().all()

        for exp in experiments:
            # Check vertical targeting
            if exp.target_verticals and vertical not in exp.target_verticals:
                continue
            # Check role targeting
            if exp.target_roles and role_type not in exp.target_roles:
                continue
            return exp

        return None

    def _assign_variant(
        self,
        experiment: MLExperiment,
        candidate_id: Optional[str]
    ) -> str:
        """Assign a variant based on traffic allocation."""
        # Use candidate_id for consistent assignment
        if candidate_id:
            hash_val = int(hashlib.md5(candidate_id.encode()).hexdigest(), 16)
        else:
            hash_val = int(hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(), 16)

        # Convert to 0-1 range
        ratio = (hash_val % 1000) / 1000

        # Assign based on traffic allocation
        allocation = experiment.traffic_allocation or {"control": 1.0}
        cumulative = 0
        for variant, weight in allocation.items():
            cumulative += weight
            if ratio < cumulative:
                return variant

        return "control"

    async def _maybe_queue_for_labeling(
        self,
        db: AsyncSession,
        event: ScoringEvent
    ) -> None:
        """
        Determine if this event should be queued for human labeling.

        Queue if:
        - Score is borderline (4.5-5.5 range)
        - Confidence is low (<0.7)
        - Random sampling (1% of events)
        - Error occurred
        """
        should_queue = False
        reason = None
        priority = 0

        # Check borderline scores
        if event.overall_score and 4.5 <= event.overall_score <= 5.5:
            should_queue = True
            reason = "borderline_score"
            priority = 1

        # Check low confidence
        if event.confidence and event.confidence < 0.7:
            should_queue = True
            reason = "low_confidence"
            priority = 2

        # Check errors
        if event.had_error:
            should_queue = True
            reason = "scoring_error"
            priority = 3

        # Random sampling (1%)
        if not should_queue:
            hash_val = int(hashlib.md5(event.id.encode()).hexdigest(), 16)
            if (hash_val % 100) < 1:
                should_queue = True
                reason = "random_sample"
                priority = 0

        if should_queue:
            await self.request_human_label(
                db, event.id, priority=priority, reason=reason
            )


# Singleton instance
ml_pipeline = MLDataPipeline()

"""Create ML scoring infrastructure tables

Revision ID: 033
Revises: 032
Create Date: 2026-02-05

Creates the ML scoring and training data tables for future model fine-tuning:
- scoring_events: Every AI scoring event for training data
- scoring_labels: Human labels for ground truth
- labeling_tasks: Queue for human labeling workflow
- candidate_outcomes: Real-world hiring outcomes for calibration
- interview_transcripts_ml: ML-ready transcript features
- github_analysis_ml: Detailed GitHub analysis
- resume_analysis_ml: Detailed resume analysis
- transcript_analysis_ml: Academic transcript analysis
- unified_candidate_scores: Combined multi-signal scores
- ml_experiments: A/B testing for scoring algorithms
- ml_training_runs: Model training tracking
- score_calibrations: Score-to-outcome calibration data
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = '033'
down_revision: Union[str, None] = '032'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def enum_exists(enum_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
    ), {"name": enum_name})
    return result.scalar()


def upgrade() -> None:
    # ================================================
    # Create all enum types first
    # ================================================
    enums_to_create = {
        'scoringeventtype': [
            'interview_response', 'interview_session', 'resume',
            'github_profile', 'github_repo', 'transcript',
            'unified_score', 'coding_challenge'
        ],
        'labelsource': [
            'internal_qa', 'employer', 'expert', 'candidate_self', 'crowdsource'
        ],
        'outcometype': [
            'hired', 'offer_extended', 'offer_declined',
            'rejected_technical', 'rejected_cultural', 'rejected_experience',
            'rejected_other', 'ghosted', 'still_interviewing', 'withdrew'
        ],
        'outcomestage': [
            'resume_screen', 'phone_screen', 'technical_interview',
            'onsite', 'final_round', 'offer', 'unknown'
        ],
        'companytier': [
            'faang', 'tier_1', 'unicorn', 'series_b_c', 'series_a', 'smb', 'unknown'
        ],
        'experimentstatus': [
            'draft', 'running', 'completed', 'aborted'
        ],
    }

    for enum_name, values in enums_to_create.items():
        if not enum_exists(enum_name):
            ENUM(*values, name=enum_name, create_type=True).create(
                op.get_bind(), checkfirst=True
            )

    # Helper to reference enums without creating
    def ref_enum(name, values):
        return ENUM(*values, name=name, create_type=False)

    # ================================================
    # 1. ml_experiments (needed first - referenced by scoring_events)
    # ================================================
    if not table_exists('ml_experiments'):
        op.create_table(
            'ml_experiments',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('hypothesis', sa.Text(), nullable=True),
            sa.Column('experiment_type', sa.String(50), nullable=False),
            sa.Column('target_component', sa.String(50), nullable=True),
            sa.Column('control_config', JSONB(), nullable=False),
            sa.Column('treatment_configs', JSONB(), nullable=False),
            sa.Column('traffic_allocation', JSONB(), nullable=True),
            sa.Column('target_verticals', ARRAY(sa.String()), nullable=True),
            sa.Column('target_roles', ARRAY(sa.String()), nullable=True),
            sa.Column('status', ref_enum('experimentstatus', ['draft', 'running', 'completed', 'aborted']),
                       server_default='draft'),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('sample_size', sa.Integer(), server_default='0'),
            sa.Column('results', JSONB(), nullable=True),
            sa.Column('statistical_analysis', JSONB(), nullable=True),
            sa.Column('winner', sa.String(50), nullable=True),
            sa.Column('decision_notes', sa.Text(), nullable=True),
            sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_experiments_status', 'ml_experiments', ['status'])
        op.create_index('ix_experiments_type', 'ml_experiments', ['experiment_type'])

    # ================================================
    # 2. scoring_events
    # ================================================
    if not table_exists('scoring_events'):
        op.create_table(
            'scoring_events',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('event_type', ref_enum('scoringeventtype', [
                'interview_response', 'interview_session', 'resume',
                'github_profile', 'github_repo', 'transcript',
                'unified_score', 'coding_challenge'
            ]), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=True),
            sa.Column('session_id', sa.String(), nullable=True),
            sa.Column('response_id', sa.String(), nullable=True),
            sa.Column('input_data', JSONB(), nullable=False),
            sa.Column('input_hash', sa.String(64), nullable=True),
            sa.Column('input_tokens', sa.Integer(), nullable=True),
            sa.Column('context_data', JSONB(), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=False),
            sa.Column('model_used', sa.String(100), nullable=True),
            sa.Column('prompt_version', sa.String(20), nullable=True),
            sa.Column('raw_scores', JSONB(), nullable=False),
            sa.Column('overall_score', sa.Float(), nullable=True),
            sa.Column('confidence', sa.Float(), nullable=True),
            sa.Column('analysis_text', sa.Text(), nullable=True),
            sa.Column('strengths', JSONB(), nullable=True),
            sa.Column('concerns', JSONB(), nullable=True),
            sa.Column('highlights', JSONB(), nullable=True),
            sa.Column('processing_time_ms', sa.Integer(), nullable=True),
            sa.Column('output_tokens', sa.Integer(), nullable=True),
            sa.Column('api_cost_usd', sa.Float(), nullable=True),
            sa.Column('had_error', sa.Boolean(), server_default='false'),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('retry_count', sa.Integer(), server_default='0'),
            sa.Column('vertical', sa.String(50), nullable=True),
            sa.Column('role_type', sa.String(50), nullable=True),
            sa.Column('experiment_id', sa.String(), nullable=True),
            sa.Column('variant', sa.String(50), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['response_id'], ['interview_responses.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['experiment_id'], ['ml_experiments.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_scoring_events_event_type', 'scoring_events', ['event_type'])
        op.create_index('ix_scoring_events_algorithm_version', 'scoring_events', ['algorithm_version'])
        op.create_index('ix_scoring_events_overall_score', 'scoring_events', ['overall_score'])
        op.create_index('ix_scoring_events_input_hash', 'scoring_events', ['input_hash'])
        op.create_index('ix_scoring_events_vertical', 'scoring_events', ['vertical'])
        op.create_index('ix_scoring_events_role_type', 'scoring_events', ['role_type'])
        op.create_index('ix_scoring_events_candidate_type', 'scoring_events', ['candidate_id', 'event_type'])
        op.create_index('ix_scoring_events_version_type', 'scoring_events', ['algorithm_version', 'event_type'])
        op.create_index('ix_scoring_events_created', 'scoring_events', ['created_at'])

    # ================================================
    # 3. scoring_labels
    # ================================================
    if not table_exists('scoring_labels'):
        op.create_table(
            'scoring_labels',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('scoring_event_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('labeler_id', sa.String(), nullable=True),
            sa.Column('labeler_source', ref_enum('labelsource', [
                'internal_qa', 'employer', 'expert', 'candidate_self', 'crowdsource'
            ]), nullable=False),
            sa.Column('labeler_expertise', sa.String(100), nullable=True),
            sa.Column('labeler_vertical', sa.String(50), nullable=True),
            sa.Column('human_scores', JSONB(), nullable=False),
            sa.Column('human_overall', sa.Float(), nullable=True),
            sa.Column('label_notes', sa.Text(), nullable=True),
            sa.Column('disagreement_reasons', ARRAY(sa.String()), nullable=True),
            sa.Column('ai_score_seen', sa.Boolean(), server_default='false'),
            sa.Column('corrections', JSONB(), nullable=True),
            sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
            sa.Column('confidence', sa.String(20), nullable=True),
            sa.Column('difficulty', sa.String(20), nullable=True),
            sa.Column('is_validated', sa.Boolean(), server_default='false'),
            sa.Column('validated_by', sa.String(), nullable=True),
            sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['scoring_event_id'], ['scoring_events.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_labels_event', 'scoring_labels', ['scoring_event_id'])
        op.create_index('ix_labels_source', 'scoring_labels', ['labeler_source'])

    # ================================================
    # 4. labeling_tasks
    # ================================================
    if not table_exists('labeling_tasks'):
        op.create_table(
            'labeling_tasks',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('scoring_event_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('priority', sa.Integer(), server_default='0'),
            sa.Column('reason', sa.String(100), nullable=True),
            sa.Column('assigned_to', sa.String(), nullable=True),
            sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('status', sa.String(20), server_default='pending'),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('label_id', sa.String(), nullable=True),
            sa.Column('min_labels_needed', sa.Integer(), server_default='1'),
            sa.Column('current_label_count', sa.Integer(), server_default='0'),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['scoring_event_id'], ['scoring_events.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['label_id'], ['scoring_labels.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_labeling_tasks_status', 'labeling_tasks', ['status', 'priority'])

    # ================================================
    # 5. candidate_outcomes
    # ================================================
    if not table_exists('candidate_outcomes'):
        op.create_table(
            'candidate_outcomes',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('outcome_type', ref_enum('outcometype', [
                'hired', 'offer_extended', 'offer_declined',
                'rejected_technical', 'rejected_cultural', 'rejected_experience',
                'rejected_other', 'ghosted', 'still_interviewing', 'withdrew'
            ]), nullable=False),
            sa.Column('outcome_stage', ref_enum('outcomestage', [
                'resume_screen', 'phone_screen', 'technical_interview',
                'onsite', 'final_round', 'offer', 'unknown'
            ]), nullable=True),
            sa.Column('employer_id', sa.String(), nullable=True),
            sa.Column('job_id', sa.String(), nullable=True),
            sa.Column('company_name', sa.String(), nullable=True),
            sa.Column('company_tier', ref_enum('companytier', [
                'faang', 'tier_1', 'unicorn', 'series_b_c', 'series_a', 'smb', 'unknown'
            ]), server_default='unknown'),
            sa.Column('role_title', sa.String(), nullable=True),
            sa.Column('role_level', sa.String(), nullable=True),
            sa.Column('vertical', sa.String(50), nullable=True),
            sa.Column('role_type', sa.String(50), nullable=True),
            sa.Column('outcome_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('days_from_first_interview', sa.Integer(), nullable=True),
            sa.Column('days_from_application', sa.Integer(), nullable=True),
            # Score snapshots
            sa.Column('pathway_score_at_outcome', sa.Float(), nullable=True),
            sa.Column('interview_score_at_outcome', sa.Float(), nullable=True),
            sa.Column('github_score_at_outcome', sa.Float(), nullable=True),
            sa.Column('transcript_score_at_outcome', sa.Float(), nullable=True),
            sa.Column('resume_score_at_outcome', sa.Float(), nullable=True),
            sa.Column('offer_details', JSONB(), nullable=True),
            sa.Column('rejection_reason', sa.String(100), nullable=True),
            sa.Column('rejection_feedback', sa.Text(), nullable=True),
            sa.Column('employer_rating', sa.Float(), nullable=True),
            sa.Column('employer_notes', sa.Text(), nullable=True),
            sa.Column('would_interview_again', sa.Boolean(), nullable=True),
            sa.Column('is_verified', sa.Boolean(), server_default='false'),
            sa.Column('verification_source', sa.String(50), nullable=True),
            sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_outcomes_candidate', 'candidate_outcomes', ['candidate_id'])
        op.create_index('ix_outcomes_type', 'candidate_outcomes', ['outcome_type'])
        op.create_index('ix_outcomes_company_tier', 'candidate_outcomes', ['company_tier'])

    # ================================================
    # 6. interview_transcripts_ml
    # ================================================
    if not table_exists('interview_transcripts_ml'):
        op.create_table(
            'interview_transcripts_ml',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('response_id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('question_text', sa.Text(), nullable=False),
            sa.Column('question_type', sa.String(50), nullable=True),
            sa.Column('response_text', sa.Text(), nullable=False),
            sa.Column('key_claims', JSONB(), nullable=True),
            sa.Column('technical_terms', JSONB(), nullable=True),
            sa.Column('named_entities', JSONB(), nullable=True),
            sa.Column('structure_analysis', JSONB(), nullable=True),
            sa.Column('linguistic_features', JSONB(), nullable=True),
            sa.Column('audio_features', JSONB(), nullable=True),
            sa.Column('embedding_model', sa.String(100), nullable=True),
            sa.Column('embedding_vector', JSONB(), nullable=True),
            sa.Column('word_count', sa.Integer(), nullable=True),
            sa.Column('character_count', sa.Integer(), nullable=True),
            sa.Column('duration_seconds', sa.Integer(), nullable=True),
            sa.Column('language', sa.String(10), server_default='en'),
            sa.Column('vertical', sa.String(50), nullable=True),
            sa.Column('role_type', sa.String(50), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['response_id'], ['interview_responses.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_transcripts_candidate', 'interview_transcripts_ml', ['candidate_id'])
        op.create_index('ix_transcripts_response', 'interview_transcripts_ml', ['response_id'])

    # ================================================
    # 7. github_analysis_ml
    # ================================================
    if not table_exists('github_analysis_ml'):
        op.create_table(
            'github_analysis_ml',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('github_username', sa.String(100), nullable=False),
            sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('profile_data', JSONB(), nullable=True),
            sa.Column('contribution_data', JSONB(), nullable=True),
            sa.Column('repos_analyzed', JSONB(), nullable=True),
            sa.Column('code_quality_samples', JSONB(), nullable=True),
            sa.Column('language_proficiencies', JSONB(), nullable=True),
            sa.Column('collaboration_data', JSONB(), nullable=True),
            sa.Column('skill_evolution', JSONB(), nullable=True),
            sa.Column('authenticity_analysis', JSONB(), nullable=True),
            # Aggregated scores
            sa.Column('overall_score', sa.Float(), nullable=True),
            sa.Column('originality_score', sa.Float(), nullable=True),
            sa.Column('activity_score', sa.Float(), nullable=True),
            sa.Column('depth_score', sa.Float(), nullable=True),
            sa.Column('collaboration_score', sa.Float(), nullable=True),
            sa.Column('code_quality_score', sa.Float(), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_github_ml_candidate', 'github_analysis_ml', ['candidate_id'])
        op.create_index('ix_github_ml_username', 'github_analysis_ml', ['github_username'])

    # ================================================
    # 8. resume_analysis_ml
    # ================================================
    if not table_exists('resume_analysis_ml'):
        op.create_table(
            'resume_analysis_ml',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('resume_url', sa.String(), nullable=True),
            sa.Column('resume_hash', sa.String(64), nullable=True),
            sa.Column('file_type', sa.String(20), nullable=True),
            sa.Column('raw_text', sa.Text(), nullable=True),
            sa.Column('parsed_data', JSONB(), nullable=True),
            sa.Column('experience_analysis', JSONB(), nullable=True),
            sa.Column('companies_by_tier', JSONB(), nullable=True),
            sa.Column('education_analysis', JSONB(), nullable=True),
            sa.Column('skills_analysis', JSONB(), nullable=True),
            sa.Column('projects_analysis', JSONB(), nullable=True),
            sa.Column('quality_signals', JSONB(), nullable=True),
            sa.Column('red_flags', JSONB(), nullable=True),
            sa.Column('role_fit_scores', JSONB(), nullable=True),
            # Aggregated scores
            sa.Column('overall_score', sa.Float(), nullable=True),
            sa.Column('experience_relevance_score', sa.Float(), nullable=True),
            sa.Column('experience_progression_score', sa.Float(), nullable=True),
            sa.Column('skill_depth_score', sa.Float(), nullable=True),
            sa.Column('education_quality_score', sa.Float(), nullable=True),
            sa.Column('project_impact_score', sa.Float(), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_resume_ml_candidate', 'resume_analysis_ml', ['candidate_id'])

    # ================================================
    # 9. transcript_analysis_ml
    # ================================================
    if not table_exists('transcript_analysis_ml'):
        op.create_table(
            'transcript_analysis_ml',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('transcript_id', sa.String(), nullable=True),
            sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('university_data', JSONB(), nullable=True),
            sa.Column('course_analysis', JSONB(), nullable=True),
            sa.Column('semester_progression', JSONB(), nullable=True),
            sa.Column('grade_distribution', JSONB(), nullable=True),
            sa.Column('comparative_metrics', JSONB(), nullable=True),
            sa.Column('achievement_patterns', JSONB(), nullable=True),
            sa.Column('risk_patterns', JSONB(), nullable=True),
            sa.Column('program_analysis', JSONB(), nullable=True),
            # Aggregated scores
            sa.Column('overall_score', sa.Float(), nullable=True),
            sa.Column('rigor_score', sa.Float(), nullable=True),
            sa.Column('performance_score', sa.Float(), nullable=True),
            sa.Column('trajectory_score', sa.Float(), nullable=True),
            sa.Column('workload_score', sa.Float(), nullable=True),
            sa.Column('achievement_score', sa.Float(), nullable=True),
            sa.Column('adjusted_gpa', sa.Float(), nullable=True),
            sa.Column('adjusted_percentile', sa.Float(), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['transcript_id'], ['candidate_transcripts.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_transcript_ml_candidate', 'transcript_analysis_ml', ['candidate_id'])

    # ================================================
    # 10. unified_candidate_scores
    # ================================================
    if not table_exists('unified_candidate_scores'):
        op.create_table(
            'unified_candidate_scores',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('vertical', sa.String(50), nullable=True),
            sa.Column('role_type', sa.String(50), nullable=True),
            # Component scores
            sa.Column('interview_score', sa.Float(), nullable=True),
            sa.Column('interview_weight', sa.Float(), nullable=True),
            sa.Column('interview_confidence', sa.Float(), nullable=True),
            sa.Column('github_score', sa.Float(), nullable=True),
            sa.Column('github_weight', sa.Float(), nullable=True),
            sa.Column('github_confidence', sa.Float(), nullable=True),
            sa.Column('transcript_score', sa.Float(), nullable=True),
            sa.Column('transcript_weight', sa.Float(), nullable=True),
            sa.Column('transcript_confidence', sa.Float(), nullable=True),
            sa.Column('resume_score', sa.Float(), nullable=True),
            sa.Column('resume_weight', sa.Float(), nullable=True),
            sa.Column('resume_confidence', sa.Float(), nullable=True),
            # Final score
            sa.Column('overall_score', sa.Float(), nullable=False),
            sa.Column('overall_grade', sa.String(5), nullable=True),
            sa.Column('overall_confidence', sa.Float(), nullable=True),
            sa.Column('data_completeness', sa.Float(), nullable=True),
            sa.Column('signals_available', JSONB(), nullable=True),
            sa.Column('role_fit_scores', JSONB(), nullable=True),
            sa.Column('best_fit_roles', ARRAY(sa.String()), nullable=True),
            sa.Column('top_strengths', JSONB(), nullable=True),
            sa.Column('key_concerns', JSONB(), nullable=True),
            sa.Column('hiring_recommendation', sa.String(50), nullable=True),
            sa.Column('percentile', sa.Float(), nullable=True),
            sa.Column('percentile_cohort', sa.String(100), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_unified_scores_candidate', 'unified_candidate_scores', ['candidate_id'])
        op.create_index('ix_unified_scores_overall', 'unified_candidate_scores', ['overall_score'])

    # ================================================
    # 11. ml_training_runs
    # ================================================
    if not table_exists('ml_training_runs'):
        op.create_table(
            'ml_training_runs',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('model_name', sa.String(100), nullable=False),
            sa.Column('model_type', sa.String(50), nullable=False),
            sa.Column('target_component', sa.String(50), nullable=True),
            sa.Column('base_model', sa.String(100), nullable=True),
            sa.Column('training_data_query', sa.Text(), nullable=True),
            sa.Column('training_samples', sa.Integer(), nullable=True),
            sa.Column('validation_samples', sa.Integer(), nullable=True),
            sa.Column('test_samples', sa.Integer(), nullable=True),
            sa.Column('data_filters', JSONB(), nullable=True),
            sa.Column('hyperparameters', JSONB(), nullable=True),
            sa.Column('training_metrics', JSONB(), nullable=True),
            sa.Column('eval_metrics', JSONB(), nullable=True),
            sa.Column('baseline_comparison', JSONB(), nullable=True),
            sa.Column('model_artifact_path', sa.String(), nullable=True),
            sa.Column('model_size_mb', sa.Float(), nullable=True),
            sa.Column('is_deployed', sa.Boolean(), server_default='false'),
            sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('deployed_as_version', sa.String(20), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_training_runs_model', 'ml_training_runs', ['model_name'])
        op.create_index('ix_training_runs_deployed', 'ml_training_runs', ['is_deployed'])

    # ================================================
    # 12. score_calibrations
    # ================================================
    if not table_exists('score_calibrations'):
        op.create_table(
            'score_calibrations',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('vertical', sa.String(50), nullable=True),
            sa.Column('role_type', sa.String(50), nullable=True),
            sa.Column('company_tier', ref_enum('companytier', [
                'faang', 'tier_1', 'unicorn', 'series_b_c', 'series_a', 'smb', 'unknown'
            ]), nullable=True),
            sa.Column('calibration_data', JSONB(), nullable=False),
            sa.Column('total_samples', sa.Integer(), nullable=True),
            sa.Column('confidence_level', sa.Float(), nullable=True),
            sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
            sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
            sa.Column('algorithm_version', sa.String(20), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_calibrations_vertical_role', 'score_calibrations', ['vertical', 'role_type'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting FK dependencies)
    tables = [
        'score_calibrations', 'ml_training_runs', 'unified_candidate_scores',
        'transcript_analysis_ml', 'resume_analysis_ml', 'github_analysis_ml',
        'interview_transcripts_ml', 'candidate_outcomes',
        'labeling_tasks', 'scoring_labels', 'scoring_events', 'ml_experiments',
    ]
    for table in tables:
        if table_exists(table):
            op.drop_table(table)

    # Drop enums
    for enum_name in ['experimentstatus', 'companytier', 'outcomestage',
                      'outcometype', 'labelsource', 'scoringeventtype']:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")

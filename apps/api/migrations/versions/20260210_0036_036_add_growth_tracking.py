"""Add growth tracking tables

Revision ID: 036
Revises: 035
Create Date: 2026-02-10

Adds tables for tracking student growth over time:
- resume_versions: Track all resume uploads with diffs
- github_analysis_history: Track GitHub score changes over time
- profile_change_logs: Audit trail for GPA, major, education changes
- Add parsed date columns to activities and awards

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '036'
down_revision = '035'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create resume_versions table
    op.create_table(
        'resume_versions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        # Storage
        sa.Column('storage_key', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        # Snapshots
        sa.Column('raw_text', sa.Text(), nullable=True),
        sa.Column('parsed_data', JSONB(), nullable=True),
        # Deltas (computed from previous version)
        sa.Column('skills_added', JSONB(), nullable=True),
        sa.Column('skills_removed', JSONB(), nullable=True),
        sa.Column('projects_added', sa.Integer(), nullable=True),
        sa.Column('experience_added', sa.Integer(), nullable=True),
        # Status
        sa.Column('is_current', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_resume_versions_candidate_id', 'resume_versions', ['candidate_id'])
    op.create_index('ix_resume_versions_is_current', 'resume_versions', ['is_current'])
    op.create_index('ix_resume_versions_uploaded_at', 'resume_versions', ['uploaded_at'])

    # Create github_analysis_history table
    op.create_table(
        'github_analysis_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('github_analysis_id', sa.String(), nullable=True),
        # Score snapshot
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('originality_score', sa.Float(), nullable=True),
        sa.Column('activity_score', sa.Float(), nullable=True),
        sa.Column('depth_score', sa.Float(), nullable=True),
        sa.Column('collaboration_score', sa.Float(), nullable=True),
        # Metrics snapshot
        sa.Column('total_repos_analyzed', sa.Integer(), nullable=True),
        sa.Column('total_commits_by_user', sa.Integer(), nullable=True),
        sa.Column('primary_languages', JSONB(), nullable=True),
        # Deltas
        sa.Column('score_delta', sa.Float(), nullable=True),
        sa.Column('repos_delta', sa.Integer(), nullable=True),
        # Timestamp
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['github_analysis_id'], ['github_analyses.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_github_analysis_history_candidate_id', 'github_analysis_history', ['candidate_id'])
    op.create_index('ix_github_analysis_history_analyzed_at', 'github_analysis_history', ['analyzed_at'])

    # Create profile_change_logs table
    op.create_table(
        'profile_change_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('change_type', sa.String(), nullable=False),  # gpa_update, major_change, etc.
        sa.Column('field_name', sa.String(), nullable=False),
        sa.Column('old_value', JSONB(), nullable=True),
        sa.Column('new_value', JSONB(), nullable=True),
        sa.Column('change_source', sa.String(), nullable=True),  # manual, resume_parse, transcript_verify
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_profile_change_logs_candidate_id', 'profile_change_logs', ['candidate_id'])
    op.create_index('ix_profile_change_logs_change_type', 'profile_change_logs', ['change_type'])
    op.create_index('ix_profile_change_logs_changed_at', 'profile_change_logs', ['changed_at'])

    # Add parsed date columns to candidate_activities
    op.add_column('candidate_activities', sa.Column('parsed_start_date', sa.Date(), nullable=True))
    op.add_column('candidate_activities', sa.Column('parsed_end_date', sa.Date(), nullable=True))
    op.add_column('candidate_activities', sa.Column('is_current', sa.Boolean(), server_default='false', nullable=True))

    # Add parsed date and updated_at to candidate_awards
    op.add_column('candidate_awards', sa.Column('parsed_date', sa.Date(), nullable=True))
    op.add_column('candidate_awards', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove columns from candidate_awards
    op.drop_column('candidate_awards', 'updated_at')
    op.drop_column('candidate_awards', 'parsed_date')

    # Remove columns from candidate_activities
    op.drop_column('candidate_activities', 'is_current')
    op.drop_column('candidate_activities', 'parsed_end_date')
    op.drop_column('candidate_activities', 'parsed_start_date')

    # Drop profile_change_logs table
    op.drop_index('ix_profile_change_logs_changed_at', 'profile_change_logs')
    op.drop_index('ix_profile_change_logs_change_type', 'profile_change_logs')
    op.drop_index('ix_profile_change_logs_candidate_id', 'profile_change_logs')
    op.drop_table('profile_change_logs')

    # Drop github_analysis_history table
    op.drop_index('ix_github_analysis_history_analyzed_at', 'github_analysis_history')
    op.drop_index('ix_github_analysis_history_candidate_id', 'github_analysis_history')
    op.drop_table('github_analysis_history')

    # Drop resume_versions table
    op.drop_index('ix_resume_versions_uploaded_at', 'resume_versions')
    op.drop_index('ix_resume_versions_is_current', 'resume_versions')
    op.drop_index('ix_resume_versions_candidate_id', 'resume_versions')
    op.drop_table('resume_versions')

"""Add GitHub analysis table for deep profile analysis

Revision ID: 009
Revises: 008
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create github_analyses table
    op.create_table(
        'github_analyses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),

        # Overall Scores (0-100)
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('originality_score', sa.Float(), nullable=True),
        sa.Column('activity_score', sa.Float(), nullable=True),
        sa.Column('depth_score', sa.Float(), nullable=True),
        sa.Column('collaboration_score', sa.Float(), nullable=True),

        # Aggregate Stats
        sa.Column('total_repos_analyzed', sa.Integer(), default=0),
        sa.Column('total_commits_by_user', sa.Integer(), default=0),
        sa.Column('total_lines_added', sa.Integer(), default=0),
        sa.Column('total_lines_removed', sa.Integer(), default=0),
        sa.Column('total_prs_opened', sa.Integer(), default=0),
        sa.Column('total_prs_reviewed', sa.Integer(), default=0),

        # Contribution Patterns
        sa.Column('avg_commits_per_week', sa.Float(), nullable=True),
        sa.Column('longest_streak_days', sa.Integer(), default=0),
        sa.Column('active_months_last_year', sa.Integer(), default=0),
        sa.Column('weekend_commit_ratio', sa.Float(), nullable=True),

        # Language Proficiency
        sa.Column('primary_languages', JSONB(), nullable=True),

        # Project Classification Summary
        sa.Column('personal_projects_count', sa.Integer(), default=0),
        sa.Column('class_projects_count', sa.Integer(), default=0),
        sa.Column('fork_contributions_count', sa.Integer(), default=0),
        sa.Column('org_projects_count', sa.Integer(), default=0),

        # Code Origin Signals
        sa.Column('organic_code_ratio', sa.Float(), nullable=True),
        sa.Column('ai_assisted_repos', sa.Integer(), default=0),
        sa.Column('template_based_repos', sa.Integer(), default=0),

        # Quality Signals
        sa.Column('has_tests', sa.Boolean(), default=False),
        sa.Column('has_ci_cd', sa.Boolean(), default=False),
        sa.Column('has_documentation', sa.Boolean(), default=False),
        sa.Column('code_review_participation', sa.Boolean(), default=False),

        # Red Flags
        sa.Column('flags', JSONB(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), default=False),

        # Detailed repo analyses
        sa.Column('repo_analyses', JSONB(), nullable=True),

        # Timestamps
        sa.Column('analyzed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('candidate_id', name='uq_github_analysis_candidate'),
    )

    # Create index on candidate_id for faster lookups
    op.create_index('ix_github_analyses_candidate_id', 'github_analyses', ['candidate_id'])


def downgrade() -> None:
    op.drop_index('ix_github_analyses_candidate_id', table_name='github_analyses')
    op.drop_table('github_analyses')

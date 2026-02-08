"""Add vibe code sessions table

Revision ID: 034
Revises: 033
Create Date: 2026-02-08

Adds the vibe_code_sessions table for storing and analyzing AI coding session logs.
Students upload Cursor/Claude Code/Copilot sessions; Claude analyzes builder quality.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '034'
down_revision: Union[str, None] = '033'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def upgrade() -> None:
    if table_exists("vibe_code_sessions"):
        return

    op.create_table(
        'vibe_code_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),

        # Session metadata
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source', sa.String(), nullable=False, server_default='other'),
        sa.Column('project_url', sa.String(), nullable=True),

        # Raw session data
        sa.Column('session_content', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),

        # Analysis status
        sa.Column('analysis_status', sa.String(), server_default='pending'),
        sa.Column('analysis_error', sa.Text(), nullable=True),

        # Builder Score (0-10)
        sa.Column('builder_score', sa.Float(), nullable=True),
        sa.Column('direction_score', sa.Float(), nullable=True),
        sa.Column('design_thinking_score', sa.Float(), nullable=True),
        sa.Column('iteration_quality_score', sa.Float(), nullable=True),
        sa.Column('product_sense_score', sa.Float(), nullable=True),
        sa.Column('ai_leadership_score', sa.Float(), nullable=True),

        # Analysis output
        sa.Column('analysis_summary', sa.Text(), nullable=True),
        sa.Column('strengths', JSONB(), nullable=True),
        sa.Column('weaknesses', JSONB(), nullable=True),
        sa.Column('notable_patterns', JSONB(), nullable=True),
        sa.Column('builder_archetype', sa.String(), nullable=True),
        sa.Column('analysis_details', JSONB(), nullable=True),

        # Scoring metadata
        sa.Column('scoring_model', sa.String(), nullable=True),
        sa.Column('scoring_version', sa.String(), nullable=True),

        # Timestamps
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )

    # Index for fast lookups by candidate
    op.create_index('ix_vibe_code_sessions_candidate_id', 'vibe_code_sessions', ['candidate_id'])

    # Index for dedup by content hash
    op.create_index('ix_vibe_code_sessions_content_hash', 'vibe_code_sessions', ['candidate_id', 'content_hash'])

    # Index for filtering by analysis status
    op.create_index('ix_vibe_code_sessions_analysis_status', 'vibe_code_sessions', ['analysis_status'])

    # Index for sorting by builder score (talent pool queries)
    op.create_index('ix_vibe_code_sessions_builder_score', 'vibe_code_sessions', ['builder_score'])


def downgrade() -> None:
    op.drop_index('ix_vibe_code_sessions_builder_score', table_name='vibe_code_sessions')
    op.drop_index('ix_vibe_code_sessions_analysis_status', table_name='vibe_code_sessions')
    op.drop_index('ix_vibe_code_sessions_content_hash', table_name='vibe_code_sessions')
    op.drop_index('ix_vibe_code_sessions_candidate_id', table_name='vibe_code_sessions')
    op.drop_table('vibe_code_sessions')

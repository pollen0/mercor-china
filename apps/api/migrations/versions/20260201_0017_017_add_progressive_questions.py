"""Add progressive question tracking

Revision ID: 017
Revises: 016
Create Date: 2026-02-01

This migration adds:
1. candidate_question_history table to track which questions have been asked
2. Progressive difficulty columns to interview_questions table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '017'
down_revision: Union[str, None] = '016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        )
    """))
    return result.scalar()


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND column_name = '{column_name}'
        )
    """))
    return result.scalar()


def upgrade() -> None:
    # Add missing columns to candidate_vertical_profiles table
    if table_exists('candidate_vertical_profiles'):
        # Add total_interviews column (model has this but migration 007 uses attempt_count)
        if not column_exists('candidate_vertical_profiles', 'total_interviews'):
            op.add_column('candidate_vertical_profiles', sa.Column(
                'total_interviews',
                sa.Integer(),
                server_default='0',
                nullable=False
            ))

        # Add last_interview_at column (model has this but migration 007 uses last_attempt_at)
        if not column_exists('candidate_vertical_profiles', 'last_interview_at'):
            op.add_column('candidate_vertical_profiles', sa.Column(
                'last_interview_at',
                sa.DateTime(timezone=True),
                nullable=True
            ))

        # Add next_eligible_at column for tracking monthly cooldown
        if not column_exists('candidate_vertical_profiles', 'next_eligible_at'):
            op.add_column('candidate_vertical_profiles', sa.Column(
                'next_eligible_at',
                sa.DateTime(timezone=True),
                nullable=True
            ))

    # Create candidate_question_history table
    if not table_exists('candidate_question_history'):
        op.create_table(
            'candidate_question_history',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('question_key', sa.String(), nullable=False),
            sa.Column('question_text', sa.Text(), nullable=False),
            sa.Column('vertical', sa.String(), nullable=True),  # Using String for flexibility
            sa.Column('difficulty_level', sa.Integer(), server_default='1'),
            sa.Column('category', sa.String(), nullable=True),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('interview_session_id', sa.String(), nullable=True),
            sa.Column('asked_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='SET NULL'),
        )
        # Create indexes for efficient querying
        op.create_index('ix_candidate_question_history_candidate_id', 'candidate_question_history', ['candidate_id'])
        op.create_index('ix_candidate_question_history_session_id', 'candidate_question_history', ['interview_session_id'])
        op.create_index('ix_candidate_question_history_category', 'candidate_question_history', ['category'])
        op.create_index('ix_candidate_question_history_asked_at', 'candidate_question_history', ['asked_at'])

    # Add progressive difficulty columns to interview_questions table
    if table_exists('interview_questions'):
        if not column_exists('interview_questions', 'difficulty_level'):
            op.add_column('interview_questions', sa.Column(
                'difficulty_level',
                sa.Integer(),
                server_default='1',
                nullable=False
            ))

        if not column_exists('interview_questions', 'skill_tags'):
            op.add_column('interview_questions', sa.Column(
                'skill_tags',
                postgresql.ARRAY(sa.String()),
                nullable=True
            ))

        if not column_exists('interview_questions', 'question_key'):
            op.add_column('interview_questions', sa.Column(
                'question_key',
                sa.String(),
                nullable=True
            ))

        # Add vertical column if it doesn't exist (may already exist from talent pool migration)
        if not column_exists('interview_questions', 'vertical'):
            op.add_column('interview_questions', sa.Column(
                'vertical',
                sa.String(),  # Using String for flexibility
                nullable=True
            ))


def downgrade() -> None:
    # Remove columns from interview_questions
    if table_exists('interview_questions'):
        if column_exists('interview_questions', 'difficulty_level'):
            op.drop_column('interview_questions', 'difficulty_level')
        if column_exists('interview_questions', 'skill_tags'):
            op.drop_column('interview_questions', 'skill_tags')
        if column_exists('interview_questions', 'question_key'):
            op.drop_column('interview_questions', 'question_key')
        # Note: Not dropping vertical as it may have been added by another migration

    # Drop candidate_question_history table
    if table_exists('candidate_question_history'):
        op.drop_index('ix_candidate_question_history_asked_at')
        op.drop_index('ix_candidate_question_history_category')
        op.drop_index('ix_candidate_question_history_session_id')
        op.drop_index('ix_candidate_question_history_candidate_id')
        op.drop_table('candidate_question_history')

"""Add coding challenges for technical assessments

Revision ID: 002
Revises: 001
Create Date: 2026-01-29

This migration adds:
1. coding_challenges table for storing coding problems
2. question_type column to interview_questions and interview_responses
3. coding_challenge_id foreign key to interview_questions
4. Coding-specific columns to interview_responses (code_solution, test_results, etc.)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create coding_challenges table
    op.create_table(
        'coding_challenges',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('title_zh', sa.String(), nullable=True),
        sa.Column('problem_description', sa.Text(), nullable=False),
        sa.Column('problem_description_zh', sa.Text(), nullable=True),
        sa.Column('starter_code', sa.Text(), nullable=True),
        sa.Column('test_cases', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), server_default='5', nullable=True),
        sa.Column('difficulty', sa.String(), server_default='easy', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Add question_type to interview_questions
    op.add_column(
        'interview_questions',
        sa.Column('question_type', sa.String(), server_default='video', nullable=True)
    )

    # Add coding_challenge_id foreign key to interview_questions
    op.add_column(
        'interview_questions',
        sa.Column('coding_challenge_id', sa.String(), nullable=True)
    )
    op.create_foreign_key(
        'fk_interview_questions_coding_challenge',
        'interview_questions',
        'coding_challenges',
        ['coding_challenge_id'],
        ['id'],
        ondelete='SET NULL'
    )

    # Add coding-related columns to interview_responses
    op.add_column(
        'interview_responses',
        sa.Column('question_type', sa.String(), server_default='video', nullable=True)
    )
    op.add_column(
        'interview_responses',
        sa.Column('code_solution', sa.Text(), nullable=True)
    )
    op.add_column(
        'interview_responses',
        sa.Column('execution_status', sa.String(), nullable=True)
    )
    op.add_column(
        'interview_responses',
        sa.Column('test_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'interview_responses',
        sa.Column('execution_time_ms', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    # Remove coding-related columns from interview_responses
    op.drop_column('interview_responses', 'execution_time_ms')
    op.drop_column('interview_responses', 'test_results')
    op.drop_column('interview_responses', 'execution_status')
    op.drop_column('interview_responses', 'code_solution')
    op.drop_column('interview_responses', 'question_type')

    # Remove foreign key and column from interview_questions
    op.drop_constraint('fk_interview_questions_coding_challenge', 'interview_questions', type_='foreignkey')
    op.drop_column('interview_questions', 'coding_challenge_id')
    op.drop_column('interview_questions', 'question_type')

    # Drop coding_challenges table
    op.drop_table('coding_challenges')

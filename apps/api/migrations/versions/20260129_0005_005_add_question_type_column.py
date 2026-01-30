"""Add question_type and coding_challenge_id to interview_questions

Revision ID: 005
Revises: 004
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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


def upgrade() -> None:
    # Add question_type column to interview_questions
    if not column_exists('interview_questions', 'question_type'):
        op.add_column('interview_questions', sa.Column('question_type', sa.String(), nullable=True, server_default='video'))

    # Add coding_challenge_id column to interview_questions (without FK if table doesn't exist)
    if not column_exists('interview_questions', 'coding_challenge_id'):
        op.add_column('interview_questions', sa.Column('coding_challenge_id', sa.String(), nullable=True))

    # Create coding_challenges table if it doesn't exist
    if not table_exists('coding_challenges'):
        op.create_table(
            'coding_challenges',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('title_zh', sa.String(), nullable=True),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('description_zh', sa.Text(), nullable=True),
            sa.Column('difficulty', sa.String(), nullable=False, server_default='medium'),
            sa.Column('language', sa.String(), nullable=False, server_default='python'),
            sa.Column('starter_code', sa.Text(), nullable=True),
            sa.Column('test_cases', sa.JSON(), nullable=True),
            sa.Column('solution', sa.Text(), nullable=True),
            sa.Column('time_limit_seconds', sa.Integer(), nullable=False, server_default='300'),
            sa.Column('category', sa.String(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        )

    # Create code_responses table if it doesn't exist
    if not table_exists('code_responses'):
        op.create_table(
            'code_responses',
            sa.Column('id', sa.String(), primary_key=True),
            sa.Column('response_id', sa.String(), sa.ForeignKey('interview_responses.id', ondelete='CASCADE'), nullable=False),
            sa.Column('code', sa.Text(), nullable=True),
            sa.Column('language', sa.String(), nullable=True),
            sa.Column('execution_result', sa.JSON(), nullable=True),
            sa.Column('test_results', sa.JSON(), nullable=True),
            sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade() -> None:
    op.drop_table('code_responses')
    op.drop_table('coding_challenges')
    op.drop_column('interview_questions', 'coding_challenge_id')
    op.drop_column('interview_questions', 'question_type')

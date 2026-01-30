"""Add missing columns to interview_responses

Revision ID: 006
Revises: 005
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
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


def upgrade() -> None:
    # Add missing columns to interview_responses
    if not column_exists('interview_responses', 'is_followup'):
        op.add_column('interview_responses', sa.Column('is_followup', sa.Boolean(), nullable=False, server_default='false'))

    if not column_exists('interview_responses', 'parent_response_id'):
        op.add_column('interview_responses', sa.Column('parent_response_id', sa.String(), nullable=True))

    if not column_exists('interview_responses', 'question_type'):
        op.add_column('interview_responses', sa.Column('question_type', sa.String(), nullable=True, server_default='video'))

    if not column_exists('interview_responses', 'code_solution'):
        op.add_column('interview_responses', sa.Column('code_solution', sa.Text(), nullable=True))

    if not column_exists('interview_responses', 'execution_status'):
        op.add_column('interview_responses', sa.Column('execution_status', sa.String(), nullable=True))

    if not column_exists('interview_responses', 'test_results'):
        op.add_column('interview_responses', sa.Column('test_results', sa.JSON(), nullable=True))

    if not column_exists('interview_responses', 'execution_time_ms'):
        op.add_column('interview_responses', sa.Column('execution_time_ms', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('interview_responses', 'execution_time_ms')
    op.drop_column('interview_responses', 'test_results')
    op.drop_column('interview_responses', 'execution_status')
    op.drop_column('interview_responses', 'code_solution')
    op.drop_column('interview_responses', 'question_type')
    op.drop_column('interview_responses', 'parent_response_id')
    op.drop_column('interview_responses', 'is_followup')

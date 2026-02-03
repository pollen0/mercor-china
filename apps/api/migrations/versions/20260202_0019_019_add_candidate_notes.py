"""Add candidate notes table

Revision ID: 019a
Revises: 019
Create Date: 2026-02-02

This migration adds the candidate_notes table for employer private notes on candidates.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '019a'
down_revision: Union[str, None] = '019'
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


def upgrade() -> None:
    if not table_exists('candidate_notes'):
        op.create_table(
            'candidate_notes',
            sa.Column('id', sa.String(32), primary_key=True),
            sa.Column('employer_id', sa.String(32), sa.ForeignKey('employers.id'), nullable=False, index=True),
            sa.Column('candidate_id', sa.String(32), sa.ForeignKey('candidates.id'), nullable=False, index=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        )

        # Create index for efficient lookups
        op.create_index(
            'ix_candidate_notes_employer_candidate',
            'candidate_notes',
            ['employer_id', 'candidate_id']
        )


def downgrade() -> None:
    if table_exists('candidate_notes'):
        op.drop_index('ix_candidate_notes_employer_candidate', 'candidate_notes')
        op.drop_table('candidate_notes')

"""Add transcript_key column to candidates

Revision ID: 023
Revises: 022
Create Date: 2026-02-03

This migration adds the transcript_key column to store the R2 storage key
for candidate transcripts, enabling preview functionality.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '023'
down_revision: Union[str, None] = '022'
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
    # Add transcript_key column to candidates table
    if not column_exists('candidates', 'transcript_key'):
        op.add_column(
            'candidates',
            sa.Column('transcript_key', sa.String(), nullable=True)
        )


def downgrade() -> None:
    if column_exists('candidates', 'transcript_key'):
        op.drop_column('candidates', 'transcript_key')

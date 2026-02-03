"""Add name field to employers table

Revision ID: 021
Revises: 020
Create Date: 2026-02-02

This migration adds the 'name' column to the employers table
to store the employer's personal name (separate from company name).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '021'
down_revision: Union[str, None] = '020'
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
    # Add name column to employers table
    if not column_exists('employers', 'name'):
        op.add_column('employers', sa.Column('name', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove name column
    op.drop_column('employers', 'name')

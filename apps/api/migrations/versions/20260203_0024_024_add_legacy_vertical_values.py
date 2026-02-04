"""Migrate legacy vertical values to new format

Revision ID: 024
Revises: 023
Create Date: 2026-02-03

This migration:
1. Adds new enum values to PostgreSQL: software_engineering, product, finance, data, design (lowercase)
2. Updates legacy data: engineering -> software_engineering, business -> product
3. Normalizes uppercase values: DATA -> data, DESIGN -> design
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '024'
down_revision: Union[str, None] = '023'
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
    # Add new enum values (PostgreSQL ADD VALUE is idempotent with IF NOT EXISTS)
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'software_engineering'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'product'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'finance'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'data'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'design'")

    # Tables that may have a vertical column
    tables = ['jobs', 'candidate_vertical_profiles', 'interview_sessions',
              'questions', 'match_alerts', 'employer_question_templates']

    for table in tables:
        if table_exists(table) and column_exists(table, 'vertical'):
            # Migrate legacy values
            op.execute(f"""
                UPDATE {table}
                SET vertical = 'software_engineering'
                WHERE vertical IN ('engineering', 'ENGINEERING')
            """)
            op.execute(f"""
                UPDATE {table}
                SET vertical = 'product'
                WHERE vertical IN ('business', 'BUSINESS')
            """)
            # Normalize uppercase to lowercase
            op.execute(f"UPDATE {table} SET vertical = 'data' WHERE vertical = 'DATA'")
            op.execute(f"UPDATE {table} SET vertical = 'design' WHERE vertical = 'DESIGN'")


def downgrade() -> None:
    # Note: Cannot remove enum values in PostgreSQL without recreating the type
    # Data migration is not reversible as we're normalizing legacy values
    pass

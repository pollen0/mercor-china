"""Add lowercase enum values for vertical and role_type

Revision ID: 025
Revises: 024
Create Date: 2026-02-04

This migration adds the lowercase enum values.
The actual data update happens in migration 026.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '025'
down_revision: Union[str, None] = '024'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # VERTICAL ENUM - Add any missing lowercase values
    # ============================================
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'software_engineering'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'data'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'product'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'design'")
    op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'finance'")

    # ============================================
    # ROLE_TYPE ENUM - Add lowercase values
    # ============================================
    # Check if roletype enum exists
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT typname FROM pg_type WHERE typname IN ('roletype', 'role_type')
    """))
    role_enum_name = result.scalar()

    if role_enum_name:
        # Add all lowercase role_type values
        role_types = [
            'software_engineer', 'embedded_engineer', 'qa_engineer',
            'data_analyst', 'data_scientist', 'ml_engineer', 'data_engineer',
            'product_manager', 'associate_pm',
            'ux_designer', 'ui_designer', 'product_designer',
            'ib_analyst', 'finance_analyst', 'equity_research'
        ]
        for role in role_types:
            op.execute(f"ALTER TYPE {role_enum_name} ADD VALUE IF NOT EXISTS '{role}'")


def downgrade() -> None:
    # Cannot remove enum values in PostgreSQL
    pass

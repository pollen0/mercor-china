"""Add legacy vertical enum values

Revision ID: 024
Revises: 023
Create Date: 2026-02-03

This migration adds legacy 'engineering' and 'business' values to the vertical enum
to support existing data in the database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '024'
down_revision: Union[str, None] = '023'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def enum_value_exists(enum_name: str, value: str) -> bool:
    """Check if an enum value exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM pg_enum
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = '{enum_name}')
            AND enumlabel = '{value}'
        )
    """))
    return result.scalar()


def upgrade() -> None:
    # Add 'engineering' to vertical enum if not exists
    if not enum_value_exists('vertical', 'engineering'):
        op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'engineering'")

    # Add 'business' to vertical enum if not exists
    if not enum_value_exists('vertical', 'business'):
        op.execute("ALTER TYPE vertical ADD VALUE IF NOT EXISTS 'business'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # The legacy values will remain but won't cause issues
    # To fully remove them would require recreating the enum type
    pass

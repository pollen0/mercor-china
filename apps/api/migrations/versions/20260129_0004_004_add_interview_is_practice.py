"""Add is_practice column to interview_sessions

Revision ID: 004
Revises: 003
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
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
    # Add is_practice column to interview_sessions
    if not column_exists('interview_sessions', 'is_practice'):
        op.add_column('interview_sessions', sa.Column('is_practice', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('interview_sessions', 'is_practice')

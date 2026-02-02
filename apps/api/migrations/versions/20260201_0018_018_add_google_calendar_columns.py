"""Add Google Calendar columns to employers and candidates

Revision ID: 018
Revises: 017
Create Date: 2026-02-01

This migration adds Google Calendar OAuth columns:
- google_calendar_token (encrypted access token)
- google_calendar_refresh_token (encrypted refresh token)
- google_calendar_connected_at (timestamp)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '018'
down_revision: Union[str, None] = '017'
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
    # Add Google Calendar columns to employers table
    if not column_exists('employers', 'google_calendar_token'):
        op.add_column('employers', sa.Column('google_calendar_token', sa.String(), nullable=True))

    if not column_exists('employers', 'google_calendar_refresh_token'):
        op.add_column('employers', sa.Column('google_calendar_refresh_token', sa.String(), nullable=True))

    if not column_exists('employers', 'google_calendar_connected_at'):
        op.add_column('employers', sa.Column('google_calendar_connected_at', sa.DateTime(timezone=True), nullable=True))

    # Add Google Calendar columns to candidates table
    if not column_exists('candidates', 'google_calendar_token'):
        op.add_column('candidates', sa.Column('google_calendar_token', sa.String(), nullable=True))

    if not column_exists('candidates', 'google_calendar_refresh_token'):
        op.add_column('candidates', sa.Column('google_calendar_refresh_token', sa.String(), nullable=True))

    if not column_exists('candidates', 'google_calendar_connected_at'):
        op.add_column('candidates', sa.Column('google_calendar_connected_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove Google Calendar columns from employers table
    if column_exists('employers', 'google_calendar_connected_at'):
        op.drop_column('employers', 'google_calendar_connected_at')

    if column_exists('employers', 'google_calendar_refresh_token'):
        op.drop_column('employers', 'google_calendar_refresh_token')

    if column_exists('employers', 'google_calendar_token'):
        op.drop_column('employers', 'google_calendar_token')

    # Remove Google Calendar columns from candidates table
    if column_exists('candidates', 'google_calendar_connected_at'):
        op.drop_column('candidates', 'google_calendar_connected_at')

    if column_exists('candidates', 'google_calendar_refresh_token'):
        op.drop_column('candidates', 'google_calendar_refresh_token')

    if column_exists('candidates', 'google_calendar_token'):
        op.drop_column('candidates', 'google_calendar_token')

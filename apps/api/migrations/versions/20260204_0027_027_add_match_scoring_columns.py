"""Add scoring columns to matches table

Revision ID: 027
Revises: 026
Create Date: 2026-02-04

This migration adds the enhanced matching score columns to the matches table.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '027'
down_revision: Union[str, None] = '026'
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
    # Add interview_score column
    if not column_exists('matches', 'interview_score'):
        op.add_column('matches', sa.Column('interview_score', sa.Float(), nullable=True))

    # Add skills_match_score column
    if not column_exists('matches', 'skills_match_score'):
        op.add_column('matches', sa.Column('skills_match_score', sa.Float(), nullable=True))

    # Add experience_match_score column
    if not column_exists('matches', 'experience_match_score'):
        op.add_column('matches', sa.Column('experience_match_score', sa.Float(), nullable=True))

    # Add location_match column
    if not column_exists('matches', 'location_match'):
        op.add_column('matches', sa.Column('location_match', sa.Boolean(), nullable=True))

    # Add overall_match_score column
    if not column_exists('matches', 'overall_match_score'):
        op.add_column('matches', sa.Column('overall_match_score', sa.Float(), nullable=True))

    # Add factors column (JSON text for detailed scoring breakdown)
    if not column_exists('matches', 'factors'):
        op.add_column('matches', sa.Column('factors', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('matches', 'factors')
    op.drop_column('matches', 'overall_match_score')
    op.drop_column('matches', 'location_match')
    op.drop_column('matches', 'experience_match_score')
    op.drop_column('matches', 'skills_match_score')
    op.drop_column('matches', 'interview_score')

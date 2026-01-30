"""Add candidate authentication columns

Revision ID: 003
Revises: 002
Create Date: 2026-01-29

This migration adds:
1. password_hash column to candidates for email/password authentication
2. resume_raw_text column for storing extracted resume text
3. resume_parsed_data column for storing parsed resume JSON
4. resume_uploaded_at column for tracking upload time
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # Add password_hash column (nullable for WeChat-only users)
    if not column_exists('candidates', 'password_hash'):
        op.add_column('candidates', sa.Column('password_hash', sa.String(), nullable=True))

    # Add resume columns if missing
    if not column_exists('candidates', 'resume_raw_text'):
        op.add_column('candidates', sa.Column('resume_raw_text', sa.Text(), nullable=True))

    if not column_exists('candidates', 'resume_parsed_data'):
        op.add_column('candidates', sa.Column('resume_parsed_data', postgresql.JSONB(), nullable=True))

    if not column_exists('candidates', 'resume_uploaded_at'):
        op.add_column('candidates', sa.Column('resume_uploaded_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove columns in reverse order
    if column_exists('candidates', 'resume_uploaded_at'):
        op.drop_column('candidates', 'resume_uploaded_at')

    if column_exists('candidates', 'resume_parsed_data'):
        op.drop_column('candidates', 'resume_parsed_data')

    if column_exists('candidates', 'resume_raw_text'):
        op.drop_column('candidates', 'resume_raw_text')

    if column_exists('candidates', 'password_hash'):
        op.drop_column('candidates', 'password_hash')

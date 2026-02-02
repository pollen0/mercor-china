"""Add education and GitHub columns to candidates

Revision ID: 010
Revises: 009
Create Date: 2026-01-31

This migration adds:
1. Education columns: university, major, graduation_year, gpa, courses
2. GitHub OAuth columns: github_username, github_access_token, github_data, github_connected_at
3. Bio and link columns: bio, linkedin_url, portfolio_url

These columns support the US market pivot (Pathway) features:
- University selection during registration
- GitHub OAuth integration
- Student profile enhancement
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    # ==================== CANDIDATES TABLE ====================
    # Education columns
    if not column_exists('candidates', 'university'):
        op.add_column('candidates', sa.Column('university', sa.String(), nullable=True))

    if not column_exists('candidates', 'major'):
        op.add_column('candidates', sa.Column('major', sa.String(), nullable=True))

    if not column_exists('candidates', 'graduation_year'):
        op.add_column('candidates', sa.Column('graduation_year', sa.Integer(), nullable=True))

    if not column_exists('candidates', 'gpa'):
        op.add_column('candidates', sa.Column('gpa', sa.Float(), nullable=True))

    if not column_exists('candidates', 'courses'):
        op.add_column('candidates', sa.Column('courses', JSONB(), nullable=True))

    # GitHub OAuth columns
    if not column_exists('candidates', 'github_username'):
        op.add_column('candidates', sa.Column('github_username', sa.String(), nullable=True))
        # Add unique constraint - but only if column was just created
        op.create_index('ix_candidates_github_username', 'candidates', ['github_username'], unique=True)

    if not column_exists('candidates', 'github_access_token'):
        op.add_column('candidates', sa.Column('github_access_token', sa.String(), nullable=True))

    if not column_exists('candidates', 'github_data'):
        op.add_column('candidates', sa.Column('github_data', JSONB(), nullable=True))

    if not column_exists('candidates', 'github_connected_at'):
        op.add_column('candidates', sa.Column('github_connected_at', sa.DateTime(timezone=True), nullable=True))

    # Bio and links
    if not column_exists('candidates', 'bio'):
        op.add_column('candidates', sa.Column('bio', sa.Text(), nullable=True))

    if not column_exists('candidates', 'linkedin_url'):
        op.add_column('candidates', sa.Column('linkedin_url', sa.String(), nullable=True))

    if not column_exists('candidates', 'portfolio_url'):
        op.add_column('candidates', sa.Column('portfolio_url', sa.String(), nullable=True))

    # Email verification columns
    if not column_exists('candidates', 'email_verified'):
        op.add_column('candidates', sa.Column('email_verified', sa.Boolean(), default=False, server_default='false'))

    if not column_exists('candidates', 'email_verification_token'):
        op.add_column('candidates', sa.Column('email_verification_token', sa.String(), nullable=True))

    if not column_exists('candidates', 'email_verification_expires_at'):
        op.add_column('candidates', sa.Column('email_verification_expires_at', sa.DateTime(timezone=True), nullable=True))

    # ==================== EMPLOYERS TABLE ====================
    # Employer email verification columns
    if not column_exists('employers', 'email_verification_token'):
        op.add_column('employers', sa.Column('email_verification_token', sa.String(), nullable=True))

    if not column_exists('employers', 'email_verification_expires_at'):
        op.add_column('employers', sa.Column('email_verification_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove employer verification columns
    if column_exists('employers', 'email_verification_expires_at'):
        op.drop_column('employers', 'email_verification_expires_at')

    if column_exists('employers', 'email_verification_token'):
        op.drop_column('employers', 'email_verification_token')
    # Remove email verification columns
    if column_exists('candidates', 'email_verification_expires_at'):
        op.drop_column('candidates', 'email_verification_expires_at')

    if column_exists('candidates', 'email_verification_token'):
        op.drop_column('candidates', 'email_verification_token')

    if column_exists('candidates', 'email_verified'):
        op.drop_column('candidates', 'email_verified')

    # Remove bio and links
    if column_exists('candidates', 'portfolio_url'):
        op.drop_column('candidates', 'portfolio_url')

    if column_exists('candidates', 'linkedin_url'):
        op.drop_column('candidates', 'linkedin_url')

    if column_exists('candidates', 'bio'):
        op.drop_column('candidates', 'bio')

    # Remove GitHub columns
    if column_exists('candidates', 'github_connected_at'):
        op.drop_column('candidates', 'github_connected_at')

    if column_exists('candidates', 'github_data'):
        op.drop_column('candidates', 'github_data')

    if column_exists('candidates', 'github_access_token'):
        op.drop_column('candidates', 'github_access_token')

    if column_exists('candidates', 'github_username'):
        op.drop_index('ix_candidates_github_username', table_name='candidates')
        op.drop_column('candidates', 'github_username')

    # Remove education columns
    if column_exists('candidates', 'courses'):
        op.drop_column('candidates', 'courses')

    if column_exists('candidates', 'gpa'):
        op.drop_column('candidates', 'gpa')

    if column_exists('candidates', 'graduation_year'):
        op.drop_column('candidates', 'graduation_year')

    if column_exists('candidates', 'major'):
        op.drop_column('candidates', 'major')

    if column_exists('candidates', 'university'):
        op.drop_column('candidates', 'university')

"""Add email verification fields to candidates and employers

Revision ID: 008
Revises: 007
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
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
    # Add email verification columns to candidates
    if not column_exists('candidates', 'email_verified'):
        op.add_column('candidates', sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False))

    if not column_exists('candidates', 'email_verification_token'):
        op.add_column('candidates', sa.Column('email_verification_token', sa.String(), nullable=True))

    if not column_exists('candidates', 'email_verification_expires_at'):
        op.add_column('candidates', sa.Column('email_verification_expires_at', sa.DateTime(timezone=True), nullable=True))

    # Add email verification columns to employers (they already have is_verified)
    if not column_exists('employers', 'email_verification_token'):
        op.add_column('employers', sa.Column('email_verification_token', sa.String(), nullable=True))

    if not column_exists('employers', 'email_verification_expires_at'):
        op.add_column('employers', sa.Column('email_verification_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove columns from employers
    if column_exists('employers', 'email_verification_expires_at'):
        op.drop_column('employers', 'email_verification_expires_at')
    if column_exists('employers', 'email_verification_token'):
        op.drop_column('employers', 'email_verification_token')

    # Remove columns from candidates
    if column_exists('candidates', 'email_verification_expires_at'):
        op.drop_column('candidates', 'email_verification_expires_at')
    if column_exists('candidates', 'email_verification_token'):
        op.drop_column('candidates', 'email_verification_token')
    if column_exists('candidates', 'email_verified'):
        op.drop_column('candidates', 'email_verified')

"""Add profile tokens for shareable candidate profiles

Revision ID: 016
Revises: 015
Create Date: 2026-02-01

Adds support for:
- Magic link tokens for public candidate profile viewing
- Token expiration and usage tracking
- Employer attribution for generated links

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'profile_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('created_by_id', sa.String(), nullable=True),
        sa.Column('created_by_type', sa.String(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_profile_tokens_token', 'profile_tokens', ['token'])


def downgrade() -> None:
    op.drop_index('ix_profile_tokens_token', 'profile_tokens')
    op.drop_table('profile_tokens')

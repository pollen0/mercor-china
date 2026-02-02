"""Add student sharing preferences and consent

Revision ID: 015
Revises: 014
Create Date: 2026-02-01

Adds support for:
- Student opt-in to profile sharing with employers
- Granular sharing preferences (company stage, locations, industries)
- Email digest notification preferences

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add opt-in consent for profile sharing
    op.add_column('candidates', sa.Column('opted_in_to_sharing', sa.Boolean(), server_default='false', nullable=False))

    # Add sharing preferences JSONB
    # Structure: {
    #   "company_stages": ["seed", "series_a", "series_b", "series_c_plus"],
    #   "locations": ["remote", "sf", "nyc", "seattle", "austin", ...],
    #   "industries": ["fintech", "climate", "ai", "healthcare", ...],
    #   "email_digest": true
    # }
    op.add_column('candidates', sa.Column('sharing_preferences', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('candidates', 'sharing_preferences')
    op.drop_column('candidates', 'opted_in_to_sharing')

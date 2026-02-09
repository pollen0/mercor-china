"""Add transcript verification columns

Revision ID: 034_add_transcript_verification
Revises: 033_create_ml_scoring_tables
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '034_add_transcript_verification'
down_revision = '033'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add transcript verification columns to candidates table
    op.add_column('candidates', sa.Column('transcript_verification', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('candidates', sa.Column('transcript_verification_status', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('transcript_confidence_score', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove transcript verification columns
    op.drop_column('candidates', 'transcript_confidence_score')
    op.drop_column('candidates', 'transcript_verification_status')
    op.drop_column('candidates', 'transcript_verification')

"""add scoring version tracking to interview responses

Revision ID: 014
Revises: 013
Create Date: 2026-02-01 18:40:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '014'
down_revision: Union[str, None] = '013'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add scoring version tracking columns to interview_responses
    op.add_column('interview_responses', sa.Column('scoring_algorithm_version', sa.String(), nullable=True))
    op.add_column('interview_responses', sa.Column('scored_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('interview_responses', sa.Column('raw_score_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    op.drop_column('interview_responses', 'raw_score_data')
    op.drop_column('interview_responses', 'scored_at')
    op.drop_column('interview_responses', 'scoring_algorithm_version')

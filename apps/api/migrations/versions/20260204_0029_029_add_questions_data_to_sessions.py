"""Add questions_data JSONB column to interview_sessions

Revision ID: 029
Revises: 028
Create Date: 2026-02-04

Stores AI-generated personalized questions directly on the interview session
so the room page can display them instead of falling back to static templates.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '029'
down_revision: Union[str, None] = '028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('interview_sessions', sa.Column('questions_data', JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column('interview_sessions', 'questions_data')

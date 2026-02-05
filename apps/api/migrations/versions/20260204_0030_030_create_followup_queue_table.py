"""Create followup_queue table

Revision ID: 030
Revises: 029
Create Date: 2026-02-04

The followup_queue table was defined in the model but missing from the database.
It stores AI-generated follow-up questions for interview sessions.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic.
revision: str = '030'
down_revision: Union[str, None] = '029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'followup_queue',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('generated_questions', ARRAY(sa.String()), nullable=False),
        sa.Column('selected_index', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'ASKED', 'SKIPPED', name='followupqueuestatus', create_type=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('followup_queue')
    op.execute("DROP TYPE IF EXISTS followupqueuestatus")

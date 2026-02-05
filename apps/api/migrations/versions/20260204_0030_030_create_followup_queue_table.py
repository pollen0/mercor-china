"""Create followup_queue table (if not exists)

Revision ID: 030
Revises: 029
Create Date: 2026-02-04

The followup_queue table was defined in the model and in migration 001,
but may be missing from the database. This migration safely creates it
only if it doesn't already exist.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, ENUM

# revision identifiers, used by Alembic.
revision: str = '030'
down_revision: Union[str, None] = '029'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def upgrade() -> None:
    if table_exists('followup_queue'):
        return

    # Create enum if not exists
    followup_status = ENUM('PENDING', 'ASKED', 'SKIPPED', name='followupqueuestatus', create_type=False)
    followup_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'followup_queue',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('generated_questions', ARRAY(sa.String()), nullable=False),
        sa.Column('selected_index', sa.Integer(), nullable=True),
        sa.Column('status', followup_status, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    if table_exists('followup_queue'):
        op.drop_table('followup_queue')
    op.execute("DROP TYPE IF EXISTS followupqueuestatus")

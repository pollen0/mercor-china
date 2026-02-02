"""Add scheduled_interviews table for employer interview scheduling

Revision ID: 019
Revises: 018
Create Date: 2026-02-02

This migration creates the scheduled_interviews table to support
employer-candidate interview scheduling with Google Calendar integration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '019'
down_revision: Union[str, None] = '018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        )
    """))
    return result.scalar()


def enum_exists(enum_name: str) -> bool:
    """Check if an enum type exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM pg_type
            WHERE typname = '{enum_name}'
        )
    """))
    return result.scalar()


def upgrade() -> None:
    if table_exists('scheduled_interviews'):
        return

    # Create interview_type enum if not exists
    if not enum_exists('interviewtype'):
        interview_type_enum = ENUM(
            'phone_screen', 'technical', 'behavioral', 'culture_fit', 'final', 'other',
            name='interviewtype',
            create_type=False
        )
        interview_type_enum.create(op.get_bind(), checkfirst=True)

    # Create scheduled_interview_status enum if not exists
    if not enum_exists('scheduledinterviewstatus'):
        status_enum = ENUM(
            'pending', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled',
            name='scheduledinterviewstatus',
            create_type=False
        )
        status_enum.create(op.get_bind(), checkfirst=True)

    # Reference existing enums (don't create them)
    interview_type = ENUM(
        'phone_screen', 'technical', 'behavioral', 'culture_fit', 'final', 'other',
        name='interviewtype',
        create_type=False
    )
    status_type = ENUM(
        'pending', 'confirmed', 'completed', 'cancelled', 'no_show', 'rescheduled',
        name='scheduledinterviewstatus',
        create_type=False
    )

    # Create scheduled_interviews table
    op.create_table(
        'scheduled_interviews',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employer_id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('interview_type', interview_type, server_default='other'),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), server_default='30'),
        sa.Column('timezone', sa.String(), server_default='America/Los_Angeles'),
        sa.Column('google_event_id', sa.String(), nullable=True),
        sa.Column('google_meet_link', sa.String(), nullable=True),
        sa.Column('calendar_link', sa.String(), nullable=True),
        sa.Column('additional_attendees', sa.JSON(), nullable=True),
        sa.Column('status', status_type, server_default='pending'),
        sa.Column('employer_notes', sa.Text(), nullable=True),
        sa.Column('rescheduled_to_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rescheduled_to_id'], ['scheduled_interviews.id'], ondelete='SET NULL'),
    )

    # Create indexes for common queries
    op.create_index('ix_scheduled_interviews_employer_id', 'scheduled_interviews', ['employer_id'])
    op.create_index('ix_scheduled_interviews_candidate_id', 'scheduled_interviews', ['candidate_id'])
    op.create_index('ix_scheduled_interviews_job_id', 'scheduled_interviews', ['job_id'])
    op.create_index('ix_scheduled_interviews_scheduled_at', 'scheduled_interviews', ['scheduled_at'])
    op.create_index('ix_scheduled_interviews_status', 'scheduled_interviews', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_scheduled_interviews_status', table_name='scheduled_interviews')
    op.drop_index('ix_scheduled_interviews_scheduled_at', table_name='scheduled_interviews')
    op.drop_index('ix_scheduled_interviews_job_id', table_name='scheduled_interviews')
    op.drop_index('ix_scheduled_interviews_candidate_id', table_name='scheduled_interviews')
    op.drop_index('ix_scheduled_interviews_employer_id', table_name='scheduled_interviews')

    # Drop table
    op.drop_table('scheduled_interviews')

    # Drop enums (only if they exist and no other tables use them)
    ENUM(name='scheduledinterviewstatus').drop(op.get_bind(), checkfirst=True)
    ENUM(name='interviewtype').drop(op.get_bind(), checkfirst=True)

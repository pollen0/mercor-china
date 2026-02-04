"""Add employer_team_members and scheduling tables

Revision ID: 022
Revises: 021
Create Date: 2026-02-03

This migration adds:
- employer_team_members table for team interview management
- interviewer_availability table for availability slots
- availability_exceptions table for exceptions
- scheduling_links table for self-scheduling
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = '022'
down_revision: Union[str, None] = '021'
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
    # Create team member role enum
    if not enum_exists('teammemberrole'):
        team_role_enum = ENUM('admin', 'recruiter', 'hiring_manager', 'interviewer', name='teammemberrole', create_type=False)
        team_role_enum.create(op.get_bind(), checkfirst=True)

    # Create employer_team_members table
    if not table_exists('employer_team_members'):
        op.create_table(
            'employer_team_members',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('employer_id', sa.String(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('role', ENUM('admin', 'recruiter', 'hiring_manager', 'interviewer', name='teammemberrole', create_type=False), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('google_calendar_connected', sa.Boolean(), nullable=True, default=False),
            sa.Column('google_calendar_token', sa.String(), nullable=True),
            sa.Column('google_calendar_refresh_token', sa.String(), nullable=True),
            sa.Column('google_calendar_connected_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('max_interviews_per_day', sa.Integer(), nullable=True, default=4),
            sa.Column('max_interviews_per_week', sa.Integer(), nullable=True, default=15),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_team_members_employer_id', 'employer_team_members', ['employer_id'])
        op.create_index('ix_team_members_email', 'employer_team_members', ['email'])
        op.create_index('ix_team_members_employer_active', 'employer_team_members', ['employer_id', 'is_active'])

    # Create interviewer_availability table
    if not table_exists('interviewer_availability'):
        op.create_table(
            'interviewer_availability',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('team_member_id', sa.String(), nullable=False),
            sa.Column('day_of_week', sa.Integer(), nullable=False),  # 0=Monday, 6=Sunday
            sa.Column('start_time', sa.Time(), nullable=False),
            sa.Column('end_time', sa.Time(), nullable=False),
            sa.Column('timezone', sa.String(), nullable=False, default='America/Los_Angeles'),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['team_member_id'], ['employer_team_members.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_availability_team_member', 'interviewer_availability', ['team_member_id'])

    # Create availability_exceptions table
    if not table_exists('availability_exceptions'):
        op.create_table(
            'availability_exceptions',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('team_member_id', sa.String(), nullable=False),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('is_unavailable', sa.Boolean(), nullable=True, default=True),
            sa.Column('start_time', sa.Time(), nullable=True),
            sa.Column('end_time', sa.Time(), nullable=True),
            sa.Column('reason', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['team_member_id'], ['employer_team_members.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_exceptions_team_member_date', 'availability_exceptions', ['team_member_id', 'date'])

    # Create self_scheduling_links table
    if not table_exists('self_scheduling_links'):
        op.create_table(
            'self_scheduling_links',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('employer_id', sa.String(), nullable=False),
            sa.Column('job_id', sa.String(), nullable=True),
            sa.Column('slug', sa.String(), nullable=False, unique=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.Column('duration_minutes', sa.Integer(), nullable=False, default=30),
            sa.Column('interviewer_ids', sa.JSON(), nullable=False, default=[]),
            sa.Column('buffer_before_minutes', sa.Integer(), nullable=True, default=5),
            sa.Column('buffer_after_minutes', sa.Integer(), nullable=True, default=5),
            sa.Column('min_notice_hours', sa.Integer(), nullable=True, default=24),
            sa.Column('max_days_ahead', sa.Integer(), nullable=True, default=14),
            sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('view_count', sa.Integer(), nullable=True, default=0),
            sa.Column('booking_count', sa.Integer(), nullable=True, default=0),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_self_scheduling_links_employer', 'self_scheduling_links', ['employer_id'])
        op.create_index('ix_self_scheduling_links_slug', 'self_scheduling_links', ['slug'], unique=True)


def downgrade() -> None:
    op.drop_table('self_scheduling_links')
    op.drop_table('availability_exceptions')
    op.drop_table('interviewer_availability')
    op.drop_table('employer_team_members')

    # Drop enum
    op.execute("DROP TYPE IF EXISTS teammemberrole")

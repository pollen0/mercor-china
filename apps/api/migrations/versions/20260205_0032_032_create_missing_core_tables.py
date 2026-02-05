"""Create missing core application tables

Revision ID: 032
Revises: 031
Create Date: 2026-02-05

Creates tables defined in models but missing from migrations:
- interview_history (candidate.py)
- interview_reminders (reminder.py)
- course_grade_mappings (course.py)
- candidate_transcripts (course.py)
- candidate_course_grades (course.py)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ENUM

# revision identifiers, used by Alembic.
revision: str = '032'
down_revision: Union[str, None] = '031'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def enum_exists(enum_name: str) -> bool:
    """Check if an enum type exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
    ), {"name": enum_name})
    return result.scalar()


def upgrade() -> None:
    # ========================================
    # 1. interview_history table
    # ========================================
    if not table_exists('interview_history'):
        op.create_table(
            'interview_history',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('vertical', sa.String(50), nullable=False),
            sa.Column('role_type', sa.String(50), nullable=False),
            sa.Column('interview_session_id', sa.String(), nullable=True),
            # Scores
            sa.Column('overall_score', sa.Float(), nullable=True),
            sa.Column('communication_score', sa.Float(), nullable=True),
            sa.Column('problem_solving_score', sa.Float(), nullable=True),
            sa.Column('technical_score', sa.Float(), nullable=True),
            sa.Column('growth_mindset_score', sa.Float(), nullable=True),
            sa.Column('culture_fit_score', sa.Float(), nullable=True),
            # Context snapshots
            sa.Column('education_snapshot', JSONB(), nullable=True),
            sa.Column('github_snapshot', JSONB(), nullable=True),
            # Time
            sa.Column('interview_month', sa.Integer(), nullable=False),
            sa.Column('interview_year', sa.Integer(), nullable=False),
            sa.Column('completed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            # Keys
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='SET NULL'),
            sa.UniqueConstraint('candidate_id', 'vertical', 'interview_month', 'interview_year',
                                name='uq_candidate_vertical_month'),
        )

    # ========================================
    # 2. interview_reminders table
    # ========================================
    if not table_exists('interview_reminders'):
        # Create enums
        if not enum_exists('remindertype'):
            ENUM('24h', '1h', 'custom', name='remindertype', create_type=True).create(
                op.get_bind(), checkfirst=True
            )
        if not enum_exists('reminderstatus'):
            ENUM('pending', 'sent', 'failed', 'cancelled', name='reminderstatus', create_type=True).create(
                op.get_bind(), checkfirst=True
            )

        reminder_type = ENUM('24h', '1h', 'custom', name='remindertype', create_type=False)
        reminder_status = ENUM('pending', 'sent', 'failed', 'cancelled', name='reminderstatus', create_type=False)

        op.create_table(
            'interview_reminders',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('scheduled_interview_id', sa.String(), nullable=False),
            sa.Column('reminder_type', reminder_type, nullable=False),
            sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
            sa.Column('status', reminder_status, server_default='pending'),
            sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('recipient_type', sa.String(), server_default='candidate'),
            sa.Column('recipient_email', sa.String(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['scheduled_interview_id'], ['scheduled_interviews.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_reminders_scheduled_interview', 'interview_reminders', ['scheduled_interview_id'])
        op.create_index('ix_reminders_pending', 'interview_reminders', ['status', 'scheduled_for'])
        op.create_index('ix_reminders_scheduled_for', 'interview_reminders', ['scheduled_for'])

    # ========================================
    # 3. course_grade_mappings table
    # ========================================
    if not table_exists('course_grade_mappings'):
        op.create_table(
            'course_grade_mappings',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('university_id', sa.String(), nullable=True),
            sa.Column('grade', sa.String(), nullable=False),
            sa.Column('gpa_value', sa.Float(), nullable=False),
            sa.Column('percentile_estimate', sa.Float(), nullable=True),
            sa.Column('is_passing', sa.Boolean(), server_default='true'),
            sa.Column('is_credit_only', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
        )

    # ========================================
    # 4. candidate_transcripts table
    # ========================================
    if not table_exists('candidate_transcripts'):
        op.create_table(
            'candidate_transcripts',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('file_url', sa.String(), nullable=True),
            sa.Column('university_id', sa.String(), nullable=True),
            sa.Column('is_official', sa.Boolean(), server_default='false'),
            sa.Column('parsed_courses', JSONB(), nullable=True),
            sa.Column('cumulative_gpa', sa.Float(), nullable=True),
            sa.Column('major_gpa', sa.Float(), nullable=True),
            # Computed scores
            sa.Column('transcript_score', sa.Float(), nullable=True),
            sa.Column('course_rigor_score', sa.Float(), nullable=True),
            sa.Column('performance_score', sa.Float(), nullable=True),
            sa.Column('trajectory_score', sa.Float(), nullable=True),
            sa.Column('load_score', sa.Float(), nullable=True),
            sa.Column('score_breakdown', JSONB(), nullable=True),
            # Flags
            sa.Column('flags', JSONB(), nullable=True),
            sa.Column('requires_review', sa.Boolean(), server_default='false'),
            # Metadata
            sa.Column('semesters_analyzed', sa.Integer(), server_default='0'),
            sa.Column('total_units', sa.Integer(), server_default='0'),
            sa.Column('technical_units', sa.Integer(), server_default='0'),
            # Timestamps
            sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('candidate_id'),
        )

    # ========================================
    # 5. candidate_course_grades table
    # ========================================
    if not table_exists('candidate_course_grades'):
        op.create_table(
            'candidate_course_grades',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('transcript_id', sa.String(), nullable=False),
            sa.Column('course_id', sa.String(), nullable=True),
            sa.Column('course_code', sa.String(), nullable=False),
            sa.Column('course_name', sa.String(), nullable=True),
            sa.Column('grade', sa.String(), nullable=False),
            sa.Column('gpa_value', sa.Float(), nullable=True),
            sa.Column('units', sa.Integer(), server_default='3'),
            sa.Column('semester', sa.String(), nullable=True),
            sa.Column('year', sa.Integer(), nullable=True),
            sa.Column('student_year', sa.Integer(), nullable=True),
            sa.Column('difficulty_at_time', sa.Float(), nullable=True),
            sa.Column('performance_percentile', sa.Float(), nullable=True),
            sa.Column('is_retake', sa.Boolean(), server_default='false'),
            sa.Column('is_transfer', sa.Boolean(), server_default='false'),
            sa.Column('is_ap', sa.Boolean(), server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_candidate_courses_candidate', 'candidate_course_grades', ['candidate_id'])
        op.create_index('ix_candidate_courses_course', 'candidate_course_grades', ['course_id'])


def downgrade() -> None:
    for table in ['candidate_course_grades', 'candidate_transcripts',
                  'course_grade_mappings', 'interview_reminders', 'interview_history']:
        if table_exists(table):
            op.drop_table(table)

    op.execute("DROP TYPE IF EXISTS reminderstatus")
    op.execute("DROP TYPE IF EXISTS remindertype")

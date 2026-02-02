"""Initial schema - captures existing database structure

Revision ID: 001
Revises:
Create Date: 2026-01-29

This migration represents the initial database schema for Pathway.
All tables that existed before Alembic was introduced are captured here.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enums first
    vertical_enum = postgresql.ENUM('new_energy', 'sales', name='vertical', create_type=False)
    role_type_enum = postgresql.ENUM(
        'battery_engineer', 'embedded_software', 'autonomous_driving',
        'supply_chain', 'ev_sales', 'sales_rep', 'bd_manager', 'account_manager',
        name='roletype', create_type=False
    )
    interview_status_enum = postgresql.ENUM(
        'PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED',
        name='interviewstatus', create_type=False
    )
    match_status_enum = postgresql.ENUM(
        'PENDING', 'SHORTLISTED', 'REJECTED', 'HIRED',
        name='matchstatus', create_type=False
    )
    followup_status_enum = postgresql.ENUM(
        'PENDING', 'ASKED', 'SKIPPED',
        name='followupqueuestatus', create_type=False
    )
    message_type_enum = postgresql.ENUM(
        'INTERVIEW_REQUEST', 'REJECTION', 'SHORTLIST_NOTICE', 'CUSTOM',
        name='messagetype', create_type=False
    )

    # Create enums (using DO block for IF NOT EXISTS compatibility)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE vertical AS ENUM ('new_energy', 'sales');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE roletype AS ENUM (
                'battery_engineer', 'embedded_software', 'autonomous_driving',
                'supply_chain', 'ev_sales', 'sales_rep', 'bd_manager', 'account_manager'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE interviewstatus AS ENUM ('PENDING', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE matchstatus AS ENUM ('PENDING', 'SHORTLISTED', 'REJECTED', 'HIRED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE followupqueuestatus AS ENUM ('PENDING', 'ASKED', 'SKIPPED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE messagetype AS ENUM ('INTERVIEW_REQUEST', 'REJECTION', 'SHORTLIST_NOTICE', 'CUSTOM');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Candidates table
    op.create_table('candidates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('wechat_openid', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('target_roles', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('resume_url', sa.String(), nullable=True),
        sa.Column('resume_raw_text', sa.Text(), nullable=True),
        sa.Column('resume_parsed_data', postgresql.JSONB(), nullable=True),
        sa.Column('resume_uploaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('wechat_openid')
    )
    op.create_index('ix_candidates_email', 'candidates', ['email'], unique=True)

    # Employers table
    op.create_table('employers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('logo', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('size', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_employers_email', 'employers', ['email'], unique=True)

    # Jobs table
    op.create_table('jobs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('vertical', vertical_enum, nullable=True),
        sa.Column('role_type', role_type_enum, nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('employer_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Interview questions table
    op.create_table('interview_questions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('text_zh', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('order', sa.Integer(), default=0),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('vertical', vertical_enum, nullable=True),
        sa.Column('role_type', role_type_enum, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Invite tokens table
    op.create_table('invite_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('max_uses', sa.Integer(), default=0),
        sa.Column('used_count', sa.Integer(), default=0),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )
    op.create_index('ix_invite_tokens_token', 'invite_tokens', ['token'], unique=True)

    # Interview sessions table
    op.create_table('interview_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('status', interview_status_enum, default='PENDING'),
        sa.Column('is_practice', sa.Boolean(), default=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('ai_summary', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Interview responses table
    op.create_table('interview_responses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.String(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('audio_url', sa.String(), nullable=True),
        sa.Column('transcription', sa.String(), nullable=True),
        sa.Column('ai_score', sa.Float(), nullable=True),
        sa.Column('ai_analysis', sa.String(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_followup', sa.Boolean(), default=False),
        sa.Column('parent_response_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['parent_response_id'], ['interview_responses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Follow-up queue table
    op.create_table('followup_queue',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('question_index', sa.Integer(), nullable=False),
        sa.Column('generated_questions', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('selected_index', sa.Integer(), nullable=True),
        sa.Column('status', followup_status_enum, default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['interview_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Matches table
    op.create_table('matches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('status', match_status_enum, default='PENDING'),
        sa.Column('ai_reasoning', sa.String(), nullable=True),
        sa.Column('interview_score', sa.Float(), nullable=True),
        sa.Column('skills_match_score', sa.Float(), nullable=True),
        sa.Column('experience_match_score', sa.Float(), nullable=True),
        sa.Column('location_match', sa.Boolean(), nullable=True),
        sa.Column('overall_match_score', sa.Float(), nullable=True),
        sa.Column('factors', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Messages table
    op.create_table('messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('message_type', message_type_enum, default='CUSTOM'),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('employer_id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('matches')
    op.drop_table('followup_queue')
    op.drop_table('interview_responses')
    op.drop_table('interview_sessions')
    op.drop_table('invite_tokens')
    op.drop_table('interview_questions')
    op.drop_table('jobs')
    op.drop_table('employers')
    op.drop_table('candidates')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS messagetype")
    op.execute("DROP TYPE IF EXISTS followupqueuestatus")
    op.execute("DROP TYPE IF EXISTS matchstatus")
    op.execute("DROP TYPE IF EXISTS interviewstatus")
    op.execute("DROP TYPE IF EXISTS roletype")
    op.execute("DROP TYPE IF EXISTS vertical")

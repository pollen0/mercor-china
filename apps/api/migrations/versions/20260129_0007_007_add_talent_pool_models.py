"""Add talent pool models: CandidateVerticalProfile and related columns

Revision ID: 007
Revises: 006
Create Date: 2026-01-29

This migration adds:
1. candidate_vertical_profiles table for talent pool model
2. vertical, role_type, is_vertical_interview columns to interview_sessions
3. vertical_profile_id column to matches (job_id already nullable)

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
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


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    conn = op.get_bind()
    result = conn.execute(sa.text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND column_name = '{column_name}'
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
    # Create Vertical enum if not exists
    if not enum_exists('vertical'):
        vertical_enum = postgresql.ENUM('new_energy', 'sales', name='vertical', create_type=False)
        vertical_enum.create(op.get_bind(), checkfirst=True)

    # Create RoleType enum if not exists
    if not enum_exists('roletype'):
        roletype_enum = postgresql.ENUM(
            'battery_engineer', 'embedded_software', 'autonomous_driving',
            'supply_chain', 'ev_sales', 'sales_rep', 'bd_manager', 'account_manager',
            name='roletype', create_type=False
        )
        roletype_enum.create(op.get_bind(), checkfirst=True)

    # Create VerticalProfileStatus enum if not exists
    if not enum_exists('verticalprofilestatus'):
        status_enum = postgresql.ENUM('pending', 'in_progress', 'completed', name='verticalprofilestatus', create_type=False)
        status_enum.create(op.get_bind(), checkfirst=True)

    # Create candidate_vertical_profiles table
    if not table_exists('candidate_vertical_profiles'):
        op.create_table(
            'candidate_vertical_profiles',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('candidate_id', sa.String(), nullable=False),
            sa.Column('vertical', postgresql.ENUM('new_energy', 'sales', name='vertical', create_type=False), nullable=False),
            sa.Column('role_type', postgresql.ENUM(
                'battery_engineer', 'embedded_software', 'autonomous_driving',
                'supply_chain', 'ev_sales', 'sales_rep', 'bd_manager', 'account_manager',
                name='roletype', create_type=False
            ), nullable=False),
            sa.Column('interview_session_id', sa.String(), nullable=True),
            sa.Column('interview_score', sa.Float(), nullable=True),
            sa.Column('best_score', sa.Float(), nullable=True),
            sa.Column('status', postgresql.ENUM('pending', 'in_progress', 'completed', name='verticalprofilestatus', create_type=False), server_default='pending'),
            sa.Column('attempt_count', sa.Integer(), server_default='0'),
            sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['interview_session_id'], ['interview_sessions.id'], ondelete='SET NULL'),
            sa.UniqueConstraint('candidate_id', 'vertical', name='uq_candidate_vertical')
        )
        op.create_index('ix_candidate_vertical_profiles_candidate_id', 'candidate_vertical_profiles', ['candidate_id'])
        op.create_index('ix_candidate_vertical_profiles_vertical', 'candidate_vertical_profiles', ['vertical'])
        op.create_index('ix_candidate_vertical_profiles_status', 'candidate_vertical_profiles', ['status'])

    # Add vertical interview columns to interview_sessions
    if not column_exists('interview_sessions', 'vertical'):
        op.add_column('interview_sessions', sa.Column(
            'vertical',
            postgresql.ENUM('new_energy', 'sales', name='vertical', create_type=False),
            nullable=True
        ))

    if not column_exists('interview_sessions', 'role_type'):
        op.add_column('interview_sessions', sa.Column(
            'role_type',
            postgresql.ENUM(
                'battery_engineer', 'embedded_software', 'autonomous_driving',
                'supply_chain', 'ev_sales', 'sales_rep', 'bd_manager', 'account_manager',
                name='roletype', create_type=False
            ),
            nullable=True
        ))

    if not column_exists('interview_sessions', 'is_vertical_interview'):
        op.add_column('interview_sessions', sa.Column(
            'is_vertical_interview',
            sa.Boolean(),
            server_default='false',
            nullable=False
        ))

    # Add vertical_profile_id to matches table
    if not column_exists('matches', 'vertical_profile_id'):
        op.add_column('matches', sa.Column('vertical_profile_id', sa.String(), nullable=True))
        op.create_foreign_key(
            'fk_matches_vertical_profile_id',
            'matches',
            'candidate_vertical_profiles',
            ['vertical_profile_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade() -> None:
    # Remove foreign key and column from matches
    if column_exists('matches', 'vertical_profile_id'):
        op.drop_constraint('fk_matches_vertical_profile_id', 'matches', type_='foreignkey')
        op.drop_column('matches', 'vertical_profile_id')

    # Remove columns from interview_sessions
    if column_exists('interview_sessions', 'is_vertical_interview'):
        op.drop_column('interview_sessions', 'is_vertical_interview')
    if column_exists('interview_sessions', 'role_type'):
        op.drop_column('interview_sessions', 'role_type')
    if column_exists('interview_sessions', 'vertical'):
        op.drop_column('interview_sessions', 'vertical')

    # Drop candidate_vertical_profiles table
    if table_exists('candidate_vertical_profiles'):
        op.drop_index('ix_candidate_vertical_profiles_status')
        op.drop_index('ix_candidate_vertical_profiles_vertical')
        op.drop_index('ix_candidate_vertical_profiles_candidate_id')
        op.drop_table('candidate_vertical_profiles')

    # Note: We don't drop the enums as they might be used elsewhere

"""Add organizations and team collaboration tables

Revision ID: 020
Revises: 019
Create Date: 2026-02-02

This migration adds:
- organizations table: Company entities for team collaboration
- organization_members table: Links employers to organizations with roles
- organization_invites table: Pending team invites
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM, JSONB


# revision identifiers, used by Alembic.
revision: str = '020'
down_revision: Union[str, None] = '019a'
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
    # Create organization_role enum
    if not enum_exists('organizationrole'):
        organization_role = ENUM(
            'owner', 'admin', 'recruiter', 'hiring_manager', 'interviewer',
            name='organizationrole',
            create_type=True
        )
        organization_role.create(op.get_bind(), checkfirst=True)

    # Create invite_status enum
    if not enum_exists('invitestatus'):
        invite_status = ENUM(
            'pending', 'accepted', 'expired', 'cancelled',
            name='invitestatus',
            create_type=True
        )
        invite_status.create(op.get_bind(), checkfirst=True)

    # Create organizations table
    if not table_exists('organizations'):
        op.create_table(
            'organizations',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('slug', sa.String(), nullable=False),
            sa.Column('logo_url', sa.String(), nullable=True),
            sa.Column('website', sa.String(), nullable=True),
            sa.Column('industry', sa.String(), nullable=True),
            sa.Column('company_size', sa.String(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('settings', JSONB(), nullable=True),
            sa.Column('plan', sa.String(), server_default='free', nullable=True),
            sa.Column('plan_expires_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('slug'),
        )
        op.create_index('ix_organizations_slug', 'organizations', ['slug'])

    # Create organization_members table
    if not table_exists('organization_members'):
        op.create_table(
            'organization_members',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('organization_id', sa.String(), nullable=False),
            sa.Column('employer_id', sa.String(), nullable=False),
            sa.Column('role', ENUM('owner', 'admin', 'recruiter', 'hiring_manager', 'interviewer', name='organizationrole', create_type=False), nullable=True),
            sa.Column('permissions', JSONB(), nullable=True),
            sa.Column('invited_by_id', sa.String(), nullable=True),
            sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['employer_id'], ['employers.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['invited_by_id'], ['employers.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_organization_members_organization_id', 'organization_members', ['organization_id'])
        op.create_index('ix_organization_members_employer_id', 'organization_members', ['employer_id'])
        # Unique constraint: one membership per employer per organization
        op.create_unique_constraint('uq_org_member', 'organization_members', ['organization_id', 'employer_id'])

    # Create organization_invites table
    if not table_exists('organization_invites'):
        op.create_table(
            'organization_invites',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('organization_id', sa.String(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('role', ENUM('owner', 'admin', 'recruiter', 'hiring_manager', 'interviewer', name='organizationrole', create_type=False), nullable=True),
            sa.Column('token', sa.String(), nullable=False),
            sa.Column('status', ENUM('pending', 'accepted', 'expired', 'cancelled', name='invitestatus', create_type=False), nullable=True),
            sa.Column('invited_by_id', sa.String(), nullable=True),
            sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['invited_by_id'], ['employers.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('token'),
        )
        op.create_index('ix_organization_invites_token', 'organization_invites', ['token'])
        op.create_index('ix_organization_invites_email', 'organization_invites', ['email'])


def downgrade() -> None:
    # Drop tables
    op.drop_table('organization_invites')
    op.drop_table('organization_members')
    op.drop_table('organizations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS invitestatus')
    op.execute('DROP TYPE IF EXISTS organizationrole')

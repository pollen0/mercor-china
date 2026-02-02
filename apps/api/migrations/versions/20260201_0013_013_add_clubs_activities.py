"""Add clubs, activities, and awards tables

Revision ID: 013
Revises: 012
Create Date: 2026-02-01

Adds support for:
- University clubs with prestige rankings
- Candidate activity/club memberships
- Candidate awards/achievements
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create clubs table
    op.create_table(
        'clubs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('university_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('short_name', sa.String(), nullable=True),
        sa.Column('category', sa.String(), default='other'),
        sa.Column('aliases', JSONB(), nullable=True),
        sa.Column('prestige_tier', sa.Integer(), nullable=False, default=2),
        sa.Column('prestige_score', sa.Float(), nullable=False, default=5.0),
        sa.Column('is_selective', sa.Boolean(), default=False),
        sa.Column('acceptance_rate', sa.Float(), nullable=True),
        sa.Column('typical_members', sa.Integer(), nullable=True),
        sa.Column('leadership_bonus', sa.Float(), default=1.0),
        sa.Column('is_technical', sa.Boolean(), default=False),
        sa.Column('is_professional', sa.Boolean(), default=False),
        sa.Column('has_projects', sa.Boolean(), default=False),
        sa.Column('has_competitions', sa.Boolean(), default=False),
        sa.Column('has_corporate_sponsors', sa.Boolean(), default=False),
        sa.Column('is_honor_society', sa.Boolean(), default=False),
        sa.Column('relevant_to', JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), default=1.0),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clubs_university', 'clubs', ['university_id'])
    op.create_index('ix_clubs_category', 'clubs', ['category'])
    op.create_index('ix_clubs_prestige', 'clubs', ['prestige_tier', 'prestige_score'])

    # Create candidate_activities table
    op.create_table(
        'candidate_activities',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('club_id', sa.String(), nullable=True),
        sa.Column('activity_name', sa.String(), nullable=False),
        sa.Column('organization', sa.String(), nullable=True),
        sa.Column('institution', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('role_tier', sa.Integer(), default=1),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.String(), nullable=True),
        sa.Column('end_date', sa.String(), nullable=True),
        sa.Column('duration_semesters', sa.Integer(), nullable=True),
        sa.Column('achievements', JSONB(), nullable=True),
        sa.Column('activity_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_candidate_activities_candidate', 'candidate_activities', ['candidate_id'])

    # Create candidate_awards table
    op.create_table(
        'candidate_awards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('issuer', sa.String(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('award_type', sa.String(), nullable=True),
        sa.Column('prestige_tier', sa.Integer(), default=2),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_candidate_awards_candidate', 'candidate_awards', ['candidate_id'])


def downgrade() -> None:
    op.drop_index('ix_candidate_awards_candidate', table_name='candidate_awards')
    op.drop_table('candidate_awards')

    op.drop_index('ix_candidate_activities_candidate', table_name='candidate_activities')
    op.drop_table('candidate_activities')

    op.drop_index('ix_clubs_prestige', table_name='clubs')
    op.drop_index('ix_clubs_category', table_name='clubs')
    op.drop_index('ix_clubs_university', table_name='clubs')
    op.drop_table('clubs')

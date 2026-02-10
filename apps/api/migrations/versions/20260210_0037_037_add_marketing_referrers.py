"""Add marketing referrers table for external referral tracking.

Revision ID: 037_add_marketing_referrers
Revises: 036_add_growth_tracking
Create Date: 2026-02-10

Marketing referrers are external people (marketing interns, campus ambassadors)
who don't have platform accounts but get referral codes to track their signups.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '037'
down_revision = '036'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create marketing_referrers table
    op.create_table(
        'marketing_referrers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('referral_code', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('referral_code')
    )
    op.create_index('ix_marketing_referrers_referral_code', 'marketing_referrers', ['referral_code'])

    # Add marketing_referrer_id to candidates
    op.add_column('candidates', sa.Column('marketing_referrer_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_candidates_marketing_referrer_id',
        'candidates', 'marketing_referrers',
        ['marketing_referrer_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_candidates_marketing_referrer_id', 'candidates', ['marketing_referrer_id'])


def downgrade() -> None:
    # Remove foreign key and column from candidates
    op.drop_index('ix_candidates_marketing_referrer_id', table_name='candidates')
    op.drop_constraint('fk_candidates_marketing_referrer_id', 'candidates', type_='foreignkey')
    op.drop_column('candidates', 'marketing_referrer_id')

    # Drop marketing_referrers table
    op.drop_index('ix_marketing_referrers_referral_code', table_name='marketing_referrers')
    op.drop_table('marketing_referrers')

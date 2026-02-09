"""Add referral system

Revision ID: 035
Revises: 034
Create Date: 2026-02-09

Adds support for:
- Candidate referral codes (unique per candidate)
- Referred-by tracking on candidates
- Referrals table to track referral status and conversions

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '035'
down_revision = '034'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add referral columns to candidates
    op.add_column('candidates', sa.Column('referral_code', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('referred_by_id', sa.String(), nullable=True))
    op.create_unique_constraint('uq_candidates_referral_code', 'candidates', ['referral_code'])
    op.create_foreign_key(
        'fk_candidates_referred_by_id',
        'candidates', 'candidates',
        ['referred_by_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create referrals table
    op.create_table(
        'referrals',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('referrer_id', sa.String(), nullable=False),
        sa.Column('referee_id', sa.String(), nullable=True),
        sa.Column('referee_email', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['referrer_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['referee_id'], ['candidates.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_referrals_referrer_id', 'referrals', ['referrer_id'])
    op.create_index('ix_referrals_referee_id', 'referrals', ['referee_id'])
    op.create_index('ix_referrals_status', 'referrals', ['status'])


def downgrade() -> None:
    op.drop_index('ix_referrals_status', 'referrals')
    op.drop_index('ix_referrals_referee_id', 'referrals')
    op.drop_index('ix_referrals_referrer_id', 'referrals')
    op.drop_table('referrals')
    op.drop_constraint('fk_candidates_referred_by_id', 'candidates', type_='foreignkey')
    op.drop_constraint('uq_candidates_referral_code', 'candidates', type_='unique')
    op.drop_column('candidates', 'referred_by_id')
    op.drop_column('candidates', 'referral_code')

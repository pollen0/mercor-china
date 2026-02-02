"""Add double major, minors, and transfer student support

Revision ID: 012
Revises: 011
Create Date: 2026-02-01

Adds support for:
- Double/triple majors (majors array)
- Minors
- Certificates/concentrations
- Transfer student tracking
- AP credits
- Major-specific GPA

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add majors array for double/triple majors
    op.add_column('candidates', sa.Column('majors', JSONB(), nullable=True))

    # Add minors array
    op.add_column('candidates', sa.Column('minors', JSONB(), nullable=True))

    # Add certificates/concentrations array
    op.add_column('candidates', sa.Column('certificates', JSONB(), nullable=True))

    # Add major-specific GPA
    op.add_column('candidates', sa.Column('major_gpa', sa.Float(), nullable=True))

    # Add transfer student fields
    op.add_column('candidates', sa.Column('is_transfer', sa.Boolean(), default=False))
    op.add_column('candidates', sa.Column('transfer_university', sa.String(), nullable=True))
    op.add_column('candidates', sa.Column('transfer_units', sa.Integer(), nullable=True))

    # Add AP credits tracking
    op.add_column('candidates', sa.Column('ap_credits', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('candidates', 'ap_credits')
    op.drop_column('candidates', 'transfer_units')
    op.drop_column('candidates', 'transfer_university')
    op.drop_column('candidates', 'is_transfer')
    op.drop_column('candidates', 'major_gpa')
    op.drop_column('candidates', 'certificates')
    op.drop_column('candidates', 'minors')
    op.drop_column('candidates', 'majors')

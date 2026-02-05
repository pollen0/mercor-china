"""Change additional_attendees column from JSON to JSONB

Revision ID: 028
Revises: 027
Create Date: 2026-02-04

JSONB supports containment operators (@>) needed for .contains() queries.
Plain JSON type does not support these operators, causing 'operator does not exist: json ~~ text' errors.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '028'
down_revision: Union[str, None] = '027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE scheduled_interviews
        ALTER COLUMN additional_attendees
        SET DATA TYPE jsonb
        USING additional_attendees::jsonb
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE scheduled_interviews
        ALTER COLUMN additional_attendees
        SET DATA TYPE json
        USING additional_attendees::json
    """)

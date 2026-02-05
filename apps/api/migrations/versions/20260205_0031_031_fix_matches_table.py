"""Fix matches table: nullable job_id, add vertical_profile_id, update MatchStatus enum

Revision ID: 031
Revises: 030
Create Date: 2026-02-05

Fixes mismatch between migration 001 (job_id NOT NULL, CASCADE) and the model
(job_id nullable, SET NULL). Also adds vertical_profile_id FK and new
MatchStatus enum values (CONTACTED, IN_REVIEW, WATCHLIST) for talent pool model.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '031'
down_revision: Union[str, None] = '030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
        "WHERE table_name = :table AND column_name = :col)"
    ), {"table": table_name, "col": column_name})
    return result.scalar()


def enum_value_exists(enum_name: str, value: str) -> bool:
    """Check if an enum value exists."""
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid "
        "WHERE t.typname = :enum AND e.enumlabel = :val)"
    ), {"enum": enum_name, "val": value})
    return result.scalar()


def upgrade() -> None:
    # 1. Make matches.job_id nullable (was NOT NULL in migration 001)
    op.alter_column('matches', 'job_id',
                    existing_type=sa.String(),
                    nullable=True)

    # 2. Drop the old CASCADE FK constraint and recreate with SET NULL
    # First find and drop the existing FK constraint
    op.execute("""
        DO $$
        DECLARE
            fk_name TEXT;
        BEGIN
            SELECT tc.constraint_name INTO fk_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'matches'
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'job_id';

            IF fk_name IS NOT NULL THEN
                EXECUTE 'ALTER TABLE matches DROP CONSTRAINT ' || fk_name;
            END IF;
        END $$;
    """)

    # Recreate with SET NULL
    op.create_foreign_key(
        'fk_matches_job_id',
        'matches', 'jobs',
        ['job_id'], ['id'],
        ondelete='SET NULL'
    )

    # 3. Add vertical_profile_id column if not exists
    if not column_exists('matches', 'vertical_profile_id'):
        op.add_column('matches', sa.Column(
            'vertical_profile_id', sa.String(), nullable=True
        ))
        op.create_foreign_key(
            'fk_matches_vertical_profile_id',
            'matches', 'candidate_vertical_profiles',
            ['vertical_profile_id'], ['id'],
            ondelete='SET NULL'
        )

    # 4. Add new MatchStatus enum values for talent pool model
    for value in ['CONTACTED', 'IN_REVIEW', 'WATCHLIST']:
        if not enum_value_exists('matchstatus', value):
            op.execute(f"ALTER TYPE matchstatus ADD VALUE IF NOT EXISTS '{value}'")


def downgrade() -> None:
    # Remove vertical_profile_id
    if column_exists('matches', 'vertical_profile_id'):
        op.drop_constraint('fk_matches_vertical_profile_id', 'matches', type_='foreignkey')
        op.drop_column('matches', 'vertical_profile_id')

    # Restore job_id FK to CASCADE
    op.execute("""
        DO $$
        DECLARE
            fk_name TEXT;
        BEGIN
            SELECT tc.constraint_name INTO fk_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'matches'
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'job_id';

            IF fk_name IS NOT NULL THEN
                EXECUTE 'ALTER TABLE matches DROP CONSTRAINT ' || fk_name;
            END IF;
        END $$;
    """)
    op.create_foreign_key(
        'fk_matches_job_id',
        'matches', 'jobs',
        ['job_id'], ['id'],
        ondelete='CASCADE'
    )

    # Revert job_id to NOT NULL (will fail if NULLs exist)
    op.alter_column('matches', 'job_id',
                    existing_type=sa.String(),
                    nullable=False)

    # Note: Cannot remove enum values in PostgreSQL, leaving CONTACTED/IN_REVIEW/WATCHLIST

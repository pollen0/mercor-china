"""Normalize enum data from uppercase to lowercase

Revision ID: 026
Revises: 025
Create Date: 2026-02-04

This migration updates data to use lowercase enum values.
Migration 025 added the enum values; this one updates the data.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '026'
down_revision: Union[str, None] = '025'
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


def upgrade() -> None:
    # ============================================
    # NORMALIZE VERTICAL VALUES
    # ============================================
    vertical_tables = [
        'jobs', 'candidate_vertical_profiles', 'interview_sessions',
        'interview_questions', 'candidate_question_history'
    ]

    vertical_mappings = [
        ('SOFTWARE_ENGINEERING', 'software_engineering'),
        ('DATA', 'data'),
        ('PRODUCT', 'product'),
        ('DESIGN', 'design'),
        ('FINANCE', 'finance'),
    ]

    for table in vertical_tables:
        if table_exists(table) and column_exists(table, 'vertical'):
            for old_val, new_val in vertical_mappings:
                # Cast to text for comparison to handle values not in enum
                op.execute(f"UPDATE {table} SET vertical = '{new_val}' WHERE vertical::text = '{old_val}'")

    # ============================================
    # NORMALIZE ROLE_TYPE VALUES
    # ============================================
    role_type_tables = ['jobs', 'candidate_vertical_profiles', 'interview_sessions']

    role_type_mappings = [
        ('SOFTWARE_ENGINEER', 'software_engineer'),
        ('EMBEDDED_ENGINEER', 'embedded_engineer'),
        ('QA_ENGINEER', 'qa_engineer'),
        ('DATA_ANALYST', 'data_analyst'),
        ('DATA_SCIENTIST', 'data_scientist'),
        ('ML_ENGINEER', 'ml_engineer'),
        ('DATA_ENGINEER', 'data_engineer'),
        ('PRODUCT_MANAGER', 'product_manager'),
        ('ASSOCIATE_PM', 'associate_pm'),
        ('UX_DESIGNER', 'ux_designer'),
        ('UI_DESIGNER', 'ui_designer'),
        ('PRODUCT_DESIGNER', 'product_designer'),
        ('IB_ANALYST', 'ib_analyst'),
        ('FINANCE_ANALYST', 'finance_analyst'),
        ('EQUITY_RESEARCH', 'equity_research'),
    ]

    for table in role_type_tables:
        if table_exists(table) and column_exists(table, 'role_type'):
            for old_val, new_val in role_type_mappings:
                # Cast to text for comparison to handle values not in enum
                op.execute(f"UPDATE {table} SET role_type = '{new_val}' WHERE role_type::text = '{old_val}'")


def downgrade() -> None:
    # Data migration is not reversible
    pass

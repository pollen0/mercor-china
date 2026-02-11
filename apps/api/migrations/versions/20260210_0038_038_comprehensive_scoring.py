"""Comprehensive scoring system with majors table and profile scores.

Revision ID: 038
Revises: 037
Create Date: 2026-02-10

Changes:
1. Update university tiers from 1-2 to 1-5 based on CS ranking
2. Create majors table with rigor ratings and average GPA
3. Create candidate_profile_scores table for persistent scoring with rationale
4. Add university_id FK to candidates for direct linking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '038'
down_revision = '037'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create majors table (university_id nullable for generic majors)
    op.create_table(
        'majors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('university_id', sa.String(), nullable=True),  # Nullable for generic majors
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('short_name', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('rigor_tier', sa.Integer(), server_default='3', nullable=False),
        sa.Column('rigor_score', sa.Float(), server_default='5.0', nullable=False),
        sa.Column('average_gpa', sa.Float(), nullable=True),
        sa.Column('median_gpa', sa.Float(), nullable=True),
        sa.Column('gpa_std_dev', sa.Float(), nullable=True),
        sa.Column('is_stem', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_technical', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('field_category', sa.String(), nullable=True),
        sa.Column('relevant_to', JSONB(), nullable=True),
        sa.Column('aliases', JSONB(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['university_id'], ['universities.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_majors_university_id', 'majors', ['university_id'])
    op.create_index('ix_majors_field_category', 'majors', ['field_category'])

    # 2. Create candidate_profile_scores table
    op.create_table(
        'candidate_profile_scores',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=True),
        sa.Column('education_score', sa.Float(), nullable=True),
        sa.Column('technical_score', sa.Float(), nullable=True),
        sa.Column('experience_score', sa.Float(), nullable=True),
        sa.Column('github_score', sa.Float(), nullable=True),
        sa.Column('activities_score', sa.Float(), nullable=True),
        sa.Column('education_breakdown', JSONB(), nullable=True),
        sa.Column('technical_breakdown', JSONB(), nullable=True),
        sa.Column('experience_breakdown', JSONB(), nullable=True),
        sa.Column('github_breakdown', JSONB(), nullable=True),
        sa.Column('activities_breakdown', JSONB(), nullable=True),
        sa.Column('scoring_version', sa.String(), nullable=True),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('raw_inputs', JSONB(), nullable=True),
        sa.Column('computation_log', JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('candidate_id'),
    )
    op.create_index('ix_candidate_profile_scores_candidate_id', 'candidate_profile_scores', ['candidate_id'])
    op.create_index('ix_candidate_profile_scores_total_score', 'candidate_profile_scores', ['total_score'])

    # 3. Add university_id FK to candidates (for direct linking)
    op.add_column('candidates', sa.Column('university_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_candidates_university_id',
        'candidates', 'universities',
        ['university_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_candidates_university_id', 'candidates', ['university_id'])

    # 4. Add major_id FK to candidates
    op.add_column('candidates', sa.Column('major_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_candidates_major_id',
        'candidates', 'majors',
        ['major_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_candidates_major_id', 'candidates', ['major_id'])

    # 5. Update university tiers based on CS ranking (1-5 scale)
    op.execute("""
        UPDATE universities SET tier =
            CASE
                WHEN cs_ranking IS NOT NULL AND cs_ranking <= 10 THEN 1
                WHEN cs_ranking IS NOT NULL AND cs_ranking <= 25 THEN 2
                WHEN cs_ranking IS NOT NULL AND cs_ranking <= 50 THEN 3
                WHEN cs_ranking IS NOT NULL AND cs_ranking <= 75 THEN 4
                WHEN cs_ranking IS NOT NULL THEN 5
                ELSE 3
            END
    """)

    # 6. Seed majors table with initial data
    from app.data.seed_majors import get_majors_for_seeding
    import json

    majors = get_majors_for_seeding()
    for major in majors:
        # Build INSERT statement
        aliases_json = json.dumps(major.get('aliases', [])) if major.get('aliases') else None
        relevant_to_json = json.dumps(major.get('relevant_to', [])) if major.get('relevant_to') else None

        op.execute(f"""
            INSERT INTO majors (
                id, university_id, name, short_name, department,
                rigor_tier, rigor_score, average_gpa, is_stem, is_technical,
                field_category, relevant_to, aliases, source, source_url
            ) VALUES (
                '{major['id']}',
                {f"'{major['university_id']}'" if major.get('university_id') else 'NULL'},
                '{major['name'].replace("'", "''")}',
                {f"'{major.get('short_name', '')}'" if major.get('short_name') else 'NULL'},
                {f"'{major.get('department', '')}'" if major.get('department') else 'NULL'},
                {major.get('rigor_tier', 3)},
                {major.get('rigor_score', 5.0)},
                {major.get('average_gpa') if major.get('average_gpa') else 'NULL'},
                {str(major.get('is_stem', False)).lower()},
                {str(major.get('is_technical', False)).lower()},
                {f"'{major.get('field_category', '')}'" if major.get('field_category') else 'NULL'},
                {f"'{relevant_to_json}'::jsonb" if relevant_to_json else 'NULL'},
                {f"'{aliases_json}'::jsonb" if aliases_json else 'NULL'},
                {f"'{major.get('source', '')}'" if major.get('source') else 'NULL'},
                {f"'{major.get('source_url', '')}'" if major.get('source_url') else 'NULL'}
            ) ON CONFLICT (id) DO NOTHING
        """)


def downgrade() -> None:
    # Remove candidate FKs
    op.drop_index('ix_candidates_major_id', table_name='candidates')
    op.drop_constraint('fk_candidates_major_id', 'candidates', type_='foreignkey')
    op.drop_column('candidates', 'major_id')

    op.drop_index('ix_candidates_university_id', table_name='candidates')
    op.drop_constraint('fk_candidates_university_id', 'candidates', type_='foreignkey')
    op.drop_column('candidates', 'university_id')

    # Drop candidate_profile_scores
    op.drop_index('ix_candidate_profile_scores_total_score', table_name='candidate_profile_scores')
    op.drop_index('ix_candidate_profile_scores_candidate_id', table_name='candidate_profile_scores')
    op.drop_table('candidate_profile_scores')

    # Drop majors
    op.drop_index('ix_majors_field_category', table_name='majors')
    op.drop_index('ix_majors_university_id', table_name='majors')
    op.drop_table('majors')

    # Revert university tiers to 1-2
    op.execute("""
        UPDATE universities SET tier =
            CASE
                WHEN cs_ranking IS NOT NULL AND cs_ranking <= 20 THEN 1
                ELSE 2
            END
    """)

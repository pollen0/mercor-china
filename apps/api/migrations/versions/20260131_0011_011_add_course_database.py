"""Add course database and transcript analysis tables

Revision ID: 011
Revises: 010
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create universities table
    op.create_table(
        'universities',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('short_name', sa.String(), nullable=False),
        sa.Column('course_pattern', sa.String(), nullable=True),
        sa.Column('gpa_scale', sa.Float(), default=4.0),
        sa.Column('uses_plus_minus', sa.Boolean(), default=True),
        sa.Column('tier', sa.Integer(), default=1),
        sa.Column('cs_ranking', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create courses table
    op.create_table(
        'courses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('university_id', sa.String(), nullable=False),
        sa.Column('department', sa.String(), nullable=False),
        sa.Column('number', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('aliases', JSONB(), nullable=True),
        sa.Column('difficulty_tier', sa.Integer(), nullable=False, default=2),
        sa.Column('difficulty_score', sa.Float(), nullable=False, default=5.0),
        sa.Column('typical_gpa', sa.Float(), nullable=True),
        sa.Column('is_curved', sa.Boolean(), default=False),
        sa.Column('curve_type', sa.String(), nullable=True),
        sa.Column('course_type', sa.String(), default='core'),
        sa.Column('is_technical', sa.Boolean(), default=True),
        sa.Column('is_weeder', sa.Boolean(), default=False),
        sa.Column('is_proof_based', sa.Boolean(), default=False),
        sa.Column('has_heavy_projects', sa.Boolean(), default=False),
        sa.Column('has_coding', sa.Boolean(), default=False),
        sa.Column('units', sa.Integer(), default=3),
        sa.Column('prerequisites', JSONB(), nullable=True),
        sa.Column('relevant_to', JSONB(), nullable=True),
        sa.Column('equivalents', JSONB(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), default=1.0),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_courses_university_dept', 'courses', ['university_id', 'department'])
    op.create_index('ix_courses_difficulty', 'courses', ['difficulty_tier', 'difficulty_score'])

    # Create course_grade_mappings table
    op.create_table(
        'course_grade_mappings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('university_id', sa.String(), nullable=True),
        sa.Column('grade', sa.String(), nullable=False),
        sa.Column('gpa_value', sa.Float(), nullable=False),
        sa.Column('percentile_estimate', sa.Float(), nullable=True),
        sa.Column('is_passing', sa.Boolean(), default=True),
        sa.Column('is_credit_only', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create candidate_transcripts table
    op.create_table(
        'candidate_transcripts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('file_url', sa.String(), nullable=True),
        sa.Column('university_id', sa.String(), nullable=True),
        sa.Column('is_official', sa.Boolean(), default=False),
        sa.Column('parsed_courses', JSONB(), nullable=True),
        sa.Column('cumulative_gpa', sa.Float(), nullable=True),
        sa.Column('major_gpa', sa.Float(), nullable=True),
        sa.Column('transcript_score', sa.Float(), nullable=True),
        sa.Column('course_rigor_score', sa.Float(), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('trajectory_score', sa.Float(), nullable=True),
        sa.Column('load_score', sa.Float(), nullable=True),
        sa.Column('score_breakdown', JSONB(), nullable=True),
        sa.Column('flags', JSONB(), nullable=True),
        sa.Column('requires_review', sa.Boolean(), default=False),
        sa.Column('semesters_analyzed', sa.Integer(), default=0),
        sa.Column('total_units', sa.Integer(), default=0),
        sa.Column('technical_units', sa.Integer(), default=0),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('candidate_id', name='uq_candidate_transcript')
    )
    op.create_index('ix_candidate_transcripts_candidate', 'candidate_transcripts', ['candidate_id'])

    # Create candidate_course_grades table
    op.create_table(
        'candidate_course_grades',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('candidate_id', sa.String(), nullable=False),
        sa.Column('transcript_id', sa.String(), nullable=False),
        sa.Column('course_id', sa.String(), nullable=True),
        sa.Column('course_code', sa.String(), nullable=False),
        sa.Column('course_name', sa.String(), nullable=True),
        sa.Column('grade', sa.String(), nullable=False),
        sa.Column('gpa_value', sa.Float(), nullable=True),
        sa.Column('units', sa.Integer(), default=3),
        sa.Column('semester', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('student_year', sa.Integer(), nullable=True),
        sa.Column('difficulty_at_time', sa.Float(), nullable=True),
        sa.Column('performance_percentile', sa.Float(), nullable=True),
        sa.Column('is_retake', sa.Boolean(), default=False),
        sa.Column('is_transfer', sa.Boolean(), default=False),
        sa.Column('is_ap', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidate_courses_candidate', 'candidate_course_grades', ['candidate_id'])
    op.create_index('ix_candidate_courses_course', 'candidate_course_grades', ['course_id'])


def downgrade() -> None:
    op.drop_index('ix_candidate_courses_course', table_name='candidate_course_grades')
    op.drop_index('ix_candidate_courses_candidate', table_name='candidate_course_grades')
    op.drop_table('candidate_course_grades')

    op.drop_index('ix_candidate_transcripts_candidate', table_name='candidate_transcripts')
    op.drop_table('candidate_transcripts')

    op.drop_table('course_grade_mappings')

    op.drop_index('ix_courses_difficulty', table_name='courses')
    op.drop_index('ix_courses_university_dept', table_name='courses')
    op.drop_table('courses')

    op.drop_table('universities')

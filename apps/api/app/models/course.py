"""
Course difficulty database for academic transcript analysis.
Stores courses from various universities with difficulty ratings and metadata.
"""

from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Text, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base
import enum


class DifficultyTier(int, enum.Enum):
    """Course difficulty tiers (1-5 scale)."""
    INTRODUCTORY = 1      # No prior experience needed (Data 8, CS 101)
    FOUNDATIONAL = 2      # Builds on intro, moderate (CS 61B, CS 225)
    CHALLENGING = 3       # Known difficult courses (CS 61C, CS 70, CS 173)
    VERY_CHALLENGING = 4  # Heavy workload + conceptual (CS 170, CS 374, EECS 16B)
    ELITE = 5             # Hardest in curriculum (CS 189, CS 162, ECE 391)


class CourseType(str, enum.Enum):
    """Type of course."""
    CORE = "core"                    # Required for major
    ELECTIVE = "elective"            # Optional for major
    BREADTH = "breadth"              # General education
    MATH_PREREQ = "math_prereq"      # Math prerequisites
    RESEARCH = "research"            # Independent study/research
    CAPSTONE = "capstone"            # Senior project/capstone


class University(Base):
    """
    University metadata for course lookups.
    Helps normalize course data across schools.
    """
    __tablename__ = "universities"

    id = Column(String, primary_key=True)  # e.g., "berkeley", "uiuc", "stanford"
    name = Column(String, nullable=False)  # e.g., "University of California, Berkeley"
    short_name = Column(String, nullable=False)  # e.g., "UC Berkeley"

    # Course numbering patterns (regex) for parsing
    course_pattern = Column(String, nullable=True)  # e.g., r"([A-Z]{2,})\s*(\d+[A-Z]?)"

    # Grading scale info
    gpa_scale = Column(Float, default=4.0)  # 4.0, 4.3, etc.
    uses_plus_minus = Column(Boolean, default=True)

    # Metadata
    tier = Column(Integer, default=1)  # University prestige tier (1=top, 2=great, 3=good)
    cs_ranking = Column(Integer, nullable=True)  # US News CS ranking

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Course(Base):
    """
    Individual course with difficulty rating and metadata.
    Used for transcript analysis and scoring.
    """
    __tablename__ = "courses"

    id = Column(String, primary_key=True)  # e.g., "berkeley_cs61a", "uiuc_cs225"
    university_id = Column(String, nullable=False)  # e.g., "berkeley"

    # Course identification
    department = Column(String, nullable=False)  # e.g., "CS", "EECS", "DATA", "MATH"
    number = Column(String, nullable=False)  # e.g., "61A", "225", "C100"
    name = Column(String, nullable=False)  # e.g., "Structure and Interpretation of Computer Programs"

    # Aliases for fuzzy matching (handles different formats)
    aliases = Column(JSONB, nullable=True)  # ["COMPSCI 61A", "CS 61A", "CompSci61A"]

    # Difficulty rating
    difficulty_tier = Column(Integer, nullable=False, default=2)  # 1-5 scale
    difficulty_score = Column(Float, nullable=False, default=5.0)  # 0-10 fine-grained score

    # Grading info
    typical_gpa = Column(Float, nullable=True)  # Average class GPA (e.g., 3.0)
    is_curved = Column(Boolean, default=False)
    curve_type = Column(String, nullable=True)  # "standard", "generous", "strict"

    # Course characteristics
    course_type = Column(String, default="core")  # core, elective, breadth, etc.
    is_technical = Column(Boolean, default=True)
    is_weeder = Column(Boolean, default=False)  # Known "weeder" course
    is_proof_based = Column(Boolean, default=False)
    has_heavy_projects = Column(Boolean, default=False)
    has_coding = Column(Boolean, default=False)

    # Units/Credits
    units = Column(Integer, default=3)

    # Prerequisites (course IDs)
    prerequisites = Column(JSONB, nullable=True)  # ["berkeley_cs61a", "berkeley_math54"]

    # Relevance to fields
    relevant_to = Column(JSONB, nullable=True)  # ["software_engineering", "machine_learning", "data_science"]

    # Equivalent courses at other schools
    equivalents = Column(JSONB, nullable=True)  # {"uiuc": "cs225", "stanford": "cs106b"}

    # Additional context
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Admin notes about the course

    # Data quality
    confidence = Column(Float, default=1.0)  # How confident we are in the rating (0-1)
    source = Column(String, nullable=True)  # "manual", "research", "ai_estimated"
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for efficient lookups
    __table_args__ = (
        Index('ix_courses_university_dept', 'university_id', 'department'),
        Index('ix_courses_difficulty', 'difficulty_tier', 'difficulty_score'),
    )


class CourseGradeMapping(Base):
    """
    Maps letter grades to numeric values for different grading scales.
    Handles variations like A+, A, A-, etc.
    """
    __tablename__ = "course_grade_mappings"

    id = Column(String, primary_key=True)
    university_id = Column(String, nullable=True)  # Null for default/universal

    grade = Column(String, nullable=False)  # "A+", "A", "A-", "B+", etc.
    gpa_value = Column(Float, nullable=False)  # 4.0, 3.7, 3.3, etc.
    percentile_estimate = Column(Float, nullable=True)  # Estimated class percentile

    # For pass/fail or other non-standard grades
    is_passing = Column(Boolean, default=True)
    is_credit_only = Column(Boolean, default=False)  # P/NP, CR/NC, S/U

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============= Candidate Transcript Data =============

class CandidateTranscript(Base):
    """
    Stores parsed transcript data for a candidate.
    Links to their courses and grades for scoring.
    """
    __tablename__ = "candidate_transcripts"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, nullable=False, unique=True)  # One transcript per candidate

    # Source info
    file_url = Column(String, nullable=True)  # R2 URL of uploaded transcript
    university_id = Column(String, nullable=True)  # Detected/confirmed university
    is_official = Column(Boolean, default=False)  # Official vs unofficial

    # Parsed data
    parsed_courses = Column(JSONB, nullable=True)  # List of {course_id, grade, semester, units}
    cumulative_gpa = Column(Float, nullable=True)  # Extracted or calculated
    major_gpa = Column(Float, nullable=True)  # CS/technical courses only

    # Computed scores (cached)
    transcript_score = Column(Float, nullable=True)  # Overall 0-100
    course_rigor_score = Column(Float, nullable=True)  # How hard were the courses
    performance_score = Column(Float, nullable=True)  # How well did they do
    trajectory_score = Column(Float, nullable=True)  # Are grades improving
    load_score = Column(Float, nullable=True)  # Units per semester

    # Detailed breakdown (for display)
    score_breakdown = Column(JSONB, nullable=True)  # Detailed scoring components

    # Flags
    flags = Column(JSONB, nullable=True)  # Notable patterns (good or concerning)
    requires_review = Column(Boolean, default=False)  # Needs manual review

    # Metadata
    semesters_analyzed = Column(Integer, default=0)
    total_units = Column(Integer, default=0)
    technical_units = Column(Integer, default=0)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CandidateCourseGrade(Base):
    """
    Individual course grade for a candidate.
    Allows detailed analysis of course history.
    """
    __tablename__ = "candidate_course_grades"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, nullable=False)
    transcript_id = Column(String, nullable=False)

    # Course info
    course_id = Column(String, nullable=True)  # FK to courses table (if known)
    course_code = Column(String, nullable=False)  # Raw code from transcript (e.g., "CS 61A")
    course_name = Column(String, nullable=True)  # Name if available

    # Grade info
    grade = Column(String, nullable=False)  # "A", "B+", "P", etc.
    gpa_value = Column(Float, nullable=True)  # Numeric value
    units = Column(Integer, default=3)

    # Timing
    semester = Column(String, nullable=True)  # "Fall 2023", "Spring 2024"
    year = Column(Integer, nullable=True)
    student_year = Column(Integer, nullable=True)  # 1=freshman, 2=sophomore, etc.

    # Analysis
    difficulty_at_time = Column(Float, nullable=True)  # Course difficulty score at time taken
    performance_percentile = Column(Float, nullable=True)  # Estimated percentile

    # Flags
    is_retake = Column(Boolean, default=False)
    is_transfer = Column(Boolean, default=False)  # Transfer credit
    is_ap = Column(Boolean, default=False)  # AP credit

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_candidate_courses_candidate', 'candidate_id'),
        Index('ix_candidate_courses_course', 'course_id'),
    )

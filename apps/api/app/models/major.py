"""
Major model for tracking academic program rigor and GPA data.
Used for adjusted GPA scoring in candidate profiles.
"""

from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base


class Major(Base):
    """
    Academic major/program with rigor ratings and GPA statistics.
    Used to adjust candidate GPA scores based on program difficulty.
    """
    __tablename__ = "majors"

    id = Column(String, primary_key=True)  # e.g., "berkeley_eecs", "stanford_cs", "generic_cs"
    university_id = Column(String, ForeignKey("universities.id", ondelete="CASCADE"), nullable=True)  # Nullable for generic majors

    # Major identification
    name = Column(String, nullable=False)  # "Electrical Engineering & Computer Science"
    short_name = Column(String, nullable=True)  # "EECS"
    department = Column(String, nullable=True)  # "EECS", "CS", "Data Science"

    # Aliases for fuzzy matching
    aliases = Column(JSONB, nullable=True)  # ["Electrical Engineering and Computer Science", "EE/CS"]

    # Difficulty/rigor metrics (1-5 scale, with 0-10 fine-grained score)
    rigor_tier = Column(Integer, nullable=False, default=3)  # 1=easy, 5=hardest
    rigor_score = Column(Float, nullable=False, default=5.0)  # 0-10

    # GPA statistics from grade distribution data
    average_gpa = Column(Float, nullable=True)  # Average GPA in major
    median_gpa = Column(Float, nullable=True)  # Median GPA
    gpa_std_dev = Column(Float, nullable=True)  # Standard deviation

    # Classification
    is_stem = Column(Boolean, default=False, nullable=False)
    is_technical = Column(Boolean, default=False, nullable=False)
    field_category = Column(String, nullable=True)  # "engineering", "science", "business", "humanities", "arts", "social_science"

    # Relevance to career verticals
    relevant_to = Column(JSONB, nullable=True)  # ["software_engineering", "data", "product"]

    # Data source and quality
    source = Column(String, nullable=True)  # "official", "berkeleytime", "research", "estimated"
    source_url = Column(String, nullable=True)  # Link to grade distribution data
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    university = relationship("University", backref="majors")

    # Indexes
    __table_args__ = (
        Index('ix_majors_university_id', 'university_id'),
        Index('ix_majors_field_category', 'field_category'),
        Index('ix_majors_rigor', 'rigor_tier', 'rigor_score'),
    )

    def __repr__(self):
        return f"<Major {self.id}: {self.short_name or self.name}>"

"""Coding Challenge model for technical assessments."""
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class CodingChallenge(Base):
    """
    A coding challenge problem for technical assessment.

    Test cases format (JSON):
    [
        {"input": "5", "expected": "120", "hidden": false, "name": "Test 1"},
        {"input": "10", "expected": "3628800", "hidden": true, "name": "Large input"}
    ]
    """
    __tablename__ = "coding_challenges"

    id = Column(String, primary_key=True)

    # Problem content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)  # Problem description

    # Starter code template
    starter_code = Column(Text, nullable=True)  # e.g., "def solution(n):\n    pass"

    # Test cases as JSON array
    # Format: [{"input": "...", "expected": "...", "hidden": bool, "name": "..."}]
    test_cases = Column(JSON, nullable=False)

    # Solution (reference answer)
    solution = Column(Text, nullable=True)

    # Execution settings
    time_limit_seconds = Column(Integer, default=5)

    # Difficulty level
    difficulty = Column(String, default="easy")  # easy, medium, hard

    # Language (python, javascript, etc.)
    language = Column(String, default="python")

    # Category (algorithms, data-structures, etc.)
    category = Column(String, nullable=True)

    # Target vertical (engineering, data, etc.) - for filtering challenges by interview type
    vertical = Column(String, nullable=True)

    # Target role types (comma-separated, e.g. "software_engineer,backend_engineer")
    role_types = Column(String, nullable=True)

    # Active status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to questions that use this challenge
    questions = relationship("InterviewQuestion", back_populates="coding_challenge")

    # Alias property for backward compatibility with code using problem_description
    @property
    def problem_description(self):
        return self.description

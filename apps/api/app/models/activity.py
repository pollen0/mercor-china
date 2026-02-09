"""
Activity and club database for extracurricular analysis.
Stores clubs/organizations from universities with prestige rankings and metadata.
Similar to course difficulty ratings but for extracurricular activities.
"""

from sqlalchemy import Column, String, DateTime, Date, Float, Integer, Boolean, Text, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class ActivityTier(int, enum.Enum):
    """Activity/club prestige tiers (1-5 scale)."""
    GENERAL = 1           # Open membership, general interest clubs
    COMPETITIVE = 2       # Some selection process, moderate prestige
    SELECTIVE = 3         # Competitive admission, well-known on campus
    HIGHLY_SELECTIVE = 4  # Very competitive, strong alumni network
    ELITE = 5             # Top-tier, national recognition (e.g., varsity sports, ASES, HKN)


class ActivityCategory(str, enum.Enum):
    """Categories of activities."""
    ENGINEERING = "engineering"         # Engineering/CS clubs
    BUSINESS = "business"               # Business, consulting, finance clubs
    RESEARCH = "research"               # Research groups, labs
    COMPETITION = "competition"         # Hackathons, competitive programming
    SOCIAL_IMPACT = "social_impact"     # Social good, volunteer, nonprofits
    PROFESSIONAL = "professional"       # Professional societies, honor societies
    LEADERSHIP = "leadership"           # Student government, orientation leaders
    MEDIA = "media"                     # Publications, broadcasting
    ARTS = "arts"                       # Arts, performance, creative
    SPORTS = "sports"                   # Club/varsity sports
    CULTURAL = "cultural"               # Cultural organizations
    GREEK = "greek"                     # Fraternities/sororities
    OTHER = "other"


class Club(Base):
    """
    University club/organization with prestige ranking.
    Used for activity scoring on candidate profiles.
    """
    __tablename__ = "clubs"

    id = Column(String, primary_key=True)  # e.g., "berkeley_csm", "uiuc_acm"
    university_id = Column(String, nullable=False)  # e.g., "berkeley", "uiuc"

    # Club identification
    name = Column(String, nullable=False)  # Full name
    short_name = Column(String, nullable=True)  # Common abbreviation (e.g., "HKN", "CSM")
    category = Column(String, default="other")  # ActivityCategory value

    # Aliases for fuzzy matching
    aliases = Column(JSONB, nullable=True)  # Alternative names

    # Prestige rating
    prestige_tier = Column(Integer, nullable=False, default=2)  # 1-5 scale
    prestige_score = Column(Float, nullable=False, default=5.0)  # 0-10 fine-grained score

    # Selectivity info
    is_selective = Column(Boolean, default=False)  # Has application process
    acceptance_rate = Column(Float, nullable=True)  # If known (0.0-1.0)
    typical_members = Column(Integer, nullable=True)  # Approximate active members

    # Leadership impact multiplier
    leadership_bonus = Column(Float, default=1.0)  # Multiplier for leadership roles (1.5x for president, etc.)

    # Club characteristics
    is_technical = Column(Boolean, default=False)  # Tech-focused
    is_professional = Column(Boolean, default=False)  # Career-oriented
    has_projects = Column(Boolean, default=False)  # Builds real projects
    has_competitions = Column(Boolean, default=False)  # Participates in competitions
    has_corporate_sponsors = Column(Boolean, default=False)  # Industry connections
    is_honor_society = Column(Boolean, default=False)  # Academic honor society

    # Relevance to career fields
    relevant_to = Column(JSONB, nullable=True)  # ["software_engineering", "product_management", "consulting"]

    # Additional context
    description = Column(Text, nullable=True)
    website_url = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Data quality
    confidence = Column(Float, default=1.0)  # How confident we are in the rating (0-1)
    source = Column(String, nullable=True)  # "manual", "research", "scraped"
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes for efficient lookups
    __table_args__ = (
        Index('ix_clubs_university', 'university_id'),
        Index('ix_clubs_category', 'category'),
        Index('ix_clubs_prestige', 'prestige_tier', 'prestige_score'),
    )


class CandidateActivity(Base):
    """
    Activity/club membership for a candidate.
    Tracks their involvement, role, and duration.
    """
    __tablename__ = "candidate_activities"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    # Activity info
    club_id = Column(String, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)  # FK to clubs table (if known)
    activity_name = Column(String, nullable=False)  # Raw name from input
    organization = Column(String, nullable=True)  # If not a university club
    institution = Column(String, nullable=True)  # University or external org

    # Role and involvement
    role = Column(String, nullable=True)  # "President", "Member", "Project Lead", etc.
    role_tier = Column(Integer, default=1)  # 1=member, 2=active member, 3=officer, 4=exec, 5=president/founder
    description = Column(Text, nullable=True)  # What they did

    # Duration
    start_date = Column(String, nullable=True)  # "Fall 2022", "2022-09"
    end_date = Column(String, nullable=True)  # "Present", "Spring 2024"
    duration_semesters = Column(Integer, nullable=True)  # Calculated duration

    # Parsed dates for querying (populated from start_date/end_date strings)
    parsed_start_date = Column(Date, nullable=True)
    parsed_end_date = Column(Date, nullable=True)
    is_current = Column(Boolean, default=False, nullable=True)  # True if end_date = "Present"

    # Achievements within the activity
    achievements = Column(JSONB, nullable=True)  # List of specific accomplishments

    # Computed score (cached)
    activity_score = Column(Float, nullable=True)  # Composite score considering club prestige + role

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="activities")
    club = relationship("Club")

    __table_args__ = (
        Index('ix_candidate_activities_candidate', 'candidate_id'),
    )


class CandidateAward(Base):
    """
    Awards and achievements for a candidate.
    Honors, scholarships, competition wins, etc.
    """
    __tablename__ = "candidate_awards"

    id = Column(String, primary_key=True)
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    # Award info
    name = Column(String, nullable=False)  # Award name
    issuer = Column(String, nullable=True)  # Who gave the award
    date = Column(String, nullable=True)  # When received

    # Classification
    award_type = Column(String, nullable=True)  # "scholarship", "honor", "competition", "certification"
    prestige_tier = Column(Integer, default=2)  # 1-5 scale

    # Additional details
    description = Column(Text, nullable=True)

    # Parsed date for querying (populated from date string)
    parsed_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="awards")

    __table_args__ = (
        Index('ix_candidate_awards_candidate', 'candidate_id'),
    )

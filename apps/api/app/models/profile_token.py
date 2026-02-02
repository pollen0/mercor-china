from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ProfileToken(Base):
    """
    Magic link tokens for sharing candidate profiles publicly.
    Allows employers to view candidate profiles without logging in.
    """
    __tablename__ = "profile_tokens"

    id = Column(String, primary_key=True)
    token = Column(String, unique=True, nullable=False, index=True)  # Random secure token
    candidate_id = Column(String, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)

    # Token metadata
    created_by_id = Column(String, nullable=True)  # Employer ID who created it (nullable for admin-created)
    created_by_type = Column(String, nullable=True)  # 'employer' or 'admin'
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Token expiration (default 7 days)

    # Usage tracking
    view_count = Column(Integer, default=0)  # How many times the link was accessed
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)  # Last time someone viewed

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    candidate = relationship("Candidate", back_populates="profile_tokens")

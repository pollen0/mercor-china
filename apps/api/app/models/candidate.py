from sqlalchemy import Column, String, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    target_roles = Column(ARRAY(String), default=[])
    resume_url = Column(String, nullable=True)
    wechat_open_id = Column(String, unique=True, nullable=True)
    wechat_union_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    interview_sessions = relationship("InterviewSession", back_populates="candidate")
    matches = relationship("Match", back_populates="candidate")

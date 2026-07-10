from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Education(Base):
    __tablename__ = "education"

    education_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    candidate_name = Column(String(255), nullable=True)
    degree = Column(String(255), nullable=True)
    college = Column(String(255), nullable=True)
    branch = Column(String(255), nullable=True)
    cgpa = Column(String(50), nullable=True)
    graduation_year = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    candidate = relationship("Candidate", back_populates="educations")
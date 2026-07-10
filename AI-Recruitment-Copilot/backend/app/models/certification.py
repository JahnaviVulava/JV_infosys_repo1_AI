from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Certification(Base):
    __tablename__ = "certifications"

    certificate_id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(36), ForeignKey("candidates.candidate_id", ondelete="CASCADE"), nullable=False)
    certificate_name = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    candidate = relationship("Candidate", back_populates="certifications")

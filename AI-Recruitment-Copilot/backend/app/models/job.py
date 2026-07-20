from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Job(Base):
    __tablename__ = "job"

    job_id = Column(String(36), primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, nullable=True)
    experience = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    salary = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

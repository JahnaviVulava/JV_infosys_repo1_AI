from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.sql import func

from backend.app.core.database import Base


class Recruiter(Base):
    __tablename__ = "recruiters"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=True)
    role = Column(String(50), default="recruiter")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

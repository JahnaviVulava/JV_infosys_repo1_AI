from datetime import datetime

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    required_skills: str | None = None
    required_education: str | None = None
    experience: str | None = None
    location: str | None = None
    salary: str | None = None


class JobUpdate(BaseModel):
    job_title: str | None = Field(None, min_length=2, max_length=255)
    company_name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = None
    required_skills: str | None = None
    required_education: str | None = None
    experience: str | None = None
    location: str | None = None
    salary: str | None = None


class JobReplace(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=255)
    company_name: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=1)
    required_skills: str = Field(..., min_length=1)
    required_education: str = Field(..., min_length=1)
    experience: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    salary: str = Field(..., min_length=1)


class JobRead(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    description: str | None = None
    required_skills: str | None = None
    required_education: str | None = None
    experience: str | None = None
    location: str | None = None
    salary: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

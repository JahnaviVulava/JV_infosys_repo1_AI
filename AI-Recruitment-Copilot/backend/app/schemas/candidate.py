from typing import List
from pydantic import BaseModel, Field


class EducationRead(BaseModel):
    degree: str | None = None
    college: str | None = None
    branch: str | None = None
    cgpa: str | None = None
    graduation_year: str | None = None

    class Config:
        from_attributes = True


class SkillRead(BaseModel):
    skill_name: str

    class Config:
        from_attributes = True


class ProjectRead(BaseModel):
    title: str
    description: str | None = None
    technologies: str | None = None

    class Config:
        from_attributes = True


class CertificationRead(BaseModel):
    certificate_name: str
    organization: str | None = None
    issue_date: str | None = None

    class Config:
        from_attributes = True


class CandidateCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    address: str | None = None
    experience_years: str | None = None
    educations: List[EducationRead] | None = None
    skills: List[SkillRead] | None = None
    projects: List[ProjectRead] | None = None
    certifications: List[CertificationRead] | None = None


class CandidateRead(BaseModel):
    candidate_id: str
    name: str
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    address: str | None = None
    resume_file: str | None = None
    experience_years: str | None = None
    educations: List[EducationRead] = []
    skills: List[SkillRead] = []
    projects: List[ProjectRead] = []
    certifications: List[CertificationRead] = []

    class Config:
        from_attributes = True

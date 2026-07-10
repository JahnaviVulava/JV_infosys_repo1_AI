import os
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from backend.app.models.candidate import Candidate
from backend.app.models.certification import Certification
from backend.app.models.education import Education
from backend.app.models.project import Project
from backend.app.models.skill import Skill
from backend.app.services.entity_extractor import EntityExtractor
from backend.app.services.resume_parser import ResumeParser


def _model_columns(model_cls: type) -> set[str]:
    """Return the set of column attribute names actually mapped on a
    SQLAlchemy model class."""
    return {attr.key for attr in inspect(model_cls).mapper.column_attrs}


def _safe_kwargs(model_cls: type, **kwargs: Any) -> dict[str, Any]:
    """Filter kwargs down to only the ones the model actually has a column
    for. This lets candidate_service pass through optional/new fields (like
    candidate_name, branch, cgpa, graduation_year) without crashing the
    whole resume upload if a given model hasn't been migrated to include
    that column yet - it's just silently omitted instead of raising
    'invalid keyword argument for <Model>'."""
    valid = _model_columns(model_cls)
    return {k: v for k, v in kwargs.items() if k in valid}


class CandidateService:
    def __init__(self, db: Session, upload_dir: str) -> None:
        self.db = db
        self.upload_dir = upload_dir
        self.parser = ResumeParser(upload_dir=upload_dir)
        self.extractor = EntityExtractor()

    def process_resume(self, uploaded_file, filename: str) -> dict[str, Any]:
        # Validate the extension BEFORE writing anything to disk, instead
        # of after, so a rejected file type never gets persisted first.
        if not self.parser.validate_resume(filename):
            raise ValueError("Unsupported file type")

        file_path = self.parser.save_uploaded_file(uploaded_file, filename)
        text = self.parser.parse_file(file_path)
        extracted = self.extractor.extract(text)

        candidate_id = str(uuid.uuid4())
        candidate_name = extracted.get("name") or "Unknown"
        candidate = Candidate(
            candidate_id=candidate_id,
            name=candidate_name,
            email=extracted.get("email"),
            phone=extracted.get("phone"),
            linkedin=extracted.get("linkedin"),
            github=extracted.get("github"),
            portfolio=extracted.get("portfolio"),
            resume_file=filename,
            experience_years=extracted.get("experience_years"),
        )
        self.db.add(candidate)
        self.db.flush()

        if extracted.get("education"):
            for item in extracted["education"]:
                education = Education(
                    **_safe_kwargs(
                        Education,
                        candidate_id=candidate_id,
                        candidate_name=candidate_name,
                        degree=item.get("degree"),
                        college=item.get("college"),
                        branch=item.get("branch"),
                        cgpa=item.get("cgpa"),
                        graduation_year=item.get("graduation_year"),
                    )
                )
                self.db.add(education)

        for skill_name in extracted.get("skills", []):
            self.db.add(
                Skill(
                    **_safe_kwargs(
                        Skill,
                        candidate_id=candidate_id,
                        candidate_name=candidate_name,
                        skill_name=skill_name,
                    )
                )
            )

        for project in extracted.get("projects", []):
            self.db.add(
                Project(
                    **_safe_kwargs(
                        Project,
                        candidate_id=candidate_id,
                        candidate_name=candidate_name,
                        title=project.get("title") or "Unnamed Project",
                        description=project.get("description"),
                    )
                )
            )

        for cert in extracted.get("certifications", []):
            self.db.add(
                Certification(
                    **_safe_kwargs(
                        Certification,
                        candidate_id=candidate_id,
                        candidate_name=candidate_name,
                        certificate_name=cert.get("certificate_name") or "Certification",
                    )
                )
            )

        self.db.commit()
        self.db.refresh(candidate)

        return {
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "linkedin": candidate.linkedin,
            "github": candidate.github,
            "portfolio": candidate.portfolio,
            "resume_file": candidate.resume_file,
            "experience_years": candidate.experience_years,
            "skills": extracted.get("skills", []),
            "education": extracted.get("education", []),
            "projects": extracted.get("projects", []),
            "certifications": extracted.get("certifications", []),
            "languages": extracted.get("languages", []),
        }
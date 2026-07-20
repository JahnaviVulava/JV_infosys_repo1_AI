import re
from collections import Counter
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.candidate import Candidate
from backend.app.models.job import Job
from backend.app.schemas.job import JobCreate, JobRead, JobUpdate
from backend.app.services.entity_extractor import EntityExtractor
from backend.app.services.resume_parser import ResumeParser

router = APIRouter(prefix="/jobs", tags=["jobs"])
settings = get_settings()


KNOWN_TECH_SKILLS = {
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "sql",
    "html", "css", "react", "angular", "vue", "node.js", "nodejs", "django",
    "flask", "fastapi", "spring", "mysql", "postgresql", "mongodb", "sqlite",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "linux",
    "pandas", "numpy", "tensorflow", "pytorch", "machine learning", "deep learning",
    "data analysis", "power bi", "tableau", "excel", "figma", "selenium",
}

SKILL_RECOMMENDATIONS = {
    "python": "Build a Python API or data-processing project and practise core language features.",
    "sql": "Practise joins, aggregations, and query optimisation with a small database project.",
    "fastapi": "Build and document a small FastAPI service with validation and CRUD endpoints.",
    "react": "Create a React interface that consumes an API and manages application state.",
    "docker": "Containerise an application and practise writing Dockerfiles and Compose configurations.",
    "aws": "Complete a small deployment using core AWS services and document the architecture.",
    "kubernetes": "Deploy a containerised sample application with Kubernetes manifests.",
    "machine learning": "Train, evaluate, and document an end-to-end machine-learning project.",
}


def normalise_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def recommendation_for_skill(skill: str) -> str:
    return SKILL_RECOMMENDATIONS.get(
        skill,
        f"Complete a focused course and build a small demonstrable project using {skill}.",
    )


def skills_required_by_job(job: Job, candidates: list[Candidate]) -> list[str]:
    """Extract named technical skills from the recruiter-written job description."""
    description = " ".join(filter(None, [job.job_title, job.description or ""])).lower()
    explicit_skills = {
        normalise_skill(skill)
        for skill in (job.required_skills or "").split(",")
        if skill.strip()
    }
    candidate_skills = {
        normalise_skill(skill.skill_name)
        for candidate in candidates
        for skill in candidate.skills
        if skill.skill_name
    }
    catalog = KNOWN_TECH_SKILLS | candidate_skills
    extracted_skills = {
        skill for skill in catalog
        if re.search(rf"(?<!\w){re.escape(skill)}(?!\w)", description)
    }
    return sorted(explicit_skills | extracted_skills)


def experience_matches(candidate_experience: str | None, job_experience: str | None) -> bool | None:
    if not job_experience:
        return None
    candidate_numbers = re.findall(r"\d+(?:\.\d+)?", candidate_experience or "")
    job_numbers = re.findall(r"\d+(?:\.\d+)?", job_experience)
    if not candidate_numbers or not job_numbers:
        return None
    minimum_required = float(job_numbers[0])
    return float(candidate_numbers[0]) >= minimum_required


def experience_surplus(candidate_experience: str | None, job_experience: str | None) -> float:
    """Return years above the job minimum, used only to break ranking ties."""
    candidate_numbers = re.findall(r"\d+(?:\.\d+)?", candidate_experience or "")
    job_numbers = re.findall(r"\d+(?:\.\d+)?", job_experience or "")
    if not candidate_numbers or not job_numbers:
        return -1.0
    return float(candidate_numbers[0]) - float(job_numbers[0])


def locations_match(candidate_address: str | None, job_location: str | None) -> bool | None:
    if not candidate_address or not job_location:
        return None
    candidate_location = normalise_skill(candidate_address)
    target_location = normalise_skill(job_location)
    return target_location in candidate_location or candidate_location in target_location


def details_from_existing_resume(candidate: Candidate) -> dict[str, object]:
    """Recover fields for candidates uploaded before improved extraction."""
    if not candidate.resume_file:
        return {}
    resume_path = Path(settings.upload_dir) / candidate.resume_file
    if not resume_path.exists():
        return {}
    try:
        resume_text = ResumeParser(settings.upload_dir).parse_file(str(resume_path))
        return EntityExtractor().extract(resume_text)
    except Exception:
        return {}


@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
) -> Job:
    job = Job(
        job_id=str(uuid4()),
        **job_data.model_dump(),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("", response_model=list[JobRead])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}/matches")
def match_candidates_to_job(job_id: str, db: Session = Depends(get_db)) -> dict[str, object]:
    """Rank every candidate against skills named in a selected job description."""
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Hide historical duplicate uploads in matching results. Prefer the most
    # recently created record for the same email, LinkedIn URL, or name+phone.
    raw_candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    candidates: list[Candidate] = []
    seen_candidates: set[str] = set()
    for candidate in raw_candidates:
        identity = (
            f"email:{normalise_skill(candidate.email)}" if candidate.email else
            f"linkedin:{normalise_skill(candidate.linkedin)}" if candidate.linkedin else
            f"name-phone:{normalise_skill(candidate.name)}:{candidate.phone}" if candidate.phone else
            f"id:{candidate.candidate_id}"
        )
        if identity not in seen_candidates:
            seen_candidates.add(identity)
            candidates.append(candidate)
    required_skills = skills_required_by_job(job, candidates)
    results: list[dict[str, object]] = []
    backfilled_candidate_data = False

    for candidate in candidates:
        recovered_details = {}
        if not candidate.address or candidate.experience_years in (None, "", "0"):
            recovered_details = details_from_existing_resume(candidate)
        candidate_location = candidate.address or recovered_details.get("address")
        candidate_experience = candidate.experience_years
        recovered_experience = recovered_details.get("experience_years")
        if candidate_experience in (None, "", "0") and recovered_experience not in (None, "", "0"):
            candidate_experience = str(recovered_experience)
        if candidate_location and not candidate.address:
            candidate.address = str(candidate_location)
            backfilled_candidate_data = True
        if candidate_experience and candidate_experience != candidate.experience_years:
            candidate.experience_years = candidate_experience
            backfilled_candidate_data = True

        candidate_skills = sorted({
            normalise_skill(skill.skill_name)
            for skill in candidate.skills
            if skill.skill_name
        })
        candidate_skill_set = set(candidate_skills)
        required_skill_set = set(required_skills)
        matched_skills = sorted(candidate_skill_set & required_skill_set)
        missing_skills = sorted(required_skill_set - candidate_skill_set)
        additional_skills = sorted(candidate_skill_set - required_skill_set)
        skill_score = round((len(matched_skills) / len(required_skills)) * 100) if required_skills else 0
        experience_match = experience_matches(candidate_experience, job.experience)
        location_match = locations_match(candidate_location, job.location)
        relevant_certifications = [
            re.sub(r"\s*\(cid:\d+\)", "", cert.certificate_name, flags=re.IGNORECASE).strip()
            for cert in candidate.certifications
            if cert.certificate_name and any(
                skill in normalise_skill(cert.certificate_name)
                for skill in required_skill_set
            )
        ]
        skill_score_points = round(skill_score * 0.75, 1)
        experience_score_points = 20 if experience_match else 0
        location_score_points = 5 if location_match else 0
        # Skills carry 75% of the score, experience 20%, and location only 5%.
        score = round(skill_score_points + experience_score_points + location_score_points)

        results.append({
            "candidate_id": candidate.candidate_id,
            "candidate_name": candidate.name,
            "candidate_experience": candidate_experience,
            "education": [education.degree for education in candidate.educations if education.degree],
            "certifications": [
                re.sub(r"\s*\(cid:\d+\)", "", cert.certificate_name, flags=re.IGNORECASE).strip()
                for cert in candidate.certifications
                if cert.certificate_name
            ],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "additional_skills": additional_skills,
            "matched_skill_count": len(matched_skills),
            "missing_skill_count": len(missing_skills),
            "skill_match_percentage": skill_score,
            "skill_gap_percentage": 100 - skill_score,
            "skill_score_points": skill_score_points,
            "experience_score_points": experience_score_points,
            "location_score_points": location_score_points,
            "missing_skill_recommendations": [
                {"skill": skill, "recommendation": recommendation_for_skill(skill)}
                for skill in missing_skills
            ],
            "experience_match": experience_match,
            "experience_surplus": experience_surplus(candidate_experience, job.experience),
            "candidate_location": candidate_location,
            "job_location": job.location,
            "location_match": location_match,
            "relevant_certifications": relevant_certifications,
            "education_count": len([education for education in candidate.educations if education.degree]),
            "match_score": score,
        })

    if backfilled_candidate_data:
        db.commit()

    # Equal scores are ranked by skill coverage, fewer skill gaps, experience,
    # relevant certifications/education, and only then the low-priority location.
    results.sort(
        key=lambda result: (
            result["match_score"],
            result["matched_skill_count"],
            -result["missing_skill_count"],
            result["experience_surplus"],
            len(result["relevant_certifications"]),
            result["education_count"],
            result["location_match"] is True,
        ),
        reverse=True,
    )
    name_occurrences: dict[str, int] = {}
    for rank, result in enumerate(results, start=1):
        result["rank"] = rank
        candidate_name = str(result["candidate_name"])
        name_occurrences[candidate_name] = name_occurrences.get(candidate_name, 0) + 1
        occurrence = name_occurrences[candidate_name]
        # Distinguish genuinely different candidates with the same name without
        # exposing an internal candidate ID in the recruiter UI.
        result["display_name"] = candidate_name if occurrence == 1 else f"{candidate_name} ({occurrence})"

    missing_skill_counts = Counter(
        skill
        for result in results
        for skill in result["missing_skills"]
    )

    return {
        "job_id": job.job_id,
        "job_title": job.job_title,
        "required_skills": required_skills,
        "summary": {
            "candidate_count": len(results),
            "top_score": results[0]["match_score"] if results else 0,
            "average_score": round(sum(result["match_score"] for result in results) / len(results)) if results else 0,
        },
        "skill_gap_summary": [
            {"skill": skill, "candidates_missing": count}
            for skill, count in missing_skill_counts.most_common()
        ],
        "matches": results,
    }


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
) -> Job:
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.put("/{job_id}", response_model=JobRead)
def update_job(
    job_id: str,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
) -> Job:
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: str,
    db: Session = Depends(get_db),
) -> None:
    job = db.query(Job).filter(Job.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db.delete(job)
    db.commit()

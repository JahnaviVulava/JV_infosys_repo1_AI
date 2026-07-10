from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_recruiter
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.candidate import Candidate
from backend.app.models.recruiter import Recruiter
from backend.app.schemas.candidate import CandidateRead
from backend.app.services.candidate_service import CandidateService

router = APIRouter(prefix="", tags=["candidates"])
settings = get_settings()


def process_resume_file(file: UploadFile, db: Session) -> dict[str, object]:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")

    service = CandidateService(db=db, upload_dir=settings.upload_dir)
    try:
        result = service.process_resume(uploaded_file=file.file, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process resume") from exc

    return {"message": "Resume processed successfully", "candidate": result}


@router.post("/resume/upload", status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    current_recruiter: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    return process_resume_file(file, db)


@router.post("/public/resume/upload", status_code=status.HTTP_201_CREATED)
def upload_resume_public(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict[str, object]:
    return process_resume_file(file, db)


@router.get("/candidate/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: str, db: Session = Depends(get_db), current_recruiter: Recruiter = Depends(get_current_recruiter)) -> CandidateRead:
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    return CandidateRead.model_validate(candidate)


@router.get("/candidates", response_model=list[CandidateRead])
def list_candidates(db: Session = Depends(get_db), current_recruiter: Recruiter = Depends(get_current_recruiter)) -> list[CandidateRead]:
    candidates = db.query(Candidate).all()
    return [CandidateRead.model_validate(candidate) for candidate in candidates]


@router.get("/public/candidates", response_model=list[CandidateRead])
def list_candidates_public(db: Session = Depends(get_db)) -> list[CandidateRead]:
    candidates = db.query(Candidate).all()
    return [CandidateRead.model_validate(candidate) for candidate in candidates]


@router.get("/public/candidate/{candidate_id}/text")
def get_candidate_text(candidate_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    if not candidate.resume_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not available")

    resume_path = Path(settings.upload_dir) / candidate.resume_file
    if not resume_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")

    # EVERYTHING below is now inside one try/except. Previously only the
    # parser call was guarded, but candidate_data = CandidateRead.model_
    # validate(candidate).model_dump() (and the dict assignment after it)
    # sat unguarded below that - if either of those raised, it was still
    # an unhandled exception producing the blank "Internal Server Error"
    # you kept seeing, even after the parser call itself was fixed. This
    # wraps the whole rest of the handler so ANY failure here returns a
    # real, readable HTTPException detail instead of a bare 500.
    try:
        parser = CandidateService(db=db, upload_dir=settings.upload_dir).parser
        resume_text = parser.parse_file(str(resume_path))

        # Return structured candidate data plus extracted resume text so
        # the frontend can render formatted details and sections.
        candidate_data = CandidateRead.model_validate(candidate).model_dump()
        candidate_data["resume_text"] = resume_text
        return candidate_data
    except HTTPException:
        raise
    except ValueError as exc:
        # Unsupported file types or validation errors are client errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - surface parsing/setup errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load candidate text: {type(exc).__name__}: {exc}",
        ) from exc


@router.get("/public/candidate/{candidate_id}/resume")
def download_candidate_resume(candidate_id: str, db: Session = Depends(get_db)) -> FileResponse:
    candidate = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found")

    if not candidate.resume_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not available")

    resume_path = Path(settings.upload_dir) / candidate.resume_file
    if not resume_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")

    return FileResponse(path=str(resume_path), filename=candidate.resume_file, media_type="application/octet-stream")
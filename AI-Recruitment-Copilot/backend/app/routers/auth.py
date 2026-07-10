import uuid

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.auth.dependencies import get_current_recruiter
from backend.app.auth.jwt_utils import create_access_token
from backend.app.auth.password_utils import hash_password, verify_password
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.recruiter import Recruiter
from backend.app.schemas.auth import AuthResponse, LoginRequest, Token, UserCreate

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.query(Recruiter).filter(Recruiter.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    recruiter = Recruiter(
        id=str(uuid.uuid4()),
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)

    access_token = create_access_token(recruiter.id)
    return AuthResponse(message="Recruiter registered successfully", access_token=access_token)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    recruiter = db.query(Recruiter).filter(Recruiter.email == str(payload.email)).first()
    if not recruiter or not recruiter.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not verify_password(payload.password, recruiter.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(recruiter.id)
    return Token(access_token=access_token)


@router.post("/logout")
def logout(current_recruiter: Recruiter = Depends(get_current_recruiter)) -> dict[str, str]:
    return {"message": f"Recruiter {current_recruiter.name} logged out successfully"}


@router.get("/google", response_model=Token)
def google_login(access_token: str = Query(...), db: Session = Depends(get_db)) -> Token:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")

    response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google access token")

    payload = response.json()
    email = payload.get("email")
    recruiter = db.query(Recruiter).filter(Recruiter.email == email).first()
    if not recruiter:
        recruiter = Recruiter(
            id=str(uuid.uuid4()),
            name=payload.get("name") or "Google Recruiter",
            email=email,
            google_id=payload.get("sub"),
            password_hash=None,
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

    app_token = create_access_token(recruiter.id)
    return Token(access_token=app_token)

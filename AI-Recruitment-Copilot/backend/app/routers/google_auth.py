import uuid

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.app.auth.jwt_utils import create_access_token
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.recruiter import Recruiter

router = APIRouter(prefix="/auth/google", tags=["google-auth"])
settings = get_settings()


@router.get("/login")
def google_login_redirect() -> RedirectResponse:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth"
    query = "&".join([f"{key}={requests.utils.quote(str(value))}" for key, value in params.items()])
    return RedirectResponse(f"{url}?{query}")


@router.get("/callback")
def google_login_callback(code: str = Query(...), db: Session = Depends(get_db)) -> dict[str, str]:
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google OAuth is not configured")

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )

    if token_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google token exchange failed")

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google access token not found")

    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unable to fetch Google user info")

    userinfo = userinfo_response.json()
    email = userinfo.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google account email not found")

    recruiter = db.query(Recruiter).filter(Recruiter.email == email).first()
    if not recruiter:
        recruiter = Recruiter(
            id=str(uuid.uuid4()),
            name=userinfo.get("name") or "Google Recruiter",
            email=email,
            google_id=userinfo.get("sub"),
            password_hash=None,
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

    app_token = create_access_token(recruiter.id)
    return RedirectResponse(f"{settings.frontend_url}/?token={app_token}")

import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import get_settings
from backend.app.core.database import create_tables
from backend.app.routers import (
    auth_router,
    candidates_router,
    google_auth_router,
    health_router,
    jobs_router,
)

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(google_auth_router)
app.include_router(candidates_router)
app.include_router(jobs_router)


@app.on_event("startup")
def startup_event() -> None:
    create_tables()


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{type(exc).__name__}: {exc}",
            "path": str(request.url),
            "traceback": traceback.format_exc(),
        },
    )


@app.get("/debug-ping")
def debug_ping():
    return {"status": "new-code-is-running"}
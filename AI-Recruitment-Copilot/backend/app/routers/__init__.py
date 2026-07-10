from backend.app.routers.auth import router as auth_router
from backend.app.routers.candidates import router as candidates_router
from backend.app.routers.google_auth import router as google_auth_router
from backend.app.routers.health import router as health_router

__all__ = ["auth_router", "candidates_router", "google_auth_router", "health_router"]

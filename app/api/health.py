"""Health check endpoints."""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.database import check_db_connection

router = APIRouter(prefix="/api", tags=["health"])

API_VERSION = "0.1.0"


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    """Liveness probe with database connectivity status."""
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app_env": settings.app_env,
        "version": API_VERSION,
        "database": "connected" if db_ok else "unreachable",
    }

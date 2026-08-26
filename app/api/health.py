"""Health check endpoints.

`GET /api/health` is the first thing any deploy tool / load balancer will
probe. Later phases will extend it with database connectivity status.
"""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(prefix="/api", tags=["health"])

API_VERSION = "0.1.0"


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    """Liveness probe. Returns process status and active environment."""
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "version": API_VERSION,
        "database": "not_configured",  # Phase 2 will report real DB status
    }

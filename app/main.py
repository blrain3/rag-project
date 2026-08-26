"""Application entry point.

Run in development with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Application factory: builds and configures the FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=health.API_VERSION,
        debug=settings.debug,
    )

    # Routers
    app.include_router(health.router)

    @app.get("/", tags=["health"])
    def root() -> dict:
        return {"message": "RAG API is running"}

    return app


app = create_app()

"""Health check endpoints."""

from typing import Any

from fastapi import APIRouter
from src.core.config import app_config

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": app_config.title,
        "version": app_config.version,
        "environment": app_config.environment,
        "auth_provider": "spotify_oauth",
    }

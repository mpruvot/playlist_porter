"""Main API router for all endpoints."""

from fastapi import APIRouter
from src.api.spotify.playlists import router as spotify_router

router = APIRouter()

# Include all provider routers
router.include_router(spotify_router, prefix="/spotify", tags=["Spotify"])

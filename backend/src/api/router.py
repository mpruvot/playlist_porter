from fastapi import APIRouter
from src.api.auth import router as auth_router
from src.api.spotify.playlists import router as spotify_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(spotify_router, prefix="/spotify", tags=["Spotify"])

"""Spotify-specific API dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.adapters.providers.spotify.repository import SpotifyPlaylistRepository
from src.core.config import spotify_config
from src.domain.services.migration_manager import MigrationManager
from src.domain.services.playlist_manager import PlaylistManager

# Simple Bearer token for Swagger UI
bearer = HTTPBearer(auto_error=False)


async def get_spotify_token(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    """Get Spotify token from Bearer or header."""
    # PRIORITIZE x-spotify-token header first (from frontend)
    spotify_token = request.headers.get("x-spotify-token")
    if spotify_token:
        return spotify_token

    if credentials:
        return credentials.credentials

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Missing Spotify token. Use Bearer token or x-spotify-token header.",
    )


def get_spotify_repository(
    spotify_token: Annotated[str, Depends(get_spotify_token)],
) -> SpotifyPlaylistRepository:
    """Get Spotify playlist repository instance."""
    return SpotifyPlaylistRepository(spotify_config, spotify_token)


def get_spotify_playlist_manager(
    repository: Annotated[SpotifyPlaylistRepository, Depends(get_spotify_repository)],
) -> PlaylistManager:
    """Get playlist manager with Spotify repository."""
    return PlaylistManager(repository)


def get_spotify_migration_manager(
    repository: Annotated[SpotifyPlaylistRepository, Depends(get_spotify_repository)],
) -> MigrationManager:
    """Get migration manager with Spotify repository."""
    return MigrationManager(repository)

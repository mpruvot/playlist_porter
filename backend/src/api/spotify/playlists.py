"""Spotify playlist API endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies.spotify import (
    get_spotify_migration_manager,
    get_spotify_playlist_manager,
)
from src.api.spotify.schemas import (
    AddTracksRequest,
    CreatePlaylistRequest,
)
from src.core.exceptions import SpotifyAPIError
from src.domain.models.playlist import Playlist
from src.domain.models.track import Track
from src.domain.services.migration_manager import MigrationManager
from src.domain.services.playlist_manager import PlaylistManager
from src.infrastructure.logging import get_logger

logger = get_logger("api.spotify.playlists")

router = APIRouter()


def _handle_spotify_error(e: SpotifyAPIError) -> HTTPException:
    """Convert SpotifyAPIError to HTTPException."""
    if e.status_code == 401:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to continue",
        )
    elif e.status_code == 403:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to perform this action",
        )
    elif e.status_code == 404:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )
    elif e.status_code == 429:
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while communicating with Spotify",
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_playlists(
    playlist_manager: Annotated[PlaylistManager, Depends(get_spotify_playlist_manager)],
) -> list[Playlist]:
    """Get user's Spotify playlists."""
    try:
        playlists = await playlist_manager.get_user_playlists()
        return playlists
    except SpotifyAPIError as e:
        logger.error(f"Spotify API error: {e}")
        raise _handle_spotify_error(e)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching playlists",
        )


@router.get("/{playlist_id}/tracks", status_code=status.HTTP_200_OK)
async def get_playlist_tracks(
    playlist_id: str,
    playlist_manager: Annotated[PlaylistManager, Depends(get_spotify_playlist_manager)],
) -> list[Track]:
    """Get tracks from a specific playlist."""
    try:
        tracks = await playlist_manager.get_playlist_tracks(playlist_id)
        return tracks
    except SpotifyAPIError as e:
        logger.error(f"Spotify API error: {e}")
        raise _handle_spotify_error(e)
    except Exception as e:
        logger.error(f"Unexpected error getting tracks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching tracks",
        )


@router.post("/create", status_code=status.HTTP_200_OK)
async def create_playlist(
    request_data: CreatePlaylistRequest,
    playlist_manager: PlaylistManager = Depends(get_spotify_playlist_manager),
) -> Playlist:
    """Create a new playlist."""
    try:
        playlist = await playlist_manager.create_playlist(
            name=request_data.name,
            description=request_data.description,
            is_public=request_data.public,
        )

        return playlist

    except SpotifyAPIError as e:
        logger.error(f"Spotify API error creating playlist: {e}")
        raise _handle_spotify_error(e)
    except Exception as e:
        logger.error(f"Unexpected error creating playlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the playlist",
        )


@router.post("/{playlist_id}/tracks", status_code=status.HTTP_201_CREATED)
async def add_tracks_to_playlist(
    playlist_id: str,
    request_data: AddTracksRequest,
    playlist_manager: Annotated[PlaylistManager, Depends(get_spotify_playlist_manager)],
) -> dict[str, str]:
    """Add tracks to a playlist."""
    try:
        await playlist_manager.add_tracks_to_playlist(
            playlist_id, request_data.track_uris
        )
        return {
            "message": f"Successfully added {len(request_data.track_uris)} tracks to playlist"
        }
    except SpotifyAPIError as e:
        logger.error(f"Spotify API error: {e}")
        raise _handle_spotify_error(e)
    except Exception as e:
        logger.error(f"Unexpected error adding tracks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while adding tracks",
        )


@router.post("/{source_id}/copy-to/{target_id}", status_code=status.HTTP_200_OK)
async def copy_playlist_tracks(
    source_id: str,
    target_id: str,
    migration_manager: MigrationManager = Depends(get_spotify_migration_manager),
) -> dict[str, Any]:
    """Copy tracks from one playlist to another."""
    try:
        result = await migration_manager.copy_playlist_tracks(source_id, target_id)
        return result
    except SpotifyAPIError as e:
        logger.error(f"Spotify API error: {e}")
        raise _handle_spotify_error(e)
    except Exception as e:
        logger.error(f"Unexpected error copying tracks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while copying tracks",
        )

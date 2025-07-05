"""Spotify implementation of PlaylistRepository."""

from typing import Any

from src.adapters.providers.spotify.client import (
    SpotifyAPIUrls,
    SpotifyClient,
    SpotifyLimits,
)
from src.adapters.providers.spotify.mappers import SpotifyMappers
from src.core.config import SpotifyConfig
from src.core.exceptions import SpotifyAPIError
from src.domain.interfaces.playlist_repository import PlaylistRepository
from src.domain.models.playlist import Playlist
from src.domain.models.track import Track
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.providers.spotify.repository")


class SpotifyPlaylistRepository(PlaylistRepository):
    """Spotify implementation of PlaylistRepository protocol."""

    def __init__(self, config: SpotifyConfig, access_token: str):
        self.client = SpotifyClient(config, access_token)
        self.mappers = SpotifyMappers()

    async def get_by_id(self, playlist_id: str) -> Playlist | None:
        """Get a playlist by its ID."""
        clean_id = self.client.extract_id_from_url(playlist_id)
        url = SpotifyAPIUrls.PLAYLIST_BY_ID.format(playlist_id=clean_id)

        try:
            data = await self.client.make_request(
                "GET", url, f"Failed to get playlist {playlist_id}"
            )
            return self.mappers.playlist_from_api(data)
        except SpotifyAPIError as e:
            if e.status_code == 404:
                return None
            raise

    async def get_all(self) -> list[Playlist]:
        """Get all playlists for a user."""
        params = {"limit": SpotifyLimits.MAX_PLAYLISTS_PER_REQUEST}
        data = await self.client.make_request(
            "GET", SpotifyAPIUrls.PLAYLISTS, "Failed to fetch playlists", params=params
        )
        return [self.mappers.playlist_from_api(item) for item in data.get("items", [])]

    async def get_tracks(self, playlist_id: str) -> list[Track]:
        """Get all tracks from a playlist."""
        url = SpotifyAPIUrls.PLAYLIST_TRACKS.format(playlist_id=playlist_id)
        params = {"limit": SpotifyLimits.MAX_TRACKS_PER_REQUEST}
        data = await self.client.make_request(
            "GET",
            url,
            f"Failed to fetch tracks for playlist {playlist_id}",
            params=params,
        )
        return [
            self.mappers.track_from_api(item["track"])
            for item in data.get("items", [])
            if item.get("track")
        ]

    async def create(
        self, name: str, description: str = "", is_public: bool = False
    ) -> Playlist:
        """Create a new playlist."""
        user_info = await self.get_user_info()
        url = SpotifyAPIUrls.CREATE_PLAYLIST.format(user_id=user_info["id"])
        payload = {"name": name, "description": description, "public": is_public}

        try:
            data = await self.client.make_request(
                "POST", url, f"Failed to create playlist '{name}'", json=payload
            )
            return self.mappers.playlist_from_api(data)
        except SpotifyAPIError as e:
            if e.status_code == 403:
                raise SpotifyAPIError(
                    f"Insufficient permissions to create playlist '{name}'. The Spotify token may not have the required scopes.",
                    status_code=403,
                    error_response=e.error_response,
                )
            raise

    async def add_tracks(
        self, playlist_id: str, track_uris: list[str], position: int | None = None
    ) -> str:
        """Add tracks to a playlist."""
        url = SpotifyAPIUrls.PLAYLIST_TRACKS.format(playlist_id=playlist_id)
        payload: dict[str, Any] = {"uris": track_uris}
        if position is not None:
            payload["position"] = position

        data = await self.client.make_request(
            "POST", url, f"Failed to add tracks to playlist {playlist_id}", json=payload
        )
        return data.get("snapshot_id", "")

    async def delete(self, playlist_id: str) -> bool:
        """Delete (unfollow) a playlist."""
        url = SpotifyAPIUrls.UNFOLLOW_PLAYLIST.format(playlist_id=playlist_id)
        await self.client.make_request(
            "DELETE", url, f"Failed to delete playlist {playlist_id}"
        )
        return True

    async def get_user_info(self) -> dict[str, Any]:
        """Get current user information."""
        return await self.client.make_request(
            "GET", SpotifyAPIUrls.ME, "Failed to get user info"
        )

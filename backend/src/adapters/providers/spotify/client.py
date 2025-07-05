"""Spotify API client for HTTP communication."""

from typing import Any

import httpx
from src.core.config import SpotifyConfig
from src.core.exceptions import SpotifyAPIError
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.providers.spotify.client")


class SpotifyAPIUrls:
    """Spotify API endpoint URLs."""

    BASE_URL = "https://api.spotify.com/v1"

    # User endpoints
    ME = f"{BASE_URL}/me"

    # Playlist endpoints
    PLAYLISTS = f"{BASE_URL}/me/playlists"
    PLAYLIST_BY_ID = f"{BASE_URL}/playlists/{{playlist_id}}"
    PLAYLIST_TRACKS = f"{BASE_URL}/playlists/{{playlist_id}}/tracks"
    CREATE_PLAYLIST = f"{BASE_URL}/users/{{user_id}}/playlists"
    UNFOLLOW_PLAYLIST = f"{BASE_URL}/playlists/{{playlist_id}}/followers"

    # Track endpoints
    TRACKS = f"{BASE_URL}/tracks"
    TRACK_BY_ID = f"{BASE_URL}/tracks/{{track_id}}"


class SpotifyLimits:
    """Spotify API limits and constraints."""

    MAX_TRACKS_PER_REQUEST = 100
    MAX_PLAYLISTS_PER_REQUEST = 50
    MAX_PLAYLIST_NAME_LENGTH = 100
    MAX_PLAYLIST_DESCRIPTION_LENGTH = 300


class SpotifyClient:
    """Spotify API client for HTTP communication."""

    def __init__(self, config: SpotifyConfig, access_token: str):
        self.config = config
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def make_request(
        self,
        method: str,
        url: str,
        error_msg: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with centralized error handling."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    **kwargs,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP {e.response.status_code}: {error_msg}")
                raise SpotifyAPIError(
                    error_msg,
                    status_code=e.response.status_code,
                    error_response=e.response.text,
                )
            except Exception as e:
                logger.error(f"Request failed: {error_msg} - {e}")
                raise SpotifyAPIError(f"{error_msg}: {e}")

    def extract_id_from_url(self, playlist_id: str) -> str:
        """Extract playlist ID from Spotify URL or return ID as-is."""
        if "open.spotify.com" in playlist_id:
            return playlist_id.split("/")[-1].split("?")[0]
        return playlist_id

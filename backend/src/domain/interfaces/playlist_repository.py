"""Repository interface for playlist CRUD operations."""

from typing import Protocol

from src.domain.models.playlist import Playlist
from src.domain.models.track import Track


class PlaylistRepository(Protocol):
    """Protocol for playlist repository implementations."""

    async def get_user_info(self) -> dict:
        """Get current user information."""
        ...

    async def get_by_id(self, playlist_id: str) -> Playlist | None:
        """Get a playlist by its ID."""
        ...

    async def get_all(self) -> list[Playlist]:
        """Get all playlists for a user."""
        ...

    async def get_tracks(self, playlist_id: str) -> list[Track]:
        """Get all tracks from a playlist."""
        ...

    async def create(
        self, name: str, description: str = "", is_public: bool = False
    ) -> Playlist:
        """Create a new playlist."""
        ...

    async def add_tracks(
        self, playlist_id: str, track_uris: list[str], position: int | None = None
    ) -> str:
        """Add tracks to a playlist. Returns snapshot_id."""
        ...

    async def delete(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        ...

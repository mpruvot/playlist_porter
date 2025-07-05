"""Domain service for playlist management."""

from src.domain.interfaces.playlist_repository import PlaylistRepository
from src.domain.models.playlist import Playlist
from src.domain.models.track import Track
from src.infrastructure.logging import get_logger

logger = get_logger("domain.services.playlist_manager")


class PlaylistManager:
    """Domain service for playlist operations."""

    def __init__(self, repository: PlaylistRepository):
        self.repository = repository

    async def get_user_playlists(self) -> list[Playlist]:
        """Get all playlists for a user."""
        return await self.repository.get_all()

    async def get_playlist_tracks(self, playlist_id: str) -> list[Track]:
        """Get tracks from a playlist."""
        return await self.repository.get_tracks(playlist_id)

    async def create_playlist(
        self, name: str, description: str = "", is_public: bool = False
    ) -> Playlist:
        """Create a new playlist."""
        return await self.repository.create(name, description, is_public)

    async def add_tracks_to_playlist(
        self, playlist_id: str, track_uris: list[str]
    ) -> None:
        """Add tracks to a playlist."""
        await self.repository.add_tracks(playlist_id, track_uris)

    async def delete_playlist(self, playlist_id: str) -> bool:
        """Delete a playlist."""
        return await self.repository.delete(playlist_id)

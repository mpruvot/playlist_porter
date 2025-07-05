"""Domain service for playlist migration and copying."""

from typing import Any

from src.domain.interfaces.playlist_repository import PlaylistRepository
from src.infrastructure.logging import get_logger

logger = get_logger("domain.services.migration_manager")


class MigrationManager:
    """Domain service for playlist migration operations."""

    def __init__(self, repository: PlaylistRepository):
        self.repository = repository

    async def copy_playlist_tracks(
        self, source_id: str, target_id: str
    ) -> dict[str, Any]:
        """Copy all tracks from source playlist to target playlist."""
        try:
            # Get source tracks
            source_tracks = await self.repository.get_tracks(source_id)

            if not source_tracks:
                return {"tracks_copied": 0, "message": "Source playlist is empty"}

            # Extract track URIs
            track_uris = [
                track.external_uri for track in source_tracks if track.external_uri
            ]

            # Batch processing (Spotify API limits to 100 tracks per request)
            batch_size = 100
            total_copied = 0
            batches_processed = 0

            for i in range(0, len(track_uris), batch_size):
                batch_uris = track_uris[i : i + batch_size]
                await self.repository.add_tracks(target_id, batch_uris)
                total_copied += len(batch_uris)
                batches_processed += 1

            return {
                "tracks_copied": total_copied,
                "batches_processed": batches_processed,
                "message": f"Successfully copied {total_copied} tracks in {batches_processed} batches",
                "source_playlist_id": source_id,
                "target_playlist_id": target_id,
            }

        except Exception as e:
            logger.error(f"Error copying playlist tracks: {e}")
            raise

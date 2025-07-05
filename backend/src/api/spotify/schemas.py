"""Request and response schemas for Spotify API endpoints."""

from pydantic import BaseModel, Field


class CreatePlaylistRequest(BaseModel):
    """Request model for creating a playlist."""

    name: str = Field(..., min_length=1, max_length=100, description="Playlist name")
    description: str = Field(
        default="", max_length=300, description="Playlist description"
    )
    public: bool = Field(default=True, description="Whether playlist is public")
    collaborative: bool = Field(
        default=False, description="Whether playlist is collaborative"
    )


class AddTracksRequest(BaseModel):
    """Request model for adding tracks to a playlist."""

    track_uris: list[str] = Field(
        ...,
        min_length=0,
        max_length=100,
        description="List of Spotify track URIs to add",
    )
    position: int | None = Field(
        default=None,
        ge=0,
        description="Position to insert tracks (0-based, None for end)",
    )


class DuplicatePlaylistRequest(BaseModel):
    """Request model for duplicating a playlist."""

    source_playlist_id: str = Field(..., description="Source playlist ID")
    target_playlist_name: str = Field(
        ..., min_length=1, max_length=100, description="Target playlist name"
    )
    target_playlist_description: str = Field(
        default="", max_length=300, description="Target playlist description"
    )
    public: bool = Field(default=False, description="Whether target playlist is public")

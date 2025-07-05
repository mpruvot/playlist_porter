"""Domain model for Playlist."""

from pydantic import BaseModel, Field


class Playlist(BaseModel):
    """Domain model for a playlist."""

    id: str = Field(..., description="Playlist ID")
    name: str = Field(..., description="Playlist name")
    description: str = Field(default="", description="Playlist description")
    tracks_count: int = Field(..., description="Number of tracks in playlist")
    is_public: bool = Field(default=False, description="Whether playlist is public")
    is_collaborative: bool = Field(
        default=False, description="Whether playlist is collaborative"
    )
    owner_id: str = Field(..., description="Owner user ID")
    owner_name: str | None = Field(default=None, description="Owner display name")
    external_id: str = Field(..., description="External provider ID")
    provider: str = Field(default="spotify", description="Music provider")
    external_url: str = Field(default="", description="External URL to playlist")
    image_url: str | None = Field(default=None, description="Playlist cover image URL")
    snapshot_id: str | None = Field(
        default=None, description="Snapshot ID for versioning"
    )
    uri: str = Field(default="", description="Provider URI (spotify:playlist:xxx)")
    href: str = Field(default="", description="API href to playlist details")

"""Domain model for Track."""

from pydantic import BaseModel, Field


class Artist(BaseModel):
    """Domain model for an artist."""

    id: str = Field(..., description="Artist ID")
    name: str = Field(..., description="Artist name")
    external_id: str = Field(..., description="External provider ID")
    provider: str = Field(default="spotify", description="Music provider")
    external_url: str = Field(default="", description="External URL to artist")
    uri: str = Field(default="", description="Provider URI (spotify:artist:xxx)")


class Album(BaseModel):
    """Domain model for an album."""

    id: str = Field(..., description="Album ID")
    name: str = Field(..., description="Album name")
    external_id: str = Field(..., description="External provider ID")
    provider: str = Field(default="spotify", description="Music provider")
    external_url: str = Field(default="", description="External URL to album")
    uri: str = Field(default="", description="Provider URI (spotify:album:xxx)")
    release_date: str | None = Field(default=None, description="Release date")
    artists: list[Artist] = Field(default_factory=list, description="Album artists")
    image_url: str | None = Field(default=None, description="Album cover image URL")


class Track(BaseModel):
    """Domain model for a track."""

    id: str = Field(..., description="Track ID")
    title: str = Field(..., description="Track title")
    artists: list[Artist] = Field(..., description="Track artists")
    album: Album = Field(..., description="Track album")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    external_uri: str = Field(..., description="Provider URI (spotify:track:xxx)")
    external_id: str = Field(..., description="External provider ID")
    provider: str = Field(default="spotify", description="Music provider")
    external_url: str = Field(default="", description="External URL to track")
    preview_url: str | None = Field(default=None, description="Preview URL")
    is_explicit: bool = Field(default=False, description="Whether track is explicit")
    popularity: int = Field(default=0, description="Track popularity (0-100)")
    track_number: int | None = Field(default=None, description="Track number in album")
    disc_number: int | None = Field(default=None, description="Disc number")

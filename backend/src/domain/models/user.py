"""Domain model for User."""

from pydantic import BaseModel, Field


class User(BaseModel):
    """Domain model for a user."""

    id: str = Field(..., description="User ID")
    email: str | None = Field(default=None, description="User email")
    display_name: str | None = Field(default=None, description="User display name")
    external_id: str = Field(..., description="External provider ID")
    provider: str = Field(default="spotify", description="Music provider")
    external_url: str = Field(default="", description="External URL to user profile")
    image_url: str | None = Field(default=None, description="User profile image URL")
    country: str | None = Field(default=None, description="User country")
    followers_count: int = Field(default=0, description="Number of followers")

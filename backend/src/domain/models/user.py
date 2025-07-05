from datetime import datetime

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

    # Authentication fields
    auth_id: str | None = Field(default=None, description="Supabase Auth ID")
    is_authenticated: bool = Field(default=False, description="Auth status")
    roles: list[str] = Field(default_factory=list, description="User roles")
    created_at: datetime | None = Field(default=None, description="Account creation")
    last_login: datetime | None = Field(default=None, description="Last login")
    is_active: bool = Field(default=True, description="Account status")

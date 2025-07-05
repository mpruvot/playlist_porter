"""Domain model for authentication session."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuthSession(BaseModel):
    """Domain model for an authentication session."""

    user_id: str = Field(..., description="User ID")
    access_token: str = Field(..., description="Supabase JWT access token")
    refresh_token: str | None = Field(
        default=None, description="Supabase JWT refresh token"
    )
    provider_token: str | None = Field(
        default=None, description="OAuth provider access token"
    )
    provider_refresh_token: str | None = Field(
        default=None, description="OAuth provider refresh token"
    )
    provider: str = Field(
        default="spotify", description="OAuth provider (always spotify)"
    )
    expires_at: datetime = Field(..., description="Token expiration time")
    created_at: datetime = Field(..., description="Session creation time")
    last_used_at: datetime = Field(..., description="Last token usage time")
    user_agent: str | None = Field(default=None, description="User agent string")
    ip_address: str | None = Field(default=None, description="Client IP address")


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class SpotifyOAuthRequest(BaseModel):
    """Spotify OAuth authentication request."""

    redirect_url: str | None = Field(
        default=None, description="Redirect URL after auth"
    )
    scopes: str | None = Field(default=None, description="Spotify OAuth scopes")


class SpotifyOAuthCallback(BaseModel):
    """Spotify OAuth callback data."""

    code: str = Field(..., description="Spotify authorization code")
    state: str | None = Field(default=None, description="OAuth state parameter")

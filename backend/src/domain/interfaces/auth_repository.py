"""Authentication repository protocol."""

from typing import Protocol

from src.domain.models.auth_session import (
    AuthSession,
    SpotifyOAuthCallback,
    SpotifyOAuthRequest,
)
from src.domain.models.user import User


class AuthRepository(Protocol):
    """Authentication repository protocol."""

    # Spotify OAuth methods
    async def get_spotify_oauth_url(self, request: SpotifyOAuthRequest) -> str:
        """Get Spotify OAuth authorization URL."""
        ...

    async def exchange_spotify_oauth_code(
        self, callback: SpotifyOAuthCallback
    ) -> tuple[User, AuthSession]:
        """Exchange Spotify OAuth code for user and session."""
        ...

    async def refresh_spotify_session(self, refresh_token: str) -> AuthSession:
        """Refresh Spotify OAuth session using refresh token."""
        ...

    # Session management
    async def verify_session_token(self, token: str) -> User | None:
        """Verify Supabase session token and return user."""
        ...

    async def get_current_session(self, token: str) -> AuthSession | None:
        """Get current session information."""
        ...

    async def revoke_session(self, token: str) -> bool:
        """Revoke a session (logout)."""
        ...

    # User management
    async def get_user_by_auth_id(self, auth_id: str) -> User | None:
        """Get user by auth provider ID."""
        ...

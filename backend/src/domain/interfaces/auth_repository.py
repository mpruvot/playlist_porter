from typing import Protocol

from src.domain.models.auth_session import AuthSession
from src.domain.models.user import User


class AuthRepository(Protocol):
    """Authentication repository protocol."""

    # Generic OAuth methods
    async def get_oauth_url(self, provider: str, scopes: str) -> str:
        """Get OAuth authorization URL for specified provider."""
        ...

    async def exchange_oauth_code(
        self, provider: str, code: str, state: str | None = None
    ) -> tuple[User, AuthSession]:
        """Exchange OAuth code for user and session."""
        ...

    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """Refresh OAuth session using refresh token."""
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

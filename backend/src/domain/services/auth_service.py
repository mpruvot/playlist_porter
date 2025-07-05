"""Domain service for authentication business logic."""

from src.core.exceptions import SpotifyAPIError
from src.domain.interfaces.auth_repository import AuthRepository
from src.domain.models.auth_session import (
    AuthSession,
    LoginRequest,
    OAuthCallback,
    OAuthRequest,
    RegisterRequest,
    TokenPair,
)
from src.domain.models.user import User


class AuthenticationError(Exception):
    """Authentication-related errors."""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthService:
    """Domain service for authentication business logic."""

    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    # OAuth methods (primary)
    async def get_oauth_authorization_url(self, request: OAuthRequest) -> str:
        """Get OAuth authorization URL for the specified provider."""
        try:
            return await self.auth_repository.get_oauth_url(request)
        except Exception as e:
            raise AuthenticationError(f"OAuth URL generation failed: {str(e)}", 400)

    async def handle_oauth_callback(
        self, callback: OAuthCallback
    ) -> tuple[User, AuthSession]:
        """Handle OAuth callback and create user session."""
        try:
            user, session = await self.auth_repository.exchange_oauth_code(callback)

            if not user.is_active:
                raise AuthenticationError("Account is deactivated", 403)

            return user, session
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"OAuth callback failed: {str(e)}", 401)

    async def verify_session_token(self, token: str) -> User:
        """Verify session token and return authenticated user."""
        user = await self.auth_repository.verify_session_token(token)
        if not user:
            raise AuthenticationError("Invalid or expired session", 401)

        if not user.is_active:
            raise AuthenticationError("Account is deactivated", 403)

        return user

    async def get_current_session(self, token: str) -> AuthSession:
        """Get current session information."""
        session = await self.auth_repository.get_current_session(token)
        if not session:
            raise AuthenticationError("Invalid session", 401)

        return session

    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """Refresh session using refresh token."""
        try:
            session = await self.auth_repository.refresh_oauth_session(refresh_token)
            return session
        except Exception as e:
            raise AuthenticationError(f"Session refresh failed: {str(e)}", 401)

    async def logout_user(self, token: str) -> bool:
        """Logout user by revoking session."""
        try:
            return await self.auth_repository.revoke_session(token)
        except Exception:
            # Logout should be permissive - even if token is invalid
            return True

    async def get_user_by_auth_id(self, auth_id: str) -> User | None:
        """Get user by authentication ID."""
        return await self.auth_repository.get_user_by_auth_id(auth_id)

    # Fallback email/password methods (optional)
    async def register_user(self, request: RegisterRequest) -> User:
        """Register a new user with email/password (fallback)."""
        try:
            user = await self.auth_repository.register_user(request)
            return user
        except Exception as e:
            raise AuthenticationError(f"Registration failed: {str(e)}", 400)

    async def authenticate_user(self, request: LoginRequest) -> User:
        """Authenticate user with email/password (fallback)."""
        try:
            user = await self.auth_repository.authenticate_user(request)
            return user
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}", 401)

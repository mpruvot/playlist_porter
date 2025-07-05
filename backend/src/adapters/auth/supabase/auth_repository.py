"""Supabase OAuth implementation of AuthRepository."""

from src.adapters.auth.supabase.client import SupabaseClient
from src.adapters.auth.supabase.mappers import SupabaseAuthMappers
from src.core.config import AuthConfig, SupabaseConfig
from src.core.exceptions import AuthenticationError
from src.domain.models.auth_session import (
    AuthSession,
    SpotifyOAuthCallback,
    SpotifyOAuthRequest,
)
from src.domain.models.user import User
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.auth.supabase.repository")


class SupabaseAuthRepository:
    """Supabase implementation of AuthRepository using OAuth."""

    def __init__(self, supabase_config: SupabaseConfig, auth_config: AuthConfig):
        self.client = SupabaseClient(supabase_config, auth_config)
        self.mappers = SupabaseAuthMappers()

    # Spotify OAuth methods
    async def get_spotify_oauth_url(self, request: SpotifyOAuthRequest) -> str:
        """Get Spotify OAuth authorization URL."""
        try:
            return await self.client.get_oauth_url(
                provider="spotify",
                redirect_url=request.redirect_url,
                scopes=request.scopes,
            )
        except Exception as e:
            logger.error(f"Spotify OAuth URL generation failed: {str(e)}")
            raise AuthenticationError(f"Spotify OAuth URL generation failed: {str(e)}")

    async def exchange_spotify_oauth_code(
        self, callback: SpotifyOAuthCallback
    ) -> tuple[User, AuthSession]:
        """Exchange Spotify OAuth code for user and session."""
        try:
            # Exchange the code for a session
            session_data = await self.client.exchange_oauth_code(callback.code)

            if not session_data.get("user"):
                raise AuthenticationError(
                    "Spotify OAuth exchange failed: No user returned"
                )

            # Map to domain models - always Spotify
            user = self.mappers.user_from_oauth_session(session_data, "spotify")
            session = self.mappers.session_from_supabase(session_data, "spotify")

            logger.info(f"Spotify OAuth exchange successful for user: {user.email}")
            return user, session
        except Exception as e:
            logger.error(f"Spotify OAuth code exchange failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Spotify OAuth exchange failed: {str(e)}")

    async def refresh_spotify_session(self, refresh_token: str) -> AuthSession:
        """Refresh Spotify OAuth session using refresh token."""
        try:
            # Set the refresh token and refresh the session
            session_data = await self.client.refresh_session()

            # Always Spotify
            session = self.mappers.session_from_supabase(session_data, "spotify")

            logger.info("Spotify OAuth session refreshed successfully")
            return session
        except Exception as e:
            logger.error(f"Spotify OAuth session refresh failed: {str(e)}")
            raise AuthenticationError(f"Spotify session refresh failed: {str(e)}")

    # Session management
    async def verify_session_token(self, token: str) -> User | None:
        """Verify Supabase session token and return user."""
        try:
            user_data = await self.client.get_user_from_token(token)
            if not user_data:
                return None

            user = self.mappers.user_from_supabase(user_data)
            logger.debug(f"Session token verified for user: {user.email}")
            return user
        except Exception as e:
            logger.warning(f"Session token verification failed: {str(e)}")
            return None

    async def get_current_session(self, token: str) -> AuthSession | None:
        """Get current session information."""
        try:
            # Set token and get session
            session_data = await self.client.get_session()
            if not session_data:
                return None

            provider = "spotify"  # Should be determined from session data
            session = self.mappers.session_from_supabase(session_data, provider)

            logger.debug("Current session retrieved successfully")
            return session
        except Exception as e:
            logger.warning(f"Failed to get current session: {str(e)}")
            return None

    async def revoke_session(self, token: str) -> bool:
        """Revoke a session (logout)."""
        try:
            result = await self.client.sign_out()
            logger.info("Session revoked successfully")
            return result
        except Exception as e:
            logger.warning(f"Session revocation failed: {str(e)}")
            # Be permissive with logout
            return True

    # User management
    async def get_user_by_auth_id(self, auth_id: str) -> User | None:
        """Get user by auth provider ID."""
        try:
            # This would typically query the Supabase database
            # For now, we'll implement a simple approach
            logger.debug(f"Getting user by auth_id: {auth_id}")
            # TODO: Implement user lookup by auth_id from Supabase database
            return None
        except Exception as e:
            logger.error(f"User lookup by auth_id failed: {str(e)}")
            return None

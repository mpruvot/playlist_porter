from src.adapters.auth.supabase.client import SupabaseClient
from src.adapters.auth.supabase.mappers import SupabaseAuthMappers
from src.core.config import AuthConfig, SupabaseConfig
from src.core.exceptions import AuthenticationError
from src.domain.models.auth_session import AuthSession
from src.domain.models.user import User
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.auth.supabase.repository")


class SupabaseAuthRepository:
    """Supabase implementation of AuthRepository using OAuth."""

    def __init__(self, supabase_config: SupabaseConfig, auth_config: AuthConfig):
        self.client = SupabaseClient(supabase_config, auth_config)
        self.mappers = SupabaseAuthMappers()

    # Generic OAuth methods
    async def get_oauth_url(self, provider: str, scopes: str) -> str:
        """Get OAuth authorization URL for specified provider."""
        try:
            return await self.client.get_oauth_url(
                provider=provider,
                redirect_url=None,  # Supabase handles redirect URL
                scopes=scopes,
            )
        except Exception as e:
            logger.error(f"{provider} OAuth URL generation failed: {str(e)}")
            raise AuthenticationError(
                f"{provider} OAuth URL generation failed: {str(e)}"
            )

    async def exchange_oauth_code(
        self, provider: str, code: str, state: str | None = None
    ) -> tuple[User, AuthSession]:
        """Exchange OAuth code for user and session."""
        try:
            # Exchange the code for a session
            session_data = await self.client.exchange_oauth_code(code)

            if not session_data.get("user"):
                raise AuthenticationError(
                    f"{provider} OAuth exchange failed: No user returned"
                )

            # Map to domain models
            user = self.mappers.user_from_oauth_session(session_data, provider)
            session = self.mappers.session_from_supabase(session_data, provider)

            logger.info(f"{provider} OAuth exchange successful for user: {user.email}")
            return user, session
        except Exception as e:
            logger.error(f"{provider} OAuth code exchange failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"{provider} OAuth exchange failed: {str(e)}")

    async def refresh_session(self, refresh_token: str) -> AuthSession:
        """Refresh OAuth session using refresh token."""
        try:
            # Set the refresh token and refresh the session
            session_data = await self.client.refresh_session()

            # Determine provider from session data, default to spotify
            provider = session_data.get("session", {}).get("provider", "spotify")
            session = self.mappers.session_from_supabase(session_data, provider)

            logger.info(f"{provider} OAuth session refreshed successfully")
            return session
        except Exception as e:
            logger.error(f"OAuth session refresh failed: {str(e)}")
            raise AuthenticationError(f"Session refresh failed: {str(e)}")

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

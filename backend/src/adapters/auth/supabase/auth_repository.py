"""Supabase OAuth implementation of AuthRepository."""

from src.adapters.auth.supabase.client import SupabaseClient
from src.adapters.auth.supabase.mappers import SupabaseAuthMappers
from src.core.config import AuthConfig, SupabaseConfig
from src.core.exceptions import AuthenticationError
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
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.auth.supabase.repository")


class SupabaseAuthRepository(AuthRepository):
    """Supabase implementation of AuthRepository using OAuth."""

    def __init__(self, supabase_config: SupabaseConfig, auth_config: AuthConfig):
        self.client = SupabaseClient(supabase_config, auth_config)
        self.mappers = SupabaseAuthMappers()

    # OAuth methods (primary)
    async def get_oauth_url(self, request: OAuthRequest) -> str:
        """Get OAuth authorization URL for the specified provider."""
        try:
            return await self.client.get_oauth_url(
                provider=request.provider,
                redirect_url=request.redirect_url,
                scopes=request.scopes,
            )
        except Exception as e:
            logger.error(f"OAuth URL generation failed: {str(e)}")
            raise AuthenticationError(f"OAuth URL generation failed: {str(e)}")

    async def exchange_oauth_code(
        self, callback: OAuthCallback
    ) -> tuple[User, AuthSession]:
        """Exchange OAuth code for user and session."""
        try:
            # Exchange the code for a session
            session_data = await self.client.exchange_oauth_code(callback.code)

            if not session_data.get("user"):
                raise AuthenticationError("OAuth exchange failed: No user returned")

            # Map to domain models
            provider = "spotify"  # Default for now, could be extracted from callback
            user = self.mappers.user_from_oauth_session(session_data, provider)
            session = self.mappers.session_from_supabase(session_data, provider)

            logger.info(f"OAuth exchange successful for user: {user.email}")
            return user, session
        except Exception as e:
            logger.error(f"OAuth code exchange failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"OAuth exchange failed: {str(e)}")

    async def refresh_oauth_session(self, refresh_token: str) -> AuthSession:
        """Refresh OAuth session using refresh token."""
        try:
            # Set the refresh token and refresh the session
            session_data = await self.client.refresh_session()

            provider = "spotify"  # Should be stored/determined from context
            session = self.mappers.session_from_supabase(session_data, provider)

            logger.info("OAuth session refreshed successfully")
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

            # Determine provider from user metadata or default to spotify
            provider = user_data.get("app_metadata", {}).get("provider", "spotify")

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

    # Fallback email/password methods (optional)
    async def register_user(self, request: RegisterRequest) -> User:
        """Register a new user with email/password (fallback)."""
        try:
            response = await self.client.sign_up_with_email(
                request.email, request.password
            )

            if not response.get("user"):
                raise AuthenticationError("Registration failed: No user returned")

            user = self.mappers.user_from_supabase(response["user"])
            logger.info(f"User registered successfully: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Registration failed: {str(e)}")

    async def authenticate_user(self, request: LoginRequest) -> User:
        """Authenticate user with email/password (fallback)."""
        try:
            response = await self.client.sign_in_with_email(
                request.email, request.password
            )

            if not response.get("user"):
                raise AuthenticationError("Authentication failed: Invalid credentials")

            user = self.mappers.user_from_supabase(response["user"])
            logger.info(f"User authenticated successfully: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError("Invalid email or password")

    async def generate_tokens(self, user: User, remember_me: bool = False) -> TokenPair:
        """Generate access and refresh tokens for user."""
        try:
            token_data = self.client.generate_jwt_tokens(
                user.auth_id or user.id, remember_me
            )
            tokens = self.mappers.tokens_from_data(token_data)
            logger.debug(f"Tokens generated for user: {user.email}")
            return tokens
        except Exception as e:
            logger.error(f"Token generation failed: {str(e)}")
            raise AuthenticationError(f"Token generation failed: {str(e)}")

    async def verify_access_token(self, token: str) -> User | None:
        """Verify access token and return user."""
        try:
            user_data = await self.client.get_user_from_token(token)
            if not user_data:
                return None

            user = self.mappers.user_from_supabase(user_data)
            logger.debug(f"Access token verified for user: {user.email}")
            return user
        except Exception as e:
            logger.warning(f"Access token verification failed: {str(e)}")
            return None

    async def verify_refresh_token(self, token: str) -> User | None:
        """Verify refresh token and return user."""
        try:
            # For refresh tokens, we verify the JWT structure first
            user_data = await self.client.get_user_from_token(token)
            if not user_data:
                return None

            user = self.mappers.user_from_supabase(user_data)
            logger.debug(f"Refresh token verified for user: {user.email}")
            return user
        except Exception as e:
            logger.warning(f"Refresh token verification failed: {str(e)}")
            return None

    async def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """Generate new tokens from refresh token."""
        try:
            # First verify the refresh token
            user = await self.verify_refresh_token(refresh_token)
            if not user:
                raise AuthenticationError("Invalid refresh token")

            # Generate new tokens
            token_data = self.client.generate_jwt_tokens(user.auth_id or user.id)
            tokens = self.mappers.tokens_from_data(token_data)
            logger.info(f"Tokens refreshed for user: {user.email}")
            return tokens
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Token refresh failed: {str(e)}")

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token (logout)."""
        try:
            result = await self.client.sign_out(token)
            logger.info("Token revoked successfully")
            return result
        except Exception as e:
            logger.warning(f"Token revocation failed: {str(e)}")
            # Be permissive with logout
            return True

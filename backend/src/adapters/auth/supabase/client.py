"""Supabase client for OAuth authentication."""

from supabase import Client, create_client
from src.core.config import AuthConfig, SupabaseConfig
from src.infrastructure.logging import get_logger

logger = get_logger("adapters.auth.supabase.client")


class SupabaseClient:
    """Supabase client wrapper for OAuth authentication operations."""

    def __init__(self, supabase_config: SupabaseConfig, auth_config: AuthConfig):
        self.supabase_config = supabase_config
        self.auth_config = auth_config
        self._client: Client | None = None

    @property
    def client(self) -> Client:
        """Get or create Supabase client."""
        if self._client is None:
            self._client = create_client(
                self.supabase_config.url, self.supabase_config.anon_key
            )
        return self._client

    async def get_oauth_url(
        self, provider: str, redirect_url: str | None = None, scopes: str | None = None
    ) -> str:
        """Get OAuth authorization URL for the specified provider."""
        try:
            credentials = {"provider": provider}
            if redirect_url or scopes:
                options = {}
                if redirect_url:
                    options["redirect_to"] = redirect_url
                if scopes:
                    options["scopes"] = scopes
                credentials["options"] = options

            response = self.client.auth.sign_in_with_oauth(credentials)

            if hasattr(response, "url") and response.url:
                logger.info(f"OAuth URL generated for provider: {provider}")
                return response.url
            else:
                raise Exception("No OAuth URL returned from Supabase")

        except Exception as e:
            logger.error(f"OAuth URL generation failed for {provider}: {str(e)}")
            raise

    async def exchange_oauth_code(
        self, code: str, code_verifier: str | None = None
    ) -> dict:
        """Exchange OAuth authorization code for session."""
        try:
            # Build code exchange parameters
            code_params = {"auth_code": code}
            if code_verifier:
                code_params["code_verifier"] = code_verifier

            response = self.client.auth.exchange_code_for_session(code_params)
            logger.info("OAuth code exchanged successfully")
            return response.model_dump()
        except Exception as e:
            logger.error(f"OAuth code exchange failed: {str(e)}")
            raise

    async def get_session(self) -> dict | None:
        """Get current session."""
        try:
            session = self.client.auth.get_session()
            if session:
                return session.model_dump()
            return None
        except Exception as e:
            logger.warning(f"Failed to get session: {str(e)}")
            return None

    async def get_user_from_token(self, token: str) -> dict | None:
        """Get user information from session token."""
        try:
            # Set the session with the provided token
            self.client.auth.set_session(token, "")

            # Get the user
            user_response = self.client.auth.get_user()

            if user_response and user_response.user:
                logger.debug(f"Token verified for user: {user_response.user.email}")
                return user_response.user.model_dump()

            return None
        except Exception as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None

    async def refresh_session(self) -> dict:
        """Refresh current session using stored refresh token."""
        try:
            response = self.client.auth.refresh_session()
            logger.info("Session refreshed successfully")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Session refresh failed: {str(e)}")
            raise

    async def sign_out(self) -> bool:
        """Sign out user and invalidate session."""
        try:
            self.client.auth.sign_out()
            logger.info("User signed out successfully")
            return True
        except Exception as e:
            logger.warning(f"Sign out failed: {str(e)}")
            # Return True anyway - sign out should be permissive
            return True

    # Fallback email/password methods
    async def sign_up_with_email(self, email: str, password: str) -> dict:
        """Sign up user with email and password (fallback)."""
        try:
            response = self.client.auth.sign_up({"email": email, "password": password})
            logger.info(f"User signed up: {email}")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Sign up failed for {email}: {str(e)}")
            raise

    async def sign_in_with_email(self, email: str, password: str) -> dict:
        """Sign in user with email and password (fallback)."""
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            logger.info(f"User signed in: {email}")
            return response.model_dump()
        except Exception as e:
            logger.error(f"Sign in failed for {email}: {str(e)}")
            raise

"""Mappers to convert Supabase data to domain models."""

from datetime import datetime
from src.domain.models.auth_session import AuthSession, TokenPair
from src.domain.models.user import User


class SupabaseAuthMappers:
    """Mappers for Supabase authentication data."""

    @staticmethod
    def user_from_supabase(supabase_user: dict) -> User:
        """Convert Supabase user to domain User model."""
        return User(
            id=supabase_user.get("id", ""),
            email=supabase_user.get("email"),
            display_name=supabase_user.get("user_metadata", {}).get("display_name"),
            external_id="",  # Not applicable for auth user
            provider="auth",  # This is the auth user, not music provider
            external_url="",
            image_url=supabase_user.get("user_metadata", {}).get("avatar_url"),
            country=None,
            followers_count=0,
            # Auth-specific fields
            auth_id=supabase_user.get("id"),
            is_authenticated=True,
            roles=supabase_user.get("user_metadata", {}).get("roles", []),
            created_at=datetime.fromisoformat(
                supabase_user.get("created_at", "").replace("Z", "+00:00")
            )
            if supabase_user.get("created_at")
            else None,
            last_login=datetime.fromisoformat(
                supabase_user.get("last_sign_in_at", "").replace("Z", "+00:00")
            )
            if supabase_user.get("last_sign_in_at")
            else None,
            is_active=True,  # Supabase users are active by default
        )

    @staticmethod
    def tokens_from_data(token_data: dict) -> TokenPair:
        """Convert token data to TokenPair domain model."""
        return TokenPair(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type="bearer",
            expires_in=token_data.get("expires_in", 900),  # Default 15 minutes
        )

    @staticmethod
    def tokens_from_supabase_session(session_data: dict) -> TokenPair:
        """Convert Supabase session to TokenPair domain model."""
        session = session_data.get("session", {})
        return TokenPair(
            access_token=session.get("access_token", ""),
            refresh_token=session.get("refresh_token", ""),
            token_type="bearer",
            expires_in=session.get("expires_in", 3600),  # Supabase default
        )

    @staticmethod
    def session_from_supabase(session_data: dict, provider: str) -> AuthSession:
        """Convert Supabase OAuth session to AuthSession domain model."""
        session = session_data.get("session", {})
        user = session_data.get("user", {})

        # Extract provider token from session
        provider_token = session.get("provider_token")
        provider_refresh_token = session.get("provider_refresh_token")

        return AuthSession(
            user_id=user.get("id", ""),
            access_token=session.get("access_token", ""),
            refresh_token=session.get("refresh_token", ""),
            provider_token=provider_token,
            provider_refresh_token=provider_refresh_token,
            provider=provider,
            expires_at=datetime.fromisoformat(
                session.get("expires_at", "").replace("Z", "+00:00")
            )
            if session.get("expires_at")
            else datetime.utcnow(),
            created_at=datetime.fromisoformat(
                user.get("created_at", "").replace("Z", "+00:00")
            )
            if user.get("created_at")
            else datetime.utcnow(),
            last_used_at=datetime.fromisoformat(
                user.get("last_sign_in_at", "").replace("Z", "+00:00")
            )
            if user.get("last_sign_in_at")
            else datetime.utcnow(),
        )

    @staticmethod
    def user_from_oauth_session(session_data: dict, provider: str) -> User:
        """Convert Supabase OAuth session user to domain User model."""
        user = session_data.get("user", {})
        user_metadata = user.get("user_metadata", {})

        return User(
            id=user.get("id", ""),
            email=user.get("email"),
            display_name=user_metadata.get("full_name") or user_metadata.get("name"),
            external_id=user_metadata.get("provider_id", ""),
            provider=provider,
            external_url=user_metadata.get("avatar_url", ""),
            image_url=user_metadata.get("picture") or user_metadata.get("avatar_url"),
            country=user_metadata.get("country"),
            followers_count=0,
            # Auth-specific fields
            auth_id=user.get("id"),
            is_authenticated=True,
            roles=user_metadata.get("roles", []),
            created_at=datetime.fromisoformat(
                user.get("created_at", "").replace("Z", "+00:00")
            )
            if user.get("created_at")
            else None,
            last_login=datetime.fromisoformat(
                user.get("last_sign_in_at", "").replace("Z", "+00:00")
            )
            if user.get("last_sign_in_at")
            else None,
            is_active=True,
        )

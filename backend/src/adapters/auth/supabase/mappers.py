"""Mappers to convert Supabase data to domain models."""

from datetime import datetime

from src.domain.models.auth_session import AuthSession
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
    def session_from_supabase(session_data: dict, provider: str) -> AuthSession:
        """Convert Supabase OAuth session to AuthSession domain model."""
        session = session_data.get("session", {})
        user = session_data.get("user", {})

        # Extract Spotify tokens - check multiple possible locations
        provider_token = None
        provider_refresh_token = None

        # Method 1: Direct from session (most common)
        if session.get("provider_token"):
            provider_token = session.get("provider_token")
            provider_refresh_token = session.get("provider_refresh_token")

        # Method 2: From user metadata (alternative location)
        elif user.get("user_metadata", {}).get("provider_token"):
            user_metadata = user.get("user_metadata", {})
            provider_token = user_metadata.get("provider_token")
            provider_refresh_token = user_metadata.get("provider_refresh_token")

        # Method 3: From app metadata (admin/system tokens)
        elif user.get("app_metadata", {}).get("provider_token"):
            app_metadata = user.get("app_metadata", {})
            provider_token = app_metadata.get("provider_token")
            provider_refresh_token = app_metadata.get("provider_refresh_token")

        # Method 4: From session user (nested structure)
        elif session.get("user", {}).get("user_metadata", {}).get("provider_token"):
            session_user_metadata = session.get("user", {}).get("user_metadata", {})
            provider_token = session_user_metadata.get("provider_token")
            provider_refresh_token = session_user_metadata.get("provider_refresh_token")

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

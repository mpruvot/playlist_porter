"""Authentication dependencies for FastAPI."""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Cookie, Depends, HTTPException, status
from src.adapters.auth.supabase import SupabaseAuthRepository
from src.core.config import AuthConfig, SupabaseConfig, auth_config, supabase_config
from src.domain.models.user import User
from src.domain.services.auth_service import AuthenticationError, AuthService


def get_supabase_auth_repository() -> SupabaseAuthRepository:
    """Get Supabase authentication repository instance."""
    return SupabaseAuthRepository(supabase_config, auth_config)


def get_auth_service(
    auth_repository: Annotated[
        SupabaseAuthRepository, Depends(get_supabase_auth_repository)
    ],
) -> AuthService:
    """Get authentication service instance."""
    return AuthService(auth_repository)


def get_auth_config() -> AuthConfig:
    """Get authentication configuration."""
    return auth_config


def get_supabase_config() -> SupabaseConfig:
    """Get Supabase configuration."""
    return supabase_config


async def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """Get current authenticated user from session token."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access token provided",
        )

    try:
        user = await auth_service.verify_session_token(access_token)
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        )


async def get_current_user_optional(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> User | None:
    """Get current authenticated user from session token (optional)."""
    if not access_token:
        return None

    try:
        user = await auth_service.verify_session_token(access_token)
        return user
    except AuthenticationError:
        return None


def require_roles(*required_roles: str) -> Callable[..., Coroutine[Any, Any, User]]:
    """Dependency factory for role-based access control."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """Check if user has required roles."""
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}",
            )
        return current_user

    return role_checker


def require_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure user account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return current_user


def require_authenticated_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure user is authenticated and active."""
    if not current_user.is_authenticated or not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user


# Commonly used dependency combinations
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentUserOptional = Annotated[User | None, Depends(get_current_user_optional)]
ActiveUser = Annotated[User, Depends(require_active_user)]
AuthenticatedUser = Annotated[User, Depends(require_authenticated_user)]

"""Authentication endpoints."""

from datetime import timedelta
from typing import Annotated, Literal, cast

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from fastapi.responses import RedirectResponse
from src.api.dependencies.auth import (
    get_auth_config,
    get_auth_service,
    get_current_user,
)
from src.core.config import AuthConfig
from src.domain.models.auth_session import (
    AuthSession,
    SpotifyOAuthCallback,
    SpotifyOAuthRequest,
)
from src.domain.models.user import User
from src.domain.services.auth_service import AuthenticationError, AuthService

router = APIRouter()


@router.get("/spotify/login", response_class=RedirectResponse)
async def spotify_login(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    redirect_url: str | None = Query(
        default=None, description="Redirect URL after auth"
    ),
) -> RedirectResponse:
    """Initiate Spotify OAuth login."""
    try:
        request = SpotifyOAuthRequest(
            redirect_url=redirect_url,
            scopes="user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private",
        )

        oauth_url = await auth_service.get_spotify_oauth_url(request)
        return RedirectResponse(url=oauth_url)

    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/spotify/callback", response_model=User)
async def spotify_callback(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_config: Annotated[AuthConfig, Depends(get_auth_config)],
    code: str = Query(..., description="Spotify authorization code"),
    state: str | None = Query(default=None, description="OAuth state parameter"),
) -> User:
    """Handle Spotify OAuth callback and create user session."""
    try:
        callback = SpotifyOAuthCallback(code=code, state=state)
        user, session = await auth_service.handle_spotify_callback(callback)

        # Set secure cookies with Supabase tokens
        _set_session_cookies(response, session, auth_config)

        return user
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=AuthSession)
async def refresh_session(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    auth_config: Annotated[AuthConfig, Depends(get_auth_config)],
    refresh_token: Annotated[str | None, Cookie()] = None,
) -> AuthSession:
    """Refresh OAuth session using refresh token."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided"
        )

    try:
        new_session = await auth_service.refresh_session(refresh_token)

        # Update cookies with new session
        _set_session_cookies(response, new_session, auth_config)

        return new_session
    except AuthenticationError as e:
        _clear_session_cookies(response)
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> None:
    """Logout user and revoke session."""
    if access_token:
        try:
            await auth_service.logout_user(access_token)
        except Exception:
            pass  # Be permissive with logout

    # Clear cookies
    _clear_session_cookies(response)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current authenticated user."""
    return current_user


@router.get("/session", response_model=AuthSession)
async def get_current_session(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    access_token: Annotated[str | None, Cookie()] = None,
) -> AuthSession:
    """Get current session information including provider tokens."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No access token provided"
        )

    try:
        session = await auth_service.get_current_session(access_token)
        return session
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


def _set_session_cookies(
    response: Response, session: AuthSession, auth_config: AuthConfig
) -> None:
    """Set secure session cookies."""
    # Supabase access token cookie (short-lived)
    response.set_cookie(
        key="access_token",
        value=session.access_token,
        max_age=3600,  # 1 hour - Supabase default
        httponly=True,
        secure=auth_config.cookie_secure,
        samesite=cast(Literal["lax", "strict", "none"], auth_config.cookie_samesite),
        domain=auth_config.cookie_domain,
        path="/",
    )

    # Supabase refresh token cookie (long-lived)
    if session.refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=session.refresh_token,
            max_age=int(timedelta(days=7).total_seconds()),  # 7 days
            httponly=True,
            secure=auth_config.cookie_secure,
            samesite=cast(
                Literal["lax", "strict", "none"], auth_config.cookie_samesite
            ),
            domain=auth_config.cookie_domain,
            path="/",
        )

    # Provider token (for API calls to Spotify/etc) - optional
    if session.provider_token:
        response.set_cookie(
            key="provider_token",
            value=session.provider_token,
            max_age=3600,  # 1 hour - depends on provider
            httponly=True,
            secure=auth_config.cookie_secure,
            samesite=cast(
                Literal["lax", "strict", "none"], auth_config.cookie_samesite
            ),
            domain=auth_config.cookie_domain,
            path="/",
        )


def _clear_session_cookies(response: Response) -> None:
    """Clear session cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    response.delete_cookie(key="provider_token", path="/")

"""Custom exceptions for Playlist Porter."""


class PlaylistPorterError(Exception):
    """Base exception for all Playlist Porter errors."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class ConfigurationError(PlaylistPorterError):
    """Raised when there's a configuration issue."""


class ValidationError(PlaylistPorterError):
    """Raised when data validation fails."""


class AuthenticationError(PlaylistPorterError):
    """Raised when authentication fails."""


class AuthorizationError(PlaylistPorterError):
    """Raised when authorization fails."""


class SpotifyAPIError(PlaylistPorterError):
    """Raised when Spotify API calls fail."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_response: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_response = error_response


class StorageError(PlaylistPorterError):
    """Raised when storage operations fail."""

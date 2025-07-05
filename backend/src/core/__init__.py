"""Core package exports - Configuration and Exceptions only."""

from src.core.config import (
    AppConfig,
    SpotifyConfig,
    app_config,
    spotify_config,
)
from src.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    PlaylistPorterError,
    SpotifyAPIError,
    StorageError,
    ValidationError,
)

__all__ = [
    # Config
    "AppConfig",
    "SpotifyConfig",
    "app_config",
    "spotify_config",
    # Exceptions
    "PlaylistPorterError",
    "AuthenticationError",
    "SpotifyAPIError",
    "ValidationError",
    "ConfigurationError",
    "StorageError",
]

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Main application configuration."""

    # App settings
    title: str = "Playlist Porter"
    description: str = "Modern playlist transfer service"
    version: str = "2.0.0"
    debug: bool = False
    environment: str = "production"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


class SpotifyConfig(BaseSettings):
    """Spotify configuration."""

    client_id: str = Field(default="", description="Spotify Client ID")
    client_secret: str = Field(default="", description="Spotify Client Secret")

    model_config = SettingsConfigDict(
        env_prefix="SPOTIFY_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> tuple[AppConfig, SpotifyConfig]:
    """Get all configurations."""
    return AppConfig(), SpotifyConfig()


# Global instances
app_config, spotify_config = get_settings()

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


class SupabaseConfig(BaseSettings):
    """Supabase configuration."""

    url: str = Field(default="", description="Supabase URL")
    anon_key: str = Field(default="", description="Supabase Anonymous Key")
    service_key: str = Field(default="", description="Supabase Service Key")
    jwt_secret: str = Field(default="", description="Supabase JWT Secret")

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AuthConfig(BaseSettings):
    """Authentication configuration."""

    jwt_algorithm: str = Field(default="HS256", description="JWT Algorithm")
    access_token_expire_minutes: int = Field(
        default=15, description="Access token lifetime"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token lifetime"
    )

    # Cookie settings
    cookie_secure: bool = Field(default=True, description="Secure cookies")
    cookie_samesite: str = Field(default="strict", description="SameSite policy")
    cookie_domain: str | None = Field(default=None, description="Cookie domain")

    model_config = SettingsConfigDict(
        env_prefix="AUTH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> tuple[AppConfig, SpotifyConfig, SupabaseConfig, AuthConfig]:
    """Get all configurations."""
    return AppConfig(), SpotifyConfig(), SupabaseConfig(), AuthConfig()


app_config, spotify_config, supabase_config, auth_config = get_settings()

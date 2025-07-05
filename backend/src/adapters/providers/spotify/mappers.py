"""Mappers to convert Spotify API data to domain models."""

from src.domain.models.playlist import Playlist
from src.domain.models.track import Album, Artist, Track
from src.domain.models.user import User


class SpotifyMappers:
    """Mappers to convert Spotify API data to domain models."""

    @staticmethod
    def playlist_from_api(spotify_data: dict) -> Playlist:
        """Convert Spotify playlist data to domain Playlist."""
        return Playlist(
            id=spotify_data["id"],
            name=spotify_data["name"],
            description=spotify_data.get("description", ""),
            tracks_count=spotify_data["tracks"]["total"],
            is_public=spotify_data.get("public", False),
            is_collaborative=spotify_data.get("collaborative", False),
            owner_id=spotify_data["owner"]["id"],
            owner_name=spotify_data["owner"].get("display_name"),
            external_id=spotify_data["id"],
            provider="spotify",
            external_url=spotify_data.get("external_urls", {}).get("spotify", ""),
            image_url=spotify_data["images"][0]["url"]
            if spotify_data.get("images")
            else None,
            snapshot_id=spotify_data.get("snapshot_id"),
            uri=spotify_data.get("uri", f"spotify:playlist:{spotify_data['id']}"),
            href=spotify_data.get("href", ""),
        )

    @staticmethod
    def track_from_api(spotify_data: dict) -> Track:
        """Convert Spotify track data to domain Track."""
        # Convert Spotify artists to domain Artist objects
        artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                external_id=artist["id"],
                provider="spotify",
                external_url=artist.get("external_urls", {}).get("spotify", ""),
                uri=artist.get("uri", f"spotify:artist:{artist['id']}"),
            )
            for artist in spotify_data["artists"]
        ]

        # Convert Spotify album to domain Album object
        album_data = spotify_data["album"]
        album_artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                external_id=artist["id"],
                provider="spotify",
                external_url=artist.get("external_urls", {}).get("spotify", ""),
                uri=artist.get("uri", f"spotify:artist:{artist['id']}"),
            )
            for artist in album_data["artists"]
        ]

        album = Album(
            id=album_data["id"],
            name=album_data["name"],
            external_id=album_data["id"],
            provider="spotify",
            external_url=album_data.get("external_urls", {}).get("spotify", ""),
            uri=album_data.get("uri", f"spotify:album:{album_data['id']}"),
            release_date=album_data.get("release_date"),
            artists=album_artists,
            image_url=album_data["images"][0]["url"]
            if album_data.get("images")
            else None,
        )

        return Track(
            id=spotify_data["id"],
            title=spotify_data["name"],
            artists=artists,
            album=album,
            duration_ms=spotify_data["duration_ms"],
            external_uri=spotify_data["uri"],
            external_id=spotify_data["id"],
            provider="spotify",
            external_url=spotify_data.get("external_urls", {}).get("spotify", ""),
            preview_url=spotify_data.get("preview_url"),
            is_explicit=spotify_data.get("explicit", False),
            popularity=spotify_data.get("popularity", 0),
            track_number=spotify_data.get("track_number"),
            disc_number=spotify_data.get("disc_number"),
        )

    @staticmethod
    def user_from_api(spotify_data: dict) -> User:
        """Convert Spotify user data to domain User."""
        return User(
            id=spotify_data["id"],
            email=spotify_data.get("email"),
            display_name=spotify_data.get("display_name"),
            external_id=spotify_data["id"],
            provider="spotify",
            external_url=spotify_data.get("external_urls", {}).get("spotify", ""),
            image_url=spotify_data["images"][0]["url"]
            if spotify_data.get("images")
            else None,
            country=spotify_data.get("country"),
            followers_count=spotify_data.get("followers", {}).get("total", 0),
        )

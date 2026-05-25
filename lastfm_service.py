import requests
import random

# Key Points: Tek bir yerde tanımlanmış Base URL
LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFMService:

    ERA_MAP = {
        "1970s": ["70s", "1970s"],
        "1980s": ["80s", "1980s"],
        "1990s": ["90s", "1990s"],
        "2000s": ["00s", "2000s"],
        "2010s": ["2010s"],
        "2020s": ["2020s"]
    }

    GENRE_MAP = {
        "Pop": ["pop"],
        "Rock": ["rock"],
        "Hip-Hop / Rap": ["hip hop", "rap"],
        "Electronic": ["electronic"],
        "Indie": ["indie", "indie rock"],
        "R&B / Soul": ["rnb", "soul"],
        "Jazz": ["jazz"],
        "Metal": ["metal"],
        "Türk Pop": ["turkce pop", "turkish pop"],
        "Klasik": ["classical"]
    }

    def __init__(self, api_key):
        self.api_key = api_key

    def build_lastfm_tags(self, genre, era, mood_tags):

        genre_tags = self.GENRE_MAP.get(genre, [])
        era_tags = self.ERA_MAP.get(era, [])

        hybrid_tags = []

        for era_tag in era_tags:
            for genre_tag in genre_tags:
                hybrid_tags.append(f"{era_tag} {genre_tag}")

        final_tags = (
            hybrid_tags +
            genre_tags +
            era_tags +
            mood_tags[:2]
        )

        # duplicate temizle
        final_tags = list(dict.fromkeys(final_tags))

        return final_tags

    def fetch_tracks_by_tag(self, tag, limit=35):

        # REQUIREMENT 1:
        # requests + tag.gettoptracks

        params = {
            "method": "tag.gettoptracks",
            "tag": tag,
            "limit": limit,
            "api_key": self.api_key,
            "format": "json"
        }

        headers = {
            "User-Agent": "AlbumCoverStudio/1.0"
        }

        try:
            response = requests.get(
                LASTFM_BASE_URL,
                params=params,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            return data.get("tracks", {}).get("track", [])

        except Exception:
            return []

    def build_tracklist(self, tags, requested_count):

        all_tracks = []
        seen_songs = set()

        # REQUIREMENT 1:
        # multiple tag combine

        for tag in tags:

            tracks = self.fetch_tracks_by_tag(tag, limit=40)

            for track in tracks:

                name = track.get("name", "").strip()

                artist_data = track.get("artist", {})

                artist_name = (
                    artist_data.get("name", "")
                    if isinstance(artist_data, dict)
                    else str(artist_data)
                ).strip()

                url = track.get("url", "").strip()

                if not name or not artist_name:
                    continue

                unique_key = (
                    f"{name.lower()}|||{artist_name.lower()}"
                )

                # REQUIREMENT 5:
                # duplicate engelleme

                if unique_key not in seen_songs:

                    seen_songs.add(unique_key)

                    all_tracks.append({
                        "name": name,
                        "artist": artist_name,
                        "url": url
                    })

        # shuffle
        random.shuffle(all_tracks)

        # fallback sistemi
        if len(all_tracks) < requested_count:

            fallback_tags = [
                "pop",
                "rock",
                "hip hop",
                "electronic",
                "indie",
                "jazz",
                "metal",
                "turkish pop",
                "classical"
            ]

            for tag in fallback_tags:

                tracks = self.fetch_tracks_by_tag(tag, limit=20)

                for track in tracks:

                    name = track.get("name", "").strip()

                    artist_data = track.get("artist", {})

                    artist_name = (
                        artist_data.get("name", "")
                        if isinstance(artist_data, dict)
                        else str(artist_data)
                    ).strip()

                    url = track.get("url", "").strip()

                    if not name or not artist_name:
                        continue

                    unique_key = (
                        f"{name.lower()}|||{artist_name.lower()}"
                    )

                    if unique_key not in seen_songs:

                        seen_songs.add(unique_key)

                        all_tracks.append({
                            "name": name,
                            "artist": artist_name,
                            "url": url
                        })

                    if len(all_tracks) >= requested_count:
                        break

                if len(all_tracks) >= requested_count:
                    break

        return all_tracks[:requested_count]
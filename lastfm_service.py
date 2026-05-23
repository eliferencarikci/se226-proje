import requests

LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFMService:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_tracks_by_tag(self, tag, limit=15):
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

        response = requests.get(
            LASTFM_BASE_URL,
            params=params,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data.get("tracks", {}).get("track", [])

    def build_tracklist(self, tags, requested_count):
        all_tracks = []
        seen = set()

        for tag in tags:
            tracks = self.fetch_tracks_by_tag(tag)

            for track in tracks:
                name = track.get("name", "Unknown")
                artist = track.get("artist", {}).get("name", "Unknown")
                url = track.get("url", "")

                unique_key = f"{name.lower()}-{artist.lower()}"

                if unique_key not in seen:
                    seen.add(unique_key)

                    all_tracks.append({
                        "name": name,
                        "artist": artist,
                        "url": url
                    })

                if len(all_tracks) >= requested_count:
                    return all_tracks

        return all_tracks[:requested_count]
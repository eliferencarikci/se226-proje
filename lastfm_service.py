import requests

# Key Points: Tek bir yerde tanımlanmış Base URL
LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"


class LastFMService:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_tracks_by_tag(self, tag, limit=35):
        # REQUIREMENT 1: requests kütüphanesi ve tag.gettoptracks kullanımı
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
            response = requests.get(LASTFM_BASE_URL, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("tracks", {}).get("track", [])
        except Exception:
            return []

    def build_tracklist(self, tags, requested_count):
        # REQUIREMENT 1 & 5: Birden fazla etiketi birleştirme ve filtreleme
        all_tracks = []
        seen_songs = set()

        for tag in tags:
            tracks = self.fetch_tracks_by_tag(tag, limit=40)

            for track in tracks:
                name = track.get("name", "").strip()
                artist_data = track.get("artist", {})
                artist_name = artist_data.get("name", "") if isinstance(artist_data, dict) else str(artist_data)
                artist_name = artist_name.strip()
                url = track.get("url", "").strip()

                if not name or not artist_name:
                    continue

                # REQUIREMENT 5: Duplicate (mükerrer) şarkı engelleme kontrolü
                unique_key = f"{name.lower()}|||{artist_name.lower()}"
                if unique_key not in seen_songs:
                    seen_songs.add(unique_key)
                    all_tracks.append({
                        "name": name,
                        "artist": artist_name,
                        "url": url
                    })

                # İstenen sayıya ulaşıldığında bitir
                if len(all_tracks) >= requested_count:
                    return all_tracks

        return all_tracks[:requested_count]

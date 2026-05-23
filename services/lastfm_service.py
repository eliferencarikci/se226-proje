import requests
import webbrowser
from models.track import Track

LASTFM_BASE_URL = "https://ws.audioscrobbler.com/2.0/"
LASTFM_API_KEY = "1093b73660eca2814acb8ca879408419"

def fetch_tracks_by_tag(tag: str, limit: int = 10) -> list:
    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "limit": limit,
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }
    headers = {"User-Agent": "AlbumCoverStudio/1.0"}

    try:
        response = requests.get(
            LASTFM_BASE_URL,
            params=params,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        raw_tracks = data.get("tracks", {}).get("track", [])

        result = []
        for item in raw_tracks:
            title = item.get("name", "Unknown")
            artist = item.get("artist", {}).get("name", "Unknown")
            url = item.get("url", "")
            result.append(Track(title, artist, url))

        return result

    except requests.RequestException as e:
        print(f"[LastFM] '{tag}' tag'i için istek başarısız: {e}")
        return []


def fetch_tracks_for_tags(tags: list, limit_per_tag: int = 15) -> list:
    all_tracks = []

    for tag in tags:
        tracks = fetch_tracks_by_tag(tag, limit=limit_per_tag)
        all_tracks.extend(tracks)
        print(f"[LastFM] '{tag}' → {len(tracks)} şarkı bulundu")

    return all_tracks


def remove_duplicates(tracks: list) -> list:
    seen = set()
    unique_tracks = []

    for track in tracks:
        key = f"{track.title.lower()}|{track.artist.lower()}"

        if key not in seen:
            seen.add(key)
            unique_tracks.append(track)

    return unique_tracks


def get_tracklist(tags: list, track_count: int) -> list:
    print(f"[LastFM] {len(tags)} tag için şarkılar çekiliyor: {tags}")

    all_tracks = fetch_tracks_for_tags(tags, limit_per_tag=20)
    unique_tracks = remove_duplicates(all_tracks)
    print(f"[LastFM] Toplam benzersiz şarkı: {len(unique_tracks)}")

    if len(unique_tracks) < track_count:
        print(f"[LastFM] Uyarı: {track_count} şarkı istendi ama sadece {len(unique_tracks)} bulundu.")
        return unique_tracks

    return unique_tracks[:track_count]


def open_track_url(url: str):
    if url:
        webbrowser.open(url)
    else:
        print("[LastFM] Bu şarkı için URL bulunamadı.")
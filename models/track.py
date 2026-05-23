class Track:
    def __init__(self, title: str, artist: str, url: str):
        self.title = title
        self.artist = artist
        self.url = url

    def __repr__(self):
        return f"Track('{self.title}' by '{self.artist}')"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "artist": self.artist,
            "url": self.url
        }
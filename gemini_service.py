import json
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_album_data(self, journal_text, genre, era, track_count):
        prompt = f"""
        Based on the user's mood journal below, generate a fictional album concept that STRICTLY matches the selected music genre and historical era.

        CRITICAL INSTRUCTIONS FOR GENRE AND ERA:
        1. The requested genre is "{genre}" and the era is "{era}".
        2. The generated "album_name", "artist_name", and "mood_description" MUST reflect the authentic musical culture, language, and aesthetic of that specific period and genre.
        3. If the genre is "Türk Pop", ALL generated concept elements MUST be in Turkish.

        CRITICAL INSTRUCTION FOR LAST.FM TAGS (DANGER ZONE):
        The "lastfm_tags" array MUST contain 4-6 specific, lower-case tags that exist on Last.fm.
        - If the genre is "Türk Pop", you MUST NOT include generic international tags like "pop", "dance", or "pop rock" alone, because they mix with western music.
        - For "Türk Pop", you MUST strictly use local Turkish tags depending on the selected era:
          * If era is "2020s": ["turkce pop", "turkish pop", "turkish", "2020s pop"]
          * If era is "2010s": ["2010lar turkce pop", "turkce pop", "turkish pop", "turkish"]
          * If era is "2000s": ["2000ler turkce pop", "turkce pop", "turkish pop", "turkish"]
          * If era is "1990s": ["90lar turkce pop", "90s turkish pop", "turkce pop", "turkish pop"]
          * If era is "1980s" or "1970s": ["70ler", "80ler", "turkce pop", "turkish pop", "turkish rock"]
        - If the genre is NOT "Türk Pop", combine the genre with the requested era normally (e.g., "2000s indie", "80s rock").

        Schema:
        {{
          "album_name": "string",
          "artist_name": "string",
          "year": "string",
          "label": "string",
          "mood_description": "string",
          "cover_prompt": "string",
          "lastfm_tags": ["tag1", "tag2", "tag3", "tag4"]
        }}

        User Journal:
        "{journal_text}"

        Genre: {genre}
        Era: {era}
        Track Count: {track_count}
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )

        text = response.text.strip()
        return json.loads(text)
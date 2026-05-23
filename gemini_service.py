import json
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self, api_key):

        self.client = genai.Client(api_key=api_key)

    def generate_album_data(self, journal_text, genre, era, track_count):
        prompt = f"""
Based on the user's mood journal below, generate a fictional album.

Return ONLY valid JSON.

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
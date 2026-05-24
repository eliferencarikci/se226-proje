import json
from google import genai
from google.genai import types


class GeminiService:

    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

    def generate_album_data(self, journal_text, genre, era, track_count):
       
        prompt = f"""
Based on the user's mood journal below, generate a fictional album concept.

Return ONLY valid JSON matching the schema precisely.

CRITICAL INSTRUCTION FOR LAST.FM TAGS:
The "lastfm_tags" array MUST contain 4-6 specific, lower-case tags that exist on Last.fm.
- Since the user selected the genre "{genre}", you MUST prioritize tags that reflect this specific music culture and geography.
- If the genre is "Türk Pop", you MUST use tags like ["turkish pop", "turkce pop", "turkish", "90lar turkce pop"] to ensure the system queries real Turkish songs. Do NOT just return generic tags like ["pop", "dance"].
- Combine the genre with the requested era ("{era}") in the tags if applicable (e.g., "80s rock", "90s pop").

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
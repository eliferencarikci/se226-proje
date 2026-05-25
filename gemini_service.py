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

        CRITICAL INSTRUCTION FOR COVER PROMPT:
        The "cover_prompt" field MUST be a vivid visual description that directly reflects the emotional tone of the user's journal text.
        - Identify the core emotion (e.g. heartbreak, joy, loneliness, rage) from the journal text.
        - Describe a scene, color palette, lighting, and atmosphere that embodies that emotion.
        - The style must match the {era} {genre} aesthetic.
        - Do NOT include any text, letters, or typography in the image.
        - Example for heartbreak: "A lone figure standing in rain-soaked empty streets at night, cold blue and gray tones, blurred city lights in background, melancholic and cinematic atmosphere"

        CRITICAL INSTRUCTION FOR LAST.FM TAGS:
        The "lastfm_tags" array must contain 4-6 tags. HALF of the tags must reflect the EMOTIONAL MOOD of the journal text, the other half must reflect the genre and era.
        - Mood tags: extract the dominant emotion from the journal (e.g. "heartbreak", "sad", "melancholic", "lonely", "ayrılık", "hüzün")
        - Genre/era tags for "Türk Pop":
        * If era is "2020s": ["turkce pop", "turkish pop"]
        * If era is "2010s": ["turkce pop", "turkish pop"]
        * If era is "2000s": ["2000ler turkce pop", "turkce pop"]
        * If era is "1990s": ["90lar turkce pop", "turkce pop"]
        * If era is "1980s" or "1970s": ["turkce pop", "turkish rock"]
        - Genre/era tags for other genres: combine genre with era (e.g. "2000s indie", "80s rock")

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
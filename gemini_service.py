import json
import google.generativeai as genai


class GeminiService:
    def __init__(self, api_key):
        # Kılavuzdaki resmi konfigürasyon yapısı
        genai.configure(api_key=api_key)
        # JSON dönmesi için kesinleştirilmiş konfigürasyon
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )

    def generate_album_data(self, journal_text, genre, era, track_count):
        # REQUIREMENT 3 & 4: JSON şeması ve parametrelerin prompta aktarımı
        prompt = f"""
        Based on the user's mood journal below, generate a fictional album concept that STRICTLY matches the requested music genre and historical era.

        CRITICAL PARAMETERS:
        - Music Genre: {genre}
        - Historical Era/Decade: {era} (e.g., 1970s, 1980s, etc.)
        - Track Count requested: {track_count}

        STRICT RULES FOR METADATA:
        1. "album_name" and "artist_name" must be entirely FICTIONAL. Do not use real albums or artists.
        2. If the genre is "Türk Pop", ALL fields except "lastfm_tags" and "cover_prompt" MUST be written in Turkish.
        3. The "year" field must be a specific, realistic year within the requested era (e.g., if era is 1990s, year could be 1994).
        4. "label" should be a realistic fictional record label name fitting the genre and era.

        STRICT RULES FOR COVER PROMPT:
        - "cover_prompt" must be a vivid, descriptive visual prompt for an AI image generator.
        - It must heavily reflect the emotional vibe of the journal entry (e.g., melancholy, isolation, joy).
        - DO NOT include any text, letters, typography, or words like "text", "label", "album cover" inside the prompt itself.

        STRICT RULES FOR LAST.FM TAGS ("lastfm_tags"):
        - Provide an array of exactly 5-6 lowercase strings.
        - To get REAL songs from that specific era and genre from the Last.fm API, you MUST generate accurate hybrid tags.
        - Examples of valid historical/genre tags for Last.fm:
          * For 1970s Rock: ["70s rock", "1970s", "classic rock", "rock"]
          * For 1990s Hip-Hop: ["90s hip hop", "90s rap", "old school hip hop"]
          * For 2000s Indie: ["2000s indie", "00s indie", "indie rock"]
          * For Türk Pop 1990s: ["90lar turkce pop", "90s turkish", "turkce pop"]
          * For Türk Pop 2000s: ["2000ler turkce pop", "turkish pop"]
        - Blend these with 1 or 2 emotional mood tags from the journal (e.g., "melancholic", "sad", "chill", "hüzünlü").

        Return ONLY a valid JSON object matching this schema:
        {{
          "album_name": "Fictional Album Title",
          "artist_name": "Fictional Artist Name",
          "year": "YYYY",
          "label": "Fictional Record Label",
          "mood_description": "A detailed explanation of how the album's concept matches the user's journal entry.",
          "cover_prompt": "A vivid description of the artwork scene without any text.",
          "lastfm_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
        }}

        User Journal:
        "{journal_text}"
        """

        response = self.model.generate_content(prompt)
        text = response.text.strip()

        # REQUIREMENT 4: Markdown kod çitlerini temizleme mekanizması
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        return json.loads(text)

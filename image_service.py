import io
import requests
from PIL import Image
from urllib.parse import quote


class ImageService:
    def generate_cover(self, prompt, genre, era):
        # REQUIREMENT 6: Seçilen müzik türüne özel görsel tarz tanımları
        genre_styles = {
            "Pop": "vibrant colors, clean modern pop aesthetic, glossy, professional studio lighting",
            "Rock": "grungy textures, high contrast, dramatic shadows, vintage rock vinyl cover style",
            "Hip-Hop / Rap": "urban street art, parental advisory layout background, cinematic moody lighting",
            "Electronic": "cyberpunk neon lights, futuristic synthwave aesthetic, glowing retro-futuristic grid elements",
            "Indie": "lo-fi photography style, vintage film grain, warm indie aesthetics, artsy and melancholic",
            "R&B / Soul": "smooth velvety textures, warm neon glow, elegant and sensual mood, rich warm colors",
            "Jazz": "smoky jazz club atmosphere, retro vinyl record feel, classic monochrome or sepia photography",
            "Metal": "dark metal aesthetic, aggressive symbolism, high contrast dramatic lighting",
            "Türk Pop": "bright Mediterranean saturated colors, energetic retro Turkish pop album artwork presentation",
            "Klasik": "classical oil painting style, fine art textures, elegant orchestral hall atmosphere, timeless artwork",
        }

        visual_style = genre_styles.get(genre, "artistic digital album cover design")

        # REQUIREMENT 6: Gemini görsel promptu ile müzik türünün görsel stilini birleştirme
        full_prompt = (
            f"Official square music album cover art from the {era}. "
            f"Vibe: {prompt}. "
            f"Visual style: {visual_style}. "
            f"Professional album cover look. Strictly no text, no letters, no words, no typography."
        )

        encoded = quote(full_prompt)
        # Öntanımlı servis: Pollinations.ai (API anahtarı ve kayıt istemez)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=600&height=600&nologo=true"

        response = requests.get(url, timeout=90)
        response.raise_for_status()

        return Image.open(io.BytesIO(response.content)).convert("RGB")

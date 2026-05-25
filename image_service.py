import io
from urllib.parse import quote
from PIL import Image
import requests

class ImageService:

    def generate_cover(self, prompt, genre, era="modern"):

        genre_styles = {
            "Pop": "vibrant colors, clean modern pop aesthetic, glossy, professional studio lighting",
            "Rock": "grungy textures, edgy rock concert vibe, high contrast, dramatic shadows",
            "Hip-Hop / Rap": "urban street art, parental advisory style, graffiti elements, cinematic moody lighting",
            "Electronic": "cyberpunk neon lights, futuristic synthwave aesthetic, retro-futurism, glowing elements",
            "Indie": "lo-fi photography style, vintage film grain, warm indie aesthetics, melancholic and artsy",
            "R&B / Soul": "smooth velvety textures, warm neon glow, elegant and sensual mood, rich colors",
            "Jazz": "smoky jazz club atmosphere, monochrome with golden accents, retro vinyl record feel",
            "Metal": "dark metal aesthetic, aggressive symbolism, high contrast monochrome or fiery lighting",
            "Türk Pop": "bright Mediterranean colors, energetic album cover, modern Turkish pop aesthetic",
            "Klasik": "classical oil painting style, fine art textures, elegant orchestral hall atmosphere, timeless",
        }

        visual_style = genre_styles.get(
            genre, "artistic digital art, professional album cover design"
        )


        full_prompt = (
            f"Official square album cover art from the {era}. "
            f"Mood and emotion: {prompt}. "
            f"Visual style: {visual_style}. "
            f"The cover art must visually reflect the emotional tone described. "
            f"No text, no typography, purely visual artwork."
        )

        encoded = quote(full_prompt)


        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=600&height=600&enhance=false"
        )

        response = requests.get(url, timeout=90)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        return image
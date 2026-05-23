import io
import requests

from PIL import Image
from urllib.parse import quote


class ImageService:
    def generate_cover(self, prompt, genre):
        full_prompt = (
            f"Album cover art, {genre} style, {prompt}, "
            f"cinematic lighting, high quality, square album art"
        )

        encoded = quote(full_prompt)

        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=600&height=600&nologo=true"
        )

        response = requests.get(url, timeout=90)
        response.raise_for_status()

        image = Image.open(io.BytesIO(response.content)).convert("RGB")

        return image
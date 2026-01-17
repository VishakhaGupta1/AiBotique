import os
import base64
from typing import Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _client():
    if OpenAI is None:
        raise RuntimeError("openai package not installed")
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    return OpenAI(api_key=OPENAI_API_KEY)


def generate_outfit_image(prompt: str, size: str = "1024x1024") -> str:
    """
    Uses OpenAI DALL·E (Images API) to generate an outfit image and returns base64 PNG.
    """
    client = _client()
    res = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        n=1,
        response_format="b64_json",
    )
    b64_png = res.data[0].b64_json
    return b64_png

import requests
from io import BytesIO
from PIL import Image
import pytesseract

HEADERS = {
    "User-Agent": "DSCI560-Lab5-Bot/1.0"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def extract_ocr_text(image_url):
    if not image_url:
        return ""

    try:
        response = requests.get(
            image_url,
            headers=HEADERS,
            timeout=10,
            allow_redirects=True
        )
        response.raise_for_status()

        # Validate content type
        content_type = response.headers.get("Content-Type", "").lower()
        if "image" not in content_type:
            return ""

        # Prevent very large images
        if len(response.content) > MAX_IMAGE_SIZE:
            return ""

        img = Image.open(BytesIO(response.content)).convert("L")

        text = pytesseract.image_to_string(img, lang="eng")

        return text.strip()

    except Exception:
        return ""

import requests
from io import BytesIO
from PIL import Image
import pytesseract


HEADERS = {
    "User-Agent": "dsci560_lab5_script"
}


def extract_ocr_text(image_url):
    """
    Downloads an image and extracts text using Tesseract OCR.
    Returns extracted text or empty string on failure.
    """

    if not image_url:
        return ""

    try:
        response = requests.get(image_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        # Convert to RGB (important for some image formats)
        img = img.convert("RGB")

        text = pytesseract.image_to_string(img)

        return text.strip()

    except Exception as e:
        # Fail silently (important so scraper doesn't crash)
        print(f"OCR failed for {image_url}: {e}")
        return ""

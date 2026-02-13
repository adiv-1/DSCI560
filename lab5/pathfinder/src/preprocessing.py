import re
from datetime import datetime


def clean_text(text):
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove non-alphanumeric characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def mask_author(author):
    if not author:
        return "user_unknown"

    return f"user_{abs(hash(author)) % 100000}"


def convert_timestamp(ts):
    try:
        return datetime.fromtimestamp(ts)
    except Exception:
        return None


def build_document(post):
    """
    Builds the full text document used for embeddings.
    Includes:
        - Cleaned title
        - Cleaned body
        - Cleaned OCR text (if exists)
    """

    title = clean_text(post.get("title", ""))
    body = clean_text(post.get("selftext", ""))
    ocr_text = clean_text(post.get("ocr_text", ""))

    full_text = f"{title} {body} {ocr_text}".strip()

    return full_text

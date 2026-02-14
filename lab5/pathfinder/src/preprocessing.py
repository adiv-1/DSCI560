import re
import hashlib
from datetime import datetime, timezone

MASK_SALT = "DSCI560_lab5"


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def mask_author(author):
    author = (author or "").strip()

    if not author or author == "[deleted]":
        return "[deleted]"

    hashed = hashlib.sha256(
        (MASK_SALT + author).encode("utf-8")
    ).hexdigest()

    return f"user_{hashed[:10]}"


def convert_timestamp(ts):
    if isinstance(ts, int):
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    try:
        return datetime.fromisoformat(
            ts.replace("Z", "+00:00")
        ).astimezone(timezone.utc)
    except Exception:
        return None


def build_document(post):
    title = clean_text(post.get("title", ""))
    body = clean_text(post.get("selftext", ""))
    ocr_text = clean_text(post.get("ocr_text", ""))

    return f"{title} {body} {ocr_text}".strip()

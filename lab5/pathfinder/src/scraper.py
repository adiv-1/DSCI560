import requests
import time
import hashlib
from datetime import datetime, timezone
from io import BytesIO
from typing import List, Dict, Optional

from bs4 import BeautifulSoup
from PIL import Image
import pytesseract


BASE_URL = "https://old.reddit.com"
USER_AGENT = "DSCI560-Lab5-Bot/1.0"
HEADERS = {"User-Agent": USER_AGENT}

REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 2
MASK_SALT = "DSCI560_lab5"
MAX_IMAGE_SIZE = 5 * 1024 * 1024


def mask_username(username: Optional[str]) -> str:
    user = (username or "").strip()
    if not user or user == "[deleted]":
        return "[deleted]"
    return "user_" + hashlib.sha256((MASK_SALT + user).encode()).hexdigest()[:10]


def _extract_ocr_text(image_url: str) -> str:
    if not image_url:
        return ""
    try:
        resp = requests.get(image_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()

        if "image" not in resp.headers.get("Content-Type", "").lower():
            return ""

        if len(resp.content) > MAX_IMAGE_SIZE:
            return ""

        img = Image.open(BytesIO(resp.content)).convert("L")
        return pytesseract.image_to_string(img, lang="eng").strip()
    except Exception:
        return ""


def _parse_post(div, subreddit: str) -> Dict:
    post_id = div.get("data-fullname", "").replace("t3_", "")

    title_tag = div.find("a", class_="title")
    title = title_tag.text.strip() if title_tag else ""

    author_tag = div.find("a", class_="author")
    author = author_tag.text.strip() if author_tag else "[deleted]"

    score_tag = div.find("div", class_="score unvoted")
    score_text = score_tag.text if score_tag else "0"
    try:
        score = int(score_text.replace(" points", "").replace(" point", "").replace("k", "000"))
    except:
        score = 0

    comments_tag = div.find("a", string=lambda x: x and "comment" in x.lower())
    comments = 0
    if comments_tag:
        try:
            comments = int(comments_tag.text.split()[0])
        except:
            comments = 0

    time_tag = div.find("time")
    created_iso = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else ""
    try:
        created_dt = datetime.fromisoformat(created_iso.replace("Z", "+00:00"))
        created_utc = int(created_dt.timestamp())
    except:
        created_utc = 0
        created_dt = datetime.now(timezone.utc)

    image_url = ""
    link_tag = div.find("a", class_="thumbnail")
    if link_tag and link_tag.get("href"):
        image_url = link_tag["href"]

    ocr_text = _extract_ocr_text(image_url) if image_url else ""

    return {
        "subreddit": subreddit,
        "id": post_id,
        "title": title,
        "selftext": "",  # old.reddit list view does not include body
        "author": author,
        "author_masked": mask_username(author),
        "created_utc": created_utc,
        "created_iso": created_dt.isoformat(),
        "score": score,
        "num_comments": comments,
        "url": title_tag["href"] if title_tag and title_tag.get("href") else "",
        "image_url": image_url,
        "ocr_text": ocr_text
    }


def fetch_posts(subreddit: str, total_posts: int) -> List[Dict]:

    posts: List[Dict] = []
    after = None

    while len(posts) < total_posts:

        url = f"{BASE_URL}/r/{subreddit}/new/"
        if after:
            url += f"?after={after}"

        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")

        post_divs = soup.find_all("div", class_="thing")

        if not post_divs:
            break

        for div in post_divs:
            if len(posts) >= total_posts:
                break

            if div.get("data-promoted") == "true":
                continue

            parsed = _parse_post(div, subreddit)

            if parsed["id"]:
                posts.append(parsed)

        next_button = soup.find("span", class_="next-button")
        if next_button and next_button.find("a"):
            next_link = next_button.find("a")["href"]
            after = next_link.split("after=")[-1] if "after=" in next_link else None
        else:
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    return posts

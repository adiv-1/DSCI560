import requests
import time
from ocr import extract_ocr_text

BASE_URL = "https://www.reddit.com"
HEADERS = {"User-Agent": "dsci560_lab5_script"}

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def fetch_posts(subreddit, total_posts):
    posts = []
    seen_ids = set()
    after = None

    while len(posts) < total_posts:
        url = f"{BASE_URL}/r/{subreddit}/new.json?limit=100"
        if after:
            url += f"&after={after}"

        try:
            r = requests.get(url, headers=HEADERS, timeout=10)

            if r.status_code == 429:
                print("Rate limited. Sleeping 5 seconds...")
                time.sleep(5)
                continue

            r.raise_for_status()
            data = r.json()

        except Exception as e:
            print(f"Request error: {e}")
            break

        children = data.get("data", {}).get("children", [])
        if not children:
            break

        for child in children:
            p = child.get("data", {})
            post_id = p.get("id")

            if not post_id or post_id in seen_ids:
                continue

            # Skip promoted/sponsored posts
            if p.get("promoted") or p.get("is_sponsored"):
                continue

            seen_ids.add(post_id)

            # --- OCR Integration ---
            image_url = p.get("url", "")
            ocr_text = ""

            if image_url.lower().endswith(IMAGE_EXTENSIONS):
                print(f"Running OCR on image: {image_url}")
                ocr_text = extract_ocr_text(image_url)

            p["ocr_text"] = ocr_text

            posts.append(p)

            if len(posts) >= total_posts:
                break

        after = data.get("data", {}).get("after")
        if not after:
            break

        print(f"Collected {len(posts)} posts so far...")
        time.sleep(1)

    return posts

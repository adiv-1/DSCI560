import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ocr import extract_ocr_text

BASE_URL = "https://old.reddit.com"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")

# Multiple sort endpoints
SORT_URLS = [
    "/new/",
    "/hot/",
    "/top/?t=day",
    "/top/?t=week",
    "/top/?t=month",
    "/top/?t=year",
    "/top/?t=all",
    "/controversial/?t=all"
]


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    })
    return session


def fetch_posts(subreddit, total_posts):
    posts = []
    seen_ids = set()
    session = create_session()

    for sort_path in SORT_URLS:

        if len(posts) >= total_posts:
            break

        print(f"\nScraping sort: {sort_path}")

        url = f"{BASE_URL}/r/{subreddit}{sort_path}"

        while url and len(posts) < total_posts:

            try:
                response = session.get(url, timeout=15)

                if response.status_code == 429:
                    print("Rate limited. Sleeping 10 seconds...")
                    time.sleep(10)
                    continue

                response.raise_for_status()

            except Exception as e:
                print(f"Request error: {e}")
                break

            # Detect block / captcha page
            if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                print("Blocked by Reddit. Sleeping 15 seconds...")
                time.sleep(15)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            things = soup.find_all("div", class_="thing")

            if not things:
                print("No posts found on page. Moving to next sort.")
                break

            for thing in things:
                post_id = thing.get("data-id")

                if not post_id or post_id in seen_ids:
                    continue

                # Skip promoted posts
                if thing.get("data-promoted") == "true":
                    continue

                seen_ids.add(post_id)

                title_tag = thing.find("a", class_="title")
                title = title_tag.text.strip() if title_tag else ""

                author_tag = thing.find("a", class_="author")
                author = author_tag.text.strip() if author_tag else "[deleted]"

                score_tag = thing.find("div", class_="score unvoted")
                score = score_tag.get("title") if score_tag and score_tag.get("title") else "0"

                comments_tag = thing.find("a", string=lambda s: s and "comment" in s.lower())
                comments_text = comments_tag.text.strip() if comments_tag else "0 comments"

                time_tag = thing.find("time")
                created_utc = time_tag.get("datetime") if time_tag else None

                permalink = thing.get("data-permalink")
                full_link = urljoin(BASE_URL, permalink) if permalink else ""

                image_url = thing.get("data-url", "")
                ocr_text = ""

                if image_url and image_url.lower().endswith(IMAGE_EXTENSIONS):
                    print(f"OCR: {image_url}")
                    try:
                        ocr_text = extract_ocr_text(image_url)
                    except Exception as e:
                        print(f"OCR failed: {e}")

                post_data = {
                    "id": post_id,
                    "title": title,
                    "author": author,
                    "score": score,
                    "comments": comments_text,
                    "created_utc": created_utc,
                    "permalink": full_link,
                    "url": image_url,
                    "ocr_text": ocr_text
                }

                posts.append(post_data)

                if len(posts) >= total_posts:
                    break

            print(f"Collected {len(posts)} posts so far...")

            # Pagination
            next_button = soup.find("span", class_="next-button")
            if next_button and next_button.find("a"):
                url = next_button.find("a")["href"]
            else:
                url = None

            time.sleep(2)

    print(f"\nFinished. Total collected: {len(posts)}")
    return posts
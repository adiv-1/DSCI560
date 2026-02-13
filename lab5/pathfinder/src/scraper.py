import requests
import time
import random
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

# Rotating user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36"
]


def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
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
                response = session.get(url, timeout=20)

                if response.status_code == 429:
                    sleep_time = random.uniform(30, 60)
                    print(f"Rate limited. Sleeping {sleep_time:.1f} seconds...")
                    time.sleep(sleep_time)
                    continue

                response.raise_for_status()

            except Exception as e:
                print(f"Request error: {e}")
                break

            # Detect block / captcha page
            if "captcha" in response.text.lower() or "blocked" in response.text.lower():
                sleep_time = random.uniform(60, 120)
                print(f"Blocked by Reddit. Sleeping {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
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

                # Title
                title_tag = thing.find("a", class_="title")
                title = title_tag.text.strip() if title_tag else ""

                # Author
                author_tag = thing.find("a", class_="author")
                author = author_tag.text.strip() if author_tag else "[deleted]"

                # Score
                score_tag = thing.find("div", class_="score unvoted")
                score_raw = score_tag.get("title") if score_tag and score_tag.get("title") else "0"
                try:
                    score = int(score_raw)
                except:
                    score = 0

                # Comments
                comments_tag = thing.find("a", string=lambda s: s and "comment" in s.lower())
                comments_text = comments_tag.text.strip() if comments_tag else "0 comments"

                # Timestamp
                time_tag = thing.find("time")
                created_utc = time_tag.get("datetime") if time_tag else None

                # Permalink
                permalink = thing.get("data-permalink")
                full_link = urljoin(BASE_URL, permalink) if permalink else ""

                # OCR
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

            # Human-like delay
            sleep_time = random.uniform(3, 6)
            time.sleep(sleep_time)

    print(f"\nFinished. Total collected: {len(posts)}")
    return posts

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time


def fetch_posts_selenium(subreddit, total_posts):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # Set correct binary path
    options.binary_location = "/usr/bin/chromium-browser"

    # Set correct chromedriver path
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://www.reddit.com/r/{subreddit}/new/"
    driver.get(url)

    posts = []
    seen_ids = set()

    while len(posts) < total_posts:
        elements = driver.find_elements("css selector", "div[data-testid='post-container']")

        for el in elements:
            try:
                post_id = el.get_attribute("id")
                if not post_id or post_id in seen_ids:
                    continue

                title_el = el.find_element("tag name", "h3")
                title = title_el.text

                posts.append({
                    "id": post_id,
                    "title": title,
                    "selftext": "",
                    "author": "unknown",
                    "score": 0,
                    "num_comments": 0,
                    "created_utc": int(time.time()),
                    "ocr_text": ""
                })

                seen_ids.add(post_id)

                if len(posts) >= total_posts:
                    break

            except Exception:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    driver.quit()
    return posts

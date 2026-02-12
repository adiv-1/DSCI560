import requests
import sqlite3
import sys
import time

BASE_URL = "https://www.reddit.com"
HEADERS = {
    "User-Agent": "script:reddit_bs4.py:v0.1 (by /u/Powerpuff_girls560)"
}

CHUNK_SIZE = 100  # Max posts per request
SLEEP_BETWEEN_REQUESTS = 2  # Num seconds

def clear_db(db_name="reddit.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS posts")  # Drops existing content in reddit.db
    conn.commit()
    conn.close()

def get_posts(subreddit, total_posts):
    posts = []
    post_ids = set()
    after = None
    backoff = 2 # Start with 2 seconds

    while len(posts) < total_posts:
        url = f"{BASE_URL}/r/{subreddit}/.json?limit={CHUNK_SIZE}"
        if after:
            url += f"&after={after}"  # Get more posts

        response = requests.get(url, headers=HEADERS, timeout=10)  # Waits up to 10s for response
        if response.status_code == 429:
            time.sleep(backoff)
            backoff = min(backoff * 2, 60) # Max 60 seconds
            continue
        response.raise_for_status()

        data = response.json()
        list_of_posts = data.get("data", {}).get("children", [])
        if not list_of_posts:
            break  # No more posts

        before = len(posts)
        for post in list_of_posts:
            p = post["data"]
            if p["id"] in post_ids:
                continue  # Skip duplicates
            post_ids.add(p["id"])
            posts.append(
                {
                    "id": p["id"],
                    "title": p["title"].strip(),
                    "author": p["author"],
                    "score": p["score"],
                    "url": p["url"],
                    "comments": p["num_comments"],
                }
            )
            if len(posts) >= total_posts:
                break

        after = data.get("data", {}).get("after")  # Get next page
        if len(posts) != before:
            print(f"Scraped {len(posts)} posts so far...")
        if not after:
            break  # Reached last page

        time.sleep(SLEEP_BETWEEN_REQUESTS)  # Wait between requests

    return posts

def save_to_db(posts, db_name="reddit.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Use TEXT instead of CHAR for variable length
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        score INTEGER,
        url TEXT,
        comments INTEGER
    )
    """)

    for post in posts:
        cursor.execute("""
        INSERT OR IGNORE INTO posts VALUES (?, ?, ?, ?, ?, ?)
        """, (
            post["id"],
            post["title"],
            post["author"],
            post["score"],
            post["url"],
            post["comments"]
        ))

    conn.commit()
    conn.close()

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Enter a number of posts to scrape or 'all'")
        sys.exit(1)

    if sys.argv[1].lower() == "all":
        num_posts = float("inf")
    else:
        num_posts = int(sys.argv[1])

    # Clear database before starting
    clear_db("reddit.db")

    subreddit_name = "tech"
    posts = get_posts(subreddit_name, num_posts)
    save_to_db(posts)

    print(f"Scraping complete: Stored {len(posts)} posts")

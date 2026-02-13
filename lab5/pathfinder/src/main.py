import sys
import time

from preprocessing import build_document, mask_author, convert_timestamp
from db import (
    init_table,
    insert_post,
    update_embedding,
    update_cluster,
    get_connection
)
from embedding_cluster import (
    generate_embeddings,
    cluster_embeddings,
    closest_to_centroids,
    extract_cluster_keywords
)

# Default subreddit
SUBREDDIT = "careerguidance"
MAX_POSTS = 10000


def get_scraper(scraper_type):
    if scraper_type == "selenium":
        from selenium_scraper import fetch_posts_selenium as fetch_posts
        print("Using Selenium scraper.")
    else:
        from scraper import fetch_posts
        print("Using JSON scraper.")
    return fetch_posts


def run_once(fetch_posts_func, subreddit, total_posts):
    print(f"\nFetching {total_posts} posts from r/{subreddit}...")
    raw_posts = fetch_posts_func(subreddit, total_posts)
    print(f"Fetched {len(raw_posts)} posts")

    docs = []
    post_ids = []

    for i, p in enumerate(raw_posts):
        doc = build_document(p)

        insert_post((
            p["id"],
            doc,
            mask_author(p.get("author")),
            p.get("score", 0),
            p.get("num_comments", 0),
            convert_timestamp(p.get("created_utc", int(time.time())))
        ))

        docs.append(doc)
        post_ids.append(p["id"])

        if (i + 1) % 50 == 0:
            print(f"Saved {i + 1} posts...")

    if not docs:
        print("No documents fetched. Skipping this cycle.")
        return

    print("Generating embeddings...")
    embeddings = generate_embeddings(docs)

    print("Clustering embeddings...")
    labels, kmeans = cluster_embeddings(embeddings)

    print("Updating database with embeddings and cluster IDs...")
    for i in range(len(post_ids)):
        update_embedding(post_ids[i], embeddings[i].tolist())
        update_cluster(post_ids[i], int(labels[i]))

    print("\nRepresentative posts per cluster:")
    closest = closest_to_centroids(embeddings, labels, kmeans)

    for cluster_id, idx in closest.items():
        print(f"\nCluster {cluster_id}:")
        print(docs[idx][:400])

    print("\nCluster Keywords:")
    cluster_keywords = extract_cluster_keywords(docs, labels)

    for cluster_id, keywords in cluster_keywords.items():
        print(f"\nCluster {cluster_id} keywords:")
        print(", ".join(keywords))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_rows = cursor.fetchone()[0]
    conn.close()

    print(f"\nTotal rows currently in database: {total_rows}")
    print("Cycle complete.\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python main.py <interval_seconds> <posts_per_cycle> [json|selenium]")
        sys.exit(1)

    interval = int(sys.argv[1])
    posts_per_cycle = int(sys.argv[2])
    scraper_type = sys.argv[3].lower() if len(sys.argv) > 3 else "json"

    fetch_posts_func = get_scraper(scraper_type)

    init_table()

    while True:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM posts")
        total_rows = cursor.fetchone()[0]
        conn.close()

        if total_rows >= MAX_POSTS:
            print(f"\nReached {MAX_POSTS} posts. Stopping execution.")
            break

        remaining = MAX_POSTS - total_rows
        batch_size = min(posts_per_cycle, remaining)

        run_once(fetch_posts_func, SUBREDDIT, batch_size)

        print(f"Sleeping for {interval} seconds...")
        time.sleep(interval)
import sys
import time
import numpy as np
from datetime import datetime, timezone

from preprocessing import build_document, mask_author
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


SUBREDDITS = [
#    "careerguidance",
#    "jobs",
#    "cscareerquestions",
    "resume",
    "career"
]


def convert_timestamp(ts):
    if isinstance(ts, int):
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return datetime.utcnow()


def get_scraper():
    from scraper import fetch_posts
    print("Using JSON scraper.")
    return fetch_posts


def interactive_query_mode(kmeans):
    if kmeans is None:
        print("No clustering model available.")
        return

    print("\nEntering interactive query mode.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter query: ").strip()

        if user_input.lower() == "exit":
            print("Exiting interactive mode.")
            break

        if not user_input:
            continue

        query_embedding = generate_embeddings([user_input])

        centroids = kmeans.cluster_centers_
        distances = np.linalg.norm(
            centroids - query_embedding[0],
            axis=1
        )

        closest_cluster = int(np.argmin(distances))

        print(f"\nClosest Cluster: {closest_cluster}\n")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cleaned_text
            FROM posts
            WHERE cluster_id = %s
            LIMIT 10
        """, (closest_cluster,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        print("Sample posts from this cluster:\n")

        for i, row in enumerate(rows, 1):
            print(f"{i}. {row[0][:300]}\n")

        print("-" * 60)


def run_once(fetch_posts_func, subreddit, total_posts):

    print(f"\nFetching {total_posts} posts from r/{subreddit}...")
    raw_posts = fetch_posts_func(subreddit, total_posts)
    print(f"Fetched {len(raw_posts)} posts")

    docs = []
    post_ids = []

    for i, p in enumerate(raw_posts):

        doc = build_document(p)

        score = int(p.get("score", 0))
        comments = int(p.get("num_comments", 0))

        created_raw = p.get("created_utc")
        created_at = convert_timestamp(created_raw) if created_raw else datetime.utcnow()

        insert_post((
            p["id"],
            doc,
            mask_author(p.get("author")),
            score,
            comments,
            created_at
        ))

        docs.append(doc)
        post_ids.append(p["id"])

        if (i + 1) % 50 == 0:
            print(f"Saved {i + 1} posts...")

    if not docs:
        print("No documents fetched. Skipping.")
        return None

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
    cursor.close()
    conn.close()

    print(f"\nTotal rows currently in database: {total_rows}")
    print("Cycle complete.\n")

    return kmeans


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: python main.py <interval_seconds> <posts_per_subreddit>")
        sys.exit(1)

    interval = int(sys.argv[1])
    posts_per_subreddit = int(sys.argv[2])

    fetch_posts_func = get_scraper()
    init_table()

    final_kmeans = None

    for subreddit in SUBREDDITS:
        final_kmeans = run_once(fetch_posts_func, subreddit, posts_per_subreddit)
        print(f"\nSleeping for {interval} seconds...\n")
        time.sleep(interval)

    print("\nFinished scraping all subreddits.")

    if final_kmeans is not None:
        interactive_query_mode(final_kmeans)
import mysql.connector
import json


# ---- Configure Your MySQL Credentials Here ----
DB_CONFIG = {
    "host": "localhost",
    "user": "reddit_user",
    "password": "your_password",  # replace
    "database": "reddit_db"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def init_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id VARCHAR(20) PRIMARY KEY,
            cleaned_text TEXT,
            masked_author VARCHAR(50),
            score INT,
            comments INT,
            created_at DATETIME,
            embedding JSON,
            cluster_id INT,
            INDEX idx_cluster (cluster_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def insert_post(data_tuple):
    """
    data_tuple:
    (id, cleaned_text, masked_author, score, comments, created_at)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO posts
        (id, cleaned_text, masked_author, score, comments, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, data_tuple)

    conn.commit()
    cursor.close()
    conn.close()


def update_embedding(post_id, embedding):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE posts
        SET embedding = %s
        WHERE id = %s
    """, (json.dumps(embedding), post_id))

    conn.commit()
    cursor.close()
    conn.close()


def update_cluster(post_id, cluster_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE posts
        SET cluster_id = %s
        WHERE id = %s
    """, (cluster_id, post_id))

    conn.commit()
    cursor.close()
    conn.close()


def fetch_all_posts():
    """
    Returns list of (id, cleaned_text)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, cleaned_text FROM posts")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def fetch_posts_by_cluster(cluster_id):
    """
    Returns all posts in a given cluster.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cleaned_text
        FROM posts
        WHERE cluster_id = %s
    """, (cluster_id,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

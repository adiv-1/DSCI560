import mysql.connector
import json


# ---- Configure Your MySQL Credentials Here ----
DB_CONFIG = {
    "host": "localhost",
    "user": "reddit_user",
    "password": "your_password",   # ← Replace with your actual password
    "database": "reddit_db"
}


def get_connection():
    """
    Create and return a new MySQL connection.
    """
    return mysql.connector.connect(**DB_CONFIG)


def init_table():
    """
    Create posts table if it does not exist.
    """
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
            cluster_id INT
        )
    """)

    conn.commit()
    conn.close()


def insert_post(data_tuple):
    """
    Insert a new post.
    Uses INSERT IGNORE to prevent duplicates.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO posts
        (id, cleaned_text, masked_author, score, comments, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, data_tuple)

    conn.commit()
    conn.close()


def update_embedding(post_id, embedding):
    """
    Update embedding for a given post.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE posts
        SET embedding = %s
        WHERE id = %s
    """, (json.dumps(embedding), post_id))

    conn.commit()
    conn.close()


def update_cluster(post_id, cluster_id):
    """
    Update cluster ID for a given post.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE posts
        SET cluster_id = %s
        WHERE id = %s
    """, (cluster_id, post_id))

    conn.commit()
    conn.close()
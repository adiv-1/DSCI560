from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# Load embedding model once globally
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):
    if not texts:
        return np.array([])

    embeddings = model.encode(texts, show_progress_bar=False)
    embeddings = np.array(embeddings)

    # Normalize embeddings (improves KMeans behavior)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms

    return embeddings


def cluster_embeddings(embeddings, k=5):
    if embeddings is None or len(embeddings) == 0:
        return np.array([]), None

    k = min(k, len(embeddings))

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(embeddings)

    return labels, kmeans


def closest_to_centroids(embeddings, labels, kmeans):
    if kmeans is None or len(embeddings) == 0:
        return {}

    centroids = kmeans.cluster_centers_
    closest_indices = {}

    for cluster_id in range(len(centroids)):
        cluster_points = np.where(labels == cluster_id)[0]

        if len(cluster_points) == 0:
            continue

        cluster_embeddings = embeddings[cluster_points]

        distances = np.linalg.norm(
            cluster_embeddings - centroids[cluster_id],
            axis=1
        )

        closest_idx = cluster_points[np.argmin(distances)]
        closest_indices[cluster_id] = closest_idx

    return closest_indices


def extract_cluster_keywords(docs, labels, top_n=10):
    if not docs or len(labels) == 0:
        return {}

    if len(docs) < 2:
        return {0: []}

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = np.array(vectorizer.get_feature_names_out())

    cluster_keywords = {}
    unique_clusters = np.unique(labels)

    for cluster_id in unique_clusters:
        cluster_indices = np.where(labels == cluster_id)[0]

        if len(cluster_indices) == 0:
            continue

        cluster_tfidf = tfidf_matrix[cluster_indices]
        mean_tfidf = np.asarray(
            cluster_tfidf.mean(axis=0)
        ).flatten()

        top_indices = mean_tfidf.argsort()[-top_n:][::-1]

        cluster_keywords[int(cluster_id)] = (
            feature_names[top_indices].tolist()
        )

    return cluster_keywords

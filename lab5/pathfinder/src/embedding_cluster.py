from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# Load embedding model once (important for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(texts):
    """
    Generate sentence embeddings for a list of documents.
    """
    if not texts:
        return np.array([])

    return model.encode(texts, show_progress_bar=False)


def cluster_embeddings(embeddings, k=5):
    """
    Cluster embeddings using KMeans.
    Returns:
        labels (cluster assignments)
        fitted KMeans model
    """
    if len(embeddings) == 0:
        return np.array([]), None

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    return labels, kmeans


def closest_to_centroids(embeddings, labels, kmeans):
    """
    Find the document closest to each cluster centroid.
    Returns:
        Dictionary: {cluster_id: index_of_representative_doc}
    """
    if kmeans is None or len(embeddings) == 0:
        return {}

    centroids = kmeans.cluster_centers_
    closest_indices = {}

    for cluster_id in range(len(centroids)):
        cluster_points = np.where(labels == cluster_id)[0]

        if len(cluster_points) == 0:
            continue  # Safety guard for empty clusters

        cluster_embeddings = embeddings[cluster_points]

        distances = np.linalg.norm(
            cluster_embeddings - centroids[cluster_id],
            axis=1
        )

        closest_idx = cluster_points[np.argmin(distances)]
        closest_indices[cluster_id] = closest_idx

    return closest_indices


def extract_cluster_keywords(docs, labels, top_n=10):
    """
    Extract top TF-IDF keywords per cluster.
    Returns:
        Dictionary: {cluster_id: [keyword1, keyword2, ...]}
    """
    if not docs:
        return {}

    cluster_keywords = {}

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = np.array(vectorizer.get_feature_names_out())

    unique_clusters = np.unique(labels)

    for cluster_id in unique_clusters:
        cluster_indices = np.where(labels == cluster_id)[0]

        if len(cluster_indices) == 0:
            continue

        cluster_tfidf = tfidf_matrix[cluster_indices]

        mean_tfidf = cluster_tfidf.mean(axis=0)
        mean_tfidf = np.asarray(mean_tfidf).flatten()

        top_indices = mean_tfidf.argsort()[-top_n:][::-1]
        top_keywords = feature_names[top_indices]

        cluster_keywords[cluster_id] = top_keywords.tolist()

    return cluster_keywords

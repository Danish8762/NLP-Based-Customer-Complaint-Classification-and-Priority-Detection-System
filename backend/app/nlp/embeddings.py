"""
VoiceShield AI - Semantic Embeddings & Vector Indexing Module
Uses SentenceTransformer (all-MiniLM-L6-v2) to generate dense 384-dimensional
vector embeddings. Implements singleton model caching and cosine similarity search.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from sentence_transformers import SentenceTransformer

_MODEL_INSTANCE: Optional[SentenceTransformer] = None
_DATASET_EMBEDDINGS: Optional[np.ndarray] = None
_DATASET_METADATA: Optional[List[Dict[str, Any]]] = None


def get_embedder() -> SentenceTransformer:
    """Singleton getter for the SentenceTransformer model to prevent reloading."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        # Load local cached model
        _MODEL_INSTANCE = SentenceTransformer('all-MiniLM-L6-v2')
    return _MODEL_INSTANCE


def load_vector_index():
    """Loads precomputed training set embeddings and aligned metadata."""
    global _DATASET_EMBEDDINGS, _DATASET_METADATA
    if _DATASET_EMBEDDINGS is None or _DATASET_METADATA is None:
        emb_path = os.path.join("models", "saved", "dataset_embeddings.npy")
        meta_path = os.path.join("models", "saved", "dataset_metadata.json")

        if os.path.exists(emb_path) and os.path.exists(meta_path):
            _DATASET_EMBEDDINGS = np.load(emb_path)
            with open(meta_path, "r", encoding="utf-8") as f:
                _DATASET_METADATA = json.load(f)
        else:
            _DATASET_EMBEDDINGS = np.empty((0, 384))
            _DATASET_METADATA = []


def generate_embedding(text: str) -> List[float]:
    """Generates a normalized 384-dimensional embedding vector for input text."""
    if not text or not text.strip():
        return [0.0] * 384
    embedder = get_embedder()
    emb = embedder.encode(text, normalize_embeddings=True)
    return emb.tolist()


def search_similar_messages(text: str, top_k: int = 5, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Computes cosine similarity between query text embedding and stored dataset embeddings.
    Returns ranked similar historical records with match explanations.
    """
    load_vector_index()
    if _DATASET_EMBEDDINGS is None or len(_DATASET_EMBEDDINGS) == 0:
        return []

    embedder = get_embedder()
    query_emb = embedder.encode([text], normalize_embeddings=True)[0]

    # Cosine similarity for unit normalized vectors is simple dot product
    similarities = np.dot(_DATASET_EMBEDDINGS, query_emb)

    indexed_sims = list(enumerate(similarities))
    # Sort descending by similarity
    indexed_sims.sort(key=lambda x: x[1], reverse=True)

    results = []
    for idx, sim in indexed_sims:
        record = _DATASET_METADATA[idx]
        if category_filter and category_filter != "all" and record.get("category") != category_filter:
            continue

        sim_pct = round(float(sim) * 100, 2)
        sim_score = max(0.0, min(1.0, float(sim)))

        # Explain why they are similar
        reasons = []
        if sim_pct >= 85:
            reasons.append("High semantic alignment in syntactic phrasing and targeted social-engineering goal.")
        elif sim_pct >= 70:
            reasons.append("Strong thematic overlap in pressure tactics and requested action.")
        else:
            reasons.append("Moderate topical resemblance.")

        if record.get("intent"):
            reasons.append(f"Shares operational intent: '{record['intent']}'.")

        results.append({
            "id": record.get("id", idx + 1),
            "text": record["text"],
            "category": record["category"],
            "intent": record.get("intent", "Unknown"),
            "urgency": record.get("urgency", "LOW"),
            "manipulation_techniques": record.get("manipulation_techniques", []),
            "sensitive_requested": record.get("sensitive_requested", []),
            "similarity_score": round(sim_score, 4),
            "similarity_percentage": sim_pct,
            "explanation": " ".join(reasons)
        })

        if len(results) >= top_k:
            break

    return results

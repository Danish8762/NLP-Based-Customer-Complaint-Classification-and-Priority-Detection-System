"""
VoiceShield AI - Similarity Search & Vector Retrieval Endpoints
"""

from fastapi import APIRouter, HTTPException
from backend.app.schemas.analysis import SimilaritySearchRequest
from backend.app.nlp.embeddings import search_similar_messages

router = APIRouter(prefix="/api/similarity", tags=["Similarity"])


@router.post("/search")
def similarity_search_endpoint(req: SimilaritySearchRequest):
    """
    Computes vector cosine similarity against the historical scam knowledge base
    using all-MiniLM-L6-v2 dense embeddings.
    """
    if not req.text or len(req.text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Search query must contain at least 3 characters.")

    results = search_similar_messages(
        text=req.text,
        top_k=req.top_k or 5,
        category_filter=req.category_filter
    )

    return {
        "query": req.text,
        "match_count": len(results),
        "results": results
    }

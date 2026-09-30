"""
VoiceShield AI - Pydantic Request & Response Schemas
Provides strict validation for analysis, conversation, similarity search,
knowledge queries, and batch operations.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MessageAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=2, description="The message or suspicious text to analyze.")
    preferred_model: Optional[str] = Field("Linear SVM", description="Active classifier: 'Linear SVM', 'Logistic Regression', or 'Multinomial Naive Bayes'.")


class ConversationAnalysisRequest(BaseModel):
    raw_text: str = Field(..., min_length=5, description="Full dialogue transcript with speaker turns.")


class SimilaritySearchRequest(BaseModel):
    text: str = Field(..., min_length=3, description="Query text to search for semantically similar scam messages.")
    top_k: Optional[int] = Field(5, ge=1, le=20)
    category_filter: Optional[str] = Field(None, description="Optional category filter or 'all'.")


class BatchItemResult(BaseModel):
    index: int
    text: str
    category: str
    risk_score: float
    risk_level: str
    intent: str
    urgency_level: str
    sentiment: str
    is_scam: bool

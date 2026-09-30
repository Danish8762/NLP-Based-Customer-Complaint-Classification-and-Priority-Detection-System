"""
VoiceShield AI - Multi-Turn Conversation Analysis Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.database import get_db
from backend.app.schemas.analysis import ConversationAnalysisRequest
from backend.app.nlp.contextual import analyze_conversation
from backend.app.database.repositories import (
    save_conversation,
    list_conversations,
    get_conversation_by_id
)

router = APIRouter(prefix="/api", tags=["Conversations"])


@router.post("/analyze/conversation")
def analyze_conversation_endpoint(req: ConversationAnalysisRequest, db: Session = Depends(get_db)):
    """Analyzes a multi-turn dialogue, building timeline, escalation metrics, and entity graph."""
    if not req.raw_text or len(req.raw_text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Conversation text must contain at least 5 characters.")

    result = analyze_conversation(req.raw_text)
    record = save_conversation(db, req.raw_text, result)
    result["id"] = record.id
    result["created_at"] = record.created_at.isoformat()
    return result


@router.get("/conversations")
def get_conversations(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """Lists saved conversation analyses."""
    return list_conversations(db, limit=limit, offset=offset)


@router.get("/conversations/{conv_id}")
def get_conversation_detail(conv_id: int, db: Session = Depends(get_db)):
    """Retrieves full conversation analysis by ID."""
    res = get_conversation_by_id(db, conv_id)
    if not res:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return res

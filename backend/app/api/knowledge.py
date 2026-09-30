"""
VoiceShield AI - Scam Knowledge Base Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.database import get_db
from backend.app.database.repositories import (
    list_knowledge_articles,
    get_knowledge_article,
    seed_knowledge_base_if_empty
)

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


@router.get("")
def get_knowledge_articles(search: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    """Lists knowledge articles detailing scam types, warning signs, and linguistic patterns."""
    seed_knowledge_base_if_empty(db)
    return list_knowledge_articles(db, search=search, category=category)


@router.get("/{article_id}")
def get_article_detail(article_id: int, db: Session = Depends(get_db)):
    """Retrieves full article by ID."""
    article = get_knowledge_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge article not found.")
    return article

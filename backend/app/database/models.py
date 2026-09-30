"""
VoiceShield AI - SQLAlchemy ORM Models
Defines tables for:
- MessageAnalysis
- ConversationAnalysis
- KnowledgeArticle
- BatchJob
"""

import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from backend.app.database.database import Base


class MessageAnalysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    language_code = Column(String(20), default="en")
    language_name = Column(String(100), default="English")
    predicted_category = Column(String(100), index=True)
    confidence = Column(Float, default=0.0)
    risk_score = Column(Float, index=True)
    risk_level = Column(String(20), index=True)
    intent = Column(String(100), index=True)
    sentiment_label = Column(String(50))
    dominant_emotion = Column(String(50))
    urgency_level = Column(String(20))
    is_scam = Column(Boolean, default=True)
    processing_time_ms = Column(Float, default=0.0)
    full_result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "input_text": self.input_text,
            "language_code": self.language_code,
            "language_name": self.language_name,
            "predicted_category": self.predicted_category,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "intent": self.intent,
            "sentiment_label": self.sentiment_label,
            "dominant_emotion": self.dominant_emotion,
            "urgency_level": self.urgency_level,
            "is_scam": self.is_scam,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analysis": json.loads(self.full_result_json) if self.full_result_json else {}
        }


class ConversationAnalysis(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), default="Conversation Analysis")
    turn_count = Column(Integer, default=0)
    primary_suspect = Column(String(100))
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(20), default="LOW")
    raw_text = Column(Text, nullable=False)
    full_result_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "turn_count": self.turn_count,
            "primary_suspect": self.primary_suspect,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "analysis": json.loads(self.full_result_json) if self.full_result_json else {}
        }


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True, index=True)
    scam_type = Column(String(100), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    linguistic_patterns = Column(Text, nullable=False)  # JSON list
    typical_intent = Column(String(100))
    warning_signs = Column(Text, nullable=False)  # JSON list
    example_messages = Column(Text, nullable=False)  # JSON list
    recommended_action = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "scam_type": self.scam_type,
            "title": self.title,
            "description": self.description,
            "linguistic_patterns": json.loads(self.linguistic_patterns) if self.linguistic_patterns else [],
            "typical_intent": self.typical_intent,
            "warning_signs": json.loads(self.warning_signs) if self.warning_signs else [],
            "example_messages": json.loads(self.example_messages) if self.example_messages else [],
            "recommended_action": self.recommended_action
        }


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(200), nullable=False)
    total_messages = Column(Integer, default=0)
    suspicious_messages = Column(Integer, default=0)
    high_risk_messages = Column(Integer, default=0)
    avg_risk_score = Column(Float, default=0.0)
    summary_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "total_messages": self.total_messages,
            "suspicious_messages": self.suspicious_messages,
            "high_risk_messages": self.high_risk_messages,
            "avg_risk_score": self.avg_risk_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "summary": json.loads(self.summary_json) if self.summary_json else {}
        }

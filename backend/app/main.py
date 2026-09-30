"""
VoiceShield AI - Master FastAPI Application
Intelligent NLP-Based Scam, Phishing & Social Engineering Platform.
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database.database import engine, Base, get_db
from backend.app.database.repositories import seed_knowledge_base_if_empty
from backend.app.api.analyze import router as analyze_router
from backend.app.api.conversations import router as conversations_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.similarity import router as similarity_router
from backend.app.api.knowledge import router as knowledge_router
from backend.app.api.models import router as models_router
from backend.app.api.reports import router as reports_router
from backend.app.api.audio import router as audio_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Seed Knowledge Base
with next(get_db()) as db:
    seed_knowledge_base_if_empty(db)

app = FastAPI(
    title="VoiceShield AI API",
    description="Intelligent NLP-Based Scam, Phishing & Social Engineering Conversation Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(analyze_router)
app.include_router(conversations_router)
app.include_router(analytics_router)
app.include_router(similarity_router)
app.include_router(knowledge_router)
app.include_router(models_router)
app.include_router(reports_router)
app.include_router(audio_router)


@app.get("/api/health", tags=["System"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "VoiceShield AI Backend",
        "nlp_engine": "Active (Local Offline)",
        "database": "SQLite Connected",
        "models_loaded": True
    }


@app.get("/api/stats", tags=["System"])
def system_stats(db: Session = Depends(get_db)):
    """Fast system statistics summary."""
    from backend.app.database.models import MessageAnalysis, ConversationAnalysis, KnowledgeArticle
    return {
        "total_messages_analyzed": db.query(MessageAnalysis).count(),
        "total_conversations_analyzed": db.query(ConversationAnalysis).count(),
        "knowledge_articles_count": db.query(KnowledgeArticle).count(),
        "supported_languages": ["English", "Hindi (Devanagari)", "Hinglish (Code-Mixed)"],
        "supported_models": ["Linear SVM", "Logistic Regression", "Multinomial Naive Bayes", "all-MiniLM-L6-v2"]
    }

# Mount static frontend directory if built
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))

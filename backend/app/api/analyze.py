"""
VoiceShield AI - Single Message & Batch Analysis Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.database import get_db
from backend.app.schemas.analysis import MessageAnalysisRequest
from backend.app.services.analysis_service import analyze_message_full
from backend.app.services.batch_service import process_csv_batch
from backend.app.database.repositories import (
    save_analysis,
    get_analysis_by_id,
    list_analyses,
    list_batch_jobs
)

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze")
def analyze_message_endpoint(req: MessageAnalysisRequest, db: Session = Depends(get_db)):
    """Executes the full 17-stage NLP analysis pipeline on input text and saves to database."""
    if not req.text or len(req.text.strip()) < 2:
        raise HTTPException(status_code=400, detail="Input text must be at least 2 characters.")

    result = analyze_message_full(req.text, preferred_model=req.preferred_model or "Linear SVM")
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    record = save_analysis(db, result)
    result["id"] = record.id
    result["created_at"] = record.created_at.isoformat()
    return result


@router.get("/analysis/{analysis_id}")
def get_analysis_detail(analysis_id: int, db: Session = Depends(get_db)):
    """Retrieves full NLP analysis result by ID."""
    res = get_analysis_by_id(db, analysis_id)
    if not res:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return res


@router.get("/history")
def get_history(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lists historical analyses with search and filtering."""
    return list_analyses(db, limit=limit, offset=offset, search=search, category=category, risk_level=risk_level)


@router.post("/analyze/batch")
async def analyze_batch_endpoint(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Uploads and analyzes a CSV file containing message rows."""
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV or TXT files are accepted for batch analysis.")

    content_bytes = await file.read()
    try:
        content_str = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        content_str = content_bytes.decode("latin-1")

    batch_summary = process_csv_batch(content_str, file.filename, db)
    return batch_summary


@router.get("/batch/jobs")
def get_batch_jobs(db: Session = Depends(get_db)):
    """Lists past batch analysis jobs."""
    return list_batch_jobs(db)

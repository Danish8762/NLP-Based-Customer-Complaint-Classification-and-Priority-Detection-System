"""
VoiceShield AI - Report Export Endpoints
Generates PDF, JSON, and CSV forensic intelligence reports.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.database.repositories import get_analysis_by_id
from backend.app.services.report_service import (
    generate_pdf_report,
    generate_json_report,
    generate_csv_report
)

router = APIRouter(prefix="/api/export", tags=["Reports"])


@router.get("/{analysis_id}/pdf")
def export_pdf_report(analysis_id: int, db: Session = Depends(get_db)):
    """Exports PDF intelligence report."""
    item = get_analysis_by_id(db, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    pdf_bytes = generate_pdf_report(item.get("analysis", {}))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=VoiceShield_Report_{analysis_id}.pdf"}
    )


@router.get("/{analysis_id}/json")
def export_json_report(analysis_id: int, db: Session = Depends(get_db)):
    """Exports JSON intelligence report."""
    item = get_analysis_by_id(db, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    json_str = generate_json_report(item.get("analysis", {}))
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=VoiceShield_Report_{analysis_id}.json"}
    )


@router.get("/{analysis_id}/csv")
def export_csv_report(analysis_id: int, db: Session = Depends(get_db)):
    """Exports CSV intelligence summary."""
    item = get_analysis_by_id(db, analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    csv_str = generate_csv_report(item.get("analysis", {}))
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=VoiceShield_Report_{analysis_id}.csv"}
    )

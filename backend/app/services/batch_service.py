"""
VoiceShield AI - Batch Analysis Service
Parses uploaded CSV/TXT files, iterates through rows/messages,
executes the full NLP pipeline on each item, aggregates batch-level intelligence,
and stores the job in SQLite.
"""

import io
import csv
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.services.analysis_service import analyze_message_full
from backend.app.database.repositories import save_batch_job


def process_csv_batch(csv_content: str, filename: str, db: Session) -> Dict[str, Any]:
    """
    Parses CSV content, locates message text column, runs NLP analysis,
    and returns comprehensive batch statistics.
    """
    reader = csv.reader(io.StringIO(csv_content))
    rows = list(reader)
    if not rows:
        return {"error": "CSV file is empty."}

    # Find text column index
    header = rows[0]
    text_col_idx = 0
    for idx, col in enumerate(header):
        col_lower = col.lower().strip()
        if col_lower in ["message", "text", "body", "content", "complaint", "sms", "email"]:
            text_col_idx = idx
            break

    # If first row was a header, skip it
    data_rows = rows[1:] if len(rows) > 1 else rows

    results = []
    category_counts = {}
    risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    intent_counts = {}
    emotion_counts = {}
    lang_counts = {}
    technique_counts = {}
    keyword_counts = {}

    total_risk_sum = 0.0
    suspicious_count = 0
    high_risk_count = 0

    for idx, row in enumerate(data_rows):
        if not row or text_col_idx >= len(row):
            continue
        msg_text = row[text_col_idx].strip()
        if not msg_text or len(msg_text) < 3:
            continue

        # Run NLP
        analysis = analyze_message_full(msg_text)
        if "error" in analysis:
            continue

        risk = analysis["risk"]
        clf = analysis["classification"]
        intent = analysis["intent"]
        emotion = analysis["emotion"]
        lang = analysis["language"]
        manip = analysis["manipulation"]

        total_risk_sum += risk["score"]
        if clf["is_scam"]:
            suspicious_count += 1
        if risk["level"] in ["HIGH", "CRITICAL"]:
            high_risk_count += 1

        # Tally distributions
        cat = clf["predicted_category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

        r_lvl = risk["level"]
        risk_counts[r_lvl] = risk_counts.get(r_lvl, 0) + 1

        i_name = intent["intent"]
        intent_counts[i_name] = intent_counts.get(i_name, 0) + 1

        e_name = emotion["dominant_emotion"]
        emotion_counts[e_name] = emotion_counts.get(e_name, 0) + 1

        l_name = lang["language_name"]
        lang_counts[l_name] = lang_counts.get(l_name, 0) + 1

        for tech in manip["techniques"]:
            t_name = tech["technique"]
            technique_counts[t_name] = technique_counts.get(t_name, 0) + 1

        for kw in analysis["keywords"][:4]:
            w = kw["keyword"]
            keyword_counts[w] = keyword_counts.get(w, 0) + 1

        results.append({
            "index": idx + 1,
            "text": msg_text,
            "category": cat,
            "risk_score": risk["score"],
            "risk_level": r_lvl,
            "intent": i_name,
            "urgency": analysis["urgency"]["level"],
            "sentiment": analysis["sentiment"]["label"],
            "dominant_emotion": e_name,
            "is_scam": clf["is_scam"]
        })

    total_msgs = len(results)
    avg_risk = round(total_risk_sum / max(1, total_msgs), 1)

    summary = {
        "filename": filename,
        "total_messages": total_msgs,
        "suspicious_messages": suspicious_count,
        "high_risk_messages": high_risk_count,
        "detection_rate": round((suspicious_count / max(1, total_msgs)) * 100, 1),
        "average_risk_score": avg_risk,
        "category_distribution": [{"name": k, "value": v} for k, v in category_counts.items()],
        "risk_distribution": [{"name": k, "value": v} for k, v in risk_counts.items()],
        "intent_distribution": [{"name": k, "value": v} for k, v in sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)[:8]],
        "emotion_distribution": [{"name": k, "value": v} for k, v in emotion_counts.items()],
        "language_distribution": [{"name": k, "value": v} for k, v in lang_counts.items()],
        "top_manipulation_techniques": [{"name": k, "value": v} for k, v in sorted(technique_counts.items(), key=lambda x: x[1], reverse=True)[:8]],
        "top_keywords": [{"name": k, "value": v} for k, v in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]],
        "items": results
    }

    # Save to database
    save_batch_job(
        db=db,
        filename=filename,
        total=total_msgs,
        suspicious=suspicious_count,
        high_risk=high_risk_count,
        avg_risk=avg_risk,
        summary=summary
    )

    return summary

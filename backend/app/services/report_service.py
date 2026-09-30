"""
VoiceShield AI - Report Generation Service
Generates professional forensic intelligence reports in:
- PDF (via ReportLab with headers, risk badges, evidence tables, and recommendations)
- JSON
- CSV
"""

import io
import csv
import json
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_json_report(analysis_data: Dict[str, Any]) -> str:
    """Serializes analysis into formatted JSON."""
    return json.dumps(analysis_data, indent=2, ensure_ascii=False)


def generate_csv_report(analysis_data: Dict[str, Any]) -> str:
    """Flattens key NLP metrics into CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Input Text", analysis_data.get("input_text", "")])
    writer.writerow(["Language", f"{analysis_data.get('language', {}).get('language_name')} ({analysis_data.get('language', {}).get('confidence')})"])
    writer.writerow(["Risk Score", analysis_data.get("risk", {}).get("score", "")])
    writer.writerow(["Risk Level", analysis_data.get("risk", {}).get("level", "")])
    writer.writerow(["Predicted Category", analysis_data.get("classification", {}).get("predicted_category", "")])
    writer.writerow(["Confidence", f"{analysis_data.get('classification', {}).get('confidence_percentage', '')}%"])
    writer.writerow(["Intent", analysis_data.get("intent", {}).get("intent", "")])
    writer.writerow(["Sentiment", analysis_data.get("sentiment", {}).get("label", "")])
    writer.writerow(["Dominant Emotion", analysis_data.get("emotion", {}).get("dominant_emotion", "")])
    writer.writerow(["Urgency Level", analysis_data.get("urgency", {}).get("level", "")])
    writer.writerow(["Urgency Score", analysis_data.get("urgency", {}).get("score", "")])
    
    # Manipulation Techniques
    techs = [t["technique"] for t in analysis_data.get("manipulation", {}).get("techniques", [])]
    writer.writerow(["Manipulation Techniques", "; ".join(techs)])
    
    # Sensitive Requests
    sens = [s.get("request_type", "") for s in analysis_data.get("manipulation", {}).get("sensitive_requests", [])]
    writer.writerow(["Sensitive Data Requested", "; ".join(sens)])
    
    # Entities
    ents = [f"{e['text']} ({e['label']})" for e in analysis_data.get("entities", [])]
    writer.writerow(["Entities", "; ".join(ents)])
    
    # Recommendations
    recs = analysis_data.get("explanation", {}).get("recommendations", [])
    writer.writerow(["Recommendations", " | ".join(recs)])
    
    return output.getvalue()


def generate_pdf_report(analysis_data: Dict[str, Any]) -> bytes:
    """Generates an academic-grade cybersecurity intelligence PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        fontName='Helvetica'
    )
    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    quote_style = ParagraphStyle(
        'QuoteCustom',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        fontName='Helvetica-Oblique'
    )

    elements = []

    # Header
    elements.append(Paragraph("VoiceShield AI", title_style))
    elements.append(Paragraph("Intelligent NLP Scam, Phishing & Social Engineering Analysis Platform", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=15))

    # Input Text Card
    elements.append(Paragraph("ANALYZED TEXT INPUT", h2_style))
    input_text = analysis_data.get("input_text", "")
    elements.append(Paragraph(f'"{input_text}"', quote_style))
    elements.append(Spacer(1, 10))

    # Executive Summary Key Metrics Table
    risk = analysis_data.get("risk", {})
    clf = analysis_data.get("classification", {})
    intent = analysis_data.get("intent", {})
    urgency = analysis_data.get("urgency", {})

    risk_level = risk.get("level", "LOW")
    risk_color = colors.HexColor("#ef4444") if risk_level in ["CRITICAL", "HIGH"] else colors.HexColor("#10b981")

    kpi_data = [
        [
            Paragraph(f"<b>Risk Level:</b> <font color='{risk_color.hexval()}'>{risk_level}</font> ({risk.get('score', 0)}/100)", body_style),
            Paragraph(f"<b>Category:</b> {clf.get('predicted_category', 'Unknown')}", body_style)
        ],
        [
            Paragraph(f"<b>Intent:</b> {intent.get('intent', 'Unknown')} ({int(intent.get('confidence', 0)*100)}%)", body_style),
            Paragraph(f"<b>Urgency:</b> {urgency.get('level', 'LOW')} ({urgency.get('score', 0)}/100)", body_style)
        ],
        [
            Paragraph(f"<b>Language:</b> {analysis_data.get('language', {}).get('language_name', 'English')}", body_style),
            Paragraph(f"<b>Classifier Confidence:</b> {clf.get('confidence_percentage', 0)}%", body_style)
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[270, 270])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 12))

    # Explainable Evidence Cards
    elements.append(Paragraph("WHY THIS MESSAGE IS SUSPICIOUS (EXPLAINABLE NLP EVIDENCE)", h2_style))
    evidence_cards = analysis_data.get("explanation", {}).get("evidence_cards", [])
    
    if evidence_cards:
        ev_table_data = [["Indicator", "Evidence Quote", "NLP Explanation"]]
        for ec in evidence_cards:
            ev_table_data.append([
                Paragraph(f"<b>{ec.get('title')}</b>", body_style),
                Paragraph(f"{ec.get('evidence')}", quote_style),
                Paragraph(ec.get('description', ''), body_style)
            ])
        t_ev = Table(ev_table_data, colWidths=[140, 160, 240])
        t_ev.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
            ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,0), (-1,0), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(t_ev)
    else:
        elements.append(Paragraph("No significant malicious or coercive indicators detected.", body_style))
    elements.append(Spacer(1, 12))

    # Extracted Entities & Keywords
    elements.append(Paragraph("LINGUISTIC & ENTITY EXTRACTION", h2_style))
    ents = analysis_data.get("entities", [])
    ent_str = ", ".join(f"{e['text']} [{e['label']}]" for e in ents) if ents else "None detected"
    kws = analysis_data.get("keywords", [])
    kw_str = ", ".join(k['keyword'] for k in kws) if kws else "None"
    
    elements.append(Paragraph(f"<b>Named Entities:</b> {ent_str}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Key Terms:</b> {kw_str}", body_style))
    elements.append(Spacer(1, 12))

    # Actionable Recommendations
    elements.append(Paragraph("RECOMMENDED USER ACTIONS", h2_style))
    recs = analysis_data.get("explanation", {}).get("recommendations", [])
    for idx, r in enumerate(recs, 1):
        elements.append(Paragraph(f"{idx}. {r}", body_style))
        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10))
    elements.append(Paragraph("Generated by VoiceShield AI | Academic Major Project Platform | Fully Local NLP Verification", subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

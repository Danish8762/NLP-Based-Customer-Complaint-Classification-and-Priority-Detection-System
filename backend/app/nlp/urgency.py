"""
VoiceShield AI - NLP Urgency Detection Module
Evaluates psychological time pressure, expiration threats, and countdown cues.
Generates urgency levels (LOW, MEDIUM, HIGH, CRITICAL), urgency scores (0-100),
detected cue tokens, and a sentence-level heatmap.
"""

import re
from typing import Dict, Any, List

URGENCY_PATTERNS = [
    (r'\b(?:immediately|right now|turant|jaldi|fatafat|without delay)\b', "Immediate action cue", 25),
    (r'\b(?:within\s+\d+\s*(?:hours?|hrs?|minutes?|mins?|seconds?|sec))\b', "Definite deadline countdown", 30),
    (r'\b(?:today|tonight|before midnight|in 24 hours?)\b', "Short time window constraint", 20),
    (r'\b(?:urgent|urgently|emergency|critical alert)\b', "Explicit urgency declaration", 20),
    (r'\b(?:final warning|last notice|permanently deleted|account termination)\b', "Irrevocable consequence threat", 35),
    (r'\b(?:limited time|hurry|act fast|expires soon)\b', "Scarcity / FOMO time pressure", 15),
    (r'\b(?:action required|immediate response)\b', "Directive urgency marker", 15)
]


def detect_urgency(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """
    Computes overall urgency score (0-100), urgency level,
    extracted cues with evidence, and sentence-level heatmap.
    """
    if not text:
        return {
            "level": "LOW",
            "score": 0,
            "cues": [],
            "heatmap": []
        }

    text_lower = text.lower()
    total_score = 0
    detected_cues = []

    for pattern, reason, weight in URGENCY_PATTERNS:
        matches = list(re.finditer(pattern, text_lower))
        for m in matches:
            total_score += weight
            detected_cues.append({
                "cue": text[m.start():m.end()],
                "reason": reason,
                "weight": weight,
                "start": m.start(),
                "end": m.end()
            })

    # Uppercase exclamations boost
    caps_urgent = len(re.findall(r'\b[A-Z]{3,}\b', text))
    if caps_urgent >= 2 and total_score > 0:
        total_score += 15
        detected_cues.append({
            "cue": "MULTIPLE_ALL_CAPS",
            "reason": "All-caps text simulating alarm and panic",
            "weight": 15,
            "start": -1,
            "end": -1
        })

    normalized_score = min(100, total_score)

    if normalized_score >= 70:
        level = "CRITICAL"
    elif normalized_score >= 45:
        level = "HIGH"
    elif normalized_score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Sentence-level heatmap calculation
    heatmap = []
    if sentences:
        for s in sentences:
            s_lower = s.lower()
            s_score = 0
            s_cues = []
            for pattern, reason, weight in URGENCY_PATTERNS:
                m = re.findall(pattern, s_lower)
                if m:
                    s_score += weight * len(m)
                    s_cues.extend(m)
            
            s_score = min(100, s_score)
            intensity = round(s_score / 100.0, 2)
            heatmap.append({
                "sentence": s,
                "score": s_score,
                "intensity": intensity,
                "cues": s_cues,
                "level": "CRITICAL" if s_score >= 70 else ("HIGH" if s_score >= 45 else ("MEDIUM" if s_score >= 20 else "LOW"))
            })

    return {
        "level": level,
        "score": normalized_score,
        "cues": detected_cues,
        "heatmap": heatmap
    }

"""
VoiceShield AI - Psychological & Social Engineering Emotion Analysis Module
Analyzes psychological emotional triggers: Fear, Urgency/Anxiety, Joy/Reward,
Anger, Sadness, Surprise, and Neutral.
Produces continuous distributions and sentence-level tracking.
"""

import re
from typing import Dict, Any, List

# Lexical emotion markers tailored for phishing and social engineering contexts
EMOTION_LEXICON = {
    "fear": {
        "blocked", "suspended", "locked", "freeze", "lawsuit", "arrest", "warrant",
        "police", "court", "breach", "hacked", "stolen", "penalty", "illegal",
        "danger", "compromised", "virus", "malware", "encrypted", "unauthorized",
        "seized", "investigation", "punishment", "consequences", "khatra", "jail"
    },
    "urgency/anxiety": {
        "immediately", "urgent", "hurry", "expire", "today", "now", "deadline",
        "critical", "fast", "hours", "minutes", "warning", "final", "terminate",
        "cancel", "turant", "jaldi", "fatafat", "acting", "delay", "action"
    },
    "joy": {
        "congratulations", "won", "winner", "prize", "reward", "lucky", "cashback",
        "bonus", "free", "gift", "cheque", "selected", "approved", "special",
        "celebrate", "crorepati", "happy", "badhai", "khushi"
    },
    "surprise": {
        "unbelievable", "unexpected", "astonishing", "shocking", "mystery",
        "unclaimed", "unusual", "noticed", "detected", "sudden", "achanok"
    },
    "anger": {
        "dispute", "violation", "fraud", "unacceptable", "blame", "failed",
        "offense", "infringement", "demand", "fault", "gussa"
    },
    "sadness": {
        "deactivation", "loss", "damaged", "sorry", "trouble", "suffering",
        "emergency", "hospital", "sick", "tragedy", "dukh"
    }
}


def analyze_emotion(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """
    Computes emotion distribution across 7 dimensions:
    fear, urgency/anxiety, joy, surprise, anger, sadness, neutral.
    """
    if not text:
        return {
            "dominant_emotion": "neutral",
            "confidence": 1.0,
            "distribution": {"neutral": 1.0},
            "sentence_emotions": []
        }

    words = [re.sub(r'[^a-zA-Z]', '', w.lower()) for w in text.split()]
    words = [w for w in words if w]
    total_words = max(1, len(words))

    raw_scores = {
        "fear": 0.0,
        "urgency/anxiety": 0.0,
        "joy": 0.0,
        "surprise": 0.0,
        "anger": 0.0,
        "sadness": 0.0,
        "neutral": 0.05
    }

    for w in words:
        matched = False
        for emo, lex in EMOTION_LEXICON.items():
            if w in lex:
                raw_scores[emo] += 1.0
                matched = True
        if not matched:
            raw_scores["neutral"] += 0.15

    # Exclamation mark boosts urgency and joy/surprise
    excl = text.count("!")
    if excl > 0:
        raw_scores["urgency/anxiety"] += excl * 0.4
        if raw_scores["joy"] > 0:
            raw_scores["joy"] += excl * 0.3

    # Normalize to probabilities
    total_sum = sum(raw_scores.values())
    distribution = {k: round(v / total_sum, 4) for k, v in raw_scores.items()}

    dominant_emotion = max(distribution.items(), key=lambda x: x[1])[0]
    dominant_confidence = distribution[dominant_emotion]

    # Sentence-level emotions
    sentence_emotions = []
    if sentences:
        for s in sentences:
            s_words = [re.sub(r'[^a-zA-Z]', '', w.lower()) for w in s.split()]
            s_scores = {k: 0.0 for k in EMOTION_LEXICON}
            s_scores["neutral"] = 0.1
            for sw in s_words:
                for emo, lex in EMOTION_LEXICON.items():
                    if sw in lex:
                        s_scores[emo] += 1.0

            s_dom = max(s_scores.items(), key=lambda x: x[1])[0]
            sentence_emotions.append({
                "sentence": s,
                "dominant_emotion": s_dom,
                "scores": {k: round(v, 2) for k, v in s_scores.items() if v > 0}
            })

    return {
        "dominant_emotion": dominant_emotion,
        "confidence": round(dominant_confidence, 3),
        "distribution": distribution,
        "sentence_emotions": sentence_emotions
    }

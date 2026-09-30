"""
VoiceShield AI - Multi-Approach Sentiment Analysis Module
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner)
and linguistic polarity lexicon to extract valence, subjectivity,
and token-level sentiment contributions.
"""

from typing import Dict, Any, List
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

try:
    SIA = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download("vader_lexicon", quiet=True)
    SIA = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str, sentences: List[str] = None) -> Dict[str, Any]:
    """
    Computes overall and sentence-level sentiment scores.
    Identifies high-impact polarity words.
    """
    if not text:
        return {
            "label": "Neutral",
            "compound": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0,
            "subjectivity": 0.0,
            "significant_words": [],
            "sentence_sentiment": []
        }

    scores = SIA.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    # Token-level valence analysis using VADER lexicon
    words = text.split()
    significant_words = []
    for w in words:
        clean_w = w.lower().strip(".,!?:;\"'()[]{}")
        if clean_w in SIA.lexicon:
            score = SIA.lexicon[clean_w]
            significant_words.append({
                "word": clean_w,
                "valence": score,
                "type": "positive" if score > 0 else "negative"
            })

    # Sort by absolute impact
    significant_words.sort(key=lambda x: abs(x["valence"]), reverse=True)

    # Sentence-level breakdown
    sentence_breakdown = []
    if sentences:
        for s in sentences:
            s_scores = SIA.polarity_scores(s)
            s_comp = s_scores["compound"]
            s_label = "Positive" if s_comp >= 0.05 else ("Negative" if s_comp <= -0.05 else "Neutral")
            sentence_breakdown.append({
                "sentence": s,
                "label": s_label,
                "compound": round(s_comp, 3),
                "positive": round(s_scores["pos"], 3),
                "negative": round(s_scores["neg"], 3),
                "neutral": round(s_scores["neu"], 3)
            })

    # Approximate subjectivity from ratio of emotional to neutral words
    emotional_words_count = len(significant_words)
    total_words_count = max(1, len(words))
    subjectivity = min(1.0, round((emotional_words_count * 2.5) / total_words_count, 3))

    return {
        "label": label,
        "compound": round(compound, 3),
        "positive": round(scores["pos"], 3),
        "neutral": round(scores["neu"], 3),
        "negative": round(scores["neg"], 3),
        "subjectivity": subjectivity,
        "significant_words": significant_words[:10],
        "sentence_sentiment": sentence_breakdown
    }

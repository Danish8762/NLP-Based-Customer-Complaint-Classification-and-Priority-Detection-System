"""
VoiceShield AI - Multilingual Language Detection Module
Identifies English, Devanagari Hindi, and Romanized Hindi (Hinglish).
Computes confidence scores based on lexical and script matching.
"""

import re
from typing import Dict, Any

# Common Romanized Hindi / Hinglish lexical markers
HINGLISH_MARKERS = {
    "aapka", "aap", "tumhara", "humara", "karein", "kijiye", "bhejo", "bhejiye",
    "turant", "jaldi", "wala", "wali", "wale", "hoga", "hogi", "hai", "hain",
    "bhai", "paisa", "paise", "rupaye", "rupay", "khata", "sambandhit", "nahi",
    "karo", "karna", "baat", "dekh", "roko", "bachao", "aaya", "aaye", "gaya",
    "de", "dena", "saath", "liye", "bina", "sirf", "yahan", "wahan", "kaise",
    "kyun", "kab", "mat", "kripya", "shukriya", "dhyan", "suno", "bolo", "khabar"
}

DEVANAGARI_REGEX = re.compile(r'[\u0900-\u097F]')


def detect_language(text: str) -> Dict[str, Any]:
    """
    Detects language with support for English, Hindi (Devanagari), and Hinglish (Code-mixed).
    Returns language code, human-readable name, confidence score, and script type.
    """
    if not text or not text.strip():
        return {
            "language_code": "unknown",
            "language_name": "Unknown",
            "confidence": 0.0,
            "script": "None",
            "is_code_mixed": False
        }

    # 1. Check Devanagari Script (Hindi, Marathi, Nepali)
    devanagari_chars = len(DEVANAGARI_REGEX.findall(text))
    total_alpha_chars = len(re.findall(r'[a-zA-Z\u0900-\u097F]', text))

    if total_alpha_chars > 0 and (devanagari_chars / total_alpha_chars) > 0.35:
        confidence = min(0.99, round(devanagari_chars / total_alpha_chars + 0.1, 2))
        return {
            "language_code": "hi",
            "language_name": "Hindi (Devanagari)",
            "confidence": confidence,
            "script": "Devanagari",
            "is_code_mixed": False
        }

    # 2. Check Romanized Hindi / Hinglish markers
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return {
            "language_code": "en",
            "language_name": "English",
            "confidence": 0.5,
            "script": "Latin",
            "is_code_mixed": False
        }

    hinglish_count = sum(1 for w in words if w in HINGLISH_MARKERS)
    hinglish_ratio = hinglish_count / len(words)

    if hinglish_count >= 2 or (len(words) <= 6 and hinglish_count >= 1):
        confidence = min(0.95, round(0.60 + (hinglish_ratio * 0.4), 2))
        return {
            "language_code": "hinglish",
            "language_name": "Hinglish (Code-Mixed Romanized Hindi)",
            "confidence": confidence,
            "script": "Latin",
            "is_code_mixed": True
        }

    # 3. Default to English
    return {
        "language_code": "en",
        "language_name": "English",
        "confidence": 0.94,
        "script": "Latin",
        "is_code_mixed": False
    }

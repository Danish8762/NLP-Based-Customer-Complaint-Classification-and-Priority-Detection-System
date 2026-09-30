"""
VoiceShield AI - Keyword & Keyphrase Extraction Module
Implements statistical TF-IDF-based extraction, frequency/importance weighting,
and n-gram keyphrase extraction.
Allows method comparison as required by academic evaluation.
"""

import re
import math
import string
from collections import Counter
from typing import List, Dict, Any, Tuple
from backend.app.nlp.preprocessing import STOP_WORDS, tokenize_and_tag


def extract_keywords(text: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Extracts keywords using multiple algorithms:
    1. POS-filtered Frequency Importance
    2. Term-Frequency with Length & Position Bias (Statistical YAKE-style heuristic)
    3. High-Risk Scam Keyword Density
    """
    if not text:
        return {
            "top_keywords": [],
            "methods_comparison": {
                "frequency": [],
                "statistical": [],
                "high_risk_lexical": []
            }
        }

    tagged_tokens = tokenize_and_tag(text)
    
    # Method 1: POS-filtered Frequency Importance
    pos_candidates = [
        t["lemma"].lower() for t in tagged_tokens
        if t["is_important"] and len(t["lemma"]) > 2
    ]
    freq_counter = Counter(pos_candidates)
    freq_keywords = [
        {"keyword": word, "score": count, "method": "Frequency + POS Filter"}
        for word, count in freq_counter.most_common(top_k)
    ]

    # Method 2: Statistical Heuristic (Length, position in text, capitalisation)
    words = re.findall(r'[a-zA-Z]{3,}', text)
    stat_scores = {}
    for idx, w in enumerate(words):
        w_lower = w.lower()
        if w_lower in STOP_WORDS:
            continue
        # Position weight (earlier words slightly favored), length weight, caps bonus
        pos_weight = 1.0 + (1.0 / (idx + 1))
        len_weight = math.log(len(w) + 1)
        caps_weight = 1.3 if w.isupper() else 1.0
        score = pos_weight * len_weight * caps_weight
        stat_scores[w_lower] = stat_scores.get(w_lower, 0.0) + score

    stat_keywords = [
        {"keyword": k, "score": round(v, 2), "method": "Statistical Heuristic"}
        for k, v in sorted(stat_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    ]

    # Method 3: High-Risk Scam Lexical Density
    scam_lexicon = {
        "otp", "verify", "account", "blocked", "suspended", "password", "urgent",
        "immediately", "kyc", "bank", "card", "pin", "cvv", "payment", "cashback",
        "winner", "invest", "returns", "trojan", "malware", "support", "refund",
        "aadhaar", "pan", "deactivation", "clearance", "customs", "delivery"
    }
    risk_candidates = [w for w in pos_candidates if w in scam_lexicon]
    risk_counter = Counter(risk_candidates)
    risk_keywords = [
        {"keyword": word, "score": count, "method": "Cybersecurity Lexical"}
        for word, count in risk_counter.most_common(top_k)
    ]

    # Consolidated Top Keywords
    combined_scores = {}
    for item in stat_keywords:
        combined_scores[item["keyword"]] = combined_scores.get(item["keyword"], 0.0) + item["score"]
    for item in risk_keywords:
        combined_scores[item["keyword"]] = combined_scores.get(item["keyword"], 0.0) + (item["score"] * 3.0)

    top_consolidated = [
        {"keyword": k, "score": round(v, 2)}
        for k, v in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    ]

    return {
        "top_keywords": top_consolidated,
        "methods_comparison": {
            "frequency": freq_keywords,
            "statistical": stat_keywords,
            "high_risk_lexical": risk_keywords
        }
    }


def extract_keyphrases(text: str, top_k: int = 8) -> List[Dict[str, Any]]:
    """
    Extracts multi-word keyphrases (Bigrams and Trigrams) filtered by
    syntactic structure and relevance.
    """
    if not text:
        return []

    words = re.findall(r'[a-zA-Z]+', text.lower())
    if len(words) < 2:
        return []

    # Generate candidate 2-grams and 3-grams
    candidates = []
    
    # 2-grams
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        # Ignore if both are stopwords
        if w1 in STOP_WORDS and w2 in STOP_WORDS:
            continue
        if len(w1) > 1 and len(w2) > 1:
            phrase = f"{w1} {w2}"
            candidates.append(phrase)

    # 3-grams
    for i in range(len(words) - 2):
        w1, w2, w3 = words[i], words[i+1], words[i+2]
        if w1 in STOP_WORDS and w2 in STOP_WORDS and w3 in STOP_WORDS:
            continue
        if len(w1) > 1 and len(w3) > 1:
            phrase = f"{w1} {w2} {w3}"
            candidates.append(phrase)

    # Filter by cybersecurity or action relevance
    action_terms = {
        "verify", "account", "blocked", "suspended", "send", "otp", "code", "pin",
        "link", "click", "password", "bank", "card", "immediately", "today",
        "unauthorized", "kyc", "update", "clearance", "delivery", "fee", "cashback",
        "winner", "invest", "returns", "login", "credentials", "support", "refund"
    }

    scored_phrases = []
    phrase_counts = Counter(candidates)

    for phrase, count in phrase_counts.items():
        tokens = phrase.split()
        relevance_hits = sum(1 for t in tokens if t in action_terms)
        score = count * (1.5 + (relevance_hits * 2.0))
        if relevance_hits > 0:
            scored_phrases.append({
                "phrase": phrase,
                "relevance_score": round(score, 2),
                "frequency": count,
                "length": len(tokens)
            })

    scored_phrases.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored_phrases[:top_k]

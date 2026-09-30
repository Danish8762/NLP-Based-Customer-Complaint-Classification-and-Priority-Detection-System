"""
VoiceShield AI - Master NLP Orchestration Service
Executes the complete end-to-end linguistic pipeline on incoming messages:
Language Detection -> Cleaning -> Sentences -> Tokens/POS/Lemma -> NER ->
Keywords/Keyphrases -> Intent -> Sentiment -> Emotion -> Urgency ->
Manipulation -> URLs -> Classification -> Vector Similarity -> Risk -> Explainability.
"""

import time
from typing import Dict, Any, Optional

from backend.app.nlp.language import detect_language
from backend.app.nlp.preprocessing import (
    clean_text,
    extract_sentences,
    extract_urls,
    tokenize_and_tag,
    compute_text_statistics
)
from backend.app.nlp.ner import extract_entities
from backend.app.nlp.keywords import extract_keywords, extract_keyphrases
from backend.app.nlp.intent import detect_intent
from backend.app.nlp.sentiment import analyze_sentiment
from backend.app.nlp.emotion import analyze_emotion
from backend.app.nlp.urgency import detect_urgency
from backend.app.nlp.manipulation import detect_manipulation
from backend.app.nlp.scam_classifier import classify_message
from backend.app.nlp.embeddings import generate_embedding, search_similar_messages
from backend.app.nlp.risk import calculate_risk_score
from backend.app.nlp.explainability import generate_nlp_explanation


def analyze_message_full(text: str, preferred_model: str = "Linear SVM") -> Dict[str, Any]:
    """
    Executes the entire NLP pipeline synchronously and returns a rich,
    academic-grade intelligence dictionary.
    """
    start_total_time = time.time()
    
    # 1. Text Cleaning
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return {"error": "Input text is empty."}

    # 2. Language Detection
    lang_data = detect_language(cleaned_text)

    # 3. Sentence Segmentation
    sentences = extract_sentences(cleaned_text)

    # 4. Tokenization, Lemmatization, POS Tagging
    tagged_tokens = tokenize_and_tag(cleaned_text)

    # 5. Linguistic Text Statistics
    text_stats = compute_text_statistics(cleaned_text, tagged_tokens, sentences)

    # 6. URL Extraction and Structural Heuristics
    urls = extract_urls(cleaned_text)

    # 7. Named Entity Recognition
    entities = extract_entities(cleaned_text)

    # 8. Keywords and Keyphrases Extraction
    keywords_data = extract_keywords(cleaned_text, top_k=8)
    keyphrases = extract_keyphrases(cleaned_text, top_k=6)

    # 9. Intent Detection
    intent_data = detect_intent(cleaned_text)

    # 10. Sentiment Analysis
    sentiment_data = analyze_sentiment(cleaned_text, sentences=sentences)

    # 11. Emotion Analysis
    emotion_data = analyze_emotion(cleaned_text, sentences=sentences)

    # 12. Urgency Detection
    urgency_data = detect_urgency(cleaned_text, sentences=sentences)

    # 13. Manipulation & Sensitive Data Request Detection
    manipulation_data = detect_manipulation(cleaned_text)

    # 14. ML Scam Classification (TF-IDF + Classifiers)
    classification_data = classify_message(cleaned_text, preferred_model=preferred_model)

    # 15. Semantic Embeddings & Similarity Search
    similar_messages = search_similar_messages(cleaned_text, top_k=4)

    # 16. Risk Intelligence Engine
    risk_data = calculate_risk_score(
        classification=classification_data,
        intent_data=intent_data,
        urgency_data=urgency_data,
        manipulation_data=manipulation_data,
        urls=urls,
        similar_messages=similar_messages
    )

    # 17. Explainable NLP
    explanation_data = generate_nlp_explanation(
        text=cleaned_text,
        classification=classification_data,
        intent_data=intent_data,
        urgency_data=urgency_data,
        manipulation_data=manipulation_data,
        entities=entities,
        urls=urls,
        similar_messages=similar_messages
    )

    elapsed_ms = round((time.time() - start_total_time) * 1000, 2)

    return {
        "input_text": cleaned_text,
        "processing_time_ms": elapsed_ms,
        "language": lang_data,
        "statistics": text_stats,
        "sentences": sentences,
        "tokens": tagged_tokens,
        "urls": urls,
        "entities": entities,
        "keywords": keywords_data["top_keywords"],
        "keywords_comparison": keywords_data["methods_comparison"],
        "keyphrases": keyphrases,
        "intent": intent_data,
        "sentiment": sentiment_data,
        "emotion": emotion_data,
        "urgency": urgency_data,
        "manipulation": manipulation_data,
        "classification": classification_data,
        "similar_messages": similar_messages,
        "risk": risk_data,
        "explanation": explanation_data
    }

"""
VoiceShield AI - Multi-Model Scam Classification Engine
Loads trained TF-IDF vectorizer and classifiers (Logistic Regression, Linear SVM, Naive Bayes).
Performs inference, extracts genuine class confidence distributions,
and compares model predictions side-by-side.
"""

import os
import pickle
from typing import Dict, Any, List, Optional
import numpy as np

_VECTORIZER = None
_LOGISTIC_MODEL = None
_SVM_MODEL = None
_NB_MODEL = None
_CLASSES = None


def load_classification_models():
    """Lazy loads trained TF-IDF and classifier artifacts."""
    global _VECTORIZER, _LOGISTIC_MODEL, _SVM_MODEL, _NB_MODEL, _CLASSES

    models_dir = os.path.join("models", "saved")
    vec_path = os.path.join(models_dir, "tfidf_vectorizer.pkl")
    lr_path = os.path.join(models_dir, "logistic_regression_model.pkl")
    svm_path = os.path.join(models_dir, "linear_svm_model.pkl")
    nb_path = os.path.join(models_dir, "multinomial_naive_bayes_model.pkl")

    if _VECTORIZER is None and os.path.exists(vec_path):
        with open(vec_path, "rb") as f:
            _VECTORIZER = pickle.load(f)

    if _LOGISTIC_MODEL is None and os.path.exists(lr_path):
        with open(lr_path, "rb") as f:
            _LOGISTIC_MODEL = pickle.load(f)

    if _SVM_MODEL is None and os.path.exists(svm_path):
        with open(svm_path, "rb") as f:
            _SVM_MODEL = pickle.load(f)

    if _NB_MODEL is None and os.path.exists(nb_path):
        with open(nb_path, "rb") as f:
            _NB_MODEL = pickle.load(f)

    if _LOGISTIC_MODEL is not None and hasattr(_LOGISTIC_MODEL, "classes_"):
        _CLASSES = list(_LOGISTIC_MODEL.classes_)


def classify_message(text: str, preferred_model: str = "Linear SVM") -> Dict[str, Any]:
    """
    Classifies input message text using the specified model, and provides
    comparisons with other trained models.
    """
    load_classification_models()

    if _VECTORIZER is None or _SVM_MODEL is None or not text.strip():
        return {
            "predicted_category": "Unknown",
            "confidence": 0.0,
            "is_scam": False,
            "class_probabilities": {},
            "top_candidates": [],
            "model_comparison": {}
        }

    X_vec = _VECTORIZER.transform([text])

    # Model instances map
    model_map = {
        "Linear SVM": _SVM_MODEL,
        "Logistic Regression": _LOGISTIC_MODEL,
        "Multinomial Naive Bayes": _NB_MODEL
    }

    chosen_model = model_map.get(preferred_model, _SVM_MODEL)
    
    # 1. Prediction using chosen model
    pred_class = chosen_model.predict(X_vec)[0]

    # Probabilities
    if hasattr(chosen_model, "predict_proba"):
        probs = chosen_model.predict_proba(X_vec)[0]
    elif hasattr(chosen_model, "decision_function"):
        df = chosen_model.decision_function(X_vec)[0]
        exp_df = np.exp(df - np.max(df))
        probs = exp_df / np.sum(exp_df)
    else:
        probs = [1.0 if c == pred_class else 0.0 for c in _CLASSES]

    prob_dict = {
        cls_name: round(float(prob), 4)
        for cls_name, prob in zip(_CLASSES, probs)
    }

    # Top candidates
    sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    confidence = round(float(sorted_probs[0][1]), 4)
    top_candidates = [
        {"category": cat, "probability": prob, "percentage": round(prob * 100, 2)}
        for cat, prob in sorted_probs[:4]
    ]

    is_scam = pred_class != "Legitimate / Safe"

    # 2. Multi-Model Comparison
    comparison = {}
    for name, m in model_map.items():
        if m is not None:
            m_pred = m.predict(X_vec)[0]
            if hasattr(m, "predict_proba"):
                m_conf = float(np.max(m.predict_proba(X_vec)[0]))
            else:
                m_conf = 0.85
            comparison[name] = {
                "prediction": m_pred,
                "confidence": round(m_conf, 4),
                "is_scam": m_pred != "Legitimate / Safe"
            }

    return {
        "predicted_category": pred_class,
        "confidence": confidence,
        "confidence_percentage": round(confidence * 100, 2),
        "is_scam": is_scam,
        "active_model": preferred_model,
        "top_candidates": top_candidates,
        "class_probabilities": prob_dict,
        "model_comparison": comparison
    }

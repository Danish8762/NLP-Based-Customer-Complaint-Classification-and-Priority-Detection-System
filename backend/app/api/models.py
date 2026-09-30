"""
VoiceShield AI - Model Center & Academic Evaluation Endpoints
Exposes real training benchmarks, confusion matrices, cross-validation metrics,
and multi-model comparison parameters.
"""

import os
import json
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/models", tags=["Model Center"])


@router.get("")
def get_models_overview():
    """Returns overview of all integrated NLP and ML models in the layered architecture."""
    metrics_path = os.path.join("models", "saved", "model_metrics.json")
    metrics_data = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)

    models_info = [
        {
            "name": "Linear SVM (Calibrated)",
            "purpose": "Primary scam classification & high-dimensional text separation",
            "input": "TF-IDF N-grams (1-3, 5000 features)",
            "output": "14 Category Probabilities & Classification",
            "type": "Support Vector Machine with CalibratedClassifierCV",
            "status": "Production Active",
            "metrics": metrics_data.get("models", {}).get("Linear SVM", {})
        },
        {
            "name": "Logistic Regression (Multinomial)",
            "purpose": "Baseline probabilistic text classification & feature coefficient interpretability",
            "input": "TF-IDF N-grams (1-3, 5000 features)",
            "output": "14 Category Log-Odds & Probabilities",
            "type": "L2-Regularized Multinomial Logistic Regression",
            "status": "Available / Benchmark",
            "metrics": metrics_data.get("models", {}).get("Logistic Regression", {})
        },
        {
            "name": "Multinomial Naive Bayes",
            "purpose": "Probabilistic Bayesian baseline text classification",
            "input": "TF-IDF Frequency Vector",
            "output": "Posterior Category Distribution",
            "type": "Naive Bayes with Laplace Smoothing (alpha=0.2)",
            "status": "Available / Benchmark",
            "metrics": metrics_data.get("models", {}).get("Multinomial Naive Bayes", {})
        },
        {
            "name": "SentenceTransformer (all-MiniLM-L6-v2)",
            "purpose": "Dense semantic vector representations & cosine similarity retrieval",
            "input": "Raw natural language utterance / conversation",
            "output": "384-dimensional unit-normalized embedding vector",
            "type": "Transformer Bi-Encoder (MiniLM architecture)",
            "status": "Active (Local Offline)",
            "dimensions": 384,
            "pooling": "Mean Pooling"
        },
        {
            "name": "VADER Sentiment Reasoner",
            "purpose": "Rule-based and valence-aware sentiment polarity extraction",
            "input": "Tokenized text & punctuation syntax",
            "output": "Compound, positive, neutral, negative valence scores",
            "type": "Lexicon and Rule-based Sentiment Engine",
            "status": "Active"
        },
        {
            "name": "NLTK Named Entity Chunker & Regex Lexicon",
            "purpose": "Cybersecurity & linguistic entity extraction",
            "input": "Part-of-Speech tagged token sequence",
            "output": "Spanned entities (BANK, ACCOUNT, OTP, PERSON, ORG, etc.)",
            "type": "Maximum Entropy Chunking + Targeted Automata",
            "status": "Active"
        }
    ]

    return {
        "dataset_summary": metrics_data.get("dataset_summary", {}),
        "models": models_info
    }


@router.get("/evaluation")
def get_detailed_evaluation():
    """Returns confusion matrices and classification reports for academic viva evaluation."""
    metrics_path = os.path.join("models", "saved", "model_metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=404, detail="Model evaluation metrics file not found.")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    return metrics_data

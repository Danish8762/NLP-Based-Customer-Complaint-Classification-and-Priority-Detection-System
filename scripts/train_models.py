"""
VoiceShield AI - Model Training and Evaluation Pipeline
Trains:
1. TF-IDF + Logistic Regression
2. TF-IDF + Linear SVM (Calibrated)
3. TF-IDF + Multinomial Naive Bayes
4. SentenceTransformer (all-MiniLM-L6-v2) offline vector embedding index

Calculates and stores genuine evaluation metrics (accuracy, precision, recall,
f1-score, confusion matrix, cross-validation scores, inference latencies).
"""

import os
import json
import time
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# Inject truststore for SSL compatibility on Windows
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from sentence_transformers import SentenceTransformer


def run_training():
    data_path = os.path.join("data", "processed", "scam_dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    df = pd.DataFrame(records)
    X = df["text"].values
    y = df["category"].values

    classes = sorted(list(set(y)))
    print(f"Loaded {len(X)} records across {len(classes)} classes.")

    # Train / Test Split (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train size: {len(X_train)}, Test size: {len(X_test)}")

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=5000,
        sublinear_tf=True,
        lowercase=True,
        strip_accents='unicode'
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Models definition
    models = {
        "Logistic Regression": LogisticRegression(
            C=2.0, max_iter=1000, random_state=42
        ),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(C=1.0, random_state=42), cv=3
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.2)
    }

    metrics_result = {
        "dataset_summary": {
            "total_samples": len(X),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "num_classes": len(classes),
            "classes": classes
        },
        "models": {}
    }

    saved_models_dir = os.path.join("models", "saved")
    os.makedirs(saved_models_dir, exist_ok=True)

    # Save Vectorizer
    with open(os.path.join(saved_models_dir, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in models.items():
        print(f"\n--- Training {name} ---")
        start_train = time.time()
        model.fit(X_train_vec, y_train)
        train_time = time.time() - start_train

        # Cross Validation
        cv_scores = cross_val_score(model, X_train_vec, y_train, cv=cv, scoring='f1_weighted')

        # Evaluation on test set
        start_inf = time.time()
        y_pred = model.predict(X_test_vec)
        inf_time_total = time.time() - start_inf
        avg_inf_ms = (inf_time_total / len(X_test)) * 1000

        acc = float(accuracy_score(y_test, y_pred))
        prec_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
        prec_weighted = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
        rec_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
        rec_weighted = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
        f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
        f1_weighted = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))

        cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
        report = classification_report(y_test, y_pred, labels=classes, output_dict=True, zero_division=0)

        # File name for model
        slug = name.lower().replace(" ", "_")
        model_filename = f"{slug}_model.pkl"
        with open(os.path.join(saved_models_dir, model_filename), "wb") as f:
            pickle.dump(model, f)

        metrics_result["models"][name] = {
            "model_name": name,
            "filename": model_filename,
            "training_time_sec": round(train_time, 4),
            "inference_latency_ms": round(avg_inf_ms, 3),
            "accuracy": round(acc, 4),
            "precision_weighted": round(prec_weighted, 4),
            "precision_macro": round(prec_macro, 4),
            "recall_weighted": round(rec_weighted, 4),
            "recall_macro": round(rec_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "f1_macro": round(f1_macro, 4),
            "cv_f1_scores": [round(float(s), 4) for s in cv_scores],
            "cv_f1_mean": round(float(np.mean(cv_scores)), 4),
            "cv_f1_std": round(float(np.std(cv_scores)), 4),
            "confusion_matrix": cm,
            "classification_report": report
        }

        print(f"Accuracy: {acc:.4f} | F1 (Weighted): {f1_weighted:.4f} | Inference: {avg_inf_ms:.2f}ms")

    # 4. Generate Semantic Embeddings for entire dataset for Similarity Search
    print("\n--- Generating Semantic Embeddings with all-MiniLM-L6-v2 ---")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(X.tolist(), show_progress_bar=False, normalize_embeddings=True)
    
    np.save(os.path.join(saved_models_dir, "dataset_embeddings.npy"), embeddings)

    # Save dataset metadata aligned with embeddings
    metadata = []
    for i, r in enumerate(records):
        metadata.append({
            "id": i + 1,
            "text": r["text"],
            "category": r["category"],
            "intent": r["intent"],
            "urgency": r["urgency"],
            "manipulation_techniques": r["manipulation_techniques"],
            "sensitive_requested": r["sensitive_requested"],
            "language": r["language"]
        })
    with open(os.path.join(saved_models_dir, "dataset_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Save overall metrics
    metrics_path = os.path.join(saved_models_dir, "model_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_result, f, indent=2)

    print(f"\nSaved all models and metrics to {saved_models_dir}")


if __name__ == "__main__":
    run_training()

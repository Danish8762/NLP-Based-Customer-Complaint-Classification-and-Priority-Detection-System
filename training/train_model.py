import os
import sys
import joblib
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from nlp.preprocessing import preprocess_text
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


def train_and_evaluate():
    """
    Train TF-IDF + Logistic Regression models for:
    1. Complaint Category Classification
    2. Complaint Priority Detection
    
    Evaluates both models with standard metrics (Accuracy, Precision, Recall, F1)
    and saves artifacts to models/ directory using Joblib.
    """
    print("=" * 70)
    print("NLP MINI-PROJECT: MODEL TRAINING & EVALUATION PIPELINE")
    print("=" * 70)

    # 1. Load Dataset
    data_path = os.path.join(PROJECT_ROOT, 'dataset', 'complaints.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")

    print(f"\n[1/6] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"      Total records loaded: {len(df)}")
    print(f"      Columns: {list(df.columns)}")
    print(f"      Categories: {df['category'].nunique()} unique classes")
    print(f"      Priorities: {df['priority'].nunique()} unique classes ({list(df['priority'].unique())})")

    # 2. NLP Preprocessing
    print("\n[2/6] Applying NLP preprocessing pipeline...")
    print("      (Lowercasing -> Regex cleaning -> Tokenization -> Stopword removal -> Lemmatization)")
    df['clean_complaint'] = df['complaint'].apply(preprocess_text)
    
    # Quick sanity check on preprocessed data
    sample_idx = 0
    print(f"      Sample Original   : \"{df.loc[sample_idx, 'complaint']}\"")
    print(f"      Sample Preprocessed: \"{df.loc[sample_idx, 'clean_complaint']}\"")

    # 3. Train / Test Split
    print("\n[3/6] Splitting dataset into 80% Training and 20% Testing sets...")
    X = df['clean_complaint']
    y_cat = df['category']
    y_prio = df['priority']

    X_train, X_test, y_train_cat, y_test_cat, y_train_prio, y_test_prio = train_test_split(
        X, y_cat, y_prio,
        test_size=0.20,
        random_state=42,
        stratify=y_cat
    )
    print(f"      Training samples : {len(X_train)}")
    print(f"      Testing samples  : {len(X_test)}")

    # 4. Feature Extraction: TF-IDF Vectorizer
    print("\n[4/6] Fitting TF-IDF Vectorizer (unigrams + bigrams, sublinear TF scaling)...")
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3000,
        sublinear_tf=True
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    print(f"      Vocabulary size extracted: {len(tfidf.get_feature_names_out())} features")

    # 5. Train Models using Logistic Regression
    print("\n[5/6] Training Logistic Regression classifiers (random_state=42)...")
    
    # Model A: Category Classifier
    print("      - Training Category Classification Model...")
    category_model = LogisticRegression(max_iter=1000, random_state=42)
    category_model.fit(X_train_tfidf, y_train_cat)

    # Model B: Priority Detection Model
    print("      - Training Priority Detection Model...")
    priority_model = LogisticRegression(C=2.0, max_iter=1000, class_weight='balanced', random_state=42)
    priority_model.fit(X_train_tfidf, y_train_prio)

    # 6. Evaluation
    print("\n[6/6] Evaluating Models on Test Dataset (20% unseen data)...")
    print("-" * 70)

    # Category Model Evaluation
    y_pred_cat = category_model.predict(X_test_tfidf)
    acc_cat = accuracy_score(y_test_cat, y_pred_cat)
    prec_cat = precision_score(y_test_cat, y_pred_cat, average='weighted', zero_division=0)
    rec_cat = recall_score(y_test_cat, y_pred_cat, average='weighted', zero_division=0)
    f1_cat = f1_score(y_test_cat, y_pred_cat, average='weighted', zero_division=0)

    print("CATEGORY CLASSIFICATION RESULTS:")
    print(f"  * Accuracy : {acc_cat * 100:.2f}%")
    print(f"  * Precision: {prec_cat * 100:.2f}% (Weighted Average)")
    print(f"  * Recall   : {rec_cat * 100:.2f}% (Weighted Average)")
    print(f"  * F1-Score : {f1_cat * 100:.2f}% (Weighted Average)")
    print("\nDetailed Category Classification Report:")
    print(classification_report(y_test_cat, y_pred_cat, zero_division=0))

    print("\nCategory Confusion Matrix:")
    print(confusion_matrix(y_test_cat, y_pred_cat))

    # Priority Model Evaluation
    y_pred_prio = priority_model.predict(X_test_tfidf)
    acc_prio = accuracy_score(y_test_prio, y_pred_prio)
    prec_prio = precision_score(y_test_prio, y_pred_prio, average='weighted', zero_division=0)
    rec_prio = recall_score(y_test_prio, y_pred_prio, average='weighted', zero_division=0)
    f1_prio = f1_score(y_test_prio, y_pred_prio, average='weighted', zero_division=0)

    print("-" * 70)
    print("PRIORITY DETECTION RESULTS:")
    print(f"  * Accuracy : {acc_prio * 100:.2f}%")
    print(f"  * Precision: {prec_prio * 100:.2f}% (Weighted Average)")
    print(f"  * Recall   : {rec_prio * 100:.2f}% (Weighted Average)")
    print(f"  * F1-Score : {f1_prio * 100:.2f}% (Weighted Average)")
    print("\nDetailed Priority Classification Report:")
    print(classification_report(y_test_prio, y_pred_prio, zero_division=0))

    # Note on sample dataset
    print("=" * 70)
    print("NOTE FOR COLLEGE VIVA / PROJECT REVIEW:")
    print("These evaluation scores are calculated on a representative synthetic sample")
    print("dataset curated for college mini-project demonstration purposes.")
    print("=" * 70)

    # 7. Save Models and Vectorizer with Joblib
    models_dir = os.path.join(PROJECT_ROOT, 'models')
    os.makedirs(models_dir, exist_ok=True)

    cat_path = os.path.join(models_dir, 'category_model.pkl')
    prio_path = os.path.join(models_dir, 'priority_model.pkl')
    tfidf_path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')

    joblib.dump(category_model, cat_path)
    joblib.dump(priority_model, prio_path)
    joblib.dump(tfidf, tfidf_path)

    print(f"\nSuccessfully saved trained artifacts:")
    print(f"  [OK] {cat_path}")
    print(f"  [OK] {prio_path}")
    print(f"  [OK] {tfidf_path}")
    print("\nModel training and artifact persistence completed successfully!")

if __name__ == '__main__':
    train_and_evaluate()

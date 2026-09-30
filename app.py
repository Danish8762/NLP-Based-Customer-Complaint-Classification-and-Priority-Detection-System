import os
import sys
import joblib
import numpy as np
from flask import Flask, render_template, request, jsonify

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from nlp.preprocessing import preprocess_text, detailed_preprocess
from nlp.sentiment import analyze_sentiment
from training.train_model import train_and_evaluate

app = Flask(__name__)

# Paths to serialized ML models
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
CAT_MODEL_PATH = os.path.join(MODELS_DIR, 'category_model.pkl')
PRIO_MODEL_PATH = os.path.join(MODELS_DIR, 'priority_model.pkl')
TFIDF_PATH = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')

category_model = None
priority_model = None
tfidf_vectorizer = None
tfidf_feature_names = None


def load_artifacts():
    """Load trained models and TF-IDF vocabulary from disk."""
    global category_model, priority_model, tfidf_vectorizer, tfidf_feature_names

    if not (os.path.exists(CAT_MODEL_PATH) and os.path.exists(PRIO_MODEL_PATH) and os.path.exists(TFIDF_PATH)):
        print("[INFO] Model artifacts not found. Initiating training pipeline...")
        train_and_evaluate()

    category_model = joblib.load(CAT_MODEL_PATH)
    priority_model = joblib.load(PRIO_MODEL_PATH)
    tfidf_vectorizer = joblib.load(TFIDF_PATH)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names_out()
    print("[SUCCESS] Category Model, Priority Model, and TF-IDF Vectorizer loaded successfully.")


# Load models at application startup
load_artifacts()


def _get_helpdesk_recommendations(category: str, priority: str, sentiment: str) -> dict:
    """Generate explainable helpdesk routing and SLA recommendations."""
    departments = {
        'Payment Issue': 'Fintech & Billing Reconciliation Desk',
        'Delivery Issue': 'Logistics & Courier Dispatch Operations',
        'Product Issue': 'Quality Assurance & Returns Verification Desk',
        'Technical Issue': 'Tier-2 Engineering & Application Bug Triage',
        'Account Issue': 'Identity Security & User Access Control',
        'Service Issue': 'Customer Experience & Executive Escalations'
    }

    sla_map = {
        'High': 'Immediate Action: Resolve within 2 Hours',
        'Medium': 'Standard Queue: Resolve within 24 Hours',
        'Low': 'Routine Queue: Resolve within 48 Hours'
    }

    action_map = {
        'Payment Issue': 'Verify transaction hash/gateway reference, verify duplicate deduction logs, and initiate refund escrow hold.',
        'Delivery Issue': 'Contact local courier hub for last-mile geolocation scan; issue courier priority tracer ticket.',
        'Product Issue': 'Request photo evidence of defect; generate automated pre-paid reverse pickup label.',
        'Technical Issue': 'Cross-reference crash timestamps against server error telemetry; request client app build logs.',
        'Account Issue': 'Temporarily freeze outgoing transaction privileges; trigger biometric/two-factor reset verification.',
        'Service Issue': 'Assign senior case supervisor; initiate direct phone outreach with customer loyalty voucher.'
    }

    return {
        'department': departments.get(category, 'General Customer Service'),
        'target_sla': sla_map.get(priority, 'Standard: 24 Hours'),
        'action_plan': action_map.get(category, 'Review complaint details and assign to appropriate specialist agent.')
    }


def _calculate_severity_score(priority: str, compound_score: float) -> int:
    """
    Compute unified 0-100 Ticket Urgency Severity Index
    combining Priority classification with VADER negative emotional polarity.
    """
    base_scores = {'High': 72, 'Medium': 45, 'Low': 18}
    score = base_scores.get(priority, 40)

    # Negative emotional valence increases severity up to +25 points
    if compound_score < 0:
        score += int(abs(compound_score) * 25)
    elif compound_score > 0:
        score -= int(compound_score * 10)

    return max(5, min(100, score))


@app.route('/', methods=['GET'])
def index():
    """Render main web dashboard."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Comprehensive NLP analysis endpoint:
    - Preprocessing with detailed token transformations
    - Multi-class Category & Priority probabilities
    - TF-IDF Top Salient Keywords extraction (Explainable AI)
    - VADER Sentiment Polarity
    - Urgency Severity Scoring & Helpdesk Recommendations
    """
    try:
        data = request.get_json(silent=True)
        if not data or 'complaint' not in data:
            return jsonify({'error': 'Please enter a complaint before analyzing.'}), 400

        raw_complaint = data.get('complaint', '').strip()

        if not raw_complaint:
            return jsonify({'error': 'Please enter a complaint before analyzing.'}), 400

        if len(raw_complaint) < 5:
            return jsonify({'error': 'Complaint is too short. Please provide more descriptive details.'}), 400

        # Step 1: Detailed NLP Preprocessing
        detailed_nlp = detailed_preprocess(raw_complaint)
        clean_text = detailed_nlp['final_text']

        if not clean_text:
            return jsonify({'error': 'Complaint contained only symbols or stop-words. Please enter a valid sentence.'}), 400

        # Step 2: TF-IDF Vectorization
        vectorized = tfidf_vectorizer.transform([clean_text])

        # Step 3: Extract Top Salient Keywords from TF-IDF
        coo = vectorized.tocoo()
        top_keywords = []
        if coo.data.size > 0:
            word_weights = sorted(zip(coo.col, coo.data), key=lambda x: x[1], reverse=True)[:6]
            for col_idx, weight in word_weights:
                top_keywords.append({
                    'term': str(tfidf_feature_names[col_idx]),
                    'weight': round(float(weight), 3)
                })

        # Step 4: Category Classification & Full Probability Distribution
        cat_probs = category_model.predict_proba(vectorized)[0]
        max_cat_idx = int(np.argmax(cat_probs))
        category = str(category_model.classes_[max_cat_idx])
        confidence = round(float(cat_probs[max_cat_idx]), 4)

        cat_distribution = [
            {'name': str(cls_name), 'probability': round(float(prob), 4)}
            for cls_name, prob in sorted(zip(category_model.classes_, cat_probs), key=lambda x: x[1], reverse=True)
        ]

        # Step 5: Priority Detection & Distribution
        prio_probs = priority_model.predict_proba(vectorized)[0]
        max_prio_idx = int(np.argmax(prio_probs))
        priority = str(priority_model.classes_[max_prio_idx])
        priority_confidence = round(float(prio_probs[max_prio_idx]), 4)

        prio_distribution = [
            {'name': str(cls_name), 'probability': round(float(prob), 4)}
            for cls_name, prob in sorted(zip(priority_model.classes_, prio_probs), key=lambda x: x[1], reverse=True)
        ]

        # Step 6: Sentiment Analysis (VADER)
        sentiment_res = analyze_sentiment(raw_complaint)

        # Step 7: Unified Severity Score & Helpdesk Recommendations
        severity_score = _calculate_severity_score(priority, sentiment_res['compound_score'])
        recommendations = _get_helpdesk_recommendations(category, priority, sentiment_res['sentiment'])

        response_payload = {
            'category': category,
            'confidence': confidence,
            'category_distribution': cat_distribution,
            'priority': priority,
            'priority_confidence': priority_confidence,
            'priority_distribution': prio_distribution,
            'sentiment': sentiment_res['sentiment'],
            'compound_score': sentiment_res['compound_score'],
            'sentiment_details': sentiment_res,
            'severity_score': severity_score,
            'helpdesk_recommendation': recommendations,
            'top_keywords': top_keywords,
            'nlp_details': detailed_nlp,
            'preprocessed_text': clean_text
        }

        return jsonify(response_payload), 200

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred during processing: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'models_loaded': category_model is not None and priority_model is not None
    }), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

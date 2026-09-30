import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure vader_lexicon is available
def _ensure_vader():
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except (LookupError, AttributeError):
        try:
            nltk.download('vader_lexicon', quiet=True)
        except Exception:
            pass

_ensure_vader()

try:
    _analyzer = SentimentIntensityAnalyzer()
    # Enhance VADER lexicon with customer service domain terms
    # Standard VADER was trained on social media (tweets/reviews).
    # In complaint ticketing, technical failures, service disruptions,
    # and unauthorized billing express strong negative sentiment.
    domain_sentiment_terms = {
        'deducted': -1.5,
        'deducted twice': -2.5,
        'cancelled': -2.0,
        'crashed': -2.5,
        'crashing': -2.5,
        'crashes': -2.5,
        'crash': -2.2,
        'damaged': -2.4,
        'broken': -2.3,
        'unauthorized': -2.8,
        'fraud': -3.2,
        'fraudulent': -3.2,
        'stolen': -3.0,
        'hacked': -3.2,
        'hijacked': -3.2,
        'delayed': -1.8,
        'delay': -1.5,
        'missing': -2.0,
        'failed': -2.2,
        'fails': -2.0,
        'failing': -2.0,
        'error': -1.8,
        'glitch': -1.8,
        'bug': -1.5,
        'unable': -1.5,
        'cannot': -1.2,
        'outage': -2.5,
        'unresponsive': -2.0,
        'corrupted': -2.2,
        'abusive': -3.2,
        'harassment': -3.4,
        'threatened': -3.2,
        'defective': -2.2
    }
    _analyzer.lexicon.update(domain_sentiment_terms)
except Exception:
    _analyzer = None


def analyze_sentiment(text: str) -> dict:
    """
    Perform sentiment analysis using NLTK VADER (Valence Aware Dictionary and sEntiment Reasoner)
    tailored with customer-complaint domain sentiment weights.
    
    Returns:
        dict: {
            'sentiment': 'Positive' | 'Neutral' | 'Negative',
            'compound_score': float (-1.0 to 1.0),
            'positive_score': float,
            'neutral_score': float,
            'negative_score': float
        }
    """
    if not text or not isinstance(text, str) or not _analyzer:
        return {
            'sentiment': 'Neutral',
            'compound_score': 0.0,
            'positive_score': 0.0,
            'neutral_score': 1.0,
            'negative_score': 0.0
        }

    scores = _analyzer.polarity_scores(text)
    compound = scores['compound']

    # Standard VADER threshold classification
    if compound >= 0.05:
        sentiment = 'Positive'
    elif compound <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'

    return {
        'sentiment': sentiment,
        'compound_score': round(compound, 2),
        'positive_score': round(scores['pos'], 2),
        'neutral_score': round(scores['neu'], 2),
        'negative_score': round(scores['neg'], 2)
    }


if __name__ == '__main__':
    test_samples = [
        "My payment was deducted twice from my account.",
        "My package has still not arrived after one week.",
        "The mobile application keeps crashing when I open it.",
        "I want to know how I can change my account password.",
        "The product I received is damaged.",
        "Thank you so much for the quick help, excellent service!"
    ]
    for sample in test_samples:
        res = analyze_sentiment(sample)
        print(f"'{sample}' -> {res['sentiment']} (compound: {res['compound_score']})")

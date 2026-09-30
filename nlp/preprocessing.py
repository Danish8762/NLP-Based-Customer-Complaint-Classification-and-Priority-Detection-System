import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK resources are available
def _ensure_nltk_resources():
    required_packages = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
    for pkg in required_packages:
        try:
            if 'punkt' in pkg:
                nltk.data.find(f'tokenizers/{pkg}')
            else:
                nltk.data.find(f'corpora/{pkg}')
        except (LookupError, AttributeError):
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass

_ensure_nltk_resources()

# Initialize NLP components
try:
    _lemmatizer = WordNetLemmatizer()
    _stop_words = set(stopwords.words('english'))
except Exception:
    _lemmatizer = None
    _stop_words = set()

# Crucial words in customer complaints that should NOT be filtered out as stop words
# These words convey negation, downtime, or critical service status
_RETAIN_WORDS = {'down', 'not', 'no', 'nor', 'neither', 'never', 'off', 'out', 'again', 'cannot'}
_stop_words = _stop_words - _RETAIN_WORDS
_stop_words.add('since')


def preprocess_text(text: str) -> str:
    """
    Standard preprocessing pipeline returning clean string:
    1. Lowercasing
    2. URL, email, and special character removal
    3. Word tokenization
    4. Stop-word removal (preserving key negation words)
    5. WordNet Lemmatization
    """
    if not text or not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    processed_tokens = []
    for token in tokens:
        token = token.strip()
        if len(token) > 1 and token not in _stop_words:
            if _lemmatizer:
                lemma = _lemmatizer.lemmatize(token, pos='n')
                if lemma == token:
                    lemma = _lemmatizer.lemmatize(token, pos='v')
                processed_tokens.append(lemma)
            else:
                processed_tokens.append(token)

    return ' '.join(processed_tokens)


def detailed_preprocess(text: str) -> dict:
    """
    Enhanced step-by-step pipeline for interactive visualization:
    Returns intermediate representations, filtered stop-words,
    lemmatization pairings, and lexical diversity statistics.
    """
    if not text or not isinstance(text, str):
        return {
            'raw': '',
            'lowercased': '',
            'cleaned': '',
            'tokens': [],
            'stopwords_removed': [],
            'retained_tokens': [],
            'lemmas': [],
            'final_text': '',
            'stats': {
                'total_chars': 0,
                'total_words': 0,
                'unique_words': 0,
                'lexical_diversity': 0.0
            }
        }

    raw = text.strip()
    lowercased = raw.lower()

    # Regex cleaning
    cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', lowercased)
    cleaned = re.sub(r'\S+@\S+', ' ', cleaned)
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', cleaned)

    # Tokenization
    try:
        raw_tokens = word_tokenize(cleaned)
    except Exception:
        raw_tokens = cleaned.split()

    stopwords_removed = []
    retained_tokens = []
    lemmas = []
    final_tokens = []

    for t in raw_tokens:
        tok = t.strip()
        if not tok:
            continue
        if tok in _stop_words or len(tok) <= 1:
            stopwords_removed.append(tok)
        else:
            retained_tokens.append(tok)
            if _lemmatizer:
                lemma = _lemmatizer.lemmatize(tok, pos='n')
                if lemma == tok:
                    lemma = _lemmatizer.lemmatize(tok, pos='v')
                lemmas.append({'original': tok, 'lemma': lemma})
                final_tokens.append(lemma)
            else:
                lemmas.append({'original': tok, 'lemma': tok})
                final_tokens.append(tok)

    words_count = len(raw_tokens)
    unique_count = len(set(raw_tokens))
    lex_diversity = round((unique_count / words_count * 100), 1) if words_count > 0 else 0.0

    return {
        'raw': raw,
        'lowercased': lowercased,
        'cleaned': ' '.join(cleaned.split()),
        'tokens': raw_tokens,
        'stopwords_removed': stopwords_removed,
        'retained_tokens': retained_tokens,
        'lemmas': lemmas,
        'final_text': ' '.join(final_tokens),
        'stats': {
            'total_chars': len(raw),
            'total_words': words_count,
            'unique_words': unique_count,
            'lexical_diversity': lex_diversity
        }
    }


if __name__ == '__main__':
    sample = "My Internet connection has been down since yesterday!"
    print("Preprocess text:", preprocess_text(sample))
    print("Detailed stats :", detailed_preprocess(sample)['stats'])

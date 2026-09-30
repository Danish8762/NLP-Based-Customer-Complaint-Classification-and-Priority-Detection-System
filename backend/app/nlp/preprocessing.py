"""
VoiceShield AI - NLP Preprocessing Module
Modular NLP pipeline providing text cleaning, normalization, sentence segmentation,
tokenization, lemmatization, POS tagging, and linguistic statistics.
"""

import re
import string
from typing import List, Dict, Any, Tuple
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# Ensure resources are available
try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    STOP_WORDS = set(stopwords.words("english"))

LEMMATIZER = WordNetLemmatizer()

URL_REGEX = re.compile(
    r'(?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’])',
    re.IGNORECASE
)

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,5}')
MONEY_REGEX = re.compile(r'(?:[\$₹£€]|INR|USD|EUR|Rs\.?|Rupees?)\s*\d+(?:,\d+)*(?:\.\d+)?', re.IGNORECASE)


def clean_text(text: str) -> str:
    """Removes irregular whitespace, non-printable characters, preserves casing for acronyms."""
    if not text:
        return ""
    cleaned = re.sub(r'[\r\n\t]+', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def normalize_text(text: str) -> str:
    """Lowercase text and strip excess punctuation for TF-IDF / keyword matching."""
    cleaned = clean_text(text).lower()
    return cleaned


def extract_sentences(text: str) -> List[str]:
    """Segments text into sentences using NLTK sent_tokenize with regex fallback."""
    if not text:
        return []
    try:
        sentences = sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    return [s for s in sentences if s.strip()]


def extract_urls(text: str) -> List[Dict[str, Any]]:
    """Extracts URLs and performs structural heuristic risk analysis."""
    matches = URL_REGEX.findall(text)
    # The regex findall returns tuples if groups exist, so re-find full matches
    raw_urls = [m.group(0) for m in URL_REGEX.finditer(text)]
    results = []
    
    suspicious_tlds = {'.xyz', '.top', '.cc', '.info', '.site', '.club', '.tk', '.ga', '.cf', '.work', '.me'}
    
    for url in raw_urls:
        url_lower = url.lower()
        is_ip = bool(re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_lower))
        has_suspicious_tld = any(url_lower.endswith(tld) or (tld + '/') in url_lower for tld in suspicious_tlds)
        excessive_subdomains = len(url.split('/')[0].split('.')) > 3
        is_shortened = any(short in url_lower for short in ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'is.gd'])
        
        heuristics = []
        if is_ip:
            heuristics.append("IP-based URL host")
        if has_suspicious_tld:
            heuristics.append("Unusual/high-risk TLD")
        if excessive_subdomains:
            heuristics.append("Excessive subdomain depth")
        if is_shortened:
            heuristics.append("URL shortener used to conceal target")
            
        suspicious_score = len(heuristics) * 25
        results.append({
            "url": url,
            "is_suspicious": len(heuristics) > 0,
            "suspicious_score": min(100, suspicious_score),
            "reasons": heuristics
        })
    return results


def tokenize_and_tag(text: str) -> List[Dict[str, Any]]:
    """
    Performs tokenization, lemmatization, and POS tagging.
    Identifies whether each token is an informative/important word.
    """
    if not text:
        return []
    
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    
    token_details = []
    important_pos = {"NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "JJ", "JJR", "JJS", "RB", "RBR", "RBS"}
    
    for token, tag in pos_tags:
        # Convert POS to WordNet tag format
        wn_tag = "n"
        if tag.startswith("V"):
            wn_tag = "v"
        elif tag.startswith("J"):
            wn_tag = "a"
        elif tag.startswith("R"):
            wn_tag = "r"
            
        try:
            lemma = LEMMATIZER.lemmatize(token.lower(), wn_tag)
        except Exception:
            lemma = token.lower()
            
        is_punct = token in string.punctuation
        is_stop = token.lower() in STOP_WORDS
        is_important = (tag in important_pos) and (not is_stop) and (not is_punct) and len(token) > 1
        
        token_details.append({
            "token": token,
            "lemma": lemma,
            "pos": tag,
            "is_stop": is_stop,
            "is_important": is_important
        })
        
    return token_details


def compute_text_statistics(text: str, tokens: List[Dict[str, Any]], sentences: List[str]) -> Dict[str, Any]:
    """Computes comprehensive linguistic statistics."""
    char_count = len(text)
    word_tokens = [t["token"] for t in tokens if t["token"] not in string.punctuation]
    word_count = len(word_tokens)
    sent_count = max(1, len(sentences))
    avg_sentence_len = round(word_count / sent_count, 2)
    
    lower_words = [w.lower() for w in word_tokens]
    unique_words = len(set(lower_words))
    lexical_diversity = round((unique_words / word_count), 4) if word_count > 0 else 0.0
    
    # Uppercase analysis (indicators of screaming / false urgency)
    caps_words = [w for w in word_tokens if w.isupper() and len(w) > 1]
    caps_ratio = round((len(caps_words) / word_count), 4) if word_count > 0 else 0.0
    
    # Exclamation & question counts
    exclamation_count = text.count("!")
    question_count = text.count("?")
    
    # POS distribution counts
    pos_counts: Dict[str, int] = {}
    for t in tokens:
        tag = t["pos"]
        pos_counts[tag] = pos_counts.get(tag, 0) + 1
        
    return {
        "character_count": char_count,
        "word_count": word_count,
        "sentence_count": sent_count,
        "avg_sentence_length": avg_sentence_len,
        "unique_words": unique_words,
        "lexical_diversity": lexical_diversity,
        "capitalized_word_count": len(caps_words),
        "capitalized_ratio": caps_ratio,
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "pos_distribution": pos_counts
    }


def generate_ngrams(words: List[str], n: int) -> List[str]:
    """Generates contiguous n-grams from cleaned word list."""
    if len(words) < n:
        return []
    return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

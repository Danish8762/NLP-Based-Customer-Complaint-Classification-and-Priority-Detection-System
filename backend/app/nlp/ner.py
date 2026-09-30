"""
VoiceShield AI - Named Entity Recognition Module
Extracts standard linguistic entities (PERSON, ORG, GPE, DATE, MONEY)
and domain-specific cybersecurity entities (BANK, ACCOUNT, OTP/CODE, PHONE, EMAIL, URL).
Provides character offsets for interactive UI highlighting.
"""

import re
from typing import List, Dict, Any
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

KNOWN_BANKS = {
    "sbi", "state bank of india", "hdfc", "hdfc bank", "icici", "icici bank",
    "axis", "axis bank", "kotak", "kotak mahindra", "pnb", "punjab national bank",
    "bank of baroda", "canara bank", "yes bank", "chase", "bank of america",
    "wells fargo", "citi", "citibank", "barclays", "hsbc"
}

KNOWN_PRODUCTS = {
    "netflix", "amazon", "flipkart", "google", "microsoft", "apple", "paytm",
    "phonepe", "gpay", "google pay", "whatsapp", "telegram", "facebook",
    "instagram", "swiggy", "zomato", "uber", "ola", "ebay", "paypal"
}

AUTH_KEYWORDS = {
    "otp": "OTP / One-Time Passcode",
    "pin": "Security PIN / MPIN",
    "cvv": "Card Verification Value (CVV)",
    "password": "Account Password",
    "aadhaar": "Aadhaar Identity Number",
    "pan": "PAN Card Tax Identifier",
    "passcode": "Access Passcode",
    "mpin": "Mobile Banking PIN"
}


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts entities using a combination of NLTK chunking and targeted regex/lexical analyzers.
    Returns entity text, type, category, start, and end offsets.
    """
    entities: List[Dict[str, Any]] = []
    text_lower = text.lower()

    # 1. Regex-based Specialized Cybersecurity & Financial Entities
    # URLs
    from backend.app.nlp.preprocessing import URL_REGEX, EMAIL_REGEX, PHONE_REGEX, MONEY_REGEX

    for match in URL_REGEX.finditer(text):
        entities.append({
            "text": match.group(0),
            "label": "URL",
            "category": "CYBER_INDICATOR",
            "start": match.start(),
            "end": match.end(),
            "description": "Web link / Domain address"
        })

    # Emails
    for match in EMAIL_REGEX.finditer(text):
        entities.append({
            "text": match.group(0),
            "label": "EMAIL",
            "category": "CONTACT",
            "start": match.start(),
            "end": match.end(),
            "description": "Email address"
        })

    # Phone Numbers
    for match in PHONE_REGEX.finditer(text):
        # avoid matching simple small numbers
        matched_str = match.group(0)
        digits_only = re.sub(r'\D', '', matched_str)
        if len(digits_only) >= 7:
            entities.append({
                "text": matched_str,
                "label": "PHONE",
                "category": "CONTACT",
                "start": match.start(),
                "end": match.end(),
                "description": "Telephone or mobile contact"
            })

    # Money / Currency
    for match in MONEY_REGEX.finditer(text):
        entities.append({
            "text": match.group(0),
            "label": "MONEY",
            "category": "FINANCIAL",
            "start": match.start(),
            "end": match.end(),
            "description": "Monetary value / currency"
        })

    # Bank Names
    for bank in KNOWN_BANKS:
        pattern = re.compile(r'\b' + re.escape(bank) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(text):
            entities.append({
                "text": text[m.start():m.end()],
                "label": "BANK",
                "category": "FINANCIAL_INSTITUTION",
                "start": m.start(),
                "end": m.end(),
                "description": "Banking organization"
            })

    # Product / Tech Services
    for prod in KNOWN_PRODUCTS:
        pattern = re.compile(r'\b' + re.escape(prod) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(text):
            entities.append({
                "text": text[m.start():m.end()],
                "label": "PRODUCT",
                "category": "TECHNOLOGY",
                "start": m.start(),
                "end": m.end(),
                "description": "Brand, Application or Service"
            })

    # Authentication / Identity Tokens (OTP, PIN, Aadhaar, PAN)
    for auth_term, desc in AUTH_KEYWORDS.items():
        pattern = re.compile(r'\b' + re.escape(auth_term) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(text):
            entities.append({
                "text": text[m.start():m.end()],
                "label": "AUTH_CREDENTIAL",
                "category": "SENSITIVE_DATA",
                "start": m.start(),
                "end": m.end(),
                "description": desc
            })

    # Account Number Patterns (e.g. account #XX1234 or account 12345678)
    acc_pattern = re.compile(r'\b(?:account|acct|a/c)\s*(?:#|no\.?|num\.?)?\s*([xX\*\d]{4,16})\b', re.IGNORECASE)
    for m in acc_pattern.finditer(text):
        entities.append({
            "text": m.group(0),
            "label": "ACCOUNT",
            "category": "FINANCIAL_IDENTIFIER",
            "start": m.start(),
            "end": m.end(),
            "description": "Bank / Service Account Identifier"
        })

    # 2. NLTK Linguistic Named Entity Chunker for PERSON, ORGANIZATION, GPE
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        chunks = ne_chunk(tagged, binary=False)

        current_pos = 0
        for chunk in chunks:
            if isinstance(chunk, Tree):
                ent_name = " ".join(c[0] for c in chunk.leaves())
                ent_label = chunk.label()
                
                # Find occurrence in text from current_pos
                start_idx = text_lower.find(ent_name.lower(), current_pos)
                if start_idx != -1:
                    end_idx = start_idx + len(ent_name)
                    current_pos = end_idx
                    # Map NLTK label
                    std_label = ent_label
                    if ent_label == "GPE":
                        std_label = "LOCATION"
                    elif ent_label == "ORGANIZATION":
                        std_label = "ORGANIZATION"
                    elif ent_label == "PERSON":
                        std_label = "PERSON"
                        
                    entities.append({
                        "text": text[start_idx:end_idx],
                        "label": std_label,
                        "category": "LINGUISTIC_ENTITY",
                        "start": start_idx,
                        "end": end_idx,
                        "description": f"Standard NLP {std_label} entity"
                    })
    except Exception:
        pass

    # Deduplicate overlapping entities, preferring longer spans or specialized labels
    entities.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))
    deduped: List[Dict[str, Any]] = []
    last_end = -1

    for ent in entities:
        if ent["start"] >= last_end:
            deduped.append(ent)
            last_end = ent["end"]
        else:
            # Overlap: keep if it's a more specific category than standard LINGUISTIC_ENTITY
            if deduped and deduped[-1]["category"] == "LINGUISTIC_ENTITY" and ent["category"] != "LINGUISTIC_ENTITY":
                deduped[-1] = ent
                last_end = ent["end"]

    return deduped

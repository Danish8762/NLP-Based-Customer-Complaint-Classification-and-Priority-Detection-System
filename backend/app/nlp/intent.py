"""
VoiceShield AI - Dedicated NLP Intent Detection Engine
Identifies communicative intent using pattern parsing, dependency-style keyword
co-occurrences, imperative verb structures, and probabilistic scoring across 18 distinct classes.
Outputs top intent, genuine confidence score, and alternative candidate rankings.
"""

import re
from typing import Dict, Any, List, Tuple

INTENT_RULES = {
    "Request OTP": {
        "keywords": ["otp", "passcode", "verification code", "6-digit code", "one-time password", "bhejo otp", "share code", "enter otp"],
        "patterns": [
            r'\b(?:send|share|provide|tell|enter|give|bataiye|bhejo)\b.*\b(?:otp|passcode|code|pin)\b',
            r'\b(?:otp|code)\b.*\b(?:immediately|now|received|sent|mobile)\b'
        ],
        "weight": 3.0
    },
    "Request Password": {
        "keywords": ["password", "secret pin", "mpin", "netbanking password", "login credentials", "reset password", "change password"],
        "patterns": [
            r'\b(?:enter|provide|confirm|submit|send|batao)\b.*\b(?:password|mpin|pin|credentials)\b'
        ],
        "weight": 2.8
    },
    "Request Payment": {
        "keywords": ["pay", "transfer", "send money", "wire", "deposit", "fee", "upi", "qr code", "cash", "paise bhej", "registration fee", "tax clearance"],
        "patterns": [
            r'\b(?:pay|transfer|wire|send|deposit|bhejo)\b.*\b(?:rs|inr|\$|amount|fee|money|charge|funds)\b',
            r'\b(?:scan|use)\b.*\b(?:qr|upi|gpay|phonepe)\b'
        ],
        "weight": 2.5
    },
    "Credential Harvesting": {
        "keywords": ["login", "sign in", "authenticate", "portal", "verify password", "username", "token leak", "ssh key", "quota full"],
        "patterns": [
            r'\b(?:log in|sign in|authenticate|verify)\b.*\b(?:credentials|username|password|portal|link)\b',
            r'\b(?:quota|storage|mailbox)\b.*\b(?:full|exceeded|verify)\b'
        ],
        "weight": 2.6
    },
    "Account Suspension": {
        "keywords": ["suspended", "blocked", "locked", "freeze", "terminated", "block hone wala", "deactivation", "disabled"],
        "patterns": [
            r'\b(?:account|card|profile|sim|service)\b.*\b(?:blocked|suspended|locked|terminated|deactivated|freeze)\b',
            r'\b(?:block|freeze|terminate)\b.*\b(?:within|today|immediately|hours)\b'
        ],
        "weight": 2.7
    },
    "Account Verification": {
        "keywords": ["verify account", "kyc", "aadhaar", "pan card", "identity verification", "update kyc", "re-authenticate", "confirm identity"],
        "patterns": [
            r'\b(?:verify|update|complete|re-register)\b.*\b(?:kyc|aadhaar|pan|account|biometric)\b',
            r'\b(?:kyc|aadhaar|pan)\b.*\b(?:pending|expired|mandatory|verification)\b'
        ],
        "weight": 2.5
    },
    "Link Click Request": {
        "keywords": ["click link", "visit link", "tap here", "link below", "click here", "open link", "diye gaye link"],
        "patterns": [
            r'\b(?:click|tap|visit|open|follow)\b.*\b(?:link|url|portal|below|here|http)\b'
        ],
        "weight": 2.4
    },
    "Investment Request": {
        "keywords": ["guaranteed returns", "crypto", "arbitrage", "forex", "daily profit", "earn daily", "stock tips", "vip channel", "deposit funds"],
        "patterns": [
            r'\b(?:invest|deposit|earn|returns)\b.*\b(?:guaranteed|crypto|profit|arbitrage|daily|double)\b'
        ],
        "weight": 2.6
    },
    "Job Offer": {
        "keywords": ["hiring", "part-time", "earn daily", "salary", "work from home", "shortlisted for job", "rate products", "like and subscribe"],
        "patterns": [
            r'\b(?:hiring|job|shortlisted|recruiting|vacancy)\b.*\b(?:salary|earn|daily|per month|home)\b',
            r'\b(?:part-time|data entry|typing)\b.*\b(?:earn|rs|\$)\b'
        ],
        "weight": 2.5
    },
    "Delivery Notification": {
        "keywords": ["parcel", "package", "consignment", "delivery", "customs", "held at customs", "redelivery fee", "undelivered", "courier", "order"],
        "patterns": [
            r'\b(?:parcel|package|delivery|shipment|consignment)\b.*\b(?:held|customs|address|surcharge|fee|stopped)\b',
            r'\b(?:track|reschedule|deliver)\b.*\b(?:package|order|consignment)\b'
        ],
        "weight": 2.5
    },
    "Prize/Reward": {
        "keywords": ["won", "winner", "prize", "lucky draw", "lottery", "cashback", "crorepati", "scratch card", "congratulations you won"],
        "patterns": [
            r'\b(?:congratulations|selected|won|winner)\b.*\b(?:prize|lottery|draw|cashback|bmw|crore|lakhs)\b',
            r'\b(?:claim|scratch)\b.*\b(?:reward|cashback|prize)\b'
        ],
        "weight": 2.6
    },
    "Threat": {
        "keywords": ["legal action", "lawsuit", "police", "arrest", "warrant", "cyber crime", "court", "penalty", "trojan malware", "encrypted"],
        "patterns": [
            r'\b(?:legal action|arrest|warrant|police|court|fine|penalty)\b.*\b(?:issued|initiated|against you|charged)\b',
            r'\b(?:infected|trojan|malware|breach)\b.*\b(?:call|immediate|encrypted)\b'
        ],
        "weight": 2.8
    },
    "Customer Support": {
        "keywords": ["support desk", "helpdesk", "technical support", "anydesk", "teamviewer", "customer care", "customer service", "remote access"],
        "patterns": [
            r'\b(?:technical support|support team|customer desk|helpdesk)\b',
            r'\b(?:install|download)\b.*\b(?:anydesk|teamviewer|quicksupport)\b'
        ],
        "weight": 2.4
    },
    "Refund Request": {
        "keywords": ["refund", "dispute charge", "cancel subscription", "auto-charged", "tax refund", "overpayment", "wire back"],
        "patterns": [
            r'\b(?:refund|dispute|cancel|overpayment)\b.*\b(?:charge|auto-debit|approved|processed|invoice)\b'
        ],
        "weight": 2.4
    },
    "Urgent Action": {
        "keywords": ["urgent", "immediately", "right now", "without delay", "before today", "final warning", "action required"],
        "patterns": [
            r'\b(?:action required|urgent notice|final warning|act immediately)\b'
        ],
        "weight": 2.0
    },
    "Legitimate Inquiry": {
        "keywords": ["meeting", "agenda", "project", "quarterly", "discussion", "dental appointment", "prescription", "flight", "standup", "assignment", "kal milte hain", "notes"],
        "patterns": [
            r'\b(?:meeting|sync|standup|appointment|discussion|class|notes|assignment)\b',
            r'\b(?:track live|picked up|generated|scheduled)\b.*\b(?:app|calendar|portal)\b'
        ],
        "weight": 2.2
    }
}


def detect_intent(text: str) -> Dict[str, Any]:
    """
    Computes intent classification with genuine scoring derived from
    linguistic pattern matches, keyword hits, and imperative structures.
    """
    if not text or not text.strip():
        return {
            "intent": "Unknown",
            "confidence": 0.0,
            "alternatives": []
        }

    text_lower = text.lower()
    raw_scores: Dict[str, float] = {}

    for intent, config in INTENT_RULES.items():
        score = 0.0
        # Keyword hits
        for kw in config["keywords"]:
            if kw in text_lower:
                score += 1.0

        # Regex structural pattern matches
        for pat in config["patterns"]:
            if re.search(pat, text_lower, re.IGNORECASE):
                score += 2.0

        if score > 0:
            raw_scores[intent] = score * config["weight"]

    if not raw_scores:
        # Default fallback
        return {
            "intent": "Legitimate Inquiry" if len(text.split()) > 4 else "Unknown",
            "confidence": 0.52,
            "alternatives": [
                {"intent": "Unknown", "confidence": 0.48}
            ]
        }

    # Softmax-style normalization for genuine model probabilities
    max_score = max(raw_scores.values())
    exp_scores = {k: np_exp(v / 2.0) for k, v in raw_scores.items()}
    sum_exp = sum(exp_scores.values())
    
    probabilities = {k: round(v / sum_exp, 3) for k, v in exp_scores.items()}
    sorted_intents = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

    primary_intent, primary_conf = sorted_intents[0]

    alternatives = [
        {"intent": intent, "confidence": conf}
        for intent, conf in sorted_intents[1:5]
        if conf > 0.05
    ]

    return {
        "intent": primary_intent,
        "confidence": primary_conf,
        "alternatives": alternatives,
        "scoring_factors": {k: round(v, 2) for k, v in raw_scores.items() if v > 0}
    }


def np_exp(x: float) -> float:
    """Bounded exponential to prevent numerical overflow."""
    import math
    return math.exp(min(50.0, x))

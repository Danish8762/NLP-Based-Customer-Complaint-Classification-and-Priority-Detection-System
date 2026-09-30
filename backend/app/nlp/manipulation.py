"""
VoiceShield AI - Psychological Manipulation & Social Engineering Detection Module
Identifies 14 distinct social engineering and manipulation patterns:
1. Urgency
2. Fear
3. Threat
4. Authority Impersonation
5. Reward/Greed
6. Curiosity
7. Scarcity
8. Emotional Pressure
9. Trust Exploitation
10. Secrecy
11. Social Pressure
12. Financial Pressure
13. Account Suspension Pressure
14. Time Pressure

Also implements Sensitive Information Request Detection (OTP, Passwords, PIN, CVV,
Card Details, Aadhaar/PAN, Remote Desktop tools).
"""

import re
from typing import Dict, Any, List

MANIPULATION_PATTERNS = {
    "Urgency": {
        "regex": r'\b(?:immediately|right now|turant|jaldi|urgent|fatafat|without delay|act now)\b',
        "explanation": "Creates intense time pressure to bypass critical thinking and force immediate compliance.",
        "severity": "HIGH"
    },
    "Fear": {
        "regex": r'\b(?:compromised|hacked|breach|arrested|lawsuit|penalty|criminal|police|illegal|virus|infected|warrant)\b',
        "explanation": "Induces panic and distress to manipulate the victim into believing they face imminent harm.",
        "severity": "CRITICAL"
    },
    "Threat": {
        "regex": r'\b(?:legal action|terminate|police warrant|court summons|penalized|severe consequences|jailed)\b',
        "explanation": "Uses explicit punitive threats to compel compliance through intimidation.",
        "severity": "CRITICAL"
    },
    "Authority Impersonation": {
        "regex": r'\b(?:state bank|hdfc|icici|axis bank|police department|cyber crime cell|microsoft support|google security|income tax|irs|customs officer|telecom compliance|officer|manager)\b',
        "explanation": "Falsely borrows institutional authority and prestige to establish unearned credibility.",
        "severity": "HIGH"
    },
    "Reward/Greed": {
        "regex": r'\b(?:won|winner|lucky draw|cashback|lottery|crorepati|400% returns|guaranteed profit|free gift|unclaimed reward|100x)\b',
        "explanation": "Exploits financial desires and greed through unrealistically lucrative promises.",
        "severity": "HIGH"
    },
    "Curiosity": {
        "regex": r'\b(?:secret method|leaked|shocking truth|see who viewed|you won\'t believe|mystery)\b',
        "explanation": "Appeals to natural human curiosity to induce unsafe clicks or engagement.",
        "severity": "MEDIUM"
    },
    "Scarcity": {
        "regex": r'\b(?:limited to first|only \d+ left|exclusive pre-ipo|rare opportunity|quota full)\b',
        "explanation": "Manufactures artificial scarcity to invoke fear of missing out (FOMO).",
        "severity": "MEDIUM"
    },
    "Emotional Pressure": {
        "regex": r'\b(?:hospital emergency|dearest love|darling|stranded abroad|need rent|family crisis|help me dad)\b',
        "explanation": "Preys on empathy, familial affection, or romantic feelings to solicit urgent financial transfers.",
        "severity": "CRITICAL"
    },
    "Trust Exploitation": {
        "regex": r'\b(?:trust me|100% safe|certified|official partner|verified desk|government approved|bhai)\b',
        "explanation": "Artificially asserts reliability and friendliness to lower defensive skepticism.",
        "severity": "MEDIUM"
    },
    "Secrecy": {
        "regex": r'\b(?:don\'t tell anyone|keep this secret|confidential deal|between you and me|private channel)\b',
        "explanation": "Isolates the victim from trusted friends, family, or official channels to prevent verification.",
        "severity": "CRITICAL"
    },
    "Social Pressure": {
        "regex": r'\b(?:share with 5 friends|everyone is doing it|group consensus|join \d+ investors)\b',
        "explanation": "Pressures victim through social conformity and viral forwarding mechanics.",
        "severity": "MEDIUM"
    },
    "Financial Pressure": {
        "regex": r'\b(?:unpaid invoice|auto-charged|overpayment|wire back|penalty fee|registration fee|customs duty)\b',
        "explanation": "Creates sudden unexpected monetary claims to trigger rash defensive payment.",
        "severity": "HIGH"
    },
    "Account Suspension Pressure": {
        "regex": r'\b(?:account.*blocked|account.*suspended|wallet.*freeze|card.*expire|service.*interruption|deactivation)\b',
        "explanation": "Threatens loss of access to essential digital or financial services unless instructions are obeyed.",
        "severity": "HIGH"
    },
    "Time Pressure": {
        "regex": r'\b(?:within \d+ hours?|within \d+ mins?|before midnight|in 24 hours?|expires today)\b',
        "explanation": "Sets an explicit ticking clock to prevent consultation with genuine authorities.",
        "severity": "HIGH"
    }
}

SENSITIVE_DATA_PATTERNS = [
    {
        "type": "OTP / One-Time Passcode",
        "regex": r'\b(?:otp|one-time passcode|6-digit code|sms code|verification code|bhejo otp)\b',
        "risk_weight": 35,
        "description": "Direct request for two-factor authentication or transaction authorization passcode."
    },
    {
        "type": "Password / Credentials",
        "regex": r'\b(?:password|netbanking password|passcode|login credentials|current password)\b',
        "risk_weight": 35,
        "description": "Request for master account login credentials enabling complete account takeover."
    },
    {
        "type": "Security PIN / MPIN",
        "regex": r'\b(?:upi pin|mpin|atm pin|secret pin|debit card pin)\b',
        "risk_weight": 35,
        "description": "Request for confidential banking PIN used to authorize direct financial debits."
    },
    {
        "type": "Card CVV & Expiry",
        "regex": r'\b(?:cvv|cvv2|card security code|3-digit code on back)\b',
        "risk_weight": 30,
        "description": "Card verification value required for card-not-present online transactions."
    },
    {
        "type": "National Identity (Aadhaar / PAN / SSN)",
        "regex": r'\b(?:aadhaar|pan card|ssn|social security|passport details)\b',
        "risk_weight": 25,
        "description": "Government identity records useful for identity theft and fraudulent SIM issuance."
    },
    {
        "type": "Remote Desktop Access",
        "regex": r'\b(?:anydesk|teamviewer|quicksupport|ultraviewer|screen share)\b',
        "risk_weight": 35,
        "description": "Software tool enabling the scammer to remotely control device and siphon credentials."
    }
]


def detect_manipulation(text: str) -> Dict[str, Any]:
    """
    Detects psychological manipulation techniques and sensitive information requests.
    Returns matched evidence quotes, explanations, and severity levels.
    """
    if not text:
        return {
            "techniques": [],
            "manipulation_score": 0,
            "sensitive_requests": []
        }

    text_lower = text.lower()
    detected_techniques = []

    for name, data in MANIPULATION_PATTERNS.items():
        matches = list(re.finditer(data["regex"], text_lower, re.IGNORECASE))
        if matches:
            evidence_quotes = list(set([text[m.start():m.end()] for m in matches]))
            detected_techniques.append({
                "technique": name,
                "evidence": evidence_quotes,
                "explanation": data["explanation"],
                "severity": data["severity"],
                "count": len(matches)
            })

    # Sensitive Information Requests
    detected_sensitive = []
    for sens in SENSITIVE_DATA_PATTERNS:
        matches = list(re.finditer(sens["regex"], text_lower, re.IGNORECASE))
        if matches:
            evidence_quotes = list(set([text[m.start():m.end()] for m in matches]))
            detected_sensitive.append({
                "request_type": sens["type"],
                "evidence": evidence_quotes,
                "description": sens["description"],
                "risk_weight": sens["risk_weight"]
            })

    # Manipulation score based on technique severities and counts
    score = 0
    for t in detected_techniques:
        if t["severity"] == "CRITICAL":
            score += 25
        elif t["severity"] == "HIGH":
            score += 15
        else:
            score += 8
    manipulation_score = min(100, score)

    return {
        "techniques": detected_techniques,
        "manipulation_score": manipulation_score,
        "sensitive_requests": detected_sensitive
    }

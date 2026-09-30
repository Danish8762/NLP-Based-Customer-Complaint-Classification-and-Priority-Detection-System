"""
VoiceShield AI - Transparent Risk Intelligence Engine
Calculates a 0-100 composite risk index based on empirical NLP dimensions:
1. Sensitive Information Request (Weight 25%)
2. Psychological Manipulation Techniques (Weight 20%)
3. Urgency & Time Pressure (Weight 15%)
4. Scam Classifier Probability (Weight 15%)
5. Semantic Similarity to Known Scams (Weight 15%)
6. Suspicious Structural URL / Threat Detection (Weight 10%)

Outputs Levels:
LOW (0-24), MEDIUM (25-49), HIGH (50-74), CRITICAL (75-100)
"""

from typing import Dict, Any, List


def calculate_risk_score(
    classification: Dict[str, Any],
    intent_data: Dict[str, Any],
    urgency_data: Dict[str, Any],
    manipulation_data: Dict[str, Any],
    urls: List[Dict[str, Any]],
    similar_messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Computes transparent composite risk score with breakdown of contributory weights.
    """
    # Factor 1: Sensitive Information Request (Max 25 pts)
    sensitive_reqs = manipulation_data.get("sensitive_requests", [])
    if len(sensitive_reqs) >= 2:
        f1_score = 25.0
    elif len(sensitive_reqs) == 1:
        f1_score = 22.0
    else:
        f1_score = 0.0

    # Factor 2: Psychological Manipulation Techniques (Max 20 pts)
    techs = manipulation_data.get("techniques", [])
    crit_techs = [t for t in techs if t.get("severity") == "CRITICAL"]
    high_techs = [t for t in techs if t.get("severity") == "HIGH"]
    f2_score = min(20.0, (len(crit_techs) * 10.0) + (len(high_techs) * 6.0) + (len(techs) * 3.0))

    # Factor 3: Urgency & Time Pressure (Max 15 pts)
    urg_raw = urgency_data.get("score", 0)  # 0 to 100
    f3_score = min(15.0, (urg_raw / 100.0) * 15.0)

    # Factor 4: Scam Classifier Probability (Max 15 pts)
    is_scam = classification.get("is_scam", False)
    conf = classification.get("confidence", 0.0)
    if is_scam:
        f4_score = min(15.0, conf * 15.0)
    else:
        f4_score = max(0.0, (1.0 - conf) * 5.0)

    # Factor 5: Semantic Similarity to Known Scams (Max 15 pts)
    if similar_messages and len(similar_messages) > 0:
        top_sim = similar_messages[0]
        sim_pct = top_sim.get("similarity_percentage", 0.0)
        # If top similarity is to a scam category
        if top_sim.get("category") != "Legitimate / Safe":
            f5_score = min(15.0, (sim_pct / 100.0) * 15.0)
        else:
            f5_score = 0.0
    else:
        f5_score = 0.0

    # Factor 6: Suspicious Structural URL / Threat Cues (Max 10 pts)
    suspicious_urls = [u for u in urls if u.get("is_suspicious")]
    has_threat = intent_data.get("intent") in ["Threat", "Account Suspension"]
    f6_score = 0.0
    if suspicious_urls:
        f6_score += 6.0
    if has_threat:
        f6_score += 4.0
    f6_score = min(10.0, f6_score)

    total_risk = round(f1_score + f2_score + f3_score + f4_score + f5_score + f6_score, 1)
    
    # If classified as Legitimate and no critical factors detected, cap risk
    if not is_scam and f1_score == 0 and len(crit_techs) == 0:
        total_risk = min(24.0, total_risk)

    total_risk = max(0.0, min(100.0, total_risk))

    if total_risk >= 75.0:
        risk_level = "CRITICAL"
        risk_color = "red"
        badge_variant = "destructive"
    elif total_risk >= 50.0:
        risk_level = "HIGH"
        risk_color = "orange"
        badge_variant = "warning"
    elif total_risk >= 25.0:
        risk_level = "MEDIUM"
        risk_color = "yellow"
        badge_variant = "secondary"
    else:
        risk_level = "LOW"
        risk_color = "green"
        badge_variant = "success"

    factors_breakdown = [
        {
            "name": "Sensitive Information Request",
            "weight": 25,
            "score": round(f1_score, 1),
            "description": f"{len(sensitive_reqs)} sensitive fields requested (e.g. OTP, PIN, Passwords)"
        },
        {
            "name": "Psychological Manipulation Cues",
            "weight": 20,
            "score": round(f2_score, 1),
            "description": f"{len(techs)} social engineering techniques identified"
        },
        {
            "name": "Urgency & Time Pressure",
            "weight": 15,
            "score": round(f3_score, 1),
            "description": f"Level: {urgency_data.get('level', 'LOW')} ({urg_raw}/100)"
        },
        {
            "name": "Scam Model Probability",
            "weight": 15,
            "score": round(f4_score, 1),
            "description": f"{classification.get('active_model', 'Classifier')} predicted {classification.get('predicted_category')} ({classification.get('confidence_percentage', 0)}%)"
        },
        {
            "name": "Semantic Vector Similarity",
            "weight": 15,
            "score": round(f5_score, 1),
            "description": f"Nearest scam cluster match at {round(f5_score/15*100, 1)}% affinity"
        },
        {
            "name": "Suspicious URL / Coercive Threat",
            "weight": 10,
            "score": round(f6_score, 1),
            "description": f"{len(suspicious_urls)} high-risk link(s) or explicit threats present"
        }
    ]

    return {
        "score": total_risk,
        "level": risk_level,
        "color": risk_color,
        "badge_variant": badge_variant,
        "factors": factors_breakdown,
        "methodology": "Transparent multi-factorial weighted NLP aggregation. Not a guarantee; provides risk intelligence."
    }

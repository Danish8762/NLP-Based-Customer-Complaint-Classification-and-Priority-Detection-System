"""
VoiceShield AI - Explainable NLP Module
Generates transparent linguistic explanations, token-level feature importance,
matched empirical evidence cards, and actionable recommendations.
"""

from typing import Dict, Any, List


def generate_nlp_explanation(
    text: str,
    classification: Dict[str, Any],
    intent_data: Dict[str, Any],
    urgency_data: Dict[str, Any],
    manipulation_data: Dict[str, Any],
    entities: List[Dict[str, Any]],
    urls: List[Dict[str, Any]],
    similar_messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Synthesizes multi-module NLP findings into transparent, explainable evidence cards,
    feature importance rankings, and user next steps.
    """
    evidence_cards = []
    category = classification.get("predicted_category", "Unknown")
    is_scam = classification.get("is_scam", False)

    # 1. Sensitive Data Requests Evidence
    for sens in manipulation_data.get("sensitive_requests", []):
        req_type = sens.get("request_type", sens.get("type", "Sensitive Information"))
        evidence_cards.append({
            "title": f"Sensitive Request Detected: {req_type}",
            "evidence": ", ".join(f'"{q}"' for q in sens.get("evidence", [])),
            "description": sens.get("description", ""),
            "severity": "CRITICAL",
            "tag": "Credential Risk"
        })

    # 2. Urgency Cues Evidence
    if urgency_data.get("score", 0) >= 20:
        cues_text = ", ".join(f'"{c["cue"]}"' for c in urgency_data.get("cues", [])[:3])
        evidence_cards.append({
            "title": f"Psychological Urgency ({urgency_data.get('level', 'MEDIUM')})",
            "evidence": cues_text or "Time-constrained vocabulary",
            "description": "The message attempts to create immediate time pressure to discourage deliberate verification.",
            "severity": urgency_data.get("level", "HIGH"),
            "tag": "Time Pressure"
        })

    # 3. Manipulation Techniques Evidence
    for tech in manipulation_data.get("techniques", []):
        if tech["technique"] != "Urgency":  # already highlighted above
            quotes = ", ".join(f'"{q}"' for q in tech.get("evidence", [])[:2])
            evidence_cards.append({
                "title": f"Social Engineering: {tech['technique']}",
                "evidence": quotes,
                "description": tech.get("explanation", ""),
                "severity": tech.get("severity", "HIGH"),
                "tag": "Manipulation Cue"
            })

    # 4. Intent Evidence
    intent = intent_data.get("intent", "Unknown")
    if intent not in ["Unknown", "Legitimate Inquiry"]:
        evidence_cards.append({
            "title": f"Action Intent: {intent}",
            "evidence": f"Confidence: {int(intent_data.get('confidence', 0.8) * 100)}%",
            "description": f"The linguistic structure is oriented around attempting to perform '{intent}'.",
            "severity": "HIGH",
            "tag": "Intent Alignment"
        })

    # 5. Suspicious URL Evidence
    for u in urls:
        if u.get("is_suspicious"):
            reasons = "; ".join(u.get("reasons", []))
            evidence_cards.append({
                "title": "Suspicious URL Structure",
                "evidence": u["url"],
                "description": f"Domain heuristics flagged: {reasons}.",
                "severity": "CRITICAL" if u.get("suspicious_score", 0) > 50 else "HIGH",
                "tag": "Phishing Link"
            })

    # 6. High Semantic Similarity to Known Scams
    if similar_messages and len(similar_messages) > 0:
        top_sim = similar_messages[0]
        if top_sim.get("similarity_percentage", 0) >= 70:
            evidence_cards.append({
                "title": f"Matches Known Scam Pattern ({top_sim.get('category')})",
                "evidence": f"{top_sim.get('similarity_percentage')}% Semantic Cosine Similarity",
                "description": f"Semantically identical to historical incident #{top_sim.get('id')}: '{top_sim.get('text')[:75]}...'",
                "severity": "HIGH",
                "tag": "Vector Match"
            })

    # Feature Importance (Tokens with highest signal)
    feature_importance = []
    from backend.app.nlp.scam_classifier import _VECTORIZER, _SVM_MODEL, _CLASSES
    try:
        if _VECTORIZER is not None and _SVM_MODEL is not None and _CLASSES is not None:
            feature_names = _VECTORIZER.get_feature_names_out()
            X_vec = _VECTORIZER.transform([text]).toarray()[0]
            non_zero_indices = X_vec.nonzero()[0]
            
            # Find index of predicted class
            if category in _CLASSES:
                class_idx = _CLASSES.index(category)
                # CalibratedClassifierCV wraps estimators_
                coefs = None
                if hasattr(_SVM_MODEL, "calibrated_classifiers_"):
                    base_est = _SVM_MODEL.calibrated_classifiers_[0].estimator
                    if hasattr(base_est, "coef_"):
                        coefs = base_est.coef_
                elif hasattr(_SVM_MODEL, "coef_"):
                    coefs = _SVM_MODEL.coef_
                    
                if coefs is not None and class_idx < len(coefs):
                    weights = coefs[class_idx]
                    token_weights = []
                    for idx in non_zero_indices:
                        word = feature_names[idx]
                        score = float(X_vec[idx] * weights[idx])
                        token_weights.append((word, score))
                    
                    token_weights.sort(key=lambda x: abs(x[1]), reverse=True)
                    for word, score in token_weights[:8]:
                        feature_importance.append({
                            "feature": word,
                            "contribution": round(score, 3),
                            "direction": "scam" if score > 0 else "neutral"
                        })
    except Exception:
        pass

    # Fallback to keyphrase importance if model weights not directly inspectable
    if not feature_importance:
        from backend.app.nlp.keywords import extract_keywords
        kw_res = extract_keywords(text, top_k=6)
        for kw in kw_res.get("top_keywords", []):
            feature_importance.append({
                "feature": kw["keyword"],
                "contribution": round(kw["score"] / 10.0, 3),
                "direction": "scam" if is_scam else "neutral"
            })

    # Actionable Recommendations
    recommendations = []
    if is_scam:
        recommendations.append("NEVER share any one-time passcode (OTP), UPI PIN, or netbanking passwords.")
        if any(u.get("is_suspicious") for u in urls):
            recommendations.append("Do NOT click or open the link provided in the message. Verify domain on official company portals.")
        if "Banking Scam" in category or "Payment Scam" in category or "OTP Scam" in category:
            recommendations.append("Contact your bank immediately via the official phone number printed on the back of your debit/credit card.")
            recommendations.append("If you entered credentials, freeze your card and change passwords immediately from an official banking app.")
        if any("Remote Desktop" in s.get("request_type", "") for s in manipulation_data.get("sensitive_requests", [])):
            recommendations.append("Do NOT install AnyDesk, TeamViewer, or screen-sharing applications. Disconnect device Wi-Fi immediately if already installed.")
        recommendations.append("Report this sender to national cyber crime portals (e.g. cybercrime.gov.in or reportphishing@apwg.org).")
    else:
        recommendations.append("This message appears legitimate and matches standard communications.")
        recommendations.append("Maintain good digital hygiene: always double-check sender email or phone numbers before sharing private data.")

    return {
        "evidence_cards": evidence_cards,
        "feature_importance": feature_importance,
        "recommendations": recommendations,
        "summary": (
            f"VoiceShield AI classified this message as '{category}' with {classification.get('confidence_percentage', 0)}% confidence. "
            f"Linguistic analysis identified {len(evidence_cards)} distinct indicators including "
            f"{', '.join(t['technique'] for t in manipulation_data.get('techniques', [])[:2]) or 'standard patterns'}."
        )
    }

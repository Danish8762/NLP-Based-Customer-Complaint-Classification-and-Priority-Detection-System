"""
VoiceShield AI - Contextual Multi-Turn Conversation Analysis Module
Parses dialogue turns, extracts speaker roles, tracks intent transitions,
monitors manipulation escalation trajectories, builds entity relationships,
and assesses conversation-level social engineering risk.
"""

import re
from typing import List, Dict, Any, Tuple
from backend.app.nlp.intent import detect_intent
from backend.app.nlp.urgency import detect_urgency
from backend.app.nlp.manipulation import detect_manipulation
from backend.app.nlp.sentiment import analyze_sentiment
from backend.app.nlp.ner import extract_entities


def parse_conversation_turns(raw_text: str) -> List[Dict[str, Any]]:
    """
    Parses dialogue script with formats like:
    'Person A: ...', 'Caller: ...', 'Speaker 1: ...', 'Scammer: ...', 'Victim: ...', 'User: ...'
    or line-by-line fallback.
    """
    lines = raw_text.strip().split("\n")
    turns = []
    current_speaker = "Speaker 1"
    current_text = []

    speaker_pattern = re.compile(r'^([A-Za-z0-9_\s\-\.]+?)\s*:\s*(.*)$')

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        match = speaker_pattern.match(line_clean)
        if match:
            # If we had a previous speaker block, save it
            if current_text:
                turns.append({
                    "speaker": current_speaker,
                    "text": " ".join(current_text).strip()
                })
                current_text = []
            current_speaker = match.group(1).strip()
            text_content = match.group(2).strip()
            if text_content:
                current_text.append(text_content)
        else:
            current_text.append(line_clean)

    if current_text:
        turns.append({
            "speaker": current_speaker,
            "text": " ".join(current_text).strip()
        })

    # If format was just raw sentences without labels, split by sentence or alternate
    if len(turns) <= 1 and len(lines) > 1:
        turns = []
        for i, l in enumerate(lines):
            l_clean = l.strip()
            if l_clean:
                turns.append({
                    "speaker": f"Speaker {(i % 2) + 1}",
                    "text": l_clean
                })

    return turns


def map_stage_lifecycle(intent: str, techniques: List[str], turn_idx: int) -> str:
    """Classifies the dialogue turn into the canonical cyber scam lifecycle stage."""
    tech_names = [t.lower() for t in techniques]
    intent_lower = intent.lower()

    if "otp" in intent_lower or "credential" in intent_lower or "password" in intent_lower:
        return "Credential Request (Critical)"
    elif "payment" in intent_lower or "financial" in intent_lower:
        return "Financial Extraction"
    elif "urgency" in tech_names or "time pressure" in tech_names:
        return "Urgency Acceleration"
    elif "fear" in tech_names or "threat" in tech_names or "account suspension" in intent_lower:
        return "Problem & Fear Creation"
    elif "authority impersonation" in tech_names or "support" in intent_lower:
        return "Authority Claim / Pretext"
    elif turn_idx == 0:
        return "Pretext / Initial Contact"
    else:
        return "Information Solicitation"


def analyze_conversation(raw_text: str) -> Dict[str, Any]:
    """
    Performs comprehensive contextual dialogue analysis:
    - Turn-by-turn NLP feature extraction
    - Escalation trajectory
    - Intent transition graph
    - Entity relationship network
    - Overall conversation threat score
    """
    turns = parse_conversation_turns(raw_text)
    if not turns:
        return {
            "turn_count": 0,
            "turns": [],
            "escalation_timeline": [],
            "intent_transitions": [],
            "entity_graph": {"nodes": [], "edges": []},
            "conversation_risk": {"score": 0, "level": "LOW", "summary": "No turns detected."}
        }

    turn_analyses = []
    cumulative_risk = 0.0
    intent_sequence = []
    all_entities = []
    max_urgency = 0
    total_manipulations = 0
    speaker_risk_tally: Dict[str, float] = {}

    context_window = []

    for idx, t in enumerate(turns):
        speaker = t["speaker"]
        text = t["text"]

        # Run NLP modules on this turn
        intent_res = detect_intent(text)
        urg_res = detect_urgency(text)
        manip_res = detect_manipulation(text)
        sent_res = analyze_sentiment(text)
        ent_res = extract_entities(text)

        all_entities.extend(ent_res)
        intent = intent_res.get("intent", "Unknown")
        intent_sequence.append(intent)

        # Urgency & manipulation tracking
        if urg_res["score"] > max_urgency:
            max_urgency = urg_res["score"]
        total_manipulations += len(manip_res["techniques"])

        tech_names = [item["technique"] for item in manip_res["techniques"]]
        stage = map_stage_lifecycle(intent, tech_names, idx)

        # Compute turn-level risk (0-100)
        t_risk = 0.0
        if manip_res.get("sensitive_requests"):
            t_risk += 40.0
        if tech_names:
            t_risk += len(tech_names) * 15.0
        if urg_res["score"] >= 40:
            t_risk += 20.0
        if intent in ["Request OTP", "Request Password", "Threat", "Credential Harvesting"]:
            t_risk += 30.0

        t_risk = min(100.0, t_risk)
        speaker_risk_tally[speaker] = speaker_risk_tally.get(speaker, 0.0) + t_risk

        turn_analyses.append({
            "turn_index": idx + 1,
            "speaker": speaker,
            "text": text,
            "intent": intent,
            "stage": stage,
            "urgency_level": urg_res["level"],
            "urgency_score": urg_res["score"],
            "sentiment": sent_res["label"],
            "manipulation_techniques": tech_names,
            "sensitive_requests": [s.get("request_type", s.get("type", "")) for s in manip_res.get("sensitive_requests", [])],
            "turn_risk_score": round(t_risk, 1),
            "turn_risk_level": "CRITICAL" if t_risk >= 70 else ("HIGH" if t_risk >= 45 else ("MEDIUM" if t_risk >= 20 else "LOW"))
        })

    # Timeline of escalation
    timeline = []
    for ta in turn_analyses:
        timeline.append({
            "step": f"Turn {ta['turn_index']}",
            "speaker": ta["speaker"],
            "stage": ta["stage"],
            "intent": ta["intent"],
            "risk_score": ta["turn_risk_score"],
            "risk_level": ta["turn_risk_level"],
            "cue": ta["manipulation_techniques"][0] if ta["manipulation_techniques"] else "Standard"
        })

    # Intent transitions (flow from intent A -> intent B)
    intent_transitions = []
    for i in range(len(intent_sequence) - 1):
        from_intent = intent_sequence[i]
        to_intent = intent_sequence[i + 1]
        intent_transitions.append({
            "from": from_intent,
            "to": to_intent,
            "step": f"Turn {i+1} → Turn {i+2}"
        })

    # Entity Relationship Graph (Nodes & Edges)
    graph_nodes = []
    graph_edges = []
    seen_nodes = set()

    # Identify primary actors
    suspicious_speaker = max(speaker_risk_tally.items(), key=lambda x: x[1])[0] if speaker_risk_tally else "Speaker 1"
    victim_speaker = [s for s in speaker_risk_tally if s != suspicious_speaker]
    victim_speaker = victim_speaker[0] if victim_speaker else "Victim"

    graph_nodes.append({"id": suspicious_speaker, "label": f"{suspicious_speaker} (Suspect)", "type": "actor_suspect"})
    graph_nodes.append({"id": victim_speaker, "label": f"{victim_speaker} (Target)", "type": "actor_target"})
    seen_nodes.add(suspicious_speaker)
    seen_nodes.add(victim_speaker)

    for ent in all_entities[:12]:
        ent_id = f"ent_{ent['text'].lower()}"
        if ent_id not in seen_nodes:
            seen_nodes.add(ent_id)
            graph_nodes.append({
                "id": ent_id,
                "label": f"{ent['text']} ({ent['label']})",
                "type": ent["label"].lower()
            })
            # Connect suspicious speaker to extracted entities
            graph_edges.append({
                "source": suspicious_speaker,
                "target": ent_id,
                "relation": "targets / claims" if ent["label"] in ["BANK", "ACCOUNT"] else "solicits"
            })

    # Also connect suspicious speaker to victim
    graph_edges.append({
        "source": suspicious_speaker,
        "target": victim_speaker,
        "relation": "pressures with urgency" if max_urgency > 40 else "interacts with"
    })

    # Overall conversation risk
    max_turn_risk = max(t["turn_risk_score"] for t in turn_analyses) if turn_analyses else 0
    avg_turn_risk = sum(t["turn_risk_score"] for t in turn_analyses) / len(turn_analyses) if turn_analyses else 0
    conv_score = round(min(100.0, (max_turn_risk * 0.7) + (avg_turn_risk * 0.3)), 1)

    if conv_score >= 70:
        conv_level = "CRITICAL"
        conv_desc = "High-confidence social engineering attack detected with severe escalation toward credential harvesting."
    elif conv_score >= 45:
        conv_level = "HIGH"
        conv_desc = "Suspicious conversational escalation with coercion, urgency, or identity claims."
    elif conv_score >= 20:
        conv_level = "MEDIUM"
        conv_desc = "Moderate pressure tactics detected. Further caution recommended."
    else:
        conv_level = "LOW"
        conv_desc = "Natural dialogue progression with no significant social engineering triggers."

    return {
        "turn_count": len(turn_analyses),
        "turns": turn_analyses,
        "primary_suspect": suspicious_speaker,
        "escalation_timeline": timeline,
        "intent_transitions": intent_transitions,
        "entity_graph": {
            "nodes": graph_nodes,
            "edges": graph_edges
        },
        "conversation_risk": {
            "score": conv_score,
            "level": conv_level,
            "max_turn_risk": max_turn_risk,
            "summary": conv_desc
        }
    }

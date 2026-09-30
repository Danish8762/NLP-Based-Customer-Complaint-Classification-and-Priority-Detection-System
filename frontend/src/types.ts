export interface TokenInfo {
  token: string;
  lemma: string;
  pos: string;
  is_stop: boolean;
  is_important: boolean;
}

export interface EntityInfo {
  text: string;
  label: string;
  category: string;
  start: number;
  end: number;
  description: string;
}

export interface UrlInfo {
  url: string;
  is_suspicious: boolean;
  suspicious_score: number;
  reasons: string[];
}

export interface ManipulationTechnique {
  technique: string;
  evidence: string[];
  explanation: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  count: number;
}

export interface SensitiveRequest {
  request_type: string;
  evidence: string[];
  description: string;
  risk_weight: number;
}

export interface EvidenceCard {
  title: string;
  evidence: string;
  description: string;
  severity: string;
  tag: string;
}

export interface AnalysisResult {
  id?: number;
  created_at?: string;
  input_text: string;
  processing_time_ms: number;
  language: {
    language_code: string;
    language_name: string;
    confidence: number;
    script: string;
    is_code_mixed: boolean;
  };
  statistics: {
    character_count: number;
    word_count: number;
    sentence_count: number;
    avg_sentence_length: number;
    unique_words: number;
    lexical_diversity: number;
    capitalized_word_count: number;
    capitalized_ratio: number;
    exclamation_count: number;
    question_count: number;
    pos_distribution: Record<string, number>;
  };
  sentences: string[];
  tokens: TokenInfo[];
  urls: UrlInfo[];
  entities: EntityInfo[];
  keywords: Array<{ keyword: string; score: number }>;
  keywords_comparison: {
    frequency: Array<{ keyword: string; score: number; method: string }>;
    statistical: Array<{ keyword: string; score: number; method: string }>;
    high_risk_lexical: Array<{ keyword: string; score: number; method: string }>;
  };
  keyphrases: Array<{ phrase: string; relevance_score: number; frequency: number; length: number }>;
  intent: {
    intent: string;
    confidence: number;
    alternatives: Array<{ intent: string; confidence: number }>;
    scoring_factors?: Record<string, number>;
  };
  sentiment: {
    label: "Positive" | "Negative" | "Neutral";
    compound: number;
    positive: number;
    neutral: number;
    negative: number;
    subjectivity: number;
    significant_words: Array<{ word: string; valence: number; type: string }>;
    sentence_sentiment: Array<{ sentence: string; label: string; compound: number }>;
  };
  emotion: {
    dominant_emotion: string;
    confidence: number;
    distribution: Record<string, number>;
    sentence_emotions: Array<{ sentence: string; dominant_emotion: string; scores: Record<string, number> }>;
  };
  urgency: {
    level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    score: number;
    cues: Array<{ cue: string; reason: string; weight: number; start: number; end: number }>;
    heatmap: Array<{ sentence: string; score: number; intensity: number; cues: string[]; level: string }>;
  };
  manipulation: {
    techniques: ManipulationTechnique[];
    manipulation_score: number;
    sensitive_requests: SensitiveRequest[];
  };
  classification: {
    predicted_category: string;
    confidence: number;
    confidence_percentage: number;
    is_scam: boolean;
    active_model: string;
    top_candidates: Array<{ category: string; probability: number; percentage: number }>;
    model_comparison: Record<string, { prediction: string; confidence: number; is_scam: boolean }>;
  };
  similar_messages: Array<{
    id: number;
    text: string;
    category: string;
    intent: string;
    urgency: string;
    similarity_score: number;
    similarity_percentage: number;
    explanation: string;
  }>;
  risk: {
    score: number;
    level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
    color: string;
    badge_variant: string;
    factors: Array<{ name: string; weight: number; score: number; description: string }>;
    methodology: string;
  };
  explanation: {
    evidence_cards: EvidenceCard[];
    feature_importance: Array<{ feature: string; contribution: number; direction: string }>;
    recommendations: string[];
    summary: string;
  };
}

export interface ConversationTurn {
  turn_index: number;
  speaker: string;
  text: string;
  intent: string;
  stage: string;
  urgency_level: string;
  urgency_score: number;
  sentiment: string;
  manipulation_techniques: string[];
  sensitive_requests: string[];
  turn_risk_score: number;
  turn_risk_level: string;
}

export interface ConversationResult {
  id?: number;
  created_at?: string;
  turn_count: number;
  turns: ConversationTurn[];
  primary_suspect: string;
  escalation_timeline: Array<{
    step: string;
    speaker: string;
    stage: string;
    intent: string;
    risk_score: number;
    risk_level: string;
    cue: string;
  }>;
  intent_transitions: Array<{
    from: string;
    to: string;
    step: string;
  }>;
  entity_graph: {
    nodes: Array<{ id: string; label: string; type: string }>;
    edges: Array<{ source: string; target: string; relation: string }>;
  };
  conversation_risk: {
    score: number;
    level: string;
    max_turn_risk: number;
    summary: string;
  };
}

export interface KnowledgeArticle {
  id: number;
  scam_type: string;
  title: string;
  description: string;
  linguistic_patterns: string[];
  typical_intent: string;
  warning_signs: string[];
  example_messages: string[];
  recommended_action: string;
}

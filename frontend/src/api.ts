import { AnalysisResult, ConversationResult, KnowledgeArticle } from './types';

const API_BASE = '/api';

export async function analyzeMessage(text: string, preferredModel = 'Linear SVM'): Promise<AnalysisResult> {
  const resp = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, preferred_model: preferredModel })
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'Analysis failed');
  }
  return resp.json();
}

export async function analyzeConversation(raw_text: string): Promise<ConversationResult> {
  const resp = await fetch(`${API_BASE}/analyze/conversation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text })
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Conversation analysis failed' }));
    throw new Error(err.detail || 'Conversation analysis failed');
  }
  return resp.json();
}

export async function searchSimilarity(text: string, top_k = 5, category_filter?: string) {
  const resp = await fetch(`${API_BASE}/similarity/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, top_k, category_filter })
  });
  if (!resp.ok) throw new Error('Similarity search failed');
  return resp.json();
}

export async function fetchAnalytics() {
  const resp = await fetch(`${API_BASE}/analytics`);
  if (!resp.ok) throw new Error('Failed to load analytics');
  return resp.json();
}

export async function fetchNlpMetrics() {
  const resp = await fetch(`${API_BASE}/analytics/nlp`);
  if (!resp.ok) throw new Error('Failed to load NLP metrics');
  return resp.json();
}

export async function fetchThreatPatterns() {
  const resp = await fetch(`${API_BASE}/threat-patterns`);
  if (!resp.ok) throw new Error('Failed to load threat patterns');
  return resp.json();
}

export async function fetchKnowledgeArticles(search?: string, category?: string): Promise<KnowledgeArticle[]> {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (category && category !== 'all') params.append('category', category);
  const resp = await fetch(`${API_BASE}/knowledge?${params.toString()}`);
  if (!resp.ok) throw new Error('Failed to load knowledge articles');
  return resp.json();
}

export async function fetchHistory(limit = 50, offset = 0, search?: string, category?: string, risk_level?: string) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (search) params.append('search', search);
  if (category && category !== 'all') params.append('category', category);
  if (risk_level && risk_level !== 'all') params.append('risk_level', risk_level);
  const resp = await fetch(`${API_BASE}/history?${params.toString()}`);
  if (!resp.ok) throw new Error('Failed to load history');
  return resp.json();
}

export async function fetchModelsInfo() {
  const resp = await fetch(`${API_BASE}/models`);
  if (!resp.ok) throw new Error('Failed to load models info');
  return resp.json();
}

export async function fetchEvaluationMetrics() {
  const resp = await fetch(`${API_BASE}/models/evaluation`);
  if (!resp.ok) throw new Error('Failed to load evaluation metrics');
  return resp.json();
}

export async function uploadBatchCsv(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch(`${API_BASE}/analyze/batch`, {
    method: 'POST',
    body: formData
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Batch upload failed' }));
    throw new Error(err.detail || 'Batch upload failed');
  }
  return resp.json();
}

export async function uploadAudio(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch(`${API_BASE}/analyze/audio`, {
    method: 'POST',
    body: formData
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Audio analysis failed' }));
    throw new Error(err.detail || 'Audio analysis failed');
  }
  return resp.json();
}

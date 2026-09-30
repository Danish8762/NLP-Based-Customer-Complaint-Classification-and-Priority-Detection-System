import React, { useState } from 'react';
import { AnalysisResult } from '../types';
import {
  Globe,
  FileCode,
  Tag,
  Hash,
  Compass,
  Smile,
  Zap,
  Shield,
  Network,
  HelpCircle,
  CheckCircle2,
  ChevronRight
} from 'lucide-react';

interface PipelineVisualizerProps {
  analysis: AnalysisResult;
}

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({ analysis }) => {
  const [selectedStep, setSelectedStep] = useState<string>('risk');

  const steps = [
    {
      id: 'input',
      name: '1. Input',
      icon: FileCode,
      summary: `${analysis.statistics.character_count} chars, ${analysis.statistics.word_count} words`,
      render: () => (
        <div className="space-y-2">
          <div className="text-xs font-semibold text-slate-400">Raw Input Text:</div>
          <div className="p-3 rounded-lg bg-slate-950 font-mono text-xs text-slate-200 border border-slate-800">
            {analysis.input_text}
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2">
            <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50 text-center">
              <div className="text-[10px] text-slate-400">Characters</div>
              <div className="text-sm font-bold text-white font-mono">{analysis.statistics.character_count}</div>
            </div>
            <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50 text-center">
              <div className="text-[10px] text-slate-400">Words</div>
              <div className="text-sm font-bold text-white font-mono">{analysis.statistics.word_count}</div>
            </div>
            <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50 text-center">
              <div className="text-[10px] text-slate-400">Sentences</div>
              <div className="text-sm font-bold text-white font-mono">{analysis.statistics.sentence_count}</div>
            </div>
            <div className="p-2 rounded bg-slate-800/40 border border-slate-700/50 text-center">
              <div className="text-[10px] text-slate-400">Avg Sent Length</div>
              <div className="text-sm font-bold text-white font-mono">{analysis.statistics.avg_sentence_length}w</div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'language',
      name: '2. Language Detection',
      icon: Globe,
      summary: `${analysis.language.language_name} (${intPct(analysis.language.confidence)}%)`,
      render: () => (
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div>
              <div className="text-xs text-slate-400">Detected Language</div>
              <div className="text-sm font-bold text-blue-400">{analysis.language.language_name}</div>
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-400">Confidence</div>
              <div className="text-sm font-bold font-mono text-emerald-400">{intPct(analysis.language.confidence)}%</div>
            </div>
          </div>
          <div className="text-xs text-slate-400">
            Script: <span className="font-mono text-white">{analysis.language.script}</span> | Code-mixed:{' '}
            <span className="font-mono text-white">{analysis.language.is_code_mixed ? 'Yes (Hinglish)' : 'No'}</span>
          </div>
        </div>
      )
    },
    {
      id: 'tokenization',
      name: '3. Tokenization & POS',
      icon: Tag,
      summary: `${analysis.tokens.length} tokens extracted`,
      render: () => (
        <div className="space-y-2">
          <div className="text-xs text-slate-400">Token Sequence with Part-of-Speech & Lemmatization:</div>
          <div className="max-h-48 overflow-y-auto space-y-1 pr-1">
            <div className="grid grid-cols-4 gap-1 text-[10px] font-semibold text-slate-500 uppercase px-2 py-1 border-b border-slate-800">
              <div>Token</div>
              <div>Lemma</div>
              <div>POS</div>
              <div className="text-right">Informative</div>
            </div>
            {analysis.tokens.map((t, idx) => (
              <div
                key={idx}
                className="grid grid-cols-4 gap-1 text-xs px-2 py-1 rounded bg-slate-950/60 font-mono border border-slate-800/40"
              >
                <div className="text-white truncate">{t.token}</div>
                <div className="text-slate-400 truncate">{t.lemma}</div>
                <div className="text-cyan-400">{t.pos}</div>
                <div className="text-right">
                  {t.is_important ? (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">YES</span>
                  ) : (
                    <span className="text-[10px] text-slate-600">-</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 'ner',
      name: '4. Named Entities (NER)',
      icon: Hash,
      summary: `${analysis.entities.length} entities discovered`,
      render: () => (
        <div className="space-y-2">
          <div className="text-xs text-slate-400">Cybersecurity & Linguistic Entity Extraction:</div>
          {analysis.entities.length === 0 ? (
            <div className="p-3 text-xs text-slate-500 italic">No specific named entities detected.</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-48 overflow-y-auto">
              {analysis.entities.map((ent, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-start justify-between">
                  <div>
                    <div className="text-xs font-bold text-white">{ent.text}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{ent.description}</div>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    {ent.label}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )
    },
    {
      id: 'intent',
      name: '5. Intent Detection',
      icon: Compass,
      summary: `${analysis.intent.intent} (${intPct(analysis.intent.confidence)}%)`,
      render: () => (
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-blue-950/30 border border-blue-800/50 flex items-center justify-between">
            <div>
              <div className="text-[10px] text-blue-400 font-semibold uppercase">Primary Action Intent</div>
              <div className="text-sm font-bold text-white mt-0.5">{analysis.intent.intent}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-blue-400 font-semibold uppercase">Confidence</div>
              <div className="text-base font-bold font-mono text-emerald-400">{intPct(analysis.intent.confidence)}%</div>
            </div>
          </div>
          {analysis.intent.alternatives.length > 0 && (
            <div className="space-y-1">
              <div className="text-[11px] text-slate-400 font-medium">Alternative Candidate Intents:</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {analysis.intent.alternatives.map((alt, i) => (
                  <div key={i} className="px-2.5 py-1.5 rounded bg-slate-900 border border-slate-800 flex justify-between text-xs">
                    <span className="text-slate-300">{alt.intent}</span>
                    <span className="font-mono text-slate-500">{intPct(alt.confidence)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )
    },
    {
      id: 'psychology',
      name: '6. Urgency & Emotion',
      icon: Smile,
      summary: `Urgency: ${analysis.urgency.level} | Emotion: ${analysis.emotion.dominant_emotion}`,
      render: () => (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Urgency Level</div>
              <div className="text-sm font-bold text-amber-400 mt-0.5">{analysis.urgency.level} ({analysis.urgency.score}/100)</div>
              <div className="text-[10px] text-slate-500 mt-1">
                {analysis.urgency.cues.length} explicit time pressure cues detected
              </div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Dominant Emotion</div>
              <div className="text-sm font-bold text-cyan-400 mt-0.5 capitalize">{analysis.emotion.dominant_emotion}</div>
              <div className="text-[10px] text-slate-500 mt-1">
                Valence: <span className="font-mono text-slate-400">{analysis.sentiment.compound}</span>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'classification',
      name: '7. Classification & Model Comparison',
      icon: Zap,
      summary: `${analysis.classification.predicted_category} (${analysis.classification.confidence_percentage}%)`,
      render: () => (
        <div className="space-y-3">
          <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Active Model: {analysis.classification.active_model}</div>
              <div className="text-sm font-bold text-rose-400 mt-0.5">{analysis.classification.predicted_category}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Model Confidence</div>
              <div className="text-sm font-bold font-mono text-white">{analysis.classification.confidence_percentage}%</div>
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-[11px] text-slate-400 font-medium">Multi-Model Comparison on This Input:</div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-1.5">
              {Object.entries(analysis.classification.model_comparison || {}).map(([mName, mData]) => (
                <div key={mName} className="p-2 rounded bg-slate-950 border border-slate-800 text-xs">
                  <div className="font-semibold text-slate-300 truncate">{mName}</div>
                  <div className="text-rose-400 font-medium truncate mt-0.5">{mData.prediction}</div>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">{intPct(mData.confidence)}% conf</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'similarity',
      name: '8. Semantic Vector Similarity',
      icon: Network,
      summary: `${analysis.similar_messages.length} similar scam records retrieved`,
      render: () => (
        <div className="space-y-2">
          <div className="text-xs text-slate-400">Nearest Cosine Vector Matches (all-MiniLM-L6-v2):</div>
          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {analysis.similar_messages.map((sim) => (
              <div key={sim.id} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="text-xs text-slate-200 line-clamp-2">"{sim.text}"</div>
                  <div className="text-[10px] text-slate-500 mt-1">{sim.explanation}</div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-xs font-bold font-mono text-blue-400">{sim.similarity_percentage}%</div>
                  <div className="text-[9px] text-slate-400 font-mono">{sim.category}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 'risk',
      name: '9. Risk Intelligence Engine',
      icon: Shield,
      summary: `Score: ${analysis.risk.score}/100 (${analysis.risk.level})`,
      render: () => (
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div>
              <div className="text-xs text-slate-400">Composite Risk Score</div>
              <div className="text-xl font-bold font-mono text-red-400">{analysis.risk.score} / 100</div>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                analysis.risk.level === 'CRITICAL'
                  ? 'bg-red-500/20 text-red-400 border border-red-500/40'
                  : analysis.risk.level === 'HIGH'
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              {analysis.risk.level}
            </span>
          </div>
          <div className="space-y-1.5">
            <div className="text-[11px] text-slate-400 font-medium">Contributory NLP Factors:</div>
            {analysis.risk.factors.map((f, i) => (
              <div key={i} className="p-2 rounded bg-slate-950 border border-slate-800/80 flex items-center justify-between text-xs">
                <div>
                  <div className="font-medium text-slate-200">{f.name}</div>
                  <div className="text-[10px] text-slate-500">{f.description}</div>
                </div>
                <div className="font-mono text-right shrink-0 ml-3">
                  <span className="text-blue-400 font-bold">{f.score}</span>
                  <span className="text-slate-600"> / {f.weight} pts</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 'explainability',
      name: '10. Explainable NLP Evidence',
      icon: HelpCircle,
      summary: `${analysis.explanation.evidence_cards.length} empirical evidence cards`,
      render: () => (
        <div className="space-y-2">
          <div className="text-xs text-slate-400">Why VoiceShield AI Flagged This Message:</div>
          <div className="space-y-1.5 max-h-48 overflow-y-auto">
            {analysis.explanation.evidence_cards.map((card, i) => (
              <div key={i} className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold text-amber-400">{card.title}</div>
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                    {card.tag}
                  </span>
                </div>
                <div className="text-xs text-slate-300 font-mono mt-1 bg-slate-950 p-1.5 rounded border border-slate-800">
                  {card.evidence}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">{card.description}</div>
              </div>
            ))}
          </div>
        </div>
      )
    }
  ];

  const currentStepObj = steps.find((s) => s.id === selectedStep) || steps[0];

  return (
    <div className="glass-panel rounded-xl p-5 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            Interactive NLP Pipeline Visualizer
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
              Live Inspection
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Click on any phase to inspect the actual intermediate representations generated for this message.
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs text-slate-400">Pipeline Latency: </span>
          <span className="text-xs font-mono font-bold text-emerald-400">{analysis.processing_time_ms} ms</span>
        </div>
      </div>

      {/* Step Pills Progression Bar */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-3 mb-4 scrollbar-thin">
        {steps.map((step, idx) => {
          const isSelected = selectedStep === step.id;
          return (
            <React.Fragment key={step.id}>
              <button
                onClick={() => setSelectedStep(step.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium shrink-0 transition-all ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20 border border-blue-400/40'
                    : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                <step.icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-slate-400'}`} />
                <span>{step.name}</span>
              </button>
              {idx < steps.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-slate-700 shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Detail Inspector Card */}
      <div className="bg-slate-950/70 rounded-xl p-4 border border-slate-800/80">
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <currentStepObj.icon className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-bold text-white">{currentStepObj.name}</span>
          </div>
          <span className="text-xs font-mono text-slate-400">{currentStepObj.summary}</span>
        </div>
        {currentStepObj.render()}
      </div>
    </div>
  );
};

function intPct(val: number): number {
  return Math.round(val * 100);
}

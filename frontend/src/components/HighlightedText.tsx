import React, { useState } from 'react';
import { AnalysisResult } from '../types';

interface HighlightedTextProps {
  analysis: AnalysisResult;
}

interface SpanItem {
  start: number;
  end: number;
  text: string;
  type: string;
  category: string;
  reason: string;
  colorClass: string;
}

export const HighlightedText: React.FC<HighlightedTextProps> = ({ analysis }) => {
  const [activeTooltip, setActiveTooltip] = useState<SpanItem | null>(null);

  const text = analysis.input_text;
  const spans: SpanItem[] = [];

  // 1. Entities
  for (const ent of analysis.entities) {
    let color = 'bg-purple-500/20 text-purple-300 border-purple-500/40 hover:bg-purple-500/30';
    if (ent.label === 'AUTH_CREDENTIAL') {
      color = 'bg-red-500/25 text-red-300 border-red-500/50 hover:bg-red-500/35';
    } else if (ent.label === 'BANK' || ent.label === 'MONEY') {
      color = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30';
    } else if (ent.label === 'URL') {
      color = 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 hover:bg-cyan-500/30';
    }

    spans.push({
      start: ent.start,
      end: ent.end,
      text: ent.text,
      type: ent.label,
      category: 'Named Entity',
      reason: ent.description,
      colorClass: color
    });
  }

  // 2. Urgency Cues
  for (const cue of analysis.urgency.cues) {
    if (cue.start >= 0 && cue.end > cue.start) {
      spans.push({
        start: cue.start,
        end: cue.end,
        text: cue.cue,
        type: 'Urgency Cue',
        category: 'Psychological Pressure',
        reason: cue.reason,
        colorClass: 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
      });
    }
  }

  // Sort and remove duplicates or overlaps
  spans.sort((a, b) => a.start - b.start);

  const renderSegments = () => {
    const segments: React.ReactNode[] = [];
    let currentIndex = 0;

    for (let i = 0; i < spans.length; i++) {
      const span = spans[i];
      if (span.start < currentIndex) continue; // skip overlapping

      // Text before the highlight
      if (span.start > currentIndex) {
        segments.push(
          <span key={`plain-${currentIndex}`}>
            {text.substring(currentIndex, span.start)}
          </span>
        );
      }

      // Highlighted token
      segments.push(
        <span
          key={`span-${span.start}-${i}`}
          onMouseEnter={() => setActiveTooltip(span)}
          onMouseLeave={() => setActiveTooltip(null)}
          className={`relative inline-block px-1.5 py-0.5 mx-0.5 rounded border text-xs font-medium cursor-pointer transition-all duration-150 ${span.colorClass}`}
        >
          {text.substring(span.start, span.end)}
        </span>
      );

      currentIndex = span.end;
    }

    if (currentIndex < text.length) {
      segments.push(
        <span key={`plain-end`}>{text.substring(currentIndex)}</span>
      );
    }

    return segments;
  };

  return (
    <div className="glass-card rounded-xl p-4 border border-slate-800 relative">
      <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-800">
        <div className="text-xs font-semibold text-slate-300 flex items-center gap-2">
          <span>Linguistic Feature Highlighting</span>
          <span className="text-[10px] text-slate-500 font-normal">Hover words for NLP rationale</span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded bg-purple-400" />
            <span className="text-slate-400">Entity</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded bg-amber-400" />
            <span className="text-slate-400">Urgency</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded bg-red-400" />
            <span className="text-slate-400">Credential / Risk</span>
          </span>
        </div>
      </div>

      <div className="p-3 bg-slate-950/80 rounded-lg text-sm leading-relaxed text-slate-200 font-sans tracking-wide">
        {renderSegments()}
      </div>

      {/* Floating rationale tooltip card */}
      {activeTooltip && (
        <div className="mt-3 p-3 rounded-lg bg-slate-900 border border-slate-700 shadow-xl flex items-start justify-between text-xs animate-fadeIn">
          <div>
            <div className="font-semibold text-white flex items-center gap-2">
              <span>{activeTooltip.text}</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded font-mono bg-blue-500/20 text-blue-400 border border-blue-500/30">
                {activeTooltip.type}
              </span>
            </div>
            <div className="text-slate-400 text-[11px] mt-1">{activeTooltip.reason}</div>
          </div>
          <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-4">
            {activeTooltip.category}
          </span>
        </div>
      )}
    </div>
  );
};

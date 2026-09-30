import React from 'react';
import { AnalysisResult } from '../types';
import { AlertTriangle, CheckCircle, ShieldAlert, ShieldCheck } from 'lucide-react';

interface RiskCardProps {
  analysis: AnalysisResult;
}

export const RiskCard: React.FC<RiskCardProps> = ({ analysis }) => {
  const { risk, classification, intent, urgency } = analysis;
  const score = risk.score;
  const level = risk.level;

  let strokeColor = '#10b981'; // green
  if (level === 'CRITICAL') strokeColor = '#ef4444'; // red
  else if (level === 'HIGH') strokeColor = '#f97316'; // orange
  else if (level === 'MEDIUM') strokeColor = '#eab308'; // yellow

  // SVG gauge constants
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800 relative overflow-hidden">
      {/* Background ambient glow */}
      <div
        className="absolute -top-16 -right-16 w-56 h-56 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ backgroundColor: strokeColor }}
      />

      <div className="flex flex-col md:flex-row items-center gap-6 justify-between">
        {/* Left: Gauge and Level */}
        <div className="flex items-center gap-5">
          <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
            <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 130 130">
              <circle
                cx="65"
                cy="65"
                r={radius}
                className="stroke-slate-800"
                strokeWidth="10"
                fill="transparent"
              />
              <circle
                cx="65"
                cy="65"
                r={radius}
                stroke={strokeColor}
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
                {Math.round(score)}
              </span>
              <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">
                Risk Score
              </span>
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs uppercase font-semibold tracking-wider text-slate-400">
                Threat Assessment
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider font-mono border ${
                  level === 'CRITICAL'
                    ? 'bg-red-500/20 text-red-400 border-red-500/40'
                    : level === 'HIGH'
                    ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
                    : level === 'MEDIUM'
                    ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40'
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}
              >
                {level}
              </span>
            </div>

            <h2 className="text-xl font-bold text-white mt-1.5 flex items-center gap-2">
              {classification.predicted_category}
            </h2>

            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              Model confidence:{' '}
              <span className="text-white font-mono font-semibold">
                {classification.confidence_percentage}%
              </span>{' '}
              | Classifier:{' '}
              <span className="text-blue-400 font-mono">
                {classification.active_model}
              </span>
            </p>
          </div>
        </div>

        {/* Right: Key Signals Grid */}
        <div className="grid grid-cols-2 gap-3 w-full md:w-auto shrink-0">
          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 min-w-[140px]">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Intent</div>
            <div className="text-xs font-bold text-white mt-0.5 truncate">{intent.intent}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              {Math.round(intent.confidence * 100)}% match
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 min-w-[140px]">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Urgency</div>
            <div className="text-xs font-bold text-amber-400 mt-0.5">{urgency.level}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              Score: {urgency.score}/100
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 min-w-[140px]">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Language</div>
            <div className="text-xs font-bold text-white mt-0.5 truncate">{analysis.language.language_name}</div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              {analysis.language.script} script
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 min-w-[140px]">
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Classification</div>
            <div className={`text-xs font-bold mt-0.5 ${classification.is_scam ? 'text-red-400' : 'text-emerald-400'}`}>
              {classification.is_scam ? 'Malicious / Scam' : 'Legitimate / Safe'}
            </div>
            <div className="text-[10px] text-slate-500 font-mono mt-0.5">
              {analysis.similar_messages.length} similar matches
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

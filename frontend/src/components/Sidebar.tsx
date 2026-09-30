import React from 'react';
import {
  LayoutDashboard,
  MessageSquareText,
  MessagesSquare,
  Binary,
  ShieldAlert,
  Search,
  BookOpen,
  History,
  BarChart3,
  Cpu,
  Layers,
  FileSpreadsheet,
  Mic,
  FileText,
  Boxes,
  Settings,
  GraduationCap
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'analyze', label: 'Analyze Message', icon: MessageSquareText },
  { id: 'conversation', label: 'Conversation Analyzer', icon: MessagesSquare },
  { id: 'nlp-deep', label: 'NLP Deep Analysis', icon: Binary },
  { id: 'risk', label: 'Risk Intelligence', icon: ShieldAlert },
  { id: 'similarity', label: 'Similarity Search', icon: Search },
  { id: 'knowledge', label: 'Scam Knowledge Base', icon: BookOpen },
  { id: 'history', label: 'Conversation History', icon: History },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'nlp-metrics', label: 'NLP Metrics', icon: Cpu },
  { id: 'threat-patterns', label: 'Threat Patterns', icon: Layers },
  { id: 'batch', label: 'Batch Analysis', icon: FileSpreadsheet },
  { id: 'audio', label: 'Audio Analysis', icon: Mic },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'models', label: 'Model Center', icon: Boxes },
  { id: 'settings', label: 'Settings', icon: Settings },
  { id: 'about-viva', label: 'Architecture & Viva', icon: GraduationCap }
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, isOpen, setIsOpen }) => {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-screen w-64 bg-[#0d1322] border-r border-slate-800 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <ShieldAlert className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-base font-bold text-white tracking-tight flex items-center gap-1.5">
                VoiceShield <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-mono">AI</span>
              </div>
              <div className="text-[10px] text-slate-400 font-medium tracking-wide">NLP Scam Intelligence</div>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id);
                  setIsOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span className="truncate">{item.label}</span>
                {item.id === 'about-viva' && (
                  <span className="ml-auto text-[9px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.2 rounded font-mono">
                    BE Sem 7
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer / Status */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
          <div className="flex items-center gap-2 px-2 py-1.5 rounded-md bg-slate-800/40 border border-slate-700/50">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <div className="text-[11px] text-slate-300 font-mono truncate">
              Local NLP: <span className="text-emerald-400 font-semibold">Active</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

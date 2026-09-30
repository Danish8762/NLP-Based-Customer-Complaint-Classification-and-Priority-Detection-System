import React from 'react';
import { Menu, Play, Presentation, ShieldCheck, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  toggleSidebar: () => void;
  onSelectDemo: (text: string) => void;
}

export const DEMO_PRESETS = [
  {
    title: "1. SBI Bank Account Freeze & PAN Coercion",
    category: "Banking Scam",
    text: "URGENT NOTICE: Your State Bank savings account has been temporarily locked due to irregular transactions. Click http://sbi-secure-update.com to verify your PAN immediately."
  },
  {
    title: "2. OTP Passcode Extraction for Transaction",
    category: "OTP Scam",
    text: "Your one-time passcode for transaction of INR 12,499 is 849201. If you did not authorize this, share this code with our fraud desk officer on call immediately."
  },
  {
    title: "3. FedEx Parcel Delivery Surcharge Phishing",
    category: "Delivery Scam",
    text: "FedEx: Your package delivery has been stopped due to incomplete street address. Pay $1.99 redelivery fee at http://fedex-parcel-redeliver.info within 12 hours."
  },
  {
    title: "4. Amazon Part-Time WFH Job Offer",
    category: "Job Scam",
    text: "Amazon Part-Time Hiring: Earn INR 3,000 to 8,000 daily by simply rating products from home. No prior experience needed. Contact WhatsApp: +91-9988776655."
  },
  {
    title: "5. Hinglish ICICI Account Threat",
    category: "Banking Scam (Hinglish)",
    text: "Aapka ICICI bank account achanak freeze kar diya gaya hai. Turant diye gaye link par click karein aur account unlock karwayein: http://icici-verify-now.cc"
  },
  {
    title: "6. Legitimate Quarterly Project Meeting",
    category: "Legitimate / Safe",
    text: "Hi Team, please find attached the minutes of our quarterly project review meeting. Let me know if you have any questions before our Friday standup."
  }
];

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  toggleSidebar,
  onSelectDemo
}) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-[#0b0f19]/80 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-sm font-semibold text-white capitalize tracking-wide flex items-center gap-2">
            {activeTab.replace('-', ' ')}
            <span className="hidden sm:inline-block w-1.5 h-1.5 rounded-full bg-blue-500" />
            <span className="hidden sm:inline-block text-xs font-normal text-slate-400">
              BE Semester 7 AI & Data Science Major Project
            </span>
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Quick Demo Dropdown */}
        <div className="relative group">
          <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600/10 border border-blue-500/30 text-blue-400 hover:bg-blue-600/20 text-xs font-medium transition-colors">
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Load Demo Message</span>
          </button>
          
          <div className="absolute right-0 mt-1 w-80 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2 hidden group-hover:block z-50">
            <div className="text-[11px] font-semibold text-slate-400 px-2 py-1 uppercase tracking-wider">
              Academic Test Presets
            </div>
            {DEMO_PRESETS.map((demo, idx) => (
              <button
                key={idx}
                onClick={() => {
                  onSelectDemo(demo.text);
                  setActiveTab('analyze');
                }}
                className="w-full text-left p-2 rounded-lg hover:bg-slate-800/80 transition-colors group/item"
              >
                <div className="text-xs font-medium text-slate-200 group-hover/item:text-blue-400">
                  {demo.title}
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                  {demo.category}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Presentation Mode Toggle */}
        <button
          onClick={() => setActiveTab('about-viva')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
            activeTab === 'about-viva'
              ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-600/30'
              : 'bg-slate-800/60 border-slate-700 text-slate-300 hover:bg-slate-700'
          }`}
        >
          <Presentation className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Presentation & Viva</span>
        </button>
      </div>
    </header>
  );
};

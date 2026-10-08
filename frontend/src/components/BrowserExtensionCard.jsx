import React, { useState } from 'react';
import {
  Puzzle,
  Download,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function BrowserExtensionCard() {
  const [copied, setCopied] = useState(false);

  const handleCopyPath = () => {
    navigator.clipboard?.writeText('chrome://extensions');
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gradient-to-br from-white to-teal-50/40 rounded-2xl border border-teal-200/80 p-5 sm:p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex items-start space-x-3.5">
        <div className="w-12 h-12 rounded-xl bg-teal-700 text-white flex items-center justify-center shrink-0 shadow-sm shadow-teal-700/20">
          <Puzzle className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-slate-900">
              ScamShield Browser Companion Extension
            </h3>
            <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
              Manifest V3
            </span>
          </div>
          <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
            Real-time proactive shield for <strong>Gmail Web</strong>, <strong>WhatsApp Web</strong>, and <strong>Outlook</strong>. Automatically inspects incoming links and highlights deceptive lookalikes before you click.
          </p>
          <div className="flex items-center gap-3 pt-1 text-[11px] text-teal-800 font-medium">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Zero tracking
            </span>
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Instant tooltip alerts
            </span>
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" /> Right-click quick inspect
            </span>
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-center gap-2.5 shrink-0">
        <button
          onClick={handleCopyPath}
          className="w-full sm:w-auto px-3.5 py-2 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 transition-colors flex items-center justify-center space-x-1.5 cursor-pointer shadow-2xs"
          title="Open chrome://extensions in a new tab"
        >
          <span>{copied ? 'Copied chrome://extensions' : 'Load Unpacked in Chrome'}</span>
        </button>

        <a
          href="/extension/scamshield-extension.zip"
          download="scamshield-extension.zip"
          className="w-full sm:w-auto px-4 py-2 rounded-xl bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold transition-colors flex items-center justify-center space-x-1.5 shadow-xs cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Get Extension Bundle</span>
        </a>
      </div>
    </div>
  );
}

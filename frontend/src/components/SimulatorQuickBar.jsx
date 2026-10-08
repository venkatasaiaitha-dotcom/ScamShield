import React, { useState } from 'react';
import { Play, Sparkles, CheckCircle2, AlertTriangle, AlertOctagon, Loader2 } from 'lucide-react';

export default function SimulatorQuickBar({ onTriggerScenario, isSimulating }) {
  const [activeScenario, setActiveScenario] = useState(null);

  const presets = [
    { type: 'WHATSAPP_FAMILY_IMPERSONATION', label: 'WhatsApp Hi-Mum Scam', icon: AlertOctagon, color: 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' },
    { type: 'FAKE_KYC', label: 'SMS Fake KYC Phishing', icon: AlertOctagon, color: 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' },
    { type: 'BANK_IMPERSONATION', label: 'Bank Impersonation', icon: AlertOctagon, color: 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' },
    { type: 'WHATSAPP_ACCOUNT_TAKEOVER', label: 'WhatsApp Deactivation Link', icon: AlertTriangle, color: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' },
    { type: 'JOB_SCAM', label: 'Part-time Job Fraud', icon: AlertTriangle, color: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' },
    { type: 'PRIZE_SCAM', label: 'Lottery / Prize', icon: AlertTriangle, color: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' },
    { type: 'LEGITIMATE_OTP', label: 'Safe Bank OTP', icon: CheckCircle2, color: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' },
    { type: 'NORMAL_DELIVERY', label: 'Safe Courier Notice', icon: CheckCircle2, color: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' },
  ];

  const handleSimulate = async (type) => {
    setActiveScenario(type);
    try {
      await onTriggerScenario(type);
    } finally {
      setActiveScenario(null);
    }
  };

  return (
    <div className="p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-teal-700" />
          <h2 className="text-xs sm:text-sm font-bold text-slate-900 tracking-wide uppercase">
            Incoming Threat Simulator (Interactive Demonstration Stream)
          </h2>
        </div>
        <span className="text-[11px] text-slate-500">
          Injects realistic test threats directly into the proactive agent pipeline
        </span>
      </div>

      <div className="mt-3.5 flex flex-wrap gap-2 items-center">
        {presets.map((preset) => {
          const Icon = preset.icon;
          const isLoading = isSimulating && activeScenario === preset.type;

          return (
            <button
              key={preset.type}
              onClick={() => handleSimulate(preset.type)}
              disabled={isSimulating}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all active:scale-95 disabled:opacity-50 shadow-xs cursor-pointer ${preset.color}`}
            >
              {isLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Icon className="w-3.5 h-3.5" />
              )}
              <span>{preset.label}</span>
            </button>
          );
        })}

        <button
          onClick={() => handleSimulate('RANDOM')}
          disabled={isSimulating}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-teal-700 hover:bg-teal-800 text-white shadow-xs transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
        >
          {isSimulating && activeScenario === 'RANDOM' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5" />
          )}
          <span>Random Simulation</span>
        </button>
      </div>
    </div>
  );
}

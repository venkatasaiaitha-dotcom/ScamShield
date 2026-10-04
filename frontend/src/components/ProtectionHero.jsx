import React from 'react';
import { Shield, Power, RefreshCw } from 'lucide-react';

export default function ProtectionHero({ agentStatus, onToggleProtection, loadingToggle }) {
  const isActive = agentStatus?.protection_active;
  const monitoringSources = agentStatus?.monitoring_sources || [];

  return (
    <div className={`relative overflow-hidden rounded-2xl border transition-all duration-300 p-6 md:p-8 shadow-xs ${
      isActive
        ? 'bg-white border-teal-200 shadow-teal-900/5'
        : 'bg-white border-slate-200 shadow-slate-900/5'
    }`}>
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Left Column: Heading and description */}
        <div className="space-y-3 max-w-2xl">
          <div className="flex items-center space-x-3">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center border shadow-xs ${
              isActive
                ? 'bg-teal-50 border-teal-200 text-teal-700'
                : 'bg-slate-100 border-slate-200 text-slate-500'
            }`}>
              <Shield className={`w-6 h-6 ${isActive ? 'animate-pulse-slow' : ''}`} />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
                🛡️ ScamShield
              </h1>
              <p className="text-sm font-semibold text-teal-700">
                Your AI Safety Agent
              </p>
            </div>
          </div>

          <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
            ScamShield automatically inspects incoming messages as they arrive across connected sources and warns you before you interact with them.
          </p>

          {/* Status Display */}
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <div className={`inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full text-xs font-semibold border ${
              isActive
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-slate-100 border-slate-300 text-slate-700'
            }`}>
              <span className={`w-2.5 h-2.5 rounded-full ${isActive ? 'bg-emerald-600 animate-pulse' : 'bg-slate-400'}`} />
              <span>{isActive ? '🟢 Protection Active' : '⚪ Protection Paused'}</span>
            </div>

            <span className="text-xs text-slate-500 font-medium">
              {isActive
                ? 'Monitoring connected message sources'
                : 'Turn protection on to automatically inspect incoming messages'}
            </span>
          </div>

          {/* Connected message sources pills */}
          {isActive && monitoringSources.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 pt-2">
              <span className="text-xs text-slate-500 font-semibold">Active Integrations:</span>
              {monitoringSources.map((sourceName) => (
                <span
                  key={sourceName}
                  className="inline-flex items-center text-[11px] px-2.5 py-1 rounded-md bg-slate-50 text-slate-700 border border-slate-200 font-medium"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-600 mr-1.5" />
                  {sourceName}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Large Action Switch */}
        <div className="flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-end justify-center gap-2 pt-2 lg:pt-0">
          <button
            onClick={onToggleProtection}
            disabled={loadingToggle}
            className={`flex items-center justify-center space-x-2.5 px-6 py-3.5 rounded-xl font-bold text-sm tracking-wide transition-all shadow-xs active:scale-95 disabled:opacity-50 cursor-pointer ${
              isActive
                ? 'bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300'
                : 'bg-teal-700 hover:bg-teal-800 text-white shadow-sm'
            }`}
          >
            {loadingToggle ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Power className="w-4 h-4" />
            )}
            <span>{isActive ? 'Pause Protection' : 'Enable Protection'}</span>
          </button>

          <span className="text-[11px] text-slate-400">
            {isActive ? 'Click to temporarily pause threat inspection' : 'Proactive safety agent is standing by'}
          </span>
        </div>
      </div>
    </div>
  );
}

import React from 'react';
import { GitCommit, ArrowRight, ShieldAlert, Sparkles, CheckCircle2, Clock } from 'lucide-react';

export default function ScamAttackChainCard({ attackChain }) {
  if (!attackChain) return null;

  const {
    current_stage_name,
    predicted_next_stage,
    stages_timeline = [],
    chain_narrative
  } = attackChain;

  return (
    <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-lg relative overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 relative z-10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-red-500/20 text-red-400 rounded-lg border border-red-500/30">
            <GitCommit className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-red-400 uppercase bg-red-950/60 px-2 py-0.5 rounded border border-red-800/50">
                Kill-Chain Correlation
              </span>
              <span className="text-xs text-slate-400">Multi-Stage Analysis</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2 mt-0.5">
              SCAM ATTACK CHAIN DETECTED
            </h3>
          </div>
        </div>

        {predicted_next_stage && (
          <div className="flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 text-xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Predicted Next Stage:</span>
            <span className="font-semibold text-amber-300">{predicted_next_stage}</span>
          </div>
        )}
      </div>

      {/* Horizontal Kill-Chain Timeline */}
      <div className="mt-4 mb-5 relative z-10">
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 sm:gap-1.5">
          {stages_timeline.map((step, idx) => {
            const isCompleted = step.status === 'COMPLETED';
            const isActive = step.is_current || step.status === 'ACTIVE_DETECTED';
            const isFuture = step.status === 'PREDICTED_FUTURE';

            return (
              <div
                key={step.stage_id || idx}
                className={`relative flex flex-col p-3 rounded-lg border transition-all ${
                  isActive
                    ? 'bg-red-950/40 border-red-500/80 ring-2 ring-red-500/30'
                    : isCompleted
                    ? 'bg-slate-800/60 border-emerald-500/40 text-slate-300'
                    : 'bg-slate-800/30 border-slate-700/60 text-slate-400 opacity-70'
                }`}
              >
                {/* Stage number & status badge */}
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] font-mono uppercase tracking-wider font-semibold text-slate-400">
                    Stage {idx + 1}
                  </span>
                  {isActive && (
                    <span className="flex h-2 w-2 relative">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                    </span>
                  )}
                  {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                  {isFuture && <Clock className="w-3.5 h-3.5 text-slate-500" />}
                </div>

                <div className="font-semibold text-xs leading-snug text-slate-100 mb-1">
                  {step.name}
                </div>

                <div className="text-[11px] text-slate-400 leading-tight line-clamp-2">
                  {step.description}
                </div>

                {isActive && (
                  <div className="mt-2 text-[10px] font-bold uppercase tracking-wider text-red-400 bg-red-900/40 px-1.5 py-0.5 rounded text-center border border-red-700/50">
                    Active Vector
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Narrative Footer */}
      {chain_narrative && (
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800 flex items-start gap-2.5 text-xs text-slate-300">
          <ShieldAlert className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <span className="font-semibold text-slate-200">Threat Correlation: </span>
            {chain_narrative}
          </div>
        </div>
      )}
    </div>
  );
}

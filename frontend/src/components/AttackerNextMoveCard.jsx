import React from 'react';
import { Eye, Shield, HelpCircle, AlertCircle, ArrowUpRight } from 'lucide-react';

export default function AttackerNextMoveCard({ nextMoves }) {
  if (!nextMoves || !nextMoves.length) return null;

  return (
    <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-lg relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3 relative z-10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-purple-500/20 text-purple-400 rounded-lg border border-purple-500/30">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-purple-400 uppercase bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/50">
                Predictive Intelligence
              </span>
              <span className="text-xs text-slate-400">Adversary Forecast</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-0.5">
              WHAT THE ATTACKER MAY TRY NEXT
            </h3>
          </div>
        </div>

        <div className="text-[11px] font-mono text-purple-300 bg-purple-950/60 px-2.5 py-1 rounded border border-purple-800/50">
          Probabilistic Tactical Forecast
        </div>
      </div>

      <p className="text-xs text-slate-400 mb-4 relative z-10">
        Based on historical attack kill chains for this campaign profile, ScamShield predicts the following subsequent coercion maneuvers:
      </p>

      {/* Predicted Moves Cards */}
      <div className="space-y-3 relative z-10">
        {nextMoves.map((item, idx) => {
          const title = item.predicted_move || item.move;
          const prob = item.probability_pct || (item.probability ? Math.round(item.probability * 100) : 85);
          const tip = item.prevention_tip || item.defensive_advice;

          return (
            <div
              key={idx}
              className="bg-slate-950/70 rounded-xl p-4 border border-slate-800 hover:border-purple-500/40 transition-all"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                  <span className="flex items-center justify-center w-5 h-5 rounded-full bg-purple-900/60 text-purple-300 text-xs font-mono font-bold border border-purple-700/60">
                    {idx + 1}
                  </span>
                  {title}
                </div>

                <div className="flex items-center gap-1.5 flex-shrink-0">
                  <span className="text-xs font-mono font-bold text-purple-300">
                    {prob}% confidence
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden mb-3">
                <div
                  className="bg-gradient-to-r from-purple-500 to-indigo-400 h-full rounded-full transition-all duration-500"
                  style={{ width: `${prob}%` }}
                />
              </div>

              {/* Defensive Recommendation */}
              {tip && (
                <div className="flex items-start gap-2 text-xs text-slate-300 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800/80">
                  <Shield className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-semibold text-emerald-400">Counter-Measure: </span>
                    {tip}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Accuracy Label Disclaimer */}
      <div className="mt-3.5 text-[10px] text-slate-500 font-mono flex items-center gap-1.5 relative z-10">
        <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
        Estimates derived from MITRE ATT&CK probabilistic kill-chain transitions. Labelled as predictive forecasts, not guaranteed outcomes.
      </div>
    </div>
  );
}

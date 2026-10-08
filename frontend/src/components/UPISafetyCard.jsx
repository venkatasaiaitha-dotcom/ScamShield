import React from 'react';
import { IndianRupee, AlertOctagon, AlertTriangle, CheckCircle2, ShieldCheck, ArrowRight, Info } from 'lucide-react';

export default function UPISafetyCard({ upiSafety }) {
  if (!upiSafety || !upiSafety.has_upi_payload) return null;

  const {
    safety_verdict = 'SAFE',
    badge_color = 'green',
    primary_vpa,
    all_vpas = [],
    is_mismatch = false,
    mismatch_details,
    reasons = [],
    risk_score = 0,
    disclaimer = 'Pre-payment security safety advisory. ScamShield does not directly execute or block banking rail transactions.'
  } = upiSafety;

  const isHighRisk = safety_verdict === 'HIGH_RISK_DO_NOT_PAY';
  const isVerify = safety_verdict === 'VERIFY_BEFORE_PAYING';
  const isSafe = safety_verdict === 'SAFE';

  const verdictStyles = isHighRisk
    ? {
        border: 'border-red-500/50',
        bg: 'bg-red-950/40',
        badgeBg: 'bg-red-900/60 text-red-200 border-red-700',
        icon: <AlertOctagon className="w-5 h-5 text-red-400" />,
        title: 'HIGH RISK — DO NOT PAY',
        accentColor: 'text-red-400',
      }
    : isVerify
    ? {
        border: 'border-amber-500/50',
        bg: 'bg-amber-950/30',
        badgeBg: 'bg-amber-900/60 text-amber-200 border-amber-700',
        icon: <AlertTriangle className="w-5 h-5 text-amber-400" />,
        title: 'VERIFY BEFORE PAYING',
        accentColor: 'text-amber-400',
      }
    : {
        border: 'border-emerald-500/50',
        bg: 'bg-emerald-950/30',
        badgeBg: 'bg-emerald-900/60 text-emerald-200 border-emerald-700',
        icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />,
        title: 'SAFE PAYMENT RECIPIENT',
        accentColor: 'text-emerald-400',
      };

  return (
    <div className={`rounded-xl p-5 border ${verdictStyles.border} ${verdictStyles.bg} bg-slate-900 text-white shadow-lg relative overflow-hidden`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-amber-500/20 text-amber-400 rounded-lg border border-amber-500/30">
            <IndianRupee className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-amber-400 uppercase bg-amber-950/60 px-2 py-0.5 rounded border border-amber-800/50">
                India Payment Guard
              </span>
              <span className="text-xs text-slate-400">Pre-Payment Rail Audit</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-0.5">
              UPI PAYMENT SAFETY VERDICT
            </h3>
          </div>
        </div>

        {/* Verdict Badge */}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-bold text-xs ${verdictStyles.badgeBg}`}>
          {verdictStyles.icon}
          <span>{verdictStyles.title}</span>
        </div>
      </div>

      {/* Target VPA & Entity Mismatch Box */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Destination UPI Handle (VPA)
          </div>
          <div className="font-mono text-xs font-bold text-amber-300 select-all">
            {primary_vpa || 'None extracted'}
          </div>
        </div>

        <div className={`rounded-lg p-3 border ${is_mismatch ? 'bg-red-950/40 border-red-700/60' : 'bg-slate-950/60 border-slate-800'}`}>
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Entity vs Account Match
          </div>
          <div className="text-xs font-bold flex items-center gap-1.5">
            {is_mismatch ? (
              <span className="text-red-400 flex items-center gap-1">
                <AlertOctagon className="w-3.5 h-3.5" /> CRITICAL MISMATCH DETECTED
              </span>
            ) : (
              <span className="text-emerald-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> No Entity Discrepancy Found
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Mismatch Context Alert */}
      {is_mismatch && mismatch_details && (
        <div className="bg-red-950/60 border border-red-800/80 rounded-lg p-3 mb-3 text-xs text-red-200">
          <div className="font-semibold text-red-300 mb-0.5">Payment Identity Discrepancy:</div>
          <div>{mismatch_details}</div>
        </div>
      )}

      {/* Specific Reasons */}
      {reasons.length > 0 && (
        <div className="mb-3 space-y-1.5">
          {reasons.map((r, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-300 bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
              <span className="text-amber-400 font-bold">•</span>
              <span>{r}</span>
            </div>
          ))}
        </div>
      )}

      {/* Safe Golden Rule */}
      <div className="bg-slate-950/80 rounded-lg p-3 border border-slate-800 text-xs text-slate-300 mb-3 flex items-start gap-2">
        <Info className="w-4 h-4 text-sky-400 mt-0.5 flex-shrink-0" />
        <div>
          <span className="font-semibold text-sky-300">UPI Security Principle: </span>
          Entering your UPI PIN is <span className="text-white font-bold underline">always and exclusively</span> for sending money. You <span className="text-red-300 font-semibold">never</span> enter a UPI PIN to receive money, refunds, lottery rewards, or KYC updates.
        </div>
      </div>

      {/* Mandatory Disclaimer */}
      <div className="text-[10px] text-slate-500 font-mono leading-tight">
        * {disclaimer}
      </div>
    </div>
  );
}

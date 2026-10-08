import React from 'react';
import { Fingerprint, Shield, Users, Layers, ExternalLink, Activity, Award } from 'lucide-react';

export default function ScamDNACard({ scamDna }) {
  if (!scamDna) return null;

  const {
    campaign_id,
    dna_hash,
    scam_type,
    impersonated_brand,
    attack_techniques = [],
    variant_count = 1,
    community_reports = 0,
    immunity_protected_count = 1,
    threat_status = 'ACTIVE_CAMPAIGN'
  } = scamDna;

  return (
    <div className="bg-slate-900 text-white rounded-xl p-5 border border-slate-800 shadow-lg relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 relative z-10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Fingerprint className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-indigo-400 uppercase bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/50">
                Campaign Fingerprint
              </span>
              <span className="text-xs text-slate-400">Structural DNA</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-0.5">
              SCAM DNA & CAMPAIGN CLUSTER
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-red-950/60 text-red-300 border border-red-800/60">
            <Activity className="w-3 h-3 text-red-400 animate-pulse" />
            {threat_status.replace(/_/g, ' ')}
          </span>
        </div>
      </div>

      {/* DNA Identifiers Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4 relative z-10">
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Deterministic DNA Hash
          </div>
          <div className="font-mono text-xs font-bold text-indigo-300 select-all break-all">
            {dna_hash || 'DNA-GEN-000-000-0000'}
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Cluster Campaign ID
          </div>
          <div className="font-mono text-xs font-bold text-emerald-400 select-all">
            {campaign_id || 'CMP-GEN-0000'}
          </div>
        </div>
      </div>

      {/* Metadata Highlights */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4 relative z-10 text-xs">
        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-[11px]">Impersonated Brand</div>
          <div className="font-semibold text-slate-200 mt-0.5 truncate">
            {impersonated_brand || 'Generic / Unbranded'}
          </div>
        </div>

        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-[11px]">Scam Category</div>
          <div className="font-semibold text-slate-200 mt-0.5 truncate">
            {scam_type?.replace(/_/g, ' ') || 'Social Engineering'}
          </div>
        </div>

        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-[11px] flex items-center gap-1">
            <Layers className="w-3 h-3 text-slate-400" /> Wording Variants
          </div>
          <div className="font-semibold text-amber-300 mt-0.5">
            {variant_count} tracked variants
          </div>
        </div>

        <div className="bg-slate-800/40 p-2.5 rounded-lg border border-slate-800">
          <div className="text-slate-400 text-[11px] flex items-center gap-1">
            <Users className="w-3 h-3 text-slate-400" /> Community Reports
          </div>
          <div className="font-semibold text-slate-200 mt-0.5">
            {community_reports} verified
          </div>
        </div>
      </div>

      {/* MITRE ATT&CK Techniques */}
      {attack_techniques.length > 0 && (
        <div className="mb-4 relative z-10">
          <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <ExternalLink className="w-3 h-3 text-slate-400" />
            MITRE ATT&CK® Techniques Mapped
          </div>
          <div className="flex flex-wrap gap-1.5">
            {attack_techniques.map((tech, i) => (
              <span
                key={i}
                className="text-[11px] font-mono bg-slate-800/90 hover:bg-slate-800 text-slate-300 px-2.5 py-1 rounded border border-slate-700/80 transition"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Signature Feature 5: Community Immunity Network */}
      <div className="bg-gradient-to-r from-emerald-950/40 to-slate-900 rounded-lg p-3.5 border border-emerald-800/40 flex items-center justify-between gap-3 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg border border-emerald-500/30">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold">
              Community Immunity Network
            </div>
            <div className="text-sm font-bold text-slate-100">
              Community Immunity: <span className="text-emerald-400">{immunity_protected_count} users</span> protected from similar campaign patterns.
            </div>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-300/80 bg-emerald-950/80 px-2.5 py-1 rounded border border-emerald-800/50">
          <Award className="w-3.5 h-3.5 text-emerald-400" />
          Active Herd Shield
        </div>
      </div>
    </div>
  );
}

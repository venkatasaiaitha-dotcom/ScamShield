import React from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  AlertOctagon,
  ArrowRight,
  Clock,
  Smartphone,
  Mail,
  Cpu,
  Globe
} from 'lucide-react';
import ProtectionHero from '../components/ProtectionHero';
import MetricCards from '../components/MetricCards';
import SimulatorQuickBar from '../components/SimulatorQuickBar';
import GmailConnectorCard from '../components/GmailConnectorCard';
import ImageInspectorCard from '../components/ImageInspectorCard';
import BrowserExtensionCard from '../components/BrowserExtensionCard';

export default function DashboardView({
  agentStatus,
  onToggleProtection,
  loadingToggle,
  onTriggerScenario,
  isSimulating,
  recentAnalyses,
  onViewAnalysis,
  onNavigateHistory,
  onMessageAnalyzed,
  dateRange,
  onDateRangeChange,
}) {
  const threatsOnly = (recentAnalyses || []).filter(
    (a) => a.risk_level === 'HIGH' || a.risk_level === 'SUSPICIOUS'
  );

  const getSourceIcon = (source) => {
    switch (source?.toUpperCase()) {
      case 'SMS':
        return <Smartphone className="w-3.5 h-3.5 text-blue-600" />;
      case 'EMAIL':
      case 'GMAIL':
        return <Mail className="w-3.5 h-3.5 text-red-600" />;
      case 'WEBHOOK':
        return <Globe className="w-3.5 h-3.5 text-teal-600" />;
      default:
        return <Cpu className="w-3.5 h-3.5 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Primary Protection Hero Section */}
      <ProtectionHero
        agentStatus={agentStatus}
        onToggleProtection={onToggleProtection}
        loadingToggle={loadingToggle}
      />

      {/* Real-Time Browser Extension Companion Banner */}
      <BrowserExtensionCard />

      {/* Main KPI Statistics with Date Filter */}
      <MetricCards
        stats={agentStatus}
        dateRange={dateRange}
        onDateRangeChange={onDateRangeChange}
      />

      {/* Gmail Input & Inbound Safety Inspector */}
      <GmailConnectorCard
        onMessageAnalyzed={onMessageAnalyzed}
        onOpenDetail={onViewAnalysis}
      />

      {/* Visual Image & QR / Quishing Inspector */}
      <ImageInspectorCard
        onMessageAnalyzed={onMessageAnalyzed}
        onOpenDetail={onViewAnalysis}
      />

      {/* Quick Interactive Simulator Trigger Bar */}
      <SimulatorQuickBar
        onTriggerScenario={onTriggerScenario}
        isSimulating={isSimulating}
      />

      {/* 2-Column Split: Recent Threats & Live Protection Activity Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Threats Card */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-red-600" />
              <h3 className="text-xs sm:text-sm font-bold tracking-wide text-slate-900 uppercase">
                Recent Threats Flagged
              </h3>
            </div>
            <button
              onClick={onNavigateHistory}
              className="text-xs text-teal-700 hover:text-teal-800 font-semibold flex items-center space-x-1 cursor-pointer"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="mt-3.5 space-y-3 flex-1">
            {threatsOnly.length > 0 ? (
              threatsOnly.slice(0, 4).map((threat) => {
                const isHigh = threat.risk_level === 'HIGH';
                return (
                  <div
                    key={threat.id}
                    onClick={() => onViewAnalysis(threat)}
                    className="p-3.5 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200 transition-all cursor-pointer shadow-2xs hover:shadow-xs"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center space-x-2">
                        {getSourceIcon(threat.source)}
                        <span className="text-xs font-bold text-slate-800 truncate max-w-[160px] sm:max-w-xs">
                          {threat.sender}
                        </span>
                      </div>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        isHigh
                          ? 'bg-red-50 text-red-700 border-red-200'
                          : 'bg-amber-50 text-amber-700 border-amber-200'
                      }`}>
                        {isHigh ? 'HIGH RISK' : 'SUSPICIOUS'} • {threat.risk_score}/100
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 line-clamp-1 italic">
                      "{threat.content_preview}"
                    </p>

                    <div className="mt-2 flex items-center justify-between text-[11px] text-slate-500 pt-1.5 border-t border-slate-200/60">
                      <span className="truncate max-w-[200px]">
                        Category: <strong className="text-slate-700">{threat.category}</strong>
                      </span>
                      <span className="flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>{threat.timestamp}</span>
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="h-full flex flex-col items-center justify-center py-8 text-center text-slate-400">
                <ShieldCheck className="w-10 h-10 text-teal-600/40 mb-2" />
                <span className="text-xs font-semibold text-slate-700">No active threats detected</span>
                <span className="text-[11px] text-slate-500 mt-0.5">Your incoming message stream is clean</span>
              </div>
            )}
          </div>
        </div>

        {/* Real-time Activity Timeline */}
        <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-xs flex flex-col">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-teal-700" />
              <h3 className="text-xs sm:text-sm font-bold tracking-wide text-slate-900 uppercase">
                Activity Stream
              </h3>
            </div>
            <span className="text-[11px] font-medium text-slate-500">Live Inspection Log</span>
          </div>

          <div className="mt-3.5 space-y-3 flex-1 overflow-y-auto max-h-[380px]">
            {recentAnalyses && recentAnalyses.length > 0 ? (
              recentAnalyses.slice(0, 5).map((item) => {
                const isSafe = item.risk_level === 'LOW';
                const isHigh = item.risk_level === 'HIGH';
                return (
                  <div
                    key={item.id}
                    onClick={() => onViewAnalysis(item)}
                    className="p-3 rounded-xl bg-slate-50 hover:bg-slate-100/80 border border-slate-200 transition-colors cursor-pointer flex items-center justify-between gap-3 shadow-2xs"
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <div className={`p-2 rounded-lg border ${
                        isSafe
                          ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                          : isHigh
                          ? 'bg-red-50 border-red-200 text-red-700'
                          : 'bg-amber-50 border-amber-200 text-amber-700'
                      }`}>
                        {isSafe ? (
                          <ShieldCheck className="w-4 h-4" />
                        ) : isHigh ? (
                          <AlertOctagon className="w-4 h-4" />
                        ) : (
                          <AlertTriangle className="w-4 h-4" />
                        )}
                      </div>
                      <div className="truncate">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-800 truncate">
                            {item.sender}
                          </span>
                          <span className="text-[10px] text-slate-500">
                            via {item.source}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-600 truncate">
                          {item.summary || item.content_preview}
                        </p>
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <span className={`text-xs font-bold block ${
                        isSafe
                          ? 'text-emerald-700'
                          : isHigh
                          ? 'text-red-600'
                          : 'text-amber-600'
                      }`}>
                        {item.risk_score}/100
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {item.timestamp}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="h-full flex flex-col items-center justify-center py-8 text-center text-slate-400">
                <Clock className="w-10 h-10 text-slate-300 mb-2" />
                <span className="text-xs font-semibold text-slate-700">No activity logged yet</span>
                <span className="text-[11px] text-slate-500 mt-0.5">Simulate a message or connect Gmail</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

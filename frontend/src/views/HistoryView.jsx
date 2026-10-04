import React, { useState, useEffect, useMemo } from 'react';
import { FixedSizeList } from 'react-window';
import {
  History,
  Search,
  Trash2,
  Eye,
  Clock,
  Smartphone,
  Mail,
  Cpu,
  Globe,
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';

export default function HistoryView({
  history,
  onFilterRisk,
  activeRiskFilter,
  searchTerm,
  setSearchTerm,
  onDeleteEntry,
  onClearHistory,
  onViewAnalysis,
  loading,
}) {
  const [confirmClear, setConfirmClear] = useState(false);

  // Risk filter tabs
  const filterTabs = [
    { id: 'ALL', label: 'All Messages' },
    { id: 'HIGH', label: '🔴 High Risk' },
    { id: 'SUSPICIOUS', label: '🟡 Suspicious' },
    { id: 'LOW', label: '🟢 Low Risk' },
  ];

  // Debounced search term to avoid excessive recomputation
  const [debouncedTerm, setDebouncedTerm] = useState(searchTerm);
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedTerm(searchTerm), 300);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  // Memoized filtered list
  const filteredHistory = useMemo(() => {
    let list = history || [];
    if (activeRiskFilter && activeRiskFilter !== 'ALL') {
      list = list.filter((item) => item.risk_level === activeRiskFilter);
    }
    if (debouncedTerm && debouncedTerm.trim()) {
      const term = debouncedTerm.toLowerCase().trim();
      list = list.filter((item) =>
        (item.sender && item.sender.toLowerCase().includes(term)) ||
        (item.content_preview && item.content_preview.toLowerCase().includes(term)) ||
        (item.summary && item.summary.toLowerCase().includes(term)) ||
        (item.category && item.category.toLowerCase().includes(term))
      );
    }
    return list;
  }, [history, activeRiskFilter, debouncedTerm]);

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

  // Row renderer for react-window (memoized)
  const Row = React.memo(({ index, style }) => {
    const item = filteredHistory[index];
    const isSafe = item.risk_level === 'LOW';
    const isHigh = item.risk_level === 'HIGH';
    const badgeBorder = isHigh ? 'border-red-200' : isSafe ? 'border-emerald-200' : 'border-amber-200';
    const badgeBg = isHigh ? 'bg-red-50 text-red-700' : isSafe ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700';
    return (
      <div style={style} className="p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 shadow-xs transition-all">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start space-x-3 truncate">
            <div className="mt-1">
              {isSafe ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              ) : isHigh ? (
                <AlertOctagon className="w-5 h-5 text-red-600" />
              ) : (
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              )}
            </div>
            <div className="truncate">
              <div className="flex items-center space-x-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeBorder} ${badgeBg}`}>
                  {item.risk_level} • {item.risk_score}/100
                </span>
                <div className="flex items-center space-x-1 text-xs text-slate-500 font-medium">
                  {getSourceIcon(item.source)}
                  <span>{item.source}</span>
                </div>
              </div>
              <h3 className="mt-1 text-sm font-semibold text-slate-900 truncate">{item.sender}</h3>
              <p className="text-xs text-slate-600 truncate mt-0.5 font-mono">"{item.content_preview}"</p>
              <div className="mt-2 flex items-center space-x-4 text-[11px] text-slate-500">
                <span className="flex items-center space-x-1"><Clock className="w-3 h-3" /><span>{item.timestamp}</span></span>
                <span>Category: <strong className="text-slate-700">{item.category}</strong></span>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2 self-end sm:self-center shrink-0">
            <button onClick={() => onViewAnalysis(item)} className="px-3 py-1.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold flex items-center space-x-1 shadow-xs transition-colors cursor-pointer">
              <Eye className="w-3.5 h-3.5" /><span>Report</span>
            </button>
            {onDeleteEntry && (
              <button onClick={() => onDeleteEntry(item.id)} className="p-1.5 rounded-xl text-slate-400 hover:text-red-600 hover:bg-red-50 border border-slate-200 transition-colors cursor-pointer" title="Delete log entry">
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    );
  });

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-700">
              <History className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">Protection History</h2>
              <p className="text-xs text-slate-500">Audit trail of incoming messages checked by ScamShield under your tenancy</p>
            </div>
          </div>

          {/* Clear History Action */}
          <div>
            {!confirmClear ? (
              <button onClick={() => setConfirmClear(true)} className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-red-600 hover:text-red-700 hover:bg-red-50 border border-red-200 transition-colors cursor-pointer">
                <Trash2 className="w-3.5 h-3.5" />
                <span>Purge My History</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                <span className="text-xs text-red-600 font-semibold">Delete personal logs?</span>
                <button onClick={() => { onClearHistory(); setConfirmClear(false); }} className="px-2.5 py-1 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-bold cursor-pointer">Confirm</button>
                <button onClick={() => setConfirmClear(false)} className="px-2 py-1 rounded-lg bg-slate-100 text-slate-600 text-xs font-semibold cursor-pointer">Cancel</button>
              </div>
            )}
          </div>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-2">
          {/* Risk Level Filter Tabs */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200 overflow-x-auto">
            {filterTabs.map((tab) => (
              <button key={tab.id} onClick={() => onFilterRisk(tab.id)} className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap cursor-pointer ${activeRiskFilter === tab.id ? 'bg-white text-teal-800 shadow-xs border border-slate-200' : 'text-slate-600 hover:text-slate-900'}`}>
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
            <input type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search sender, keyword, url..." className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-teal-600 focus:bg-white transition-colors" />
          </div>
        </div>
      </div>

      {/* History List */}
      <div className="space-y-3">
        {filteredHistory.length > 0 ? (
          <FixedSizeList height={600} itemCount={filteredHistory.length} itemSize={140} width="100%">
            {Row}
          </FixedSizeList>
        ) : (
          <div className="py-16 text-center rounded-2xl bg-white border border-slate-200">
            <History className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-800">No records found</h3>
            <p className="text-xs text-slate-500 mt-1">Try changing filters or simulate a test message.</p>
          </div>
        )}
      </div>
    </div>
  );
}

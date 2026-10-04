import React from 'react';
import { MailCheck, ShieldAlert, AlertTriangle, AlertOctagon, Calendar } from 'lucide-react';

export default function MetricCards({ stats, dateRange = 'all', onDateRangeChange }) {
  const cards = [
    {
      title: 'Messages Checked',
      value: stats?.messages_checked ?? 0,
      label: 'Proactively analyzed',
      icon: MailCheck,
      color: 'text-teal-700',
      badgeBg: 'bg-teal-50 text-teal-700 border-teal-200',
      bgHover: 'hover:border-teal-300',
    },
    {
      title: 'Threats Detected',
      value: stats?.threats_detected ?? 0,
      label: 'Flagged interactions',
      icon: ShieldAlert,
      color: 'text-amber-600',
      badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
      bgHover: 'hover:border-amber-300',
    },
    {
      title: 'High Risk Threats',
      value: stats?.high_risk_count ?? 0,
      label: 'Urgent scams blocked',
      icon: AlertOctagon,
      color: 'text-red-600',
      badgeBg: 'bg-red-50 text-red-700 border-red-200',
      bgHover: 'hover:border-red-300',
    },
    {
      title: 'Suspicious Notices',
      value: stats?.suspicious_count ?? 0,
      label: 'Verification recommended',
      icon: AlertTriangle,
      color: 'text-amber-500',
      badgeBg: 'bg-amber-50 text-amber-700 border-amber-200',
      bgHover: 'hover:border-amber-300',
    },
  ];

  return (
    <div className="space-y-3">
      {/* Date Filter Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-medium">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>Real-Time Threat Analytics</span>
        </div>
        <div className="flex items-center space-x-1 bg-slate-100 p-0.5 rounded-lg border border-slate-200 text-xs">
          {[
            { id: 'today', label: 'Today' },
            { id: '7days', label: '7 Days' },
            { id: '30days', label: '30 Days' },
            { id: 'all', label: 'All Time' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => onDateRangeChange && onDateRangeChange(item.id)}
              className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                dateRange === item.id
                  ? 'bg-white text-teal-800 shadow-xs border border-slate-200/80 font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* 4 Clean Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className={`p-4 sm:p-5 rounded-2xl bg-white border border-slate-200 shadow-xs transition-all hover:shadow-md hover:-translate-y-0.5 ${card.bgHover}`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm font-semibold text-slate-700">
                  {card.title}
                </span>
                <div className={`p-2 rounded-xl border ${card.badgeBg}`}>
                  <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
                </div>
              </div>
              <div className="mt-2 flex items-baseline space-x-2">
                <span className={`text-2xl sm:text-3xl font-bold tracking-tight ${card.color}`}>
                  {card.value.toLocaleString()}
                </span>
              </div>
              <p className="mt-1 text-[11px] text-slate-500">
                {card.label}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

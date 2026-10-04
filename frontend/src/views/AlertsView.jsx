import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, AlertOctagon, CheckCheck, Eye, Clock, CheckCircle } from 'lucide-react';

export default function AlertsView({ alerts, onMarkRead, onMarkAllRead, onViewAnalysis }) {
  const [filterUnread, setFilterUnread] = useState(false);

  const displayedAlerts = filterUnread ? alerts.filter((a) => !a.is_read) : alerts;
  const unreadTotal = alerts.filter((a) => !a.is_read).length;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-white border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-red-50 border border-red-200 text-red-600">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                Security Alert Center
              </h2>
              <p className="text-xs text-slate-500">
                Prioritized warnings and adaptive alerts for suspicious incoming messages
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setFilterUnread(!filterUnread)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold border transition-colors cursor-pointer ${
              filterUnread
                ? 'bg-teal-50 border-teal-300 text-teal-800'
                : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
            }`}
          >
            {filterUnread ? 'Showing Unread Only' : 'Show All Alerts'}
          </button>

          {unreadTotal > 0 && (
            <button
              onClick={onMarkAllRead}
              className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-white hover:bg-slate-50 text-slate-700 transition-colors border border-slate-200 shadow-xs cursor-pointer"
            >
              <CheckCheck className="w-3.5 h-3.5 text-teal-700" />
              <span>Mark All Read</span>
            </button>
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {displayedAlerts.length > 0 ? (
          displayedAlerts.map((alert) => {
            const isHigh = alert.risk_level === 'HIGH';
            const riskBorder = isHigh ? 'border-red-200' : 'border-amber-200';
            const badgeBg = isHigh ? 'bg-red-50 text-red-700 border-red-200' : 'bg-amber-50 text-amber-700 border-amber-200';

            return (
              <div
                key={alert.id}
                className={`p-5 rounded-2xl bg-white border ${riskBorder} transition-all shadow-xs ${
                  !alert.is_read ? 'ring-2 ring-red-400/20' : 'opacity-90'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="flex items-start space-x-3">
                    <div className="mt-1">
                      {isHigh ? (
                        <AlertOctagon className="w-5 h-5 text-red-600" />
                      ) : (
                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${badgeBg}`}>
                          {isHigh ? '🔴 HIGH RISK' : '🟡 SUSPICIOUS'}
                        </span>
                        <span className="text-xs font-semibold text-slate-600">
                          {alert.category?.replace('_', ' ')}
                        </span>
                        {!alert.is_read && (
                          <span className="text-[10px] font-bold px-1.5 py-0.2 bg-teal-600 text-white rounded-full">
                            NEW
                          </span>
                        )}
                      </div>

                      <h3 className="mt-1.5 text-sm font-semibold text-slate-900 leading-snug">
                        {alert.summary}
                      </h3>

                      <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span>Sender: <strong className="text-slate-800">{alert.sender}</strong></span>
                        <span>•</span>
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3.5 h-3.5" />
                          <span>{alert.timestamp}</span>
                        </span>
                        <span>•</span>
                        <span>Score: <strong className={isHigh ? 'text-red-600' : 'text-amber-600'}>{alert.risk_score}/100</strong></span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 self-end sm:self-center">
                    {!alert.is_read && (
                      <button
                        onClick={() => onMarkRead(alert.id)}
                        className="p-2 rounded-xl text-slate-500 hover:text-teal-700 hover:bg-teal-50 border border-slate-200 transition-colors cursor-pointer"
                        title="Mark as read"
                      >
                        <CheckCircle className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => onViewAnalysis(alert)}
                      className="px-3 py-1.5 rounded-xl bg-teal-700 hover:bg-teal-800 text-white text-xs font-semibold flex items-center space-x-1 shadow-xs transition-colors cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Details</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="py-16 text-center rounded-2xl bg-white border border-slate-200">
            <CheckCircle className="w-12 h-12 text-teal-600 mx-auto mb-3" />
            <h3 className="text-base font-bold text-slate-800">All clear</h3>
            <p className="text-xs text-slate-500 mt-1">No security alerts at this time.</p>
          </div>
        )}
      </div>
    </div>
  );
}

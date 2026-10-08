import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  X,
  ExternalLink,
  Smartphone,
  Mail,
  MessageSquare,
  Globe,
  BellRing,
} from 'lucide-react';

export default function MobileHeadsUpNotification({ notification, onClose, onInspect }) {
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (!notification) return;

    // Haptic vibration feedback on mobile
    if ('vibrate' in navigator) {
      try {
        if (notification.risk_level === 'HIGH') {
          navigator.vibrate([200, 80, 200]);
        } else if (notification.risk_level === 'SUSPICIOUS') {
          navigator.vibrate([120]);
        }
      } catch (e) {}
    }

    // Auto-dismiss countdown progress bar (8 seconds)
    const duration = 8000;
    const intervalTime = 100;
    const step = (intervalTime / duration) * 100;

    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev <= step) {
          clearInterval(timer);
          onClose();
          return 0;
        }
        return prev - step;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [notification, onClose]);

  if (!notification) return null;

  const isHigh = notification.risk_level === 'HIGH';
  const isSuspicious = notification.risk_level === 'SUSPICIOUS';
  const isSafe = !isHigh && !isSuspicious;

  const senderText = notification.sender || 'Unknown Sender';
  const isWhatsApp =
    senderText.toLowerCase().includes('whatsapp') ||
    notification.source === 'WHATSAPP' ||
    notification.source === 'MESSAGING_API';
  const isSMS = notification.source === 'SMS' || (!isWhatsApp && /^\+?\d+/.test(senderText));
  const isEmail = notification.source === 'GMAIL' || notification.source === 'EMAIL';

  const getChannelBadge = () => {
    if (isWhatsApp) {
      return {
        label: 'WhatsApp Message',
        icon: <MessageSquare className="w-3.5 h-3.5 text-emerald-600" />,
        bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      };
    }
    if (isSMS) {
      return {
        label: 'Incoming SMS',
        icon: <Smartphone className="w-3.5 h-3.5 text-blue-600" />,
        bg: 'bg-blue-50 text-blue-800 border-blue-200',
      };
    }
    if (isEmail) {
      return {
        label: 'Gmail Inbox',
        icon: <Mail className="w-3.5 h-3.5 text-red-600" />,
        bg: 'bg-red-50 text-red-800 border-red-200',
      };
    }
    return {
      label: 'Security Stream',
      icon: <Globe className="w-3.5 h-3.5 text-teal-600" />,
      bg: 'bg-teal-50 text-teal-800 border-teal-200',
    };
  };

  const channel = getChannelBadge();

  return (
    <div className="fixed top-3 left-3 right-3 sm:left-auto sm:right-6 sm:w-105 z-50 pointer-events-auto">
      <div
        className={`rounded-2xl border shadow-2xl backdrop-blur-md overflow-hidden transition-all duration-300 transform translate-y-0 ${
          isHigh
            ? 'bg-white border-red-400 ring-2 ring-red-400/20 shadow-red-500/10'
            : isSuspicious
            ? 'bg-white border-amber-400 ring-2 ring-amber-400/20 shadow-amber-500/10'
            : 'bg-white border-emerald-300 shadow-slate-300/40'
        }`}
      >
        {/* Top Progress countdown line */}
        <div className="w-full bg-slate-100 h-1">
          <div
            className={`h-full transition-all duration-100 ${
              isHigh ? 'bg-red-500' : isSuspicious ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="p-3.5 sm:p-4">
          {/* Header Row: Channel Tag & Risk Pill */}
          <div className="flex items-center justify-between gap-2 mb-2">
            <div className="flex items-center space-x-2">
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${channel.bg}`}
              >
                {channel.icon}
                <span>{channel.label}</span>
              </span>
              <span className="text-[11px] text-slate-400">Just now</span>
            </div>

            <div className="flex items-center space-x-1.5">
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold border ${
                  isHigh
                    ? 'bg-red-50 text-red-700 border-red-200 animate-pulse'
                    : isSuspicious
                    ? 'bg-amber-50 text-amber-700 border-amber-200'
                    : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                }`}
              >
                {isHigh ? (
                  <ShieldAlert className="w-3.5 h-3.5" />
                ) : isSuspicious ? (
                  <AlertTriangle className="w-3.5 h-3.5" />
                ) : (
                  <ShieldCheck className="w-3.5 h-3.5" />
                )}
                <span>
                  {isHigh
                    ? `HIGH RISK (${notification.risk_score}%)`
                    : isSuspicious
                    ? `SUSPICIOUS (${notification.risk_score}%)`
                    : 'SAFE'}
                </span>
              </span>

              <button
                onClick={onClose}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Sender & Message Preview */}
          <div className="flex items-start gap-3">
            <div
              className={`p-2 rounded-xl shrink-0 mt-0.5 ${
                isHigh ? 'bg-red-100 text-red-600' : isSuspicious ? 'bg-amber-100 text-amber-600' : 'bg-emerald-100 text-emerald-600'
              }`}
            >
              <BellRing className="w-4 h-4" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-slate-900 truncate">
                {notification.sender}
              </p>
              <p className="text-xs text-slate-600 line-clamp-2 mt-0.5 leading-relaxed font-sans">
                {notification.content_preview || notification.summary}
              </p>
            </div>
          </div>

          {/* Footer Action Bar */}
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between">
            <span className="text-[11px] text-slate-500 font-medium">
              Proactive AI Agent Intercept
            </span>
            <button
              onClick={() => {
                onInspect(notification);
                onClose();
              }}
              className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-bold transition-all shadow-xs cursor-pointer ${
                isHigh
                  ? 'bg-red-600 hover:bg-red-700 text-white'
                  : isSuspicious
                  ? 'bg-amber-600 hover:bg-amber-700 text-white'
                  : 'bg-teal-700 hover:bg-teal-800 text-white'
              }`}
            >
              <span>Audit Threat Breakdown</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

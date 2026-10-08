import React, { useState } from 'react';
import {
  Smartphone,
  Mail,
  MessageSquare,
  Globe,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Lock,
  Shield,
  Send,
  Loader2,
  Sparkles,
  Info,
} from 'lucide-react';
import GmailConnectorCard from '../components/GmailConnectorCard';
import MobileIngestionCard from '../components/MobileIngestionCard';

export default function SourcesView({
  sources,
  onConnectSource,
  onDisconnectSource,
  onSendCustomMessage,
  isSendingCustom,
  onMessageAnalyzed,
  onViewAnalysis,
  onTriggerScenario,
}) {
  const [customSender, setCustomSender] = useState('SBI-ALERT');
  const [customChannel, setCustomChannel] = useState('SMS');
  const [customText, setCustomText] = useState(
    'Dear Customer, Your account KYC expires today. Verify immediately at http://secure-sbi-portal.top/kyc or your card will be deactivated within 12 hours.'
  );

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (!customText.trim()) return;
    onSendCustomMessage({
      source: customChannel,
      sender: customSender.trim() || 'Simulated Sender',
      content: customText.trim(),
    });
  };

  const getSourceIcon = (iconName) => {
    switch (iconName) {
      case 'smartphone':
        return <Smartphone className="w-5 h-5 text-blue-600" />;
      case 'mail':
        return <Mail className="w-5 h-5 text-red-600" />;
      case 'message-square':
        return <MessageSquare className="w-5 h-5 text-amber-600" />;
      case 'globe':
        return <Globe className="w-5 h-5 text-teal-600" />;
      default:
        return <Cpu className="w-5 h-5 text-slate-600" />;
    }
  };

  return (
    <div className="space-y-8">
      {/* Featured Mobile Interception Hub (SMS, WhatsApp, Gmail) */}
      <MobileIngestionCard
        onTriggerMobileSimulation={onTriggerScenario}
      />

      {/* Featured Gmail Inspector Card */}
      <GmailConnectorCard
        onMessageAnalyzed={onMessageAnalyzed}
        onOpenDetail={onViewAnalysis}
      />

      {/* Top Section: Connected Sources Management */}
      <div>
        <div className="mb-4">
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            Connected Message Sources
          </h2>
          <p className="text-xs text-slate-500">
            ScamShield monitors incoming messages from authorized channels. Direct private messaging apps require explicit permission.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sources.map((source) => {
            const isConnected = source.status === 'CONNECTED';
            const isRestricted = source.status === 'RESTRICTED';

            return (
              <div
                key={source.id}
                className={`p-5 rounded-2xl border transition-all flex flex-col justify-between shadow-xs ${
                  isConnected
                    ? 'bg-white border-slate-200'
                    : isRestricted
                    ? 'bg-amber-50/40 border-amber-200'
                    : 'bg-slate-50 border-slate-200'
                }`}
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-200">
                      {getSourceIcon(source.icon)}
                    </div>
                    <span
                      className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                        isConnected
                          ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                          : isRestricted
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-slate-100 text-slate-600 border-slate-300'
                      }`}
                    >
                      {isConnected ? '● ACTIVE' : isRestricted ? '⚠️ RESTRICTED' : '○ DISABLED'}
                    </span>
                  </div>

                  <h3 className="mt-3 text-sm font-bold text-slate-900">
                    {source.name}
                  </h3>
                  <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                    {source.description}
                  </p>

                  {source.permission_info && (
                    <div className="mt-3 p-2 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-600 flex items-start space-x-1.5">
                      <Info className="w-3.5 h-3.5 text-teal-700 shrink-0 mt-0.5" />
                      <span>{source.permission_info}</span>
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="text-slate-500">
                    Checked: <strong className="text-slate-700">{source.message_count || 0}</strong>
                  </span>

                  {isConnected ? (
                    <button
                      onClick={() => onDisconnectSource(source.id)}
                      className="px-2.5 py-1 text-xs font-semibold text-slate-500 hover:text-red-600 transition-colors cursor-pointer"
                    >
                      Disable
                    </button>
                  ) : isRestricted ? (
                    <span className="text-[10px] font-bold text-amber-700 uppercase bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                      Requires Approval
                    </span>
                  ) : (
                    <button
                      onClick={() => onConnectSource(source.id)}
                      className="px-3 py-1 bg-teal-700 hover:bg-teal-800 text-white rounded-lg text-xs font-semibold transition-colors shadow-xs cursor-pointer"
                    >
                      Enable
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Manual Ingestion Simulator Card */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-700">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Custom Inbound Payload Simulator
            </h2>
            <p className="text-xs text-slate-500">
              Inject custom message payloads to test proactive AI classification and URL detection
            </p>
          </div>
        </div>

        <form onSubmit={handleCustomSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Source Channel
              </label>
              <select
                value={customChannel}
                onChange={(e) => setCustomChannel(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:border-teal-600 focus:bg-white transition-colors"
              >
                <option value="WHATSAPP">WhatsApp (Messaging Bridge)</option>
                <option value="SMS">SMS (Android Bridge)</option>
                <option value="EMAIL">Inbound Email</option>
                <option value="WEBHOOK">External Ingestion Webhook</option>
                <option value="DEMO">Simulator Stream</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Sender Header
              </label>
              <input
                type="text"
                value={customSender}
                onChange={(e) => setCustomSender(e.target.value)}
                placeholder="e.g., SBI-ALERT, Amazon Support"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:border-teal-600 focus:bg-white transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Message Content (Include links to test URL analyzer)
            </label>
            <textarea
              rows={3}
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              placeholder="Write or paste message to simulate..."
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs sm:text-sm text-slate-800 focus:outline-none focus:border-teal-600 focus:bg-white font-mono leading-relaxed transition-colors"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSendingCustom}
              className="px-5 py-2.5 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white font-semibold rounded-xl text-xs sm:text-sm transition-colors shadow-xs flex items-center space-x-2 cursor-pointer"
            >
              {isSendingCustom ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span>{isSendingCustom ? 'Injecting Message...' : 'Simulate Inbound Delivery'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

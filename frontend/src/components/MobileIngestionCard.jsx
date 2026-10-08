import React, { useState } from 'react';
import {
  Smartphone,
  MessageSquare,
  Mail,
  Share2,
  Copy,
  Check,
  Zap,
  ShieldAlert,
  Download,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
  Shield,
  Layers,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

export default function MobileIngestionCard({ onTriggerMobileSimulation }) {
  const [activeTab, setActiveTab] = useState('FORWARDER');
  const [copiedWebhook, setCopiedWebhook] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const webhookEndpoint = `${window.location.origin}/api/webhook`;

  const handleCopyWebhook = () => {
    navigator.clipboard.writeText(webhookEndpoint);
    setCopiedWebhook(true);
    setTimeout(() => setCopiedWebhook(false), 2000);
  };

  return (
    <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-5 border-b border-slate-100">
        <div className="flex items-start space-x-3.5">
          <div className="p-3 rounded-2xl bg-teal-50 border border-teal-200 text-teal-700 shrink-0">
            <Smartphone className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Mobile Live Interception Hub (SMS, WhatsApp & Gmail)
              </h2>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                Active Architecture
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl leading-relaxed">
              How ScamShield proactively intercepts and audits messages received on your phone while respecting mobile OS sandbox security.
            </p>
          </div>
        </div>

        {/* 1-Click Simulation Triggers */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => onTriggerMobileSimulation('WHATSAPP_FAMILY_IMPERSONATION')}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-semibold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 transition-colors shadow-xs cursor-pointer"
          >
            <MessageSquare className="w-3.5 h-3.5 text-emerald-600" />
            <span>Test WhatsApp Scam</span>
          </button>
          <button
            onClick={() => onTriggerMobileSimulation('FAKE_KYC')}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-xl text-xs font-semibold bg-red-50 hover:bg-red-100 text-red-800 border border-red-200 transition-colors shadow-xs cursor-pointer"
          >
            <Smartphone className="w-3.5 h-3.5 text-red-600" />
            <span>Test SMS Phish</span>
          </button>
        </div>
      </div>

      {/* Architecture Tabs */}
      <div className="flex border-b border-slate-100 overflow-x-auto gap-2">
        <button
          onClick={() => setActiveTab('FORWARDER')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors cursor-pointer ${
            activeTab === 'FORWARDER'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Zap className="w-4 h-4 text-amber-500" />
          <span>1. Android Auto-Forwarder (Webhook)</span>
        </button>

        <button
          onClick={() => setActiveTab('PWA')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors cursor-pointer ${
            activeTab === 'PWA'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Share2 className="w-4 h-4 text-blue-500" />
          <span>2. Native Mobile Share Sheet (PWA)</span>
        </button>

        <button
          onClick={() => setActiveTab('GMAIL')}
          className={`pb-3 px-3 text-xs sm:text-sm font-bold flex items-center space-x-2 border-b-2 transition-colors cursor-pointer ${
            activeTab === 'GMAIL'
              ? 'border-teal-700 text-teal-800'
              : 'border-transparent text-slate-500 hover:text-slate-700'
          }`}
        >
          <Mail className="w-4 h-4 text-red-500" />
          <span>3. Cloud Gmail Push API</span>
        </button>
      </div>

      {/* Tab 1: Android Auto Forwarder */}
      {activeTab === 'FORWARDER' && (
        <div className="space-y-4 animate-in fade-in duration-200">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed space-y-2">
            <p className="font-semibold text-slate-900 flex items-center gap-1.5">
              <span>Why an automated bridge is needed on mobile:</span>
            </p>
            <p>
              Mobile operating systems (Android & iOS) protect user privacy by sandboxing apps. Web browsers cannot silently access your private SMS inbox or WhatsApp database without explicit OS permissions.
            </p>
            <p>
              By using Android's native <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-teal-800 font-mono">NotificationListenerService</code> (via companion apps or tools like <strong>MacroDroid</strong>, <strong>Tasker</strong>, or <strong>SMS Forwarder</strong>), every incoming WhatsApp message, SMS, or banking alert is automatically forwarded to ScamShield's secure webhook in real-time.
            </p>
          </div>

          {/* Webhook Configuration Box */}
          <div className="p-4 rounded-xl bg-white border border-slate-200 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <span className="text-xs font-bold text-slate-800">
                Your Private Webhook Receiver URL:
              </span>
              <button
                onClick={handleCopyWebhook}
                className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-teal-50 hover:bg-teal-100 text-teal-800 border border-teal-200 transition-colors cursor-pointer w-fit"
              >
                {copiedWebhook ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedWebhook ? 'Copied to Clipboard!' : 'Copy Webhook URL'}</span>
              </button>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900 text-slate-200 font-mono text-xs break-all select-all">
              {webhookEndpoint}
            </div>

            <div className="pt-2">
              <button
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="text-xs text-teal-700 font-semibold hover:underline flex items-center space-x-1"
              >
                <span>{showTechnicalDetails ? 'Hide' : 'Show'} Sample Android Webhook Payload Format</span>
                {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showTechnicalDetails && (
                <pre className="mt-2 p-3 bg-slate-50 border border-slate-200 rounded-lg text-[11px] font-mono text-slate-800 overflow-x-auto">
{`POST ${webhookEndpoint}
Content-Type: application/json

{
  "source": "WHATSAPP",
  "sender": "+91-91234-56789",
  "content": "Hi Mom, my phone fell in water. Need urgent ₹15,000 for fees..."
}`}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: PWA Web Share Target */}
      {activeTab === 'PWA' && (
        <div className="space-y-4 animate-in fade-in duration-200">
          <div className="p-4 rounded-xl bg-blue-50/50 border border-blue-200 text-xs text-slate-700 leading-relaxed space-y-2">
            <p className="font-semibold text-slate-900">
              Zero-Setup Mobile Protection with Web Share Target API:
            </p>
            <p>
              ScamShield is configured as a full <strong>Progressive Web App (PWA)</strong> with the W3C Web Share Target API. Once installed to your mobile home screen, ScamShield appears directly in your phone's native <strong>"Share" menu</strong>!
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Android Instructions */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Smartphone className="w-4 h-4 text-emerald-600" />
                <span>On Android (Chrome / Brave / Edge)</span>
              </h3>
              <ol className="text-xs text-slate-600 space-y-1.5 list-decimal pl-4">
                <li>Open ScamShield in mobile Chrome.</li>
                <li>Tap the <strong>three dots (⋮)</strong> menu in the top-right.</li>
                <li>Tap <strong>"Install app"</strong> or <strong>"Add to Home screen"</strong>.</li>
                <li>When you see any suspicious WhatsApp message or SMS, highlight it and tap <strong>Share ➔ ScamShield</strong> for an instant audit!</li>
              </ol>
            </div>

            {/* iOS Instructions */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <h3 className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Smartphone className="w-4 h-4 text-blue-600" />
                <span>On iPhone (Safari)</span>
              </h3>
              <ol className="text-xs text-slate-600 space-y-1.5 list-decimal pl-4">
                <li>Open ScamShield in mobile Safari.</li>
                <li>Tap the <strong>Share icon (square with arrow ↑)</strong> at the bottom.</li>
                <li>Scroll down and tap <strong>"Add to Home Screen"</strong>.</li>
                <li>ScamShield now runs in full-screen standalone mode with haptic buzz and sound alerts.</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Cloud Gmail Sync */}
      {activeTab === 'GMAIL' && (
        <div className="space-y-4 animate-in fade-in duration-200">
          <div className="p-4 rounded-xl bg-red-50/50 border border-red-200 text-xs text-slate-700 leading-relaxed space-y-2">
            <p className="font-semibold text-slate-900">
              Official Google Cloud Ingestion:
            </p>
            <p>
              For Gmail, ScamShield does not need to read your phone's local storage. Using official Google OAuth and the Gmail API, ScamShield monitors incoming emails in the cloud, checks links with sandbox telemetry, and fires a push notification to your phone the second a phishing attack is detected.
            </p>
          </div>
        </div>
      )}

      {/* Footer Alert Capabilities Info */}
      <div className="p-4 rounded-xl bg-teal-50/50 border border-teal-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2.5">
          <Shield className="w-4 h-4 text-teal-700 shrink-0" />
          <span className="text-slate-700 font-medium">
            <strong>Mobile Alert Engine:</strong> Enabled with <strong>Vibration Haptics</strong> (buzz patterns), <strong>Audio Siren</strong>, and <strong>Floating Heads-Up Banners</strong>.
          </span>
        </div>
      </div>
    </div>
  );
}

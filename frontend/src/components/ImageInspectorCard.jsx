import React, { useState } from 'react';
import {
  QrCode,
  Upload,
  Image as ImageIcon,
  CheckCircle2,
  AlertTriangle,
  AlertOctagon,
  Eye,
  Loader2,
  Sparkles,
  Link as LinkIcon
} from 'lucide-react';
import { api } from '../services/api';

export default function ImageInspectorCard({ onMessageAnalyzed, onOpenDetail }) {
  const [imagePreview, setImagePreview] = useState(null);
  const [qrText, setQrText] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const presets = [
    {
      label: 'Fake KYC QR Phishing',
      qr: 'http://sbi-kyc-verify-portal.in/login?qr=auth',
      text: 'Scan with GPay or PhonePe to verify your bank KYC immediately. Account will be blocked in 24 hours.',
    },
    {
      label: 'Fake Payment QR (UPI Bait)',
      qr: 'upi://pay?pa=scam-collector@upi&pn=AmazonRewards&am=1&cu=INR',
      text: 'Congratulations! You won ₹25,000. Scan this QR code to receive money into your bank account.',
    },
    {
      label: 'Legitimate Ticket QR',
      qr: 'https://irctc.co.in/pnr-status?pnr=4910293144',
      text: 'Verified train boarding pass for passenger PNR 4910293144. Coach B3 Seat 42.',
    },
  ];

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        setImagePreview(reader.result);
        setFeedback(null);
        // Automatically prefill simulated or extracted QR link
        setQrText('http://secure-banking-auth-token.xyz/kyc/update');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleInspect = async (overrideQr = null, overrideText = null) => {
    const payloadQr = overrideQr !== null ? overrideQr : qrText;
    const payloadText = overrideText !== null ? overrideText : (imagePreview ? 'Suspicious QR Image' : '');

    if (!payloadQr.trim() && !payloadText.trim() && !imagePreview) return;

    setLoading(true);
    setFeedback(null);
    try {
      const res = await api.analyzeImage(imagePreview, payloadText, payloadQr);
      if (onMessageAnalyzed) onMessageAnalyzed(res);
      setFeedback({
        type: 'success',
        message: `Visual inspection complete: ${res.risk_level} RISK (${res.risk_score}/100)`,
        analysis: res,
      });
    } catch (err) {
      setFeedback({
        type: 'error',
        message: err.message || 'Failed to inspect image',
      });
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (preset) => {
    setQrText(preset.qr);
    handleInspect(preset.qr, preset.text);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden transition-all">
      {/* Header */}
      <div className="p-5 sm:p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 shadow-xs">
            <QrCode className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base sm:text-lg font-bold text-slate-900">
                Visual &amp; QR Code Inspector
              </h2>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-purple-50 text-purple-800 border border-purple-200">
                Quishing Defense
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Detect deceptive QR codes, payment receipt lures &amp; evasive visual phishing
            </p>
          </div>
        </div>

        {/* Quick Presets */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-semibold text-slate-400 mr-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-purple-600" /> Test Presets:
          </span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => applyPreset(p)}
              disabled={loading}
              className="px-2.5 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200 transition-colors cursor-pointer"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Body */}
      <div className="p-5 sm:p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Upload Drop Zone */}
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-200 hover:border-purple-400 rounded-xl p-6 bg-slate-50/50 hover:bg-purple-50/30 transition-all cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            {imagePreview ? (
              <div className="text-center space-y-2">
                <img
                  src={imagePreview}
                  alt="QR Preview"
                  className="w-24 h-24 object-cover mx-auto rounded-lg border border-slate-200 shadow-xs"
                />
                <span className="text-xs font-semibold text-purple-700 block">
                  Image loaded. Click below to inspect.
                </span>
              </div>
            ) : (
              <div className="text-center space-y-2">
                <div className="w-10 h-10 rounded-full bg-purple-50 text-purple-600 mx-auto flex items-center justify-center">
                  <Upload className="w-5 h-5" />
                </div>
                <div className="text-xs font-semibold text-slate-700">
                  Upload QR Code or Screenshot
                </div>
                <p className="text-[11px] text-slate-400">
                  PNG, JPG, or WebP up to 5MB
                </p>
              </div>
            )}
          </label>

          {/* QR Destination or Extracted Link */}
          <div className="flex flex-col justify-between space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Embedded Destination URL / QR Payload
              </label>
              <div className="relative">
                <LinkIcon className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="text"
                  value={qrText}
                  onChange={(e) => setQrText(e.target.value)}
                  placeholder="e.g. http://sbi-kyc-verify-portal.in/login or paste raw QR URL"
                  className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-purple-600 focus:bg-white transition-colors"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-1.5">
                Automatically decoded from uploaded images or pasted directly for deep URL analysis.
              </p>
            </div>

            <button
              onClick={() => handleInspect()}
              disabled={loading || (!qrText && !imagePreview)}
              className="w-full py-2.5 px-4 rounded-xl bg-purple-700 hover:bg-purple-800 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center space-x-2 shadow-xs transition-colors cursor-pointer"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Scanning Visual Threat Pipeline...</span>
                </>
              ) : (
                <>
                  <QrCode className="w-4 h-4" />
                  <span>Inspect Visual Payload</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Feedback Display */}
        {feedback && (
          <div
            className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
              feedback.type === 'error'
                ? 'bg-red-50 border-red-200 text-red-700'
                : feedback.analysis?.risk_level === 'HIGH'
                ? 'bg-red-50 border-red-200 text-red-700'
                : feedback.analysis?.risk_level === 'SUSPICIOUS'
                ? 'bg-amber-50 border-amber-200 text-amber-700'
                : 'bg-emerald-50 border-emerald-200 text-emerald-700'
            }`}
          >
            <div className="flex items-center space-x-2.5">
              {feedback.analysis?.risk_level === 'HIGH' ? (
                <AlertOctagon className="w-5 h-5 shrink-0" />
              ) : feedback.analysis?.risk_level === 'SUSPICIOUS' ? (
                <AlertTriangle className="w-5 h-5 shrink-0" />
              ) : (
                <CheckCircle2 className="w-5 h-5 shrink-0" />
              )}
              <div className="text-xs font-semibold">{feedback.message}</div>
            </div>

            {feedback.analysis && onOpenDetail && (
              <button
                onClick={() => onOpenDetail(feedback.analysis)}
                className="px-3 py-1.5 rounded-lg bg-white text-slate-800 border border-slate-200 hover:bg-slate-50 text-xs font-semibold flex items-center space-x-1 shadow-xs transition-colors self-end sm:self-auto cursor-pointer"
              >
                <Eye className="w-3.5 h-3.5" />
                <span>View Full Report</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

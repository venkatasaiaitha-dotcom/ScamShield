import React, { useState, useEffect } from 'react';
import {
  Settings,
  Shield,
  Bell,
  Lock,
  Sliders,
  Trash2,
  CheckCircle,
  Volume2,
  Info,
  Save,
  Loader2,
  Sun,
  Moon,
  Monitor,
  KeyRound,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';

export default function SettingsView({
  settings,
  onSaveSettings,
  onClearHistory,
  currentUser,
  onThemeChange,
}) {
  const [formData, setFormData] = useState({
    appearance: localStorage.getItem('scamshield_theme') || 'light',
    ...settings,
  });

  useEffect(() => {
    if (settings) {
      setFormData((prev) => ({
        ...prev,
        ...settings,
        appearance: localStorage.getItem('scamshield_theme') || settings.appearance || 'light',
      }));
    }
  }, [settings]);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [confirmWipe, setConfirmWipe] = useState(false);
  const [wiping, setWiping] = useState(false);
  const [wipeResult, setWipeResult] = useState('');

  // Password Change State
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwdLoading, setPwdLoading] = useState(false);
  const [pwdFeedback, setPwdFeedback] = useState(null);

  const handleChange = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    if (key === 'appearance' && onThemeChange) {
      onThemeChange(value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSaveSettings(formData);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 2500);
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (!newPassword || newPassword.length < 8) {
      setPwdFeedback({ type: 'error', message: 'New password must be at least 8 characters long.' });
      return;
    }
    setPwdLoading(true);
    setPwdFeedback(null);
    try {
      await api.changePassword(oldPassword, newPassword);
      setPwdFeedback({ type: 'success', message: 'Password updated successfully! Re-hashed with Argon2id.' });
      setOldPassword('');
      setNewPassword('');
    } catch (err) {
      setPwdFeedback({ type: 'error', message: err.message || 'Failed to change password.' });
    } finally {
      setPwdLoading(false);
    }
  };

  const handleAdminWipe = async () => {
    setWiping(true);
    setWipeResult('');
    try {
      const res = await api.wipeAllDataAdmin();
      setWipeResult(res.message || 'All database data wiped successfully.');
      setConfirmWipe(false);
    } catch (err) {
      setWipeResult(`Wipe rejected: ${err.message}`);
    } finally {
      setWiping(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between p-6 rounded-2xl bg-white border border-slate-200 shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-700">
            <Settings className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              System Settings &amp; Privacy Controls
            </h2>
            <p className="text-xs text-slate-500">
              Configure ScamShield AI detection thresholds, appearance, and security policies
            </p>
          </div>
        </div>

        {savedSuccess && (
          <span className="flex items-center space-x-1.5 text-xs text-teal-800 font-semibold px-3 py-1 rounded-xl bg-teal-50 border border-teal-200">
            <CheckCircle className="w-4 h-4" />
            <span>Settings Saved!</span>
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Appearance System (Part 1) */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
          <div>
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-600" />
              <span>Appearance &amp; Theme</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Select your dashboard visual theme. Light mode is the default cybersecurity SaaS theme.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'light', label: 'Light (Default)', icon: Sun },
              { id: 'dark', label: 'Dark', icon: Moon },
              { id: 'system', label: 'System', icon: Monitor },
            ].map((theme) => {
              const Icon = theme.icon;
              const isSelected = (formData.appearance || 'light') === theme.id;
              return (
                <button
                  key={theme.id}
                  type="button"
                  onClick={() => handleChange('appearance', theme.id)}
                  className={`p-3.5 rounded-xl border text-center transition-all cursor-pointer flex flex-col items-center justify-center space-y-2 ${
                    isSelected
                      ? 'bg-teal-50/80 border-teal-600 text-teal-900 font-bold shadow-xs'
                      : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5 text-teal-700" />
                  <span className="text-xs">{theme.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Protection & Detection Preferences */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-teal-700" />
            <span>AI Agent Protection</span>
          </h3>

          <div className="space-y-3">
            <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer">
              <div>
                <span className="text-xs font-semibold text-slate-800 block">
                  Active Protection
                </span>
                <span className="text-[11px] text-slate-500">
                  Continuously inspect incoming messages from connected channels
                </span>
              </div>
              <input
                type="checkbox"
                checked={formData.protection_enabled}
                onChange={(e) => handleChange('protection_enabled', e.target.checked)}
                className="w-4 h-4 accent-teal-700 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer">
              <div>
                <span className="text-xs font-semibold text-slate-800 block">
                  Prominent High-Risk Warning Modals
                </span>
                <span className="text-[11px] text-slate-500">
                  Instantly open focused action guidance when a dangerous scam is detected
                </span>
              </div>
              <input
                type="checkbox"
                checked={formData.auto_alert_high}
                onChange={(e) => handleChange('auto_alert_high', e.target.checked)}
                className="w-4 h-4 accent-teal-700 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer">
              <div>
                <span className="text-xs font-semibold text-slate-800 block">
                  Audible Sound Alerts
                </span>
                <span className="text-[11px] text-slate-500">
                  Play Web Audio chime when high-risk threats arrive
                </span>
              </div>
              <input
                type="checkbox"
                checked={formData.sound_alerts}
                onChange={(e) => handleChange('sound_alerts', e.target.checked)}
                className="w-4 h-4 accent-teal-700 rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50 border border-slate-200 cursor-pointer">
              <div>
                <span className="text-xs font-semibold text-slate-800 block">
                  Privacy-First Minimal Metadata Storage
                </span>
                <span className="text-[11px] text-slate-500">
                  Do not store full message bodies in SQLite; retain only SHA-256 hash previews
                </span>
              </div>
              <input
                type="checkbox"
                checked={formData.privacy_minimal_metadata}
                onChange={(e) => handleChange('privacy_minimal_metadata', e.target.checked)}
                className="w-4 h-4 accent-teal-700 rounded cursor-pointer"
              />
            </label>
          </div>
        </div>

        {/* Risk Threshold Sliders */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <Sliders className="w-4 h-4 text-teal-700" />
            <span>Detection Sensitivity Thresholds</span>
          </h3>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-700">High Risk Threshold</span>
                <span className="font-bold text-red-600 font-mono">{formData.high_risk_threshold} / 100</span>
              </div>
              <input
                type="range"
                min="50"
                max="90"
                value={formData.high_risk_threshold}
                onChange={(e) => handleChange('high_risk_threshold', parseInt(e.target.value))}
                className="w-full accent-red-600 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="font-semibold text-slate-700">Suspicious Threshold</span>
                <span className="font-bold text-amber-600 font-mono">{formData.suspicious_threshold} / 100</span>
              </div>
              <input
                type="range"
                min="15"
                max="50"
                value={formData.suspicious_threshold}
                onChange={(e) => handleChange('suspicious_threshold', parseInt(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Save Changes Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white font-semibold rounded-xl text-xs sm:text-sm transition-colors shadow-xs flex items-center space-x-2 cursor-pointer"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>Save Preferences</span>
          </button>
        </div>
      </form>

      {/* Account Security: Change Password */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-xs space-y-4">
        <div>
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <KeyRound className="w-4 h-4 text-teal-700" />
            <span>Account Security &amp; Password</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Update your account password with Argon2id cryptographic hashing
          </p>
        </div>

        {pwdFeedback && (
          <div className={`p-3 rounded-xl text-xs border ${
            pwdFeedback.type === 'success'
              ? 'bg-teal-50 border-teal-200 text-teal-900'
              : 'bg-red-50 border-red-200 text-red-900'
          }`}>
            {pwdFeedback.message}
          </div>
        )}

        <form onSubmit={handlePasswordChange} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              required
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-teal-600 focus:bg-white"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              New Password (min 8 chars)
            </label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-teal-600 focus:bg-white"
            />
          </div>
          <div className="sm:col-span-2 flex justify-end">
            <button
              type="submit"
              disabled={pwdLoading}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              {pwdLoading ? 'Updating...' : 'Update Password'}
            </button>
          </div>
        </form>
      </div>

      {/* Admin Operations Section (Part 4) */}
      <div className="p-6 rounded-2xl bg-white border border-red-200 shadow-xs space-y-3">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-red-600" />
          <h3 className="text-sm font-bold text-slate-900 uppercase">
            Administrative Operations &amp; Database Wipe
          </h3>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Destructive operations are protected by role-based access control. Wipes all message logs, alerts, URL inspections, and resets statistics to 0. Requires <strong className="text-red-700">ADMIN</strong> privileges.
        </p>

        {wipeResult && (
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-800">
            {wipeResult}
          </div>
        )}

        <div className="pt-2">
          {!confirmWipe ? (
            <button
              type="button"
              onClick={() => setConfirmWipe(true)}
              className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-bold transition-colors cursor-pointer"
            >
              Wipe Database (Admin Only)
            </button>
          ) : (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 flex items-center justify-between gap-3">
              <span className="text-xs font-bold text-red-800">Are you sure? This cannot be undone.</span>
              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={handleAdminWipe}
                  disabled={wiping}
                  className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg cursor-pointer"
                >
                  {wiping ? 'Wiping...' : 'Confirm Wipe'}
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmWipe(false)}
                  className="px-3 py-1.5 bg-white text-slate-600 border border-slate-200 text-xs font-semibold rounded-lg cursor-pointer"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

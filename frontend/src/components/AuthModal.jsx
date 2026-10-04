import React, { useState } from 'react';
import { Shield, Lock, Mail, UserCheck, AlertCircle, ArrowRight } from 'lucide-react';
import { api } from '../services/api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  if (!isOpen) return null;

  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let res;
      if (mode === 'login') {
        res = await api.login(email.trim(), password);
      } else {
        res = await api.register(email.trim(), password);
      }
      onAuthSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (quickEmail, quickPassword) => {
    setEmail(quickEmail);
    setPassword(quickPassword);
    setError('');
    setLoading(true);
    try {
      const res = await api.login(quickEmail, quickPassword);
      onAuthSuccess(res.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Quick login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div 
        className="w-full max-w-md bg-white rounded-2xl border border-slate-200 shadow-2xl p-6 sm:p-8 animate-scale-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-11 h-11 rounded-xl bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-700 shadow-sm">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900">ScamShield Security Portal</h2>
            <p className="text-xs text-slate-500">Authenticated Session & Tenant Isolation</p>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex border border-slate-200 rounded-xl p-1 bg-slate-50 mb-5">
          <button
            type="button"
            onClick={() => { setMode('login'); setError(''); }}
            className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors ${
              mode === 'login'
                ? 'bg-white text-teal-800 shadow-sm border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setMode('register'); setError(''); }}
            className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-colors ${
              mode === 'register'
                ? 'bg-white text-teal-800 shadow-sm border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Quick Login Presets for Hackathon */}
        <div className="mb-5 bg-teal-50/60 border border-teal-100 rounded-xl p-3">
          <div className="text-xs font-semibold text-teal-900 mb-2 flex items-center justify-between">
            <span>⚡ Hackathon Quick Connect</span>
            <span className="text-[10px] text-teal-700 bg-teal-100/70 px-2 py-0.5 rounded-full font-medium">1-Click</span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => handleQuickLogin('admin@scamshield.local', 'ScamShieldAdmin2026!')}
              disabled={loading}
              className="px-2.5 py-1.5 bg-white hover:bg-teal-50 text-teal-800 border border-teal-200 rounded-lg text-xs font-medium transition-colors text-left flex items-center space-x-1.5 shadow-xs"
            >
              <Shield className="w-3.5 h-3.5 text-teal-600 shrink-0" />
              <div className="truncate">
                <span className="font-semibold block truncate">Admin</span>
                <span className="text-[10px] text-slate-500 block truncate">Full privilege</span>
              </div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickLogin('user@scamshield.local', 'UserSafe2026!')}
              disabled={loading}
              className="px-2.5 py-1.5 bg-white hover:bg-teal-50 text-slate-800 border border-teal-200 rounded-lg text-xs font-medium transition-colors text-left flex items-center space-x-1.5 shadow-xs"
            >
              <UserCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <div className="truncate">
                <span className="font-semibold block truncate">Demo User</span>
                <span className="text-[10px] text-slate-500 block truncate">Tenant isolated</span>
              </div>
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-2 text-xs text-red-700">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-600 focus:bg-white transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-600 focus:bg-white transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-teal-700 hover:bg-teal-800 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-colors shadow-sm flex items-center justify-center space-x-2 mt-2"
          >
            <span>{loading ? 'Authenticating...' : (mode === 'login' ? 'Sign In Securely' : 'Create & Launch Account')}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-slate-500 border-t border-slate-100 pt-4">
          Protected by Argon2id password hashing &amp; HttpOnly SameSite session tokens.
        </div>
      </div>
    </div>
  );
}

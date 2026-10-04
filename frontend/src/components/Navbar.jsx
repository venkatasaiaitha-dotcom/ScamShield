import React from 'react';
import { Shield, Radio, Volume2, VolumeX, Bell, User, LogOut, LogIn } from 'lucide-react';

export default function Navbar({
  agentStatus,
  wsConnected,
  unreadCount,
  soundEnabled,
  setSoundEnabled,
  currentTab,
  setCurrentTab,
  onOpenAlerts,
  currentUser,
  onOpenAuth,
  onLogout,
}) {
  const isProtectionActive = agentStatus?.protection_active;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 lg:px-8 py-3 transition-colors shadow-xs">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('home')}>
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-teal-700 shadow-sm shadow-teal-800/20">
            <Shield className="w-5 h-5 text-white" />
            {isProtectionActive && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border border-white"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-slate-900 flex items-center">
                Scam<span className="text-teal-700">Shield</span>
              </span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-teal-50 text-teal-800 border border-teal-200">
                AI Safety Agent
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              Detect. Understand. Stay Safe.
            </p>
          </div>
        </div>

        {/* Center Desktop Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 bg-slate-100/90 border border-slate-200 rounded-full px-2 py-1 shadow-inner">
          {[
            { id: 'home', label: 'Home' },
            { id: 'alerts', label: 'Alerts', badge: unreadCount },
            { id: 'history', label: 'History' },
            { id: 'sources', label: 'Sources & Simulator' },
            { id: 'safety', label: 'Safety Hub' },
            { id: 'settings', label: 'Settings' },
          ].map((tab) => {
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`relative px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-teal-700 text-white font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/80'
                }`}
              >
                {tab.label}
                {tab.badge > 0 && (
                  <span className={`ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                    isActive ? 'bg-white text-teal-800' : 'bg-red-600 text-white'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Actions & Status Badges */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Live WS Pulse */}
          <div
            title={wsConnected ? 'Real-Time Tenant Stream Connected' : 'Connecting Stream...'}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200 text-[11px] text-slate-700 shadow-xs"
          >
            <Radio className={`w-3.5 h-3.5 ${wsConnected ? 'text-emerald-600 animate-pulse' : 'text-amber-500'}`} />
            <span className="hidden lg:inline">{wsConnected ? 'Live' : 'Syncing'}</span>
          </div>

          {/* Sound Toggle */}
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            title={soundEnabled ? 'Mute alert chimes' : 'Unmute alert chimes'}
            className={`p-2 rounded-lg border transition-colors ${
              soundEnabled
                ? 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
                : 'bg-slate-50/50 border-slate-200 text-slate-400'
            }`}
          >
            {soundEnabled ? <Volume2 className="w-4 h-4 text-teal-700" /> : <VolumeX className="w-4 h-4" />}
          </button>

          {/* User Account / Profile Info */}
          {currentUser ? (
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
              <div 
                onClick={onOpenAuth}
                className="cursor-pointer flex items-center space-x-2 px-2.5 py-1 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-colors"
                title="Click to switch account"
              >
                <div className="w-6 h-6 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center font-bold text-xs">
                  {currentUser.email.slice(0, 1).toUpperCase()}
                </div>
                <div className="text-left hidden lg:block">
                  <div className="text-xs font-semibold text-slate-800 truncate max-w-[120px]">
                    {currentUser.email}
                  </div>
                  <div className="text-[10px] font-bold text-teal-700 uppercase">
                    {currentUser.role}
                  </div>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign out"
                className="p-2 rounded-lg border border-slate-200 text-slate-500 hover:text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-teal-700 hover:bg-teal-800 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}

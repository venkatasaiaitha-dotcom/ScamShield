import React from 'react';
import { Home, ShieldAlert, History, BookOpen, Settings, Radio } from 'lucide-react';

export default function BottomNav({ currentTab, setCurrentTab, unreadCount }) {
  const tabs = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'alerts', label: 'Alerts', icon: ShieldAlert, badge: unreadCount },
    { id: 'history', label: 'History', icon: History },
    { id: 'sources', label: 'Sources', icon: Radio },
    { id: 'safety', label: 'Safety', icon: BookOpen },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-lg border-t border-slate-200 px-2 py-1.5 shadow-lg">
      <div className="flex items-center justify-around">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setCurrentTab(tab.id)}
              className={`relative flex flex-col items-center justify-center py-1 px-2.5 rounded-lg transition-colors cursor-pointer ${
                isActive ? 'text-teal-700 font-semibold' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <div className="relative">
                <Icon className={`w-5 h-5 ${isActive ? 'scale-110' : ''} transition-transform`} />
                {tab.badge > 0 && (
                  <span className="absolute -top-1.5 -right-2 flex h-3.5 min-w-3.5 px-1 items-center justify-center rounded-full bg-red-600 text-[9px] font-bold text-white">
                    {tab.badge}
                  </span>
                )}
              </div>
              <span className="text-[10px] mt-1 tracking-tight">{tab.label}</span>
              {isActive && (
                <span className="absolute bottom-0 w-6 h-0.5 bg-teal-700 rounded-full" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

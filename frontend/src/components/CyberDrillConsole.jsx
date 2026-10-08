import React, { useState, useEffect } from 'react';
import { Play, Sparkles, Shield, Cpu, ArrowRight, CheckCircle2, Loader2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function CyberDrillConsole({ onSelectScenario, onAnalysisComplete }) {
  const [drills, setDrills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningId, setRunningId] = useState(null);

  useEffect(() => {
    async function loadDrills() {
      try {
        const list = await api.getExpoDrills();
        setDrills(list);
      } catch (err) {
        console.error('Failed to load cyber drills:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDrills();
  }, []);

  const handleRunDrill = async (drill) => {
    setRunningId(drill.id);
    try {
      if (onSelectScenario) {
        onSelectScenario(drill);
      }
      const res = await api.analyzeMessage(drill.content, drill.sender);
      if (onAnalysisComplete) {
        onAnalysisComplete(res);
      }
    } catch (err) {
      console.error('Drill execution failed:', err);
    } finally {
      setRunningId(null);
    }
  };

  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center text-slate-400 text-xs flex items-center justify-center gap-2">
        <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
        Loading Cyber Drill Console...
      </div>
    );
  }

  return (
    <div className="bg-slate-900 text-white rounded-xl p-5 border border-indigo-900/60 shadow-xl relative overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 relative z-10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold tracking-wider text-indigo-400 uppercase bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/50">
                Interactive Drill Mode
              </span>
              <span className="text-xs text-slate-400">University Expo & Demo Lab</span>
            </div>
            <h3 className="text-lg font-bold text-slate-100 mt-0.5">
              EXPO DEMO / CYBER DRILL MODE
            </h3>
          </div>
        </div>

        <div className="text-xs text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800">
          5 Preset Test Scenarios • Real-Time AI Pipeline
        </div>
      </div>

      <p className="text-xs text-slate-300 mb-4 relative z-10 leading-relaxed">
        Select a safe test scenario below to simulate an active threat and observe ScamShield’s complete end-to-end detection pipeline:
        <span className="text-indigo-300 font-semibold"> Multi-Vector Analysis ➔ Scam DNA ➔ Attack Chain Timeline ➔ Next-Move Prediction ➔ UPI Guard ➔ Community Immunity</span>.
      </p>

      {/* 5 Preset Drills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 relative z-10">
        {drills.map((drill) => {
          const isRunning = runningId === drill.id;

          return (
            <div
              key={drill.id}
              className="bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-xl p-4 flex flex-col justify-between transition-all group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-800/40">
                    {drill.category.replace(/_/g, ' ')}
                  </span>
                  <span className="text-[11px] font-mono text-slate-400 truncate max-w-[120px]">
                    {drill.sender}
                  </span>
                </div>

                <h4 className="font-bold text-sm text-slate-100 group-hover:text-indigo-300 transition-colors mb-1.5">
                  {drill.name}
                </h4>

                <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-snug">
                  {drill.description}
                </p>

                <div className="bg-slate-900/90 rounded p-2 text-[11px] font-mono text-slate-300 italic line-clamp-2 border border-slate-800 mb-3">
                  "{drill.content}"
                </div>
              </div>

              <button
                type="button"
                onClick={() => handleRunDrill(drill)}
                disabled={isRunning}
                className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 transition shadow-sm"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    Executing Pipeline...
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    Launch Cyber Drill
                  </>
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

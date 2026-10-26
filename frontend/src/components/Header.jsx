import React from 'react';
import { Bot, Play, RotateCcw, Cpu, CheckCircle2, AlertCircle, Info, Sparkles } from 'lucide-react';

export default function Header({
  backendStatus,
  isRunning,
  onRun,
  onReset,
  selectedExample,
  onSelectExample,
  examples,
  onOpenAbout,
}) {
  return (
    <header className="glass-panel border-b border-cyan-500/20 bg-slate-950/80 px-4 py-3 sticky top-0 z-40">
      <div className="max-w-[1920px] mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Brand / Logo */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Bot className="w-5 h-5 text-cyan-400" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 rounded-full bg-cyan-400 border-2 border-slate-950 flex items-center justify-center">
              <Sparkles className="w-2 h-2 text-slate-950" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                RoboLang <span className="text-cyan-400 font-extrabold">Studio 2.0</span>
              </h1>
              <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
                Playground
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium hidden sm:block">
              Write Code • Control Robots • Visualize Compilation
            </p>
          </div>
        </div>

        {/* Center / Action Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Example Selector */}
          <div className="relative">
            <select
              value={selectedExample}
              onChange={(e) => onSelectExample(e.target.value)}
              className="bg-slate-900 border border-slate-700 hover:border-cyan-500/50 text-slate-200 text-xs rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-1 focus:ring-cyan-500 cursor-pointer transition-colors"
            >
              <option value="" disabled>Load Example Program...</option>
              {Object.entries(examples).map(([key, ex]) => (
                <option key={key} value={key}>
                  {ex.title}
                </option>
              ))}
            </select>
          </div>

          {/* Reset button */}
          <button
            onClick={onReset}
            title="Reset code and simulation"
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-slate-600 transition-all active:scale-95"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-400" />
            <span>Reset</span>
          </button>

          {/* Run Program Button */}
          <button
            onClick={onRun}
            disabled={isRunning}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold tracking-wide shadow-lg transition-all active:scale-95 ${
              isRunning
                ? 'bg-cyan-600/50 text-cyan-200 cursor-not-allowed shadow-none'
                : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold shadow-cyan-500/25 hover:shadow-cyan-500/40'
            }`}
          >
            {isRunning ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                <span>Compiling...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Program</span>
                <span className="text-[10px] opacity-75 font-mono px-1 py-0.2 bg-slate-950/20 rounded ml-1 hidden md:inline">
                  Ctrl+↵
                </span>
              </>
            )}
          </button>
        </div>

        {/* Right Status Indicators & About */}
        <div className="flex items-center gap-3">
          {/* Backend Status Badge */}
          <div
            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-full text-xs font-medium border ${
              backendStatus === 'online'
                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
                : backendStatus === 'checking'
                ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
            }`}
            title={
              backendStatus === 'online'
                ? 'FastAPI Backend running and connected'
                : 'Backend unreachable. Start with python -m uvicorn web_api.app:app'
            }
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-emerald-400 animate-pulse'
                  : backendStatus === 'checking'
                  ? 'bg-amber-400'
                  : 'bg-rose-400'
              }`}
            />
            <span className="hidden sm:inline">
              {backendStatus === 'online'
                ? 'Python Backend Online'
                : backendStatus === 'checking'
                ? 'Connecting...'
                : 'Backend Offline'}
            </span>
            <Cpu className="w-3.5 h-3.5 opacity-70" />
          </div>

          {/* About / Help */}
          <button
            onClick={onOpenAbout}
            className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-300 hover:bg-slate-800/80 transition-colors"
            title="About RoboLang Studio 2.0"
          >
            <Info className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}

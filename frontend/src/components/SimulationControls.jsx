import React from 'react';
import { Play, Pause, RotateCcw, FastForward, Repeat } from 'lucide-react';

export default function SimulationControls({
  isPlaying,
  isFinished,
  hasHistory,
  onPlay,
  onPause,
  onReplay,
  onReset,
  speedMultiplier,
  onSpeedChange,
}) {
  const speeds = [0.5, 1.0, 2.0, 4.0];

  return (
    <div className="glass-panel px-4 py-2.5 rounded-xl flex items-center justify-between gap-4 flex-wrap border border-slate-800">
      {/* Playback Controls */}
      <div className="flex items-center gap-2">
        {/* Play / Pause */}
        {isPlaying ? (
          <button
            onClick={onPause}
            disabled={!hasHistory}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-semibold shadow-md active:scale-95 transition-all"
            title="Pause Animation"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
            <span>Pause</span>
          </button>
        ) : (
          <button
            onClick={onPlay}
            disabled={!hasHistory || isFinished}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-md active:scale-95 transition-all ${
              !hasHistory || isFinished
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold shadow-cyan-500/20'
            }`}
            title="Play / Resume Animation"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Resume</span>
          </button>
        )}

        {/* Replay */}
        <button
          onClick={onReplay}
          disabled={!hasHistory}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all active:scale-95 ${
            !hasHistory
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border-slate-700'
              : 'bg-violet-500/20 hover:bg-violet-500/30 text-violet-300 border-violet-500/40'
          }`}
          title="Replay from Beginning (Without Re-compiling)"
        >
          <Repeat className="w-3.5 h-3.5" />
          <span>Replay</span>
        </button>

        {/* Reset Simulation */}
        <button
          onClick={onReset}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-slate-600 text-xs font-semibold transition-all active:scale-95"
          title="Reset to Origin (0,0)"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Sim</span>
        </button>
      </div>

      {/* Speed Multiplier */}
      <div className="flex items-center gap-2">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
          <FastForward className="w-3 h-3 text-cyan-400" />
          <span>Speed:</span>
        </span>
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5">
          {speeds.map((s) => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`px-2 py-0.5 text-xs rounded font-mono font-medium transition-colors ${
                speedMultiplier === s
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

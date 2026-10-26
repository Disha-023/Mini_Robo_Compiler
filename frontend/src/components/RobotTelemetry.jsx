import React from 'react';
import { Compass, Gauge, PenTool, Activity, CheckCircle2, Navigation, Layers, ShieldCheck } from 'lucide-react';

const DIR_ROTATIONS = {
  NORTH: 'rotate-0',
  EAST: 'rotate-90',
  SOUTH: 'rotate-180',
  WEST: '-rotate-90',
};

export default function RobotTelemetry({
  telemetry,
  finalState,
  isFinished,
  totalEvents,
}) {
  const x = telemetry?.currentPos?.x ?? 0;
  const y = telemetry?.currentPos?.y ?? 0;
  const direction = telemetry?.direction ?? 'NORTH';
  const penDown = telemetry?.penDown ?? false;
  const speed = telemetry?.speed ?? 1;
  const currentAction = telemetry?.currentEvent?.type ?? (isFinished ? 'IDLE' : 'READY');
  const currentEventIdx = (telemetry?.eventIndex ?? 0) + 1;
  const progressPercent = Math.min(100, Math.round((telemetry?.progressFraction ?? 0) * 100));

  return (
    <div className="flex flex-col h-full bg-slate-950/90 rounded-xl border border-slate-800/80 overflow-hidden shadow-xl">
      {/* Panel Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-900/90 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2 text-slate-300 font-semibold">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>Robot Telemetry</span>
        </div>
        <div className="flex items-center gap-1.5 text-[11px]">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-emerald-400 font-medium">Real-time</span>
        </div>
      </div>

      {/* Telemetry Grid */}
      <div className="p-3 space-y-3 flex-1 overflow-y-auto">
        {/* Coordinates Cards */}
        <div className="grid grid-cols-2 gap-2">
          {/* X Coordinate */}
          <div className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-lg flex flex-col">
            <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase">
              X Coordinate
            </span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-xl font-bold font-mono text-cyan-400">{x}</span>
              <span className="text-[10px] text-slate-500 font-mono">grid units</span>
            </div>
          </div>

          {/* Y Coordinate */}
          <div className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-lg flex flex-col">
            <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase">
              Y Coordinate
            </span>
            <div className="flex items-baseline justify-between mt-1">
              <span className="text-xl font-bold font-mono text-cyan-400">{y}</span>
              <span className="text-[10px] text-slate-500 font-mono">grid units</span>
            </div>
          </div>
        </div>

        {/* Heading & Compass */}
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
              <Navigation
                className={`w-5 h-5 text-cyan-400 transition-transform duration-300 ${
                  DIR_ROTATIONS[direction] || 'rotate-0'
                }`}
              />
            </div>
            <div>
              <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase block">
                Heading Direction
              </span>
              <span className="text-sm font-bold font-mono text-white tracking-wide">
                {direction}
              </span>
            </div>
          </div>
          <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono">
            {direction === 'NORTH' && '+Y Axis'}
            {direction === 'EAST' && '+X Axis'}
            {direction === 'SOUTH' && '-Y Axis'}
            {direction === 'WEST' && '-X Axis'}
          </span>
        </div>

        {/* Pen & Speed Status */}
        <div className="grid grid-cols-2 gap-2">
          {/* Pen State */}
          <div className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-lg flex items-center gap-2.5">
            <div
              className={`p-1.5 rounded-md ${
                penDown
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 glow-cyan'
                  : 'bg-slate-800 text-slate-500'
              }`}
            >
              <PenTool className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase block">
                Pen State
              </span>
              <span
                className={`text-xs font-bold font-mono ${
                  penDown ? 'text-cyan-400' : 'text-slate-400'
                }`}
              >
                {penDown ? 'DOWN (Drawing)' : 'UP (Hover)'}
              </span>
            </div>
          </div>

          {/* Speed */}
          <div className="bg-slate-900/80 border border-slate-800 p-2.5 rounded-lg flex items-center gap-2.5">
            <div className="p-1.5 rounded-md bg-violet-500/20 text-violet-400 border border-violet-500/40">
              <Gauge className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase block">
                Speed Level
              </span>
              <span className="text-xs font-bold font-mono text-violet-300">
                {speed}x
              </span>
            </div>
          </div>
        </div>

        {/* Current Executing Action Card */}
        <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-lg space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase">
              Current Action
            </span>
            <span className="text-[10px] font-mono text-slate-400">
              {totalEvents > 0 ? `Step ${Math.min(currentEventIdx, totalEvents)} / ${totalEvents}` : '0 / 0'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-bold font-mono text-cyan-300 bg-slate-950 px-2 py-1 rounded border border-cyan-500/20">
              {currentAction}
            </span>
            <span className="text-xs font-mono text-slate-400">
              {progressPercent}%
            </span>
          </div>

          {/* Progress Bar */}
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-violet-500 transition-all duration-150"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Final Backend State Check */}
        {finalState && (
          <div className="bg-emerald-950/30 border border-emerald-500/30 p-2.5 rounded-lg space-y-1">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Python Backend Final State</span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 flex items-center justify-between">
              <span>Pos: ({finalState.x}, {finalState.y})</span>
              <span>Dir: {finalState.direction}</span>
              <span>Pen: {finalState.pen_down ? 'DOWN' : 'UP'}</span>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-1.5 bg-slate-900/60 border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
        <span>Kinematic Interpolator</span>
        <span className="text-emerald-400">Active</span>
      </div>
    </div>
  );
}

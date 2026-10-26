import React from 'react';
import { X, Bot, CheckCircle, Terminal, Layers, Cpu } from 'lucide-react';

export default function AboutModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-cyan-500/30 rounded-2xl p-6 shadow-2xl shadow-cyan-500/10 text-slate-200">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Title */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center text-slate-950 shadow-md">
            <Bot className="w-6 h-6 text-slate-950" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              RoboLang Studio <span className="text-cyan-400">2.0</span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive 3D Compiler Playground & Robot Simulator
            </p>
          </div>
        </div>

        {/* Modal Content */}
        <div className="space-y-4 text-xs text-slate-300 max-h-[70vh] overflow-y-auto pr-1">
          <p className="leading-relaxed">
            RoboLang Studio 2.0 is an interactive compiler demonstration platform.
            It connects a modern React &amp; Three.js 3D web interface to an existing Python compiler backend.
          </p>

          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-2">
            <h3 className="font-semibold text-cyan-300 flex items-center gap-1.5 uppercase text-[11px] tracking-wider">
              <Cpu className="w-3.5 h-3.5" />
              Full Python Compiler Pipeline
            </h3>
            <ul className="grid grid-cols-2 gap-2 text-[11px]">
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>Lexer:</strong> Lexical analysis &amp; tokenization</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>Parser:</strong> Recursive descent AST generation</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>Semantic:</strong> Type checking &amp; symbol tables</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>IR Generator:</strong> Quadruple instructions &amp; labels</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>Codegen:</strong> Python executable target code</span>
              </li>
              <li className="flex items-center gap-1.5">
                <CheckCircle className="w-3 h-3 text-cyan-400 shrink-0" />
                <span><strong>Executor:</strong> Robot runtime kinematics &amp; history</span>
              </li>
            </ul>
          </div>

          <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800 space-y-2">
            <h3 className="font-semibold text-violet-300 flex items-center gap-1.5 uppercase text-[11px] tracking-wider">
              <Layers className="w-3.5 h-3.5" />
              Real Execution Replay Guarantee
            </h3>
            <p className="leading-relaxed text-[11px] text-slate-400">
              The 3D robot does not guess what commands to run. When you click <strong>Run Program</strong>, your code is compiled and executed by the Python runtime. The robot's recorded chronological history is returned to the browser and smoothly replayed using procedural Three.js interpolation.
            </p>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800">
            <span>Shortcut: <kbd className="px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded font-mono">Ctrl + Enter</kbd> to Run</span>
            <span>Version 2.0.0</span>
          </div>
        </div>

        <div className="mt-5 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-colors shadow-lg shadow-cyan-500/20"
          >
            Got it, Let's Code!
          </button>
        </div>
      </div>
    </div>
  );
}

import React, { useRef } from 'react';
import { Code, Trash2, Copy, Check, Terminal } from 'lucide-react';

const KEYWORDS = new Set([
  'START', 'STOP', 'MOVE', 'BACK', 'TURN', 'LEFT', 'RIGHT',
  'REPEAT', 'SPEED', 'POSITION', 'PEN_UP', 'PEN_DOWN',
  'LET', 'IF', 'ELSE', 'WHILE', 'PRINT', 'FUNC',
  'AND', 'OR', 'NOT', 'TRUE', 'FALSE', 'OBSTACLE_AHEAD'
]);

function highlightRoboLang(code) {
  const lines = code.split('\n');
  return lines.map((line, lIdx) => {
    // Check for comment
    const commentIdx = line.indexOf('//');
    let codePart = commentIdx !== -1 ? line.slice(0, commentIdx) : line;
    const commentPart = commentIdx !== -1 ? line.slice(commentIdx) : '';

    const tokens = [];
    let i = 0;
    while (i < codePart.length) {
      const ch = codePart[i];

      // String literal
      if (ch === '"') {
        let strVal = '"';
        i++;
        while (i < codePart.length && codePart[i] !== '"') {
          if (codePart[i] === '\\' && i + 1 < codePart.length) {
            strVal += codePart[i] + codePart[i + 1];
            i += 2;
          } else {
            strVal += codePart[i];
            i++;
          }
        }
        if (i < codePart.length && codePart[i] === '"') {
          strVal += '"';
          i++;
        }
        tokens.push(<span key={i} className="text-amber-300">{strVal}</span>);
        continue;
      }

      // Word / Keyword / Identifier
      if (/[a-zA-Z_]/.test(ch)) {
        let word = '';
        while (i < codePart.length && /[a-zA-Z0-9_]/.test(codePart[i])) {
          word += codePart[i];
          i++;
        }
        const upper = word.toUpperCase();
        if (KEYWORDS.has(upper)) {
          if (['START', 'STOP'].includes(upper)) {
            tokens.push(<span key={i} className="text-emerald-400 font-bold">{word}</span>);
          } else if (['MOVE', 'BACK', 'TURN', 'LEFT', 'RIGHT', 'SPEED', 'POSITION', 'PEN_UP', 'PEN_DOWN'].includes(upper)) {
            tokens.push(<span key={i} className="text-cyan-400 font-bold">{word}</span>);
          } else if (['IF', 'ELSE', 'WHILE', 'REPEAT'].includes(upper)) {
            tokens.push(<span key={i} className="text-violet-400 font-bold">{word}</span>);
          } else if (['LET', 'FUNC', 'PRINT'].includes(upper)) {
            tokens.push(<span key={i} className="text-pink-400 font-bold">{word}</span>);
          } else {
            tokens.push(<span key={i} className="text-blue-400 font-bold">{word}</span>);
          }
        } else {
          tokens.push(<span key={i} className="text-slate-200">{word}</span>);
        }
        continue;
      }

      // Numbers
      if (/[0-9]/.test(ch)) {
        let num = '';
        while (i < codePart.length && /[0-9.]/.test(codePart[i])) {
          num += codePart[i];
          i++;
        }
        tokens.push(<span key={i} className="text-orange-300 font-mono">{num}</span>);
        continue;
      }

      // Braces / Punctuation
      if (['{', '}', '(', ')', ',', '='].includes(ch)) {
        tokens.push(<span key={i} className="text-cyan-300 font-bold">{ch}</span>);
        i++;
        continue;
      }

      // Operators
      if (['+', '-', '*', '/', '>', '<', '!'].includes(ch)) {
        tokens.push(<span key={i} className="text-rose-400 font-bold">{ch}</span>);
        i++;
        continue;
      }

      // Any other char (spaces, etc.)
      tokens.push(<span key={i}>{ch}</span>);
      i++;
    }

    return (
      <div key={lIdx} className="h-6 whitespace-pre">
        {tokens}
        {commentPart && <span className="text-slate-500 italic">{commentPart}</span>}
      </div>
    );
  });
}

export default function CodeEditor({ code, onChange, onRun }) {
  const textareaRef = useRef(null);
  const highlightRef = useRef(null);
  const [copied, setCopied] = React.useState(false);

  const handleScroll = () => {
    if (textareaRef.current && highlightRef.current) {
      highlightRef.current.scrollTop = textareaRef.current.scrollTop;
      highlightRef.current.scrollLeft = textareaRef.current.scrollLeft;
    }
  };

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onRun();
    }
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      onChange(newCode);
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 4;
        }
      }, 0);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const lineCount = (code.match(/\n/g) || []).length + 1;
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1);

  return (
    <div className="flex flex-col h-full bg-slate-950/90 rounded-xl border border-slate-800/80 overflow-hidden shadow-xl">
      {/* Editor Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-900/90 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2 text-slate-300 font-semibold">
          <Code className="w-4 h-4 text-cyan-400" />
          <span>RoboLang Source Editor</span>
          <span className="text-[10px] text-slate-500 font-mono">(.robo)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Copy Code"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => onChange('')}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-rose-400 transition-colors"
            title="Clear Editor"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className="relative flex-1 flex overflow-hidden">
        {/* Line Numbers Gutter */}
        <div className="w-11 py-3 bg-slate-950/90 border-r border-slate-800/60 select-none text-right pr-2.5 text-slate-600 font-mono text-[13px] leading-6">
          {lineNumbers.map((num) => (
            <div key={num} className="h-6">{num}</div>
          ))}
        </div>

        {/* Text Container */}
        <div className="relative flex-1 h-full overflow-hidden">
          {/* Syntax Highlight Underlay */}
          <div
            ref={highlightRef}
            aria-hidden="true"
            className="absolute inset-0 p-3 m-0 border-0 overflow-hidden pointer-events-none font-mono text-[13px] leading-6"
            style={{
              fontFamily: 'monospace',
              letterSpacing: '0px',
            }}
          >
            {highlightRoboLang(code)}
          </div>

          {/* Editable Transparent Textarea Overlay */}
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => onChange(e.target.value)}
            onScroll={handleScroll}
            onKeyDown={handleKeyDown}
            spellCheck="false"
            autoCapitalize="off"
            autoComplete="off"
            autoCorrect="off"
            className="absolute inset-0 w-full h-full p-3 m-0 border-0 bg-transparent text-transparent caret-cyan-400 resize-none font-mono text-[13px] leading-6 focus:outline-none whitespace-pre overflow-auto"
            style={{
              fontFamily: 'monospace',
              letterSpacing: '0px',
            }}
            placeholder="// Type RoboLang program here or select an example..."
          />
        </div>
      </div>

      {/* Footer Info */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-900/60 border-t border-slate-800/80 text-[11px] text-slate-500">
        <div className="flex items-center gap-3">
          <span>{lineCount} lines</span>
          <span>{code.length} characters</span>
        </div>
        <div className="flex items-center gap-1.5 text-cyan-400/80 font-mono">
          <Terminal className="w-3 h-3" />
          <span>RoboLang 2.0</span>
        </div>
      </div>
    </div>
  );
}

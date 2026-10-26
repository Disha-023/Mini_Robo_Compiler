import React, { useState } from 'react';
import {
  ListFilter,
  FileCode,
  Binary,
  Terminal,
  AlertTriangle,
  Copy,
  Check,
  Search,
  CheckCircle2,
  GitBranch,
} from 'lucide-react';

export default function CompilerOutput({
  tokens = [],
  ast = null,
  ir = [],
  irFormatted = [],
  generatedCode = [],
  generatedCodeRaw = '',
  output = '',
  errors = [],
  activeTab,
  onTabChange,
}) {
  const [tokenSearch, setTokenSearch] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const filteredTokens = tokens.filter((t) =>
    t.type.toLowerCase().includes(tokenSearch.toLowerCase()) ||
    String(t.value).toLowerCase().includes(tokenSearch.toLowerCase())
  );

  const tabs = [
    {
      id: 'output',
      label: 'Program Output',
      icon: Terminal,
      badge: output ? 'active' : null,
      badgeColor: 'bg-cyan-500/20 text-cyan-300',
    },
    {
      id: 'tokens',
      label: 'Tokens',
      icon: ListFilter,
      count: tokens.length,
    },
    {
      id: 'ast',
      label: 'Abstract Syntax Tree',
      icon: GitBranch,
      badge: ast ? 'parsed' : null,
      badgeColor: 'bg-violet-500/20 text-violet-300',
    },
    {
      id: 'ir',
      label: 'Intermediate Representation',
      icon: Binary,
      count: irFormatted.length,
    },
    {
      id: 'codegen',
      label: 'Generated Python',
      icon: FileCode,
      count: generatedCode.length,
    },
    {
      id: 'errors',
      label: 'Compiler Errors',
      icon: AlertTriangle,
      count: errors.length,
      badgeColor: errors.length > 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : null,
    },
  ];

  return (
    <div className="flex flex-col h-full bg-slate-950/90 rounded-xl border border-slate-800/80 overflow-hidden shadow-xl">
      {/* Tabs Header */}
      <div className="flex items-center justify-between px-3 bg-slate-900/90 border-b border-slate-800 text-xs overflow-x-auto">
        <div className="flex items-center gap-1 py-1.5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-800 text-cyan-300 border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{tab.label}</span>
                {typeof tab.count === 'number' && tab.count > 0 && (
                  <span
                    className={`px-1.5 py-0.2 text-[10px] rounded-full font-mono ${
                      tab.id === 'errors' && errors.length > 0
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30 font-bold'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
                {tab.badge && (
                  <span className={`px-1.5 py-0.2 text-[9px] rounded uppercase font-semibold ${tab.badgeColor}`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Global Copy Button for Active Tab Content */}
        <div className="flex items-center pl-2">
          <button
            onClick={() => {
              if (activeTab === 'output') handleCopy(output);
              else if (activeTab === 'ir') handleCopy(irFormatted.join('\n'));
              else if (activeTab === 'codegen') handleCopy(generatedCodeRaw);
              else if (activeTab === 'ast') handleCopy(JSON.stringify(ast, null, 2));
              else if (activeTab === 'tokens') handleCopy(JSON.stringify(tokens, null, 2));
              else if (activeTab === 'errors') handleCopy(errors.join('\n'));
            }}
            className="flex items-center gap-1 px-2 py-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
            title="Copy tab content"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span className="text-[11px]">Copy</span>
          </button>
        </div>
      </div>

      {/* Tab Panels Content */}
      <div className="flex-1 p-3 overflow-y-auto font-mono text-xs">
        {/* TAB 1: Program Output */}
        {activeTab === 'output' && (
          <div className="h-full">
            {output ? (
              <pre className="p-3 bg-slate-900 rounded-lg text-emerald-300 whitespace-pre-wrap leading-relaxed border border-slate-800/80">
                {output}
              </pre>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 py-8">
                <Terminal className="w-8 h-8 mb-2 opacity-40 text-cyan-400" />
                <p>No program output yet. Run a program with PRINT or POSITION commands.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Tokens */}
        {activeTab === 'tokens' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between gap-3">
              <div className="relative flex-1 max-w-sm">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter tokens by type or value..."
                  value={tokenSearch}
                  onChange={(e) => setTokenSearch(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500/50"
                />
              </div>
              <span className="text-[11px] text-slate-400">
                Showing {filteredTokens.length} of {tokens.length} tokens
              </span>
            </div>

            {tokens.length > 0 ? (
              <div className="overflow-x-auto border border-slate-800 rounded-lg">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 uppercase tracking-wider text-[10px]">
                    <tr>
                      <th className="py-2 px-3">#</th>
                      <th className="py-2 px-3">Token Type</th>
                      <th className="py-2 px-3">Lexeme Value</th>
                      <th className="py-2 px-3">Line</th>
                      <th className="py-2 px-3">Column</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {filteredTokens.map((t, idx) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="py-1.5 px-3 text-slate-500">{idx + 1}</td>
                        <td className="py-1.5 px-3 text-cyan-400 font-bold">{t.type}</td>
                        <td className="py-1.5 px-3 text-amber-300">{JSON.stringify(t.value)}</td>
                        <td className="py-1.5 px-3 text-slate-400">{t.line}</td>
                        <td className="py-1.5 px-3 text-slate-400">{t.column}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center text-slate-500 py-8">
                Click "Run Program" to perform lexical analysis.
              </div>
            )}
          </div>
        )}

        {/* TAB 3: Abstract Syntax Tree */}
        {activeTab === 'ast' && (
          <div className="h-full">
            {ast ? (
              <pre className="p-3 bg-slate-900 rounded-lg text-violet-300 whitespace-pre-wrap leading-relaxed border border-slate-800/80 overflow-auto">
                {JSON.stringify(ast, null, 2)}
              </pre>
            ) : (
              <div className="text-center text-slate-500 py-8">
                Run program to construct the Abstract Syntax Tree.
              </div>
            )}
          </div>
        )}

        {/* TAB 4: Intermediate Representation (IR) */}
        {activeTab === 'ir' && (
          <div className="space-y-1">
            {irFormatted.length > 0 ? (
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800/80 font-mono">
                {irFormatted.map((instr, idx) => {
                  const parts = instr.split(' ');
                  const opcode = parts[0];
                  const operands = parts.slice(1).join(' ');
                  return (
                    <div key={idx} className="flex items-center gap-3 py-1 hover:bg-slate-850 px-2 rounded">
                      <span className="w-8 text-right text-slate-600 select-none">{idx + 1}</span>
                      <span className="text-cyan-400 font-bold w-32">{opcode}</span>
                      <span className="text-slate-300 flex-1">{operands}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center text-slate-500 py-8">
                Run program to generate Intermediate Representation (IR).
              </div>
            )}
          </div>
        )}

        {/* TAB 5: Generated Python Code */}
        {activeTab === 'codegen' && (
          <div className="h-full">
            {generatedCode.length > 0 ? (
              <div className="p-3 bg-slate-900 rounded-lg border border-slate-800/80 font-mono">
                {generatedCode.map((line, idx) => (
                  <div key={idx} className="flex items-start gap-3 py-0.5 hover:bg-slate-850 px-2 rounded">
                    <span className="w-8 text-right text-slate-600 select-none">{idx + 1}</span>
                    <span className="text-emerald-400 flex-1 whitespace-pre">{line}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-slate-500 py-8">
                Run program to view generated Python target code.
              </div>
            )}
          </div>
        )}

        {/* TAB 6: Errors */}
        {activeTab === 'errors' && (
          <div className="space-y-2">
            {errors.length > 0 ? (
              errors.map((err, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-rose-950/40 border border-rose-500/40 rounded-lg text-rose-300 flex items-start gap-2.5"
                >
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                  <div className="flex-1 whitespace-pre-wrap">{err}</div>
                </div>
              ))
            ) : (
              <div className="flex flex-col items-center justify-center text-slate-500 py-8">
                <CheckCircle2 className="w-8 h-8 mb-2 text-emerald-400/60" />
                <p className="text-slate-400">No compilation or execution errors detected.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Terminal as TerminalIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TerminalProps {
  title?: string;
  lines: string[];
  className?: string;
  showPrompt?: boolean;
}

export function Terminal({ title = 'pnj-telemetry', lines, className, showPrompt = true }: TerminalProps) {
  const [history, setHistory] = useState<string[]>(lines);
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Focus the input when clicking anywhere inside the terminal screen
  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  // Scroll to the bottom when history logs update
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const cmd = input.trim();
    if (!cmd) return;

    const newHistory = [...history, `pnj@studio:~$ ${cmd}`];
    const parts = cmd.toLowerCase().split(' ');
    const command = parts[0];

    let output: string[] = [];

    switch (command) {
      case 'help':
        output = [
          'Available commands:',
          '  help      - List available shell operations',
          '  status    - Check telemetry health & database states',
          '  neofetch  - Render system info & OS stats',
          '  modules   - List loaded personal OS dashboard features',
          '  sync      - Trigger manual vector embedding database updates',
          '  contact   - Display BuildWithPNJ communication channels',
          '  clear     - Clear the terminal console output'
        ];
        break;
      case 'clear':
        setHistory([]);
        setInput('');
        return;
      case 'status':
        output = [
          'WARBORN SYSTEM TELEMETRY:',
          '  [+] CORE: Active & Synchronized',
          '  [+] DATABASE: PostgreSQL (pgvector index enabled)',
          '  [+] QUEUE: Celery worker solo-thread online',
          '  [+] LATENCY: 12ms (vector embedding lookup query)',
          '  [+] CACHE: Redis pool initialized (156 keys loaded)',
          '  [+] DRIVE SYNC: Google Drive API (0 pending updates)'
        ];
        break;
      case 'neofetch':
        output = [
          '   _      __           __                  ',
          '  | | /| / /__ _____  / /  ___  _______    ',
          '  | |/ |/ / _ `/ __/ / _ \\/ _ \\/ __/ _ \\   ',
          '  |__/|__/\\_,_/_/   /_.__/\\___/_/  \\___/   ',
          '                                           ',
          '  OS: Warborn OS v1.2 (Stateless Core)',
          '  Host: pnj-studio (BuildWithPNJ Client)',
          '  Kernel: Next.js 15.5 / FastAPI Backend',
          '  Shell: Interactive AI Agent Shell',
          '  Uptime: 100% active operational session',
          '  Database: PostgreSQL + pgvector lookup',
          '  Status: Operational / Ready for production'
        ];
        break;
      case 'modules':
        output = [
          'LOADED OS MODULES:',
          '  - Notes Archive (Stateful Markdown search & RAG)',
          '  - Finance tracker (Double-entry ledger & balance sheet)',
          '  - Habits tracker (Weekly checklist metrics grid)',
          '  - Stateless Cloud Sync (Stateless Google Drive bridge)'
        ];
        break;
      case 'sync':
        output = [
          'Initializing vector index database sync...',
          'Scanning Google Drive directories...',
          '[1/3] Reading updated files (2 modifications found)',
          '[2/3] Generating sentence-transformer vector chunks...',
          '[3/3] Inserting vector index into pgvector schema... SUCCESS',
          'Sync finished successfully in 1.18s'
        ];
        break;
      case 'contact':
        output = [
          'BUILDWITHPNJ CONTACT BLUEPRINTS:',
          '  Email: hello@buildwithpnj.com',
          '  Twitter/X: @buildwithpnj',
          '  GitHub: github.com/buildwithpnj'
        ];
        break;
      default:
        output = [
          `bash: command not found: ${cmd}`,
          'Type "help" to view a list of available commands.'
        ];
    }

    setHistory([...newHistory, ...output]);
    setInput('');
  };

  return (
    <div 
      onClick={handleTerminalClick}
      className={cn("w-full rounded-2xl border border-border/40 bg-card/65 backdrop-blur-md shadow-2xl overflow-hidden font-mono text-[11px] text-left cursor-text", className)}
    >
      
      {/* Terminal Window Header Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-background/60 border-b border-border/40 select-none">
        <div className="flex items-center gap-2">
          {/* Simulated Mac OS window controls */}
          <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] border border-[#E0443E]/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] border border-[#DEA123]/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#27C93F] border border-[#1AAB29]/20" />
        </div>
        
        <span className="text-[9px] text-muted-foreground font-semibold flex items-center gap-1.5 uppercase tracking-wider font-sans">
          <TerminalIcon className="h-3 w-3 text-primary" /> {title}
        </span>
        
        <div className="w-12" /> {/* Spacer */}
      </div>

      {/* Terminal Content Screen */}
      <div 
        ref={scrollRef}
        className="p-5 flex flex-col gap-1.5 max-h-[260px] overflow-y-auto bg-black/45 text-muted-foreground"
      >
        
        {/* Output lines */}
        {history.map((line, idx) => (
          <div key={idx} className="flex items-start gap-1.5 leading-normal">
            {line.startsWith('pnj@') ? (
              <span className="text-primary shrink-0 select-none">pnj@studio:~$</span>
            ) : line.startsWith('>') ? (
              <span className="text-primary shrink-0 select-none">&gt;</span>
            ) : null}
            <span className={cn(
              "whitespace-pre-wrap select-text",
              line.includes('SUCCESS') || line.includes('online') || line.includes('ACTIVE') ? 'text-emerald-400 font-bold' :
              line.includes('ERROR') || line.includes('failed') || line.includes('command not found') ? 'text-red-500 font-bold' :
              line.startsWith('pnj@') ? 'text-foreground' : ''
            )}>
              {line.startsWith('pnj@') ? line.replace('pnj@studio:~$ ', '') : line.startsWith('>') ? line.substring(1) : line}
            </span>
          </div>
        ))}

        {/* Interactive Shell Prompt Form */}
        {showPrompt && (
          <form onSubmit={handleSubmit} className="flex items-center gap-1.5 mt-0.5 w-full">
            <span className="text-primary shrink-0 select-none">pnj@studio:~$</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-foreground caret-primary font-mono text-[11px] focus:ring-0 p-0 focus:outline-none"
              autoFocus
              autoComplete="off"
              autoCorrect="off"
              autoCapitalize="off"
              spellCheck="false"
            />
          </form>
        )}

      </div>

    </div>
  );
}

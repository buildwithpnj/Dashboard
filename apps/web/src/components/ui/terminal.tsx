'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Terminal as TerminalIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TerminalProps {
  title?: string;
  lines: string[];
  className?: string;
  showPrompt?: boolean;
}

export function Terminal({ title = 'warborn_telemetry.log', lines, className, showPrompt = true }: TerminalProps) {
  const [history, setHistory] = useState<string[]>([]);
  const [inputVal, setInputVal] = useState('');
  const [isStreaming, setIsStreaming] = useState(true);

  const inputRef = useRef<HTMLInputElement>(null);
  const screenRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Initialize history with initial lines
  useEffect(() => {
    if (lines && lines.length > 0 && history.length === 0) {
      setHistory(lines);
    }
  }, [lines]);

  // Live telemetry stream simulator
  useEffect(() => {
    if (!isStreaming) return;

    const logTemplates = [
      () => `API  GET /api/v1/notes 200 OK - ${(Math.random() * 8 + 4).toFixed(1)}ms`,
      () => `TASK celery_worker_1: Embedding extraction completed for ID ${Math.floor(Math.random() * 400 + 100)}`,
      () => `DB   pgvector lookup: match similarity ${(Math.random() * 5 + 92).toFixed(1)}% - ${(Math.random() * 2 + 1.5).toFixed(1)}ms`,
      () => `SYNC Google Drive stateless check: 0 changes pending`,
      () => `MEM  Redis cache lookup hit for dashboard_stats - ${(Math.random() * 0.4 + 0.2).toFixed(2)}ms`,
      () => `API  POST /api/v1/habits/check_in [200 OK] - ${(Math.random() * 10 + 8).toFixed(1)}ms`,
      () => `SYS  Garbage collection cycle completed - reclaimed 4.1MB`,
      () => `SEC  JWT verification: session validated for pnj@studio`,
      () => `TASK celery_worker_1: process_staging_entry completed job_${Math.floor(Math.random() * 800 + 100)}`
    ];

    const interval = setInterval(() => {
      const randomLog = logTemplates[Math.floor(Math.random() * logTemplates.length)]();
      const timestamp = new Date().toISOString().substring(11, 19);
      setHistory(prev => {
        const next = [...prev, `[${timestamp}] ${randomLog}`];
        return next.slice(-35); // Keep history capped
      });
    }, 3200);

    return () => clearInterval(interval);
  }, [isStreaming]);

  // Auto-scroll only the terminal box content container
  useEffect(() => {
    const el = screenRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [history]);

  const handleTerminalClick = () => {
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const command = inputVal.trim();
      if (!command) return;

      const newHistory = [...history, `pnj@studio:~$ ${command}`];
      const output = executeCommand(command);
      
      if (output && output.length > 0) {
        newHistory.push(...output);
      }

      setHistory(newHistory.slice(-60));
      setInputVal('');
    }
  };

  const executeCommand = (cmdStr: string): string[] => {
    const args = cmdStr.toLowerCase().split(' ');
    const command = args[0];

    switch (command) {
      case 'clear':
        setHistory([]);
        return [];
      case 'help':
        return [
          'Available Commands:',
          '  help      - Display this list of commands',
          '  status    - View system health & latency telemetry',
          '  neofetch  - Display host specs & ASCI art logo',
          '  ping      - Check roundtrip response latency',
          '  telemetry - Toggle live log stream (active/paused)',
          '  about     - About BuildWithPNJ & Warborn OS',
          '  clear     - Clear terminal screen buffer'
        ];
      case 'status':
        const latency = (Math.random() * 4 + 11).toFixed(1);
        return [
          '=============================================',
          '   WARBORN OS STATUS & HEALTH OVERVIEW      ',
          '=============================================',
          'NEXTJS WEB PORTAL : ONLINE  [PORT 3000]',
          'FASTAPI SERVICE   : ONLINE  [PORT 8000]',
          'CELERY SOLO TASK  : ONLINE  [SOLO WORKER]',
          `DATABASE pgvector : OPERATIONAL (similarity search)`,
          `AVG API LATENCY   : ${latency}ms`,
          'REDIS MEMORY CACHE: ACTIVE (99.8% hit rate)',
          'SYSTEM CONTROL    : 100% OK'
        ];
      case 'neofetch':
        return [
          '   _      __           __                  ',
          '  | | /| / /__ _____  / /  ___  _______    ',
          '  | |/ |/ / _ `/ __/ / _ \\/ _ \\/ __/ _ \\   ',
          '  |__/|__/\\_,_/_/   /_.__/\\___/_/  \\___/   ',
          '  --------------------------------------   ',
          '  OS      : Warborn OS v1.0.4',
          '  HOST    : buildwithpnj.studio',
          '  KERNEL  : Linux 6.1.0-py-agent',
          '  SHELL   : pnj-sh 2.0',
          '  UPTIME  : 14 days, 6 hours, 12 mins',
          '  CPU     : Virtual AI Agent Core (16 Cores)',
          '  MEMORY  : Redis In-Memory Buffered',
          '  THEME   : Electric Cyan / Graphite Black'
        ];
      case 'ping':
        const p1 = (Math.random() * 3 + 11).toFixed(1);
        const p2 = (Math.random() * 3 + 10).toFixed(1);
        const p3 = (Math.random() * 3 + 12).toFixed(1);
        return [
          'PING api.buildwithpnj.com (104.21.3.112): 56 data bytes',
          `64 bytes from 104.21.3.112: icmp_seq=0 ttl=56 time=${p1} ms`,
          `64 bytes from 104.21.3.112: icmp_seq=1 ttl=56 time=${p2} ms`,
          `64 bytes from 104.21.3.112: icmp_seq=2 ttl=56 time=${p3} ms`,
          '--- api.buildwithpnj.com ping statistics ---',
          '3 packets transmitted, 3 received, 0% packet loss'
        ];
      case 'telemetry':
        const newState = !isStreaming;
        setIsStreaming(newState);
        return [
          `Telemetry logs streaming ${newState ? 'STARTED' : 'PAUSED'}.`
        ];
      case 'about':
        return [
          'BuildWithPNJ is an AI Product Engineering Lab.',
          'Warborn OS is the central management dashboard built',
          'to automate note indexing, financial logs tracking,',
          'habits check-ins, and data synchronization workflows.',
          'Visit https://github.com/buildwithpnj for source designs.'
        ];
      default:
        return [
          `bash: command not found: ${command}`,
          'Type "help" to see available commands.'
        ];
    }
  };

  return (
    <div 
      onClick={handleTerminalClick}
      className={cn("w-full rounded-2xl border border-[#1e2030]/80 bg-[#090b10] shadow-2xl overflow-hidden font-mono text-[10.5px] text-left cursor-text", className)}
    >
      {/* Terminal Window Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#030406]/85 border-b border-[#1e2030]/50 select-none">
        <div className="flex items-center gap-1.5">
          {/* Simulated Mac OS window controls */}
          <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] border border-[#E0443E]/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] border border-[#DEA123]/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#27C93F] border border-[#1AAB29]/20" />
        </div>
        
        <span className="text-[9px] text-[#8e99b0] font-semibold flex items-center gap-1.5 uppercase tracking-wider font-sans">
          <TerminalIcon className="h-3 w-3 text-primary" /> {title}
        </span>
        
        <div className="w-10" />
      </div>

      {/* Terminal Content Screen */}
      <div 
        ref={screenRef}
        className="p-4 flex flex-col gap-1.5 h-[240px] overflow-y-auto bg-[#07080b] text-[#a6accd]"
      >
        {/* Output lines */}
        {history.map((line, idx) => {
          const isUserCommand = line.startsWith('pnj@studio:~$');
          const isError = line.startsWith('bash:') || line.includes('ERROR') || line.includes('failed');
          const isSuccess = line.includes('SUCCESS') || line.includes('200 OK') || line.includes('success') || line.includes('ONLINE');

          if (isUserCommand) {
            return (
              <div key={idx} className="flex items-start gap-1 leading-relaxed">
                <span className="text-[#06b6d4] shrink-0 font-bold">pnj@studio:~$</span>
                <span className="whitespace-pre-wrap select-text text-white font-medium">{line.replace('pnj@studio:~$ ', '')}</span>
              </div>
            );
          }

          // Parse for log tags: e.g. "[timestamp] TAG info" or "TAG info"
          const match = line.match(/^(\[\d{2}:\d{2}:\d{2}\]\s+)?(API|TASK|DB|MEM|SYNC|SYS|SEC)\s+(.*)$/);
          if (match) {
            const timestamp = match[1] || '';
            const tag = match[2];
            const rest = match[3];
            
            const tagColors: Record<string, string> = {
              API: 'text-[#38bdf8]',
              TASK: 'text-[#c084fc]',
              DB: 'text-[#fb7185]',
              MEM: 'text-[#facc15]',
              SYNC: 'text-[#34d399]',
              SYS: 'text-[#fb923c]',
              SEC: 'text-[#2dd4bf]'
            };
            
            return (
              <div key={idx} className="flex items-start gap-1 leading-relaxed text-[#8e99b0]">
                {timestamp && <span className="text-[#4c566a] shrink-0">{timestamp}</span>}
                <span className={cn("font-bold shrink-0", tagColors[tag])}>{tag}</span>
                <span className={cn(
                  "whitespace-pre-wrap select-text",
                  isSuccess && 'text-[#10b981] font-semibold',
                  isError && 'text-[#f87171]'
                )}>{rest}</span>
              </div>
            );
          }

          return (
            <div key={idx} className="flex items-start gap-1 leading-relaxed">
              <span className={cn(
                "whitespace-pre-wrap select-text",
                isSuccess && 'text-[#10b981] font-semibold',
                isError && 'text-[#f87171]',
                (line.startsWith('Available') || line.startsWith('OS ') || line.includes('Specs')) ? 'text-[#2dd4bf]' : 'text-[#8e99b0]'
              )}>
                {line}
              </span>
            </div>
          );
        })}

        {/* Dynamic prompt input line */}
        {showPrompt && (
          <div className="flex items-center gap-1.5 mt-1 relative min-h-[1.5rem]">
            <span className="text-[#06b6d4] shrink-0 font-bold">pnj@studio:~$</span>
            <div className="flex-1 flex items-center relative min-w-[50px]">
              <span className="text-white font-medium whitespace-pre">{inputVal}</span>
              <span className="w-1.5 h-3.5 bg-[#06b6d4] animate-pulse ml-0.5" />
              <input
                ref={inputRef}
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                onKeyDown={handleKeyDown}
                className="absolute inset-0 w-full h-full opacity-0 cursor-text outline-none font-mono text-white bg-transparent"
                autoCapitalize="none"
                autoComplete="off"
                autoCorrect="off"
                spellCheck={false}
              />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

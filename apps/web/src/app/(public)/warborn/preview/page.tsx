'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Send, Sparkles, Key, AlertTriangle, CornerDownLeft, RefreshCw } from 'lucide-react';

interface ChatMessage {
  sender: 'user' | 'agent';
  text: string;
}

export default function WarbornPreviewSandbox() {
  const [sessionId, setSessionId] = useState<string>('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [turnsCount, setTurnsCount] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Initialize session
  const startNewSession = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      setMessages([]);
      setTurnsCount(0);
      
      const apiHost = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiHost}/api/public-preview/session`, {
        method: 'POST',
      });
      const data = await res.json();
      if (data.session_id) {
        setSessionId(data.session_id);
        setMessages([
          {
            sender: 'agent',
            text: "Hello! I am agentEnglish. Ask me to correct grammar, rewrite text professionally, translate Hinglish, or explain grammar rules. This is a public preview sandbox."
          }
        ]);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to connect to agent kernel. Make sure the API server is active.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    startNewSession();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || loading || !sessionId) return;

    const userText = inputText;
    setInputText('');
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);
    setErrorMsg(null);

    try {
      const apiHost = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiHost}/api/public-preview/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: userText
        }),
      });

      if (res.status === 429) {
        setErrorMsg("Too many requests from this address. Please wait a minute.");
        return;
      }

      const data = await res.json();
      
      if (data.status === "blocked") {
        setMessages(prev => [...prev, { sender: 'agent', text: data.message }]);
        setErrorMsg("System constraint triggered.");
      } else {
        setMessages(prev => [...prev, { sender: 'agent', text: data.message }]);
        setTurnsCount(prev => prev + 1);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to receive agent response. Pipeline error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-foreground relative grid-dots py-12 px-4 sm:px-6 flex flex-col items-center">
      <div className="max-w-2xl w-full flex flex-col gap-6">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/40 pb-4">
          <div>
            <span className="text-3xs font-mono font-bold text-primary uppercase">{"Agent English Runtime"}</span>
            <h1 className="text-lg font-bold">{"Public Preview Sandbox"}</h1>
          </div>
          <button
            onClick={startNewSession}
            disabled={loading}
            className="p-2 rounded-lg border border-border/80 bg-card hover:bg-muted/30 transition-all"
            title="Reset Sandbox Session"
          >
            <RefreshCw className={`h-4 w-4 text-muted-foreground ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Limitations Alert Note */}
        <div className="rounded-xl border border-amber-500/25 bg-amber-500/5 p-4 flex gap-3 text-left font-mono text-[10px] text-amber-300">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">{"Sandbox Mode Rules:"}</span>
            <ul className="list-disc pl-4 space-y-0.5">
              <li>{"Max 5 turns per session (Turns remaining: "}{5 - turnsCount}{")"}</li>
              <li>{"Allowed tasks only: Grammar correction, rewrites, Hinglish translation, short explanations"}</li>
              <li>{"No file uploads, persistent memory, or external dashboard access"}</li>
            </ul>
          </div>
        </div>

        {/* Chat Console Panel */}
        <div className="rounded-2xl border border-border bg-card/45 h-96 flex flex-col overflow-hidden shadow-xl backdrop-blur-sm">
          {/* Messages body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-left">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-2.5 text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-primary text-primary-foreground font-semibold'
                      : 'bg-secondary text-foreground border border-border/60 font-mono'
                  }`}
                >
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-secondary text-muted-foreground border border-border/40 rounded-xl px-4 py-2.5 text-xs font-mono flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce delay-75" />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce delay-150" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Clickable prompt chips */}
          <div className="px-4 py-2 bg-secondary/10 border-t border-border/40 flex flex-wrap gap-2 text-[10px] font-mono justify-start">
            <span className="text-muted-foreground mr-1">Try:</span>
            {[
              { label: "Correct Grammar", text: "correct grammar: Me has went to home yesterday" },
              { label: "Professional Rewrite", text: "rewrite professionally: tell him i am late" },
              { label: "Translate Hinglish", text: "translate hinglish: please adjust kar lo" }
            ].map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                disabled={turnsCount >= 5 || loading}
                onClick={() => setInputText(prompt.text)}
                className="px-2 py-0.5 rounded border border-border/60 bg-card hover:bg-muted/40 hover:border-primary/30 transition-all text-muted-foreground hover:text-foreground"
              >
                {prompt.label}
              </button>
            ))}
          </div>

          {/* Form input */}
          <form onSubmit={handleSend} className="border-t border-border/60 p-3 bg-secondary/20 flex gap-2">
            <input
              type="text"
              placeholder={turnsCount >= 5 ? "Turn limit reached. Please reset session or log in." : "Type your correction or rewrite query..."}
              disabled={turnsCount >= 5 || loading || !sessionId}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 h-9 px-3.5 rounded-lg border border-border/40 bg-background/50 text-xs focus:outline-none focus:border-primary/50"
            />
            <button
              type="submit"
              disabled={turnsCount >= 5 || loading || !inputText.trim() || !sessionId}
              className="h-9 w-9 rounded-lg bg-primary hover:bg-primary/95 text-primary-foreground flex items-center justify-center transition-all disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>

        {/* Errors / Warnings */}
        {errorMsg && (
          <div className="text-center font-mono text-[10px] text-rose-400">
            {errorMsg}
          </div>
        )}

        {/* Bottom Handoff CTA */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-border/60 bg-muted/10 font-mono text-[10px] text-muted-foreground">
          <span>{"Need full access or developer orchestration consoles?"}</span>
          <div className="flex gap-3">
            <Link href="/login" className="flex items-center gap-1 text-primary hover:underline font-bold">
              <Key className="h-3 w-3" /> {"Log In"}
            </Link>
            <span>{"|"}</span>
            <Link href="/request-access" className="text-foreground hover:underline font-bold">
              {"Request Access"}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

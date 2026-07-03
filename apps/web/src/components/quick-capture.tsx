'use client';

import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { useShortcutStore } from '@/hooks/use-keyboard-shortcuts';
import { useCreateTransaction } from '@/hooks/use-finance';

export function QuickCapture() {
  const { isQuickCaptureOpen, setQuickCaptureOpen } = useShortcutStore();
  const [input, setInput] = useState('');
  const [inferredType, setInferredType] = useState<string>('note');
  const createTransaction = useCreateTransaction();

  if (!isQuickCaptureOpen) return null;

  function inferType(text: string) {
    const trimmed = text.trim();
    // Currency/amount pattern → transaction
    if (/^[\$₹€£]?\d+[\d,]*\.?\d*\s+/.test(trimmed) || /^\-?\d+[\d,]*\.?\d*\s+/.test(trimmed)) {
      return 'transaction';
    }
    // Contains "tmrw", "tomorrow", "today", "due" → task
    if (/\b(tmrw|tomorrow|today|due|deadline)\b/i.test(trimmed)) {
      return 'task';
    }
    // Short title-like text → could be a book
    if (trimmed.split(' ').length <= 6 && /^[A-Z]/.test(trimmed)) {
      return 'book';
    }
    return 'note';
  }

  function handleInputChange(value: string) {
    setInput(value);
    setInferredType(inferType(value));
  }

  function handleSubmit() {
    // For Phase 1, we only handle transactions
    // Other types will show a "coming soon" toast
    setInput('');
    setQuickCaptureOpen(false);
  }

  const typeColors: Record<string, string> = {
    transaction: 'text-emerald-400',
    task: 'text-sky-400',
    book: 'text-amber-400',
    note: 'text-violet-400',
  };

  return (
    <div className="fixed inset-0 z-50" id="quick-capture">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={() => setQuickCaptureOpen(false)}
      />

      {/* Capture dialog */}
      <div className="absolute left-1/2 top-[20%] w-full max-w-lg -translate-x-1/2 animate-slide-down">
        <div className="rounded-xl border border-border bg-popover shadow-2xl shadow-black/40 overflow-hidden">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-semibold text-foreground">Quick Capture</h2>
              {input && (
                <span className={`text-2xs font-medium uppercase ${typeColors[inferredType]}`}>
                  → {inferredType}
                </span>
              )}
            </div>
            <button
              onClick={() => setQuickCaptureOpen(false)}
              className="rounded p-1 text-muted-foreground hover:bg-accent"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="p-4">
            <input
              type="text"
              value={input}
              onChange={(e) => handleInputChange(e.target.value)}
              placeholder='Try: "$450 groceries" or "Atomic Habits" or "call landlord tmrw"'
              className="w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  handleSubmit();
                }
              }}
            />
          </div>

          <div className="border-t border-border px-4 py-2 flex items-center justify-between bg-muted/20">
            <p className="text-2xs text-muted-foreground">
              Type naturally — type is inferred automatically
            </p>
            <div className="flex items-center gap-3">
              <span className="text-2xs text-muted-foreground hidden sm:inline">
                Press <span className="kbd">Ctrl</span> + <span className="kbd">Enter</span>
              </span>
              <button
                onClick={handleSubmit}
                className="rounded bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground hover:bg-primary/95 transition-colors shadow-sm"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

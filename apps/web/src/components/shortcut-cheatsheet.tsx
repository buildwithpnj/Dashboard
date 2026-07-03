'use client';

import { useShortcutStore } from '@/hooks/use-keyboard-shortcuts';
import { X } from 'lucide-react';

const shortcuts = [
  {
    group: 'Global',
    items: [
      { keys: ['Ctrl', 'K'], description: 'Command palette' },
      { keys: ['Ctrl', 'N'], description: 'Quick capture' },
      { keys: ['G', 'D'], description: 'Go to Home' },
      { keys: ['G', 'F'], description: 'Go to Finance' },
      { keys: ['G', 'B'], description: 'Go to Books' },
      { keys: ['G', 'H'], description: 'Go to Habits' },
      { keys: ['G', 'N'], description: 'Go to Notes' },
      { keys: ['G', 'T'], description: 'Go to Tools' },
      { keys: ['/'], description: 'Focus search' },
      { keys: ['Ctrl', 'Shift', 'A'], description: 'Agent inbox' },
      { keys: ['Ctrl', 'Enter'], description: 'Save & close' },
      { keys: ['Esc'], description: 'Close / cancel' },
      { keys: ['?'], description: 'This cheatsheet' },
    ],
  },
  {
    group: 'Finance',
    items: [
      { keys: ['A'], description: 'Add transaction' },
      { keys: ['Ctrl', 'F'], description: 'Filter transactions' },
    ],
  },
  {
    group: 'Books',
    items: [
      { keys: ['A'], description: 'Add book' },
      { keys: ['S'], description: 'Update reading status' },
    ],
  },
  {
    group: 'Habits',
    items: [
      { keys: ['1–9'], description: 'Quick-log habit by position' },
      { keys: ['J'], description: 'New journal entry' },
    ],
  },
  {
    group: 'Notes',
    items: [
      { keys: ['Ctrl', 'Shift', 'N'], description: 'New note' },
      { keys: ['[['], description: 'Insert backlink' },
    ],
  },
];

export function ShortcutCheatsheet() {
  const { isShortcutCheatsheetOpen, setShortcutCheatsheetOpen } = useShortcutStore();

  if (!isShortcutCheatsheetOpen) return null;

  return (
    <div className="fixed inset-0 z-50" id="shortcut-cheatsheet">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={() => setShortcutCheatsheetOpen(false)}
      />

      {/* Sheet */}
      <div className="absolute left-1/2 top-[10%] w-full max-w-2xl -translate-x-1/2 animate-slide-down">
        <div className="rounded-xl border border-border bg-popover shadow-2xl shadow-black/40 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">Keyboard Shortcuts</h2>
            <button
              onClick={() => setShortcutCheatsheetOpen(false)}
              className="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Content */}
          <div className="max-h-[70vh] overflow-y-auto p-4">
            <div className="grid grid-cols-2 gap-6">
              {shortcuts.map((group) => (
                <div key={group.group}>
                  <h3 className="mb-2 text-2xs font-medium uppercase tracking-wider text-muted-foreground">
                    {group.group}
                  </h3>
                  <div className="space-y-1">
                    {group.items.map((item) => (
                      <div
                        key={item.description}
                        className="flex items-center justify-between py-0.5"
                      >
                        <span className="text-[13px] text-foreground">{item.description}</span>
                        <div className="flex gap-1">
                          {item.keys.map((key, i) => (
                            <span key={i} className="kbd">
                              {key}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

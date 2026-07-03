'use client';

import { Search, Plus } from 'lucide-react';
import { ThemeToggle } from '@/components/theme-toggle';
import { useShortcutStore } from '@/hooks/use-keyboard-shortcuts';
import { usePathname } from 'next/navigation';

const pathNames: Record<string, string> = {
  '/': 'Home',
  '/finance': 'Finance',
  '/finance/accounts': 'Accounts',
  '/finance/transactions': 'Transactions',
  '/books': 'Books',
  '/habits': 'Habits & Journal',
  '/notes': 'Notes',
  '/tools': 'Tools',
  '/agent-inbox': 'Agent Inbox',
};

export function Header() {
  const pathname = usePathname();
  const { setCommandPaletteOpen, setQuickCaptureOpen } = useShortcutStore();

  const title = pathNames[pathname] || 'WarBorn OS';

  return (
    <header className="sticky top-0 z-20 flex h-12 items-center border-b border-border bg-background/80 backdrop-blur-sm px-4 gap-3" id="header">
      {/* Title / Breadcrumb */}
      <h1 className="text-sm font-semibold text-foreground">{title}</h1>

      <div className="flex-1" />

      {/* Search trigger */}
      <button
        onClick={() => setCommandPaletteOpen(true)}
        className="inline-flex items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-1 text-[13px] text-muted-foreground hover:bg-accent transition-colors"
        id="search-trigger"
      >
        <Search className="h-3.5 w-3.5" />
        <span>Search...</span>
        <span className="kbd">Ctrl+K</span>
      </button>

      {/* Quick capture */}
      <button
        onClick={() => setQuickCaptureOpen(true)}
        className="inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        aria-label="Quick capture"
        id="quick-capture-trigger"
      >
        <Plus className="h-4 w-4" />
      </button>

      {/* Theme toggle */}
      <ThemeToggle />
    </header>
  );
}

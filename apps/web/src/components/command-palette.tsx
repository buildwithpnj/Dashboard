'use client';

import { Command } from 'cmdk';
import { useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Wallet,
  BookOpen,
  Target,
  StickyNote,
  Wrench,
  Inbox,
  Plus,
  Search,
} from 'lucide-react';
import { useShortcutStore } from '@/hooks/use-keyboard-shortcuts';
import { useEffect } from 'react';

const navigationItems = [
  { label: 'Home', icon: LayoutDashboard, href: '/', shortcut: 'G D' },
  { label: 'Finance', icon: Wallet, href: '/finance', shortcut: 'G F' },
  { label: 'Books', icon: BookOpen, href: '/books', shortcut: 'G B' },
  { label: 'Habits & Journal', icon: Target, href: '/habits', shortcut: 'G H' },
  { label: 'Notes', icon: StickyNote, href: '/notes', shortcut: 'G N' },
  { label: 'Tools', icon: Wrench, href: '/tools', shortcut: 'G T' },
  { label: 'Agent Inbox', icon: Inbox, href: '/agent-inbox', shortcut: '⌘⇧A' },
];

const actionItems = [
  { label: 'New Transaction', icon: Plus, action: 'new-transaction' },
  { label: 'New Account', icon: Plus, action: 'new-account' },
  { label: 'New Book', icon: Plus, action: 'new-book' },
  { label: 'New Note', icon: Plus, action: 'new-note' },
  { label: 'New Journal Entry', icon: Plus, action: 'new-journal' },
];

export function CommandPalette() {
  const router = useRouter();
  const { isCommandPaletteOpen, setCommandPaletteOpen, setQuickCaptureOpen } =
    useShortcutStore();

  // Cmd+K toggle
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCommandPaletteOpen(!isCommandPaletteOpen);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [isCommandPaletteOpen, setCommandPaletteOpen]);

  if (!isCommandPaletteOpen) return null;

  return (
    <div className="fixed inset-0 z-50" id="command-palette">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in"
        onClick={() => setCommandPaletteOpen(false)}
      />

      {/* Command dialog */}
      <div className="absolute left-1/2 top-[20%] w-full max-w-lg -translate-x-1/2 animate-slide-down">
        <Command
          className="rounded-xl border border-border bg-popover shadow-2xl shadow-black/40 overflow-hidden"
          label="Command palette"
        >
          <div className="flex items-center border-b border-border px-3">
            <Search className="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
            <Command.Input
              placeholder="Type a command or search..."
              className="flex h-11 w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
              autoFocus
            />
          </div>

          <Command.List className="max-h-72 overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>

            <Command.Group
              heading="Navigation"
              className="text-2xs font-medium uppercase tracking-wider text-muted-foreground px-2 py-1.5"
            >
              {navigationItems.map((item) => (
                <Command.Item
                  key={item.href}
                  onSelect={() => {
                    router.push(item.href);
                    setCommandPaletteOpen(false);
                  }}
                  className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[13px] text-foreground cursor-pointer data-[selected=true]:bg-accent transition-colors"
                >
                  <item.icon className="h-4 w-4 text-muted-foreground" />
                  <span className="flex-1">{item.label}</span>
                  <span className="kbd">{item.shortcut}</span>
                </Command.Item>
              ))}
            </Command.Group>

            <Command.Separator className="mx-2 my-1 h-px bg-border" />

            <Command.Group
              heading="Actions"
              className="text-2xs font-medium uppercase tracking-wider text-muted-foreground px-2 py-1.5"
            >
              {actionItems.map((item) => (
                <Command.Item
                  key={item.action}
                  onSelect={() => {
                    setCommandPaletteOpen(false);
                    if (item.action === 'new-transaction') {
                      router.push('/finance?action=new-transaction');
                    } else if (item.action === 'new-account') {
                      router.push('/finance/accounts?action=new-account');
                    } else {
                      setQuickCaptureOpen(true);
                    }
                  }}
                  className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[13px] text-foreground cursor-pointer data-[selected=true]:bg-accent transition-colors"
                >
                  <item.icon className="h-4 w-4 text-muted-foreground" />
                  <span>{item.label}</span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}

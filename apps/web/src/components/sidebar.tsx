'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Terminal,
  StickyNote,
  BookOpen,
  Briefcase,
  BookMarked,
  Image,
  Film,
  HardDrive,
  Calendar,
  Cpu,
  Settings,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Target,
  Flame,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { create } from 'zustand';

interface SidebarState {
  collapsed: boolean;
  toggle: () => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
  collapsed: false,
  toggle: () => set((s) => ({ collapsed: !s.collapsed })),
}));

const navItems = [
  { href: '/dashboard', label: 'Mission Control', icon: LayoutDashboard, shortcut: 'G M' },
  { href: '/workspace', label: 'Workspace', icon: Terminal, shortcut: 'G W' },
  { href: '/notes', label: 'Notes', icon: StickyNote, shortcut: 'G N' },
  { href: '/knowledge', label: 'Knowledge Base', icon: BookOpen, shortcut: 'G K' },
  { href: '/projects-dashboard', label: 'Projects', icon: Briefcase, shortcut: 'G P' },
  { href: '/books', label: 'Books', icon: BookMarked, shortcut: 'G B' },
  { href: '/assets', label: 'Assets', icon: Image, shortcut: 'G A' },
  { href: '/media', label: 'Media', icon: Film, shortcut: 'G H' },
  { href: '/storage', label: 'Storage Manager', icon: HardDrive, shortcut: 'G S' },
  { href: '/calendar', label: 'Calendar', icon: Calendar, shortcut: 'G C' },
  { href: '/habits', label: 'Habits', icon: Target, shortcut: 'G L' },
  { href: '/recovery', label: 'Quit Addiction', icon: Flame, shortcut: 'G Q' },
  { href: '/ai-memory', label: 'AI Memory', icon: Cpu, shortcut: 'G I' },
  { href: '/settings', label: 'Settings', icon: Settings, shortcut: 'G E' },
  { href: '/trash', label: 'Trash', icon: Trash2, shortcut: 'G R' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { collapsed, toggle } = useSidebarStore();

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-30 flex h-screen flex-col border-r border-[#1E2024] bg-[#0B0C0E] transition-all duration-200',
        collapsed ? 'w-14' : 'w-52'
      )}
      id="sidebar"
    >
      {/* Logo */}
      <div className="flex h-12 items-center justify-between border-b border-[#1E2024] px-3">
        {!collapsed && (
          <span className="text-xs font-semibold tracking-wider text-[#E4E6EB] uppercase font-mono">
            Warborn<span className="text-[#FFB000]">.OS</span>
          </span>
        )}
        <button
          onClick={toggle}
          className={cn(
            'inline-flex items-center justify-center rounded p-1 text-[#60646C] hover:bg-[#111315] hover:text-[#E4E6EB] transition-colors',
            collapsed && 'mx-auto'
          )}
          aria-label="Toggle sidebar"
          id="sidebar-toggle"
        >
          {collapsed ? (
            <ChevronRight className="h-3.5 w-3.5" />
          ) : (
            <ChevronLeft className="h-3.5 w-3.5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-3 px-1.5 space-y-1">
        {navItems.map((item) => {
          const isActive =
            item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'group relative flex items-center gap-2.5 rounded px-2.5 py-1.5 text-xs font-medium transition-colors',
                isActive
                  ? 'bg-[#16191D] text-[#E4E6EB]'
                  : 'text-[#60646C] hover:bg-[#111315] hover:text-[#E4E6EB]'
              )}
              id={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              {/* Active left marker */}
              {isActive && (
                <span className="absolute left-0 top-1/4 bottom-1/4 w-[2px] bg-[#FFB000] rounded-r" />
              )}
              <item.icon className={cn("h-3.5 w-3.5 flex-shrink-0 transition-colors", isActive ? "text-[#FFB000]" : "text-[#60646C] group-hover:text-[#E4E6EB]")} />
              {!collapsed && (
                <>
                  <span className="flex-1 tracking-wide">{item.label}</span>
                  <span className="text-[9px] font-mono text-[#60646C]/60 opacity-0 group-hover:opacity-100 transition-opacity">
                    {item.shortcut}
                  </span>
                </>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="border-t border-[#1E2024] p-3">
          <p className="text-[10px] font-mono text-[#60646C]">
            <span className="text-[#FFB000] font-semibold">?</span> HELP & SHORTCUTS
          </p>
        </div>
      )}
    </aside>
  );
}

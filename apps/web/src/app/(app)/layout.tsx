'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/use-auth';
import { useKeyboardShortcuts } from '@/hooks/use-keyboard-shortcuts';
import { Sidebar, useSidebarStore } from '@/components/sidebar';
import { Header } from '@/components/header';
import { CommandPalette } from '@/components/command-palette';
import { ShortcutCheatsheet } from '@/components/shortcut-cheatsheet';
import { QuickCapture } from '@/components/quick-capture';
import { cn } from '@/lib/utils';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, fetchUser } = useAuth();
  const { collapsed } = useSidebarStore();

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // Register global keyboard shortcuts
  useKeyboardShortcuts((path) => router.push(path));

  // Auth guard
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3 animate-fade-in">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground border-t-primary" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar />
      <div
        className={cn(
          'transition-all duration-200',
          collapsed ? 'ml-14' : 'ml-52'
        )}
      >
        <Header />
        <main className="p-4">{children}</main>
      </div>

      {/* Overlays */}
      <CommandPalette />
      <ShortcutCheatsheet />
      <QuickCapture />
    </div>
  );
}

'use client';

import { useEffect, useRef, useCallback } from 'react';
import { create } from 'zustand';

interface ShortcutState {
  pendingSequence: string | null;
  setPendingSequence: (key: string | null) => void;
  isCommandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;
  isShortcutCheatsheetOpen: boolean;
  setShortcutCheatsheetOpen: (open: boolean) => void;
  isQuickCaptureOpen: boolean;
  setQuickCaptureOpen: (open: boolean) => void;
}

export const useShortcutStore = create<ShortcutState>((set) => ({
  pendingSequence: null,
  setPendingSequence: (key) => set({ pendingSequence: key }),
  isCommandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ isCommandPaletteOpen: open }),
  isShortcutCheatsheetOpen: false,
  setShortcutCheatsheetOpen: (open) => set({ isShortcutCheatsheetOpen: open }),
  isQuickCaptureOpen: false,
  setQuickCaptureOpen: (open) => set({ isQuickCaptureOpen: open }),
}));

function isEditableElement(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) return false;
  const tag = target.tagName;
  return (
    tag === 'INPUT' ||
    tag === 'TEXTAREA' ||
    tag === 'SELECT' ||
    target.isContentEditable
  );
}

export function useKeyboardShortcuts(
  navigate: (path: string) => void,
  moduleShortcuts?: Record<string, () => void>
) {
  const sequenceTimer = useRef<NodeJS.Timeout | null>(null);
  const {
    pendingSequence,
    setPendingSequence,
    setCommandPaletteOpen,
    setShortcutCheatsheetOpen,
    setQuickCaptureOpen,
  } = useShortcutStore();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't capture shortcuts when typing in inputs
      if (isEditableElement(e.target)) return;

      const key = e.key.toLowerCase();
      const isMod = e.metaKey || e.ctrlKey;

      // ─── Mod combos ──────────────────────────────────
      if (isMod && key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
        return;
      }

      if (isMod && key === 'n') {
        e.preventDefault();
        setQuickCaptureOpen(true);
        return;
      }

      if (isMod && e.shiftKey && key === 'a') {
        e.preventDefault();
        navigate('/agent-inbox');
        return;
      }

      // ─── Sequence shortcuts (G then X) ───────────────
      if (pendingSequence === 'g') {
        e.preventDefault();
        const routes: Record<string, string> = {
          d: '/',
          f: '/finance',
          b: '/books',
          h: '/habits',
          n: '/notes',
          t: '/tools',
        };
        if (routes[key]) {
          navigate(routes[key]);
        }
        setPendingSequence(null);
        if (sequenceTimer.current) {
          clearTimeout(sequenceTimer.current);
          sequenceTimer.current = null;
        }
        return;
      }

      if (key === 'g' && !isMod) {
        setPendingSequence('g');
        sequenceTimer.current = setTimeout(() => {
          setPendingSequence(null);
        }, 500);
        return;
      }

      // ─── Single-key shortcuts ────────────────────────
      if (key === '/' && !isMod) {
        e.preventDefault();
        setCommandPaletteOpen(true);
        return;
      }

      if (key === '?' && !isMod) {
        e.preventDefault();
        setShortcutCheatsheetOpen(true);
        return;
      }

      if (key === 'escape') {
        setCommandPaletteOpen(false);
        setShortcutCheatsheetOpen(false);
        setQuickCaptureOpen(false);
        return;
      }

      // ─── Module-level shortcuts ──────────────────────
      if (moduleShortcuts && moduleShortcuts[key]) {
        e.preventDefault();
        moduleShortcuts[key]();
      }
    },
    [
      pendingSequence,
      setPendingSequence,
      setCommandPaletteOpen,
      setShortcutCheatsheetOpen,
      setQuickCaptureOpen,
      navigate,
      moduleShortcuts,
    ]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}

'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Command, Github } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/components/theme-toggle';

interface NavLink {
  label: string;
  href: string;
}

const navLinks: NavLink[] = [
  { label: 'Projects', href: '/projects' },
  { label: 'Labs', href: '/labs' },
  { label: 'Journal', href: '/journal' },
  { label: 'About', href: '/about' },
  { label: 'Contact', href: '/contact' },
  { label: 'Mission Control', href: '/mission-control' },
];

export function PublicHeader() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // 1. Listen to scroll events to toggle floating island styling
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 15) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 2. Lock body scroll when mobile menu overlay is active
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  return (
    <header className="sticky top-0 z-50 w-full transition-all duration-300 py-3 sm:py-4 px-4 sm:px-6 lg:px-8">
      {/* Floating Island Navigation bar container */}
      <div className={cn(
        "max-w-7xl mx-auto rounded-2xl border transition-all duration-300 flex items-center justify-between",
        scrolled 
          ? "h-12 sm:h-14 px-4 sm:px-6 bg-background/70 backdrop-blur-md border-border/40 shadow-[0_12px_40px_rgba(0,0,0,0.12)]" 
          : "h-14 sm:h-16 px-5 sm:px-8 bg-transparent border-transparent"
      )}>
        
        {/* Brand / Logo */}
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="relative">
              <span className="font-pixel text-xl sm:text-2xl tracking-widest text-primary group-hover:text-foreground transition-colors duration-200">
                PNJ
              </span>
              <span className="absolute -top-1 -right-2 text-[7px] font-mono text-emerald-400 opacity-60 group-hover:opacity-100 transition-opacity">v1.2</span>
            </div>
            <span className="hidden sm:inline font-mono text-[9px] text-muted-foreground mt-1.5 tracking-wider uppercase opacity-60 group-hover:opacity-100 transition-opacity">
              {"// AI_LABS"}
            </span>
          </Link>

          {/* Pulse network status */}
          <span className="hidden lg:inline-flex items-center gap-1.5 font-mono text-[8px] text-muted-foreground/80 px-2 py-0.5 rounded border border-border/30 bg-secondary/30 ml-4 uppercase tracking-widest">
            <span className="h-1 w-1 rounded-full bg-emerald-500 animate-pulse" />
            SYSTEM ONLINE
          </span>
        </div>

        {/* Desktop Nav Links (High performance CSS background hover pills) */}
        <nav className="hidden md:flex items-center gap-1.5 bg-secondary/20 p-1 rounded-full border border-border/20 backdrop-blur-sm">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  'text-[10px] font-mono font-bold tracking-wider uppercase px-3.5 py-1.5 rounded-full transition-all duration-300 border relative',
                  isActive 
                    ? 'text-primary bg-primary/10 border-primary/20 shadow-[0_2px_10px_rgba(59,130,246,0.05)]' 
                    : 'text-muted-foreground hover:text-primary hover:bg-primary/5 hover:border-primary/10 border-transparent'
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* System Toolbar Options (Search trigger, Github logo, ThemeToggle) */}
        <div className="hidden md:flex items-center gap-2">
          <button
            onClick={() => {
              const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true });
              window.dispatchEvent(event);
            }}
            className="flex items-center gap-2 h-8 px-2.5 text-[10px] font-mono rounded-lg border border-border/50 bg-secondary/30 hover:bg-secondary/80 text-muted-foreground transition-all hover:text-foreground hover:border-primary/20 hover:shadow-[0_0_12px_rgba(59,130,246,0.04)]"
          >
            <Command className="h-2.5 w-2.5" />
            <span>SEARCH</span>
            <kbd className="text-[8px] bg-background/80 px-1 py-0.5 rounded border border-border/40 font-sans">
              ⌘K
            </kbd>
          </button>
          
          <a
            href="https://github.com/buildwithpnj"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center h-8 w-8 rounded-lg border border-border/50 bg-secondary/30 text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all"
          >
            <Github className="h-3.5 w-3.5" />
          </a>

          <div className="h-8 w-8 rounded-lg border border-border/50 bg-secondary/30 flex items-center justify-center">
            <ThemeToggle />
          </div>
        </div>

        {/* Mobile Hamburger toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden flex items-center justify-center p-2 rounded-xl text-muted-foreground hover:text-foreground hover:bg-accent transition-all"
        >
          {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile Menu Fullscreen Glass Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 top-16 z-30 bg-background/95 backdrop-blur-md flex flex-col justify-between p-6 animate-fade-in border-t border-border/20">
          <nav className="flex flex-col gap-2">
            <div className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest pb-2 mb-2 border-b border-border/20">
              Navigation
            </div>
            {navLinks.map((link) => {
              const isActive = pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    'text-base font-mono font-bold py-2 px-3 rounded-lg border transition-all duration-300',
                    isActive 
                      ? 'text-primary bg-primary/10 border-primary/20' 
                      : 'text-muted-foreground hover:text-primary hover:bg-primary/5 hover:border-primary/10 border-transparent'
                  )}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  setTimeout(() => {
                    const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true });
                    window.dispatchEvent(event);
                  }, 200);
                }}
                className="flex flex-1 items-center justify-center gap-2 h-10 rounded-lg border border-border/50 bg-secondary/30 text-muted-foreground text-xs font-mono font-bold"
              >
                <Command className="h-3.5 w-3.5" />
                <span>SEARCH CONSOLE</span>
              </button>
              <div className="shrink-0 h-10 w-10 rounded-lg border border-border/50 bg-secondary/30 flex items-center justify-center">
                <ThemeToggle />
              </div>
            </div>
            <div className="flex justify-center gap-6 py-2 border-t border-border/20 pt-4 text-xs font-mono">
              <a href="https://github.com/buildwithpnj" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">GitHub</a>
              <a href="https://twitter.com/buildwithpnj" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">Twitter</a>
              <a href="https://linkedin.com/in/pnj" target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">LinkedIn</a>
            </div>
            <div className="text-center text-[10px] font-mono text-muted-foreground">
              © 2026 BuildWithPNJ. All rights reserved.
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

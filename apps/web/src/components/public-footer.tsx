import React from 'react';
import Link from 'next/link';
import { FooterDataStream } from './footer-data-stream';

export function PublicFooter() {
  const currentYear = new Date().getFullYear();

  return (
    <footer id="section-footer" className="w-full border-t border-border bg-background pt-8 md:pt-10 mt-20 relative z-20">
      
      {/* ── Full-bleed AI Data Stream (no container constraint) ── */}
      <div className="w-full px-4 sm:px-6 lg:px-8 mb-10">
        <FooterDataStream />
      </div>

      {/* ── Contained footer links ── */}
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12 md:pb-16 flex flex-col gap-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 lg:gap-12 text-left">
          
          {/* Brand Column */}
          <div className="md:col-span-2 flex flex-col gap-4">
            <Link href="/" className="font-pixel text-2xl tracking-widest text-primary">
              PNJ
            </Link>
            <p className="text-sm text-muted-foreground max-w-sm leading-relaxed">
              AI Engineer building production-ready systems in public. Sharing architecture decisions, codebase iterations, and practical learnings.
            </p>
          </div>

          {/* Navigation Links Column */}
          <div className="flex flex-col gap-3">
            <h4 className="font-pixel text-xs text-foreground uppercase tracking-wider">{"// NAVIGATE"}</h4>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-foreground transition-colors">Home</Link>
              <Link href="/projects" className="hover:text-foreground transition-colors">Projects</Link>
              <Link href="/labs" className="hover:text-foreground transition-colors">Labs</Link>
              <Link href="/journal" className="hover:text-foreground transition-colors">Journal</Link>
              <Link href="/about" className="hover:text-foreground transition-colors">About</Link>
              <Link href="/contact" className="hover:text-foreground transition-colors">Contact</Link>
              <Link href="/mission-control" className="hover:text-foreground transition-colors">Mission Control</Link>
            </div>
          </div>

          {/* Connect Column */}
          <div className="flex flex-col gap-3">
            <h4 className="font-pixel text-xs text-foreground uppercase tracking-wider">{"// CONNECT"}</h4>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <a href="https://github.com/buildwithpnj" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub ↗</a>
              <a href="https://www.linkedin.com/in/buildwithpnj/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">LinkedIn ↗</a>
              <a href="https://www.youtube.com/@buildwithPNJ" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">YouTube ↗</a>
              <a href="https://www.instagram.com/buildwithpnj/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Instagram ↗</a>
              <a href="https://www.threads.net/@buildwithpnj" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Threads ↗</a>
              <a href="https://dev.to/buildwithpnj" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Dev.to ↗</a>
              <a href="https://www.reddit.com/user/Diamond_1974/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Reddit ↗</a>
              <a href="https://www.facebook.com/buildwithpnj/" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Facebook ↗</a>
              <a href="mailto:hello@buildwithpnj.in" className="hover:text-foreground transition-colors">Email ↗</a>
            </div>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-4 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-muted-foreground text-center sm:text-left">
            &copy; {currentYear} BuildWithPNJ. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}


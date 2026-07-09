import React from 'react';
import { Activity, GitCommit, Flame, BookOpen, Layers, CheckCircle2 } from 'lucide-react';
import { getProjects, getBlogPosts } from '@/lib/content';
import { cn } from '@/lib/utils';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

export const metadata = {
  title: 'Mission Control — BuildWithPNJ',
  description: 'Live telemetry command center of BuildWithPNJ. Track real-time developer metrics, GitHub commits heatmap, and roadmap milestones.',
};

export default function PublicMissionControlPage() {
  const projects = getProjects();
  const posts = getBlogPosts();

  // Attempt to load real Git commits and heatmap data from all local repositories (with 5-minute file caching)
  let commitsList: { hash: string; subject: string; author: string; date: string; project: string }[] = [];
  let totalCommits = 0;
  let heatmapCells: number[] = [];
  let gitEnabled = false;

  const cacheFile = path.join(process.cwd(), '.telemetry_cache.json');
  let cacheValid = false;

  if (fs.existsSync(cacheFile)) {
    try {
      const stats = fs.statSync(cacheFile);
      const now = Date.now();
      if (now - stats.mtimeMs < 300000) { // 5-minute cache validation
        const cachedData = JSON.parse(fs.readFileSync(cacheFile, 'utf-8'));
        commitsList = cachedData.commitsList;
        totalCommits = cachedData.totalCommits;
        heatmapCells = cachedData.heatmapCells;
        gitEnabled = cachedData.gitEnabled;
        cacheValid = true;
      }
    } catch (e) {
      // Ignore cache load failure and rebuild
    }
  }

  if (!cacheValid) {
    const dateCounts: Record<string, number> = {};
    try {
      const baseProjectsDir = 'C:\\Users\\praka\\my-github-projects';
      if (fs.existsSync(baseProjectsDir)) {
        const dirs = fs.readdirSync(baseProjectsDir);
        const allCommits: { hash: string; subject: string; author: string; date: string; timestamp: number; project: string }[] = [];

        for (const dir of dirs) {
          const projPath = path.join(baseProjectsDir, dir);
          if (!fs.statSync(projPath).isDirectory()) continue;

          const gitDir = path.join(projPath, '.git');
          if (fs.existsSync(gitDir)) {
            try {
              // Get commits from this directory
              const gitLog = execSync('git log -n 10 --pretty=format:"%h|%s|%an|%ad|%at" --date=short', { 
                cwd: projPath, 
                encoding: 'utf-8',
                stdio: ['pipe', 'pipe', 'ignore']
              });

              gitLog.split('\n').filter(Boolean).forEach(line => {
                const [hash, subject, author, date, timestampStr] = line.split('|');
                const timestamp = parseInt(timestampStr, 10) || 0;
                allCommits.push({
                  hash,
                  subject: subject || 'No commit message',
                  author: author || 'Unknown',
                  date: date || '',
                  timestamp,
                  project: dir
                });
              });

              // Count all commits for heatmap
              const gitDates = execSync('git log --pretty=format:"%ad" --date=short', { 
                cwd: projPath, 
                encoding: 'utf-8',
                stdio: ['pipe', 'pipe', 'ignore']
              });
              gitDates.split('\n').filter(Boolean).forEach(date => {
                dateCounts[date] = (dateCounts[date] || 0) + 1;
                totalCommits++;
              });
              gitEnabled = true;
            } catch (e) {
              // Skip directory on git failure
            }
          }
        }

        // Sort all commits by timestamp descending and take the top 6
        allCommits.sort((a, b) => b.timestamp - a.timestamp);
        commitsList = allCommits.slice(0, 6).map(c => ({
          hash: c.hash,
          subject: c.subject,
          author: c.author,
          date: c.date,
          project: c.project
        }));
      }
    } catch (err) {
      // Ignore directory listing failures
    }

    // Populate heatmap cells based on accumulated dates or mock fallbacks
    if (gitEnabled) {
      const today = new Date();
      for (let i = 0; i < 52 * 7; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() - (52 * 7 - 1 - i));
        const dateStr = d.toISOString().split('T')[0];
        const count = dateCounts[dateStr] || 0;
        let density = 0;
        if (count > 0) {
          if (count <= 1) density = 1;
          else if (count <= 3) density = 2;
          else if (count <= 5) density = 3;
          else density = 4;
        }
        heatmapCells.push(density);
      }
    } else {
      // Fallback mock logs if git command is not available (e.g. serverless containers)
      totalCommits = 880;
      commitsList = [
        { hash: 'c2ab969', subject: 'fix(api): replace asyncio.run() seeding with synchronous psycopg2 seed to eliminate event loop corruption on login', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' },
        { hash: '21a52f5', subject: 'fix(alembic): escape percent signs for configparser in env.py', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' },
        { hash: '562c032', subject: 'fix(api): disable statement cache in SQLAlchemy and Alembic for PgBouncer compatibility', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' },
        { hash: '21c555e', subject: 'feat(homepage): Module 2.3 — Propagate dynamic photo-synced colors globally across entire homepage', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' },
        { hash: 'c00a210', subject: 'feat(hero): Module 1.3 — Extract dominant pixel color from portrait and synchronize system glows', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' },
        { hash: 'ca41b76', subject: 'feat(telemetry): Implement SystemTelemetryTicker LED status bar and biometric laser sweep on about page', author: 'buildwithpnj', date: '2026-07-09', project: 'Dashboard' }
      ];
      heatmapCells = Array.from({ length: 52 * 7 }, (_, i) => {
        const factor = Math.sin(i / 15) * Math.cos(i / 30);
        return Math.max(0, Math.floor((factor + 0.5) * 4));
      });
    }

    // Write generated telemetry stats to cache file
    try {
      fs.writeFileSync(cacheFile, JSON.stringify({
        commitsList,
        totalCommits,
        heatmapCells,
        gitEnabled
      }), 'utf-8');
    } catch (e) {
      // Ignore cache write errors
    }
  }

  // Heatmap block color mappings
  const getHeatmapColorClass = (density: number) => {
    switch (density) {
      case 0: return 'bg-muted/30 border border-border/10';
      case 1: return 'bg-primary/20 border border-primary/10';
      case 2: return 'bg-primary/40 border border-primary/20';
      case 3: return 'bg-primary/65 border border-primary/40';
      case 4: return 'bg-primary border border-primary/60 shadow-[0_0_8px_rgba(59,130,246,0.3)]';
      default: return 'bg-muted/30';
    }
  };

  return (
    <div className="flex flex-col gap-8 select-none text-left">
      
      {/* Page Title / Telemetry Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div className="flex flex-col gap-1">
          <div className="font-pixel text-[11px] text-primary tracking-wider uppercase">{"// SYSTEMS TELEMETRY"}</div>
          <h1 className="text-3xl sm:text-4xl font-pixel text-foreground">Mission Control</h1>
        </div>
        
        {/* Systems Online pulsing indicator */}
        <div className="self-start sm:self-auto inline-flex items-center gap-2 h-9 px-4 rounded-xl border border-primary/10 bg-primary/5 text-xs text-primary font-pixel uppercase tracking-widest">
          <span className="w-2 h-2 rounded-full bg-primary animate-ping" />
          Systems Online
        </div>
      </div>

      {/* ROW 1: Key Metrics (4-col grid) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-5 rounded-2xl border border-border bg-card border-t-2 border-t-primary flex flex-col gap-2 relative overflow-hidden">
          <GitCommit className="h-4 w-4 text-muted-foreground" />
          <div className="font-mono text-3xl font-bold text-primary mt-2">{totalCommits}</div>
          <div className="font-pixel text-[10px] text-muted-foreground tracking-wider uppercase">TOTAL COMMITS</div>
          <span className="text-[10px] text-positive mt-1 font-mono">{gitEnabled ? '+34 total' : '+23 this week'}</span>
        </div>

        <div className="p-5 rounded-2xl border border-border bg-card border-t-2 border-t-primary flex flex-col gap-2">
          <Flame className="h-4 w-4 text-muted-foreground" />
          <div className="font-mono text-3xl font-bold text-primary mt-2">42</div>
          <div className="font-pixel text-[10px] text-muted-foreground tracking-wider uppercase">DAY STREAK</div>
          <span className="text-[10px] text-muted-foreground mt-1 font-mono">longest: 67 days</span>
        </div>

        <div className="p-5 rounded-2xl border border-border bg-card border-t-2 border-t-primary flex flex-col gap-2">
          <BookOpen className="h-4 w-4 text-muted-foreground" />
          <div className="font-mono text-3xl font-bold text-primary mt-2">{posts.length}</div>
          <div className="font-pixel text-[10px] text-muted-foreground tracking-wider uppercase">JOURNAL ITEMS</div>
          <span className="text-[10px] text-positive mt-1 font-mono">+{posts.length} total</span>
        </div>

        <div className="p-5 rounded-2xl border border-border bg-card border-t-2 border-t-primary flex flex-col gap-2">
          <Layers className="h-4 w-4 text-muted-foreground" />
          <div className="font-mono text-3xl font-bold text-primary mt-2">{projects.length}</div>
          <div className="font-pixel text-[10px] text-muted-foreground tracking-wider uppercase">ACTIVE BUILDS</div>
          <span className="text-[10px] text-primary mt-1 font-mono">{projects.length} portfolios</span>
        </div>

      </div>

      {/* ROW 2: Focus + Heatmap (2-col: 7fr + 5fr) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Current Focus Sprint */}
        <div className="lg:col-span-7 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// CURRENT FOCUS"}</h3>
          <div className="flex flex-col gap-1">
            <h4 className="text-lg font-bold text-foreground leading-none">Personal OS — Homepage + Deployment</h4>
            <span className="text-xs text-muted-foreground font-mono mt-1 block">Status: Active · Sprint 15 · Jul 9, 2026</span>
          </div>

          <div className="flex flex-col gap-3 font-mono text-xs text-muted-foreground bg-background p-4 rounded-xl border border-border">
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Canvas pixel color extraction → dynamic design system</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>SystemTelemetryTicker LED bar + project terminal sims</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Fix asyncio event loop corruption on Render deploy</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Live login working: prakashjhadps@gmail.com</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-muted-foreground">☐</span>
              <span>Warborn OS dashboard full feature integration</span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="flex flex-col gap-1.5 mt-2">
            <div className="flex justify-between items-center text-xs font-mono">
              <span className="text-muted-foreground">Sprint Progress</span>
              <span className="text-foreground">92%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-background overflow-hidden border border-border">
              <div className="h-full bg-primary rounded-full" style={{ width: '92%' }} />
            </div>
          </div>
        </div>

        {/* Heatmap Grid */}
        <div className="lg:col-span-5 p-6 rounded-2xl border border-border bg-card flex flex-col justify-between gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// GITHUB HEATMAP"}</h3>
          
          {/* Heatmap visualization wrapper */}
          <div className="flex flex-col gap-2">
            <div className="grid grid-flow-col grid-rows-7 gap-[3px] p-2 rounded-xl bg-background border border-border overflow-x-auto">
              {heatmapCells.map((density, idx) => (
                <span 
                  key={idx} 
                  className={cn("w-[6px] h-[6px] rounded-[1px] shrink-0", getHeatmapColorClass(density))} 
                />
              ))}
            </div>
            <div className="flex justify-between items-center text-[10px] text-muted-foreground font-mono mt-1 px-1">
              <span>Less</span>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-[1px] bg-muted/30 border border-border/10" />
                <span className="w-1.5 h-1.5 rounded-[1px] bg-primary/20 border border-primary/10" />
                <span className="w-1.5 h-1.5 rounded-[1px] bg-primary/40 border border-primary/20" />
                <span className="w-1.5 h-1.5 rounded-[1px] bg-primary/65 border border-primary/40" />
                <span className="w-1.5 h-1.5 rounded-[1px] bg-primary border border-primary/60" />
                <span>More</span>
              </div>
            </div>
          </div>

          <div className="text-xs text-muted-foreground leading-relaxed pt-2 border-t border-border font-mono">
            <strong>{gitEnabled ? `${totalCommits} contributions` : '23 contributions'}</strong> tracked across all active repositories.
          </div>
        </div>

      </div>

      {/* ROW 3: Commits Log + Roadmap (2-col: 6fr + 6fr) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Latest Builds/Commits */}
        <div className="lg:col-span-6 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// LATEST BUILDS"}</h3>
          <div className="flex flex-col gap-3 font-mono text-[11px]">
            
            {commitsList.map((c) => (
              <div key={c.hash} className="flex items-start gap-3 p-3 rounded-xl bg-background border border-border">
                <span className="w-2 h-2 rounded-full bg-primary shrink-0 mt-1 shadow-[0_0_8px_rgba(59,130,246,0.4)] animate-pulse" />
                <div className="flex flex-col text-left text-[11px]">
                  <span className="text-foreground font-semibold">{c.subject}</span>
                  <span className="text-muted-foreground mt-0.5">
                    commit {c.hash} ({c.project}) · {c.date} · by <span className="text-primary font-semibold">{c.author}</span>
                  </span>
                </div>
              </div>
            ))}

          </div>
        </div>

        {/* Roadmap Milestones */}
        <div className="lg:col-span-6 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4 justify-between">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// ROADMAP STATUS"}</h3>
          
          <div className="flex flex-col gap-5">
            <div className="flex flex-col gap-1.5 text-left">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-foreground">Q3 2026: Foundation & Telemetry</span>
                <span className="text-primary">78%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-background overflow-hidden border border-border">
                <div className="h-full bg-primary" style={{ width: '78%' }} />
              </div>
            </div>

            <div className="flex flex-col gap-1.5 text-left">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-foreground">Q4 2026: Website Launch & SaaS Beta</span>
                <span className="text-primary">20%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-background overflow-hidden border border-border">
                <div className="h-full bg-primary" style={{ width: '20%' }} />
              </div>
            </div>

            <div className="flex flex-col gap-1.5 text-left">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-foreground">Q1 2027: Modular API Expansion</span>
                <span className="text-muted-foreground">0%</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-background overflow-hidden border border-border">
                <div className="h-full bg-muted" style={{ width: '0%' }} />
              </div>
            </div>
          </div>

          <div className="text-xs text-muted-foreground leading-relaxed font-mono mt-2 pt-3 border-t border-border">
            Phase 1 strategy matches approved ROADMAP.md files.
          </div>
        </div>

      </div>

      {/* ROW 4: Learning + Weekly Goals + Tech Stack (3-col) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Learning */}
        <div className="p-5 rounded-2xl border border-border bg-card flex flex-col gap-3">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// LEARNING QUEUE"}</h3>
          <div className="flex flex-col gap-2 text-xs">
            <div className="p-2 rounded-lg bg-background border border-border">
              <span className="text-foreground font-semibold">Active:</span>
              <p className="text-muted-foreground mt-1">Multi-Agent Orchestration (LangGraph, Python)</p>
            </div>
            <div className="p-2 rounded-lg bg-background border border-border">
              <span className="text-foreground font-semibold">Up Next:</span>
              <p className="text-muted-foreground mt-1">Voice AI Pipelines (Whisper, TTS modules)</p>
            </div>
          </div>
        </div>

        {/* Weekly Goals */}
        <div className="p-5 rounded-2xl border border-border bg-card flex flex-col gap-3">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// WEEKLY TARGETS"}</h3>
          <div className="flex flex-col gap-2.5 font-mono text-[11px] text-muted-foreground text-left">
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Ship canvas portrait color system</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Fix Render deployment + live login</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-positive">☑</span>
              <span>Write engineering journal Day Log</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full border border-border bg-background shrink-0" />
              <span>Warborn OS full dashboard integration</span>
            </div>
          </div>
        </div>

        {/* Tech Stack List */}
        <div className="p-5 rounded-2xl border border-border bg-card flex flex-col gap-3">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// TECH STACK ACTIVE"}</h3>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono text-muted-foreground">
            <span className="p-2 rounded-lg bg-background border border-border text-center">Python</span>
            <span className="p-2 rounded-lg bg-background border border-border text-center">TypeScript</span>
            <span className="p-2 rounded-lg bg-background border border-border text-center">Next.js 15</span>
            <span className="p-2 rounded-lg bg-background border border-border text-center">FastAPI</span>
            <span className="p-2 rounded-lg bg-background border border-border text-center">PostgreSQL</span>
            <span className="p-2 rounded-lg bg-background border border-border text-center">Redis</span>
          </div>
        </div>

      </div>

      {/* ROW 5: AI Models + reach/social stats + Activity Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* AI Models status */}
        <div className="lg:col-span-4 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// AI MODELS ACTIVE"}</h3>
          <div className="flex flex-col gap-3 font-mono text-xs">
            
            <div className="flex items-center justify-between p-2 rounded-xl bg-background border border-border">
              <span>GPT-4o API</span>
              <span className="text-positive text-[10px] uppercase font-bold flex items-center gap-1">🟢 active</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-background border border-border">
              <span>Claude 3.5 Sonnet</span>
              <span className="text-positive text-[10px] uppercase font-bold flex items-center gap-1">🟢 active</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-background border border-border">
              <span>Gemini 2.0 Flash</span>
              <span className="text-positive text-[10px] uppercase font-bold flex items-center gap-1">🟢 active</span>
            </div>

            <div className="flex items-center justify-between p-2 rounded-xl bg-background border border-border opacity-60">
              <span>Llama 3.1 Local</span>
              <span className="text-yellow-500 text-[10px] uppercase font-bold flex items-center gap-1">🟡 evaluation</span>
            </div>

          </div>
        </div>

        {/* Reach / Social Metrics */}
        <div className="lg:col-span-4 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// PUBLIC REACH"}</h3>
          <div className="flex flex-col gap-3 font-mono text-sm text-foreground">
            
            <div className="flex justify-between items-center py-2 border-b border-border">
              <span className="text-muted-foreground">GitHub Stars:</span>
              <span className="font-bold text-primary">312 ★</span>
            </div>

            <div className="flex justify-between items-center py-2 border-b border-border">
              <span className="text-muted-foreground">Twitter Followers:</span>
              <span className="font-bold text-primary">1.2K</span>
            </div>

            <div className="flex justify-between items-center py-2 border-b border-border">
              <span className="text-muted-foreground">LinkedIn Network:</span>
              <span className="font-bold text-primary">847</span>
            </div>

            <div className="flex justify-between items-center py-2">
              <span className="text-muted-foreground">Journal Views:</span>
              <span className="font-bold text-primary">3.2K /mo</span>
            </div>

          </div>
        </div>

        {/* Dynamic Activity Timeline */}
        <div className="lg:col-span-4 p-6 rounded-2xl border border-border bg-card flex flex-col gap-4">
          <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// LAB LOGS"}</h3>
          <div className="flex flex-col border-l border-border pl-3 ml-1 text-xs text-left">
            
            <div className="relative py-2.5">
              <span className="absolute -left-[17px] top-[14px] w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-[9px] font-mono text-muted-foreground">JUL 9 · 21:26</span>
              <p className="text-foreground font-semibold mt-0.5">Fixed asyncio event loop bug — login now works live</p>
            </div>

            <div className="relative py-2.5">
              <span className="absolute -left-[17px] top-[14px] w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-[9px] font-mono text-muted-foreground">JUL 9 · 16:34</span>
              <p className="text-foreground font-semibold mt-0.5">Canvas portrait color sync across full homepage</p>
            </div>

            <div className="relative py-2.5">
              <span className="absolute -left-[17px] top-[14px] w-1.5 h-1.5 rounded-full bg-primary" />
              <span className="text-[9px] font-mono text-muted-foreground">JUL 9 · 15:30</span>
              <p className="text-foreground font-semibold mt-0.5">SystemTelemetryTicker + biometric avatar shipped</p>
            </div>

            <div className="relative py-2.5">
              <span className="absolute -left-[17px] top-[14px] w-1.5 h-1.5 rounded-full bg-primary opacity-50" />
              <span className="text-[9px] font-mono text-muted-foreground">JUL 6</span>
              <p className="text-foreground font-semibold mt-0.5 opacity-60">Portfolio catalog: all 16 repositories indexed</p>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}

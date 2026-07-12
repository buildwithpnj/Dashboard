'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Shield, Sparkles, Key, Zap, CheckCircle2, ArrowRight, Brain, 
  Activity, Cpu, Sliders, Play, Terminal, Database, Check
} from 'lucide-react';
import { PremiumPixelBackground } from '@/components/premium-pixel-background';

export default function WarbornLandingPage() {
  const [emailInput, setEmailInput] = useState('');
  const [waitlistSuccess, setWaitlistSuccess] = useState(false);

  const handleWaitlistSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (emailInput.trim()) {
      setWaitlistSuccess(true);
      setEmailInput('');
    }
  };

  return (
    <div className="min-h-screen text-foreground relative py-12 px-6 sm:px-12 flex flex-col items-center justify-start bg-background">
      {/* Premium Motherboard trace canvas background */}
      <PremiumPixelBackground />

      {/* Hero Section */}
      <div id="hero-section-root" className="relative z-10 max-w-5xl text-center space-y-6 pt-12 pb-20">
        <span className="text-3xs font-mono font-bold uppercase tracking-[0.35em] text-primary bg-primary/5 border border-primary/20 px-3 py-1 rounded-full">
          {"COGNITIVE OPERATING KERNEL"}
        </span>
        <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-none text-foreground">
          {"WARBORN SYSTEM"}
        </h1>
        <p className="text-sm sm:text-base text-muted-foreground max-w-2xl mx-auto leading-relaxed">
          {"An advanced personal AI operating system featuring intent-aware chat interfaces, persistent memory profile layers, and schema-validated safe tool executions."}
        </p>

        {/* CTA Actions */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <Link
            href="/warborn/preview"
            className="h-10 px-6 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 flex items-center gap-2 transition-all shadow-lg shadow-primary/10 text-xs"
          >
            {"Try Preview Sandbox"} <Sparkles className="h-3.5 w-3.5" />
          </Link>
          <Link
            href="/login"
            className="h-10 px-6 rounded-xl border border-border/80 bg-background/95 dark:bg-card/95 hover:bg-muted/20 font-semibold flex items-center gap-2 transition-all text-xs"
          >
            {"Enter Dashboard"} <Key className="h-3.5 w-3.5" />
          </Link>
          <Link
            href="/request-access"
            className="h-10 px-6 rounded-xl border border-transparent text-primary hover:underline font-semibold flex items-center gap-1.5 transition-all text-xs"
          >
            {"Request Credentials"} <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      {/* Section 2: Core Capabilities Grid */}
      <div id="section-mission" className="relative z-10 w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6 py-12 border-t border-border/40">
        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 space-y-4 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[0_12px_36px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_12px_36px_rgba(0,0,0,0.4)] transition-all duration-300">
          <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary">
            <Shield className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-bold text-foreground">{"Production Gated"}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Stateful security sandboxes isolate public runs from core OS databases, keeping user directories secure."}
          </p>
        </div>

        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 space-y-4 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[0_12px_36px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_12px_36px_rgba(0,0,0,0.4)] transition-all duration-300">
          <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary">
            <Zap className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-bold text-foreground">{"Continuous Optimization"}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Utilizing automated gold regression testing benchmarks to monitor model quality and latency budgets."}
          </p>
        </div>

        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 space-y-4 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[0_12px_36px_rgba(0,0,0,0.06)] dark:hover:shadow-[0_12px_36px_rgba(0,0,0,0.4)] transition-all duration-300">
          <div className="h-10 w-10 rounded-xl bg-primary/10 border border-primary/25 flex items-center justify-center text-primary">
            <Key className="h-5 w-5" />
          </div>
          <h3 className="text-sm font-bold text-foreground">{"Tenant Isolation"}</h3>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Authenticated secure session handoffs direct developers to dedicated private cloud workspace modules."}
          </p>
        </div>
      </div>

      {/* Section 3: AI Chat, memory + actions deep dive */}
      <div id="section-solutions" className="relative z-10 w-full max-w-5xl py-16 border-t border-border/40 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="space-y-6 text-left">
          <div className="h-9 w-9 rounded-lg bg-primary/15 flex items-center justify-center text-primary">
            <Brain className="h-5 w-5" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight">{"Personalization Memory & Structured Profiles"}</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Warborn features long-term persistence layers that track grammar weaknesses, mastered correction patterns, tone preferences, and rewrite goals. The agent automatically loads context facts dynamically for each query without spilling sensitive developer keys."}
          </p>
          <ul className="space-y-2 text-xs text-muted-foreground font-mono">
            <li className="flex items-center gap-2">
              <Check className="h-3.5 w-3.5 text-primary shrink-0" /> {"Schema-validated settings updates."}
            </li>
            <li className="flex items-center gap-2">
              <Check className="h-3.5 w-3.5 text-primary shrink-0" /> {"Automated session cleanup after 24 hours."}
            </li>
          </ul>
        </div>

        {/* Profile memory mockup card */}
        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 text-left font-mono space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-border/40 pb-3">
            <span className="text-3xs font-bold text-muted-foreground">{"USER_PROFILE_STATE"}</span>
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>
          <div className="text-3xs space-y-2 text-muted-foreground">
            <div>{"{"}</div>
            <div className="pl-4"><span className="text-primary">{"\"tone\":"}</span> <span className="text-amber-500">{"\"professional\""}</span>,</div>
            <div className="pl-4"><span className="text-primary">{"\"explanation_style\":"}</span> <span className="text-amber-400">{"\"rule-based\""}</span>,</div>
            <div className="pl-4"><span className="text-primary">{"\"weaknesses\":"}</span>{" ["}<span className="text-amber-400">{"\"prepositions\""}</span>, <span className="text-amber-400">{"\"tenses\""}</span>{"],"}</div>
            <div className="pl-4"><span className="text-primary">{"\"corrections_accepted\":"}</span> <span className="text-emerald-400">{"14"}</span>,</div>
            <div className="pl-4"><span className="text-primary">{"\"streak\":"}</span> <span className="text-emerald-400">{"5"}</span></div>
            <div>{"}"}</div>
          </div>
        </div>
      </div>

      {/* Section 4: LifeOS & health operating layer */}
      <div id="section-projects" className="relative z-10 w-full max-w-5xl py-16 border-t border-border/40 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 text-left space-y-4 order-last md:order-first shadow-xl">
          <div className="flex items-center gap-2 border-b border-border/40 pb-3">
            <Activity className="h-4 w-4 text-rose-500" />
            <span className="text-3xs font-mono font-bold text-muted-foreground">{"HEALTH & RELAPSE TRACKERS"}</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-background/95 dark:bg-[#121214] border border-border/40 rounded-xl p-4 text-center">
              <span className="text-3xs font-mono text-muted-foreground">{"CURRENT STREAK"}</span>
              <div className="text-lg font-black text-emerald-400 mt-1">{"14 Days"}</div>
            </div>
            <div className="bg-background/95 dark:bg-[#121214] border border-border/40 rounded-xl p-4 text-center">
              <span className="text-3xs font-mono text-muted-foreground">{"WEEKLY MILESTONE"}</span>
              <div className="text-lg font-black text-primary mt-1">{"Goal Met"}</div>
            </div>
          </div>
        </div>

        <div className="space-y-6 text-left">
          <div className="h-9 w-9 rounded-lg bg-primary/15 flex items-center justify-center text-primary">
            <Activity className="h-5 w-5" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight">{"Integrated LifeOS Layer"}</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Track critical routines, sobriety targets, learning schedules, and cognitive focus goals inside the dashboard console. Warborn uses clean data-structures to keep your goals mapped, auditable, and visible from one central workspace."}
          </p>
        </div>
      </div>

      {/* Section 5: Workflow Automation Trace */}
      <div id="section-labs" className="relative z-10 w-full max-w-5xl py-16 border-t border-border/40 text-center space-y-8">
        <div className="max-w-2xl mx-auto space-y-4">
          <div className="h-9 w-9 rounded-lg bg-primary/15 flex items-center justify-center text-primary mx-auto">
            <Cpu className="h-5 w-5" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight">{"Workflow Automations & Safe Tools Execution"}</h2>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {"Run safe calendar updates, notes synchronization, or vocabulary saves directly from chat prompts. All state-changing actions are subject to user approval loops, preventing unauthorized executions."}
          </p>
        </div>

        <div className="rounded-2xl border border-border/40 bg-background/95 dark:bg-card/95 backdrop-blur-xl p-6 max-w-3xl mx-auto space-y-4 text-left font-mono text-3xs text-muted-foreground shadow-xl">
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <span>{"ACTION_AUDIT_LOG"}</span>
            <span className="text-amber-400">{"PENDING_USER_APPROVAL"}</span>
          </div>
          <div className="space-y-1">
            <div><span className="text-primary">{"Action:"}</span> {"create_followup_practice"}</div>
            <div><span className="text-primary">{"Payload:"}</span> {"{ \"task_description\": \"Review grammar rules on articles\" }"}</div>
            <div><span className="text-primary">{"Requires Approval:"}</span> {"True"}</div>
          </div>
        </div>
      </div>

      {/* Section 6: Action / Waitlist Form CTA */}
      <div id="section-journal" className="relative z-10 w-full max-w-3xl py-20 border-t border-border/40 text-center space-y-8">
        <h2 className="text-2xl font-extrabold tracking-tight">{"Join the Warborn Rollout"}</h2>
        <p className="text-xs text-muted-foreground max-w-md mx-auto leading-relaxed">
          {"Request developer credentials to obtain private system dashboard access, stateful agent sandboxes, and personalized workspace memory."}
        </p>

        {waitlistSuccess ? (
          <div className="max-w-md mx-auto p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5 text-emerald-400 text-xs font-mono">
            {"✓ Application received. We will contact you soon."}
          </div>
        ) : (
          <form onSubmit={handleWaitlistSubmit} className="max-w-md mx-auto flex gap-2">
            <input
              type="email"
              required
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              placeholder="Enter your developer email..."
              className="flex-1 h-10 px-4 rounded-xl border border-border/40 bg-background/95 dark:bg-card/95 text-xs focus:outline-none focus:border-primary/50 text-foreground"
            />
            <button
              type="submit"
              className="h-10 px-5 rounded-xl bg-primary hover:opacity-90 text-primary-foreground font-semibold text-xs transition-all"
            >
              {"Request Access"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

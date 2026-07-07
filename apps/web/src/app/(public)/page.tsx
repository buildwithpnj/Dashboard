import React from 'react';
import Link from 'next/link';
import { 
  ArrowRight, 
  Zap, 
  FlaskConical, 
  Radio, 
  Cpu, 
  Activity, 
  Shield, 
  Layers, 
  Terminal as TerminalIcon 
} from 'lucide-react';
import { getBlogPosts, getProjects, getExperiments } from '@/lib/content';
import { NewsletterForm } from '@/components/newsletter-form';
import { Terminal } from '@/components/ui/terminal';
import { AIPortraitHero } from '@/components/ai-portrait-hero';

export default async function PublicHomePage() {
  const projects = getProjects().slice(0, 3);
  const posts = getBlogPosts().slice(0, 3);
  const experiments = getExperiments().slice(0, 4);

  // Helper to map project categories to premium icons
  const getProjectIcon = (category: string) => {
    switch (category?.toLowerCase()) {
      case 'automation':
        return <Zap className="h-6 w-6 text-primary group-hover:scale-110 transition-transform duration-300" />;
      case 'ai':
      case 'agentic':
        return <Cpu className="h-6 w-6 text-primary group-hover:scale-110 transition-transform duration-300" />;
      case 'system':
      case 'infrastructure':
        return <TerminalIcon className="h-6 w-6 text-primary group-hover:scale-110 transition-transform duration-300" />;
      default:
        return <Layers className="h-6 w-6 text-primary group-hover:scale-110 transition-transform duration-300" />;
    }
  };

  return (
    <div className="flex flex-col gap-0 w-full">
      {/* 1. HERO SECTION (Interactive Portrait Centerpiece & Orbiting Stack) */}
      <AIPortraitHero />
      
      {/* Boxed Content Area */}
      <div className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32 flex flex-col gap-28 md:gap-36 text-left">
        
        {/* 2. MISSION SECTION */}
        <section className="flex flex-col gap-10">
          <div className="flex flex-col gap-3 max-w-3xl">
            <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
              {"// OPERATIONAL MISSION"}
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground leading-tight">
              Architecting production-ready AI products, autonomous agent systems, and context-aware workspaces.
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
              We bypass theoretical delay to ship working software. Explore verified system architectures, database migration post-mortems, and active product blueprints.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 hover:border-primary/25 hover:shadow-[0_8px_30px_rgba(59,130,246,0.02)] transition-all duration-300 group">
              <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center border border-primary/10">
                <Zap className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-bold text-foreground">Production-First Deployment</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                Engineering working software directly to production. Our pipelines favor operational execution over static engineering prototypes.
              </p>
            </div>

            {/* Card 2 */}
            <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 hover:border-primary/25 hover:shadow-[0_8px_30px_rgba(59,130,246,0.02)] transition-all duration-300 group">
              <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center border border-primary/10">
                <Cpu className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-bold text-foreground">Context-Aware Core</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                Constructing stateful, vector-driven pipelines and memory retention models built for daily operational workflows.
              </p>
            </div>

            {/* Card 3 */}
            <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 hover:border-primary/25 hover:shadow-[0_8px_30px_rgba(59,130,246,0.02)] transition-all duration-300 group">
              <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center border border-primary/10">
                <Radio className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-base font-bold text-foreground">Open Architectures</h3>
              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                Publishing complete system designs, database schemas, and codebase blueprints for the developer community.
              </p>
            </div>
          </div>
        </section>
 
        {/* 3. DEDICATED WARBORN OS SECTION */}
        <section className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
              {"// CENTRAL OPERATING ENGINE"}
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
              Autonomous Systems Backend
            </h2>
          </div>
          
          <div className="p-6 sm:p-8 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md relative overflow-hidden flex flex-col lg:flex-row gap-8 items-center hover:border-primary/20 transition-all duration-300 shadow-[0_12px_40px_rgba(0,0,0,0.03)]">
            <div className="absolute top-0 right-0 w-[240px] h-[240px] bg-primary/5 blur-[90px] pointer-events-none" />

            <div className="flex-1 flex flex-col gap-6 w-full text-left">
              <div className="flex flex-col gap-1.5">
                <span className="font-mono text-[9px] font-bold tracking-[0.25em] text-primary uppercase bg-primary/5 border border-primary/10 px-2 py-0.5 rounded w-max">
                  ACTIVE BLUEPRINT
                </span>
                <h3 className="text-2xl sm:text-3xl font-black text-foreground tracking-tight">Warborn OS</h3>
                <p className="text-xs font-mono text-muted-foreground">
                  Secure workflow core for note ingestion, vector-based search, and background sync.
                </p>
              </div>

              <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
                Warborn OS serves as the private operational core of the BuildWithPNJ workspace. Running on Next.js, FastAPI, and PostgreSQL with pgvector, it manages real-time financial tracking, notes archiving, and Google Drive storage synchronization utilizing context-aware local intelligence.
              </p>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 py-4 border-y border-border/40 font-mono text-center sm:text-left">
                <div>
                  <div className="text-lg font-bold text-primary">12</div>
                  <div className="text-[10px] text-muted-foreground uppercase">OS Modules</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-primary">847</div>
                  <div className="text-[10px] text-muted-foreground uppercase">Total Commits</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-primary">9</div>
                  <div className="text-[10px] text-muted-foreground uppercase">Integrations</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-primary">6mo</div>
                  <div className="text-[10px] text-muted-foreground uppercase">Active Dev</div>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-4">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-all active:scale-[0.98] shadow-md shadow-primary/10"
                >
                  Explore Dashboard <ArrowRight className="h-3.5 w-3.5" />
                </Link>
                <Link
                  href="/projects/personal-os"
                  className="text-xs font-medium text-muted-foreground hover:text-foreground border border-border/40 bg-secondary/50 hover:bg-accent px-4 py-2 rounded-xl transition-all"
                >
                  View Architecture
                </Link>
              </div>
            </div>

            <Terminal 
              title="warborn_telemetry.log"
              lines={[
                'API  HTTP/1.1 POST /habits/check_in [200 OK]',
                'TASK celery_worker_1: job_id_894 success',
                'DB   pgvector lookup: notes match 94.6%',
                'MEM  Redis caching keys: 156 initialized',
                'SYNC Google Drive API: 0 changes pending'
              ]}
              className="w-full lg:w-[340px] shrink-0 font-mono"
              showPrompt={true}
            />
          </div>
        </section>

        {/* 4. FEATURED PROJECTS SECTION */}
        <section className="flex flex-col gap-10">
          <div className="flex items-end justify-between border-b border-border/40 pb-4">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
                {"// VERIFIED SHIPS"}
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
                Active Builds
              </h2>
            </div>
            <Link 
              href="/projects" 
              className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              All Projects <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {projects.map((project) => {
              const isProd = project.status?.toLowerCase() === 'production' || project.status?.toLowerCase() === 'stable';
              return (
                <Link
                  key={project.slug}
                  href={`/projects/${project.slug}`}
                  className="group p-5 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-sm flex flex-col gap-4 hover:border-primary/20 hover:shadow-[0_8px_30px_rgba(59,130,246,0.02)] transition-all duration-300"
                >
                  <div className="aspect-video w-full rounded-lg bg-background flex items-center justify-center relative overflow-hidden border border-border/40">
                    <div className="absolute inset-0 grid-dots opacity-30" />
                    {getProjectIcon(project.category)}
                    
                    {/* Status Badge */}
                    <div className="absolute top-2.5 right-2.5 flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[9px] font-bold bg-background/95 backdrop-blur border border-border/40 shadow-sm">
                      <span className={`w-1.5 h-1.5 rounded-full ${isProd ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
                      <span className="text-foreground uppercase font-mono text-[8px]">
                        {project.status}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-1.5">
                    <h3 className="font-bold text-foreground group-hover:text-primary transition-colors text-base">
                      {project.title}
                    </h3>
                    <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                      {project.tagline}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-1 mt-auto pt-3 border-t border-border/40">
                    {project.techStack.slice(0, 3).map((tech) => (
                      <span key={tech} className="text-[9px] font-mono px-2 py-0.5 rounded bg-secondary/80 text-muted-foreground border border-border/30">
                        {tech}
                      </span>
                    ))}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* 5. ENGINEERING JOURNAL PREVIEW */}
        <section className="flex flex-col gap-10">
          <div className="flex items-end justify-between border-b border-border/40 pb-4">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
                {"// TECHNICAL JOURNAL"}
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
                Recent Articles
              </h2>
            </div>
            <Link 
              href="/journal" 
              className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              All Articles <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {posts.map((post) => (
              <Link
                key={post.slug}
                href={`/journal/${post.slug}`}
                className="group p-5 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-sm flex flex-col justify-between gap-5 hover:border-primary/20 hover:shadow-[0_8px_30px_rgba(59,130,246,0.02)] transition-all duration-300"
              >
                <div className="flex flex-col gap-3">
                  <div className="flex items-center gap-2 font-mono text-[9px] text-muted-foreground">
                    <span>{post.publishDate}</span>
                    <span>·</span>
                    <span>{post.readingTime} MIN READ</span>
                  </div>
                  <h3 className="font-bold text-base text-foreground group-hover:text-primary transition-colors leading-snug line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                    {post.excerpt}
                  </p>
                </div>
                <div className="flex flex-wrap gap-1 pt-2 border-t border-border/40">
                  {post.tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-primary/5 text-primary/80 border border-primary/10">
                      #{tag}
                    </span>
                  ))}
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* 6. LABS PREVIEW SECTION */}
        <section className="flex flex-col gap-10">
          <div className="flex items-end justify-between border-b border-border/40 pb-4">
            <div className="flex flex-col gap-2">
              <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
                {"// EXP-LAB EXPERIMENTS"}
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
                R&D Labs
              </h2>
            </div>
            <Link 
              href="/labs" 
              className="flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              Explore Labs <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {experiments.map((exp) => {
              const isActive = exp.status?.toLowerCase() === 'active' || exp.status?.toLowerCase() === 'stable';
              return (
                <Link
                  key={exp.slug}
                  href={`/labs/${exp.slug}`}
                  className="p-5 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-sm hover:bg-secondary/40 hover:border-primary/20 flex flex-col gap-4 transition-all duration-300 group shadow-sm"
                >
                  <div className="w-9 h-9 rounded-xl bg-background flex items-center justify-center border border-border/40">
                    <FlaskConical className="w-4 h-4 text-primary group-hover:scale-110 transition-transform" />
                  </div>
                  <div>
                    <h3 className="text-xs sm:text-sm font-bold text-foreground truncate group-hover:text-primary transition-colors">
                      {exp.title}
                    </h3>
                    <p className="text-[10px] text-muted-foreground truncate font-mono mt-0.5 uppercase tracking-wider">
                      {exp.category}
                    </p>
                  </div>
                  <div className="text-[9px] font-mono text-muted-foreground mt-auto flex items-center gap-1">
                    <span>Status:</span>
                    <span className={isActive ? 'text-emerald-500 font-bold' : 'text-amber-500 font-bold'}>
                      {exp.status?.toUpperCase()}
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* 7. MISSION CONTROL SUMMARY */}
        <section className="p-6 sm:p-8 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md relative overflow-hidden flex flex-col sm:flex-row items-center justify-between gap-6 hover:border-primary/20 transition-all duration-300 shadow-[0_8px_30px_rgba(0,0,0,0.02)]">
          <div className="flex flex-col gap-2 text-left w-full">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-mono text-[9px] text-emerald-400 tracking-[0.2em] uppercase font-bold">
                NETWORK OPERATIONAL: LIVE
              </span>
            </div>
            <h3 className="text-xl font-bold text-foreground">Mission Control Dashboard</h3>
            <p className="text-xs sm:text-sm text-muted-foreground max-w-xl">
              Monitor dynamic engineering logs, live code repository commits telemetry, target grids, and automated core system health meters.
            </p>
          </div>
          <Link
            href="/mission-control"
            className="shrink-0 flex items-center justify-center gap-2 h-10 px-5 rounded-xl text-xs font-semibold border border-border/40 bg-secondary/80 hover:bg-accent text-muted-foreground hover:text-foreground transition-all active:scale-[0.98] shadow-sm"
          >
            Enter Command Center <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </section>

        {/* 8. NEWSLETTER CONTAINER */}
        <section className="py-16 border-t border-border/40 flex flex-col items-center text-center gap-8">
          <div className="flex flex-col gap-3 max-w-md">
            <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
              {"// SYSTEM UPDATES"}
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground tracking-tight">
              Subscribe to the Pipeline
            </h2>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              Get detailed engineering breakdowns, agent system diagrams, and codebase reviews directly in your inbox.
            </p>
          </div>

          <div className="w-full max-w-md p-6 rounded-2xl border border-border/40 bg-card/25 backdrop-blur-md shadow-sm">
            <NewsletterForm />
          </div>
          <span className="text-[10px] text-muted-foreground font-mono">
            No marketing fluff. Opt-out at any time.
          </span>
        </section>

      </div>
    </div>
  );
}

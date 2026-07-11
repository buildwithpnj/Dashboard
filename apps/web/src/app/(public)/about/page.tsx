import React from 'react';
import Link from 'next/link';
import { AICoreVisualization } from '@/components/ai-core-visualization';
import { 
  ArrowRight, 
  Terminal, 
  Lightbulb, 
  Compass, 
  Cpu, 
  Database, 
  Server, 
  ShieldCheck, 
  CheckCircle2, 
  Circle,
  Youtube,
  Instagram,
  Linkedin,
  Github,
  Facebook,
  Globe,
  Share2,
  BookOpen
} from 'lucide-react';

export const metadata = {
  title: 'About',
  description: 'Prakash Nandan Jha (buildwithpnj), AI Engineer building production-grade tools, voice agents, and RAG systems in public.',
};

export default function PublicAboutPage() {
  const skillsData = [
    { category: 'Programming', items: ['Python', 'JavaScript', 'TypeScript', 'SQL', 'HTML5', 'CSS3'] },
    { category: 'Backend', items: ['FastAPI', 'Flask', 'Node.js', 'Express'] },
    { category: 'Frontend', items: ['React', 'Next.js', 'Tailwind CSS', 'shadcn/ui'] },
    { category: 'Databases & Cache', items: ['PostgreSQL', 'MongoDB', 'Redis'] },
    { category: 'Machine Learning', items: ['PyTorch', 'TensorFlow', 'scikit-learn', 'Transformers', 'LoRA/QLoRA', 'ONNX Runtime', 'YOLOv8'] },
    { category: 'LLMs & GenAI', items: ['GPT-4/4o', 'Claude', 'Gemini', 'Mistral', 'LLaMA', 'DeepSeek'] },
    { category: 'RAG & Vector DBs', items: ['Qdrant', 'Pinecone', 'FAISS', 'Chroma', 'Hybrid RAG'] },
    { category: 'Agents & Workflows', items: ['LangChain', 'LangGraph', 'Multi-Agent Workflows', 'Tool-calling'] },
    { category: 'Cloud & DevOps', items: ['Azure', 'GCP', 'Docker', 'Kubernetes', 'GitHub Actions', 'MLflow'] },
    { category: 'Security & Audit', items: ['RLS', 'RBAC', 'DPDP Awareness', 'CSP Headers', 'Rate Limiting', 'Secrets Management'] }
  ];

  const profiles = [
    { name: 'Website', url: 'https://www.buildwithpnj.in', icon: <Globe className="h-4 w-4" /> },
    { name: 'LinkedIn', url: 'https://www.linkedin.com/in/buildwithpnj/', icon: <Linkedin className="h-4 w-4" /> },
    { name: 'GitHub', url: 'https://github.com/buildwithpnj', icon: <Github className="h-4 w-4" /> },
    { name: 'YouTube', url: 'https://www.youtube.com/@buildwithPNJ', icon: <Youtube className="h-4 w-4" /> },
    { name: 'Instagram', url: 'https://www.instagram.com/buildwithpnj/', icon: <Instagram className="h-4 w-4" /> },
    { name: 'Threads', url: 'https://www.threads.net/@buildwithpnj', icon: <Share2 className="h-4 w-4" /> },
    { name: 'Dev.to', url: 'https://dev.to/buildwithpnj', icon: <BookOpen className="h-4 w-4" /> },
    { name: 'Facebook', url: 'https://www.facebook.com/buildwithpnj/', icon: <Facebook className="h-4 w-4" /> }
  ];

  return (
    <div className="flex flex-col gap-16 md:gap-24 text-left max-w-5xl mx-auto py-8">
      
      {/* 1. PROFILE / HEADER SECTION */}
      <section className="flex flex-col lg:flex-row items-center lg:items-start gap-12 border-b border-border/40 pb-16">
        
        {/* Left Side: Interactive AI Core Visualization */}
        <div className="relative shrink-0 flex items-center justify-center self-center lg:self-start">
          <AICoreVisualization />
        </div>

        {/* Right Side: Bio */}
        <div className="flex-1 flex flex-col gap-4">
          <div className="font-mono text-[9px] text-primary/80 tracking-[0.25em] uppercase font-bold">
            {"// ENGINEER PROFILE"}
          </div>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
            Prakash Nandan Jha
          </h1>
          <p className="text-sm font-mono text-muted-foreground -mt-2">
            Principal AI Product Engineer @ buildwithpnj
          </p>
          <p className="text-sm sm:text-base text-muted-foreground leading-relaxed mt-2">
            I build production-grade AI applications, custom voice agents, and high-performance retrieval architectures that solve real-world problems. Operating under the brand **buildwithpnj**, I specialize in taking systems from initial design into robust, live customer production environments.
          </p>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4 p-4 rounded-xl border border-border/30 bg-card/25 backdrop-blur-sm font-mono text-[9px]">
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground uppercase text-[8px]">LOCAL CORE</span>
              <span className="text-foreground font-black flex items-center gap-1">
                <Cpu className="h-3 w-3 text-primary" /> Llama-3-8B
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground uppercase text-[8px]">VECTOR DB</span>
              <span className="text-foreground font-black flex items-center gap-1">
                <Database className="h-3 w-3 text-primary" /> pgvector
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground uppercase text-[8px]">SERVER FRAME</span>
              <span className="text-foreground font-black flex items-center gap-1">
                <Server className="h-3 w-3 text-primary" /> FastAPI/Redis
              </span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground uppercase text-[8px]">SECURITY</span>
              <span className="text-foreground font-black flex items-center gap-1">
                <ShieldCheck className="h-3 w-3 text-emerald-400" /> OAuth / JWT
              </span>
            </div>
          </div>
        </div>

      </section>

      {/* 2. CHRONICLES & MISSION */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16">
        <div className="lg:col-span-7 flex flex-col gap-8">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
              {"// CHRONICLES"}
            </span>
          </div>

          {/* Who I Am */}
          <div className="flex flex-col gap-2 -mt-4">
            <h3 className="text-lg font-bold text-foreground font-mono flex items-center gap-2">
              <span className="text-primary font-black">01.</span> Who I Am
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              I am Prakash Nandan Jha, a software developer and AI engineer based in India. What started as writing simple command-line scripts to automate my own daily tasks quickly grew into a passion for building reliable software at scale. Today, I combine full-stack development with modern generative models, vector search, and agentic workflows to build software that operates autonomously and efficiently.
            </p>
          </div>

          {/* What I Build */}
          <div className="flex flex-col gap-2">
            <h3 className="text-lg font-bold text-foreground font-mono flex items-center gap-2">
              <span className="text-primary font-black">02.</span> What I Build
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              I focus on building software that solves concrete operations and growth problems. My work spans custom multilingual voice systems, semantic search engines, and real-time business dashboards. You can explore some of my active commercial work on the <Link href="/projects" className="text-primary hover:underline font-semibold">Projects</Link> page.
            </p>
          </div>

          {/* How I Work */}
          <div className="flex flex-col gap-2">
            <h3 className="text-lg font-bold text-foreground font-mono flex items-center gap-2">
              <span className="text-primary font-black">03.</span> How I Work
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              I believe in reliability, speed, and clean architecture. I write clean, grid-aligned code, build interfaces that put user legibility first, and ensure all systems run with low latency and secure parameters. For experimental ideas and pre-release tools, I maintain an active workspace on my <Link href="/labs" className="text-primary hover:underline font-semibold">R&D Labs</Link> page.
            </p>
          </div>

          {/* What I Share Publicly */}
          <div className="flex flex-col gap-2">
            <h3 className="text-lg font-bold text-foreground font-mono flex items-center gap-2">
              <span className="text-primary font-black">04.</span> What I Share Publicly
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
              I build in the open because I believe the best way to understand systems is to share their blueprints. I document my design decisions, pipeline failures, and optimization logs in my <Link href="/journal" className="text-primary hover:underline font-semibold">Technical Journal</Link>. You can also watch live agent systems telemetry on the <Link href="/mission-control" className="text-primary hover:underline font-semibold font-mono">Mission Control</Link> dashboard.
            </p>
          </div>
        </div>

        <div className="lg:col-span-5 p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-6 h-fit shadow-lg shadow-black/5">
          <div className="flex items-center gap-2">
            <span className="font-mono text-[9px] tracking-[0.25em] text-primary/80 uppercase font-bold">
              {"// MISSION STATEMENT"}
            </span>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Building a strong AI engineering brand as **buildwithpnj** while shipping revenue-generating verticals and production systems. We skip theoretical delay and focus on shipping working software.
          </p>
          <div className="flex flex-col gap-3">
            <div className="text-[10px] font-pixel text-muted-foreground tracking-widest uppercase">
              {"// WHAT I'VE BUILT"}
            </div>
            <ul className="text-xs text-foreground font-mono flex flex-col gap-2">
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                AI growth agents for local businesses.
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Production voice agent systems.
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                RAG-based business assistants.
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Internal operating systems and dashboards.
              </li>
              <li className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                Bespoke client and demo websites.
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* 3. CORE SKILL MATRIX GRID */}
      <section className="flex flex-col gap-8 border-t border-border/40 pt-16">
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
            {"// CAPABILITY MATRIX"}
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            Technical Skill Set
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {skillsData.map((skillGroup, idx) => (
            <div key={idx} className="p-5 rounded-2xl border border-border/40 bg-card/25 backdrop-blur-sm flex flex-col gap-3 shadow-sm hover:border-primary/20 transition-all">
              <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
                {skillGroup.category}
              </span>
              <div className="flex flex-wrap gap-1.5">
                {skillGroup.items.map((item, itemIdx) => (
                  <span key={itemIdx} className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary/80 text-muted-foreground border border-border/30">
                    {item}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. PUBLIC PROFILES SECTION */}
      <section className="flex flex-col gap-8 border-t border-border/40 pt-16">
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
            {"// SOCIAL ROUTING"}
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            Public Connections
          </h2>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {profiles.map((profile, idx) => (
            <a 
              key={idx}
              href={profile.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group p-4 rounded-xl border border-border/40 bg-card/25 hover:bg-secondary/40 hover:border-primary/20 flex items-center justify-between gap-3 transition-all duration-300 hover:-translate-y-[2px] shadow-sm font-mono text-xs"
            >
              <div className="flex items-center gap-2 text-muted-foreground group-hover:text-primary transition-colors">
                {profile.icon}
                <span>{profile.name}</span>
              </div>
              <ArrowRight className="h-3 w-3 text-muted-foreground group-hover:text-primary group-hover:translate-x-0.5 transition-all" />
            </a>
          ))}
        </div>
      </section>

      {/* 5. CURRENT TARGETS SECTION */}
      <section className="flex flex-col gap-8 border-t border-border/40 pt-16">
        <div className="flex flex-col gap-1.5">
          <span className="font-mono text-[10px] tracking-[0.25em] text-primary/80 uppercase">
            {"// ROADMAP MATRIX"}
          </span>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">
            Current Target Objectives
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[11px] font-mono">
          <div className="p-4 rounded-xl border border-border/40 bg-card/25 backdrop-blur-sm flex items-center justify-between gap-4 shadow-sm hover:border-primary/20 transition-all">
            <div className="flex items-center gap-3 text-muted-foreground">
              <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400 shrink-0" />
              <span>Launch Personal OS v1.0 Container</span>
            </div>
            <span className="text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/5 border border-emerald-500/10 text-[9px]">
              [ COMPLETED ]
            </span>
          </div>

          <div className="p-4 rounded-xl border border-border/40 bg-card/25 backdrop-blur-sm flex items-center justify-between gap-4 shadow-sm hover:border-primary/20 transition-all">
            <div className="flex items-center gap-3 text-muted-foreground">
              <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400 shrink-0" />
              <span>Publish 5 Systems Architecture Log files</span>
            </div>
            <span className="text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-500/5 border border-emerald-500/10 text-[9px]">
              [ COMPLETED ]
            </span>
          </div>

          <div className="p-4 rounded-xl border border-border/40 bg-card/25 backdrop-blur-sm flex items-center justify-between gap-4 shadow-sm hover:border-primary/20 transition-all">
            <div className="flex items-center gap-3 text-muted-foreground">
              <Circle className="h-4.5 w-4.5 text-primary shrink-0" />
              <span>Ship Experiment-002: Voice Personal OS</span>
            </div>
            <span className="text-primary font-bold px-1.5 py-0.5 rounded bg-primary/5 border border-primary/10 text-[9px]">
              [ IN_PROGRESS ]
            </span>
          </div>

          <div className="p-4 rounded-xl border border-border/40 bg-card/25 backdrop-blur-sm flex items-center justify-between gap-4 shadow-sm hover:border-primary/20 transition-all">
            <div className="flex items-center gap-3 text-muted-foreground">
              <Circle className="h-4.5 w-4.5 text-primary shrink-0" />
              <span>Grow local newsletter crew to 1K subscribers</span>
            </div>
            <span className="text-primary font-bold px-1.5 py-0.5 rounded bg-primary/5 border border-primary/10 text-[9px]">
              [ IN_PROGRESS ]
            </span>
          </div>
        </div>
      </section>

      {/* Footer Call-To-Action */}
      <div className="flex justify-center border-t border-border/40 pt-12">
        <Link 
          href="/contact" 
          className="inline-flex items-center gap-2 h-12 px-6 rounded-xl font-medium bg-primary text-primary-foreground hover:opacity-90 shadow-md shadow-primary/20 transition-all active:scale-[0.98]"
        >
          {"Initiate Connection"} <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

    </div>
  );
}

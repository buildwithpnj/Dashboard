import React from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft, Github, Calendar, CheckSquare } from 'lucide-react';
import { getExperimentBySlug } from '@/lib/content';
import { cn } from '@/lib/utils';

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const exp = getExperimentBySlug(slug);
  if (!exp) return { title: 'Experiment Not Found — BuildWithPNJ' };

  return {
    title: `${exp.title} — BuildWithPNJ`,
    description: exp.tagline,
    alternates: {
      canonical: `/labs/${exp.slug}`,
    },
    openGraph: {
      title: `${exp.title} — BuildWithPNJ`,
      description: exp.tagline,
      url: `https://buildwithpnj.in/labs/${exp.slug}`,
      type: 'article',
      publishedTime: exp.publishDate,
      tags: exp.tags,
      siteName: 'BuildWithPNJ',
    },
    twitter: {
      card: 'summary_large_image',
      title: `${exp.title} — BuildWithPNJ`,
      description: exp.tagline,
      creator: '@buildwithpnj',
    },
  };
}

export default async function PublicLabDetailPage({ params }: PageProps) {
  const { slug } = await params;
  const exp = getExperimentBySlug(slug);

  if (!exp) {
    notFound();
  }

  const statusColor = 
    exp.status === 'live' ? 'bg-positive/10 text-positive' :
    exp.status === 'wip' ? 'bg-yellow-500/10 text-yellow-500' :
    'bg-red-500/10 text-red-500';

  return (
    <div className="flex flex-col gap-10 text-left">
      
      {/* Back button */}
      <div>
        <Link 
          href="/labs" 
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Labs
        </Link>
      </div>

      {/* Header card */}
      <div className="flex flex-col gap-4 border-b border-border pb-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3">
              <span className="font-mono text-xs font-semibold text-primary bg-primary/5 border border-primary/10 px-2 py-0.5 rounded">
                {exp.id}
              </span>
              <span className="text-xs text-muted-foreground font-medium">{exp.category}</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-pixel text-foreground">{exp.title}</h1>
          </div>
          
          <span className={cn("self-start sm:self-auto inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider font-mono", statusColor)}>
            ● {exp.status}
          </span>
        </div>

        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          {exp.tagline}
        </p>

        {/* Links */}
        <div className="flex items-center gap-3 mt-2">
          <span className="text-xs text-muted-foreground flex items-center gap-1.5 mr-2">
            <Calendar className="h-3.5 w-3.5" /> Published: {exp.publishDate}
          </span>
          {exp.githubUrl && (
            <a
              href={exp.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 h-10 px-4 rounded-xl text-xs font-semibold border border-border hover:border-primary/30 bg-card hover:bg-accent text-muted-foreground hover:text-foreground transition-all active:scale-[0.98]"
            >
              GitHub repository <Github className="h-3 w-3" />
            </a>
          )}
        </div>
      </div>

      {/* Grid: main info + side hypothesis summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Main Column */}
        <div className="lg:col-span-8 flex flex-col gap-10">
          
          {/* Hypothesis block */}
          {exp.hypothesis && (
            <div className="p-6 rounded-2xl border-l-4 border-l-primary border-y border-r border-border bg-card">
              <div className="flex items-center gap-2 mb-3">
                <CheckSquare className="h-4 w-4 text-primary" />
                <h4 className="font-pixel text-xs text-foreground uppercase tracking-wider">{"// HYPOTHESIS"}</h4>
              </div>
              <p className="text-sm text-foreground leading-relaxed">
                {exp.hypothesis}
              </p>
            </div>
          )}

          {/* Compiled markdown overview */}
          <section className="prose dark:prose-invert max-w-none text-foreground leading-relaxed prose-headings:font-pixel prose-headings:text-foreground prose-h2:text-xl prose-h2:border-b prose-h2:border-border prose-h2:pb-2 prose-h2:mt-8">
            <div dangerouslySetInnerHTML={{ __html: exp.contentHtml }} />
          </section>

        </div>

        {/* Sidebar Column */}
        <div className="lg:col-span-4 flex flex-col gap-6 lg:sticky lg:top-24 h-fit">
          
          {/* Tech/Tags Card */}
          <div className="p-5 rounded-2xl border border-border bg-card flex flex-col gap-4">
            <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase">{"// LAB TECH"}</h3>
            <div className="flex flex-wrap gap-2">
              {exp.tags.map((tag) => (
                <span key={tag} className="px-2.5 py-1 rounded-lg text-xs font-mono bg-background border border-border text-muted-foreground">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Verification Status Card */}
          <div className="p-5 rounded-2xl border border-border bg-card flex flex-col gap-4 font-mono text-xs text-muted-foreground">
            <h3 className="font-pixel text-xs text-foreground tracking-wider uppercase font-sans">{"// STATUS TELEMETRY"}</h3>
            <div className="flex justify-between items-center py-2 border-b border-border">
              <span>EXPERIMENT:</span>
              <span className="text-foreground">{exp.id}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-border">
              <span>RUN STATUS:</span>
              <span className="text-foreground capitalize">{exp.status}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span>TEAMS ACTIVE:</span>
              <span className="text-foreground">AI Labs</span>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}

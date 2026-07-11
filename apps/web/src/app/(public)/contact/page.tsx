'use client';

import React, { useState } from 'react';
import { 
  Mail, 
  Github, 
  Linkedin, 
  Youtube, 
  Instagram, 
  Share2, 
  BookOpen, 
  Send, 
  CheckCircle2,
  AlertCircle,
  Facebook
} from 'lucide-react';

export default function PublicContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    useCase: 'Production Voice Agent',
    budgetRange: 'Startup / Discovery Phase',
    message: '',
    altContact: ''
  });

  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.message || !formData.altContact) {
      setStatus('error');
      return;
    }

    setStatus('submitting');
    
    // Simulate API request processing
    setTimeout(() => {
      setStatus('success');
      setFormData({
        name: '',
        company: '',
        useCase: 'Production Voice Agent',
        budgetRange: 'Startup / Discovery Phase',
        message: '',
        altContact: ''
      });
    }, 1200);
  };

  const socialLinks = [
    { name: 'LinkedIn', url: 'https://www.linkedin.com/in/buildwithpnj/', icon: <Linkedin className="h-4 w-4 text-muted-foreground" /> },
    { name: 'GitHub', url: 'https://github.com/buildwithpnj', icon: <Github className="h-4 w-4 text-muted-foreground" /> },
    { name: 'YouTube', url: 'https://www.youtube.com/@buildwithPNJ', icon: <Youtube className="h-4 w-4 text-muted-foreground" /> },
    { name: 'Instagram', url: 'https://www.instagram.com/buildwithpnj/', icon: <Instagram className="h-4 w-4 text-muted-foreground" /> },
    { name: 'Threads', url: 'https://www.threads.net/@buildwithpnj', icon: <Share2 className="h-4 w-4 text-muted-foreground" /> },
    { name: 'Dev.to', url: 'https://dev.to/buildwithpnj', icon: <BookOpen className="h-4 w-4 text-muted-foreground" /> },
    { name: 'Facebook', url: 'https://www.facebook.com/buildwithpnj/', icon: <Facebook className="h-4 w-4 text-muted-foreground" /> }
  ];

  return (
    <div className="flex flex-col gap-12 text-left max-w-5xl mx-auto py-8">
      
      {/* Title */}
      <div className="flex flex-col gap-2">
        <div className="font-mono text-[10px] text-primary tracking-[0.25em] uppercase font-bold">{"// GET IN TOUCH"}</div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">{"Let's Build Together"}</h1>
        <p className="text-base text-muted-foreground max-w-xl leading-relaxed mt-2">
          Have a workflow you want to automate, a custom voice agent you need to deploy, or a question about my work? Drop me a message below, and I will get back to you with a technical response.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
        
        {/* Left Side: Contact Form */}
        <div className="lg:col-span-7 p-6 sm:p-8 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md relative overflow-hidden shadow-lg shadow-black/5">
          {status === 'success' ? (
            <div className="flex flex-col items-center text-center py-12 gap-4">
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="text-lg font-bold text-foreground">Message Received</h3>
                <p className="text-xs text-muted-foreground max-w-xs leading-relaxed">
                  Your request has been submitted successfully. I will get back to you with a technical response shortly.
                </p>
              </div>
              <button 
                onClick={() => setStatus('idle')}
                className="mt-4 px-4 py-2 rounded-xl text-xs font-mono border border-border/40 bg-secondary/80 hover:bg-accent text-muted-foreground hover:text-foreground transition-all"
              >
                Submit another request
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-5 text-sm">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Name */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="name" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Your Name *</label>
                  <input
                    type="text"
                    id="name"
                    required
                    placeholder="Prakash"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="h-10 px-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors"
                  />
                </div>

                {/* Company */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="company" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Company</label>
                  <input
                    type="text"
                    id="company"
                    placeholder="AI Lab"
                    value={formData.company}
                    onChange={(e) => setFormData({...formData, company: e.target.value})}
                    className="h-10 px-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Use Case Dropdown */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="useCase" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Use Case *</label>
                  <select
                    id="useCase"
                    value={formData.useCase}
                    onChange={(e) => setFormData({...formData, useCase: e.target.value})}
                    className="h-10 px-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors font-sans text-xs cursor-pointer"
                  >
                    <option>Production Voice Agent</option>
                    <option>RAG Business Assistant</option>
                    <option>Custom Agentic Workflow</option>
                    <option>Core Software Automation</option>
                  </select>
                </div>

                {/* Budget Dropdown */}
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="budgetRange" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Budget Range *</label>
                  <select
                    id="budgetRange"
                    value={formData.budgetRange}
                    onChange={(e) => setFormData({...formData, budgetRange: e.target.value})}
                    className="h-10 px-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors font-sans text-xs cursor-pointer"
                  >
                    <option>Startup / Discovery Phase</option>
                    <option>SMB Automation Scale</option>
                    <option>Enterprise Pipeline</option>
                  </select>
                </div>
              </div>

              {/* Message */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="message" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Message Details *</label>
                <textarea
                  id="message"
                  required
                  rows={4}
                  placeholder="Outline your target automation requirements and constraints..."
                  value={formData.message}
                  onChange={(e) => setFormData({...formData, message: e.target.value})}
                  className="p-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors resize-none"
                />
              </div>

              {/* Alternate Contact / Email */}
              <div className="flex flex-col gap-1.5">
                <label htmlFor="altContact" className="font-mono text-[10px] text-muted-foreground uppercase font-bold">Primary Contact Info *</label>
                <input
                  type="text"
                  id="altContact"
                  required
                  placeholder="Email, X (@handle), or LinkedIn url"
                  value={formData.altContact}
                  onChange={(e) => setFormData({...formData, altContact: e.target.value})}
                  className="h-10 px-3 rounded-xl border border-border/40 bg-background/50 focus:border-primary/50 focus:outline-none transition-colors"
                />
              </div>

              {status === 'error' && (
                <div className="flex items-center gap-2 text-xs text-rose-500 bg-rose-500/5 border border-rose-500/10 p-3 rounded-xl">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <span>Please fill in all required fields marked with *</span>
                </div>
              )}

              <button
                type="submit"
                disabled={status === 'submitting'}
                className="mt-2 flex items-center justify-center gap-2 h-11 px-5 rounded-xl font-semibold bg-primary text-primary-foreground hover:opacity-90 transition-all active:scale-[0.98] shadow-md shadow-primary/10 disabled:opacity-50"
              >
                {status === 'submitting' ? 'Submitting...' : 'Submit Project Brief'} <Send className="h-3.5 w-3.5" />
              </button>
            </form>
          )}
        </div>

        {/* Right Side: Directory & Direct Connections */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* Contact Inquiries Guidelines */}
          <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 text-left shadow-sm">
            <div className="font-mono text-[9px] text-primary/80 tracking-[0.25em] uppercase font-bold">{"// CONTACT INQUIRIES"}</div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              I am available for work, collaborations, and technical queries regarding my projects:
            </p>
            <ul className="text-xs text-muted-foreground flex flex-col gap-2.5 pl-4 list-disc space-y-1">
              <li><strong>Custom AI Integration</strong>: Custom multilingual voice agent pipelines and systems architecture.</li>
              <li><strong>Search & Retrieval</strong>: High-fidelity document search, vector indexing, or database implementations.</li>
              <li><strong>Dashboards & Admin Panels</strong>: Custom business operations dashboards and self-hostable tools.</li>
              <li><strong>General Queries</strong>: Direct collaborations, open-source feedback, or technical consulting.</li>
            </ul>
          </div>

          {/* Email Card */}
          <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 text-left shadow-sm">
            <div className="font-mono text-[9px] text-primary/80 tracking-[0.25em] uppercase font-bold">{"// DIRECT ROUTING"}</div>
            
            <a
              href="mailto:hello@buildwithpnj.in"
              className="flex items-center gap-4 p-3 rounded-xl border border-border/45 bg-background/80 hover:bg-accent group transition-all overflow-hidden"
            >
              <div className="h-10 w-10 rounded-lg bg-card border border-border flex items-center justify-center text-primary group-hover:text-primary/80 shrink-0">
                <Mail className="h-4 w-4" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-[8px] text-muted-foreground font-mono leading-none">EMAIL</span>
                <span className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors mt-1 font-mono truncate select-all">
                  hello@buildwithpnj.in
                </span>
              </div>
            </a>
          </div>

          {/* Social Profiles Grid */}
          <div className="p-6 rounded-2xl border border-border/40 bg-card/35 backdrop-blur-md flex flex-col gap-4 text-left shadow-sm">
            <div className="font-mono text-[9px] text-primary/80 tracking-[0.25em] uppercase font-bold">{"// NETWORK CHANNELS"}</div>
            
            <div className="grid grid-cols-1 gap-2 text-xs">
              {socialLinks.map((social, idx) => (
                <a
                  key={idx}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-2.5 rounded-xl border border-border/30 bg-background/50 hover:bg-accent hover:border-primary/20 transition-all font-mono"
                >
                  <div className="flex items-center gap-2.5">
                    {social.icon}
                    <span>{social.name}</span>
                  </div>
                  <span className="text-[9px] text-muted-foreground hover:text-primary">Connect</span>
                </a>
              ))}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}

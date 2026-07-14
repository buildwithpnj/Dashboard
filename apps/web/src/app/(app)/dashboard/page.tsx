'use client';

import { useState, useEffect } from 'react';
import { 
  CheckSquare, 
  HardDrive, 
  Calendar as CalendarIcon, 
  Activity, 
  ShieldCheck,
  Flame,
  Brain,
  Sparkles,
  Target,
  Globe,
  Cpu
} from 'lucide-react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface StorageProvider {
  provider_label: string;
  account_email: string;
  connected: boolean;
  status: string;
}

interface Habit {
  id: string;
  name: string;
  logs: { date: string }[];
}

interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
}

interface Addiction {
  id: string;
  name: string;
  current_streak_days: number;
  money_saved?: number;
  time_saved_hours?: number;
}

interface CoachInsight {
  content: string;
  completion_rate: number;
}

interface GeoInfo {
  country_name: string;
  country_code: string;
  currency: string;
  timezone: string;
}

interface MemoryProgress {
  corrections_accepted: number;
  streak: number;
  weak_categories: string[];
  mastered_patterns: string[];
}

const currencySymbols: Record<string, string> = {
  USD: '$',
  INR: '₹',
  GBP: '£',
  JPY: '¥',
  EUR: '€',
};

const getBrowserGeo = (): GeoInfo => {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  let code = 'US';
  let name = 'United States';
  let curr = 'USD';
  
  if (tz.includes('Kolkata') || tz.includes('India') || tz.includes('Asia/Calcutta')) {
    code = 'IN';
    name = 'India';
    curr = 'INR';
  } else if (tz.includes('London') || tz.includes('Europe/London')) {
    code = 'GB';
    name = 'United Kingdom';
    curr = 'GBP';
  } else if (tz.includes('Tokyo') || tz.includes('Asia/Tokyo')) {
    code = 'JP';
    name = 'Japan';
    curr = 'JPY';
  }
  return { country_name: name, country_code: code, currency: curr, timezone: tz };
};

export default function MissionControlPage() {
  const [time, setTime] = useState<string>('');
  const [providers, setProviders] = useState<StorageProvider[]>([]);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [addictions, setAddictions] = useState<Addiction[]>([]);
  const [insight, setInsight] = useState<CoachInsight | null>(null);
  const [geo, setGeo] = useState<GeoInfo | null>(null);
  const [memoryProgress, setMemoryProgress] = useState<MemoryProgress | null>(null);
  const [loading, setLoading] = useState(true);

  // Time ticker
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const options: Intl.DateTimeFormatOptions = {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
      };
      if (geo?.timezone) {
        options.timeZone = geo.timezone;
      }
      setTime(now.toLocaleTimeString([], options));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, [geo]);

  // Geo detection API
  useEffect(() => {
    async function detectGeo() {
      try {
        const res = await fetch('https://ipapi.co/json/');
        if (res.ok) {
          const data = await res.json();
          setGeo({
            country_name: data.country_name || 'United States',
            country_code: data.country_code || 'US',
            currency: data.currency || 'USD',
            timezone: data.timezone || 'America/New_York',
          });
        } else {
          setGeo(getBrowserGeo());
        }
      } catch {
        setGeo(getBrowserGeo());
      }
    }
    detectGeo();
  }, []);

  const loadData = async () => {
    try {
      const stData = await api<{ providers: StorageProvider[] }>('/api/storage/providers');
      setProviders(stData.providers || []);

      const hData = await api<Habit[]>('/api/habits');
      setHabits(hData?.slice(0, 4) || []);

      const cData = await api<CalendarEvent[]>('/api/gcalendar/events');
      setEvents(cData?.slice(0, 3) || []);

      const aData = await api<Addiction[]>('/api/recovery/addictions');
      setAddictions(aData?.slice(0, 3) || []);

      const iData = await api<CoachInsight>('/api/aicoach/insights');
      setInsight(iData);

      const mData = await api<MemoryProgress>('/api/memory/progress');
      setMemoryProgress(mData);
    } catch (err) {
      console.error('Failed to load Mission Control telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const toggleHabitLog = async (h: Habit) => {
    const todayStr = new Date().toISOString().split('T')[0];
    const logged = h.logs?.some((l) => l.date === todayStr);
    try {
      await api(`/api/habits/${h.id}/log`, {
        method: 'POST',
        body: {
          date: todayStr,
          value: logged ? 0.0 : 1.0,
        },
      });
      loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const getTodayEvents = () => {
    const todayStr = new Date().toISOString().split('T')[0];
    return events.filter(e => e.start_time.startsWith(todayStr));
  };
  const todayEvents = getTodayEvents();

  return (
    <div className="space-y-6 animate-fade-in text-[#E4E6EB] font-sans pb-12">
      {/* 1. System Status Ribbon */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-[#1E2024] pb-4 gap-4">
        <div>
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#FFB000]">OPERATIONAL SPACE</span>
          <h1 className="text-lg font-medium tracking-tight text-white mt-0.5">Mission Control</h1>
        </div>

        <div className="flex items-center gap-6 text-[11px] font-mono text-[#60646C]">
          {geo && (
            <span className="flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5 text-[#FFB000]" />
              <span>{geo.country_code} Node</span>
            </span>
          )}
          <span className="h-3 w-px bg-[#1E2024]" />
          <span className="tabular-nums text-[#E4E6EB]">{time || '--:--:--'}</span>
          <span className="h-3 w-px bg-[#1E2024]" />
          <span className="flex items-center gap-1 text-[#00E676]">
            <Activity className="h-3 w-3 animate-pulse" /> 14 ms
          </span>
          <span className="h-3 w-px bg-[#1E2024]" />
          <span className="flex items-center gap-1 text-sky-400">
            <ShieldCheck className="h-3 w-3" /> AES-256
          </span>
        </div>
      </div>

      {/* 2. Cognitive Hero Block */}
      <div className="bg-[#16191D] rounded-lg p-6 border border-[#1E2024]/40 flex flex-col md:flex-row gap-6 shadow-xl">
        <div className="flex-1 space-y-2">
          <span className="text-[10px] font-mono tracking-wider uppercase text-[#FFB000]">AI Coach Context</span>
          {loading ? (
            <div className="text-xs text-[#60646C] flex items-center gap-2">
              <Sparkles className="h-3.5 w-3.5 animate-spin text-[#FFB000]" /> Analyzing workspace state...
            </div>
          ) : insight ? (
            <p className="text-sm font-normal text-white leading-relaxed font-mono">
              "{insight.content}"
            </p>
          ) : (
            <p className="text-xs text-[#60646C]">No active coaching context.</p>
          )}
        </div>
        
        <div className="w-full md:w-80 border-t md:border-t-0 md:border-l border-[#1E2024]/60 pt-4 md:pt-0 md:pl-6 space-y-3">
          <span className="text-[10px] font-mono tracking-wider uppercase text-[#60646C]">Today's Focus priorities</span>
          <div className="space-y-2">
            {loading ? (
              <p className="text-xs text-[#60646C] italic">Checking priorities...</p>
            ) : todayEvents.length === 0 ? (
              <p className="text-xs text-[#60646C] italic">No scheduled events to prioritize.</p>
            ) : (
              todayEvents.map((evt) => (
                <div key={evt.id} className="flex items-start gap-2.5 text-xs text-neutral-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#FFB000] mt-1.5 shrink-0" />
                  <span className="truncate">{evt.title}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* 3. Daily Execution & Behavioral health Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Daily Timeline (60%) */}
        <div className="lg:col-span-3 bg-[#111315] rounded-lg p-5 border border-[#1E2024] space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-[#1E2024]/65">
            <h2 className="text-xs font-mono tracking-wider uppercase text-[#60646C] flex items-center gap-2">
              <CalendarIcon className="h-4 w-4 text-[#FFB000]" />
              Schedule & Timeline
            </h2>
            <Link href="/calendar" className="text-[10px] font-mono text-[#FFB000] hover:underline">SYNC</Link>
          </div>

          <div className="space-y-2.5 text-xs">
            {loading ? (
              <p className="text-xs text-[#60646C] italic">Updating schedule...</p>
            ) : events.length === 0 ? (
              <p className="text-xs text-[#60646C] italic font-mono">No events scheduled.</p>
            ) : (
              events.map((evt) => (
                <div key={evt.id} className="p-3 rounded border border-[#1E2024]/80 bg-[#0B0C0E]/50 flex justify-between items-center">
                  <span className="font-medium text-white truncate">{evt.title}</span>
                  <span className="text-[10px] font-mono text-[#FFB000] shrink-0 ml-4">
                    {new Date(evt.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Behavioral Progress Module (40%) */}
        <div className="lg:col-span-2 bg-[#111315] rounded-lg p-5 border border-[#1E2024] space-y-4">
          <div className="flex justify-between items-center pb-2 border-b border-[#1E2024]/65">
            <h2 className="text-xs font-mono tracking-wider uppercase text-[#60646C] flex items-center gap-2">
              <Target className="h-4 w-4 text-[#FFB000]" />
              Behavioral Streaks
            </h2>
            <Link href="/habits" className="text-[10px] font-mono text-[#FFB000] hover:underline">MANAGE</Link>
          </div>

          <div className="space-y-3">
            {/* Sobriety Streaks Section */}
            <div className="space-y-2">
              {loading ? (
                <p className="text-xs text-[#60646C] italic">Reading recovery node...</p>
              ) : addictions.length === 0 ? (
                <p className="text-xs text-[#60646C] italic">No active addiction tracking.</p>
              ) : (
                addictions.map((add) => (
                  <div key={add.id} className="p-3 rounded border border-[#1E2024]/60 bg-[#0B0C0E]/40 flex justify-between items-center text-xs">
                    <div className="min-w-0">
                      <span className="block truncate text-white font-medium">{add.name}</span>
                      <span className="text-[10px] font-mono text-[#60646C]">
                        Saved: {currencySymbols[geo?.currency || 'USD'] || '$'}{add.money_saved || 0}
                      </span>
                    </div>
                    <span className="text-[#FFB000] font-mono font-bold text-sm ml-2 shrink-0 flex items-center gap-1">
                      <Flame className="h-3.5 w-3.5 text-[#FFB000]" /> {add.current_streak_days}d
                    </span>
                  </div>
                ))
              )}
            </div>

            {/* Quick Habit Action Bar */}
            <div className="border-t border-[#1E2024]/60 pt-3 space-y-2">
              <span className="text-[9px] font-mono tracking-wider uppercase text-[#60646C] block">Routine Checkins</span>
              <div className="grid grid-cols-2 gap-2 text-[11px]">
                {loading ? (
                  <p className="text-xs text-[#60646C] col-span-2 italic">Loading habits...</p>
                ) : habits.length === 0 ? (
                  <p className="text-xs text-[#60646C] col-span-2 italic">No routine habits configured.</p>
                ) : (
                  habits.slice(0, 2).map((h) => {
                    const todayStr = new Date().toISOString().split('T')[0];
                    const checked = h.logs?.some((l) => l.date === todayStr);
                    return (
                      <button
                        key={h.id}
                        onClick={() => toggleHabitLog(h)}
                        className={cn(
                          "flex items-center gap-2 p-2 rounded border transition-colors text-left truncate font-medium",
                          checked 
                            ? "bg-[#16191D] border-[#FFB000]/40 text-[#E4E6EB] line-through decoration-[#FFB000]/40" 
                            : "bg-[#0B0C0E]/30 border-[#1E2024] text-[#60646C] hover:border-[#1E2024]"
                        )}
                      >
                        <CheckSquare className={cn("h-3.5 w-3.5 shrink-0", checked ? "text-[#FFB000]" : "text-[#60646C]")} />
                        <span className="truncate">{h.name}</span>
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 4. System Health & Memory Telemetry Strip */}
      <div className="bg-[#111315] rounded-lg p-5 border border-[#1E2024] space-y-4">
        <div className="flex justify-between items-center pb-2 border-b border-[#1E2024]/65">
          <h2 className="text-xs font-mono tracking-wider uppercase text-[#60646C] flex items-center gap-2">
            <Cpu className="h-4 w-4 text-[#FFB000]" />
            Telemetry & Cognitive Memory
          </h2>
          <Link href="/storage" className="text-[10px] font-mono text-[#FFB000] hover:underline">DRIVES</Link>
        </div>

        <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-6 text-xs font-mono">
          {/* Storage nodes */}
          <div className="flex-1 flex flex-wrap gap-3">
            {loading ? (
              <p className="text-xs text-[#60646C] italic">Polling drives...</p>
            ) : providers.length === 0 ? (
              <p className="text-xs text-[#60646C] italic">No active storage nodes connected.</p>
            ) : (
              providers.map((p, idx) => (
                <div key={idx} className="px-3 py-2 rounded border border-[#1E2024]/80 bg-[#0B0C0E]/40 flex items-center gap-2">
                  <HardDrive className="h-3.5 w-3.5 text-[#60646C]" />
                  <span className="text-[#E4E6EB] font-medium">{p.provider_label}</span>
                  <span className={cn(
                    "w-1.5 h-1.5 rounded-full",
                    p.connected ? "bg-[#00E676] animate-pulse" : "bg-[#60646C]"
                  )} />
                </div>
              ))
            )}
          </div>

          {/* Cognitive kernel metrics */}
          {memoryProgress && (
            <div className="flex items-center gap-4 bg-[#0B0C0E]/40 border border-[#1E2024]/80 rounded p-2.5 shrink-0">
              <div className="flex flex-col text-right">
                <span className="text-[9px] uppercase text-[#60646C]">Memory facts</span>
                <span className="text-xs font-semibold text-[#E4E6EB]">{memoryProgress.corrections_accepted} Accepted</span>
              </div>
              <span className="h-6 w-px bg-[#1E2024]" />
              <div className="flex flex-col text-right">
                <span className="text-[9px] uppercase text-[#60646C]">Streak</span>
                <span className="text-xs font-semibold text-[#FFB000]">{memoryProgress.streak} Days</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

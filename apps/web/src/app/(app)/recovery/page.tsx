'use client';

import { useState, useEffect } from 'react';
import {
  Flame,
  Award,
  AlertTriangle,
  Clock,
  Heart,
  TrendingDown,
  DollarSign,
  Plus,
  Loader2,
  AlertCircle,
  HelpCircle
} from 'lucide-react';
import { api } from '@/lib/api';
import { RecoveryIntervention } from '@/components/recovery-intervention';

interface RelapseLog {
  id: string;
  relapsed_at: string;
  trigger_notes: string | null;
  mood_rating: number | null;
}

interface Addiction {
  id: string;
  name: string;
  quit_at: string;
  cost_per_day: number;
  time_saved_per_day_mins: number;
  current_streak_days: number;
  money_saved: number;
  time_saved_hours: number;
  relapse_count: number;
  relapses: RelapseLog[];
}

export default function QuitAddictionPage() {
  const [addictions, setAddictions] = useState<Addiction[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAdd, setSelectedAdd] = useState<Addiction | null>(null);

  // New Addiction Form states
  const [showModal, setShowModal] = useState(false);
  const [newName, setNewName] = useState('Smoking');
  const [customName, setCustomName] = useState('');
  const [cost, setCost] = useState(12.5);
  const [timeSavedMins, setTimeSavedMins] = useState(45);

  // Relapse form states
  const [showRelapseModal, setShowRelapseModal] = useState(false);
  const [relapseTrigger, setRelapseTrigger] = useState('');
  const [relapseMood, setRelapseMood] = useState(2);

  const loadAddictions = async () => {
    setLoading(true);
    try {
      const data = await api<Addiction[]>('/api/recovery/addictions');
      setAddictions(data || []);
      if (data && data.length > 0) {
        setSelectedAdd(data[0]);
      }
    } catch (err) {
      console.error('Failed to load addiction tracks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAddictions();
  }, []);

  const handleCreateAddiction = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalName = newName === 'custom' ? customName : newName;
    if (!finalName.trim()) return;

    try {
      await api('/api/recovery/addictions', {
        method: 'POST',
        body: {
          name: finalName,
          quit_at: new Date().toISOString(),
          cost_per_day: cost,
          time_saved_per_day_mins: timeSavedMins,
        },
      });
      setShowModal(false);
      setCustomName('');
      await loadAddictions();
    } catch (err) {
      alert('Failed to register addiction.');
      console.error(err);
    }
  };

  const handleLogRelapse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdd) return;

    try {
      await api(`/api/recovery/addictions/${selectedAdd.id}/relapse`, {
        method: 'POST',
        body: {
          relapsed_at: new Date().toISOString(),
          trigger_notes: relapseTrigger,
          mood_rating: relapseMood,
        },
      });
      setShowRelapseModal(false);
      setRelapseTrigger('');
      await loadAddictions();
    } catch (err) {
      alert('Failed to log relapse.');
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6 animate-fade-in text-foreground h-[calc(100vh-80px)] overflow-hidden">
      {/* System Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border border-border/80 rounded-2xl bg-card/45 p-6 grid-dots gap-4">
        <div>
          <span className="text-3xs font-bold uppercase tracking-[0.25em] text-primary">Sovereignty Matrix</span>
          <h1 className="text-2xl font-bold tracking-tight mt-1 flex items-center gap-2">
            <Flame className="h-7 w-7 text-primary animate-pulse" />
            Quit Addiction Manager
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            Sovereign tracking of sobriety counters, trigger tags, and accrued health dividends.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="rounded-lg bg-primary hover:bg-primary/90 px-4 py-2 text-xs font-semibold text-primary-foreground flex items-center gap-1.5 transition-colors self-start md:self-auto"
        >
          <Plus className="h-3.5 w-3.5" /> Track Addiction
        </button>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
        {/* Sidebar - active addiction counters */}
        <div className="border border-border rounded-2xl bg-card/30 p-5 overflow-y-auto space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
            <TrendingDown className="h-4 w-4 text-primary" />
            Active Trackers
          </h3>

          {loading ? (
            <div className="py-8 text-center text-xs text-muted-foreground flex justify-center items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading sovereign counters...
            </div>
          ) : addictions.length === 0 ? (
            <p className="text-xs text-muted-foreground italic py-4">No addiction counters configured.</p>
          ) : (
            <div className="space-y-3">
              {addictions.map((add) => (
                <button
                  key={add.id}
                  onClick={() => setSelectedAdd(add)}
                  className={`w-full p-4 rounded-xl border text-left transition-all ${
                    selectedAdd?.id === add.id
                      ? 'bg-primary/10 border-primary shadow-[0_0_12px_rgba(59,130,246,0.1)]'
                      : 'border-border bg-muted/20 hover:border-primary/20'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs font-semibold">
                    <span>{add.name}</span>
                    <span className="font-mono text-primary text-sm font-bold">{add.current_streak_days}d</span>
                  </div>
                  <p className="text-3xs text-muted-foreground mt-1">Quit date: {new Date(add.quit_at).toLocaleDateString()}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sovereign Analytics Detail Board */}
        <div className="lg:col-span-2 overflow-y-auto space-y-6 pr-2">
          {selectedAdd ? (
            <div className="space-y-6">
              {/* Cognitive Behavioral Intervention Engine */}
              <RecoveryIntervention />

              {/* Sovereign Streak Header */}
              <div className="rounded-2xl border border-border bg-card/45 p-6 text-center space-y-4 flex flex-col items-center relative grid-dots">
                <div className="rounded-full bg-primary/10 border border-primary/20 p-5">
                  <Flame className="h-12 w-12 text-primary animate-pulse" />
                </div>
                <div>
                  <h2 className="text-xl font-bold tracking-tight text-foreground">{selectedAdd.name} Sobriety Streak</h2>
                  <p className="text-2xs text-muted-foreground mt-1 font-mono">SOVEREIGN STATE ESTABLISHED FOR:</p>
                  <h1 className="text-5xl font-mono font-bold text-primary tracking-tight mt-3">{selectedAdd.current_streak_days} DAYS</h1>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowRelapseModal(true)}
                    className="rounded-lg border border-destructive/40 hover:bg-destructive/10 px-6 py-2.5 text-xs font-semibold text-destructive transition-all flex items-center gap-1.5"
                  >
                    <AlertTriangle className="h-4 w-4" /> Log Relapse
                  </button>
                </div>
              </div>

              {/* Accrued Dividends Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-2xl border border-border bg-card/30 p-5 space-y-2">
                  <span className="text-3xs uppercase tracking-wider text-muted-foreground font-bold flex items-center gap-1">
                    <DollarSign className="h-4 w-4 text-emerald-400" /> Capital Saved
                  </span>
                  <h3 className="text-2xl font-mono font-bold text-emerald-400">${selectedAdd.money_saved}</h3>
                  <p className="text-3xs text-muted-foreground">Accrued savings based on {selectedAdd.cost_per_day}/day.</p>
                </div>

                <div className="rounded-2xl border border-border bg-card/30 p-5 space-y-2">
                  <span className="text-3xs uppercase tracking-wider text-muted-foreground font-bold flex items-center gap-1">
                    <Clock className="h-4 w-4 text-primary" /> Time Reclaimed
                  </span>
                  <h3 className="text-2xl font-mono font-bold text-primary">{selectedAdd.time_saved_hours} hours</h3>
                  <p className="text-3xs text-muted-foreground">Reclaimed based on {selectedAdd.time_saved_per_day_mins}m/day.</p>
                </div>
              </div>

              {/* Recovery Journal & Relapse History logs */}
              <div className="rounded-2xl border border-border bg-card/30 p-5 space-y-4">
                <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-primary" />
                  Relapse History & Trigger logs ({selectedAdd.relapse_count})
                </h3>

                {selectedAdd.relapses.length === 0 ? (
                  <p className="text-xs text-muted-foreground italic py-2">No relapse triggers logged. Clean record!</p>
                ) : (
                  <div className="space-y-3 font-mono text-2xs">
                    {selectedAdd.relapses.map((r, idx) => (
                      <div key={idx} className="p-3 rounded-xl border border-border/60 bg-muted/20 space-y-1.5">
                        <div className="flex justify-between font-bold">
                          <span className="text-destructive">Reset Timestamp</span>
                          <span className="text-muted-foreground">{new Date(r.relapsed_at).toLocaleString()}</span>
                        </div>
                        {r.trigger_notes && (
                          <p className="text-muted-foreground leading-normal mt-1">Trigger details: &quot;{r.trigger_notes}&quot;</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 text-muted-foreground border border-dashed border-border rounded-2xl min-h-[40vh]">
              <HelpCircle className="h-12 w-12 mb-4 text-muted-foreground/35" />
              <h3 className="text-sm font-semibold text-foreground">Select Addiction Tracker</h3>
              <p className="text-xs max-w-xs mt-1">Configure an addiction track via sidebar button to trigger counts.</p>
            </div>
          )}
        </div>
      </div>

      {/* Track Addiction Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card/90 backdrop-blur-md p-6 shadow-2xl overflow-hidden">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2 pb-3 border-b border-border">
              <Plus className="h-4.5 w-4.5 text-primary" /> Track Addiction Sobriety
            </h3>

            <form onSubmit={handleCreateAddiction} className="mt-4 space-y-4">
              <div className="flex flex-col gap-1">
                <span className="text-3xs uppercase tracking-wider text-muted-foreground font-bold">Addiction Category</span>
                <select
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="rounded border border-border bg-background px-2.5 py-1 text-xs text-foreground focus:outline-none"
                >
                  <option value="Smoking">Smoking</option>
                  <option value="Alcohol">Alcohol</option>
                  <option value="Sugar">Sugar</option>
                  <option value="Social Media">Social Media</option>
                  <option value="Gaming">Gaming</option>
                  <option value="custom">Custom (Write below)</option>
                </select>
              </div>

              {newName === 'custom' && (
                <input
                  type="text"
                  placeholder="Custom addiction name..."
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  required
                  className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs outline-none focus:border-primary text-foreground"
                />
              )}

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="flex flex-col gap-1">
                  <span className="text-3xs uppercase tracking-wider text-muted-foreground font-bold">Cost/day ($)</span>
                  <input
                    type="number"
                    value={cost}
                    onChange={(e) => setCost(parseFloat(e.target.value))}
                    step="0.1"
                    className="rounded border border-border bg-background px-2.5 py-1 text-xs text-foreground focus:outline-none"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <span className="text-3xs uppercase tracking-wider text-muted-foreground font-bold">Time lost/day (mins)</span>
                  <input
                    type="number"
                    value={timeSavedMins}
                    onChange={(e) => setTimeSavedMins(parseInt(e.target.value))}
                    className="rounded border border-border bg-background px-2.5 py-1 text-xs text-foreground focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 text-xs font-semibold mt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-lg border border-border px-4 py-2 text-muted-foreground hover:bg-accent transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/95 transition-colors"
                >
                  Start Tracker
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Relapse Trigger Modal */}
      {showRelapseModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-2xl border border-border bg-card/90 backdrop-blur-md p-6 shadow-2xl overflow-hidden">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2 pb-3 border-b border-border">
              <AlertTriangle className="h-4.5 w-4.5 text-destructive" /> Reset Streak & Log Relapse
            </h3>

            <form onSubmit={handleLogRelapse} className="mt-4 space-y-4">
              <textarea
                placeholder="Log trigger details, cravings description, or triggers here..."
                value={relapseTrigger}
                onChange={(e) => setRelapseTrigger(e.target.value)}
                className="w-full h-24 bg-background border border-border rounded-xl p-3 text-xs outline-none focus:border-primary text-foreground resize-none font-mono"
              />

              <div className="flex justify-end gap-2 text-xs font-semibold mt-4">
                <button
                  type="button"
                  onClick={() => setShowRelapseModal(false)}
                  className="rounded-lg border border-border px-4 py-2 text-muted-foreground hover:bg-accent transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-destructive px-4 py-2 text-white hover:bg-destructive/90 transition-colors"
                >
                  Confirm Reset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

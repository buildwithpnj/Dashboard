'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Target,
  Plus,
  Trash2,
  Calendar,
  Smile,
  Frown,
  Meh,
  SmilePlus,
  Loader2,
  CheckCircle,
  AlertCircle,
  BookOpen,
  Edit3,
  Sparkles,
} from 'lucide-react';
import { api } from '@/lib/api';

interface HabitLog {
  date: string;
  value: number;
}

interface Habit {
  id: string;
  name: string;
  cadence: 'daily' | 'weekly' | 'monthly';
  target: number;
  created_at: string;
  updated_at: string;
  logs: HabitLog[];
}

interface JournalEntry {
  id: string;
  body_json: string;
  mood: number;
  created_at: string;
}

const moodEmojis: Record<number, string> = {
  1: '😢',
  2: '😕',
  3: '😐',
  4: '🙂',
  5: '😄',
};

const moodLabels: Record<number, string> = {
  1: 'Awful',
  2: 'Bad',
  3: 'Neutral',
  4: 'Good',
  5: 'Amazing',
};

export default function HabitsPage() {
  // Habit States
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loadingHabits, setLoadingHabits] = useState(true);
  const [newHabitName, setNewHabitName] = useState('');
  const [newHabitCadence, setNewHabitCadence] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [newHabitTarget, setNewHabitTarget] = useState(1);
  const [showHabitModal, setShowHabitModal] = useState(false);
  const [creatingHabit, setCreatingHabit] = useState(false);

  // Journal States
  const [journals, setJournals] = useState<JournalEntry[]>([]);
  const [selectedJournalId, setSelectedJournalId] = useState<string | null>(null);
  const [loadingJournal, setLoadingJournal] = useState(true);
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');

  // Journal Editor states
  const [editMood, setEditMood] = useState<number>(3);
  const [editContent, setEditContent] = useState('');
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error' | null>(null);

  const isFirstLoad = useRef(true);

  // Calculate last 7 dates for weekly tracker
  const getTrackerDays = () => {
    const days = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      days.push(d);
    }
    return days;
  };
  const trackerDays = getTrackerDays();

  // Load habits list
  const loadHabits = async (showLoader = true) => {
    if (showLoader) setLoadingHabits(true);
    try {
      const data = await api<Habit[]>('/api/habits');
      setHabits(data || []);
    } catch (error) {
      console.error('Failed to load habits:', error);
    } finally {
      if (showLoader) setLoadingHabits(false);
    }
  };

  // Load journal list
  const loadJournals = useCallback(async (selectId: string | null = null, showLoader = true) => {
    if (showLoader) setLoadingJournal(true);
    try {
      const data = await api<JournalEntry[]>('/api/habits/journal/list');
      setJournals(data || []);

      if (data && data.length > 0 && !selectedJournalId && !selectId) {
        // Auto select first journal on load
        selectJournal(data[0]);
      } else if (selectId && data) {
        const found = data.find((j) => j.id === selectId);
        if (found) selectJournal(found);
      }
    } catch (error) {
      console.error('Failed to load journals:', error);
    } finally {
      if (showLoader) setLoadingJournal(false);
    }
  }, [selectedJournalId]);

  useEffect(() => {
    loadHabits();
    loadJournals();
  }, [loadJournals]);

  // Select a journal
  const selectJournal = (entry: JournalEntry) => {
    setSelectedJournalId(entry.id);
    isFirstLoad.current = true;
    setSaveStatus(null);
    setEditMood(entry.mood);

    let text = '';
    try {
      const bodyObj = JSON.parse(entry.body_json);
      text = bodyObj.text || '';
    } catch {
      text = entry.body_json || '';
    }
    setEditContent(text);
  };

  // Create Habit
  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newHabitName.trim()) return;

    setCreatingHabit(true);
    try {
      await api('/api/habits', {
        method: 'POST',
        body: {
          name: newHabitName,
          cadence: newHabitCadence,
          target: newHabitTarget,
        },
      });
      setNewHabitName('');
      setNewHabitTarget(1);
      setShowHabitModal(false);
      await loadHabits();
    } catch (error) {
      alert('Failed to create habit.');
      console.error(error);
    } finally {
      setCreatingHabit(false);
    }
  };

  // Delete Habit
  const handleDeleteHabit = async (id: string) => {
    if (confirm('Are you sure you want to delete this habit?')) {
      try {
        await api(`/api/habits/${id}`, { method: 'DELETE' });
        await loadHabits();
      } catch (error) {
        alert('Failed to delete habit.');
        console.error(error);
      }
    }
  };

  // Toggle habit log completion (optimistic update)
  const handleToggleHabit = async (habit: Habit, dateObj: Date) => {
    const dateStr = dateObj.toISOString().split('T')[0];
    const isLogged = habit.logs.some((l) => l.date === dateStr && l.value > 0);
    const newValue = isLogged ? 0 : 1;

    // Optimistic UI update
    const updated = habits.map((h) => {
      if (h.id === habit.id) {
        let newLogs = [...h.logs];
        if (isLogged) {
          newLogs = newLogs.filter((l) => l.date !== dateStr);
        } else {
          newLogs.push({ date: dateStr, value: 1 });
        }
        return { ...h, logs: newLogs };
      }
      return h;
    });
    setHabits(updated);

    try {
      await api(`/api/habits/${habit.id}/log`, {
        method: 'POST',
        body: {
          date: dateStr,
          value: newValue,
        },
      });
      loadHabits(false);
    } catch (error) {
      console.error('Failed to log habit:', error);
      loadHabits(false); // rollback
    }
  };

  // Create journal entry
  const handleCreateJournal = async () => {
    setLoadingJournal(true);
    try {
      const entry = await api<JournalEntry>('/api/habits/journal', { method: 'POST' });
      await loadJournals(entry.id);
    } catch (error) {
      alert('Failed to create journal entry.');
      console.error(error);
      setLoadingJournal(false);
    }
  };

  // Delete journal entry
  const handleDeleteJournal = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this journal entry?')) {
      try {
        await api(`/api/habits/journal/${id}`, { method: 'DELETE' });
        setSelectedJournalId(null);
        await loadJournals();
      } catch (error) {
        alert('Failed to delete journal entry.');
        console.error(error);
      }
    }
  };

  // Debounced auto-save journal content
  useEffect(() => {
    if (!selectedJournalId) return;
    if (isFirstLoad.current) {
      isFirstLoad.current = false;
      return;
    }

    setSaveStatus('saving');
    const timer = setTimeout(async () => {
      try {
        await api(`/api/habits/journal/${selectedJournalId}`, {
          method: 'PUT',
          body: {
            body_json: JSON.stringify({ text: editContent }),
            mood: editMood,
          },
        });
        setSaveStatus('saved');
        loadJournals(selectedJournalId, false);
      } catch (error) {
        console.error('Journal auto-save failed:', error);
        setSaveStatus('error');
      }
    }, 850);

    return () => clearTimeout(timer);
  }, [editContent, editMood, selectedJournalId, loadJournals]);

  // Basic markdown renderer for journal
  const renderMarkdown = (text: string) => {
    if (!text) return '<p class="text-muted-foreground italic">No journal content yet. Start writing...</p>';
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    html = html.replace(/^# (.*?)$/gm, '<h1 class="text-xl font-bold mt-4 mb-2 border-b border-border pb-1">$1</h1>');
    html = html.replace(/^## (.*?)$/gm, '<h2 class="text-lg font-semibold mt-3 mb-1 border-b border-border/40 pb-0.5">$1</h2>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/^\s*-\s*(.*?)$/gm, '<li class="ml-4 list-disc my-0.5">$1</li>');
    html = html.split('\n').map((line) => {
      const trimmed = line.trim();
      if (trimmed.startsWith('<h') || trimmed.startsWith('<li')) return line;
      return trimmed ? `<p class="mb-2 leading-relaxed text-sm">${line}</p>` : '<div class="h-2"></div>';
    }).join('\n');
    return html;
  };

  return (
    <div className="flex h-[calc(100vh-80px)] overflow-hidden border border-border rounded-xl bg-card shadow-sm" id="habits-module">
      
      {/* 1. Left Panel - Habits completion grid */}
      <div className="w-1/2 border-r border-border flex flex-col bg-card/45">
        
        {/* Panel Header */}
        <div className="p-3 border-b border-border flex items-center justify-between">
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
            <Target className="h-4 w-4 text-primary" />
            Habit Tracker
          </h2>
          <button
            onClick={() => setShowHabitModal(true)}
            className="rounded px-2.5 py-1 bg-primary hover:bg-primary/95 text-primary-foreground text-xs font-semibold inline-flex items-center gap-1 transition-colors"
          >
            <Plus className="h-3.5 w-3.5" />
            Add Habit
          </button>
        </div>

        {/* Habits list with weekly tracker */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {loadingHabits ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : habits.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground max-w-xs mx-auto">
              <Target className="h-10 w-10 text-muted-foreground/30 mx-auto mb-2" />
              <p className="text-xs">No habits configured yet. Add one above to begin building streaks!</p>
            </div>
          ) : (
            habits.map((habit) => (
              <div key={habit.id} className="p-3 border border-border bg-card/65 rounded-lg flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-[13px] font-medium text-foreground">{habit.name}</h3>
                    <p className="text-3xs text-muted-foreground capitalize">{habit.cadence}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteHabit(habit.id)}
                    className="p-1 rounded hover:bg-destructive/15 text-muted-foreground hover:text-destructive transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                {/* Tracker Grid (Last 7 Days) */}
                <div className="flex items-center justify-between border-t border-border/40 pt-2.5 mt-1">
                  {trackerDays.map((day, idx) => {
                    const dateStr = day.toISOString().split('T')[0];
                    const isLogged = habit.logs.some((l) => l.date === dateStr && l.value > 0);
                    const dayName = day.toLocaleDateString(undefined, { weekday: 'narrow' });
                    
                    return (
                      <div key={idx} className="flex flex-col items-center gap-1">
                        <span className="text-3xs font-mono text-muted-foreground">{dayName}</span>
                        <button
                          onClick={() => handleToggleHabit(habit, day)}
                          className={`w-6 h-6 rounded-full border text-3xs font-medium flex items-center justify-center transition-all ${
                            isLogged
                              ? 'bg-primary border-primary text-primary-foreground scale-105 shadow-sm'
                              : 'hover:bg-accent border-border text-muted-foreground'
                          }`}
                          title={day.toLocaleDateString()}
                        >
                          {isLogged ? '✓' : day.getDate()}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 2. Right Panel - Journal Editor */}
      <div className="w-1/2 flex bg-background/25">
        
        {/* Journal left sidebar (List of entries) */}
        <div className="w-48 border-r border-border flex flex-col bg-card/30">
          <div className="p-3 border-b border-border flex items-center justify-between">
            <span className="text-2xs font-semibold text-muted-foreground flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              Journal
            </span>
            <button
              onClick={handleCreateJournal}
              className="rounded p-0.5 hover:bg-accent text-muted-foreground hover:text-foreground"
              title="New entry"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-1.5 space-y-1">
            {loadingJournal && journals.length === 0 ? (
              <div className="flex justify-center py-10">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
              </div>
            ) : journals.length === 0 ? (
              <p className="text-center text-3xs text-muted-foreground py-10">No entries</p>
            ) : (
              journals.map((entry) => {
                const isSelected = entry.id === selectedJournalId;
                return (
                  <div
                    key={entry.id}
                    onClick={() => selectJournal(entry)}
                    className={`group flex items-center justify-between gap-1.5 rounded px-2 py-1.5 text-left cursor-pointer transition-colors ${
                      isSelected
                        ? 'bg-primary/10 text-primary'
                        : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                    }`}
                  >
                    <span className="text-xs truncate font-medium text-foreground">
                      {moodEmojis[entry.mood] || '😐'}{' '}
                      {new Date(entry.created_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </span>
                    <button
                      onClick={(e) => handleDeleteJournal(entry.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-destructive/15 text-muted-foreground hover:text-destructive transition-opacity"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Journal Editor View */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {!selectedJournalId ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-muted-foreground">
              <Sparkles className="h-10 w-10 mb-2 text-muted-foreground/35 animate-pulse" />
              <h4 className="text-xs font-semibold text-foreground">Write Daily Journal</h4>
              <p className="text-3xs max-w-[200px] mt-0.5">
                Click the **Plus (+)** button inside the Journal sidebar to write a daily entry.
              </p>
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden">
              
              {/* Toolbar */}
              <div className="px-4 py-2 border-b border-border flex items-center justify-between bg-card/65">
                <div className="flex gap-1 border border-border p-0.5 rounded bg-muted/30">
                  <button
                    onClick={() => setActiveTab('edit')}
                    className={`flex items-center gap-0.5 px-2 py-0.5 rounded text-3xs font-semibold ${
                      activeTab === 'edit' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground'
                    }`}
                  >
                    <Edit3 className="h-3 w-3" />
                    Edit
                  </button>
                  <button
                    onClick={() => setActiveTab('preview')}
                    className={`flex items-center gap-0.5 px-2 py-0.5 rounded text-3xs font-semibold ${
                      activeTab === 'preview' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground'
                    }`}
                  >
                    <BookOpen className="h-3 w-3" />
                    Preview
                  </button>
                </div>

                {/* Save status */}
                <div className="text-[10px] text-muted-foreground flex items-center gap-1">
                  {saveStatus === 'saving' && <Loader2 className="h-3 w-3 animate-spin text-primary" />}
                  {saveStatus === 'saved' && <CheckCircle className="h-3 w-3 text-emerald-500" />}
                  {saveStatus === 'error' && <AlertCircle className="h-3 w-3 text-destructive" />}
                  <span>{saveStatus || 'Saved'}</span>
                </div>
              </div>

              {/* Mood selector */}
              <div className="p-3 border-b border-border bg-card/30 flex items-center gap-2">
                <span className="text-xs text-muted-foreground">Mood:</span>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((moodVal) => {
                    const isSelected = moodVal === editMood;
                    return (
                      <button
                        key={moodVal}
                        onClick={() => setEditMood(moodVal)}
                        className={`text-base p-1.5 rounded transition-transform ${
                          isSelected
                            ? 'bg-primary/20 border border-primary/30 scale-110'
                            : 'hover:bg-accent border border-transparent hover:scale-105'
                        }`}
                        title={moodLabels[moodVal]}
                      >
                        {moodEmojis[moodVal]}
                      </button>
                    );
                  })}
                </div>
                <span className="text-[11px] font-medium text-foreground ml-1">
                  {moodLabels[editMood]}
                </span>
              </div>

              {/* Editing Area */}
              <div className="flex-1 overflow-y-auto p-4 flex flex-col">
                {activeTab === 'edit' ? (
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    placeholder="Reflect on your day here..."
                    className="flex-1 w-full bg-transparent border-none resize-none outline-none text-xs leading-relaxed text-foreground font-mono placeholder:text-muted-foreground/40"
                  />
                ) : (
                  <div
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(editContent) }}
                    className="prose dark:prose-invert max-w-none text-xs break-words outline-none text-foreground"
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Habit Creation Modal */}
      {showHabitModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs">
          <div className="bg-card border border-border p-4 rounded-xl shadow-lg w-80 flex flex-col gap-3">
            <h3 className="text-sm font-bold text-foreground flex items-center gap-1">
              <Target className="h-4 w-4 text-primary" />
              Create Habit
            </h3>

            <form onSubmit={handleCreateHabit} className="flex flex-col gap-3">
              <div className="flex flex-col gap-1.5">
                <label className="text-3xs font-semibold text-muted-foreground uppercase">Habit Name</label>
                <input
                  type="text"
                  placeholder="e.g. Drink 3L water, Read 10 pages"
                  value={newHabitName}
                  onChange={(e) => setNewHabitName(e.target.value)}
                  className="rounded-md border border-border bg-background px-3 py-1.5 text-xs outline-none focus:border-primary text-foreground"
                  required
                />
              </div>

              <div className="flex gap-2">
                <div className="flex-1 flex flex-col gap-1.5">
                  <label className="text-3xs font-semibold text-muted-foreground uppercase">Cadence</label>
                  <select
                    value={newHabitCadence}
                    onChange={(e) => setNewHabitCadence(e.target.value as any)}
                    className="rounded-md border border-border bg-background px-2.5 py-1.5 text-xs outline-none focus:border-primary text-foreground"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                
                <div className="flex-1 flex flex-col gap-1.5">
                  <label className="text-3xs font-semibold text-muted-foreground uppercase">Daily Target</label>
                  <input
                    type="number"
                    min="1"
                    value={newHabitTarget}
                    onChange={(e) => setNewHabitTarget(parseInt(e.target.value) || 1)}
                    className="rounded-md border border-border bg-background px-3 py-1.5 text-xs outline-none focus:border-primary text-foreground"
                    required
                  />
                </div>
              </div>

              <div className="flex gap-2 justify-end mt-2">
                <button
                  type="button"
                  onClick={() => setShowHabitModal(false)}
                  className="rounded px-3 py-1.5 text-xs font-semibold border border-border text-muted-foreground hover:bg-accent transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingHabit}
                  className="rounded bg-primary hover:bg-primary/95 text-primary-foreground px-4 py-1.5 text-xs font-semibold inline-flex items-center gap-1"
                >
                  {creatingHabit && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

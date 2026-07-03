'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  StickyNote,
  Search,
  Plus,
  Trash2,
  BookOpen,
  Edit3,
  Tag,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileText,
  Link,
} from 'lucide-react';
import { api } from '@/lib/api';

interface Note {
  id: string;
  title: string;
  body_json: string;
  tags?: string;
  created_at: string;
  updated_at: string;
}

interface Backlink {
  id: string;
  title: string;
}

interface NoteDetail extends Note {
  backlinks: Backlink[];
}

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNoteId, setSelectedNoteId] = useState<string | null>(null);
  const [noteDetail, setNoteDetail] = useState<NoteDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Editor edit states
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [editTags, setEditTags] = useState('');
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error' | null>(null);

  const isFirstLoad = useRef(true);

  // Load a single note detail
  const selectNote = useCallback(async (id: string) => {
    setSelectedNoteId(id);
    setLoadingDetail(true);
    isFirstLoad.current = true; // reset first load flag for auto-save debounce
    setSaveStatus(null);
    try {
      const data = await api<NoteDetail>(`/api/notes/${id}`);
      setNoteDetail(data);
      setEditTitle(data.title);

      // Parse body json
      let text = '';
      try {
        const bodyObj = JSON.parse(data.body_json);
        text = bodyObj.text || '';
      } catch {
        text = data.body_json || '';
      }
      setEditContent(text);
      setEditTags(data.tags || '');
    } catch (error) {
      console.error('Failed to load note details:', error);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  // Load list of notes
  const loadNotes = useCallback(async (selectId: string | null = null, showLoader = true) => {
    if (showLoader) setLoadingList(true);
    try {
      const endpoint = searchQuery
        ? `/api/notes?q=${encodeURIComponent(searchQuery)}`
        : '/api/notes';
      const data = await api<Note[]>(endpoint);
      setNotes(data || []);

      if (data && data.length > 0 && !selectedNoteId && !selectId) {
        // Auto-select first note on initial load
        selectNote(data[0].id);
      } else if (selectId) {
        selectNote(selectId);
      }
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      if (showLoader) setLoadingList(false);
    }
  }, [searchQuery, selectedNoteId, selectNote]);

  useEffect(() => {
    loadNotes();
  }, [searchQuery, loadNotes]);

  // Create new note
  const handleCreateNote = async () => {
    setLoadingList(true);
    try {
      const newNote = await api<Note>('/api/notes', { method: 'POST' });
      await loadNotes(newNote.id);
    } catch (error) {
      alert('Failed to create new note.');
      console.error(error);
      setLoadingList(false);
    }
  };

  // Delete note
  const handleDeleteNote = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this note?')) {
      try {
        await api(`/api/notes/${id}`, { method: 'DELETE' });
        setSelectedNoteId(null);
        setNoteDetail(null);
        await loadNotes();
      } catch (error) {
        alert('Failed to delete note.');
        console.error(error);
      }
    }
  };

  // Debounced auto-save effect
  useEffect(() => {
    if (!selectedNoteId) return;
    if (isFirstLoad.current) {
      isFirstLoad.current = false;
      return;
    }

    setSaveStatus('saving');
    const timer = setTimeout(async () => {
      try {
        await api(`/api/notes/${selectedNoteId}`, {
          method: 'PUT',
          body: {
            title: editTitle || 'Untitled Note',
            body_json: JSON.stringify({ text: editContent }),
            tags: editTags,
          },
        });
        setSaveStatus('saved');
        // Silent refresh of the sidebar note items to update list titles
        loadNotes(selectedNoteId, false);
      } catch (error) {
        console.error('Auto-save failed:', error);
        setSaveStatus('error');
      }
    }, 800);

    return () => clearTimeout(timer);
  }, [editTitle, editContent, editTags, selectedNoteId, loadNotes]);

  // Handle clickable internal links in Preview
  const handlePreviewClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    const targetNoteId = target.getAttribute('data-note-id');
    if (targetNoteId) {
      e.preventDefault();
      selectNote(targetNoteId);
    }
  };

  // Simple Markdown renderer
  const renderMarkdown = (text: string) => {
    if (!text) return '<p class="text-muted-foreground italic">No content yet. Start writing in Markdown...</p>';

    // Basic HTML escaping
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Headers
    html = html.replace(/^# (.*?)$/gm, '<h1 class="text-xl font-bold mt-4 mb-2 border-b border-border pb-1">$1</h1>');
    html = html.replace(/^## (.*?)$/gm, '<h2 class="text-lg font-semibold mt-3 mb-1 border-b border-border/40 pb-0.5">$1</h2>');
    html = html.replace(/^### (.*?)$/gm, '<h3 class="text-base font-semibold mt-2 mb-1">$1</h3>');

    // Bold & Italics
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Lists
    html = html.replace(/^\s*-\s*(.*?)$/gm, '<li class="ml-4 list-disc my-0.5">$1</li>');
    html = html.replace(/^\s*\*\s*(.*?)$/gm, '<li class="ml-4 list-disc my-0.5">$1</li>');

    // Code
    html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-muted p-3 rounded-md font-mono text-xs my-3 overflow-x-auto border border-border">$1</pre>');
    html = html.replace(/`(.*?)`/g, '<code class="bg-muted px-1.5 py-0.5 rounded font-mono text-xs border border-border">$1</code>');

    // Internal links [[Note Title]] -> clickable anchor tags
    html = html.replace(/\[\[(.*?)\]\]/g, (match, title) => {
      const trimmedTitle = title.trim();
      const matchNote = notes.find(
        (n) => n.title.toLowerCase() === trimmedTitle.toLowerCase()
      );
      if (matchNote) {
        return `<a href="#" data-note-id="${matchNote.id}" class="text-primary hover:underline font-semibold">[[${trimmedTitle}]]</a>`;
      } else {
        return `<span class="text-muted-foreground line-through decoration-dotted" title="Note does not exist">[[${trimmedTitle}]]</span>`;
      }
    });

    // Paragraph wrapping
    html = html
      .split('\n')
      .map((line) => {
        const trimmed = line.trim();
        if (
          trimmed.startsWith('<h') ||
          trimmed.startsWith('<li') ||
          trimmed.startsWith('<pre') ||
          trimmed.startsWith('</pre>')
        ) {
          return line;
        }
        return trimmed ? `<p class="mb-2 leading-relaxed text-[13.5px]">${line}</p>` : '<div class="h-2"></div>';
      })
      .join('\n');

    return html;
  };

  return (
    <div className="flex h-[calc(100vh-80px)] overflow-hidden border border-border rounded-xl bg-card shadow-sm" id="notes-module">
      
      {/* 1. Left Notes List Panel */}
      <div className="w-64 border-r border-border flex flex-col bg-card/50">
        
        {/* Panel Header */}
        <div className="p-3 border-b border-border flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
              <StickyNote className="h-4 w-4 text-primary" />
              Notes
            </h2>
            <button
              onClick={handleCreateNote}
              className="rounded p-1 hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
              title="New Note"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-md border border-border bg-background py-1 pl-7 pr-3 text-xs outline-none focus:border-primary text-foreground"
            />
            <Search className="absolute left-2 top-2 h-3.5 w-3.5 text-muted-foreground" />
          </div>
        </div>

        {/* List Content */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loadingList && notes.length === 0 ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
          ) : notes.length === 0 ? (
            <p className="text-center text-xs text-muted-foreground py-10">
              No notes found
            </p>
          ) : (
            notes.map((note) => {
              const isSelected = note.id === selectedNoteId;
              return (
                <div
                  key={note.id}
                  onClick={() => selectNote(note.id)}
                  className={`group flex flex-col gap-1 rounded-md px-2.5 py-2 text-left cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-primary/10 text-primary'
                      : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1">
                    <span className="text-[13px] font-medium truncate block w-full text-foreground">
                      {note.title || 'Untitled Note'}
                    </span>
                    <button
                      onClick={(e) => handleDeleteNote(note.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-destructive/15 text-muted-foreground hover:text-destructive transition-opacity"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                  <div className="flex items-center gap-1.5 text-3xs text-muted-foreground font-mono">
                    <span>
                      {new Date(note.updated_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                    {note.tags && (
                      <span className="truncate max-w-[100px] border border-border px-1 rounded-sm bg-muted/40 text-[10px]">
                        {note.tags}
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 2. Right Note Editor Panel */}
      <div className="flex-1 flex flex-col bg-background/25">
        {loadingDetail ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : !selectedNoteId || !noteDetail ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-muted-foreground">
            <StickyNote className="h-12 w-12 mb-4 text-muted-foreground/45" />
            <h3 className="text-sm font-semibold text-foreground">No Note Selected</h3>
            <p className="text-xs max-w-xs mt-1">
              Select an existing note from the sidebar list, or click the **Plus (+)** button to start writing.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Editor Top Bar (Controls / Status) */}
            <div className="px-4 py-2 border-b border-border flex items-center justify-between bg-card/65">
              {/* Tab Toggles */}
              <div className="flex gap-1.5 border border-border p-0.5 rounded bg-muted/30">
                <button
                  onClick={() => setActiveTab('edit')}
                  className={`flex items-center gap-1 px-3 py-1 rounded text-xs font-semibold transition-colors ${
                    activeTab === 'edit'
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <Edit3 className="h-3.5 w-3.5" />
                  Edit
                </button>
                <button
                  onClick={() => setActiveTab('preview')}
                  className={`flex items-center gap-1 px-3 py-1 rounded text-xs font-semibold transition-colors ${
                    activeTab === 'preview'
                      ? 'bg-card text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <BookOpen className="h-3.5 w-3.5" />
                  Preview
                </button>
              </div>

              {/* Auto-save Status Indicator */}
              <div className="text-xs text-muted-foreground flex items-center gap-1.5">
                {saveStatus === 'saving' && (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                    <span>Saving...</span>
                  </>
                )}
                {saveStatus === 'saved' && (
                  <>
                    <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                    <span className="text-emerald-500">Saved</span>
                  </>
                )}
                {saveStatus === 'error' && (
                  <>
                    <AlertCircle className="h-3.5 w-3.5 text-destructive" />
                    <span className="text-destructive">Save Failed</span>
                  </>
                )}
                {!saveStatus && <span>No changes</span>}
              </div>
            </div>

            {/* Note Fields Input */}
            <div className="p-4 border-b border-border flex flex-col gap-3 bg-card/30">
              <input
                type="text"
                placeholder="Title your note..."
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="w-full text-lg font-bold bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground/60"
              />

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Tag className="h-3.5 w-3.5" />
                <input
                  type="text"
                  placeholder="Add comma-separated tags..."
                  value={editTags}
                  onChange={(e) => setEditTags(e.target.value)}
                  className="bg-transparent border-none outline-none text-foreground flex-1 placeholder:text-muted-foreground/60"
                />
              </div>
            </div>

            {/* Active Mode (Edit vs Preview) */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col">
              {activeTab === 'edit' ? (
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  placeholder="Write your note content here (Markdown & backlinks [[Link Title]] supported)..."
                  className="flex-1 w-full bg-transparent border-none resize-none outline-none text-sm leading-relaxed text-foreground placeholder:text-muted-foreground/50 font-mono"
                />
              ) : (
                <div
                  onClick={handlePreviewClick}
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(editContent) }}
                  className="prose dark:prose-invert max-w-none text-sm break-words outline-none text-foreground"
                />
              )}
            </div>

            {/* Obsidian Backlinks Footer */}
            {noteDetail.backlinks && noteDetail.backlinks.length > 0 && (
              <div className="border-t border-border p-3 bg-muted/20 text-xs">
                <h4 className="font-semibold text-muted-foreground mb-1.5 flex items-center gap-1">
                  <Link className="h-3 w-3" />
                  Backlinks ({noteDetail.backlinks.length})
                </h4>
                <div className="flex flex-wrap gap-2">
                  {noteDetail.backlinks.map((link) => (
                    <button
                      key={link.id}
                      onClick={() => selectNote(link.id)}
                      className="px-2.5 py-1 border border-border hover:border-primary hover:text-primary rounded-md bg-card transition-colors flex items-center gap-1 font-medium"
                    >
                      <FileText className="h-3 w-3" />
                      {link.title}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

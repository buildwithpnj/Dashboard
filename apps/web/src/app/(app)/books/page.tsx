'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  BookOpen,
  Search,
  Plus,
  Trash2,
  Star,
  Bookmark,
  BookMarked,
  Tag,
  Loader2,
  CheckCircle,
  AlertCircle,
  FileText,
  Clock,
  ExternalLink,
} from 'lucide-react';
import { api } from '@/lib/api';

interface Highlight {
  id: string;
  book_id: string;
  text: string;
  location?: string;
  tags?: string;
  created_at: string;
}

interface Book {
  id: string;
  title: string;
  author: string;
  status: 'to-read' | 'reading' | 'finished' | 'DNF';
  rating?: number | null;
  cover_url?: string | null;
  created_at: string;
  updated_at: string;
}

interface BookDetail extends Book {
  highlights: Highlight[];
}

export default function BooksPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [bookDetail, setBookDetail] = useState<BookDetail | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Book Edit States
  const [editTitle, setEditTitle] = useState('');
  const [editAuthor, setEditAuthor] = useState('');
  const [editStatus, setEditStatus] = useState<'to-read' | 'reading' | 'finished' | 'DNF'>('to-read');
  const [editRating, setEditRating] = useState<number | null>(null);
  const [editCoverUrl, setEditCoverUrl] = useState('');
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error' | null>(null);

  // New Highlight States
  const [newHlText, setNewHlText] = useState('');
  const [newHlLocation, setNewHlLocation] = useState('');
  const [newHlTags, setNewHlTags] = useState('');
  const [addingHl, setAddingHl] = useState(false);

  const isFirstLoad = useRef(true);

  // Load list of books
  const loadBooks = useCallback(async (selectId: string | null = null, showLoader = true) => {
    if (showLoader) setLoadingList(true);
    try {
      const endpoint = searchQuery
        ? `/api/books?q=${encodeURIComponent(searchQuery)}`
        : '/api/books';
      const data = await api<Book[]>(endpoint);
      setBooks(data || []);

      if (data && data.length > 0 && !selectedBookId && !selectId) {
        setSelectedBookId(data[0].id);
      } else if (selectId) {
        setSelectedBookId(selectId);
      }
    } catch (error) {
      console.error('Failed to load books:', error);
    } finally {
      if (showLoader) setLoadingList(false);
    }
  }, [searchQuery, selectedBookId]);

  useEffect(() => {
    loadBooks();
  }, [searchQuery, loadBooks]);

  // Load book details & highlights
  const loadBookDetail = useCallback(async (id: string) => {
    setLoadingDetail(true);
    isFirstLoad.current = true;
    setSaveStatus(null);
    try {
      const data = await api<BookDetail>(`/api/books/${id}`);
      setBookDetail(data);
      setEditTitle(data.title);
      setEditAuthor(data.author);
      setEditStatus(data.status);
      setEditRating(data.rating || null);
      setEditCoverUrl(data.cover_url || '');
    } catch (error) {
      console.error('Failed to load book details:', error);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    if (selectedBookId) {
      loadBookDetail(selectedBookId);
    }
  }, [selectedBookId, loadBookDetail]);

  // Create new book
  const handleCreateBook = async () => {
    setLoadingList(true);
    try {
      const newBook = await api<Book>('/api/books', { method: 'POST' });
      await loadBooks(newBook.id);
    } catch (error) {
      alert('Failed to create new book.');
      console.error(error);
      setLoadingList(false);
    }
  };

  // Delete book
  const handleDeleteBook = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this book?')) {
      try {
        await api(`/api/books/${id}`, { method: 'DELETE' });
        setSelectedBookId(null);
        setBookDetail(null);
        await loadBooks();
      } catch (error) {
        alert('Failed to delete book.');
        console.error(error);
      }
    }
  };

  // Debounced auto-save effect for book details
  useEffect(() => {
    if (!selectedBookId) return;
    if (isFirstLoad.current) {
      isFirstLoad.current = false;
      return;
    }

    setSaveStatus('saving');
    const timer = setTimeout(async () => {
      try {
        await api(`/api/books/${selectedBookId}`, {
          method: 'PUT',
          body: {
            title: editTitle || 'Untitled Book',
            author: editAuthor || 'Unknown Author',
            status: editStatus,
            rating: editRating,
            cover_url: editCoverUrl || null,
          },
        });
        setSaveStatus('saved');
        loadBooks(selectedBookId, false);
      } catch (error) {
        console.error('Auto-save failed:', error);
        setSaveStatus('error');
      }
    }, 850);

    return () => clearTimeout(timer);
  }, [editTitle, editAuthor, editStatus, editRating, editCoverUrl, selectedBookId, loadBooks]);

  // Add a highlight
  const handleAddHighlight = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBookId || !newHlText.trim()) return;

    setAddingHl(true);
    try {
      await api(`/api/books/${selectedBookId}/highlights`, {
        method: 'POST',
        body: {
          text: newHlText,
          location: newHlLocation || null,
          tags: newHlTags || null,
        },
      });
      setNewHlText('');
      setNewHlLocation('');
      setNewHlTags('');
      // Reload highlights
      await loadBookDetail(selectedBookId);
    } catch (error) {
      alert('Failed to save highlight.');
      console.error(error);
    } finally {
      setAddingHl(false);
    }
  };

  // Delete highlight
  const handleDeleteHighlight = async (hlId: string) => {
    if (confirm('Delete this highlight?')) {
      try {
        await api(`/api/books/highlights/${hlId}`, { method: 'DELETE' });
        if (selectedBookId) await loadBookDetail(selectedBookId);
      } catch (error) {
        alert('Failed to delete highlight.');
        console.error(error);
      }
    }
  };

  const getStatusBadgeClass = (statusVal: string) => {
    switch (statusVal) {
      case 'reading':
        return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'finished':
        return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
      case 'DNF':
        return 'bg-rose-500/10 text-rose-500 border-rose-500/20';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const getStatusLabel = (statusVal: string) => {
    switch (statusVal) {
      case 'reading':
        return 'Reading';
      case 'finished':
        return 'Finished';
      case 'DNF':
        return 'DNF';
      default:
        return 'To Read';
    }
  };

  return (
    <div className="flex h-[calc(100vh-80px)] overflow-hidden border border-border rounded-xl bg-card shadow-sm" id="books-module">
      
      {/* 1. Sidebar - Books list */}
      <div className="w-64 border-r border-border flex flex-col bg-card/50">
        
        {/* Header */}
        <div className="p-3 border-b border-border flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
              <BookOpen className="h-4 w-4 text-primary" />
              Reading List
            </h2>
            <button
              onClick={handleCreateBook}
              className="rounded p-1 hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
              title="Add Book"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search books/authors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-md border border-border bg-background py-1 pl-7 pr-3 text-xs outline-none focus:border-primary text-foreground"
            />
            <Search className="absolute left-2 top-2 h-3.5 w-3.5 text-muted-foreground" />
          </div>
        </div>

        {/* Scrollable list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {loadingList && books.length === 0 ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
          ) : books.length === 0 ? (
            <p className="text-center text-xs text-muted-foreground py-10">No books found</p>
          ) : (
            books.map((book) => {
              const isSelected = book.id === selectedBookId;
              return (
                <div
                  key={book.id}
                  onClick={() => setSelectedBookId(book.id)}
                  className={`group flex items-center gap-2 rounded-md p-2 text-left cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-primary/10 text-primary'
                      : 'hover:bg-accent text-muted-foreground hover:text-foreground'
                  }`}
                >
                  {/* Miniature Cover Thumbnail */}
                  <div className="w-8 h-11 bg-muted border border-border rounded flex-shrink-0 flex items-center justify-center overflow-hidden">
                    {book.cover_url ? (
                      <img src={book.cover_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <BookOpen className="h-3 w-3 text-muted-foreground/50" />
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-[13px] font-medium truncate block w-full text-foreground">
                        {book.title || 'Untitled Book'}
                      </span>
                      <button
                        onClick={(e) => handleDeleteBook(book.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-destructive/15 text-muted-foreground hover:text-destructive transition-opacity"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                    <p className="text-3xs text-muted-foreground truncate">{book.author || 'Unknown'}</p>
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className={`text-[10px] px-1 border rounded-sm font-mono ${getStatusBadgeClass(book.status)}`}>
                        {getStatusLabel(book.status)}
                      </span>
                      {book.rating && (
                        <span className="text-[10px] flex items-center text-amber-500 font-mono">
                          ★{book.rating}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* 2. Main content pane - Details & Highlights */}
      <div className="flex-1 flex flex-col bg-background/25">
        {loadingDetail ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : !selectedBookId || !bookDetail ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-muted-foreground">
            <BookOpen className="h-12 w-12 mb-4 text-muted-foreground/45" />
            <h3 className="text-sm font-semibold text-foreground">No Book Selected</h3>
            <p className="text-xs max-w-xs mt-1">
              Select a book from the reading list on the left, or click the **Plus (+)** button to add a new book.
            </p>
          </div>
        ) : (
          <div className="flex-1 flex flex-col overflow-hidden">
            
            {/* Details Top Header */}
            <div className="px-4 py-2 border-b border-border flex items-center justify-between bg-card/65 text-xs">
              <span className="font-semibold text-muted-foreground flex items-center gap-1.5">
                <Bookmark className="h-3.5 w-3.5 text-primary" />
                Book Details
              </span>

              {/* Save status */}
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

            {/* Book Info Panel */}
            <div className="p-4 border-b border-border bg-card/30 flex gap-4">
              
              {/* Cover input / Display */}
              <div className="flex flex-col gap-2">
                <div className="w-24 h-32 bg-muted border border-border rounded-lg shadow-sm flex items-center justify-center overflow-hidden flex-shrink-0">
                  {editCoverUrl ? (
                    <img src={editCoverUrl} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <BookOpen className="h-8 w-8 text-muted-foreground/30" />
                  )}
                </div>
                <input
                  type="text"
                  placeholder="Cover Image URL..."
                  value={editCoverUrl}
                  onChange={(e) => setEditCoverUrl(e.target.value)}
                  className="w-24 border border-border text-[9px] rounded px-1 py-0.5 outline-none focus:border-primary text-foreground bg-background"
                />
              </div>

              {/* Text Fields */}
              <div className="flex-1 flex flex-col gap-2">
                <input
                  type="text"
                  placeholder="Book Title..."
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="w-full text-base font-bold bg-transparent border-none outline-none text-foreground"
                />

                <input
                  type="text"
                  placeholder="Author..."
                  value={editAuthor}
                  onChange={(e) => setEditAuthor(e.target.value)}
                  className="w-full text-xs bg-transparent border-none outline-none text-muted-foreground"
                />

                {/* Dropdowns */}
                <div className="flex items-center gap-3 mt-2 text-xs">
                  
                  {/* Status Dropdown */}
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground">Status:</span>
                    <select
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value as any)}
                      className="border border-border rounded px-1.5 py-0.5 outline-none bg-background text-foreground text-xs"
                    >
                      <option value="to-read">To Read</option>
                      <option value="reading">Reading</option>
                      <option value="finished">Finished</option>
                      <option value="DNF">DNF</option>
                    </select>
                  </div>

                  {/* Rating Dropdown */}
                  <div className="flex items-center gap-1">
                    <span className="text-muted-foreground flex items-center gap-0.5">
                      <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                      Rating:
                    </span>
                    <select
                      value={editRating || ''}
                      onChange={(e) => setEditRating(e.target.value ? parseInt(e.target.value) : null)}
                      className="border border-border rounded px-1.5 py-0.5 outline-none bg-background text-foreground text-xs"
                    >
                      <option value="">Unrated</option>
                      <option value="5">5 Stars</option>
                      <option value="4">4 Stars</option>
                      <option value="3">3 Stars</option>
                      <option value="2">2 Stars</option>
                      <option value="1">1 Star</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Highlights Section */}
            <div className="flex-1 flex flex-col overflow-hidden">
              
              {/* Highlight list */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                <h3 className="text-xs font-semibold text-foreground flex items-center gap-1 mb-2">
                  <BookMarked className="h-4 w-4 text-primary" />
                  Highlights & Annotations ({bookDetail.highlights?.length || 0})
                </h3>

                {bookDetail.highlights?.length === 0 ? (
                  <p className="text-center text-xs text-muted-foreground py-10 italic">
                    No highlights saved yet. Add your favorite quotes or ideas below.
                  </p>
                ) : (
                  bookDetail.highlights.map((hl) => (
                    <div key={hl.id} className="p-3 border border-border bg-card/45 rounded-lg flex gap-3 text-left">
                      <div className="flex-1 space-y-1.5">
                        <p className="text-[13px] leading-relaxed text-foreground italic font-serif">
                          &quot;{hl.text}&quot;
                        </p>
                        <div className="flex items-center gap-2 text-3xs text-muted-foreground font-mono">
                          {hl.location && (
                            <span className="flex items-center gap-0.5 text-primary">
                              <Clock className="h-3 w-3" />
                              Loc: {hl.location}
                            </span>
                          )}
                          {hl.tags && (
                            <span className="flex items-center gap-0.5 border border-border px-1 rounded bg-muted/40 text-[10px]">
                              <Tag className="h-3 w-3" />
                              {hl.tags}
                            </span>
                          )}
                          <span>{new Date(hl.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteHighlight(hl.id)}
                        className="p-1 rounded hover:bg-destructive/15 text-muted-foreground hover:text-destructive flex-shrink-0 self-start"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>

              {/* Add highlight input Form */}
              <form onSubmit={handleAddHighlight} className="p-3 border-t border-border bg-card/65 flex flex-col gap-2">
                <textarea
                  placeholder="Paste a new highlight from the book here..."
                  value={newHlText}
                  onChange={(e) => setNewHlText(e.target.value)}
                  className="w-full rounded-md border border-border bg-background p-2 text-xs outline-none focus:border-primary text-foreground resize-none h-14"
                  required
                />
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Location (e.g. Page 45, 12%)"
                    value={newHlLocation}
                    onChange={(e) => setNewHlLocation(e.target.value)}
                    className="flex-1 rounded-md border border-border bg-background px-2.5 py-1 text-xs outline-none focus:border-primary text-foreground"
                  />
                  <input
                    type="text"
                    placeholder="Tags (comma-separated)"
                    value={newHlTags}
                    onChange={(e) => setNewHlTags(e.target.value)}
                    className="flex-1 rounded-md border border-border bg-background px-2.5 py-1 text-xs outline-none focus:border-primary text-foreground"
                  />
                  <button
                    type="submit"
                    disabled={addingHl}
                    className="rounded-md bg-primary hover:bg-primary/95 text-primary-foreground font-semibold px-4 text-xs inline-flex items-center gap-1"
                  >
                    {addingHl ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    ) : (
                      <Plus className="h-3.5 w-3.5" />
                    )}
                    Add Highlight
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

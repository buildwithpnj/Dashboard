export type BookStatus = 'to-read' | 'reading' | 'finished' | 'DNF';

export interface Book {
  id: string;
  user_id: string;
  title: string;
  author: string;
  status: BookStatus;
  rating: number | null;
  started_at: string | null;
  finished_at: string | null;
  cover_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface BookCreate {
  title: string;
  author: string;
  status?: BookStatus;
  rating?: number;
  started_at?: string;
  finished_at?: string;
  cover_url?: string;
}

export interface Highlight {
  id: string;
  book_id: string;
  text: string;
  location: string | null;
  tags: string | null; // comma separated list
  created_at: string;
}

export interface HighlightCreate {
  book_id: string;
  text: string;
  location?: string;
  tags?: string;
}

'use client';

import { create } from 'zustand';
import { api, setAccessToken, getAccessToken } from '@/lib/api';

interface User {
  id: string;
  email: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const data = await api<{ access_token: string }>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    });
    setAccessToken(data.access_token);
    const user = await api<User>('/api/auth/me');
    set({ user, isAuthenticated: true, isLoading: false });
  },

  register: async (email: string, password: string) => {
    const data = await api<{ access_token: string }>('/api/auth/register', {
      method: 'POST',
      body: { email, password },
    });
    setAccessToken(data.access_token);
    const user = await api<User>('/api/auth/me');
    set({ user, isAuthenticated: true, isLoading: false });
  },

  logout: async () => {
    try {
      await api('/api/auth/logout', { method: 'POST' });
    } catch {
      // ignore
    }
    setAccessToken(null);
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  fetchUser: async () => {
    if (!getAccessToken()) {
      set({ isLoading: false });
      return;
    }
    try {
      const user = await api<User>('/api/auth/me');
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },
}));

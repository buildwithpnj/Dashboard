'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

// ─── Types ─────────────────────────────────────────────────

interface Account {
  id: string;
  user_id: string;
  name: string;
  type: 'bank' | 'cash' | 'card' | 'investment';
  currency: string;
  opening_balance: number;
  current_balance: number;
  created_at: string;
}

interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  currency: string;
  category_id: string | null;
  category_name: string | null;
  merchant: string;
  note: string;
  occurred_at: string;
  source: 'manual' | 'agent';
  created_at: string;
}

interface Category {
  id: string;
  name: string;
  parent_id: string | null;
  kind: 'expense' | 'income';
  children: Category[];
}

interface DashboardSummary {
  net_worth: number;
  net_worth_change: number;
  total_income_this_month: number;
  total_expenses_this_month: number;
  recent_transactions: Transaction[];
  spending_by_category: Array<{ category: string; amount: number; color: string }>;
  accounts_summary: Array<{ id: string; name: string; type: string; balance: number }>;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ─── Dashboard ─────────────────────────────────────────────

export function useDashboard() {
  return useQuery<DashboardSummary>({
    queryKey: ['dashboard'],
    queryFn: () => api<DashboardSummary>('/api/dashboard/summary'),
  });
}

// ─── Accounts ──────────────────────────────────────────────

export function useAccounts() {
  return useQuery<Account[]>({
    queryKey: ['accounts'],
    queryFn: () => api<Account[]>('/api/accounts'),
  });
}

export function useCreateAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; type: string; currency?: string; opening_balance?: number }) =>
      api<Account>('/api/accounts', { method: 'POST', body: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useDeleteAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      api(`/api/accounts/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

// ─── Transactions ──────────────────────────────────────────

export function useTransactions(params?: {
  page?: number;
  page_size?: number;
  account_id?: string;
  category_id?: string;
  search?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set('page', String(params.page));
  if (params?.page_size) searchParams.set('page_size', String(params.page_size));
  if (params?.account_id) searchParams.set('account_id', params.account_id);
  if (params?.category_id) searchParams.set('category_id', params.category_id);
  if (params?.search) searchParams.set('search', params.search);

  return useQuery<PaginatedResponse<Transaction>>({
    queryKey: ['transactions', params],
    queryFn: () =>
      api<PaginatedResponse<Transaction>>(`/api/transactions?${searchParams.toString()}`),
  });
}

export function useCreateTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      account_id: string;
      amount: number;
      category_id?: string;
      merchant?: string;
      note?: string;
      occurred_at?: string;
    }) => api<Transaction>('/api/transactions', { method: 'POST', body: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useDeleteTransaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      api(`/api/transactions/${id}`, { method: 'DELETE' }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['transactions'] });
      qc.invalidateQueries({ queryKey: ['accounts'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

// ─── Categories ────────────────────────────────────────────

export function useCategories() {
  return useQuery<Category[]>({
    queryKey: ['categories'],
    queryFn: () => api<Category[]>('/api/categories'),
  });
}

export function useCreateCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; kind: 'expense' | 'income'; parent_id?: string }) =>
      api<Category>('/api/categories', { method: 'POST', body: data }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories'] });
    },
  });
}

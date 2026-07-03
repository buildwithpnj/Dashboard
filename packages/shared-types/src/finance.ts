export type AccountType = 'bank' | 'cash' | 'card' | 'investment';
export type CategoryKind = 'expense' | 'income';
export type BudgetPeriod = 'monthly' | 'weekly' | 'yearly';

export interface Account {
  id: string;
  user_id: string;
  name: string;
  type: AccountType;
  currency: string;
  opening_balance: number;
  current_balance: number;
  created_at: string;
}

export interface AccountCreate {
  name: string;
  type: AccountType;
  currency?: string;
  opening_balance?: number;
}

export interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  currency: string;
  category_id: string | null;
  category_name?: string;
  merchant: string;
  note: string;
  occurred_at: string;
  source: 'manual' | 'agent';
  created_at: string;
}

export interface TransactionCreate {
  account_id: string;
  amount: number;
  category_id?: string;
  merchant?: string;
  note?: string;
  occurred_at?: string;
}

export interface Category {
  id: string;
  name: string;
  parent_id: string | null;
  kind: CategoryKind;
  children?: Category[];
}

export interface CategoryCreate {
  name: string;
  parent_id?: string;
  kind: CategoryKind;
}

export interface Budget {
  id: string;
  category_id: string;
  category_name?: string;
  period: BudgetPeriod;
  amount_limit: number;
  spent: number;
}

export interface BudgetCreate {
  category_id: string;
  period: BudgetPeriod;
  amount_limit: number;
}

export interface DashboardSummary {
  net_worth: number;
  net_worth_change: number;
  total_income_this_month: number;
  total_expenses_this_month: number;
  recent_transactions: Transaction[];
  spending_by_category: Array<{
    category: string;
    amount: number;
    color: string;
  }>;
  accounts_summary: Array<{
    id: string;
    name: string;
    type: AccountType;
    balance: number;
  }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

'use client';

import { useDashboard } from '@/hooks/use-finance';
import { formatCurrency, formatRelativeDate } from '@/lib/utils';
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  Activity,
} from 'lucide-react';

export default function DashboardPage() {
  const { data: summary, isLoading } = useDashboard();

  if (isLoading) {
    return (
      <div className="space-y-4 animate-fade-in">
        {/* Skeleton */}
        <div className="grid grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-4 h-24 animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="glass-card col-span-2 h-80 animate-pulse" />
          <div className="glass-card h-80 animate-pulse" />
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
        <Wallet className="h-12 w-12 text-muted-foreground mb-4" />
        <h2 className="text-lg font-semibold text-foreground">Welcome to WarBorn OS</h2>
        <p className="mt-1 text-sm text-muted-foreground max-w-md">
          Get started by adding an account in the Finance module. Press{' '}
          <span className="kbd">G</span> <span className="kbd">F</span> to navigate there.
        </p>
      </div>
    );
  }

  const netWorthPositive = summary.net_worth >= 0;
  const changePositive = summary.net_worth_change >= 0;

  return (
    <div className="space-y-4 animate-fade-in" id="dashboard">
      {/* ─── Stat Cards ────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Net Worth */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
              Net Worth
            </span>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </div>
          <p className={`mt-2 text-xl font-bold ${netWorthPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
            {formatCurrency(summary.net_worth)}
          </p>
          <div className="mt-1 flex items-center gap-1">
            {changePositive ? (
              <ArrowUpRight className="h-3 w-3 text-emerald-400" />
            ) : (
              <ArrowDownRight className="h-3 w-3 text-rose-400" />
            )}
            <span className={`text-2xs ${changePositive ? 'text-emerald-400' : 'text-rose-400'}`}>
              {formatCurrency(Math.abs(summary.net_worth_change))} this month
            </span>
          </div>
        </div>

        {/* Income */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
              Income
            </span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="mt-2 text-xl font-bold text-emerald-400">
            {formatCurrency(summary.total_income_this_month)}
          </p>
          <p className="mt-1 text-2xs text-muted-foreground">This month</p>
        </div>

        {/* Expenses */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
              Expenses
            </span>
            <TrendingDown className="h-4 w-4 text-rose-400" />
          </div>
          <p className="mt-2 text-xl font-bold text-rose-400">
            {formatCurrency(summary.total_expenses_this_month)}
          </p>
          <p className="mt-1 text-2xs text-muted-foreground">This month</p>
        </div>

        {/* Accounts */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between">
            <span className="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
              Accounts
            </span>
            <Activity className="h-4 w-4 text-sky-400" />
          </div>
          <p className="mt-2 text-xl font-bold text-foreground">
            {summary.accounts_summary.length}
          </p>
          <p className="mt-1 text-2xs text-muted-foreground">Active accounts</p>
        </div>
      </div>

      {/* ─── Bottom section ────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* Recent Transactions */}
        <div className="glass-card col-span-2 overflow-hidden">
          <div className="border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">Recent Transactions</h2>
          </div>
          <div className="divide-y divide-border">
            {summary.recent_transactions.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-muted-foreground">
                No transactions yet
              </p>
            ) : (
              summary.recent_transactions.map((t) => (
                <div key={t.id} className="flex items-center px-4 py-2.5 hover:bg-accent/50 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-medium text-foreground truncate">
                      {t.merchant || 'Untitled'}
                    </p>
                    <p className="text-2xs text-muted-foreground">
                      {t.category_name || 'Uncategorized'} · {formatRelativeDate(t.occurred_at)}
                    </p>
                  </div>
                  <span
                    className={`text-[13px] font-mono font-medium tabular-nums ${
                      t.amount >= 0 ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {t.amount >= 0 ? '+' : ''}
                    {formatCurrency(t.amount)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Accounts Summary */}
        <div className="glass-card overflow-hidden">
          <div className="border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">Accounts</h2>
          </div>
          <div className="divide-y divide-border">
            {summary.accounts_summary.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-muted-foreground">
                No accounts yet
              </p>
            ) : (
              summary.accounts_summary.map((a) => (
                <div key={a.id} className="flex items-center justify-between px-4 py-2.5">
                  <div>
                    <p className="text-[13px] font-medium text-foreground">{a.name}</p>
                    <p className="text-2xs text-muted-foreground capitalize">{a.type}</p>
                  </div>
                  <span
                    className={`text-[13px] font-mono font-medium tabular-nums ${
                      a.balance >= 0 ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {formatCurrency(a.balance)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

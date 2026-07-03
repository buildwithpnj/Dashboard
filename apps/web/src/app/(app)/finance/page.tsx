'use client';

import { useState } from 'react';
import { useAccounts, useCreateAccount, useTransactions, useCreateTransaction, useCategories } from '@/hooks/use-finance';
import { formatCurrency, formatRelativeDate } from '@/lib/utils';
import { Plus, Wallet, CreditCard, Banknote, TrendingUp } from 'lucide-react';
import { AccountForm } from '@/components/finance/account-form';
import { TransactionForm } from '@/components/finance/transaction-form';
import { SpendingChart } from '@/components/finance/spending-chart';

const accountIcons: Record<string, typeof Wallet> = {
  bank: Wallet,
  cash: Banknote,
  card: CreditCard,
  investment: TrendingUp,
};

export default function FinancePage() {
  const { data: accounts, isLoading: accountsLoading } = useAccounts();
  const { data: transactionsData, isLoading: txLoading } = useTransactions({ page_size: 20 });
  const { data: categories } = useCategories();
  const [showAccountForm, setShowAccountForm] = useState(false);
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  const transactions = transactionsData?.items || [];

  // Calculate total balance
  const totalBalance = accounts?.reduce((sum, a) => sum + a.current_balance, 0) || 0;

  return (
    <div className="space-y-4 animate-fade-in" id="finance-page">
      {/* ─── Top bar ───────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-foreground">Finance</h2>
          <p className="text-2xs text-muted-foreground">
            Total balance: <span className="text-foreground font-medium">{formatCurrency(totalBalance)}</span>
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAccountForm(true)}
            className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-[13px] text-foreground hover:bg-accent transition-colors"
            id="add-account-btn"
          >
            <Plus className="h-3.5 w-3.5" />
            Account
          </button>
          <button
            onClick={() => setShowTransactionForm(true)}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-[13px] font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            id="add-transaction-btn"
          >
            <Plus className="h-3.5 w-3.5" />
            Transaction
          </button>
        </div>
      </div>

      {/* ─── Accounts ──────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {accountsLoading ? (
          [...Array(3)].map((_, i) => (
            <div key={i} className="glass-card h-24 animate-pulse" />
          ))
        ) : accounts?.length === 0 ? (
          <div className="glass-card col-span-full p-8 text-center">
            <Wallet className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              No accounts yet. Add your first account to get started.
            </p>
          </div>
        ) : (
          accounts?.map((account) => {
            const Icon = accountIcons[account.type] || Wallet;
            return (
              <div key={account.id} className="glass-card p-4 hover:border-primary/30 transition-colors cursor-pointer">
                <div className="flex items-center gap-2">
                  <div className="rounded-md bg-primary/10 p-1.5">
                    <Icon className="h-4 w-4 text-primary" />
                  </div>
                  <span className="text-[13px] font-medium text-foreground truncate">
                    {account.name}
                  </span>
                </div>
                <p
                  className={`mt-3 text-lg font-bold tabular-nums ${
                    account.current_balance >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {formatCurrency(account.current_balance, account.currency)}
                </p>
                <p className="mt-0.5 text-2xs text-muted-foreground capitalize">{account.type}</p>
              </div>
            );
          })
        )}
      </div>

      {/* ─── Main content ──────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* Transactions table */}
        <div className="glass-card col-span-2 overflow-hidden">
          <div className="border-b border-border px-4 py-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-foreground">Recent Transactions</h3>
            <span className="text-2xs text-muted-foreground kbd">A</span>
          </div>

          {txLoading ? (
            <div className="p-4 space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-10 rounded bg-muted animate-pulse" />
              ))}
            </div>
          ) : transactions.length === 0 ? (
            <p className="p-8 text-center text-sm text-muted-foreground">
              No transactions yet. Press <span className="kbd">A</span> to add one.
            </p>
          ) : (
            <table className="w-full table-dense">
              <thead>
                <tr className="border-b border-border">
                  <th>Date</th>
                  <th>Merchant</th>
                  <th>Category</th>
                  <th className="text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id} className="hover:bg-accent/50 transition-colors cursor-pointer">
                    <td className="text-muted-foreground">{formatRelativeDate(t.occurred_at)}</td>
                    <td className="font-medium">{t.merchant || '—'}</td>
                    <td className="text-muted-foreground">{t.category_name || 'Uncategorized'}</td>
                    <td className={`text-right font-mono tabular-nums ${t.amount >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {t.amount >= 0 ? '+' : ''}{formatCurrency(t.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Spending chart */}
        <div className="glass-card overflow-hidden">
          <div className="border-b border-border px-4 py-3">
            <h3 className="text-sm font-semibold text-foreground">Spending by Category</h3>
          </div>
          <div className="p-4">
            <SpendingChart />
          </div>
        </div>
      </div>

      {/* ─── Modals ────────────────────────────────────────── */}
      {showAccountForm && (
        <AccountForm onClose={() => setShowAccountForm(false)} />
      )}
      {showTransactionForm && (
        <TransactionForm
          accounts={accounts || []}
          categories={categories || []}
          onClose={() => setShowTransactionForm(false)}
        />
      )}
    </div>
  );
}

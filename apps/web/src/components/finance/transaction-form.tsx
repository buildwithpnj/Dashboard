'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateTransaction } from '@/hooks/use-finance';

interface Account {
  id: string;
  name: string;
  type: string;
}

interface Category {
  id: string;
  name: string;
  kind: string;
  children: Category[];
}

interface TransactionFormProps {
  accounts: Account[];
  categories: Category[];
  onClose: () => void;
}

export function TransactionForm({ accounts, categories, onClose }: TransactionFormProps) {
  const createTransaction = useCreateTransaction();
  const [accountId, setAccountId] = useState(accounts[0]?.id || '');
  const [amount, setAmount] = useState('');
  const [isExpense, setIsExpense] = useState(true);
  const [categoryId, setCategoryId] = useState('');
  const [merchant, setMerchant] = useState('');
  const [note, setNote] = useState('');
  const [occurredAt, setOccurredAt] = useState(new Date().toISOString().slice(0, 16));
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount === 0) {
      setError('Please enter a valid amount');
      return;
    }

    try {
      await createTransaction.mutateAsync({
        account_id: accountId,
        amount: isExpense ? -Math.abs(numAmount) : Math.abs(numAmount),
        category_id: categoryId || undefined,
        merchant,
        note,
        occurred_at: new Date(occurredAt).toISOString(),
      });
      onClose();
    } catch (err: any) {
      setError(err.detail || err.message || 'Failed to create transaction');
    }
  }

  // Flatten categories for select
  function flattenCategories(cats: Category[], prefix = ''): Array<{ id: string; label: string }> {
    const result: Array<{ id: string; label: string }> = [];
    for (const cat of cats) {
      result.push({ id: cat.id, label: prefix + cat.name });
      if (cat.children?.length) {
        result.push(...flattenCategories(cat.children, prefix + '  '));
      }
    }
    return result;
  }

  const flatCategories = flattenCategories(categories);

  return (
    <div className="fixed inset-0 z-50" id="transaction-form-modal">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={onClose} />
      <div className="absolute left-1/2 top-[10%] w-full max-w-md -translate-x-1/2 animate-slide-down">
        <form onSubmit={handleSubmit} className="rounded-xl border border-border bg-popover shadow-2xl shadow-black/40 overflow-hidden">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">New Transaction</h2>
            <button type="button" onClick={onClose} className="rounded p-1 text-muted-foreground hover:bg-accent">
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="p-4 space-y-4">
            {error && (
              <div className="rounded-md bg-destructive/10 border border-destructive/20 px-3 py-2 text-[13px] text-destructive">
                {error}
              </div>
            )}

            {/* Type toggle */}
            <div className="flex rounded-md border border-border overflow-hidden">
              <button
                type="button"
                onClick={() => setIsExpense(true)}
                className={`flex-1 py-1.5 text-[13px] font-medium transition-colors ${
                  isExpense ? 'bg-rose-500/10 text-rose-400 border-r border-border' : 'text-muted-foreground hover:bg-accent border-r border-border'
                }`}
              >
                Expense
              </button>
              <button
                type="button"
                onClick={() => setIsExpense(false)}
                className={`flex-1 py-1.5 text-[13px] font-medium transition-colors ${
                  !isExpense ? 'bg-emerald-500/10 text-emerald-400' : 'text-muted-foreground hover:bg-accent'
                }`}
              >
                Income
              </button>
            </div>

            {/* Amount */}
            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Amount</label>
              <input
                type="number"
                step="0.01"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className={`w-full rounded-md border border-input bg-background px-3 py-2 text-lg font-mono font-bold focus:outline-none focus:ring-2 focus:ring-ring ${
                  isExpense ? 'text-rose-400' : 'text-emerald-400'
                }`}
                placeholder="0.00"
                required
                autoFocus
              />
            </div>

            {/* Account */}
            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Account</label>
              <select
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                required
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}</option>
                ))}
              </select>
            </div>

            {/* Category */}
            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Category</label>
              <select
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Uncategorized</option>
                {flatCategories.map((c) => (
                  <option key={c.id} value={c.id}>{c.label}</option>
                ))}
              </select>
            </div>

            {/* Merchant + Date */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[13px] font-medium text-foreground mb-1.5">Merchant</label>
                <input
                  type="text"
                  value={merchant}
                  onChange={(e) => setMerchant(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="e.g., Swiggy"
                />
              </div>
              <div>
                <label className="block text-[13px] font-medium text-foreground mb-1.5">Date</label>
                <input
                  type="datetime-local"
                  value={occurredAt}
                  onChange={(e) => setOccurredAt(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            </div>

            {/* Note */}
            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Note</label>
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Optional note"
              />
            </div>
          </div>

          <div className="border-t border-border px-4 py-3 flex items-center justify-between">
            <span className="text-2xs text-muted-foreground">
              <span className="kbd">⌘</span> <span className="kbd">↵</span> to save
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-md border border-border px-3 py-1.5 text-[13px] text-foreground hover:bg-accent transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createTransaction.isPending}
                className="rounded-md bg-primary px-3 py-1.5 text-[13px] font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {createTransaction.isPending ? 'Saving...' : 'Save Transaction'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

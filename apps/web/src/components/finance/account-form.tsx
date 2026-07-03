'use client';

import { useState } from 'react';
import { X } from 'lucide-react';
import { useCreateAccount } from '@/hooks/use-finance';

interface AccountFormProps {
  onClose: () => void;
}

export function AccountForm({ onClose }: AccountFormProps) {
  const createAccount = useCreateAccount();
  const [name, setName] = useState('');
  const [type, setType] = useState('bank');
  const [currency, setCurrency] = useState('INR');
  const [openingBalance, setOpeningBalance] = useState('0');
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      await createAccount.mutateAsync({
        name,
        type,
        currency,
        opening_balance: parseFloat(openingBalance) || 0,
      });
      onClose();
    } catch (err: any) {
      setError(err.detail || err.message || 'Failed to create account');
    }
  }

  return (
    <div className="fixed inset-0 z-50" id="account-form-modal">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={onClose} />
      <div className="absolute left-1/2 top-[15%] w-full max-w-md -translate-x-1/2 animate-slide-down">
        <form onSubmit={handleSubmit} className="rounded-xl border border-border bg-popover shadow-2xl shadow-black/40 overflow-hidden">
          <div className="flex items-center justify-between border-b border-border px-4 py-3">
            <h2 className="text-sm font-semibold text-foreground">New Account</h2>
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

            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="e.g., HDFC Savings"
                required
                autoFocus
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[13px] font-medium text-foreground mb-1.5">Type</label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="bank">Bank</option>
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="investment">Investment</option>
                </select>
              </div>
              <div>
                <label className="block text-[13px] font-medium text-foreground mb-1.5">Currency</label>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="INR">INR</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-[13px] font-medium text-foreground mb-1.5">Opening Balance</label>
              <input
                type="number"
                step="0.01"
                value={openingBalance}
                onChange={(e) => setOpeningBalance(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground font-mono focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
          </div>

          <div className="border-t border-border px-4 py-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-md border border-border px-3 py-1.5 text-[13px] text-foreground hover:bg-accent transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createAccount.isPending}
              className="rounded-md bg-primary px-3 py-1.5 text-[13px] font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {createAccount.isPending ? 'Creating...' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

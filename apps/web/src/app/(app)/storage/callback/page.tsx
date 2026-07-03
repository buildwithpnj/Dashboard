'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function StorageCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');
  const callbackCalled = useRef(false);

  useEffect(() => {
    // Prevent duplicate calls in React StrictMode
    if (callbackCalled.current) return;
    callbackCalled.current = true;

    const code = searchParams.get('code');

    if (!code) {
      setStatus('error');
      setErrorMsg('No authorization code found in URL.');
      return;
    }

    async function handleCallback() {
      try {
        await api('/api/gdrive/callback', {
          method: 'POST',
          body: { code },
        });
        setStatus('success');
        setTimeout(() => {
          router.push('/storage');
        }, 2000);
      } catch (err: unknown) {
        setStatus('error');
        const message = err instanceof Error ? err.message : 'Unknown error during connection';
        setErrorMsg(message);
      }
    }

    handleCallback();
  }, [searchParams, router]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-6 text-center">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 shadow-lg">
        {status === 'loading' && (
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <h1 className="text-xl font-semibold text-foreground">Connecting Google Drive...</h1>
            <p className="text-sm text-muted-foreground">
              Please wait while we establish a secure connection to your storage.
            </p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center gap-4">
            <CheckCircle2 className="h-12 w-12 text-emerald-500 animate-bounce" />
            <h1 className="text-xl font-semibold text-foreground">Connection Successful!</h1>
            <p className="text-sm text-muted-foreground">
              Google Drive is now connected to your Personal OS dashboard. Redirecting...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center gap-4">
            <XCircle className="h-12 w-12 text-destructive" />
            <h1 className="text-xl font-semibold text-foreground">Connection Failed</h1>
            <p className="text-sm text-destructive font-medium">{errorMsg}</p>
            <button
              onClick={() => router.push('/storage')}
              className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              Go Back
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

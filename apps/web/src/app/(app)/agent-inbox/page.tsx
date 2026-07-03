'use client';

import { Inbox } from 'lucide-react';

export default function AgentInboxPage() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in" id="agent-inbox-page">
      <Inbox className="h-12 w-12 text-muted-foreground mb-4" />
      <h2 className="text-lg font-semibold text-foreground">Agent Inbox</h2>
      <p className="mt-1 text-sm text-muted-foreground max-w-md">
        Review queue for AI-proposed entries — coming in Phase 8.
      </p>
    </div>
  );
}

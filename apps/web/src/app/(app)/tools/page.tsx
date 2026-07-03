'use client';

import { Wrench } from 'lucide-react';

export default function ToolsPage() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in" id="tools-page">
      <Wrench className="h-12 w-12 text-muted-foreground mb-4" />
      <h2 className="text-lg font-semibold text-foreground">Tools</h2>
      <p className="mt-1 text-sm text-muted-foreground max-w-md">
        Generic database builder — table, board, and calendar views — coming in Phase 7.
      </p>
    </div>
  );
}

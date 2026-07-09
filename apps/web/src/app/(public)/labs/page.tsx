import React from 'react';
import { getExperiments } from '@/lib/content';
import { LabsList } from '@/components/labs-list';

export const metadata = {
  title: 'Labs',
  description: 'AI R&D lab: active experiments, model testing notes, multi-agent frameworks, and voice UI prototypes.',
};

export default function PublicLabsPage() {
  const experiments = getExperiments();

  return (
    <div className="flex flex-col gap-8 text-left">
      {/* Title */}
      <div className="flex flex-col gap-2">
        <div className="font-pixel text-[11px] text-primary tracking-wider uppercase">{"// R&D LABS"}</div>
        <h1 className="text-3xl sm:text-4xl font-pixel text-foreground">Active Experiments</h1>
        <p className="text-base text-muted-foreground max-w-xl leading-relaxed">
          Where ideas get tested, evaluated, and documented before they ever become full-scale products.
        </p>
      </div>

      {/* Filter and listing cards */}
      <LabsList initialExperiments={experiments} />
    </div>
  );
}

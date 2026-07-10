'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Heart, Activity } from 'lucide-react';
import interventionsData from '@/lib/interventions.json';

interface Intervention {
  id: number;
  category: string;
  text: string;
}

const items = interventionsData as Intervention[];

export function RecoveryIntervention() {
  const [activeItem, setActiveItem] = useState<Intervention>(items[0]);
  const [fadeState, setFadeState] = useState<'in' | 'out'>('in');
  
  // Track recently shown items and category history for smart rotation
  const shownQueueRef = useRef<number[]>([]);
  const lastCategoryRef = useRef<string>('');

  useEffect(() => {
    // Initialize with first item details
    shownQueueRef.current = [items[0].id];
    lastCategoryRef.current = items[0].category;
  }, []);

  const selectNextSmartItem = () => {
    const queue = shownQueueRef.current;
    const lastCategory = lastCategoryRef.current;
    
    // Filter out items in the queue or matching the last category
    let candidates = items.filter(
      item => !queue.includes(item.id) && item.category !== lastCategory
    );

    // Fallback if list is exhausted
    if (candidates.length === 0) {
      candidates = items.filter(item => item.category !== lastCategory);
    }
    if (candidates.length === 0) {
      candidates = items;
    }

    // Pick random candidate
    const nextItem = candidates[Math.floor(Math.random() * candidates.length)];
    
    // Update trackers
    const newQueue = [...queue, nextItem.id];
    if (newQueue.length > 15) {
      newQueue.shift(); // keep queue under 15 items
    }
    shownQueueRef.current = newQueue;
    lastCategoryRef.current = nextItem.category;

    return nextItem;
  };

  useEffect(() => {
    const interval = setInterval(() => {
      // Start fade out transition
      setFadeState('out');

      // Swap content half-way through the 7-second ex-cycle during transparent phase
      const swapTimer = setTimeout(() => {
        const next = selectNextSmartItem();
        setActiveItem(next);
        setFadeState('in');
      }, 600); // Wait for fade out to complete

      return () => clearTimeout(swapTimer);
    }, 7000); // 7-second rotation loop

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full rounded-2xl border border-border bg-card/30 p-6 flex flex-col items-center justify-center text-center relative overflow-hidden select-none min-h-[160px] grid-dots shadow-[0_0_15px_rgba(59,130,246,0.03)]">
      {/* Blueprint grid layout subtle header details */}
      <div className="absolute top-3 left-4 flex items-center gap-1.5 font-mono text-[9px] text-muted-foreground/60 uppercase tracking-widest">
        <Heart className="h-3 w-3 text-primary animate-pulse" />
        <span>Cognitive Interrupter Node</span>
      </div>
      <div className="absolute top-3 right-4 font-mono text-[9px] text-muted-foreground/60 uppercase tracking-widest">
        <span>MODULATION: {activeItem.category}</span>
      </div>

      {/* Main Intervention Text Content */}
      <div 
        className={`max-w-xl transition-all duration-700 transform px-4 py-3 mt-2 ${
          fadeState === 'in' 
            ? 'opacity-100 translate-y-0 scale-100 blur-0' 
            : 'opacity-0 -translate-y-2.5 scale-[0.98] blur-sm'
        }`}
      >
        <p className="text-sm md:text-base font-semibold leading-relaxed tracking-wide text-foreground font-sans drop-shadow-[0_0_8px_var(--ds-color)]">
          {activeItem.text}
        </p>
      </div>

      {/* Breathing rate subtle telemetry indicator bar */}
      <div className="absolute bottom-2 inset-x-6 flex items-center justify-between text-[8px] font-mono text-muted-foreground/40 uppercase tracking-widest pt-2 border-t border-border/10">
        <span>System Status: Mindful</span>
        <div className="flex gap-1 items-center">
          <span>Pulse</span>
          <div className="flex gap-0.5 items-end h-2 w-8">
            <span className="w-[2px] h-[3px] bg-primary/45 rounded-full animate-pulse" />
            <span className="w-[2px] h-[6px] bg-primary/45 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
            <span className="w-[2px] h-[4px] bg-primary/45 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
            <span className="w-[2px] h-[2px] bg-primary/45 rounded-full animate-pulse" style={{ animationDelay: '450ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}

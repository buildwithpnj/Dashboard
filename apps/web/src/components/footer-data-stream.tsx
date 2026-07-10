'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Node Definition ──────────────────────────────────────────────────────────
interface DataNode {
  id: string;
  label: string;
  // Positions expressed as percentages (0–100) of the SVG viewBox (1200×140)
  xPct: number;
  yPct: number;
  desc: string;
  connected?: boolean;
}

// ViewBox dimensions — we use a fixed logical canvas that scales
const VW = 1200;
const VH = 140;

const NODES: DataNode[] = [
  { id: 'api',       label: 'API',       xPct: 10,   yPct: 25,  desc: 'REST & gRPC Integration Endpoints' },
  { id: 'llm',       label: 'LLM',       xPct: 22,   yPct: 25,  desc: 'Large Language Model Router & Cost Optimization' },
  { id: 'rag',       label: 'RAG',       xPct: 34,   yPct: 25,  desc: 'Retrieval-Augmented Generation context pipeline' },
  { id: 'json',      label: 'JSON',      xPct: 46,   yPct: 25,  desc: 'Structured schema serialization layers' },
  { id: 'sql',       label: 'SQL',       xPct: 58,   yPct: 25,  desc: 'Relational transaction databases & query planners' },
  { id: 'cache',     label: 'CACHE',     xPct: 70,   yPct: 25,  desc: 'Redis cache synchronization layer' },
  { id: 'gpu',       label: 'GPU',       xPct: 82,   yPct: 25,  desc: 'Hardware inference acceleration cluster' },
  { id: 'cpu',       label: 'CPU',       xPct: 94,   yPct: 25,  desc: 'Task orchestrator & CPU scheduling grid' },
  
  { id: 'mcp',       label: 'MCP',       xPct: 94,   yPct: 75,  desc: 'Model Context Protocol server integrations' },
  { id: 'voice',     label: 'VOICE',     xPct: 82,   yPct: 75,  desc: 'Low-latency Realtime multilingual voice pipelines' },
  { id: 'tools',     label: 'TOOLS',     xPct: 70,   yPct: 75,  desc: 'Dynamic agentic tools execution framework' },
  { id: 'node',      label: 'NODE',      xPct: 58,   yPct: 75,  desc: 'Distributed microservice runtime nodes' },
  { id: 'token',     label: 'TOKEN',     xPct: 46,   yPct: 75,  desc: 'Context token streaming & rate limiting' },
  { id: 'vector',    label: 'VECTOR',    xPct: 34,   yPct: 75,  desc: 'Vector database similarity indexing' },
  { id: 'memory',    label: 'MEMORY',    xPct: 22,   yPct: 75,  desc: 'Persistent chat state & episodic memory structures' },
  { id: 'embedding', label: 'EMBEDDING', xPct: 10,   yPct: 75,  desc: 'High-dimensional text representation model' },
];

// Convert percentage nodes to absolute SVG coordinates
function nodeToXY(n: DataNode) {
  return { x: (n.xPct / 100) * VW, y: (n.yPct / 100) * VH };
}

// Precomputed neighbor mapping to make packets traverse horizontally & vertically
const NODE_NEIGHBORS: Record<string, string[]> = {
  api: ['llm', 'embedding'],
  llm: ['api', 'rag', 'memory'],
  rag: ['llm', 'json', 'vector'],
  json: ['rag', 'sql', 'token'],
  sql: ['json', 'cache', 'node'],
  cache: ['sql', 'gpu', 'tools'],
  gpu: ['cache', 'cpu', 'voice'],
  cpu: ['gpu', 'mcp'],
  mcp: ['cpu', 'voice'],
  voice: ['mcp', 'tools', 'gpu'],
  tools: ['voice', 'node', 'cache'],
  node: ['tools', 'token', 'sql'],
  token: ['node', 'vector', 'json'],
  vector: ['token', 'memory', 'rag'],
  memory: ['vector', 'embedding', 'llm'],
  embedding: ['memory', 'api']
};

// Build a double-rung grid path connecting all nodes in the 2x8 ladder
function buildGridPath(): string {
  let d = '';
  const xStart = (10 / 100) * VW;
  const xEnd = (94 / 100) * VW;
  const yTop = (25 / 100) * VH;
  const yBot = (75 / 100) * VH;

  // Horizontal rails
  d += `M ${xStart},${yTop} L ${xEnd},${yTop} `;
  d += `M ${xStart},${yBot} L ${xEnd},${yBot} `;

  // Vertical columns
  const cols = [10, 22, 34, 46, 58, 70, 82, 94];
  cols.forEach(pct => {
    const x = (pct / 100) * VW;
    d += `M ${x},${yTop} L ${x},${yBot} `;
  });

  return d;
}

const CIRCUIT_PATH = buildGridPath();

const STATUS_LABELS = [
  'SYSTEM ONLINE', 'MEMORY ACTIVE', 'TOOLS READY', 'VOICE READY',
  'RAG INDEXED', 'MODELS LOADED', 'PIPELINES NOMINAL', 'VECTOR CACHE SYNCD'
];

interface PacketState {
  currNodeId: string;
  targetNodeId: string;
  x: number;
  y: number;
  progress: number;
  trail: { x: number; y: number }[];
}

export function FooterDataStream() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [collected,       setCollected]       = useState<Record<string, boolean>>({});
  const [activeNode,      setActiveNode]       = useState<DataNode | null>(null);
  const [pulseNode,       setPulseNode]        = useState<string | null>(null);
  const [statusText,      setStatusText]       = useState('SYSTEM ONLINE');
  const [showSyncMessage, setShowSyncMessage]  = useState(false);
  const [inViewport,      setInViewport]       = useState(false);

  // heroColor: read from CSS variable and subscribe to changes
  const [heroColor, setHeroColor] = useState('hsl(217 91% 65%)');
  const svgRef = useRef<SVGSVGElement>(null);

  // Watch for hero color CSS variable changes
  useEffect(() => {
    const read = () => {
      const v = getComputedStyle(document.documentElement)
        .getPropertyValue('--hero-active-color').trim();
      if (v) setHeroColor(v);
    };
    read();
    const id = setInterval(read, 300);
    return () => clearInterval(id);
  }, []);

  // Intersection observer
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => setInViewport(e.isIntersecting), { threshold: 0.1 });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Set up 3 active packets with randomized starting nodes and direction choices
  const packetsRef = useRef<PacketState[]>([
    {
      currNodeId: 'api',
      targetNodeId: 'llm',
      x: nodeToXY(NODES[0]).x,
      y: nodeToXY(NODES[0]).y,
      progress: 0,
      trail: []
    },
    {
      currNodeId: 'tools',
      targetNodeId: 'node',
      x: nodeToXY(NODES[10]).x,
      y: nodeToXY(NODES[10]).y,
      progress: 0,
      trail: []
    },
    {
      currNodeId: 'gpu',
      targetNodeId: 'voice',
      x: nodeToXY(NODES[6]).x,
      y: nodeToXY(NODES[6]).y,
      progress: 0,
      trail: []
    }
  ]);

  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    if (!inViewport) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      return;
    }
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const animate = () => {
      const speed = 2.0; // Pixels per frame

      packetsRef.current.forEach((packet, pIdx) => {
        const currNode = NODES.find(n => n.id === packet.currNodeId)!;
        const targetNode = NODES.find(n => n.id === packet.targetNodeId)!;
        
        const startPt = nodeToXY(currNode);
        const endPt = nodeToXY(targetNode);
        
        const dx = endPt.x - startPt.x;
        const dy = endPt.y - startPt.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Advance progress
        if (distance > 0) {
          packet.progress += speed / distance;
        } else {
          packet.progress = 1.0;
        }

        if (packet.progress >= 1.0) {
          // Reached target node!
          packet.progress = 0;
          
          // Trigger node pulse and collection highlight
          const reachedId = packet.targetNodeId;
          setCollected(prev => ({ ...prev, [reachedId]: true }));
          setTimeout(() => {
            setCollected(prev => {
              const next = { ...prev };
              delete next[reachedId];
              return next;
            });
          }, 1500);

          setPulseNode(reachedId);
          setTimeout(() => setPulseNode(null), 400);
          setStatusText(STATUS_LABELS[Math.floor(Math.random() * STATUS_LABELS.length)]);

          // Select next target node randomly from neighbors, avoiding backtracking where possible
          const nextChoices = NODE_NEIGHBORS[reachedId].filter(id => id !== packet.currNodeId);
          const chosenId = nextChoices.length > 0 
            ? nextChoices[Math.floor(Math.random() * nextChoices.length)]
            : NODE_NEIGHBORS[reachedId][0];

          packet.currNodeId = reachedId;
          packet.targetNodeId = chosenId;

          packet.x = endPt.x;
          packet.y = endPt.y;
        } else {
          // Calculate current coordinate along segment
          packet.x = startPt.x + dx * packet.progress;
          packet.y = startPt.y + dy * packet.progress;
        }

        // Manage trail position history
        packet.trail.push({ x: packet.x, y: packet.y });
        if (packet.trail.length > 5) {
          packet.trail.shift();
        }

        // Apply positions directly to DOM elements
        const headEl = document.getElementById(`ds-packet-${pIdx}-head`);
        if (headEl) {
          headEl.style.transform = `translate(${packet.x - 3.25}px, ${packet.y - 3.25}px)`;
        }

        for (let tIdx = 0; tIdx < 5; tIdx++) {
          const trailEl = document.getElementById(`ds-packet-${pIdx}-trail-${tIdx}`);
          if (trailEl) {
            const pt = packet.trail[packet.trail.length - 1 - tIdx] || { x: packet.x, y: packet.y };
            trailEl.style.transform = `translate(${pt.x - 2}px, ${pt.y - 2}px)`;
          }
        }
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    return () => { if (animationRef.current) cancelAnimationFrame(animationRef.current); };
  }, [inViewport]);

  const glow = heroColor || '#3B82F6';
  const collectColor = glow;
  const glowCSS = `0 0 12px ${glow}, 0 0 24px ${glow}66`;

  return (
    <div
      ref={containerRef}
      className="w-full relative border border-border/40 rounded-xl bg-card/10 backdrop-blur-md overflow-hidden py-6 select-none"
      style={{ '--ds-color': glow } as React.CSSProperties}
    >
      {/* Blueprint grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(148,163,184,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(148,163,184,0.03)_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      {/* Ambient glow halo behind the visualiser */}
      <div
        className="absolute inset-0 opacity-15 dark:opacity-20 pointer-events-none"
        style={{ background: `radial-gradient(ellipse 60% 60% at 50% 50%, ${glow}22, transparent)` }}
      />

      {/* Status bar */}
      <div className="flex items-center justify-between px-6 pb-4 border-b border-border/20 font-mono text-[9px] text-muted-foreground/80">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-sm animate-pulse" style={{ backgroundColor: glow }} />
            AI NETWORK: ONLINE
          </span>
          <span className="hidden sm:inline">RATE: 1.6MBPS</span>
          <span className="hidden md:inline">COMPILATION: PNJ-SYS.INFRA</span>
        </div>
        <div className="font-semibold tracking-wider" style={{ color: glow }}>
          STATUS: {statusText}
        </div>
      </div>

      {/* ── Full-width SVG Canvas (no scroll) ── */}
      <div className="relative w-full mt-2" style={{ aspectRatio: `${VW}/${VH}` }}>
        <svg
          ref={svgRef}
          className="absolute inset-0 w-full h-full"
          viewBox={`0 0 ${VW} ${VH}`}
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Base solid wire track - perfectly visible in light and dark mode */}
          <path
            d={CIRCUIT_PATH}
            fill="none"
            stroke="currentColor"
            className="text-neutral-300/40 dark:text-neutral-700/50"
            strokeWidth="1.2"
          />

          {/* Glowing colour-synced underlay */}
          <path
            d={CIRCUIT_PATH}
            fill="none"
            stroke={glow}
            strokeWidth="2.5"
            opacity="0.08"
          />

          {/* Node hit areas + anchors (rendered in SVG for perfect scaling) */}
          {NODES.map(node => {
            const { x, y } = nodeToXY(node);
            const isCollected = collected[node.id];
            const isPulsing   = pulseNode === node.id;
            const isHovered   = activeNode?.id === node.id;
            const isConnected = node.connected !== false;

            return (
              <g
                key={node.id}
                transform={`translate(${x},${y})`}
                onMouseEnter={() => isConnected && setActiveNode(node)}
                onMouseLeave={() => isConnected && setActiveNode(null)}
                className={isConnected ? "cursor-pointer" : "pointer-events-none"}
              >
                {/* Outer square pulse ring on collect */}
                {isPulsing && isConnected && (
                  <rect
                    x="-6" y="-6" width="12" height="12" rx="1"
                    fill="none" stroke={collectColor} strokeWidth="1" opacity="0.6"
                  >
                    <animate attributeName="x" from="-6" to="-15" dur="0.4s" fill="freeze" />
                    <animate attributeName="y" from="-6" to="-15" dur="0.4s" fill="freeze" />
                    <animate attributeName="width" from="12" to="30" dur="0.4s" fill="freeze" />
                    <animate attributeName="height" from="12" to="30" dur="0.4s" fill="freeze" />
                    <animate attributeName="opacity" from="0.8" to="0" dur="0.4s" fill="freeze" />
                  </rect>
                )}

                {/* Anchor square container - styling for light and dark modes */}
                <rect
                  x="-5" y="-5" width="10" height="10" rx="2"
                  fill="none"
                  stroke={!isConnected ? 'currentColor' : (isCollected ? collectColor : (isHovered ? glow : 'currentColor'))}
                  strokeWidth="0.8"
                  className={!isConnected 
                    ? "text-neutral-200 dark:text-neutral-800" 
                    : (isCollected || isHovered ? "" : "text-neutral-400 dark:text-neutral-500")}
                  style={{ transition: 'all 0.3s' }}
                />
                
                {/* Inner dot */}
                <rect
                  x="-2.5" y="-2.5" width="5" height="5" rx="1"
                  fill={!isConnected ? 'currentColor' : (isCollected ? collectColor : (isHovered ? glow : 'currentColor'))}
                  className={!isConnected 
                    ? "text-neutral-200 dark:text-neutral-800 opacity-20" 
                    : (isCollected || isHovered ? "" : "text-neutral-500 dark:text-neutral-400")}
                  style={{ transition: 'all 0.3s' }}
                />

                {/* Label - beautifully high-contrast in light & dark mode */}
                <text
                  x="9" y="3"
                  fontSize="7"
                  fontFamily="monospace"
                  fontWeight="700"
                  fill="currentColor"
                  className={!isConnected 
                    ? "text-neutral-300 dark:text-neutral-700 opacity-35 select-none" 
                    : "text-neutral-500 dark:text-neutral-400 select-none"}
                >
                  {node.label}
                </text>

                {/* Hover tooltip */}
                {isHovered && isConnected && (
                  <g>
                    <rect x="-60" y="-38" width="120" height="26" rx="4"
                      fill="var(--popover)" stroke="var(--border)" strokeWidth="0.5" opacity="0.96" />
                    <text x="0" y="-25" fontSize="6.5" fontFamily="monospace" fontWeight="700"
                      fill={glow} textAnchor="middle">{node.label} MODULE</text>
                    <text x="0" y="-15" fontSize="5.5" fontFamily="monospace"
                      fill="var(--muted-foreground)" textAnchor="middle">{node.desc}</text>
                  </g>
                )}
              </g>
            );
          })}

          {/* ── Render 3 random packets elements without the square drop-shadow shade filter ── */}
          {Array.from({ length: 3 }).map((_, pIdx) => (
            <g key={pIdx}>
              {/* Trail dots for packet */}
              {Array.from({ length: 5 }).map((_, tIdx) => (
                <rect
                  key={tIdx}
                  id={`ds-packet-${pIdx}-trail-${tIdx}`}
                  width="4" height="4"
                  rx="1"
                  fill={glow}
                  opacity={0.65 - tIdx * 0.13}
                  style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
                />
              ))}
              {/* Head packet */}
              <rect
                id={`ds-packet-${pIdx}-head`}
                width="6.5" height="6.5"
                rx="1.5"
                fill={glow}
              />
            </g>
          ))}
        </svg>
      </div>

      {/* Sync Complete Overlay */}
      <AnimatePresence>
        {showSyncMessage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-background/85 backdrop-blur-sm flex flex-col justify-center items-center font-mono z-20"
          >
            <motion.div
              initial={{ scale: 0.94, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.94, opacity: 0 }}
              className="text-center p-6 rounded-xl bg-card max-w-sm"
              style={{ border: `1px solid ${glow}55`, boxShadow: glowCSS }}
            >
              <div className="inline-block relative">
                <span className="absolute -inset-1 rounded blur animate-pulse" style={{ backgroundColor: `${glow}33` }} />
                <h3 className="relative font-pixel text-xs tracking-widest uppercase" style={{ color: glow }}>
                  BUILD COMPLETE
                </h3>
              </div>
              <p className="text-[8px] text-muted-foreground mt-3 tracking-widest uppercase leading-relaxed">
                SYSTEM KNOWLEDGE SYNCHRONIZED
              </p>
              <div className="mt-4 flex gap-1 justify-center">
                {Array.from({ length: 16 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-1 w-1 rounded-sm animate-pulse"
                    style={{ backgroundColor: glow, animationDelay: `${i * 80}ms` }}
                  />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

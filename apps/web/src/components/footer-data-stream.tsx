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
}

// ViewBox dimensions — we use a fixed logical canvas that scales
const VW = 1200;
const VH = 140;

const NODES: DataNode[] = [
  { id: 'api',       label: 'API',       xPct: 10,   yPct: 22,  desc: 'REST & gRPC Integration Endpoints' },
  { id: 'llm',       label: 'LLM',       xPct: 20,   yPct: 22,  desc: 'Large Language Model Router & Cost Optimization' },
  { id: 'rag',       label: 'RAG',       xPct: 28.3, yPct: 39,  desc: 'Retrieval-Augmented Generation context pipeline' },
  { id: 'json',      label: 'JSON',      xPct: 36.7, yPct: 57,  desc: 'Structured schema serialization layers' },
  { id: 'sql',       label: 'SQL',       xPct: 45.8, yPct: 57,  desc: 'Relational transaction databases & query planners' },
  { id: 'cache',     label: 'CACHE',     xPct: 53.3, yPct: 39,  desc: 'Redis cache synchronization layer' },
  { id: 'gpu',       label: 'GPU',       xPct: 61.7, yPct: 22,  desc: 'Hardware inference acceleration cluster' },
  { id: 'cpu',       label: 'CPU',       xPct: 71.7, yPct: 22,  desc: 'Task orchestrator & CPU scheduling grid' },
  { id: 'tools',     label: 'TOOLS',     xPct: 80,   yPct: 39,  desc: 'Dynamic agentic tools execution framework' },
  { id: 'voice',     label: 'VOICE',     xPct: 88.3, yPct: 57,  desc: 'Low-latency Realtime multilingual voice pipelines' },
  { id: 'mcp',       label: 'MCP',       xPct: 94.2, yPct: 39,  desc: 'Model Context Protocol server integrations' },
  { id: 'node',      label: 'NODE',      xPct: 84.2, yPct: 75,  desc: 'Distributed microservice runtime nodes' },
  { id: 'token',     label: 'TOKEN',     xPct: 74.2, yPct: 75,  desc: 'Context token streaming & rate limiting' },
  { id: 'vector',    label: 'VECTOR',    xPct: 60,   yPct: 75,  desc: 'Vector database similarity indexing' },
  { id: 'memory',    label: 'MEMORY',    xPct: 41.7, yPct: 75,  desc: 'Persistent chat state & episodic memory structures' },
  { id: 'embedding', label: 'EMBEDDING', xPct: 16.7, yPct: 75,  desc: 'High-dimensional text representation model' },
];

// Convert percentage nodes to absolute SVG coordinates
function nodeToXY(n: DataNode) {
  return { x: (n.xPct / 100) * VW, y: (n.yPct / 100) * VH };
}

// Build a smooth path through all nodes in order (top row L→R, then bottom row R→L looping back)
function buildCircuitPath(): string {
  const topRow  = [NODES[0], NODES[1], NODES[2], NODES[3], NODES[4], NODES[5], NODES[6], NODES[7], NODES[8], NODES[9], NODES[10]];
  const botRow  = [NODES[11], NODES[12], NODES[13], NODES[14], NODES[15]];

  const pts = [
    ...topRow.map(nodeToXY),
    ...botRow.map(nodeToXY).reverse(),
  ];

  // Smooth polyline using simple quadratic bezier at each corner
  let d = `M ${pts[0].x},${pts[0].y}`;
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1];
    const curr = pts[i];
    const mx = (prev.x + curr.x) / 2;
    const my = (prev.y + curr.y) / 2;
    d += ` Q ${prev.x},${prev.y} ${mx},${my}`;
  }
  // close back to start smoothly
  d += ` Q ${pts[pts.length - 1].x},${pts[pts.length - 1].y} ${pts[0].x},${pts[0].y} Z`;
  return d;
}

const CIRCUIT_PATH = buildCircuitPath();

const STATUS_LABELS = [
  'SYSTEM ONLINE', 'MEMORY ACTIVE', 'TOOLS READY', 'VOICE READY',
  'RAG INDEXED', 'MODELS LOADED', 'PIPELINES NOMINAL', 'VECTOR CACHE SYNCD'
];

// ─── Component ────────────────────────────────────────────────────────────────
export function FooterDataStream() {
  const containerRef = useRef<HTMLDivElement>(null);
  const pathRef      = useRef<SVGPathElement>(null);

  const [collected,       setCollected]       = useState<Record<string, boolean>>({});
  const [activeNode,      setActiveNode]       = useState<DataNode | null>(null);
  const [pulseNode,       setPulseNode]        = useState<string | null>(null);
  const [statusText,      setStatusText]       = useState('SYSTEM ONLINE');
  const [showSyncMessage, setShowSyncMessage]  = useState(false);
  const [trailLength,     setTrailLength]      = useState(6);
  const [inViewport,      setInViewport]       = useState(false);

  // heroColor: read from CSS variable and subscribe to changes
  const [heroColor, setHeroColor] = useState('hsl(221.2 83.2% 53.3%)');

  // Track viewport size so we can scale SVG coordinates → DOM
  const [svgRect,  setSvgRect]  = useState({ width: 1, height: 1 });
  const svgRef = useRef<SVGSVGElement>(null);

  // Watch for hero color CSS variable changes via a small polling effect
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

  // Track SVG bounding rect for hit testing (node collision in DOM space)
  useEffect(() => {
    const update = () => {
      if (svgRef.current) {
        const r = svgRef.current.getBoundingClientRect();
        setSvgRect({ width: r.width, height: r.height });
      }
    };
    update();
    window.addEventListener('resize', update);
    return () => window.removeEventListener('resize', update);
  }, []);

  // Intersection observer
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => setInViewport(e.isIntersecting), { threshold: 0.1 });
    if (containerRef.current) obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  // Packet state refs (for 60fps without react re-renders)
  const progressRef   = useRef(0);
  const trailRef      = useRef<{ x: number; y: number }[]>([]);
  const animationRef  = useRef<number | null>(null);
  const trailLenRef   = useRef(trailLength);
  trailLenRef.current = trailLength;

  // Animation loop
  useEffect(() => {
    if (!inViewport) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      return;
    }
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const path = pathRef.current;
    if (!path) return;

    const totalLength = path.getTotalLength();
    const speed = 2.2;

    const animate = () => {
      progressRef.current = (progressRef.current + speed) % totalLength;
      const head = path.getPointAtLength(progressRef.current);

      // Update trail array
      trailRef.current.push({ x: head.x, y: head.y });
      if (trailRef.current.length > trailLenRef.current) trailRef.current.shift();

      // Move DOM elements directly — no react state = zero jank
      const headEl = document.getElementById('ds-packet-head');
      if (headEl) {
        headEl.style.transform = `translate(${head.x}px, ${head.y}px)`;
      }

      const trailEls = document.querySelectorAll<HTMLElement>('.ds-trail-dot');
      trailEls.forEach((el, i) => {
        const idx = Math.max(0, trailRef.current.length - 1 - i);
        const pt = trailRef.current[idx];
        if (pt) el.style.transform = `translate(${pt.x}px, ${pt.y}px)`;
      });

      // Node collision check (in SVG coordinate space)
      NODES.forEach(node => {
        const { x, y } = nodeToXY(node);
        const dx = head.x - x;
        const dy = head.y - y;
        if (dx * dx + dy * dy < 196 && !collected[node.id]) {
          setCollected(prev => {
            const next = { ...prev, [node.id]: true };
            if (NODES.every(n => next[n.id])) {
              setShowSyncMessage(true);
              setStatusText('COMPILING KNOWLEDGE...');
              setTimeout(() => {
                setShowSyncMessage(false);
                setCollected({});
                setTrailLength(6);
                setStatusText('SYSTEM ONLINE');
              }, 3000);
            }
            return next;
          });
          setPulseNode(node.id);
          setTimeout(() => setPulseNode(null), 400);
          setTrailLength(prev => Math.min(prev + 1, 30));
          setStatusText(STATUS_LABELS[Math.floor(Math.random() * STATUS_LABELS.length)]);
        }
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);
    return () => { if (animationRef.current) cancelAnimationFrame(animationRef.current); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [inViewport]);

  // glow colour derived from hero portrait
  const glow    = heroColor || 'hsl(221.2 83.2% 53.3%)';
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
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{ background: `radial-gradient(ellipse 60% 60% at 50% 50%, ${glow}33, transparent)` }}
      />

      {/* Status bar */}
      <div className="flex items-center justify-between px-6 pb-4 border-b border-border/20 font-mono text-[9px] text-muted-foreground/80">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full animate-pulse" style={{ backgroundColor: glow }} />
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
          {/* Base dashed track */}
          <path
            ref={pathRef}
            d={CIRCUIT_PATH}
            fill="none"
            stroke="currentColor"
            className="text-border/30 dark:text-border/15"
            strokeWidth="1.2"
            strokeDasharray="5 5"
          />

          {/* Glowing colour-synced underlay */}
          <path
            d={CIRCUIT_PATH}
            fill="none"
            stroke={glow}
            strokeWidth="3"
            opacity="0.12"
          />

          {/* Node hit areas + anchors (rendered in SVG for perfect scaling) */}
          {NODES.map(node => {
            const { x, y } = nodeToXY(node);
            const isCollected = collected[node.id];
            const isPulsing   = pulseNode === node.id;
            const isHovered   = activeNode?.id === node.id;
            return (
              <g
                key={node.id}
                transform={`translate(${x},${y})`}
                onMouseEnter={() => setActiveNode(node)}
                onMouseLeave={() => setActiveNode(null)}
                className="cursor-pointer"
              >
                {/* Outer pulse ring on collect */}
                {isPulsing && (
                  <circle r="12" fill="none" stroke={glow} strokeWidth="1" opacity="0.6">
                    <animate attributeName="r" from="6" to="20" dur="0.4s" fill="freeze" />
                    <animate attributeName="opacity" from="0.8" to="0" dur="0.4s" fill="freeze" />
                  </circle>
                )}

                {/* Anchor square */}
                <rect
                  x="-5" y="-5" width="10" height="10" rx="2"
                  fill={isCollected ? `${glow}33` : 'var(--card)'}
                  stroke={isCollected || isHovered ? glow : 'var(--border)'}
                  strokeWidth="0.8"
                  style={{ filter: (isCollected || isHovered) ? `drop-shadow(0 0 4px ${glow})` : 'none',
                           transition: 'all 0.3s' }}
                />
                <rect
                  x="-2.5" y="-2.5" width="5" height="5" rx="1"
                  fill={isCollected ? glow : '#888888'}
                  opacity={isCollected ? 1 : 0.5}
                />

                {/* Label */}
                <text
                  x="9" y="4"
                  fontSize="7"
                  fontFamily="monospace"
                  fontWeight="700"
                  fill={isCollected || isHovered ? glow : 'currentColor'}
                  style={{ transition: 'fill 0.3s' }}
                  className="select-none"
                >
                  {node.label}
                </text>

                {/* Hover tooltip */}
                {isHovered && (
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

          {/* ── Packet trail (SVG foreignObject for glow effect) ── */}
          {/* Trail dots */}
          {Array.from({ length: 30 }).map((_, i) => (
            <rect
              key={i}
              className="ds-trail-dot"
              width="4" height="4" rx="1"
              fill={glow}
              opacity={Math.max(0.04, 0.65 - i * 0.05)}
              style={{ transform: 'translate(0px,0px)', transformBox: 'fill-box', transformOrigin: 'center',
                       transition: 'opacity 0.1s' }}
            />
          ))}

          {/* Head packet */}
          <rect
            id="ds-packet-head"
            width="7" height="7" rx="1.5"
            fill={glow}
            style={{
              filter: `drop-shadow(0 0 5px ${glow}) drop-shadow(0 0 10px ${glow})`,
              transform: 'translate(0px,0px)',
            }}
          />
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

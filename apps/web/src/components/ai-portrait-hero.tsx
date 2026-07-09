'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Github, Twitter, Linkedin, Mail } from 'lucide-react';
import { useTheme } from 'next-themes';
import { cn } from '@/lib/utils';

// Types
interface Particle {
  x: number;
  y: number;
  ox: number;
  oy: number;
  color: { r: number; g: number; b: number };
  targetColor: { r: number; g: number; b: number };
  colorTransition: number;
  vx: number;
  vy: number;
  size: number;
  originalSize: number;
  alpha: number;
  originalAlpha: number;
  angle: number;
  spin: number;
  active: boolean;
  detached?: boolean;
  detachTimer?: number;
}

interface BGParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  alpha: number;
  color: string;
}

interface Ember {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  originalSize: number;
  alpha: number;
  color: { r: number; g: number; b: number };
  life: number;
  maxLife: number;
  swaySpeed: number;
  swayOffset: number;
}

export function AIPortraitHero() {
  const { resolvedTheme } = useTheme();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const rightContainerRef = useRef<HTMLDivElement>(null);
  
  const [portraits, setPortraits] = useState<string[]>([]);
  const [activePortrait, setActivePortrait] = useState<string>('/assets/images/portrait-1.webp');
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  
  const mouseRef = useRef({ x: -1000, y: -1000, rx: 0, ry: 0, targetRx: 0, targetRy: 0, inside: false });
  const particlesRef = useRef<Particle[]>([]);
  const bgParticlesRef = useRef<BGParticle[]>([]);
  const embersRef = useRef<Ember[]>([]);
  const layoutRef = useRef({ xOffset: 0, yOffset: 0, targetWidth: 0, targetHeight: 0 });
  const scanRef = useRef({ active: false, y: 0, progress: 0, timer: 0 });
  const morphProgressRef = useRef(1.0);
  const pixelateProgressRef = useRef(0);
  const nextImageLoadedRef = useRef<HTMLImageElement | null>(null);
  
  // Parallax rotation states for heading and elements
  const [parallax, setParallax] = useState({ x: 0, y: 0 });


  // Fetch portraits dynamic list on mount
  useEffect(() => {
    async function loadPortraits() {
      try {
        const res = await fetch('/api/portraits');
        const data = await res.json();
        if (data.portraits && data.portraits.length > 0) {
          setPortraits(data.portraits);
          // Set initial random portrait
          const randomIdx = Math.floor(Math.random() * data.portraits.length);
          setActivePortrait(data.portraits[randomIdx]);
        }
      } catch (err) {
        console.error('Failed to load portraits:', err);
      }
    }
    loadPortraits();
  }, []);

  // Cycle/morph active portraits dynamically
  useEffect(() => {
    if (portraits.length <= 1) return;
    const interval = setInterval(() => {
      setActivePortrait((current) => {
        const remaining = portraits.filter(p => p !== current);
        if (remaining.length === 0) return current;
        const randomIdx = Math.floor(Math.random() * remaining.length);
        return remaining[randomIdx];
      });
    }, 12000); // 12 seconds morph loop
    return () => clearInterval(interval);
  }, [portraits]);



  // 3. Main interactive canvas rendering loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    let animationFrameId: number;
    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
    const container = containerRef.current;
    let width = container ? container.clientWidth : window.innerWidth;
    let height = container ? container.clientHeight : window.innerHeight;
    
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);
    
    // Set offscreen canvas for downsampling
    const offscreenCanvas = document.createElement('canvas');
    const offscreenCtx = offscreenCanvas.getContext('2d');
    
    let activeImage: HTMLImageElement | null = null;
    
    // Initialize background floating particles
    const initBGParticles = () => {
      const pCount = window.innerWidth < 768 ? 35 : 90;
      const bgParticles: BGParticle[] = [];
      const colors = ['#3B82F6', '#06B6D4', '#7C3AED', '#8B5CF6', '#FFFFFF'];
      for (let i = 0; i < pCount; i++) {
        bgParticles.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.35,
          vy: (Math.random() - 0.5) * 0.35,
          size: Math.random() * 2 + 0.8,
          alpha: Math.random() * 0.4 + 0.1,
          color: colors[Math.floor(Math.random() * colors.length)]
        });
      }
      bgParticlesRef.current = bgParticles;
    };
    initBGParticles();

    // Resize handler
    const handleResize = () => {
      const container = containerRef.current;
      width = container ? container.clientWidth : window.innerWidth;
      height = container ? container.clientHeight : window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      ctx.scale(dpr, dpr);
      initBGParticles();
      if (activeImage) {
        processImage(activeImage);
      }
    };
    window.addEventListener('resize', handleResize);

    // Process active image and initialize/morph face particles centered inside the right column
    const processImage = (img: HTMLImageElement) => {
      if (!offscreenCtx) return;
      
      const targetAspect = 0.9;
      let rect = { left: width * 0.58, top: height * 0.2, width: width * 0.38, height: height * 0.6 };
      
      const el = rightContainerRef.current;
      if (el) {
        const r = el.getBoundingClientRect();
        rect = { left: r.left, top: r.top, width: r.width, height: r.height };
      }
      
      // Scale portrait to match responsive screen dimensions
      const isMobile = typeof window !== 'undefined' && window.innerWidth < 1024;
      let targetHeight = rect.height * (isMobile ? 0.92 : 0.70);
      let targetWidth = targetHeight * targetAspect;
      
      // Prevent horizontal overflow
      const maxPct = isMobile ? 0.92 : 0.85;
      if (targetWidth > rect.width * maxPct) {
        targetWidth = rect.width * maxPct;
        targetHeight = targetWidth / targetAspect;
      }
      
      // Portrait center of gravity
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height * (isMobile ? 0.50 : 0.42); // Centered vertically on mobile, slightly elevated on desktop for flows
      
      let xOffset = cx - targetWidth / 2;
      let yOffset = cy - targetHeight / 2;
      
      layoutRef.current = { xOffset, yOffset, targetWidth, targetHeight };
      
      offscreenCanvas.width = 95; // Crisp high-density background grid
      offscreenCanvas.height = Math.round(95 / targetAspect);
      
      offscreenCtx.clearRect(0, 0, offscreenCanvas.width, offscreenCanvas.height);
      offscreenCtx.drawImage(img, 0, 0, offscreenCanvas.width, offscreenCanvas.height);
      
      const imgData = offscreenCtx.getImageData(0, 0, offscreenCanvas.width, offscreenCanvas.height);
      const data = imgData.data;
      
      const newParticles: Particle[] = [];
      const cellWidth = targetWidth / offscreenCanvas.width;
      const cellHeight = targetHeight / offscreenCanvas.height;
      
      // Center-relative starting coordinates
      const gridStartX = -targetWidth / 2;
      const gridStartY = -targetHeight / 2;
      
      for (let y = 0; y < offscreenCanvas.height; y++) {
        for (let x = 0; x < offscreenCanvas.width; x++) {
          const idx = (y * offscreenCanvas.width + x) * 4;
          const r = data[idx];
          const g = data[idx+1];
          const b = data[idx+2];
          const a = data[idx+3];
          
          // Omit transparent background noise entirely
          if (a > 200) {
            let pSize = Math.random() * 1.5 + 2.5;
            let pAlpha = Math.random() * 0.35 + 0.65;
            
            // Soft chest fade-out at bottom
            const fadeZoneHeight = Math.round(offscreenCanvas.height * 0.12);
            const startFadeY = offscreenCanvas.height - fadeZoneHeight;
            if (y > startFadeY) {
              const fraction = Math.min(1.0, Math.max(0.0, (y - startFadeY) / fadeZoneHeight));
              const fade = 1.0 - fraction;
              pAlpha *= fade;
              pSize *= (0.75 + fade * 0.25);
            }
            
            // Store ox and oy as relative offsets from portrait center (cx, cy)
            const prx = x * cellWidth + gridStartX;
            const pry = y * cellHeight + gridStartY;
            
            newParticles.push({
              x: cx + prx,
              y: cy + pry,
              ox: prx, // relative offset
              oy: pry, // relative offset
              color: { r, g, b },
              targetColor: { r, g, b },
              colorTransition: 1.0,
              vx: 0,
              vy: 0,
              size: pSize,
              originalSize: pSize,
              alpha: pAlpha,
              originalAlpha: pAlpha,
              angle: Math.random() * Math.PI * 2,
              spin: (Math.random() - 0.5) * 0.05,
              active: true,
              detached: false,
              detachTimer: 0
            });
          }
        }
      }

      if (particlesRef.current.length > 0) {
        const oldP = particlesRef.current;
        const count = Math.min(oldP.length, newParticles.length);
        for (let i = 0; i < count; i++) {
          oldP[i].ox = newParticles[i].ox; // Store new relative offset
          oldP[i].oy = newParticles[i].oy; // Store new relative offset
          oldP[i].targetColor = newParticles[i].color;
          oldP[i].originalAlpha = newParticles[i].originalAlpha;
          oldP[i].originalSize = newParticles[i].originalSize;
          oldP[i].colorTransition = 0;
          // Set velocity offsets to zero to prevent scatter/flying effects during pixelated morphs
          oldP[i].vx = 0;
          oldP[i].vy = 0;
        }
        if (newParticles.length > oldP.length) {
          particlesRef.current = [...oldP, ...newParticles.slice(oldP.length)];
        } else if (newParticles.length < oldP.length) {
          particlesRef.current = oldP.slice(0, newParticles.length);
        }
        morphProgressRef.current = 0;
      } else {
        particlesRef.current = newParticles;
      }
    };

    if (activePortrait) {
      activeImage = new Image();
      activeImage.src = activePortrait;
      activeImage.onload = () => {
        if (particlesRef.current.length > 0) {
          // Trigger the high-fidelity pixelation transition
          nextImageLoadedRef.current = activeImage;
          pixelateProgressRef.current = 0.01;
        } else {
          // First load: process immediately without transition
          processImage(activeImage!);
        }
      };
    }

    // Unified pointer tracking for mouse, touch, and pen events
    const handlePointerMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      mouseRef.current.x = mx;
      mouseRef.current.y = my;
      mouseRef.current.inside = true;

      const rx = (mx - width / 2) / (width / 2);
      const ry = (my - height / 2) / (height / 2);
      mouseRef.current.targetRx = rx * 6;
      mouseRef.current.targetRy = ry * -8;
    };

    const handlePointerLeave = () => {
      mouseRef.current.inside = false;
      mouseRef.current.targetRx = 0;
      mouseRef.current.targetRy = 0;
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerdown', handlePointerMove);
    window.addEventListener('pointerup', handlePointerLeave);
    window.addEventListener('pointercancel', handlePointerLeave);
    window.addEventListener('pointerleave', handlePointerLeave);

    let scanInterval = setInterval(() => {
      if (!scanRef.current.active) {
        scanRef.current.active = true;
        scanRef.current.progress = 0;
        scanRef.current.y = 0;
      }
    }, 20000); // Sweep scanner laser every 20 seconds

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Update pixelate transition progress
      let pixelateFactor = 0;
      if (pixelateProgressRef.current > 0) {
        const prevProgress = pixelateProgressRef.current;
        pixelateProgressRef.current += 0.035; // Speed of transition
        
        // Swap image content at the middle of the transition (0.50)
        if (prevProgress < 0.50 && pixelateProgressRef.current >= 0.50 && nextImageLoadedRef.current) {
          processImage(nextImageLoadedRef.current);
          nextImageLoadedRef.current = null;
        }
        
        if (pixelateProgressRef.current >= 1.0) {
          pixelateProgressRef.current = 0;
        } else {
          // Calculate sine wave pixelation scale (peaks at 1.0 at progress=0.5)
          pixelateFactor = Math.sin(pixelateProgressRef.current * Math.PI);
        }
      }

      // Calculate dynamic center of gravity relative to the canvas local coordinates
      const canvasBounds = canvasRef.current?.getBoundingClientRect();
      const canvasTop = canvasBounds ? canvasBounds.top : 0;
      const canvasLeft = canvasBounds ? canvasBounds.left : 0;

      const isMobileViewport = typeof window !== 'undefined' && window.innerWidth < 1024;
      const rBounds = rightContainerRef.current?.getBoundingClientRect();
      const cx = rBounds ? (rBounds.left - canvasLeft + rBounds.width / 2) : (width * 0.58);
      const cy = rBounds ? (rBounds.top - canvasTop + rBounds.height * (isMobileViewport ? 0.50 : 0.42)) : (height * 0.45);
      
      if (layoutRef.current.targetWidth > 0) {
        layoutRef.current.xOffset = cx - layoutRef.current.targetWidth / 2;
        layoutRef.current.yOffset = cy - layoutRef.current.targetHeight / 2;
      }

      // Parallax update
      mouseRef.current.rx += (mouseRef.current.targetRx - mouseRef.current.rx) * 0.08;
      mouseRef.current.ry += (mouseRef.current.targetRy - mouseRef.current.ry) * 0.08;
      
      setParallax({
        x: mouseRef.current.rx * 2.2,
        y: mouseRef.current.ry * 2.2
      });

      const isDark = resolvedTheme === 'dark';
      const time = Date.now() * 0.0006;
      
      // Ambient Gradient
      const gX = width * 0.5 + Math.sin(time * 0.8) * width * 0.2;
      const gY = height * 0.5 + Math.cos(time * 0.5) * height * 0.2;
      const glowRad = Math.min(width, height) * 0.8;
      
      const bgHue = (Date.now() * 0.012) % 360;
      const ambientGlow = ctx.createRadialGradient(gX, gY, 10, gX, gY, glowRad);
      if (isDark) {
        ambientGlow.addColorStop(0, `hsla(${bgHue}, 70%, 50%, 0.05)`);
        ambientGlow.addColorStop(0.35, `hsla(${(bgHue + 120) % 360}, 65%, 50%, 0.02)`);
        ambientGlow.addColorStop(1, 'rgba(3, 4, 8, 1)'); // Deep black/graphite core
      } else {
        ambientGlow.addColorStop(0, `hsla(${bgHue}, 70%, 50%, 0.03)`);
        ambientGlow.addColorStop(0.5, `hsla(${(bgHue + 180) % 360}, 60%, 50%, 0.015)`);
        ambientGlow.addColorStop(1, 'rgba(255, 255, 255, 1)');
      }
      ctx.fillStyle = ambientGlow;
      ctx.fillRect(0, 0, width, height);

      // Background grid
      ctx.strokeStyle = isDark ? 'rgba(255, 255, 255, 0.015)' : 'rgba(0, 0, 0, 0.02)';
      ctx.lineWidth = 1;
      const gridSize = 45;
      const gridParallaxX = mouseRef.current.rx * 12;
      const gridParallaxY = mouseRef.current.ry * 12;
      
      ctx.save();
      ctx.translate(gridParallaxX, gridParallaxY);
      ctx.beginPath();
      for (let x = 0; x < width; x += gridSize) {
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
      }
      for (let y = 0; y < height; y += gridSize) {
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
      }
      ctx.stroke();
      ctx.restore();

      // Render Floating Background Particles
      bgParticlesRef.current.forEach((bp) => {
        bp.x += bp.vx;
        bp.y += bp.vy;
        if (bp.x < 0) bp.x = width;
        if (bp.x > width) bp.x = 0;
        if (bp.y < 0) bp.y = height;
        if (bp.y > height) bp.y = 0;
        
        if (mouseRef.current.inside) {
          const dx = bp.x - mouseRef.current.x;
          const dy = bp.y - mouseRef.current.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            const force = (150 - dist) / 150;
            bp.x += (dx / dist) * force * 1.5;
            bp.y += (dy / dist) * force * 1.5;
          }
        }
        
        ctx.fillStyle = bp.color;
        ctx.globalAlpha = bp.alpha;
        ctx.beginPath();
        ctx.arc(bp.x, bp.y, bp.size, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1.0;

      // Update scan line
      if (scanRef.current.active) {
        scanRef.current.progress += 0.012;
        scanRef.current.y = scanRef.current.progress * height;
        if (scanRef.current.progress >= 1.0) {
          scanRef.current.active = false;
        }
      }

      if (morphProgressRef.current < 1.0) {
        morphProgressRef.current += 0.03;
      }

      // Render portrait particles
      const particles = particlesRef.current;
      const isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      
      const mouseX = mouseRef.current.x;
      const mouseY = mouseRef.current.y;
      const breathScale = 1.0 + Math.sin(time * 1.5) * 0.01;
      const breathRotate = Math.sin(time * 0.5) * 0.004;

      ctx.save();
      ctx.globalCompositeOperation = resolvedTheme === 'light' ? 'source-over' : 'screen';

      if (!isReducedMotion && Math.random() < 0.28 && particles.length > 0) {
        const detachCount = Math.floor(Math.random() * 2) + 1;
        for (let k = 0; k < detachCount; k++) {
          const randIdx = Math.floor(Math.random() * particles.length);
          const p = particles[randIdx];
          if (p && !p.detached) {
            let canDetach = true;
            if (layoutRef.current.targetHeight > 0) {
              const baseOy = cy + p.oy;
              const bottomY = cy + layoutRef.current.targetHeight / 2;
              const distToBottom = bottomY - baseOy;
              const stability = Math.max(0.0, Math.min(1.0, distToBottom / (layoutRef.current.targetHeight * 0.40)));
              if (stability < 0.15 || Math.random() > stability) {
                canDetach = false;
              }
            }
            if (canDetach) {
              p.detached = true;
              p.detachTimer = 100 + Math.random() * 110;
            }
          }
        }
      }

      particles.forEach((p) => {
        if (p.colorTransition < 1.0) {
          p.colorTransition += 0.03;
          p.color.r += (p.targetColor.r - p.color.r) * p.colorTransition;
          p.color.g += (p.targetColor.g - p.color.g) * p.colorTransition;
          p.color.b += (p.targetColor.b - p.color.b) * p.colorTransition;
        }
        
        const baseOx = cx + p.ox;
        const baseOy = cy + p.oy;
        
        let stabilityFactor = 1.0;
        if (layoutRef.current.targetHeight > 0) {
          const bottomY = cy + layoutRef.current.targetHeight / 2;
          const distToBottom = bottomY - baseOy;
          stabilityFactor = Math.max(0.0, Math.min(1.0, distToBottom / (layoutRef.current.targetHeight * 0.40)));
          stabilityFactor = Math.pow(stabilityFactor, 2);
        }
        
        let targetX = baseOx;
        let targetY = baseOy;
        
        if (!isReducedMotion) {
          const dx = baseOx - cx;
          const dy = baseOy - cy;
          const rx = dx * Math.cos(breathRotate) - dy * Math.sin(breathRotate);
          const ry = dx * Math.sin(breathRotate) + dy * Math.cos(breathRotate);
          
          const breatheTargetX = rx * breathScale + cx;
          const breatheTargetY = ry * breathScale + cy;
          const parallaxOffsetX = mouseRef.current.rx * 8;
          const parallaxOffsetY = mouseRef.current.ry * 8;
          
          targetX = baseOx + (breatheTargetX - baseOx + parallaxOffsetX) * stabilityFactor;
          targetY = baseOy + (breatheTargetY - baseOy + parallaxOffsetY) * stabilityFactor;
        }

        if (mouseRef.current.inside && !isReducedMotion) {
          const dx = p.x - mouseX;
          const dy = p.y - mouseY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 26) {
            const repelForce = (26 - dist) / 26;
            p.vx += (dx / dist) * repelForce * 2.8 * stabilityFactor;
            p.vy += (dy / dist) * repelForce * 2.8 * stabilityFactor;
            p.angle += p.spin * repelForce * 1.5 * stabilityFactor;
            p.size = p.originalSize * (1.0 + repelForce * 0.25 * stabilityFactor);
          }
        }

        if (scanRef.current.active && !isReducedMotion) {
          const scanDist = Math.abs(p.y - scanRef.current.y);
          if (scanDist < 60) {
            const waveForce = (60 - scanDist) / 60;
            p.vx += (Math.random() - 0.5) * waveForce * 16 * stabilityFactor;
            p.vy += (Math.random() - 0.5) * waveForce * 4 * stabilityFactor;
            p.alpha = Math.max(0.2, p.alpha - waveForce * 0.4 * stabilityFactor);
          }
        }

        if (p.detached) {
          p.detachTimer!--;
          if (p.detachTimer! <= 0) p.detached = false;
          p.vx += (Math.random() - 0.5) * 0.28;
          p.vy += (Math.random() - 0.5) * 0.16 - 0.08;
          p.vx *= 0.94;
          p.vy *= 0.94;
          p.x += p.vx;
          p.y += p.vy;
          p.size += (p.originalSize * 1.4 - p.size) * 0.06;
          p.alpha += (1.0 - p.alpha) * 0.1;
        } else {
          if (isReducedMotion) {
            p.x = targetX;
            p.y = targetY;
            p.vx = 0;
            p.vy = 0;
          } else {
            const springF = 0.08;
            const friction = 0.82;
            p.vx = (p.vx + (targetX - p.x) * springF) * friction;
            p.vy = (p.vy + (targetY - p.y) * springF) * friction;
            p.x += p.vx;
            p.y += p.vy;
            p.size += (p.originalSize - p.size) * 0.08;
            p.alpha += (p.originalAlpha - p.alpha) * 0.08;
          }
        }

        const cr = Math.round(p.color.r);
        const cg = Math.round(p.color.g);
        const cb = Math.round(p.color.b);
        
        let px = p.x;
        let py = p.y;
        let pSize = p.size;
        
        if (pixelateFactor > 0) {
          const gridSize = Math.round(1 + pixelateFactor * 21);
          px = Math.round(px / gridSize) * gridSize;
          py = Math.round(py / gridSize) * gridSize;
          pSize = pSize * (1.0 + pixelateFactor * 2.8);
        }

        if (resolvedTheme !== 'light') {
          ctx.fillStyle = `rgba(${cr}, ${cg}, ${cb}, ${p.alpha * 0.35})`;
          ctx.fillRect(px - pSize, py - pSize, pSize * 2, pSize * 2);
        }
        ctx.fillStyle = `rgba(${cr}, ${cg}, ${cb}, ${p.alpha})`;
        ctx.fillRect(px - pSize / 2, py - pSize / 2, pSize, pSize);
      });
      ctx.restore();

      // Spawn and Render Rising Energy Embers
      if (!isReducedMotion) {
        const layout = layoutRef.current;
        if (layout.targetWidth > 0) {
          const spawnCount = Math.random() < 0.4 ? 2 : 1;
          for (let i = 0; i < spawnCount; i++) {
            const spawnX = layout.xOffset + Math.random() * layout.targetWidth;
            const spawnY = layout.yOffset + layout.targetHeight - Math.random() * (layout.targetHeight * 0.12);
            const speed = Math.random() * 1.8 + 1.2;
            const originalSize = Math.random() * 2.5 + 2.0;
            
            const colors = [
              { r: 6, g: 182, b: 212 },
              { r: 59, g: 130, b: 246 },
              { r: 124, g: 58, b: 237 }
            ];
            const color = colors[Math.floor(Math.random() * colors.length)];
            
            embersRef.current.push({
              x: spawnX,
              y: spawnY,
              vx: (Math.random() - 0.5) * 0.5,
              vy: -speed,
              size: originalSize,
              originalSize,
              alpha: Math.random() * 0.4 + 0.6,
              color,
              life: 90 + Math.random() * 60,
              maxLife: 150,
              swaySpeed: Math.random() * 0.04 + 0.02,
              swayOffset: Math.random() * Math.PI * 2
            });
          }
        }

        ctx.save();
        ctx.globalCompositeOperation = resolvedTheme === 'light' ? 'source-over' : 'screen';
        
        embersRef.current = embersRef.current.filter((ember) => {
          ember.life--;
          if (ember.life <= 0) return false;
          ember.y += ember.vy;
          ember.x += Math.sin(time * 2 + ember.swayOffset) * 0.45 + ember.vx;
          
          const lifeRatio = ember.life / ember.maxLife;
          ember.alpha = Math.min(1.0, lifeRatio * 1.6);
          ember.size = ember.originalSize * (0.35 + lifeRatio * 0.65);
          
          const cr = ember.color.r;
          const cg = ember.color.g;
          const cb = ember.color.b;
          
          if (resolvedTheme !== 'light') {
            ctx.fillStyle = `rgba(${cr}, ${cg}, ${cb}, ${ember.alpha * 0.35})`;
            ctx.fillRect(ember.x - ember.size, ember.y - ember.size, ember.size * 2, ember.size * 2);
          }
          ctx.fillStyle = `rgba(${cr}, ${cg}, ${cb}, ${ember.alpha})`;
          ctx.fillRect(ember.x - ember.size / 2, ember.y - ember.size / 2, ember.size, ember.size);
          return true;
        });
        ctx.restore();
      }

      // Draw Laser Identity Scan wave overlay
      if (scanRef.current.active && !isReducedMotion) {
        ctx.save();
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#06B6D4';
        const scanGrad = ctx.createLinearGradient(0, scanRef.current.y - 12, 0, scanRef.current.y + 12);
        scanGrad.addColorStop(0, 'rgba(6, 182, 212, 0)');
        scanGrad.addColorStop(0.5, 'rgba(6, 182, 212, 0.7)');
        scanGrad.addColorStop(1, 'rgba(6, 182, 212, 0)');
        ctx.fillStyle = scanGrad;
        ctx.fillRect(0, scanRef.current.y - 12, width, 24);
        ctx.restore();
      }

      // Cursor Light source glow
      if (mouseRef.current.inside && !isReducedMotion) {
        ctx.save();
        ctx.globalCompositeOperation = 'screen';
        const mouseGlow = ctx.createRadialGradient(mouseX, mouseY, 0, mouseX, mouseY, 75);
        mouseGlow.addColorStop(0, 'rgba(6, 182, 212, 0.15)');
        mouseGlow.addColorStop(0.5, 'rgba(124, 58, 237, 0.04)');
        mouseGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = mouseGlow;
        ctx.beginPath();
        ctx.arc(mouseX, mouseY, 75, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Cybernetic Cursor HUD Scanning Reticle
        ctx.save();
        ctx.globalCompositeOperation = resolvedTheme === 'light' ? 'source-over' : 'screen';
        
        const hudHue = (Date.now() * 0.018) % 360; // Smooth energetic color cycle
        const rColor = resolvedTheme === 'light' ? 'rgba(59, 130, 246, 0.45)' : `hsla(${hudHue}, 100%, 65%, 0.75)`;
        const textColor = resolvedTheme === 'light' ? 'rgba(59, 130, 246, 0.75)' : `hsla(${hudHue}, 100%, 75%, 1.0)`;
        
        ctx.strokeStyle = rColor;
        ctx.lineWidth = 0.8;
        
        // Add neon HDR glow in dark mode
        if (resolvedTheme !== 'light') {
          ctx.shadowBlur = 4;
          ctx.shadowColor = rColor;
        }
        
        // 1. Draw dashed outer ring
        ctx.setLineDash([2, 3]);
        ctx.beginPath();
        ctx.arc(mouseX, mouseY, 15, 0, Math.PI * 2);
        ctx.stroke();
        
        // 2. Draw tiny central crosshair
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.moveTo(mouseX - 3, mouseY);
        ctx.lineTo(mouseX + 3, mouseY);
        ctx.moveTo(mouseX, mouseY - 3);
        ctx.lineTo(mouseX, mouseY + 3);
        ctx.stroke();
        
        // 3. Draw miniature telemetry HUD text on the right
        ctx.font = '7.5px monospace, Courier New';
        ctx.fillStyle = textColor;
        if (resolvedTheme !== 'light') {
          ctx.shadowBlur = 5;
          ctx.shadowColor = textColor;
        }
        ctx.fillText(`SYS_AGENT: ACTIVE`, mouseX + 22, mouseY - 5);
        ctx.fillText(`CORE_SYNC: 99.8%`, mouseX + 22, mouseY + 2);
        ctx.fillText(`LATENCY: 12ms`, mouseX + 22, mouseY + 9);
        
        ctx.restore();
      }

      // ======================================================================
      // DRAW NEURAL NETWORK CONNECTIVE LINES (ORBITING TECH STACK TO PORTRAIT)
      // ======================================================================
      const pxCenter = layoutRef.current.xOffset + layoutRef.current.targetWidth / 2;
      const pyCenter = layoutRef.current.yOffset + layoutRef.current.targetHeight / 2;

      if (layoutRef.current.targetWidth > 0) {
        const nodeIds = [
          'node-python', 'node-fastapi', 'node-langchain', 'node-postgresql',
          'node-claude', 'node-gemini', 'node-openai', 'node-voiceagent',
          'node-flow-mcp'
        ];

        ctx.save();
        ctx.globalCompositeOperation = resolvedTheme === 'light' ? 'source-over' : 'screen';

        nodeIds.forEach((id) => {
          const el = document.getElementById(id);
          if (!el) return;
          const rect = el.getBoundingClientRect();
          if (rect.width === 0 || rect.height === 0) return; // Skip drawing connection link if element is hidden in CSS!
          const canvasRect = canvas.getBoundingClientRect();
          
          const targetX = rect.left - canvasRect.left + rect.width / 2;
          const targetY = rect.top - canvasRect.top + rect.height / 2;

          // A. Draw solid neural connection link
          const linkHue = (Date.now() * 0.01 + (id.charCodeAt(5) * 12)) % 360; // Offset color phases per connection line for rainbow current effect!
          ctx.strokeStyle = resolvedTheme === 'light' ? 'rgba(59, 130, 246, 0.15)' : `hsla(${linkHue}, 80%, 55%, 0.22)`;
          ctx.lineWidth = 1.2;
          ctx.beginPath();
          ctx.moveTo(pxCenter, pyCenter);
          ctx.lineTo(targetX, targetY);
          ctx.stroke();

          // B. Animate traveling data particle pulse along the link
          const pulseSpeed = 0.22;
          const pulseProgress = (time * pulseSpeed + (id.charCodeAt(5) * 0.1)) % 1.0;
          const pulseX = pxCenter + (targetX - pxCenter) * pulseProgress;
          const pulseY = pyCenter + (targetY - pyCenter) * pulseProgress;

          ctx.fillStyle = resolvedTheme === 'light' ? '#3B82F6' : `hsla(${linkHue}, 95%, 60%, 0.95)`;
          if (resolvedTheme !== 'light') {
            ctx.shadowBlur = 8;
            ctx.shadowColor = `hsla(${linkHue}, 95%, 60%, 0.85)`;
          }
          ctx.beginPath();
          ctx.arc(pulseX, pulseY, 2.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        });

        // Specific Python to FastAPI interconnect link
        const pythonEl = document.getElementById('node-python');
        const fastapiEl = document.getElementById('node-fastapi');
        if (pythonEl && fastapiEl) {
          const pyRect = pythonEl.getBoundingClientRect();
          const faRect = fastapiEl.getBoundingClientRect();
          if (pyRect.width === 0 || faRect.width === 0) return; // Exit if hidden!
          const canvasRect = canvas.getBoundingClientRect();
          const pyX = pyRect.left - canvasRect.left + pyRect.width / 2;
          const pyY = pyRect.top - canvasRect.top + pyRect.height / 2;
          const faX = faRect.left - canvasRect.left + faRect.width / 2;
          const faY = faRect.top - canvasRect.top + faRect.height / 2;

          const interconnectHue = (Date.now() * 0.01 + 45) % 360;
          ctx.strokeStyle = resolvedTheme === 'light' ? 'rgba(59, 130, 246, 0.12)' : `hsla(${interconnectHue}, 80%, 55%, 0.18)`;
          ctx.lineWidth = 1.0;
          ctx.beginPath();
          ctx.moveTo(pyX, pyY);
          ctx.lineTo(faX, faY);
          ctx.stroke();
        }

        ctx.restore();
      }

      animationFrameId = requestAnimationFrame(render);
    };
    
    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerdown', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerLeave);
      window.removeEventListener('pointercancel', handlePointerLeave);
      window.removeEventListener('pointerleave', handlePointerLeave);
      clearInterval(scanInterval);
      cancelAnimationFrame(animationFrameId);
    };
  }, [activePortrait, resolvedTheme]);

  // Inline 3D parallax styles on container hover
  const transformStyle = {
    transform: `perspective(1000px) rotateX(${parallax.y}deg) rotateY(${parallax.x}deg) translate3d(0, 0, 0)`,
    transition: 'transform 0.25s cubic-bezier(0.16, 1, 0.3, 1)'
  };

  return (
    <section 
      ref={containerRef}
      className="w-screen relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] mt-[-32px] md:mt-[-48px] min-h-[100vh] py-16 lg:py-0 flex flex-col justify-center overflow-hidden bg-background select-none border-b border-border/20 z-30"
    >
      {/* Background Interactive canvas */}
      <canvas 
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />

      {/* Readable gradient overlays to blend full-screen backdrop and guarantee high contrast */}
      <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent pointer-events-none z-12 md:w-[70vw] w-full" />
      <div className="absolute inset-0 bg-gradient-to-t from-background/50 via-transparent to-transparent pointer-events-none z-12" />

      {/* Volumetric ambient depth overlay */}
      <div className="absolute inset-0 bg-radial-gradient pointer-events-none z-13" />

      {/* Main Fullscreen Parallax Content Layout */}
      <div 
        style={transformStyle}
        className="container max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-full flex items-center relative z-20"
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center w-full">
          {/* Text block (Left side on large viewport) */}
          <div className="lg:col-span-5 flex flex-col items-start gap-6 text-left max-w-xl">
            
            <div className="font-pixel text-[10px] tracking-[0.25em] text-primary uppercase bg-primary/5 border border-primary/15 px-3 py-1 rounded-full select-none">
              {"// AI ENGINEERING LAB"}
            </div>

            <h1 className="font-pixel text-4xl sm:text-5xl lg:text-6xl leading-[1.1] tracking-wide text-foreground uppercase select-text">
              Building AI Solutions<br />
              That Actually Work.
            </h1>

            {/* Premium capability subheadline listing */}
            <div className="font-mono text-xs sm:text-sm text-muted-foreground/80 flex flex-wrap items-center gap-x-3 gap-y-1.5 select-none py-1">
              <div className="flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-primary" />
                <span>AI Agents</span>
              </div>
              <span className="text-border/60">|</span>
              <div className="flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-primary" />
                <span>Voice AI</span>
              </div>
              <span className="text-border/60">|</span>
              <div className="flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-primary" />
                <span>Business Automation</span>
              </div>
              <span className="text-border/60">|</span>
              <div className="flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-primary" />
                <span>Intelligent Systems</span>
              </div>
            </div>

            <p className="text-sm sm:text-base text-muted-foreground leading-relaxed select-text">
              We architect autonomous AI agents, voice AI systems, and production-ready automation platforms. Every blueprint is verified, deployed, and open.
            </p>

            <div className="flex flex-wrap items-center gap-3 w-full mt-2">
              <Link
                href="/projects"
                className="w-full sm:w-auto flex items-center justify-center gap-2 h-11 px-5 rounded-xl text-xs font-semibold bg-primary text-primary-foreground hover:opacity-90 shadow-md shadow-primary/20 transition-all hover:translate-y-[-1px] active:scale-[0.98]"
              >
                Explore Solutions <ArrowRight className="h-3.5 w-3.5" />
              </Link>
              <Link
                href="/projects"
                className="w-full sm:w-auto flex items-center justify-center h-11 px-5 rounded-xl text-xs font-semibold border border-border bg-secondary/40 hover:bg-accent text-muted-foreground hover:text-foreground transition-all hover:translate-y-[-1px] active:scale-[0.98]"
              >
                View Projects
              </Link>
              <Link
                href="/dashboard"
                className="w-full sm:w-auto flex items-center justify-center h-11 px-5 rounded-xl text-xs font-semibold border border-border bg-secondary/40 hover:bg-accent text-muted-foreground hover:text-foreground transition-all hover:translate-y-[-1px] active:scale-[0.98]"
              >
                Open Dashboard
              </Link>
            </div>

            {/* Premium Social Contacts */}
            <div className="flex items-center gap-3.5 mt-4">
              <a href="https://github.com/buildwithpnj" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl border border-border bg-secondary text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all hover:scale-[1.05]">
                <Github className="h-4.5 w-4.5" strokeWidth={1.8} />
              </a>
              <a href="https://twitter.com/buildwithpnj" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl border border-border bg-secondary text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all hover:scale-[1.05]">
                <Twitter className="h-4.5 w-4.5" strokeWidth={1.8} />
              </a>
              <a href="https://linkedin.com/in/pnj" target="_blank" rel="noopener noreferrer" className="p-2.5 rounded-xl border border-border bg-secondary text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all hover:scale-[1.05]">
                <Linkedin className="h-4.5 w-4.5" strokeWidth={1.8} />
              </a>
              <a href="mailto:hello@buildwithpnj.com" className="p-2.5 rounded-xl border border-border bg-secondary text-muted-foreground hover:text-foreground hover:border-primary/20 transition-all hover:scale-[1.05]">
                <Mail className="h-4.5 w-4.5" strokeWidth={1.8} />
              </a>
            </div>

          </div>

          {/* RIGHT SIDE: Interactive Portrait and Orbiting Tech Stack Ecosystem */}
          <div 
            ref={rightContainerRef}
            className="lg:col-span-7 w-full mt-10 lg:mt-0 h-[520px] sm:h-[650px] lg:h-[760px] relative flex items-center justify-center select-none z-20"
          >
            {/* Wrap orbiting stack elements in a unified pointer-interactive layout container */}
            <div className="absolute inset-0 pointer-events-none lg:pointer-events-auto">
              {/* Top Orbiting Card: AI Voice Agent */}
              <div 
                id="node-voiceagent"
                className="hidden lg:flex absolute top-[2%] left-1/2 -translate-x-1/2 p-2 rounded-xl border border-border/30 bg-card/75 backdrop-blur-md text-left flex-col gap-1 max-w-[150px] shadow-lg shadow-cyan-500/5 hover:border-primary/30 transition-all hover:scale-[1.03] duration-300"
              >
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="font-pixel text-[8px] font-bold text-emerald-400">● LIVE</span>
                </div>
                <h4 className="font-mono text-[9px] font-black text-foreground uppercase">AI Voice Agent</h4>
                <p className="text-[7.5px] leading-snug text-muted-foreground">Real-time conversational voice.</p>
              </div>

              {/* Orbiting Category Node Badges */}
              
              {/* Python Badge */}
              <EcosystemNode 
                id="node-python"
                label="Python"
                className="top-[18%] left-[2%] sm:left-[10%]"
                hoverLabel="Ollama • DeepSeek • Mistral • Llama • Hugging Face"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* FastAPI Badge */}
              <EcosystemNode 
                id="node-fastapi"
                label="FastAPI"
                className="top-[18%] right-[2%] sm:right-[10%]"
                hoverLabel="REST APIs • WebSockets • GraphQL • Node.js"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* LangChain Badge - Simplified (Hidden on mobile) */}
              <EcosystemNode 
                id="node-langchain"
                label="LangChain"
                className="hidden sm:block top-[30%] left-[4%]"
                hoverLabel="LangGraph • LlamaIndex • Agentic AI • Prompt Eng"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* PostgreSQL Badge - Simplified (Hidden on mobile) */}
              <EcosystemNode 
                id="node-postgresql"
                label="PostgreSQL"
                className="hidden sm:block top-[30%] right-[4%]"
                hoverLabel="Redis • MongoDB • pgvector • Supabase"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* Claude Badge */}
              <EcosystemNode 
                id="node-claude"
                label="Claude"
                className="top-[42%] left-[2%] sm:left-[10%]"
                hoverLabel="TypeScript • JavaScript • Embeddings • Context Eng"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* Gemini Badge */}
              <EcosystemNode 
                id="node-gemini"
                label="Gemini"
                className="top-[45%] left-1/2 -translate-x-1/2"
                hoverLabel="Google • A2A • JSON Schema • Evaluation"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* OpenAI Badge */}
              <EcosystemNode 
                id="node-openai"
                label="OpenAI"
                className="top-[42%] right-[2%] sm:right-[10%]"
                hoverLabel="Tool Calling • Function Calling • Streaming • OAuth"
                hoveredNode={hoveredNode}
                setHoveredNode={setHoveredNode}
              />

              {/* CENTER LABELS (Visual hints overlay behind the portrait) */}
              <div className="hidden lg:block absolute top-[30%] left-1/2 -translate-x-1/2 text-center pointer-events-none">
                <span className="font-pixel text-[8px] tracking-[0.3em] text-primary/30 uppercase block">AI CORE</span>
                <span className="font-mono text-[7px] text-muted-foreground/20 uppercase block mt-1">REASONING • PLANNING • MEMORY</span>
              </div>

              {/* Downward Vertical Orchestration Flow */}
              <div 
                id="node-flow-mcp"
                className="absolute top-[51%] left-1/2 -translate-x-1/2 w-full max-w-[280px] flex flex-col gap-1.5 items-center font-mono text-[8px]"
              >
                {/* Vertical connecting line indicator */}
                <div className="w-[1.2px] h-3 bg-gradient-to-b from-primary/35 to-purple-500/25 animate-pulse" />

                <FlowStackItem label="MCP • A2A • RAG" desc="Agent communication context layers" />
                <FlowStackItem label="Memory • Context • Tools" desc="Persistent semantic extraction" />
                <FlowStackItem label="Voice AI • Automation" desc="Trigger logic routing pipelines" />
                
                {/* Product Stack Cards */}
                <FlowCardItem label="AI Automation Platform" status="ACTIVE" desc="Workflow Trigger routing pipes." version="v1.0" />
                <FlowCardItem label="Customer Support AI" status="ONLINE" desc="Multi-agent CRM ticket resolver." version="v1.8" />
                <FlowCardItem label="Warborn OS" status="BUILDING" desc="Agentic desktop workspace." version="v0.2" color="bg-amber-500" />
                <FlowCardItem label="AI Growth Agent" status="DEPLOYED" desc="Autonomous lead outreach engine." version="v2.1" />
              </div>

              {/* Hover secondary tech disclosures panel */}
              {hoveredNode && (
                <div className="hidden lg:flex absolute bottom-[2px] left-4 right-4 p-2.5 rounded-xl border border-primary/20 bg-background/90 backdrop-blur-md flex-col gap-1 text-center font-mono text-[8.5px] z-30 shadow-lg animate-in">
                  <span className="text-[7.5px] text-primary/80 uppercase font-black tracking-widest">{"// COMPILER PIPELINE STACK"}</span>
                  <span className="text-foreground font-black tracking-wide uppercase">{hoveredNode}</span>
                </div>
              )}
            </div>

          </div>

        </div>
      </div>
      
      {/* Scroll indicator overlay */}
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-1.5 opacity-60 hover:opacity-100 transition-opacity">
        <span className="font-pixel text-[9px] tracking-widest text-muted-foreground uppercase">SCROLL TO DISCOVER</span>
        <div className="w-5 h-8 rounded-full border border-border flex justify-center p-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce" />
        </div>
      </div>
    </section>
  );
}

/* ============================================================================
   SUB-COMPONENT: Orbiting Ecosystem Node Badge
   ============================================================================ */
function EcosystemNode({ 
  id, 
  label, 
  className, 
  hoverLabel, 
  setHoveredNode 
}: { 
  id: string; 
  label: string; 
  className: string; 
  hoverLabel: string;
  hoveredNode: string | null;
  setHoveredNode: (val: string | null) => void;
}) {
  return (
    <div
      id={id}
      onMouseEnter={() => setHoveredNode(`${label}: ${hoverLabel}`)}
      onMouseLeave={() => setHoveredNode(null)}
      className={cn(
        "absolute p-1.5 px-2 sm:p-2 sm:px-3 rounded-lg border border-border/40 bg-card/75 backdrop-blur-sm font-mono text-[7.5px] sm:text-[8.5px] font-black text-foreground/80 hover:text-primary hover:border-primary/30 transition-all hover:scale-[1.06] duration-250 cursor-pointer shadow shadow-primary/2 shadow-lg select-none",
        className
      )}
    >
      {label}
    </div>
  );
}

/* ============================================================================
   SUB-COMPONENTS: Vertical Flow Orchestration stack
   ============================================================================ */
function FlowStackItem({ label, desc }: { label: string; desc: string }) {
  return (
    <div className="w-full max-w-[155px] sm:max-w-[190px] p-1 px-1.5 sm:px-2 rounded-lg border border-border/25 bg-background/50 text-center flex flex-col gap-0.5 shadow">
      <span className="font-black text-foreground/90 uppercase tracking-tight text-[7px] sm:text-[8px]">{label}</span>
      <span className="text-[5.5px] sm:text-[6.5px] text-muted-foreground/80 leading-none">{desc}</span>
    </div>
  );
}

function FlowCardItem({ label, status, desc, version, color = 'bg-primary' }: { label: string; status: string; desc: string; version: string; color?: string }) {
  return (
    <div className="w-full p-1 sm:p-1.5 px-2 sm:px-2.5 rounded-xl border border-border/30 bg-card/60 hover:bg-card/90 text-left flex items-start justify-between gap-2 sm:gap-3 shadow hover:border-primary/20 hover:scale-[1.01] transition-all">
      <div className="flex flex-col gap-0.5 max-w-[72%]">
        <h5 className="font-black text-foreground uppercase tracking-tight text-[7.5px] sm:text-[8.5px]">{label}</h5>
        <p className="text-[6.5px] sm:text-[7px] leading-tight text-muted-foreground">{desc}</p>
      </div>
      <div className="flex flex-col items-end gap-1 shrink-0">
        <div className="flex items-center gap-1">
          <span className={cn("w-1 h-1 rounded-full", color)} />
          <span className="text-[6px] sm:text-[6.5px] font-bold text-foreground/75 tracking-wider">{status}</span>
        </div>
        <span className="text-[5.5px] sm:text-[6px] text-muted-foreground font-bold px-0.5 rounded bg-background/50 border border-border/40">{version}</span>
      </div>
    </div>
  );
}

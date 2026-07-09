---
title: "Day Log: Building a Living Homepage and Debugging Six Hours of Deployment Hell — July 9, 2026"
excerpt: "Thirty-three commits. A dynamic canvas color system that reads your portrait. A deployment that failed seven times. And the asyncio bug that made every login return 500."
publishDate: "2026-07-09"
tags: ["engineering-log", "fastapi", "nextjs", "asyncio", "deployment", "design-system", "canvas"]
featured: true
draft: false
---

# Day Log: Building a Living Homepage and Debugging Six Hours of Deployment Hell — July 9, 2026

**33 commits. 41 files changed. 2,503 insertions, 855 deletions.**

Some days you ship features. Some days you fight your infrastructure. Today was both, compressed into one eight-hour sprint that started with animation polish and ended at 21:26 IST with a `psycopg2` synchronous seed call that finally made login return HTTP 200.

This is a full accounting of what happened.

---

## 1. Introduction

The goal coming into today was straightforward on paper: evolve the BuildWithPNJ homepage from a static portfolio page into something that feels alive — a site that reads the developer's portrait, pulls dominant colors from it, and uses those colors to drive the entire design system in real time. Alongside that, we needed to automate database migrations and seeding inside the FastAPI lifespan startup hook so Render deployments would self-initialize without manual intervention.

Neither turned out to be simple.

The frontend work went deep — deeper than planned — because once you start pulling pixel data out of a `<canvas>` element and routing it into CSS variables, you start realizing just how many things can respond to color: radar overlays, sonar pings, headline glyphs, terminal log streams, button gradients, particle shimmer. Each one you wire up makes the whole system feel more coherent, and coherence is addictive. The session stretched.

The backend work went long for the opposite reason: not ambition, but a cascade of compounding failures. Each fix revealed the next layer of the problem. URL scheme wrong. Password URL-encoding broken. PgBouncer statement cache incompatible. ConfigParser escaping wrong. And then, finally, the root cause underneath all of it: `asyncio.run()` called inside a background thread during startup closes the default event loop — the same one FastAPI's uvicorn is running on — and every subsequent database request throws `RuntimeError: Event loop is closed`.

Seven deployments to Render to get to that root cause. The fix was six lines.

---

## 2. Frontend Engineering

### 2.1 The Hero Canvas Color System

This is the centerpiece of today's frontend work. The commit chain from `c355916` through `c00a210` to `3175353` tells the full story of how the color system evolved from a rough idea into a working, pixel-accurate dynamic design system.

The problem we were solving: static hardcoded accent colors feel arbitrary. When a site is built around a specific person — their portrait is the centerpiece — the color system should derive from them, not from a designer's arbitrary HSL picker selection. The goal was to sample the actual pixel data of the developer's PNG portrait and use the dominant high-saturation colors to drive every glowing, pulsing, radiating element on the page.

**Implementation: The Pixel Sampling Loop**

The portrait is rendered into an offscreen `<canvas>` element. Once the `ImageData` is available, we iterate over every 4th pixel (RGBA stride), convert to HSL, filter for saturation above 48 (which excludes near-whites, near-grays, and near-blacks while keeping cybernetic cyans, electric blues, and warm ambers), and accumulate a frequency map.

```javascript
// Simplified pseudocode — full implementation in hero/ColorExtractor.ts
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
ctx.drawImage(img, 0, 0, sampleWidth, sampleHeight);
const { data } = ctx.getImageData(0, 0, sampleWidth, sampleHeight);

const colorBuckets = {};

for (let i = 0; i < data.length; i += 4 * stride) {
  const [r, g, b, a] = [data[i], data[i+1], data[i+2], data[i+3]];
  if (a < 128) continue; // skip transparent pixels

  const [h, s, l] = rgbToHsl(r, g, b);
  if (s < 48) continue; // skip desaturated — only cybernetic colors

  const bucket = Math.round(h / 10) * 10; // 10-degree hue buckets
  colorBuckets[bucket] = (colorBuckets[bucket] || 0) + 1;
}

const dominantHue = Object.entries(colorBuckets)
  .sort(([, a], [, b]) => b - a)[0][0];
```

The dominant hue becomes the `--primary` CSS variable, propagated as an HSL string into the document root. From there, every component that references `--primary` — and there are now many — gets the photo-synced color automatically.

One caching issue showed up during local development (`3175353`): hot module replacement was holding a stale reference to the previous image's computed color. The fix was to add a `useEffect` cleanup that revokes the object URL and resets the canvas context on unmount.

**Commit `c00a210` — Synchronized Glow Propagation**

Once the dominant hue was extracted, we needed to propagate it to components that weren't reading CSS variables directly — specifically the Canvas 2D contexts drawing the radar rings, sonar pings, and particle shimmer. CSS variables aren't readable inside `canvas.getContext('2d')` draw calls. The solution was a singleton color store (a plain JavaScript object with a pub/sub pattern) that the extractor writes to and the Canvas animation loops read from on each frame.

This is not the cleanest architecture — a proper solution would use a React context or Zustand slice — but it worked and kept the coupling surface small. It's marked as a refactor candidate.

### 2.2 Portrait Rendering: Blueprint Radar, Chromatic Aberration, Particle Shimmer

Commit `21f5e11` introduced what is now the most visually complex piece of the hero: the Interactive Portrait centerpiece with layered Canvas effects.

**Blueprint radar overlays** are concentric circles drawn on a Canvas layer behind the portrait, with opacity pulsing at 2Hz. The ring radius expands and contracts using a sine wave. The stroke color reads from the color store.

**Chromatic aberration offsets** are faked using three semi-transparent copies of the portrait drawn at ±1px and ±2px offsets in red, green, and blue channels respectively, with very low alpha. On a dark background the effect reads as a slight RGB fringe — subtle enough that it doesn't feel like a filter preset, but visible enough to give the portrait a slightly electronic quality.

**Spatial particle shimmer** is a field of 120 particles drawn on a separate Canvas layer. Each particle has:
- A position that drifts slowly outward from the portrait bounds
- A radius between 0.5 and 2px
- An opacity that oscillates independently using a seeded sine function
- A hue sampled from the color store ± 20 degrees of random spread

The neural wave heartbeat effect is a sine wave drawn horizontally across the bottom of the portrait, rendered as a `Path2D` and updated each animation frame. The amplitude spikes at a configurable interval to simulate a pulse — currently set to every 2.8 seconds.

### 2.3 Telemetry Ticker and Sonar Pings

**SystemTelemetryTicker** (`ca41b76`) is a full-width LED status bar in the root layout, inspired by NASA mission control displays. It cycles through a rotating list of system status messages — build status, uptime, memory, API latency — displayed in a monospace font with a subtle scanline effect. The messages scroll horizontally using a CSS `translateX` keyframe animation. The text color reads from `--primary`.

**Sonar pings** (`33cc998`) replaced the static capability bullet indicators. Each capability listing item now has an expanding ring animation — a `border-radius: 50%` div that scales from 0 to 2 and fades out, on a staggered delay per item. The timing is offset so the rings ripple sequentially rather than all firing simultaneously, giving the impression of active system polling rather than a decoration.

**Telemetry Ticker cycling capability listings** (`18b9e6c`) then replaced the static text entirely. The capability list is now a horizontal sliding window that cycles through eight system operation strings on a 3-second interval, with a CSS `transform: translateY` transition between items. This was a late session decision — the static list felt like a CV; the ticker feels like a running process.

### 2.4 Motion Architecture: ScrollReveal and Hover Lifts

Commit `3175353` introduced the `ScrollReveal` component. The implementation uses `IntersectionObserver` with a threshold of 0.15, meaning elements begin their reveal when 15% of them enter the viewport. Each observed element gets `opacity: 0; filter: blur(6px); transform: translateY(16px)` as its initial state, transitioning to `opacity: 1; filter: blur(0); transform: translateY(0)` on intersection.

The stagger is implemented by reading a `data-reveal-index` attribute on each child and multiplying by 80ms to set `transition-delay`. This avoids JavaScript timer management and keeps the stagger logic in CSS.

Card hover lifts add `transform: translateY(-4px)` and a box-shadow elevation increase on `:hover`. The transition duration is 200ms with `ease-out` — long enough to feel intentional, short enough to feel responsive.

### 2.5 Background Depth System

Commit `2a4ecef` added the noise texture overlay, floating gradient orbs, section dividers, and volumetric depth utilities. The noise texture is a 200×200px SVG-based `filter: url(#noise)` element positioned absolutely at full viewport size with `pointer-events: none`. Floating gradient orbs are `position: fixed` divs with radial gradients and a slow drift animation (40s cycle) — they contribute to perceived depth without competing with content.

Section dividers (`f3aa78b`) are `linear-gradient` backgrounds on `<hr>`-equivalent elements, fading from the section background color to transparent. This is a simple trick but eliminates the harsh visual edges between section backgrounds.

### 2.6 Project Card Terminal Simulations

Commit `33ceec6` replaced the static CPU icons on project cards with three alternating terminal animation styles:

1. **Line-by-line log stream**: Characters appear one at a time in a monospace terminal, simulating a running process.
2. **LED progress bar**: A horizontal bar fills from 0 to 100% with a color transition, loops with a reset delay.
3. **Blinking cursor loop**: A prompt character blinks in a terminal-like cadence with a rotating set of simulated commands.

Each card is assigned one of the three styles based on its index mod 3. This ensures visual variety without requiring per-card configuration.

### 2.7 Floating Island Navbar

Commit `5ec9c81` finalized the floating island navbar. The nav is `position: fixed`, centered horizontally, with a `backdrop-filter: blur(12px)` frosted glass background. The hover color on nav links is bound to `var(--primary)` — meaning it automatically picks up the photo-synced color from the hero. When the portrait color changes (if a different portrait is loaded), the entire navbar hover state updates without touching navbar code.

---

## 3. Infrastructure and Deployment

This is where the day got expensive.

The deployment target is a standard split: Next.js frontend on Vercel at `buildwithpnj.in`, FastAPI backend on Render at `dashboard-nb61.onrender.com`, database on Supabase PostgreSQL accessed through PgBouncer on port 6543.

The goal was simple: on Render startup, run Alembic migrations to ensure schema is current, then seed the database with a default admin user (`prakashjhadps@gmail.com`) if one doesn't exist. This is table-stakes deployment automation — nothing exotic.

What followed was seven failed deployments over approximately two and a half hours.

### Failure 1 — URL Scheme Mismatch

Render injects `DATABASE_URL` as a plain `postgresql://` connection string. SQLAlchemy's async engine requires `postgresql+asyncpg://`. First fix: a parser in `config.py` that rewrites the scheme on load.

```python
# config.py (after fix)
@property
def database_url(self) -> str:
    url = os.environ.get("DATABASE_URL", "")
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url
```

Deployed. Failed. Next layer.

### Failure 2 — Password Special Character

The database password is `dobbie@KAP1`. The `@` character in a URL signals the start of the host segment. Python's `urllib.parse.urlparse` treats everything after the last `@` as the host, splitting the password mid-string. The connection string was being parsed as a malformed URL, giving SQLAlchemy a garbled hostname.

Fix: URL-encode the password using `urllib.parse.quote(password, safe='')`. This requires parsing the URL into components, encoding just the password field, and reassembling. Added in `a7f4a82` and `da78343`.

Deployed. Failed on a different error. Progress.

### Failure 3 — DATABASE_URL= Literal Prefix

Render's environment variable injection, when copied from their dashboard, sometimes includes the variable name as a prefix in the value. The actual string stored in the environment was `DATABASE_URL=postgresql://...` — with the key name literally prepended to the value. The parser was receiving `DATABASE_URL=` as part of the URL and passing it to `urlparse`, which produced garbage.

Fix: strip the prefix before parsing.

```python
url = url.removeprefix("DATABASE_URL=")
```

Commit `f5ce6a6`. Deployed. Failed.

### Failure 4 — PgBouncer Statement Cache

Supabase's PgBouncer in transaction pooling mode does not support named prepared statements. SQLAlchemy and asyncpg both cache prepared statements by default. The error:

```
asyncpg.exceptions.FeatureNotSupportedError:
prepared statement "..." already exists
```

This is a well-documented PgBouncer gotcha. Fix: disable statement cache.

```python
# In engine creation:
connect_args={"statement_cache_size": 0}

# In alembic/env.py create_engine call:
connect_args={"statement_cache_size": 0}
```

Commit `562c032`. Deployed. Failed.

### Failure 5 — ConfigParser % Escaping

Alembic reads `alembic.ini` using Python's `configparser`. ConfigParser treats `%` as the start of an interpolation sequence — `%(varname)s` style. The database URL contained `%40` (URL-encoded `@`). ConfigParser tried to interpolate `%40` as a variable reference, failed, and threw:

```
configparser.InterpolationSyntaxError:
'%' must be followed by '%' or '(', found: '%40'
```

Fix: escape every `%` in the URL string to `%%` before writing it into the Alembic config object.

```python
# alembic/env.py
config.set_main_option(
    "sqlalchemy.url",
    database_url.replace("%", "%%")
)
```

Commit `21a52f5`. Deployed. Got further than before. Login returned 500.

### Failure 6 and 7 — The Actual Root Cause

At this point the migrations were running. The seed code was executing. But login was still returning 500. The error in Render logs:

```
RuntimeError: Event loop is closed
```

On every single request to any database-touching endpoint. This was confusing because the startup hook had finished by the time requests were hitting the API. The event loop should have been fine.

---

## 4. The Root Cause: asyncio Event Loop Architecture

Python's `asyncio.run()` is a high-level convenience function. It does three things: creates a new event loop, runs the given coroutine until completion, and then calls `loop.close()` before returning. That `loop.close()` is the problem.

The FastAPI application runs on uvicorn, which uses a single event loop for the entire process lifetime. That event loop is Python's default event loop — `asyncio.get_event_loop()`. When the startup lifespan hook fires, it needs to run the async seed function. The seed function was wrapped in `asyncio.run()` and called inside a `ThreadPoolExecutor` thread (to avoid blocking the startup hook itself).

Here is what actually happened at runtime:

1. uvicorn creates the default event loop and starts running FastAPI on it.
2. FastAPI's lifespan `startup` fires.
3. Startup spawns a thread via `asyncio.get_event_loop().run_in_executor()`.
4. Inside that thread, `asyncio.run(seed())` is called.
5. `asyncio.run()` creates a **new** event loop for the coroutine, runs `seed()`, then calls `loop.close()` when done.
6. The closed loop becomes the default event loop for the process.
7. uvicorn's server is still running on the original loop object — but `asyncio.get_event_loop()` in subsequent request handlers now returns the closed loop.
8. Every `await db.execute(...)` call throws `RuntimeError: Event loop is closed`.

The fix was to remove asyncio entirely from the seed path. The seed function was rewritten to use a synchronous SQLAlchemy engine with `psycopg2` (not asyncpg), called directly — no threads, no `asyncio.run()`, no coroutines.

```python
# seed.py (after fix)
import psycopg2
from sqlalchemy import create_engine, text

def seed_sync():
    sync_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url, connect_args={"sslmode": "require"})
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": "prakashjhadps@gmail.com"}
        )
        if result.fetchone() is None:
            conn.execute(
                text("INSERT INTO users (email, hashed_password, is_active) VALUES (:email, :pw, true)"),
                {"email": "prakashjhadps@gmail.com", "pw": hashed_default_password}
            )
            conn.commit()
```

This runs synchronously inside the startup thread. It has zero interaction with the asyncio event loop. It uses `psycopg2` directly through SQLAlchemy's sync dialect. It does not close anything that uvicorn owns.

Commit `c2ab969` deployed at 21:26 IST.

Login test: `POST /auth/login` with the seeded credentials.

```
HTTP 200 OK
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Done.

---

## 5. Key Metrics

| Metric | Value |
|--------|-------|
| Total commits | 33 |
| Files changed | 41 |
| Insertions | 2,503 |
| Deletions | 855 |
| Render deployments | 7 |
| Hours on backend debugging | ~2.5 |
| Time of final fix | 21:26 IST |
| Login status after fix | HTTP 200 + JWT |
| Canvas color extraction threshold | Saturation > 48 |
| ScrollReveal stagger interval | 80ms per index |
| Particle count in shimmer layer | 120 |
| Sonar ping interval | 3s |
| Telemetry ticker cycle | 8 items, 3s rotation |

---

## 6. Lessons Learned

**On asyncio:**
`asyncio.run()` is designed for scripts, not for use inside long-running server processes. The documentation says this clearly; we ignored it. In a server context, if you need to run an async function from a non-async context, use `asyncio.get_event_loop().run_until_complete()` from the main thread, or restructure so you're not calling async code from a thread at all. The cleanest solution in our case was eliminating asyncio from the seed path entirely — synchronous operations for a one-time startup seed are not a performance problem.

**On URL parsing with special characters:**
Database passwords containing `@`, `%`, `#`, or `/` will break any naive URL string replacement. The correct approach is to always parse the URL into components (`urllib.parse.urlsplit`), encode the username and password fields independently with `urllib.parse.quote(safe='')`, and reconstruct using `urllib.parse.urlunsplit`. Do this once, at the config layer, and never string-replace a URL again.

**On incremental deployment debugging:**
Seven deployments is too many. Each one took 3-5 minutes to build and start on Render, meaning roughly 25-30 minutes of wall-clock time was spent waiting for feedback. A local Docker replica of the Render environment would have compressed this to minutes. That setup is now on the backlog.

**On Canvas color systems:**
The pixel extraction approach works well for portraits with distinct chromatic character — a subject with warm skin tones, colored clothing, or a colorful background will produce a usable dominant hue. For grayscale or near-monochrome portraits, the saturation filter (`s > 48`) will reject most pixels and the system will fall back to a hardcoded default. That fallback currently exists but isn't elegant. A future improvement is a tiered saturation strategy: try `s > 48`, fall back to `s > 30`, fall back to `s > 15`, finally fall back to default.

**On scope management:**
The frontend work expanded significantly beyond the initial plan. The color system is genuinely good and worth the time spent, but eight hours of frontend commits delayed the backend work that was actually blocking deployment. In hindsight: fix the deployment blocker first, then iterate on the design system. The hero works locally even without the API.

---

*Next session: clean up the color store architecture (replace singleton with Zustand slice), implement the tiered saturation fallback, and write integration tests for the FastAPI startup lifespan hook.*

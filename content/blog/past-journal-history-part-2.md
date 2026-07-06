---
title: "The Open Source Archives: Retrospective Part 2 (May 2026 - Jul 2026)"
excerpt: "Analyzing 3D RAG Portfolios, Dialora AI receptionists, payment timeouts, browser PDF editors (PDFSeva), and the Unified Personal OS."
publishDate: "2026-07-06"
tags: ["retrospective", "nextjs", "webrtc", "pdfjs", "fastapi"]
featured: true
draft: false
---

In this second part of our historical engineering review, we document the systems built between **May 2026 and July 2026**, covering advanced interactive systems, RAG indexes, document manipulation workspaces, and local Operating Systems.

---

## 🛠️ Project Retrospective

### 1. Dialora AI Receptionist
*   **Purpose**: AI voice agent managing customer phone calls, bookings, and CRM logs.
*   **Local Location**: `C:\Users\praka\my-github-projects\DialoraAI`
*   **Key Tech**: Next.js 16 (App Router), TS, Tailwind v4, Framer Motion, Recharts.
*   **Key Commit Records**:
    *   `4c7dc10 - feat: add ROICalculator widget to root homepage /app/page.tsx (2026-06-12)`
    *   `3dcd799 - fix: resolve text contrast in PageHero and add animated graphics (2026-06-12)`
*   **Hurdles & Solutions**:
    *   *Problem*: Buttons on the dark-mode Final CTA section failed WCAG contrast check under light-theme modes.
    *   *Solution*: Isolated the CTA container within a locked dark-theme utility class (`dark`) to force correct text contrast ratios.

### 2. myportfolio: 3D Galaxy Portfolio
*   **Purpose**: Interactive developer portfolio showcasing skills, containing a RAG chatbot assistant.
*   **Local Location**: `C:\Users\praka\my-github-projects\myportfolio`
*   **Key Tech**: React Three Fiber, Three.js, GSAP, FAISS, OpenAI API.
*   **Key Commit Records**:
    *   `1e23942 - Image update (2026-05-24)`
    *   `9527427 - Fix UI/UX inconsistencies: branding, loading screen, theme system (2026-04-23)`
*   **Hurdles & Solutions**:
    *   *Problem*: FAISS index queries on the local RAG chatbot generated duplicate responses if the user prompt matched overlapping documents.
    *   *Solution*: Implemented Maximal Marginal Relevance (MMR) retrieval to diversify source documents before prompt engineering.

### 3. Next.js Payment Gateway
*   **Purpose**: Highly resilient mock checkout portal utilizing local storage history.
*   **Local Location**: `C:\Users\praka\my-github-projects\Next.js-payment-gateway`
*   **Key Tech**: Next.js 16, Zustand, Tailwind 4.
*   **Key Commit Records**:
    *   `d973b6d - Update README.md (2026-05-06)`
    *   `8e5e82d - chore: initialize payment gateway assignment (2026-05-06)`
*   **Hurdles & Solutions**:
    *   *Problem*: Users submitting payments multiple times during network lag created duplicate transactions.
    *   *Solution*: Implemented UUID-based idempotency tokens generated on form load. If a submission retried, the API matched the token and returned the cached status rather than creating a new payment.

### 4. PDFSeva AI
*   **Purpose**: India-first document editor allowing signing, watermarking, page rotation, and merging.
*   **Local Location**: `C:\Users\praka\my-github-projects\pdfseva`
*   **Key Tech**: Next.js, `pdf-lib`, PDF.js, Konva, FastAPI.
*   **Key Commit Records**:
    *   `a141e05 - Add advanced PDF editor, AI copilot actions, and i18n (2026-05-19)`
    *   `658fed6 - Initial PDFSeva AI MVP (2026-05-18)`
*   **Hurdles & Solutions**:
    *   *Problem*: Loading large PDFs (e.g. 50+ pages) in browser canvas editors locked the main main thread, causing severe scrolling lag.
    *   *Solution*: Set up offscreen worker rendering and only render page canvases that are visible within the current viewport using an IntersectionObserver hook.

### 5. PricePilot (DealLens AI)
*   **Purpose**: Scraper-bot comparison shopping search.
*   **Local Location**: `C:\Users\praka\my-github-projects\pricepilot`
*   **Key Tech**: Next.js, FastAPI, OpenSearch, Playwright.
*   **Key Commit Records**:
    *   `a26e0ff - Initial commit: DealLens AI MVP (2026-05-08)`
*   **Hurdles & Solutions**:
    *   *Problem*: Product comparison queries triggered severe bot blocks on Amazon and Flipkart.
    *   *Solution*: Set up a headless browser pool with random user-agent rotations and query delays (1-3s jitter) to distribute indexing loads.

### 6. Personal OS (Dashboard)
*   **Purpose**: Single-user local developer workspace coordinating finances, notes, books, habits, and Drive backups.
*   **Local Location**: `C:\Users\praka\my-github-projects\Dashboard`
*   **Key Tech**: Next.js 15, FastAPI, Supabase RLS, Redis, Celery.
*   **Key Commit Records**:
    *   `fdcbd78 - feat(portfolio): Integrate scanned GitHub projects and complete portfolio cataloging all 16 repositories (2026-07-06)`
    *   `c1622d0 - Initial commit (2026-07-03)`
*   **Hurdles & Solutions**:
    *   *Problem*: Concurrency conflicts during local notes offline edits and GDrive backups.
    *   *Solution*: Configured strict timestamp vectors to run reconciliation logic when local note edits are out-of-sync with remote instances.

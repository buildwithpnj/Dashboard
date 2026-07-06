---
title: "The Open Source Archives: Retrospective Part 1 (Dec 2025 - Apr 2026)"
excerpt: "Diving into early multimodal audio CAD systems (ADA V2), multi-agent review networks (Agentix), custom Three.js WebGL systems (MTRX), and CRM integrations."
publishDate: "2026-05-01"
tags: ["retrospective", "python", "ai-agents", "threejs"]
featured: false
draft: false
---

Documenting the building-in-public journey requires capturing the code commits, architectural decisions, and specific debugging hurdles. In this journal entry, we retroactively dissect the projects built between **December 2025 and April 2026**, detailing the code structures, commit records, and hurdles resolved along the way.

---

## 🛠️ Project Deep Dives

### 1. A.D.A V2: Advanced Design Assistant
*   **Purpose**: A desktop virtual assistant combining Google Gemini 2.5 Native Audio with hand hand-gesture controls and parametric 3D CAD output.
*   **Local Location**: `C:\Users\praka\my-github-projects\ada_v2`
*   **Key Tech**: Python, Electron, React, MediaPipe (gesture), `build123d` (CAD modeling to STL).
*   **Key Commit Records**:
    *   `d005af7 - feat: Add initial backend services including a Gemini-powered CAD agent, printer agent, server, and configuration (2025-12-23)`
    *   `e4a4920 - feat: Add Kasa, Printer, CAD, and Face Authenticator agents with corresponding tests (2025-12-17)`
*   **Hurdles & Solutions**:
    *   *Problem*: Generating CAD parametric files (`.stl`) from raw audio prompts had latency peaks of 15 seconds, blocking the Electron UI thread.
    *   *Solution*: Offloaded the model generation to a background Python worker communicating via lightweight local HTTP posts, utilizing socket streams to deliver chunk progress.
    *   *Problem*: Hand gesture frame tracking using MediaPipe was jittery and resource-intensive on standard CPUs.
    *   *Solution*: Implemented double-exponential smoothing on coordinates, filtering outliers before translating gestures to OS window movements.

### 2. Agentix Code Analyzer
*   **Purpose**: Coordinated multi-agent code analysis suite evaluating GitHub repositories and producing rich documentation (vulnerability matrices, architectural guides).
*   **Local Location**: `C:\Users\praka\my-github-projects\Agentix-Code-Analyzer`
*   **Key Tech**: FastAPI, Streamlit, LangGraph, ChromaDB.
*   **Key Commit Records**:
    *   `0fc93f2 - Encourage users to like the project (2026-04-13)`
    *   `e9cdda0 - Add files via upload (2026-04-12)`
*   **Hurdles & Solutions**:
    *   *Problem*: Complex repository dependency trees caused recursive loop overflows inside the LangGraph state machine.
    *   *Solution*: Introduced strict depth limits (max 3 nested folders) on codebase parsers and structured the chunking parser to skip vendor directories.

### 3. ecommercewithcrm (Aaina Boutique)
*   **Purpose**: Customized boutique shop storefront integrating product listing tools and a customer relations manager.
*   **Local Location**: `C:\Users\praka\my-github-projects\ecommercewithcrm`
*   **Key Tech**: Express, Node, React, Multer, Render Host.
*   **Key Commit Records**:
    *   `6875e4b - fix: image upload works locally without Cloudinary, serve uploads via static files (2026-04-20)`
    *   `3f89012 - fix: product creation - relax validator, auto-generate SKU, fix field mapping (2026-04-20)`
*   **Hurdles & Solutions**:
    *   *Problem*: Render.com hosting instance crashed during file uploads due to Cloudinary API key timeout limits.
    *   *Solution*: Bypassed Cloudinary uploads for local environments and implemented a fallback static multer diskStorage engine serving images directly.

### 4. MTRX WebGL Experiment
*   **Purpose**: Three.js WebGL particle mesh backgrounds reacting to mouse drag gestures.
*   **Local Location**: `C:\Users\praka\my-github-projects\MTRX`
*   **Key Tech**: JavaScript, HTML5 Canvas, Three.js.
*   **Key Commit Records**:
    *   `8ff46ae - feat: add Three.js WebGL dot background to all pages (2026-04-20)`
    *   `4b569e1 - fix: restore cursor:none + fix Three.js IIFE syntax + cache bust v3 (2026-04-20)`
*   **Hurdles & Solutions**:
    *   *Problem*: Browser caching prevented updated particle animation scripts from firing on client machines.
    *   *Solution*: Implemented query-string cache busting (`?v=3`) on all shared.js script elements inside the templates.

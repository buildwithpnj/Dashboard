# Roadmap

## Phase 0: Search Visibility & SEO Foundation (Completed)
- [x] Configured Google Search Console verification in public root.
- [x] Implemented dynamic sitemap.ts generation using `MetadataRoute`.
- [x] Blocked search engine crawlers from indexing `/login` and `/register` auth views.
- [x] Set up standard robots.txt routing profiles.

## Phase 1: Grid Foundation & Background (Completed)
- [x] Snapped all circuit lines to the 32px blueprint grid.
- [x] Implemented global `PremiumPixelBackground` with falling square pixel particles and snap grids.
- [x] Implemented document-relative `startY` calculation to keep line systems starting exactly at the bottom of `#hero-section-root`.
- [x] Tied AI Voice Agent card and packet animations to synchronized timing loops.

## Phase 2: Color Synchronization & Brand Polish (Completed)
- [x] Unified accent colors to Engineering Red (`#E5484D`) and Electric Blue (`#3B82F6`).
- [x] Synced central navigation bar styling, text highlighting, and PNJ brand logo dynamically to active portrait hover state variables.
- [x] Implemented PCB border trace animations pulsing electric blue along the outer container every 12 seconds.
- [x] Replaced browser fallback tab globe icon with high-res PNJ glowing sphere logo.
- [x] Simplified nested inner boxes to use borderless transparent backdrops (`bg-black/5 dark:bg-white/5`), keeping layout clean.
- [x] Optimised navbar backgrounds for light mode using theme-responsive class states (`dark:from-[#0A0F1D]/80 from-white/90`).

## Phase 3: Live Workspace & Telemetry Integrations (In Progress)
- [ ] Connect the sitemap routes with real database endpoints for Lab and Project views.
- [ ] Wire up real-time telemetry analytics for token processing and API response metrics to the footer terminal stream.
- [ ] Implement command execution hooks inside the terminal visualization overlay.

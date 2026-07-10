# Decisions Log (ADRs)

## ADR-001: Central CSS Variable Injection for Dynamic Color Sync
* **Problem**: Brand badge hovers inside the hero portrait should dynamically update colors (e.g. text highlights, packet rain, nav components) in real-time across the entire homepage.
* **Analysis**: Prop drilling is inefficient and causes performance bottlenecks. Styling inline overrides gets messy.
* **Solution**: Inject active colors directly into the document root `:root` as custom properties (`--hero-active-color`, `--hero-active-color-glow`) from `ai-portrait-hero.tsx`.
* **Tradeoffs**: Requires other client components to poll or dynamically evaluate styles using the variable, but minimizes React re-renders.

## ADR-002: SVG ViewBox Scaling for Footer Telemetry Ribbon
* **Problem**: Scrolling networks of data lines in `FooterDataStream` triggered horizontal browser scrollbars on narrow viewports.
* **Analysis**: Using `overflow-x-auto` was visually clunky.
* **Solution**: Rebuilt the layout as a scalable, responsive SVG using `viewBox="0 0 1200 140"` and `width="100%"`, containing all network nodes inside the vector space.
* **Tradeoffs**: Nodes scale dynamically with page width instead of preserving a fixed physical size, but resolves overflow bugs natively.

## ADR-003: Document-Absolute Grid Snapping for Background Circuits
* **Problem**: Background circuit lines and snapping nodes misaligned when scrolling or switching sections.
* **Analysis**: Using element heights without absolute page offsets caused rendering coordinates to drift.
* **Solution**: Target `#hero-section-root` and compute starting position using absolute coordinates `rect.bottom + window.scrollY` snapped to the closest grid value.

## ADR-004: Clean Borderless Navbar Design (Unified Glass)
* **Problem**: Outer header container and inner buttons all carried distinct borders and color tints, resulting in a nested "box-in-a-box" clutter.
* **Solution**: Moved the dynamic color tint (`var(--hero-active-color-glow)`) and shadows to the outer container. Removed borders and solid backdrops on inner buttons, switching them to borderless transparent glass (`bg-black/5 dark:bg-white/5`), only displaying active colors on mouse hover.
* **Tradeoffs**: Inner buttons look unified and flat, matching Linear and Vercel design aesthetics, but hover effects must remain crisp and immediate.

## ADR-005: Next.js Dynamic Sitemap Generator Integration
* **Problem**: Search engines need an active index of dynamic research labs, write-ups, and projects without manual configuration on updates.
* **Solution**: Integrated dynamic `sitemap.ts` using Next.js `MetadataRoute` templates to dynamically parse routing configurations on every query.
* **Tradeoffs**: Introduces a minor query build check on sitemap fetch, but fully eliminates stale sitemap links.

## ADR-006: Subtler Mouse Parallax Dampening Multipliers
* **Problem**: Mouse coordinates tracking inside the AI Portrait Hero workspace originally caused extreme, rapid rotations that felt distracting.
* **Solution**: Halved the rotation multiplier forces (dampening client side input factors) inside the tracking frame updates, delivering smooth 3D tilting effects.

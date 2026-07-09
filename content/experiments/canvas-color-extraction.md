---
id: "EXP-09"
title: "Dynamic Canvas Portrait Color Extraction"
tagline: "Sampling pixel data from a transparent PNG portrait to drive a living, photo-synced design system."
status: "completed"
category: "Design Experiments"
tags: ["canvas", "color-theory", "design-system", "hero", "pixel-art"]
hypothesis: "Extracting high-saturation pixels from a developer portrait and using them as live CSS variables will make the entire homepage feel organically connected to the subject."
publishDate: "2026-07-09"
---

# EXP-09: Dynamic Canvas Portrait Color Extraction

**Status:** Completed  
**Category:** Design Experiments  
**Date:** 2026-07-09  
**Commits:** `c00a210`, `3175353`, `21c555e`, `1d49b7e`

---

## Objective

Design systems typically define a color palette up front — a primary, a secondary, a handful of neutrals — and every component pulls from that palette. It works. It is also completely static and disconnected from the content it's presenting.

The BuildWithPNJ homepage is built around a person. The hero section is anchored to a developer portrait. The question this experiment asked: what if the color system derived from the portrait itself, rather than from a separate design decision? Could we sample the dominant colors from the actual PNG pixels and propagate them through the entire site in real time?

The concrete goal: build a pipeline that reads pixel data from the developer's portrait, extracts a dominant high-saturation hue, writes it to the `--primary` CSS variable on the document root, and verifies that downstream components (radar rings, sonar pings, headline text, navbar hover, button gradients, terminal log colors) respond to it automatically.

---

## Hypothesis

Extracting high-saturation pixels from a developer portrait and using them as live CSS variables will make the entire homepage feel organically connected to the subject — a coherence that hardcoded palettes cannot achieve. The saturation threshold of `s > 48` should be sufficient to exclude near-whites, near-grays, and dark background tones while capturing the chromatic character of skin tones, clothing, and any colored lighting in the photograph.

---

## Implementation

### Step 1: Offscreen Canvas Image Load

The portrait (`/portrait.png`) is a transparent PNG. It is drawn onto an offscreen `<canvas>` element (not inserted into the DOM) at a reduced sample size of 64×64px to minimize the cost of `getImageData`.

```typescript
// ColorExtractor.ts
function extractDominantColor(src: string): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const SAMPLE_SIZE = 64;
      const canvas = document.createElement("canvas");
      canvas.width = SAMPLE_SIZE;
      canvas.height = SAMPLE_SIZE;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0, SAMPLE_SIZE, SAMPLE_SIZE);

      const { data } = ctx.getImageData(0, 0, SAMPLE_SIZE, SAMPLE_SIZE);
      const hue = findDominantHue(data);
      resolve(`hsl(${hue}, 72%, 58%)`);
    };
    img.src = src;
  });
}
```

The sample size of 64×64 gives us 4,096 pixels to analyze — more than enough frequency data for hue bucketing, at a cost of ~16KB of RGBA data rather than the full-resolution image.

### Step 2: The Pixel Sampling Loop

We iterate over the RGBA byte array. Every pixel is 4 bytes (`R, G, B, A`). We stride by a factor of 4 to sample every pixel (or increase stride for further down-sampling if needed). Transparent pixels (`A < 128`) are skipped — the portrait background is transparent and we do not want to sample those pixels.

```typescript
function findDominantHue(data: Uint8ClampedArray): number {
  // 10-degree hue buckets: 0, 10, 20, ..., 350
  const buckets: Record<number, number> = {};

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const a = data[i + 3];

    if (a < 128) continue; // transparent — skip

    const [h, s] = rgbToHsl(r, g, b);

    if (s < 48) continue; // desaturated — skip (near-white, near-gray, near-black)

    const bucket = Math.round(h / 10) * 10 % 360;
    buckets[bucket] = (buckets[bucket] ?? 0) + 1;
  }

  if (Object.keys(buckets).length === 0) {
    return 200; // fallback: neutral blue-cyan
  }

  const dominant = Object.entries(buckets)
    .sort(([, countA], [, countB]) => countB - countA)[0];

  return parseInt(dominant[0]);
}
```

### Step 3: RGB to HSL Conversion

The RGBA data from `getImageData` is in the 0–255 range per channel. HSL conversion normalizes these to 0–1, computes the max/min channel, derives the lightness and saturation, and maps the hue to a 0–360 degree value.

```typescript
function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  const rn = r / 255, gn = g / 255, bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const delta = max - min;

  const l = (max + min) / 2;

  if (delta === 0) return [0, 0, l * 100]; // achromatic

  const s = delta / (1 - Math.abs(2 * l - 1));

  let h = 0;
  if (max === rn)      h = ((gn - bn) / delta) % 6;
  else if (max === gn) h = (bn - rn) / delta + 2;
  else                 h = (rn - gn) / delta + 4;

  h = Math.round(h * 60);
  if (h < 0) h += 360;

  return [h, s * 100, l * 100];
}
```

### Step 4: Writing to CSS Variables

Once the dominant hue is found, it is written to the document root as a CSS custom property:

```typescript
document.documentElement.style.setProperty("--primary", dominantColor);
document.documentElement.style.setProperty("--primary-hue", String(hue));
```

All components that use `var(--primary)` — the navbar hover, button gradients, headline text color, section glow effects — update immediately, with no component-level re-renders required.

### Step 5: The Color Store (Canvas 2D Bridge)

CSS variables are not accessible inside `canvas.getContext('2d')` draw calls. A separate mechanism is needed to route the extracted color into the Canvas animation loops (radar rings, sonar pings, particle shimmer).

The solution was a minimal singleton color store:

```typescript
// colorStore.ts
type ColorListener = (hsl: string, hue: number) => void;

const listeners = new Set<ColorListener>();
let currentColor = "hsl(200, 72%, 58%)";
let currentHue = 200;

export const colorStore = {
  get: () => ({ color: currentColor, hue: currentHue }),
  set: (color: string, hue: number) => {
    currentColor = color;
    currentHue = hue;
    listeners.forEach(fn => fn(color, hue));
  },
  subscribe: (fn: ColorListener) => {
    listeners.add(fn);
    return () => listeners.delete(fn); // unsubscribe
  }
};
```

The extractor calls `colorStore.set()` after computing the dominant hue. Canvas animation loops call `colorStore.get()` at the start of each frame. The pub/sub allows listeners to react immediately when the color changes.

---

## Observations

**What worked:**
- The saturation threshold of `s > 48` successfully excluded background noise (the portrait's transparent alpha blended regions, near-black shadows, near-white highlights) while capturing the chromatic subject matter.
- The hue bucketing (10-degree bins) produced a stable dominant hue even for portraits with complex, multi-color backgrounds. The dominant hue was consistent across multiple extraction runs on the same image.
- The 64×64 sample size was sufficient for accurate hue distribution analysis while keeping `getImageData` fast (under 2ms on modern hardware).
- The CSS variable propagation worked transparently — components with `var(--primary)` references updated without any component-level code changes.

**What didn't work initially:**
- **Hot module replacement caching (fixed in `3175353`):** During local development, React's HMR held a stale closure over the previous image's computed color. Subsequent image loads were not triggering re-extraction. Fixed by adding a cleanup in `useEffect` that revokes the image object URL and reinitializes the extractor.
- **CORS on local image loads:** `img.crossOrigin = "anonymous"` was required to call `getImageData` on the loaded image. Without it, Chrome throws a `SecurityError: The canvas has been tainted by cross-origin data` exception. Adding the attribute to the image before setting `src` resolved this.
- **The singleton color store is not testable in isolation:** Because it holds module-level mutable state, unit tests that check Canvas rendering colors have to reset the store between test runs. Marked for replacement with a React context or Zustand slice.

---

## Results

After wiring the extracted color into all downstream consumers, the hero now behaves as follows:

1. Portrait image loads.
2. Extractor runs `getImageData` on the 64×64 offscreen canvas.
3. Dominant hue (e.g., `200°` for a portrait with cool blue tones) is identified.
4. `--primary` is set to `hsl(200, 72%, 58%)` on the document root.
5. Radar rings: stroke color updates to `hsl(200, 72%, 58%)`.
6. Sonar pings: ring expansion color updates.
7. Headline second line: text color updates.
8. Navbar hover state: color updates.
9. Button gradients: `from-[var(--primary)]` updates.
10. Terminal log text: color updates.
11. Particle shimmer: hue center-point updates.

The result is a homepage that genuinely feels cohesive — every glowing, pulsing, highlighted element is tonally related to the portrait, not to an arbitrary design token.

---

## Performance Notes

| Operation | Time (approximate) |
|-----------|-------------------|
| Image load (64×64 draw) | <5ms |
| `getImageData` on 64×64 | <2ms |
| Pixel loop (4,096 pixels) | <1ms |
| CSS variable write | <0.1ms |
| Total extraction pipeline | <10ms |

The entire extraction runs once on component mount. It is not re-run on animation frames. The animation loops read from `colorStore.get()` which is a synchronous object property access — negligible per-frame cost.

There is no perceived jank. The extraction completes before the first animation frame renders at typical portrait image load speeds. On slow connections, the Canvas effects render with the fallback color (`hsl(200, 72%, 58%)`) until the image loads, then transition smoothly.

---

## Pros and Cons

**Pros:**
- Zero designer input required for theming — the color is derived from the actual content.
- Works with any portrait without configuration.
- Propagates to all CSS-variable-consuming components automatically.
- Extraction is fast and runs once.
- The saturation threshold is a single tuneable parameter.

**Cons:**
- Requires a semantically meaningful portrait — a grayscale photo, a photo with poor lighting, or a flat-color illustration may produce a poor dominant hue.
- The singleton color store is not React-idiomatic and complicates testing.
- The fallback (single hardcoded color) is not graduated — a portrait with moderate saturation (between 30 and 48) produces the fallback rather than a degraded-but-correct extraction.
- Cross-origin image loads require `crossOrigin = "anonymous"` and a server that sends appropriate CORS headers.

---

## Conclusion

The experiment succeeded. The hypothesis was correct: deriving the design system color from the portrait pixel data creates a coherence that feels organic rather than applied. The saturation threshold strategy works for typical developer portraits.

The implementation is production-quality on the extraction path. The color store needs to be refactored before the codebase grows further — the singleton pattern will create ordering-sensitive bugs as more components subscribe to it.

---

## Next Experiment

**EXP-10:** Incident report on the asyncio event loop destruction bug encountered during the same session. The investigation process and root cause analysis deserve standalone documentation.

**Planned: EXP-11 — Tiered Saturation Fallback Strategy.** Rather than a hard cutoff at `s > 48`, implement a tiered strategy that progressively lowers the threshold until a minimum number of qualifying pixels is found. Goal: eliminate the abrupt fallback-to-default behavior for portraits with moderate chromatic saturation.

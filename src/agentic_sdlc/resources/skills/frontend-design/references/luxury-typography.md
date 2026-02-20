# God-Tier Luxury Typography

## 1. The "Inter" Standard
For elite engineering tools, **Inter** is the gold standard. It is clean, versatile, and high-performance.
- **Headings**: `font-weight: 700+`, `letter-spacing: -0.04em`.
- **Subheadings**: `font-weight: 400`, `letter-spacing: -0.01em`, `color: var(--slate-400)`.
- **Body**: `font-weight: 400`, `line-height: 1.6`, `color: var(--slate-300)`.

## 2. Dynamic Scaling (The Golden Ratio)
Use a harmonic scale. Never guess pixel sizes.
- **Hero**: `clamp(3.5rem, 8vw, 6rem)`.
- **H2**: `clamp(2rem, 5vw, 3.5rem)`.
- **H3**: `clamp(1.25rem, 3vw, 2rem)`.

## 3. High-Contrast Pairing
Pair a bold Sans-Serif (Inter) with a high-quality Monospace (JetBrains Mono) for technical metadata. This creates a "Pro" feel.

## 4. Visual Balance (Tracking & Leading)
- As font size increases, **decrease** letter-spacing (tracking).
- For long body text, **increase** line-height (leading) for readability.
- Use `text-wrap: balance` for headings to avoid orphans.

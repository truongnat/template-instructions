# Advanced Texturing & Light Shaders

## 1. Digital Grain (The "Physical" Texture)
Pure black/dark backgrounds look flat. Apply a global SVG noise filter to create a premium, printed texture.

```html
<svg style="display:none">
  <filter id="noise">
    <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
    <feColorMatrix type="saturate" values="0" />
  </filter>
</svg>
<div class="fixed inset-0 opacity-[0.03] pointer-events-none" style="filter: url(#noise)"></div>
```

## 2. Mesh Glows (Volumetric Light)
Instead of flat gradients, use multiple overlapping `radial-gradient` circles with massive blur values.
- Primary: Cyan-400 (15% opacity, 120px blur)
- Secondary: Violet-500 (10% opacity, 180px blur)
- Location: Place behind primary CTAs or in corners to create "ambient light".

## 3. The "Glint" Effect
High-end buttons and cards should have a subtle diagonal shine that moves across the surface on hover. This mimics light reflecting off a premium surface.

## 4. SVG Iconography (Lucide/Hero)
Never use emojis in professional UI. Use Lucide SVG icons with:
- `stroke-width: 1.5` or `2`
- Consistent sizing (usually 20px or 24px)
- Lower opacity for neutral icons, primary color for active icons.

## 5. Border Shaders
Use `linear-gradient` borders that transition from `white/10` to `transparent` to create "angled lighting" on panels.

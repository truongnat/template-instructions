# Elite Visual Hierarchy Standards

## 1. The Principle of High Contrast
Don't use "grey" for everything. Use contrast to drive the eye.
- **Primary Action**: High contrast, bright accent color, or absolute white on dark.
- **Secondary**: Muted tones, border-only (ghost), or lower opacity.
- **Tertiary**: Subtle text-only or visible only on hover.

## 2. Spatial Rhythm (The power of 4)
- **Base Unit**: 4px. All margins, padding, and gaps must be `n * 4`.
- **White Space as a Luxury**: Senior design uses *more* whitespace, not less. It makes the content feel premium and "airy".
- **Density Control**: Increase spacing for marketing/hero sections, decrease for dashboard/tool sections.

## 3. Depth & Layering (Z-Axis)
- **Tier 1 (Base)**: The background. Deepest color, subtle mesh gradient.
- **Tier 2 (Panels)**: Glassmorphism (`backdrop-filter: blur()`). Use `border: 1px solid rgba(255,255,255,0.1)` to define edges.
- **Tier 3 (Floating)**: High elevation shadows (`box-shadow: 0 20px 40px rgba(0,0,0,0.5)`). Use for modals and dropdowns.
- **Tier 4 (Accents)**: Neon glows and bloom effects for critical feedback or primary CTAs.

## 4. Typography as Architecture
- **Heading 1**: Large, bold, tracking `-0.02em`, tight line-height.
- **Body**: Medium weight, tracking `0.01em`, generous line-height (`1.6`).
- **Mono**: Use strictly for technical data, code, or terminal simulations.

## 5. The "Bento Grid" Pattern
Organize content into distinct, rounded containers with consistent gaps. Use varied aspect ratios to create visual interest while maintaining a clean vertical/horizontal rhythm.

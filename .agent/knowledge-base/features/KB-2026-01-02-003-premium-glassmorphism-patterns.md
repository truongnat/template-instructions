---
title: Premium Glassmorphism & Framer Motion Patterns
date: 2026-01-02
category: Features
author: "DEV"
tags: [uiux, glassmorphism, framer-motion, react, animations]
---

# Premium Glassmorphism & Framer Motion Patterns

This entry documents the design system and animation patterns used to overhaul the Todo App into a high-end "Focus Hub".

## Core Glassmorphic Design System

### CSS Variables
```css
:root {
  --bg-dark: #0f172a;
  --bg-card: rgba(30, 41, 59, 0.7);
  --primary: #38bdf8;
  --primary-glow: rgba(56, 189, 248, 0.3);
  --border-glass: rgba(255, 255, 255, 0.1);
}
```

### Utility Classes
- `.glass`: Deep backdrop blur (20px+) with semi-transparent background and subtle border.
- `.glass-card`: Interactive card with hover effects and glass aesthetics.
- `.btn-premium`: Glow effects on hover using `box-shadow` and scaling.

## Animation Patterns (Framer Motion)

### Layout Transitions
Using `layout` and `AnimatePresence` with `mode="popLayout"` ensures that items reorder smoothly when filtered or deleted.

```tsx
<AnimatePresence mode="popLayout">
  {items.map(item => (
    <motion.div layout key={item.id}>
      {/* Content */}
    </motion.div>
  ))}
</AnimatePresence>
```

### Entrance Animations
A combination of `y: 20` and `opacity: 0` provides a professional "slide up" feel.

### Interactive Components
- **Animated Checkboxes**: Replacing standard inputs with Lucide icons (Circle -> CheckCircle2) with color transitions.
- **Delete Confirmations**: Inline motion-divs for non-disruptive confirmation flow.

## Implementation Checklist for Future Projects
- [ ] Install `framer-motion` and `lucide-react`.
- [ ] Set deep dark base background `#030712`.
- [ ] Add radial-gradient "orbs" for depth.
- [ ] Ensure all borders use very low opacity (e.g., `border-white/5`).
- [ ] Use `backdrop-blur-xl` for premium glass depth.

# Agentic SDLC Landing Page - Design Guide

**Version:** 1.0  
**Created:** 2026-01-03  
**Design System Owner:** @UIUX  
**Design Philosophy:** Premium • Accessible • Performance-First

---

## 🎨 Design Philosophy

The Agentic SDLC landing page embodies three core principles:

1. **Premium Aesthetics**: Cutting-edge design that positions Agentic SDLC as a professional, production-ready framework
2. **Accessibility First**: WCAG 2.1 AA compliance ensures everyone can experience our product
3. **Performance-Optimized**: Beautiful design that loads fast and feels responsive

### Visual Language
- **AI-Inspired**: Neural network patterns, data flow animations, intelligent color gradients
- **Glassmorphism**: Modern, layered depth with backdrop blur effects
- **Dynamic Motion**: Smooth, purposeful animations that guide user attention
- **Premium Polish**: High-quality gradients, subtle shadows, refined typography

---

## 🌈 Color System

### Primary Palette

```css
/* Brand Colors */
--blue-600:   #2563EB   /* Primary CTA, links */
--blue-500:   #3B82F6   /* Hover states, accents */
--blue-400:   #60A5FA   /* Light accents, gradients */
--purple-600: #8B5CF6   /* Secondary brand color */
--purple-500: #A855F7   /* Gradient transitions */
--purple-400: #C084FC   /* Light purple accents */
--pink-600:   #DB2777   /* Accent highlights */
--pink-500:   #EC4899   /* Gradient endpoints */
--pink-400:   #F472B6   /* Light pink accents */
```

### Background Layers

```css
/* Dark Theme Foundation */
--slate-950:  #0F172A   /* Primary background */
--slate-900:  #020617   /* Secondary background */
--slate-800:  #1E293B   /* Elevated surfaces */
--gray-900:   #111827   /* Code blocks, terminals */

/* Glass Surfaces */
--glass-light: rgba(255, 255, 255, 0.08)  /* Light glass */
--glass-dark:  rgba(255, 255, 255, 0.03)  /* Dark glass */
--glass-border: rgba(255, 255, 255, 0.10) /* Glass borders */
```

### Text Colors

```css
/* Content Hierarchy */
--text-primary:   #FFFFFF           /* Headlines, important text */
--text-secondary: rgba(255, 255, 255, 0.90)  /* Body text */
--text-tertiary:  rgba(255, 255, 255, 0.70)  /* Muted text */
--text-disabled:  rgba(255, 255, 255, 0.40)  /* Disabled states */

/* Semantic Colors */
--text-success:   #4EC9B0   /* Success messages, checkmarks */
--text-info:      #569CD6   /* Info messages, links */
--text-warning:   #DCDCAA   /* Warnings, alerts */
--text-error:     #F48771   /* Errors, critical info */
```

### Gradient Definitions

```css
/* Primary Gradient (CTAs, Hero) */
.gradient-primary {
  background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 50%, #EC4899 100%);
}

/* Glass Gradient (Backgrounds) */
.gradient-glass {
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.08) 0%, 
    rgba(255, 255, 255, 0.03) 100%
  );
}

/* Text Gradient (Headings) */
.gradient-text {
  background: linear-gradient(90deg, #60A5FA 0%, #A855F7 50%, #F472B6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Animated Gradient (Hero Background) */
.gradient-animated {
  background: linear-gradient(270deg, 
    rgba(99, 102, 241, 0.15),
    rgba(168, 85, 247, 0.15),
    rgba(236, 72, 153, 0.15)
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}
```

### Color Usage Guidelines

| Context | Color | Usage |
|---------|-------|-------|
| **Primary CTA** | Blue 600 → Purple 600 gradient | Main action buttons |
| **Secondary CTA** | White/10 border + backdrop blur | Ghost buttons |
| **Hero Title** | White (solid) | Maximum contrast |
| **Hero Subtitle** | Blue 400 → Pink 400 gradient | Eye-catching accent |
| **Body Text** | White/90 | Readable, comfortable |
| **Success Icons** | Teal (#4EC9B0) | Checkmarks, confirmations |
| **Code Syntax** | JetBrains Mono colors | Terminal demos |

---

## 📝 Typography

### Font Families

```css
/* UI & Content */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Code & Technical */
--font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

### Type Scale (Fluid, Responsive)

```css
/* Headlines */
.hero-title {
  font-size: clamp(2.5rem, 8vw, 6rem);     /* 40px → 96px */
  line-height: 1.1;
  letter-spacing: -0.02em;
  font-weight: 900;
}

.section-title {
  font-size: clamp(2rem, 5vw, 3.5rem);     /* 32px → 56px */
  line-height: 1.2;
  letter-spacing: -0.01em;
  font-weight: 800;
}

.subsection-title {
  font-size: clamp(1.5rem, 3vw, 2rem);     /* 24px → 32px */
  line-height: 1.3;
  font-weight: 700;
}

/* Body Text */
.body-large {
  font-size: clamp(1.125rem, 2vw, 1.5rem); /* 18px → 24px */
  line-height: 1.6;
  font-weight: 400;
}

.body-regular {
  font-size: 1rem;                          /* 16px */
  line-height: 1.7;
  font-weight: 400;
}

.body-small {
  font-size: 0.875rem;                      /* 14px */
  line-height: 1.5;
  font-weight: 400;
}

/* UI Elements */
.button-text {
  font-size: 1.125rem;                      /* 18px */
  font-weight: 700;
  letter-spacing: 0.01em;
}

.caption {
  font-size: 0.75rem;                       /* 12px */
  line-height: 1.4;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, descriptions |
| Medium | 500 | UI labels, captions |
| Semibold | 600 | Subheadings, emphasis |
| Bold | 700 | Buttons, important text |
| Extrabold | 800 | Section titles |
| Black | 900 | Hero headlines |

---

## 📏 Spacing System

### Base Unit: 4px (0.25rem)

```css
/* Spacing Scale (Tailwind-based) */
--space-1:  0.25rem   /*  4px */
--space-2:  0.5rem    /*  8px */
--space-3:  0.75rem   /* 12px */
--space-4:  1rem      /* 16px */
--space-5:  1.25rem   /* 20px */
--space-6:  1.5rem    /* 24px */
--space-8:  2rem      /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
--space-32: 8rem      /* 128px */
```

### Component Spacing

| Element | Padding | Margin | Gap |
|---------|---------|--------|-----|
| **Section** | 4rem top/bottom | - | - |
| **Container** | 1.5rem inline (mobile) | - | - |
| **Container** | 2rem inline (desktop) | - | - |
| **Card** | 2rem (32px) | - | - |
| **Button** | 1rem × 2rem | - | - |
| **Heading** | - | 2-3rem bottom | - |
| **Paragraph** | - | 1.5rem bottom | - |
| **Grid** | - | - | 2rem (32px) |

---

## 🧩 Component Library

### 1. Glass Card

Premium glassmorphism card with shimmer effect.

```astro
<div class="glass-card">
  <h3>Card Title</h3>
  <p>Card content goes here...</p>
</div>
```

**Styles:**
```css
.glass-card {
  backdrop-filter: blur(24px);
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.08),
    rgba(255, 255, 255, 0.03)
  );
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 1.5rem;
  padding: 2rem;
  
  /* Shadow depth */
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 2px 8px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.12),
    rgba(255, 255, 255, 0.06)
  );
  border-color: rgba(255, 255, 255, 0.20);
  transform: translateY(-8px) scale(1.02);
  box-shadow:
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(99, 102, 241, 0.2);
}
```

---

### 2. Primary Button

Animated gradient button with shimmer and glow effects.

```astro
<a href="#action" class="btn-primary">
  <svg><!-- Icon --></svg>
  Get Started
  <svg><!-- Arrow --></svg>
</a>
```

**Styles:**
```css
.btn-primary {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  
  padding: 1.25rem 2.5rem;
  min-height: 44px;
  
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  
  background: linear-gradient(90deg, #2563EB, #8B5CF6, #DB2777);
  background-size: 200% 100%;
  border-radius: 1rem;
  
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.btn-primary:hover {
  transform: scale(1.05);
  background-position: 100% 0;
  box-shadow: 0 0 40px rgba(99, 102, 241, 0.6);
}

/* Shimmer effect */
.btn-primary::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.2), 
    transparent
  );
  transform: translateX(-100%);
  transition: transform 1s;
}

.btn-primary:hover::before {
  transform: translateX(100%);
}
```

---

### 3. Terminal Window

Interactive code demonstration component.

```astro
<TerminalDemo />
```

**Features:**
- macOS-style window chrome (red/yellow/green buttons)
- Typewriter animation for commands
- Syntax highlighting (commands, output, success/error)
- Blinking cursor effect
- Auto-loop demonstration

**Color Scheme:**
```css
/* VS Code Dark+ inspired */
.cmd { color: #9cdcfe; }      /* Light Blue - commands */
.arg { color: #ce9178; }      /* Orange - arguments */
.flag { color: #dcdcaa; }     /* Yellow - flags */
.success { color: #4ec9b0; }  /* Teal - success */
.info { color: #569cd6; }     /* Blue - info */
.comment { color: #6a9955; }  /* Green - comments */
.prompt { color: #c586c0; }   /* Purple - $ prompt */
```

---

### 4. Gradient Text

Eye-catching animated gradient for headlines.

```astro
<h1 class="gradient-text">Agentic SDLC</h1>
```

**Styles:**
```css
.gradient-text {
  background: linear-gradient(90deg, #60A5FA, #A855F7, #F472B6);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}
```

---

## 🎭 Animation System

### Entrance Animations

```css
/* Slide Up */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.animate-slide-up {
  animation: slideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* Fade In */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

/* Scale In */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-scale-in {
  animation: scaleIn 0.5s ease-out forwards;
}
```

### Continuous Animations

```css
/* Float (Orbs, particles) */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.animate-float {
  animation: float 6s ease-in-out infinite;
}

/* Glow Pulse */
@keyframes glowPulse {
  0%, 100% {
    opacity: 1;
    filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.5));
  }
  50% {
    opacity: 0.8;
    filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.8));
  }
}
.animate-glow-pulse {
  animation: glowPulse 3s ease-in-out infinite;
}

/* Gradient Shift */
@keyframes gradientX {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
.animate-gradient-x {
  background-size: 200% 200%;
  animation: gradientX 15s ease infinite;
}
```

### Brain-Specific Animations

```css
/* Neural Pulse (Brain nodes) */
@keyframes neuralPulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
}

/* Data Flow (Connection lines) */
@keyframes dataFlow {
  0% {
    stroke-dashoffset: 100;
    opacity: 0;
  }
  20%, 80% {
    opacity: 1;
  }
  100% {
    stroke-dashoffset: 0;
    opacity: 0;
  }
}

/* Connection Glow */
@keyframes connectionGlow {
  0%, 100% {
    filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4));
    stroke-opacity: 0.4;
  }
  50% {
    filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.8));
    stroke-opacity: 0.8;
  }
}
```

### Animation Timing

| Animation Type | Duration | Easing | Use Case |
|----------------|----------|--------|----------|
| **Micro** | 150-300ms | ease-out | Hover, focus states |
| **Short** | 500-600ms | cubic-bezier | Entrance, transitions |
| **Medium** | 800-1000ms | ease-in-out | Fades, slides |
| **Long** | 2-4s | ease-in-out | Continuous loops |
| **Ambient** | 8-15s | linear/ease | Background gradients |

### Animation Performance

```css
/* GPU-accelerated properties (use these) */
- transform: translate(), scale(), rotate()
- opacity
- filter: blur(), drop-shadow()

/* Avoid animating (causes repaints) */
- width, height
- top, left, right, bottom (use transform instead)
- margin, padding
- background-color (use opacity or gradients)
```

---

## 🖼️ Iconography

### Icon System
- **Source**: Lucide React (tree-shakeable)
- **Size Scale**: 16px, 20px, 24px, 32px, 48px
- **Stroke Width**: 2px (consistent)
- **Style**: Outline (not filled)

### Icon Usage

```tsx
import { Zap, Play, Github } from 'lucide-react';

<Zap className="w-6 h-6 text-blue-400" />
<Play className="w-5 h-5" />
<Github className="w-8 h-8" />
```

### Common Icons

| Icon | Use Case | Context |
|------|----------|---------|
| ⚡ Zap | Speed, performance | CTAs, features |
| ▶ Play | Demo, video | Video triggers |
| 🔗 Link | External links | Navigation |
| ✓ Check | Success, completed | Feature lists, confirmations |
| 🧠 Brain | AI, intelligence | Brain architecture |
| 🤖 Robot | AI agents | Agent showcase |
| 📊 Chart | Analytics, metrics | GitHub stats |
| 🚀 Rocket | Launch, deploy | Quick start |

---

## 📐 Layout Grid

### Container System

```css
.section-container {
  max-width: 80rem;        /* 1280px */
  margin: 0 auto;
  padding: 4rem 1.5rem;    /* Mobile */
}

@media (min-width: 640px) {
  .section-container {
    padding: 6rem 2rem;    /* Tablet */
  }
}

@media (min-width: 1024px) {
  .section-container {
    padding: 6rem 2rem;    /* Desktop */
  }
}
```

### Grid Systems

```css
/* 2-Column Grid (Features) */
.grid-2col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

/* 3-Column Grid (Use Cases) */
.grid-3col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

/* 4-Column Grid (Icons, Stats) */
.grid-4col {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}
```

---

## ♿ Accessibility Guidelines

### Focus States

```css
*:focus-visible {
  outline: 3px solid #60A5FA;  /* Blue-400 */
  outline-offset: 2px;
  border-radius: 0.5rem;
}

/* Button-specific */
.btn-primary:focus-visible,
.btn-secondary:focus-visible {
  outline-offset: 3px;
}
```

### Skip Link

```css
.skip-to-main {
  @apply sr-only;
  
  /* Visible when focused */
  @apply focus:not-sr-only;
  @apply focus:absolute focus:top-4 focus:left-4 focus:z-[100];
  @apply focus:px-6 focus:py-3;
  @apply focus:bg-blue-600 focus:text-white focus:rounded-xl;
  @apply focus:font-bold focus:shadow-glow-lg;
}
```

### Color Contrast

All text meets WCAG AA standards:
- **Large text (24px+)**: Minimum 3:1 contrast ratio
- **Normal text (16-24px)**: Minimum 4.5:1 contrast ratio
- **Interactive elements**: Minimum 3:1 contrast ratio

### Motion Preferences

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  
  /* Disable expensive animations */
  .animate-float,
  .animate-glow-pulse,
  .gradient-mesh {
    animation: none;
  }
}
```

---

## 📱 Responsive Design

### Mobile-First Strategy

1. **Base styles**: Mobile (0-639px)
2. **Tablet portrait**: sm: 640px+
3. **Tablet landscape**: md: 768px+
4. **Desktop**: lg: 1024px+
5. **Large desktop**: xl: 1280px+

### Touch Targets

```css
/* Minimum 44x44px touch targets (iOS HIG) */
.btn-primary,
.btn-secondary {
  min-height: 44px;
  min-width: 44px;
  padding: 1rem 2rem;
}
```

### Typography Scaling

```css
/* Fluid typography with clamp() */
.hero-title {
  font-size: clamp(2.5rem, 8vw, 6rem);
}

.section-title {
  font-size: clamp(2rem, 5vw, 3.5rem);
}

.body-large {
  font-size: clamp(1.125rem, 2vw, 1.5rem);
}
```

---

## 🎯 Design Tokens (CSS Variables)

```css
:root {
  /* Colors */
  --color-primary: #3B82F6;
  --color-secondary: #8B5CF6;
  --color-accent: #EC4899;
  
  /* Spacing */
  --space-unit: 0.25rem;
  --space-section: 6rem;
  --space-container: 2rem;
  
  /* Typography */
  --font-primary: 'Inter', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Borders */
  --border-radius-sm: 0.5rem;
  --border-radius-md: 1rem;
  --border-radius-lg: 1.5rem;
  --border-radius-xl: 2rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
  --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.4);
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 📚 Design Resources

### Figma Files
- **Landing Page Design**: [Link to Figma]
- **Component Library**: [Link to Figma]
- **Icon Set**: Lucide icons

### Inspiration Sources
- **Vercel**: Premium dark mode, glassmorphism
- **Linear**: Clean typography, micro-animations
- **Airbnb**: Accessibility best practices
- **Stripe**: Clear content hierarchy

### Tools Used
- **Figma**: UI design and prototyping
- **Coolors**: Color palette generation
- **contrast-ratio.com**: WCAG contrast checking
- **Google Fonts**: Typography selection

---

## ✅ Design Checklist

Before shipping a new component:

- [ ] Follows color system (no hard-coded colors)
- [ ] Uses spacing tokens (no random margins/paddings)
- [ ] Typography scale compliance
- [ ] Mobile responsive (tested 320px - 1920px)
- [ ] Focus states defined
- [ ] Hover/active states smooth
- [ ] Animations respect `prefers-reduced-motion`
- [ ] WCAG AA contrast ratios
- [ ] Touch targets ≥44x44px
- [ ] Semantic HTML used
- [ ] ARIA labels where needed
- [ ] Works with keyboard navigation
- [ ] Screen reader tested

---

**Maintained by:** @UIUX  
**Last Updated:** 2026-01-03T11:43:32+07:00  
**Status:** Living Document

*This design guide is synced with the Agentic SDLC Brain system for semantic search and AI-assisted design decisions.*

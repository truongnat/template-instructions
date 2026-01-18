# UI/UX Design Specification - Version [X]

## Document Info
| Field | Value |
|-------|-------|
| Version | [X.0] |
| Date | [YYYY-MM-DD] |
| Author | @UIUX |
| Platform | Web / Mobile (iOS/Android) / Desktop / Embedded / CLI |
| Status | Draft / Review / Approved |

---

## 1. Design Overview
**Target Users:** [Primary user personas]
**Platform:** [Web/Mobile/Desktop/Embedded/CLI]
**Design Goals:** [Key objectives]

---

## 2. User Personas

### Persona 1: [Name]
| Attribute | Details |
|-----------|---------|
| Role | [e.g., End User, Admin, Developer] |
| Age Range | [e.g., 25-40] |
| Goals | [What they want to achieve] |
| Pain Points | [Current frustrations] |
| Tech Savviness | Low / Medium / High |
| Platform Usage | [Desktop/Mobile/Both] |

---

## 3. User Flows

### Flow 1: [Primary User Journey]
```
┌──────────┐    ┌───────────────┐    ┌─────────────┐
│  Entry   │───▶│   Action      │───▶│   Result    │
│  Point   │    │               │    │             │
└──────────┘    └───────┬───────┘    └─────────────┘
                        │
                        ▼ (Error)
                ┌───────────────┐
                │ Error Handling│
                └───────────────┘
```

### Flow 2: [Secondary Journey]
[Add flow diagrams for key user journeys]

---

## 4. Screen/Interface Specifications

### 4.1 [Screen/View Name]

**Layout (for GUI platforms):**
```
┌────────────────────────────────────────┐
│              [Header/Nav]              │
├────────────────────────────────────────┤
│  ┌──────────────────────────────────┐  │
│  │          Main Content            │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │ Component 1                │  │  │
│  │  └────────────────────────────┘  │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │ Component 2                │  │  │
│  │  └────────────────────────────┘  │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

**Command Structure (for CLI):**
```bash
# Command syntax
tool-name <command> [options]

# Interactive prompts
? Select option: (Use arrow keys)
  ❯ Option 1
    Option 2
    Option 3

# Output format
✓ Success message
✗ Error message
```

**Specifications:**
| Element | Specification |
|---------|---------------|
| Container | [Size, padding, margins] |
| Typography | [Font, size, weight] |
| Colors | [Primary, secondary, etc.] |
| Spacing | [Grid system] |
| Interactive Elements | [Buttons, inputs, etc.] |

**States:**
- Default: [Description]
- Hover/Focus: [Description]
- Active: [Description]
- Disabled: [Description]
- Loading: [Description]
- Error: [Description]

**Platform-Specific Notes:**
- **Mobile:** Touch targets ≥ 44x44px, swipe gestures
- **Desktop:** Keyboard shortcuts, window management
- **CLI:** Color support, progress indicators
- **Embedded:** Display constraints, button mapping

---

## 5. Design System

### 5.1 Color Palette

| Token | Hex/RGB | Usage | Accessibility |
|-------|---------|-------|---------------|
| `--color-primary` | #0066FF | CTAs, links | WCAG AA ✓ |
| `--color-secondary` | #6B7280 | Secondary text | WCAG AA ✓ |
| `--color-success` | #10B981 | Success states | WCAG AA ✓ |
| `--color-warning` | #F59E0B | Warnings | WCAG AA ✓ |
| `--color-error` | #EF4444 | Errors | WCAG AA ✓ |
| `--color-bg` | #F9FAFB | Background | - |
| `--color-text` | #111827 | Primary text | WCAG AAA ✓ |

### 5.2 Typography

| Token | Font | Size | Weight | Line Height | Usage |
|-------|------|------|--------|-------------|-------|
| `--font-h1` | [Font] | 32px | 700 | 1.2 | Page titles |
| `--font-h2` | [Font] | 24px | 600 | 1.3 | Section headers |
| `--font-body` | [Font] | 16px | 400 | 1.5 | Body text |
| `--font-small` | [Font] | 14px | 400 | 1.4 | Captions |
| `--font-mono` | [Mono] | 14px | 400 | 1.5 | Code, CLI output |

### 5.3 Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 4px | Tight spacing |
| `--space-sm` | 8px | Component padding |
| `--space-md` | 16px | Card padding |
| `--space-lg` | 24px | Section gaps |
| `--space-xl` | 32px | Page margins |

### 5.4 Component Library

| Component | Variants | States | Platform Notes |
|-----------|----------|--------|----------------|
| Button | Primary, Secondary, Ghost | Default, Hover, Active, Disabled | Touch-friendly on mobile |
| Input | Text, Password, Number | Default, Focus, Error, Disabled | Auto-complete support |
| Card | Default, Elevated, Outlined | Default, Hover | Swipeable on mobile |
| Modal | Small, Medium, Large | Open, Closing | Full-screen on mobile |
| Progress | Linear, Circular, Spinner | Indeterminate, Determinate | CLI: ASCII progress bar |

---

## 6. Responsive/Adaptive Design

### 6.1 Breakpoints (for Web/Desktop)
| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Mobile | < 768px | Single column, bottom nav |
| Tablet | 768-1024px | 2 columns, side nav |
| Desktop | > 1024px | 3 columns, full nav |

### 6.2 Platform Adaptations
- **iOS:** Native navigation patterns, SF Symbols
- **Android:** Material Design 3, FAB patterns
- **Desktop:** Menu bar, keyboard shortcuts
- **CLI:** Terminal width detection, color support check

---

## 7. Interactions & Animations

| Interaction | Animation | Duration | Platform |
|-------------|-----------|----------|----------|
| Button press | Scale 0.98 | 100ms | GUI |
| Modal open | Fade + slide | 200ms | GUI |
| Page transition | Fade | 300ms | GUI |
| Loading | Spinner/Progress | Continuous | All |
| CLI command | Typing effect | 50ms/char | CLI |

**Animation Principles:**
- Respect user motion preferences (prefers-reduced-motion)
- No animations on low-power devices (when applicable)
- Smooth 60fps animations

---

## 8. Accessibility Checklist

### Visual Accessibility
- [ ] Color contrast ≥ 4.5:1 (WCAG AA)
- [ ] Text resizable up to 200%
- [ ] No information conveyed by color alone
- [ ] Focus indicators visible on all interactive elements

### Keyboard & Navigation
- [ ] All functionality accessible via keyboard
- [ ] Logical tab order
- [ ] Skip navigation links (web)
- [ ] Keyboard shortcuts documented

### Screen Reader Support
- [ ] All images have alt text
- [ ] Form labels properly associated
- [ ] ARIA labels where needed
- [ ] Semantic HTML structure

### Platform-Specific
- [ ] **Mobile:** VoiceOver/TalkBack tested
- [ ] **Desktop:** Screen reader compatible
- [ ] **CLI:** Screen reader friendly output

---

## 9. Platform Guidelines Compliance

### iOS (if applicable)
- [ ] Human Interface Guidelines followed
- [ ] SF Symbols used appropriately
- [ ] Native navigation patterns
- [ ] Dark mode support

### Android (if applicable)
- [ ] Material Design 3 guidelines
- [ ] Adaptive icons
- [ ] System navigation support
- [ ] Dynamic color support

### Web (if applicable)
- [ ] Progressive enhancement
- [ ] Cross-browser compatibility
- [ ] Responsive design
- [ ] PWA capabilities (if needed)

---

## 10. Assets & Resources

### Required Assets
| Asset | Format | Size | Notes |
|-------|--------|------|-------|
| App Icon | PNG/SVG | [sizes] | Multiple resolutions |
| Logo | SVG | Scalable | Light/dark variants |
| Illustrations | SVG/PNG | Various | Optimized |
| Icons | SVG | 24x24 | Icon set |

### Design Files
- Figma/Sketch file: [Link]
- Component library: [Link]
- Style guide: [Link]

---

## 11. Open Questions
- [ ] @SA: [Technical feasibility question]
- [ ] @PO: [Business requirement clarification]
- [ ] @DEV: [Implementation complexity question]

---

## 12. Conclusion & Next Step

Design complete and ready for review.

### Next Step:
- @SA - Confirm system design supports UI requirements
- @QA - Review for usability and testability
- @SECA - Security review of user flows and data handling
- @PO - Validate against acceptance criteria

#uiux-design #designing

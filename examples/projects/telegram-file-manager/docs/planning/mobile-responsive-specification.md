# 📱 Mobile Responsive Telegram File Manager - Specification

> **Version:** 1.0.0  
> **Created:** 2026-01-09  
> **Status:** Planning  
> **Author:** @UIUX, @DEV

---

## 📋 Executive Summary

This specification outlines the plan to make the **Telegram File Manager** fully responsive for mobile devices. The current desktop-first design requires significant enhancements to provide an optimal mobile user experience, including touch-friendly interactions, adaptive layouts, and mobile-specific navigation patterns.

---

## 🎯 Goals & Objectives

### Primary Goals
1. **Mobile-First Experience** - Redesign layouts to work seamlessly on screens 320px - 768px
2. **Touch-Optimized Interactions** - Larger touch targets, swipe gestures, haptic feedback
3. **Efficient Navigation** - Bottom navigation bar, slide-out sidebar, contextual actions
4. **Performance Optimization** - Reduced bundle size, lazy loading, optimized images

### Success Metrics
| Metric | Target |
|--------|--------|
| Lighthouse Mobile Score | ≥ 90 |
| First Contentful Paint | < 1.5s |
| Touch Target Size | ≥ 44px × 44px |
| Mobile Usability | 100% on Google Mobile Test |

---

## 📐 Breakpoint Strategy

```
┌──────────────────────────────────────────────────────────────────┐
│                        BREAKPOINT SYSTEM                         │
├──────────────┬───────────────┬───────────────────────────────────┤
│ Name         │ Width         │ Layout                            │
├──────────────┼───────────────┼───────────────────────────────────┤
│ xs (mobile)  │ < 480px       │ Single column, bottom nav         │
│ sm (mobile+) │ 480px - 639px │ Single column, compact cards      │
│ md (tablet)  │ 640px - 767px │ 2-column grid, collapsible sidebar│
│ lg (tablet+) │ 768px - 1023px│ 3-column grid, mini sidebar      │
│ xl (desktop) │ ≥ 1024px      │ Current layout (unchanged)        │
└──────────────┴───────────────┴───────────────────────────────────┘
```

---

## 🏗️ Component Architecture

### 1. App Layout - Mobile Adaptation

**Current State:**
```
┌─────────────────────────────────────────────────────────────┐
│  Sidebar (fixed 16rem)  │  Header (fixed top)               │
│                         ├──────────────────────────────────│
│                         │  FileGrid (scrollable)            │
└─────────────────────────┴──────────────────────────────────┘
```

**Mobile Layout (< 768px):**
```
┌───────────────────────────────────────┐
│  Header (compact, searchable)         │
├───────────────────────────────────────┤
│                                       │
│          FileGrid                     │
│       (full width, 2-col)             │
│                                       │
├───────────────────────────────────────┤
│  BottomNav [Home|Files|Fav|Settings]  │
└───────────────────────────────────────┘

Sidebar → Slide-out drawer (left)
```

### 2. New Components Required

| Component | Purpose | Priority |
|-----------|---------|----------|
| `MobileNav.tsx` | Bottom navigation bar | P0 |
| `MobileHeader.tsx` | Compact header with hamburger menu | P0 |
| `SwipeableDrawer.tsx` | Slide-out sidebar for mobile | P0 |
| `MobileFileCard.tsx` | Touch-optimized file card | P1 |
| `MobileActionSheet.tsx` | iOS-style action menu | P1 |
| `PullToRefresh.tsx` | Pull-down refresh gesture | P2 |
| `SwipeableFileRow.tsx` | Swipe to reveal actions | P2 |

### 3. Responsive Hook

```typescript
// hooks/useResponsive.ts
export function useResponsive() {
  const [breakpoint, setBreakpoint] = useState<'xs' | 'sm' | 'md' | 'lg' | 'xl'>('xl');
  const isMobile = breakpoint === 'xs' || breakpoint === 'sm';
  const isTablet = breakpoint === 'md' || breakpoint === 'lg';
  const isDesktop = breakpoint === 'xl';
  
  return { breakpoint, isMobile, isTablet, isDesktop };
}
```

---

## 📱 Mobile Components Design

### 1. Bottom Navigation Bar

```
┌───────────────────────────────────────────────────┐
│  🏠 Home   │  📁 Files  │  ⭐ Favorite │  ⚙️ More │
│  (active)  │            │              │          │
└───────────────────────────────────────────────────┘
```

**Design Specs:**
- Height: 64px (safe area aware)
- Background: Glassmorphism with blur
- Icons: 24px with labels
- Active indicator: Gradient pill background
- Haptic: Light tap feedback

### 2. Mobile Header

```
┌────────────────────────────────────────────────────┐
│  ☰  │  TeleCloud         │  🔍  │  ⬆️ Upload      │
└────────────────────────────────────────────────────┘
```

**Features:**
- Hamburger menu (opens drawer)
- Compact title
- Search icon (expands to full-width search)
- Upload FAB or icon button

### 3. Swipeable Drawer

```
Closed:                         Open:
┌─────────────────┐            ┌────────────────────────────────┐
│     Content     │  ←swipe→   │ Sidebar │      Content         │
│                 │            │  80%    │   (dimmed overlay)   │
└─────────────────┘            └────────────────────────────────┘
```

**Gesture Specs:**
- Open: Swipe right from left edge (first 20px)
- Close: Swipe left or tap overlay
- Width: 80% of screen (max 320px)
- Animation: spring physics

### 4. Mobile File Card

```
Grid Mode (2-col):                    List Mode:
┌─────────────────────┐              ┌──────────────────────────────────┐
│  ┌─────────────────┐│              │ [📄] photo.jpg         [⋮]      │
│  │                 ││              │      2.5 MB · 2 min ago         │
│  │    Thumbnail    ││              └──────────────────────────────────┘
│  │                 ││
│  └─────────────────┘│
│  photo.jpg     [⋮]  │
│  2.5 MB             │
└─────────────────────┘
```

**Touch Specs:**
- Long press: Select mode / Multi-select
- Single tap: Preview
- Swipe left: Quick actions (delete, share)
- More button [⋮]: Action sheet

### 5. Action Sheet (iOS-style)

```
┌────────────────────────────────────────────┐
│           photo.jpg                        │
│           2.5 MB · PNG                     │
├────────────────────────────────────────────┤
│  📥 Download                               │
│  🔗 Share                                  │
│  ⭐ Add to Favorites                       │
│  📁 Move to Folder                         │
│  ✏️ Rename                                 │
├────────────────────────────────────────────┤
│  🗑️ Delete                    (red)        │
├────────────────────────────────────────────┤
│              Cancel                        │
└────────────────────────────────────────────┘
```

---

## 🎨 CSS Responsive Updates

### New CSS Variables

```css
@theme {
  /* Mobile spacing */
  --spacing-safe-bottom: env(safe-area-inset-bottom);
  --spacing-safe-top: env(safe-area-inset-top);
  
  /* Touch targets */
  --touch-target-min: 44px;
  --touch-target-comfortable: 48px;
  
  /* Mobile nav height */
  --nav-height-mobile: 64px;
  --header-height-mobile: 56px;
}
```

### Mobile-Specific Utilities

```css
/* Mobile-only utilities */
@media (max-width: 767px) {
  .mobile-only { display: block; }
  .desktop-only { display: none; }
  
  .touch-target {
    min-height: var(--touch-target-min);
    min-width: var(--touch-target-min);
  }
  
  .safe-area-bottom {
    padding-bottom: calc(var(--nav-height-mobile) + var(--spacing-safe-bottom));
  }
}

@media (min-width: 768px) {
  .mobile-only { display: none; }
  .desktop-only { display: block; }
}
```

---

## 🔄 State Management Updates

### Settings Store Additions

```typescript
interface SettingsState {
  // Existing...
  
  // Mobile-specific
  mobileNavVisible: boolean;
  drawerOpen: boolean;
  actionSheetFile: TelegramFile | null;
  isSearchExpanded: boolean;
  
  // Actions
  toggleDrawer: () => void;
  openActionSheet: (file: TelegramFile) => void;
  closeActionSheet: () => void;
  toggleMobileSearch: () => void;
}
```

---

## 📋 Implementation Plan

### Phase 1: Foundation (Priority: P0) 🎯
| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Create `useResponsive` hook | 2h |
| 1.2 | Add mobile breakpoint CSS utilities | 2h |
| 1.3 | Create `MobileNav` component | 4h |
| 1.4 | Create `MobileHeader` component | 3h |
| 1.5 | Create `SwipeableDrawer` component | 4h |
| 1.6 | Update `App.tsx` with responsive layout | 4h |

### Phase 2: Components (Priority: P1) 📦
| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Create `MobileFileCard` component | 4h |
| 2.2 | Create `MobileActionSheet` component | 3h |
| 2.3 | Update `FileGrid` for mobile grid (2-col) | 2h |
| 2.4 | Make `PreviewModal` full-screen on mobile | 2h |
| 2.5 | Make `SettingsDialog` full-screen on mobile | 2h |

### Phase 3: Gestures (Priority: P2) 👆
| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Add swipe gestures to file cards | 4h |
| 3.2 | Implement `PullToRefresh` component | 3h |
| 3.3 | Add long-press multi-select | 3h |
| 3.4 | Haptic feedback integration | 2h |

### Phase 4: Polish (Priority: P3) ✨
| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Performance optimization (lazy loading) | 4h |
| 4.2 | Lighthouse audit & fixes | 3h |
| 4.3 | Cross-device testing | 4h |
| 4.4 | Documentation | 2h |

**Total Estimated Effort:** ~57 hours

---

## 🎭 UI/UX Mockup References

### Mobile Home Screen
```
┌─────────────────────────────────────────┐
│ ☰  TeleCloud              🔍  ⬆️       │ ← Header (56px)
├─────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐        │
│ │             │ │             │        │
│ │   Image 1   │ │   Image 2   │        │ ← 2-column grid
│ │             │ │             │        │
│ │ photo.jpg   │ │ doc.pdf     │        │
│ └─────────────┘ └─────────────┘        │
│ ┌─────────────┐ ┌─────────────┐        │
│ │             │ │             │        │
│ │   Video 1   │ │   Music 1   │        │
│ │             │ │             │        │
│ │ video.mp4   │ │ song.mp3    │        │
│ └─────────────┘ └─────────────┘        │
│                                         │
│                                         │
├─────────────────────────────────────────┤
│ 🏠 Home  │ 📁 Files │ ⭐ Fav │ ⚙️ More  │ ← Bottom Nav (64px + safe area)
└─────────────────────────────────────────┘
```

### Drawer Open
```
┌─────────────────────────────────────────┐
│ ┌───────────────────┐ ░░░░░░░░░░░░░░░░░│
│ │ 🔵 TeleCloud      │ ░░░░░░░░░░░░░░░░░│
│ ├───────────────────┤ ░░░░░░░░░░░░░░░░░│
│ │ 📁 All Files   42 │ ░░░ (dimmed) ░░░░│
│ │ 🖼️ Photos      18 │ ░░░░░░░░░░░░░░░░░│
│ │ 🎬 Videos       8 │ ░░░░░░░░░░░░░░░░░│
│ │ 📄 Documents   12 │ ░░░░░░░░░░░░░░░░░│
│ │ 🎵 Music        4 │ ░░░░░░░░░░░░░░░░░│
│ ├───────────────────┤ ░░░░░░░░░░░░░░░░░│
│ │ ⭐ Favorites    5 │ ░░░░░░░░░░░░░░░░░│
│ │ 🗑️ Trash        2 │ ░░░░░░░░░░░░░░░░░│
│ ├───────────────────┤ ░░░░░░░░░░░░░░░░░│
│ │ Storage: 2.5 GB   │ ░░░░░░░░░░░░░░░░░│
│ │ ■■■■■■□□□□ 25%   │ ░░░░░░░░░░░░░░░░░│
│ └───────────────────┘ ░░░░░░░░░░░░░░░░░│
├─────────────────────────────────────────┤
│ 🏠 Home  │ 📁 Files │ ⭐ Fav │ ⚙️ More  │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing Strategy

### Device Matrix
| Device | Screen Size | Priority |
|--------|-------------|----------|
| iPhone SE | 375 × 667 | P0 |
| iPhone 14 Pro | 393 × 852 | P0 |
| Samsung S23 | 360 × 780 | P0 |
| iPad Mini | 768 × 1024 | P1 |
| iPad Pro 11" | 834 × 1194 | P1 |

### Test Cases
1. ✅ Navigation works with bottom bar
2. ✅ Drawer opens/closes smoothly
3. ✅ Search expands correctly
4. ✅ File grid is 2-column on mobile
5. ✅ Touch targets ≥ 44px
6. ✅ Safe areas respected (notch, home indicator)
7. ✅ Upload button accessible
8. ✅ Preview modal is full-screen
9. ✅ Action sheet appears on file tap
10. ✅ Swipe gestures work

---

## 🔗 Dependencies

### New Packages (optional)
```json
{
  "@use-gesture/react": "^10.3.0",  // Touch gestures
  "react-spring": "^9.7.3"          // Smooth animations (alternative to framer-motion)
}
```

### Existing (already installed)
- `framer-motion` - Animations ✅
- `lucide-react` - Icons ✅
- `tailwindcss` - Styling ✅

---

## ⚠️ Considerations

### Known Challenges
1. **iOS Safari** - 100vh includes the address bar, use `dvh` or JS workaround
2. **Touch vs Click** - Need to handle both for hybrid devices
3. **Keyboard** - Virtual keyboard can push content, need proper handling
4. **Orientation** - Test both portrait and landscape modes

### Performance
1. Lazy load file thumbnails below the fold
2. Use CSS `content-visibility: auto` for long lists
3. Virtualize file grid for 100+ items

---

## 📝 Approval

- [ ] **@UIUX** - Design approved
- [ ] **@DEV** - Technical feasibility confirmed
- [ ] **User** - Requirements aligned

---

## 🚀 Next Steps

1. **Review & Approve** this specification
2. Proceed to **Phase 1: Foundation** implementation
3. Create component files per the architecture above

---

*Document generated following Agentic SDLC workflow.*

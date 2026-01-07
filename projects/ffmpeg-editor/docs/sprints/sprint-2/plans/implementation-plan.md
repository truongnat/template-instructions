# FFmpeg Desktop Editor - Sprint 2 Implementation Plan

> **Sprint:** 2  
> **Created:** 2026-01-07  
> **Status:** ✅ Approved  
> **Focus:** Option A (Production Polish) + Option B (Filters)

---

## Goal

Transform the MVP into a production-ready v1.0 release with polished UX, robust error handling, modular architecture, and advanced video filter capabilities.

## Sprint 2 Scope

### Phase 1: Component Modularization (T-010)

**Objective:** Break down the 763-line monolithic `App.tsx` into reusable components.

| File | Action | Description |
|------|--------|-------------|
| `src/components/MediaPlayer.tsx` | NEW | Video player with controls, time display |
| `src/components/ExportDialog.tsx` | NEW | Export modal with format/quality selection |
| `src/components/Timeline.tsx` | NEW | Visual timeline with trim handles |
| `src/components/BatchQueue.tsx` | NEW | Batch processing queue UI |
| `src/components/MergeDialog.tsx` | NEW | Multi-file merge modal |
| `src/hooks/useMediaControls.ts` | NEW | Play/pause, seek, volume hooks |
| `src/hooks/useFFmpeg.ts` | NEW | FFmpeg command invocation hooks |
| `src/types/index.ts` | NEW | Shared TypeScript interfaces |
| `src/App.tsx` | MODIFY | Refactor to use new components |

### Phase 2: Video Filters Panel (T-011)

**Objective:** Add real-time video filter controls.

| File | Action | Description |
|------|--------|-------------|
| `src/components/FilterPanel.tsx` | NEW | Slider-based filter controls |
| `src-tauri/src/lib.rs` | MODIFY | Add `-vf` filter chain to FFmpeg commands |
| `src/types/filters.ts` | NEW | Filter type definitions |

**Supported Filters:**
- Brightness (-1.0 to 1.0)
- Contrast (0.0 to 2.0)
- Saturation (0.0 to 3.0)
- Blur (0-10 sigma)
- Sharpen (0-10 luma amount)

### Phase 3: Error Handling & UX (T-012)

| File | Action | Description |
|------|--------|-------------|
| `src/components/ErrorBoundary.tsx` | NEW | React error boundary |
| `src-tauri/src/lib.rs` | MODIFY | Add timeout handling, better error messages |
| `src/App.css` | MODIFY | Loading states, error state styling |

### Phase 4: Testing & Documentation (T-013)

| File | Action | Description |
|------|--------|-------------|
| `src-tauri/src/lib.rs` | MODIFY | Add `#[cfg(test)]` unit tests |
| `README.md` | MODIFY | Comprehensive usage documentation |
| `docs/user-guide.md` | NEW | Step-by-step user manual |

---

## Architecture After Refactoring

```
src/
├── App.tsx              # Main app shell (reduced from 763 to ~150 lines)
├── App.css              # Global styles
├── main.tsx             # Entry point
├── components/
│   ├── MediaPlayer.tsx     # Video player (150 lines)
│   ├── Timeline.tsx        # Visual timeline (100 lines)
│   ├── ExportDialog.tsx    # Export modal (120 lines)
│   ├── FilterPanel.tsx     # Filter controls (80 lines)
│   ├── BatchQueue.tsx      # Batch processing (60 lines)
│   ├── MergeDialog.tsx     # Merge modal (80 lines)
│   └── ErrorBoundary.tsx   # Error handling (30 lines)
├── hooks/
│   ├── useMediaControls.ts # Video playback logic
│   └── useFFmpeg.ts        # FFmpeg command hooks
└── types/
    ├── index.ts            # Shared types
    └── filters.ts          # Filter definitions
```

---

## Verification Plan

### Automated Tests

```bash
# Rust unit tests
cd projects/ffmpeg-editor/src-tauri
cargo test

# Type checking
cd projects/ffmpeg-editor
bun run tsc --noEmit
```

### Manual Verification

1. **Component isolation:** Each component renders independently
2. **Filter preview:** Visual confirmation of filter effects
3. **Error handling:** Test FFmpeg not found, invalid files, network errors
4. **Export workflow:** Full cycle from import to export with filters

---

## Estimated Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| Phase 1 | Component Modularization | 2-3 hours |
| Phase 2 | Filter Panel | 1-2 hours |
| Phase 3 | Error Handling | 1 hour |
| Phase 4 | Testing & Docs | 1 hour |

**Total:** ~5-7 hours

---

## Success Criteria

- [ ] App.tsx reduced to < 200 lines
- [ ] All components have clear single responsibilities
- [ ] Filter panel functional with 5 filter types
- [ ] Rust tests pass
- [ ] No TypeScript errors
- [ ] README updated with usage instructions

---

*Created by @PM using Agentic SDLC*

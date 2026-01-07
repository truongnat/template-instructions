# FFmpeg Desktop Editor - Implementation Plan

> **Sprint:** 1  
> **Created:** 2026-01-06  
> **Status:** In Progress

## Goal

Build a desktop audio/video editor powered by FFmpeg with Tauri + React.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + TS)                     │
│  MediaPlayer │ Timeline │ FileExplorer │ ExportDialog │ Effects │
├─────────────────────────────────────────────────────────────────┤
│                    IPC BRIDGE (Tauri Commands)                   │
├─────────────────────────────────────────────────────────────────┤
│                        BACKEND (Rust)                            │
│  FFmpegService │ ProgressTracker │ PresetManager                │
├─────────────────────────────────────────────────────────────────┤
│                      FFmpeg Binary (Sidecar)                     │
└─────────────────────────────────────────────────────────────────┘
```

## Proposed Changes

### Phase 1: Core FFmpeg Backend (P0)
| File | Action | Description |
|------|--------|-------------|
| `src-tauri/src/lib.rs` | MODIFY | FFmpeg commands: convert, trim, get_media_info |
| `src-tauri/Cargo.toml` | MODIFY | Add tokio, regex, tauri-plugins |
| `src-tauri/capabilities/` | MODIFY | Enable shell, dialog, fs permissions |

### Phase 2: UI Components (P0)
| File | Action | Description |
|------|--------|-------------|
| `src/components/MediaPlayer.tsx` | NEW | HTML5 video player with controls |
| `src/components/FileExplorer.tsx` | NEW | Drag-drop import, recent files |
| `src/components/ExportDialog.tsx` | NEW | Format/quality presets, progress |
| `src/components/Timeline.tsx` | NEW | Trim region selection |

### Phase 3: Core Features (P1)
| Feature | Priority | Status |
|---------|----------|--------|
| Format Conversion | P0 | 🔄 In Progress |
| Video Trimming | P0 | ⏳ Pending |
| Audio Extraction | P0 | ⏳ Pending |
| Media Info Display | P0 | ⏳ Pending |

## Verification Plan

1. **Unit Tests:** Rust command tests
2. **Integration:** Convert sample files
3. **E2E:** Full export workflow with Playwright

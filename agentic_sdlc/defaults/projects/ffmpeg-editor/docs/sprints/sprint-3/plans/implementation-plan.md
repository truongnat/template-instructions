# FFmpeg Desktop Editor - Phase 3 Implementation Plan

Phase 3 aims to transition the application from a "Conversion & Trimming" tool into a "Feature-Rich Media Editor". We will implement the missing UI for filters from Sprint 2 and add professional editing features like overlays, audio mastering, and specialized exports.

## Proposed Changes

### 1. Component Completion & Polishing

#### [NEW] [FilterPanel.tsx](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src/components/FilterPanel.tsx)
- Slider controls for Brightness, Contrast, Saturation, Blur, and Sharpen.
- Toggle for real-time preview (if feasible) or apply on export.

#### [MODIFY] [App.tsx](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src/App.tsx)
- Integrate `FilterPanel` into the sidebar or a dedicated tab.
- Add state for `FilterSettings`.

---

### 2. Overlays & Annotations (New Module)

#### [NEW] [OverlayPanel.tsx](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src/components/OverlayPanel.tsx)
- **Text Overlay:** Input for text, font size, color, and position (Top-Left, Center, etc.).
- **Image Overly:** File picker for transparent PNGs (Logos) and position control.

#### [MODIFY] [lib.rs](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src-tauri/src/lib.rs)
- Update `ConvertOptions` to include `OverlaySettings`.
- Implement FFmpeg filter complex logic for multiple overlays: `[0:v][1:i]overlay=x:y[out]`.

---

### 3. Audio Mastering & Specialized Exports

#### [MODIFY] [ExportDialog.tsx](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src/components/ExportDialog.tsx)
- Add **Audio Volume** slider (0% to 200%).
- Add **GIF Export** option (triggers high-quality palettegen/paletteuse filter).
- Add **Thumbnail Extraction** (saves current frame as PNG).

#### [MODIFY] [lib.rs](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/src-tauri/src/lib.rs)
- Support for playback speed adjustment.
- Hardware acceleration flag (`-hwaccel auto`).

---

## Technical Details

### Filter Chain Logic for Overlays
To support text and image overlays simultaneously with filters:
```bash
ffmpeg -i input.mp4 -i logo.png -filter_complex \
"[0:v]eq=brightness=0.1,drawtext=text='STAMP':x=10:y=10[v1]; \
 [v1][1:v]overlay=W-w-10:H-h-10[outv]" \
-map "[outv]" -map 0:a output.mp4
```

### GIF Generation
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

---

## Verification Plan

### Automated Tests
- Test cases for complex filter string generation in Rust.
- Unit tests for `OverlaySettings` parsing.

### Manual Verification
1. **Visual Filters:** Verify brightness/contrast adjustments are reflected in output.
2. **Watermarking:** Burn a text string and a logo into a video.
3. **GIF Export:** Check resulting file size and color quality.
4. **Audio Extraction:** Verify volume boost works as expected.

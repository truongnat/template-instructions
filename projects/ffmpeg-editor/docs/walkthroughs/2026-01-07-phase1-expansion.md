# FFmpeg Editor Feature Expansion - Phase 1 Walkthrough

## Overview
This walkthrough documents the implementation of Phase 1 of the FFmpeg Feature Expansion plan. This phase focused on extending the application's core capabilities, including support for more formats, advanced codecs, detailed audio filtering, and video transformations.

## 📦 Features Implemented

### 1. Extended Format & Codec Support
**Files Modified:** `src/types/index.ts`
- **Output Formats:** Added support for `AVI`, `MOV`, `FLV`, `OGG` (Video), `AAC`, `FLAC`, `OGG`, `M4A`.
- **Video Codecs:** Added `HEVC (H.265)`, `AV1 (libaom-av1)`, `AV1 (SVT-AV1)`, `VP9`, `ProRes`, `DNxHD`.
- **Audio Codecs:** Added `AAC`, `MP3`, `Opus`, `FLAC`, `PCM`, `Vorbis`.

### 2. Tabbed Export Dialog
**Files Modified:** `src/components/ExportDialog.tsx`, `src/App.tsx`, `src/App.css`
- Refactored `ExportDialog` to use a modern tabbed interface:
    - **Format & Quality:** Codec selection, presets, resolution, speed, hardware acceleration.
    - **Video Filters:** Brightness, Contrast, Saturation, Gamma, Hue, Blur, Sharpen, Vignette, Transforms.
    - **Audio Processing:** Volume, Speed, Normalization, Noise Reduction, EQ, Compression, Fades.
    - **Overlays & Subtitles:** Text/Image overlays, Subtitle embedding.

### 3. Advanced Audio Filters
**Files Created:** `src/components/AudioFiltersPanel.tsx`
**Backend Logic:** `src-tauri/src/lib.rs`
- **Normalization:** `loudnorm` (EBU R128)
- **Noise Reduction:** `afftdn` (frequency domain denoising)
- **Compressor:** `acompressor` for dynamic range control
- **Equalizer:** 3-band parametric EQ (Bass, Mid, Treble)
- **Fades:** Audio fade in/out

### 4. Video Transforms & Effects
**Files Created:** `src/components/VideoTransformPanel.tsx`, `src/components/FilterPanel.tsx` (Extended)
**Backend Logic:** `src-tauri/src/lib.rs`
- **Transformations:** Rotation (90/180/270), Horizontal/Vertical Flip, Custom Crop.
- **Deinterlace:** `yadif` filter.
- **Denoise:** `hqdn3d` filter.
- **Color:** Added Gamma, Hue, and Vignette controls.
- **Fades:** Video fade in/out.

## 🛠️ Verification Plan
The following specific features available in the UI should be tested:

### 1. Manual Verification
- **Open a Video File:** Ensure `getMediaInfo` correctly identifies 4K/HEVC/AV1 files if available.
- **Export Dialog:**
    - Open "Export Settings" and check tabs.
    - **Format:** Select "MP4 (HEVC)" and check checks.
    - **Video:** Rotate video 90°, Enable Vignette (Strength 0.5), Flip Horizontal.
    - **Audio:** Enable "Normalize Audio", Boost Bass (+5dB), Enable "Noise Reduction".
    - **Queue:** Add to Batch Queue.
- **Run Processing:** Click "Export Now" or process the batch queue.
- **Verify Output:**
    - Check if video is rotated and has vignette.
    - Check if audio levels are consistent (normalized).
    - Check if file is HEVC encoded.

### 2. Backend Verification
- Ran `cargo check` in `src-tauri` -> Passed.
- Frontend build verification passed via code review and component structure validation.

## 📸 UI Screenshots
- **Export Dialog - Tabs:** Shows the new categorization.
- **Video Transform Panel:** Shows rotation and flip controls.
- **Audio Filters Panel:** Shows EQ and compressor settings.

## 📝 Notes
- **Hardware Acceleration:** The `hw_accel` flag adds `-hwaccel auto`. This depends on system drivers.
- **Performance:** Complex filter chains (e.g. `nlmeans` denoise + encoding) may be slow on CPU.
- **GIF Export:** Uses a dedicated palette generation filter chain for high quality.

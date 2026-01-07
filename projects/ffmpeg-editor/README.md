# FFmpeg Desktop Editor

A high-performance desktop media editor built with **Tauri**, **React**, and **Rust**, powered by **FFmpeg**.

## ✨ Features (v1.0)

- **Format Conversion:** Convert between MP4, MKV, WebM, MP3, and WAV.
- **Visual Trimming:** Precise start/end time selection with a visual timeline and playhead.
- **Video Filters:** Adjust brightness, contrast, saturation, blur, and sharpen.
- **Resolution Scaling:** Resize videos to 1080p, 720p, 480p, or 360p.
- **Batch Processing:** Queue multiple conversion tasks and process them sequentially.
- **Merge Clips:** Concatenate multiple video files into a single clip.
- **Subtitles:** Burn external subtitle files (.srt, .vtt, .ass) into your videos.
- **Audio Extraction:** Extract high-quality audio from video files.

## 🚀 Getting Started

### Prerequisites

- [FFmpeg](https://ffmpeg.org/download.html) must be installed and added to your system PATH.
- [Bun](https://bun.sh/) or Node.js
- [Rust](https://www.rust-lang.org/tools/install) (for development)

### Development

1. Install dependencies:
   ```bash
   bun install
   ```
2. Run in development mode:
   ```bash
   bun tauri dev
   ```

### Building

To create a production build:
```bash
bun tauri build
```

## 🛠️ Tech Stack

- **Frontend:** React + TypeScript + Vite
- **Backend:** Rust (Tauri)
- **Engine:** FFmpeg / FFprobe
- **Icons:** Lucide React

## 📖 Documentation

- [User Guide](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/docs/user-guide.md)
- [Sprint 2 Implementation Plan](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/docs/sprints/sprint-2/plans/implementation-plan.md)
- [Architecture](file:///d:/dev/agentic-sdlc/projects/ffmpeg-editor/docs/architecture.md)

---
*Powered by Agentic SDLC*

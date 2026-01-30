export interface MediaInfo {
    duration: number;
    width?: number;
    height?: number;
    codec?: string;
    audio_codec?: string;
    format?: string;
    bitrate?: number;
    sample_rate?: number;
    channels?: number;
    frame_rate?: number;
}

// ============================================
// AUDIO FILTER SETTINGS (Phase 1)
// ============================================
export interface AudioFilterSettings {
    // Normalize (loudnorm)
    normalize: boolean;
    targetLufs: number; // -24 to -14 LUFS

    // Equalizer
    eqEnabled: boolean;
    bassGain: number; // -20 to +20 dB
    midGain: number;
    trebleGain: number;

    // Noise Reduction
    noiseReduction: boolean;
    noiseReductionStrength: number; // 0 to 100

    // Compressor
    compressorEnabled: boolean;
    compressorThreshold: number; // -50 to 0 dB
    compressorRatio: number; // 1 to 20

    // Fade
    fadeInDuration: number; // seconds
    fadeOutDuration: number;
}

// ============================================
// VIDEO TRANSFORM SETTINGS (Phase 1)
// ============================================
export interface VideoTransformSettings {
    // Rotation
    rotation: 0 | 90 | 180 | 270;

    // Crop
    cropEnabled: boolean;
    cropTop: number;
    cropBottom: number;
    cropLeft: number;
    cropRight: number;

    // Flip
    flipHorizontal: boolean;
    flipVertical: boolean;

    // Deinterlace
    deinterlace: boolean;

    // Additional filters
    denoise: boolean;
    denoiseStrength: number; // 0 to 10

    // Fade
    fadeInDuration: number;
    fadeOutDuration: number;
}

// ============================================
// ENCODING OPTIONS (Phase 1)
// ============================================
export interface EncodingSettings {
    // Bitrate control
    bitrateMode: 'crf' | 'cbr' | 'vbr';
    videoBitrate?: number; // kbps
    audioBitrate?: number; // kbps

    // Two-pass encoding
    twoPass: boolean;

    // Advanced
    profile?: 'baseline' | 'main' | 'high';
    level?: string; // e.g., "4.0", "5.1"
    gopSize?: number; // keyframe interval
    bFrames?: number; // 0-16

    // Audio
    sampleRate?: 44100 | 48000 | 96000;
    channels?: 'mono' | 'stereo' | '5.1';

    // Pixel format
    pixelFormat?: 'yuv420p' | 'yuv422p' | 'yuv444p';
}

export interface ConvertOptions {
    input: string;
    output: string;
    video_codec?: string;
    audio_codec?: string;
    crf?: number;
    preset?: string;
    start_time?: number;
    end_time?: number;
    width?: number;
    height?: number;
    audio_only: boolean;
    subtitle_path?: string;
    merge_files?: string[];
    // Sprint 2: Filters
    filters?: FilterSettings;
    // Phase 3: Advanced
    overlays?: OverlaySettings;
    audio_volume?: number; // 0.0 to 2.0
    playback_speed?: number; // 0.5 to 2.0
    export_gif?: boolean;
    extract_thumbnail?: boolean;
    hw_accel?: boolean;
    // Phase 1 Expansion
    audio_filters?: AudioFilterSettings;
    video_transform?: VideoTransformSettings;
    encoding?: EncodingSettings;
}

export interface OverlaySettings {
    text?: {
        content: string;
        fontSize: number;
        color: string;
        x: string; // e.g., "10", "(W-w)/2"
        y: string;
    };
    image?: {
        path: string;
        x: string;
        y: string;
        opacity: number;
    };
}

export interface Progress {
    percent: number;
    time: number;
    speed: string;
    size: string;
}

export interface FilterSettings {
    brightness: number;
    contrast: number;
    saturation: number;
    blur: number;
    sharpen: number;
    // Extended filters (Phase 1)
    gamma: number; // 0.1 to 10
    hue: number; // -180 to 180 degrees
    vignette: boolean;
    vignetteStrength: number; // 0 to 1
}

export const PRESETS = {
    high: { crf: 18, preset: 'slow', label: 'High Quality' },
    medium: { crf: 23, preset: 'medium', label: 'Balanced' },
    low: { crf: 28, preset: 'fast', label: 'Small Size' },
    lossless: { crf: 0, preset: 'veryslow', label: 'Lossless' },
};

// ============================================
// EXTENDED OUTPUT FORMATS (Phase 1)
// ============================================
export const OUTPUT_FORMATS = [
    // Video formats
    { value: 'mp4', label: 'MP4 (H.264)', codec: 'libx264', category: 'video' },
    { value: 'mp4-hevc', label: 'MP4 (HEVC/H.265)', codec: 'libx265', category: 'video' },
    { value: 'mp4-av1', label: 'MP4 (AV1)', codec: 'libaom-av1', category: 'video' },
    { value: 'mkv', label: 'MKV (H.264)', codec: 'libx264', category: 'video' },
    { value: 'mkv-hevc', label: 'MKV (HEVC/H.265)', codec: 'libx265', category: 'video' },
    { value: 'webm', label: 'WebM (VP9)', codec: 'libvpx-vp9', category: 'video' },
    { value: 'webm-av1', label: 'WebM (AV1)', codec: 'libaom-av1', category: 'video' },
    { value: 'avi', label: 'AVI (H.264)', codec: 'libx264', category: 'video' },
    { value: 'mov', label: 'MOV (H.264)', codec: 'libx264', category: 'video' },
    { value: 'mov-prores', label: 'MOV (ProRes)', codec: 'prores_ks', category: 'video' },
    { value: 'flv', label: 'FLV (H.264)', codec: 'libx264', category: 'video' },
    { value: 'ogv', label: 'OGV (Theora)', codec: 'libtheora', category: 'video' },

    // Audio formats
    { value: 'mp3', label: 'MP3', codec: 'libmp3lame', audioOnly: true, category: 'audio' },
    { value: 'aac', label: 'AAC (M4A)', codec: 'aac', audioOnly: true, category: 'audio' },
    { value: 'wav', label: 'WAV (Lossless)', codec: 'pcm_s16le', audioOnly: true, category: 'audio' },
    { value: 'flac', label: 'FLAC (Lossless)', codec: 'flac', audioOnly: true, category: 'audio' },
    { value: 'ogg', label: 'OGG (Vorbis)', codec: 'libvorbis', audioOnly: true, category: 'audio' },
    { value: 'opus', label: 'Opus', codec: 'libopus', audioOnly: true, category: 'audio' },
];

// ============================================
// CODEC OPTIONS (Phase 1)
// ============================================
export const VIDEO_CODECS = [
    { value: 'libx264', label: 'H.264 (Most Compatible)', quality: 'good' },
    { value: 'libx265', label: 'HEVC/H.265 (Better Compression)', quality: 'great' },
    { value: 'libaom-av1', label: 'AV1 (Best Compression, Slow)', quality: 'excellent' },
    { value: 'libsvtav1', label: 'AV1 (Fast Encoder)', quality: 'excellent' },
    { value: 'libvpx-vp9', label: 'VP9 (WebM)', quality: 'great' },
    { value: 'prores_ks', label: 'ProRes (Professional)', quality: 'lossless' },
    { value: 'dnxhd', label: 'DNxHD (Avid)', quality: 'lossless' },
    { value: 'copy', label: 'Copy (No Re-encode)', quality: 'original' },
];

export const AUDIO_CODECS = [
    { value: 'aac', label: 'AAC (Universal)', quality: 'good' },
    { value: 'libmp3lame', label: 'MP3 (Legacy)', quality: 'good' },
    { value: 'libopus', label: 'Opus (Best Quality/Size)', quality: 'excellent' },
    { value: 'libvorbis', label: 'Vorbis (OGG)', quality: 'good' },
    { value: 'flac', label: 'FLAC (Lossless)', quality: 'lossless' },
    { value: 'pcm_s16le', label: 'PCM (Uncompressed)', quality: 'lossless' },
    { value: 'copy', label: 'Copy (No Re-encode)', quality: 'original' },
];

// ============================================
// DEFAULT VALUES
// ============================================
export const DEFAULT_AUDIO_FILTERS: AudioFilterSettings = {
    normalize: false,
    targetLufs: -16,
    eqEnabled: false,
    bassGain: 0,
    midGain: 0,
    trebleGain: 0,
    noiseReduction: false,
    noiseReductionStrength: 50,
    compressorEnabled: false,
    compressorThreshold: -20,
    compressorRatio: 4,
    fadeInDuration: 0,
    fadeOutDuration: 0,
};

export const DEFAULT_VIDEO_TRANSFORM: VideoTransformSettings = {
    rotation: 0,
    cropEnabled: false,
    cropTop: 0,
    cropBottom: 0,
    cropLeft: 0,
    cropRight: 0,
    flipHorizontal: false,
    flipVertical: false,
    deinterlace: false,
    denoise: false,
    denoiseStrength: 3,
    fadeInDuration: 0,
    fadeOutDuration: 0,
};

export const DEFAULT_FILTER_SETTINGS: FilterSettings = {
    brightness: 0,
    contrast: 1,
    saturation: 1,
    blur: 0,
    sharpen: 0,
    gamma: 1,
    hue: 0,
    vignette: false,
    vignetteStrength: 0.3,
};

export const DEFAULT_ENCODING: EncodingSettings = {
    bitrateMode: 'crf',
    twoPass: false,
    profile: 'high',
    sampleRate: 48000,
    channels: 'stereo',
    pixelFormat: 'yuv420p',
};

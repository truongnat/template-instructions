use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FilterSettings {
    pub brightness: f32,
    pub contrast: f32,
    pub saturation: f32,
    pub blur: f32,
    pub sharpen: f32,
    // Extended Filters
    #[serde(default)]
    pub gamma: f32,
    #[serde(default)]
    pub hue: f32,
    #[serde(default)]
    pub vignette: bool,
    #[serde(default)]
    pub vignette_strength: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")] // Match JS camelCase
pub struct AudioFilterSettings {
    pub normalize: bool,
    pub target_lufs: f32,
    pub eq_enabled: bool,
    pub bass_gain: f32,
    pub mid_gain: f32,
    pub treble_gain: f32,
    pub noise_reduction: bool,
    pub noise_reduction_strength: f32,
    pub compressor_enabled: bool,
    pub compressor_threshold: f32,
    pub compressor_ratio: f32,
    pub fade_in_duration: f32,
    pub fade_out_duration: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub struct VideoTransformSettings {
    pub rotation: u16,
    pub crop_enabled: bool,
    pub crop_top: u32,
    pub crop_bottom: u32,
    pub crop_left: u32,
    pub crop_right: u32,
    pub flip_horizontal: bool,
    pub flip_vertical: bool,
    pub deinterlace: bool,
    pub denoise: bool,
    pub denoise_strength: u32,
    pub fade_in_duration: f32,
    pub fade_out_duration: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct TextOverlay {
    pub content: String,
    pub font_size: u32,
    pub color: String,
    pub x: String,
    pub y: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ImageOverlay {
    pub path: String,
    pub x: String,
    pub y: String,
    pub opacity: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OverlaySettings {
    pub text: Option<TextOverlay>,
    pub image: Option<ImageOverlay>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MediaInfo {
    pub duration: f64,
    pub width: Option<u32>,
    pub height: Option<u32>,
    pub codec: Option<String>,
    pub audio_codec: Option<String>,
    pub format: Option<String>,
    pub bitrate: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConvertOptions {
    pub input: String,
    pub output: String,
    pub video_codec: Option<String>,
    pub audio_codec: Option<String>,
    pub crf: Option<u8>,
    pub preset: Option<String>,
    pub start_time: Option<f64>,
    pub end_time: Option<f64>,
    pub width: Option<u32>,
    pub height: Option<u32>,
    pub audio_only: bool,
    pub subtitle_path: Option<String>,
    pub merge_files: Option<Vec<String>>,
    pub filters: Option<FilterSettings>,
    pub overlays: Option<OverlaySettings>,
    pub audio_volume: Option<f32>,
    pub playback_speed: Option<f32>,
    pub export_gif: Option<bool>,
    pub extract_thumbnail: Option<bool>,
    pub hw_accel: Option<bool>,
    
    // New Fields
    #[serde(rename = "audioFilters")] 
    pub audio_filters: Option<AudioFilterSettings>,
    #[serde(rename = "videoTransform")] 
    pub video_transform: Option<VideoTransformSettings>,
}

#[derive(Debug, Serialize, Clone)]
pub struct Progress {
    pub percent: f64,
    pub time: f64,
    pub speed: String,
    pub size: String,
}

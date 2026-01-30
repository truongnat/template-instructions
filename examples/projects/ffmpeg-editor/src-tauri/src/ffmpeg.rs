use crate::models::ConvertOptions;

/// Helper to build FFmpeg filter arguments
pub fn build_filter_chain(options: &ConvertOptions, total_duration: f64) -> (Vec<String>, bool) {
    let mut args = Vec::new();
    let mut vf_filters = Vec::new();

    // 1. Pre-Scale Transforms (Deinterlace, Denoise)
    if let Some(ref transform) = options.video_transform {
        if transform.deinterlace {
            vf_filters.push("yadif".to_string());
        }
        if transform.denoise {
            vf_filters.push(format!("hqdn3d=luma_tmp={}", transform.denoise_strength as f32 / 2.0));
        }
    }

    // 2. Playback Speed (Video PTS)
    if let Some(speed) = options.playback_speed {
        if (speed - 1.0).abs() > f32::EPSILON {
            vf_filters.push(format!("setpts={}*PTS", 1.0 / speed));
        }
    }

    // 3. Rotation (Transpose)
    if let Some(ref transform) = options.video_transform {
        match transform.rotation {
            90 => vf_filters.push("transpose=1".to_string()),
            180 => vf_filters.push("transpose=2,transpose=2".to_string()),
            270 => vf_filters.push("transpose=2".to_string()),
            _ => {}
        }
    }

    // 4. Crop
    if let Some(ref transform) = options.video_transform {
        if transform.crop_enabled {
            vf_filters.push(format!(
                "crop=in_w-{}-{}:in_h-{}-{}:{}:{}",
                transform.crop_left, transform.crop_right,
                transform.crop_top, transform.crop_bottom,
                transform.crop_left, transform.crop_top
            ));
        }
    }

    // 5. Scale
    if options.width.is_some() || options.height.is_some() {
        let w = options.width.map(|v| v.to_string()).unwrap_or("-1".to_string());
        let h = options.height.map(|v| v.to_string()).unwrap_or("-1".to_string());
        vf_filters.push(format!("scale={}:{}", w, h));
    }

    // 6. Post-Scale Transforms (Flip)
    if let Some(ref transform) = options.video_transform {
        if transform.flip_horizontal {
            vf_filters.push("hflip".to_string());
        }
        if transform.flip_vertical {
            vf_filters.push("vflip".to_string());
        }
    }

    // 7. Video Filters (Color, Blur, Sharpen)
    if let Some(ref filters) = options.filters {
        vf_filters.push(format!(
            "eq=brightness={}:contrast={}:saturation={}:gamma={}", 
            filters.brightness, filters.contrast, filters.saturation, filters.gamma
        ));
        
        if filters.hue != 0.0 {
            vf_filters.push(format!("hue=h={}", filters.hue));
        }

        if filters.blur > 0.0 {
            vf_filters.push(format!("boxblur={}", filters.blur));
        }

        if filters.sharpen > 0.0 {
            vf_filters.push(format!("unsharp=5:5:{}", filters.sharpen));
        }
        
        if filters.vignette {
            let angle = std::f32::consts::PI / 2.0 * filters.vignette_strength;
            vf_filters.push(format!("vignette=a={}", angle));
        }
    }

    // 8. Video Fade In/Out
    if let Some(ref transform) = options.video_transform {
        if transform.fade_in_duration > 0.0 {
            vf_filters.push(format!("fade=t=in:st={}:d={}", 
                options.start_time.unwrap_or(0.0), 
                transform.fade_in_duration
            ));
        }
        if transform.fade_out_duration > 0.0 {
            let start = options.start_time.unwrap_or(0.0);
            let end = options.end_time.unwrap_or(total_duration);
            let output_duration = end - start;
            let fade_start = (output_duration - transform.fade_out_duration as f64).max(0.0);
            
            vf_filters.push(format!("fade=t=out:st={}:d={}", 
                fade_start, 
                transform.fade_out_duration
            ));
        }
    }

    // 9. Overlays (Text / Subtitles)
    if let Some(ref sub_path) = options.subtitle_path {
        let sub_processed = sub_path.replace("\\", "/").replace(":", "\\:");
        vf_filters.push(format!("subtitles='{}'", sub_processed));
    }

    if let Some(ref overlays) = options.overlays {
        if let Some(ref text) = overlays.text {
            let x_pos = if text.x.is_empty() { "10" } else { &text.x };
            let y_pos = if text.y.is_empty() { "10" } else { &text.y };
            
            vf_filters.push(format!(
                "drawtext=text='{}':fontsize={}:fontcolor={}:x={}:y={}",
                text.content.replace(":", "\\:").replace("'", "'\\''"),
                text.font_size, 
                text.color, 
                x_pos, 
                y_pos
            ));
        }
    }

    // GIF Export
    if options.export_gif.unwrap_or(false) {
        vf_filters.push("fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse".to_string());
    }

    // Construct Video Filter Args
    let has_image_overlay = options.overlays.as_ref()
        .and_then(|o| o.image.as_ref())
        .is_some();
    
    let mut uses_complex = false;

    if has_image_overlay {
        let img = options.overlays.as_ref().unwrap().image.as_ref().unwrap();
        let vf_str = if vf_filters.is_empty() { "null".to_string() } else { vf_filters.join(",") };
        
        let x_pos = if img.x.is_empty() { "0" } else { &img.x };
        let y_pos = if img.y.is_empty() { "0" } else { &img.y };
        
        // Use colorchannelmixer for opacity on the overlay input (stream 1)
        // Force RGBA format before mixing to ensure alpha channel exists even for JPGs
        let overlay_chain = if (img.opacity - 1.0).abs() > f32::EPSILON {
             format!("[1:v]format=rgba,colorchannelmixer=aa={:.2}[ovr];[v1][ovr]overlay=x={}:y={}[outv]", 
                img.opacity, x_pos, y_pos)
        } else {
             format!("[v1][1:v]overlay=x={}:y={}[outv]", x_pos, y_pos)
        };

        let filter_comp = format!(
            "[0:v]{}[v1];{}",
            vf_str, overlay_chain
        );
        
        args.push("-filter_complex".to_string());
        args.push(filter_comp);
        args.push("-map".to_string());
        args.push("[outv]".to_string());
        uses_complex = true;
    } else if !vf_filters.is_empty() {
        args.push("-vf".to_string());
        args.push(vf_filters.join(","));
    }

    // Audio Filter Chain
    let mut af_filters = Vec::new();
    
    // 1. Noise Reduction
    if let Some(ref af) = options.audio_filters {
        if af.noise_reduction {
            let strength_db = (af.noise_reduction_strength as f32 / 100.0) * 30.0;
            af_filters.push(format!("afftdn=nr={:.2}", strength_db.max(0.1)));
        }
    }

    // 2. Playback Speed
    if let Some(speed) = options.playback_speed {
        if (speed - 1.0).abs() > f32::EPSILON {
            af_filters.push(format!("atempo={}", speed));
        }
    }

    // 3. Simple Volume
    if let Some(vol) = options.audio_volume {
        if (vol - 1.0).abs() > f32::EPSILON {
            af_filters.push(format!("volume={}", vol));
        }
    }

    // 4. Equalizer
    if let Some(ref af) = options.audio_filters {
        if af.eq_enabled {
            af_filters.push(format!("equalizer=f=100:t=h:w=200:g={}", af.bass_gain));
            af_filters.push(format!("equalizer=f=1000:t=h:w=500:g={}", af.mid_gain));
            af_filters.push(format!("equalizer=f=10000:t=h:w=2000:g={}", af.treble_gain));
        }
    }

    // 5. Compressor
    if let Some(ref af) = options.audio_filters {
        if af.compressor_enabled {
            af_filters.push(format!(
                "acompressor=threshold={}dB:ratio={}:attack=5:release=50",
                af.compressor_threshold, af.compressor_ratio
            ));
        }
    }

    // 6. Loudness Normalization
    if let Some(ref af) = options.audio_filters {
        if af.normalize {
            af_filters.push(format!("loudnorm=I={}:TP=-1.5:LRA=11", af.target_lufs));
        }
    }

    // 7. Audio Fade
    if let Some(ref af) = options.audio_filters {
        if af.fade_in_duration > 0.0 {
            af_filters.push(format!("afade=t=in:st={}:d={}", 
                options.start_time.unwrap_or(0.0), 
                af.fade_in_duration
            ));
        }
        if af.fade_out_duration > 0.0 {
            let start = options.start_time.unwrap_or(0.0);
            let end = options.end_time.unwrap_or(total_duration);
            let output_duration = end - start;
            let fade_start = (output_duration - af.fade_out_duration as f64).max(0.0);
            
            af_filters.push(format!("afade=t=out:st={}:d={}", 
                fade_start, 
                af.fade_out_duration
            ));
        }
    }

    if !af_filters.is_empty() {
        args.push("-af".to_string());
        args.push(af_filters.join(","));
    }

    // Map audio if we used filter_complex for video
    if has_image_overlay && !options.audio_only {
        args.push("-map".to_string());
        args.push("0:a".to_string());
    }
    
    // Thumbnail Extraction
    if options.extract_thumbnail.unwrap_or(false) {
        args.push("-vframes".to_string());
        args.push("1".to_string());
    }

    (args, uses_complex)
}

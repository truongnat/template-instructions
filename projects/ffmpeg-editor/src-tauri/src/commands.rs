use tauri::{AppHandle, Emitter};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;
use std::process::Stdio;
use std::sync::atomic::{AtomicBool, Ordering};

use crate::models::{ConvertOptions, MediaInfo, Progress};
use crate::utils::{parse_duration, parse_progress};
use crate::ffmpeg::build_filter_chain;

// Global flag to track cancellation - Re-declared here effectively as a new static for this module?
// No, generics/statics don't work like that across mods easily if we want "THE" global.
// Usage in lib.rs was `static CANCELLED`.
// If we move it here, it is local to this module.
// Since `cancel_conversion` is also moved here, it should share the same static.
static CANCELLED: AtomicBool = AtomicBool::new(false);

/// Get media info using ffprobe
#[tauri::command]
pub async fn get_media_info(path: String) -> Result<MediaInfo, String> {
    let output = tokio::time::timeout(
        std::time::Duration::from_secs(10),
        Command::new("ffprobe")
            .args([
                "-v", "error",
                "-show_entries", "format=duration,bit_rate:stream=width,height,codec_name,codec_type",
                "-of", "json",
                &path,
            ])
            .output(),
    )
    .await
    .map_err(|_| "ffprobe timed out".to_string())?
    .map_err(|e| format!("Failed to run ffprobe: {}", e))?;

    if !output.status.success() {
        return Err("ffprobe failed".to_string());
    }

    let json_str = String::from_utf8_lossy(&output.stdout);
    let json: serde_json::Value =
        serde_json::from_str(&json_str).map_err(|e| format!("Failed to parse JSON: {}", e))?;

    let duration = json["format"]["duration"]
        .as_str()
        .and_then(|s| s.parse::<f64>().ok())
        .unwrap_or(0.0);

    let bitrate = json["format"]["bit_rate"]
        .as_str()
        .and_then(|s| s.parse::<u64>().ok());

    let streams = json["streams"].as_array();
    let mut width = None;
    let mut height = None;
    let mut codec = None;
    let mut audio_codec = None;

    if let Some(streams) = streams {
        for stream in streams {
            let codec_type = stream["codec_type"].as_str().unwrap_or("");
            if codec_type == "video" {
                width = stream["width"].as_u64().map(|w| w as u32);
                height = stream["height"].as_u64().map(|h| h as u32);
                codec = stream["codec_name"].as_str().map(|s| s.to_string());
            } else if codec_type == "audio" {
                audio_codec = stream["codec_name"].as_str().map(|s| s.to_string());
            }
        }
    }

    Ok(MediaInfo {
        duration,
        width,
        height,
        codec,
        audio_codec,
        format: Some(
            path.split('.')
                .last()
                .unwrap_or("unknown")
                .to_uppercase(),
        ),
        bitrate,
    })
}

/// Convert/process media using ffmpeg
#[tauri::command]
pub async fn convert_media(app: AppHandle, options: ConvertOptions) -> Result<(), String> {
    CANCELLED.store(false, Ordering::SeqCst);

    // First, get duration for progress calculation
    let probe_output = tokio::time::timeout(
        std::time::Duration::from_secs(10),
        Command::new("ffprobe")
            .args(["-v", "error", "-show_format", &options.input])
            .output(),
    )
    .await
    .map_err(|_| "ffprobe (probe) timed out".to_string())?
    .map_err(|e| format!("Failed to probe: {}", e))?;

    let probe_str = String::from_utf8_lossy(&probe_output.stdout);
    let total_duration = parse_duration(&probe_str);

    // Build ffmpeg command
    let mut args = Vec::new();

    // Hardware Acceleration
    if options.hw_accel.unwrap_or(false) {
        args.push("-hwaccel".to_string());
        args.push("auto".to_string());
    }

    args.push("-y".to_string());
    args.push("-i".to_string());
    args.push(options.input.clone());

    // Image Overlay Input (Index 1)
    if let Some(ref overlays) = options.overlays {
        if let Some(ref img) = overlays.image {
            args.push("-i".to_string());
            args.push(img.path.clone());
        }
    }

    // Add trim options
    if let Some(start) = options.start_time {
        args.push("-ss".to_string());
        args.push(format!("{:.2}", start));
    }
    if let Some(end) = options.end_time {
        args.push("-to".to_string());
        args.push(format!("{:.2}", end));
    }

    // Audio only extraction
    if options.audio_only {
        args.push("-vn".to_string());
    }

    // Video codec
    if let Some(ref vcodec) = options.video_codec {
        args.push("-c:v".to_string());
        args.push(vcodec.clone());
    }

    // Audio codec
    if let Some(ref acodec) = options.audio_codec {
        args.push("-c:a".to_string());
        args.push(acodec.clone());
    }

    // Quality (CRF)
    if let Some(crf) = options.crf {
        args.push("-crf".to_string());
        args.push(crf.to_string());
    }

    // Preset
    if let Some(ref preset) = options.preset {
        args.push("-preset".to_string());
        args.push(preset.clone());
    }

    // Construct arguments using helper
    let (filter_args, _has_complex) = build_filter_chain(&options, total_duration);
    args.extend(filter_args);

    // Progress
    args.push("-progress".to_string());
    args.push("pipe:1".to_string());

    // Output
    args.push(options.output.clone());

    // Spawn
    let mut child = Command::new("ffmpeg")
        .args(&args)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start ffmpeg: {}", e))?;

    let stderr = child.stderr.take().unwrap();
    let mut reader = BufReader::new(stderr).lines();

    while let Ok(Some(line)) = reader.next_line().await {
        if CANCELLED.load(Ordering::SeqCst) {
            let _ = child.kill().await;
            return Err("Cancelled by user".to_string());
        }
        if let Some(progress) = parse_progress(&line, total_duration) {
            let _ = app.emit("ffmpeg-progress", progress);
        }
    }

    let status = child.wait().await.map_err(|e| format!("Process error: {}", e))?;

    if !status.success() {
        return Err("FFmpeg conversion failed".to_string());
    }

    let _ = app.emit(
        "ffmpeg-progress",
        Progress {
            percent: 100.0,
            time: total_duration,
            speed: "Done".to_string(),
            size: "Complete".to_string(),
        },
    );

    Ok(())
}

#[tauri::command]
pub fn cancel_conversion() {
    CANCELLED.store(true, Ordering::SeqCst);
}

#[tauri::command]
pub async fn merge_media(app: AppHandle, files: Vec<String>, output: String) -> Result<(), String> {
    CANCELLED.store(false, Ordering::SeqCst);
    
    let temp_dir = std::env::temp_dir();
    let list_path = temp_dir.join(format!("ffmpeg_concat_{}.txt", uuid::Uuid::new_v4()));
    
    let mut content = String::new();
    for file in files {
        content.push_str(&format!("file '{}'\n", file.replace("'", "'\\''")));
    }
    
    std::fs::write(&list_path, content).map_err(|e| format!("Failed to create concat list: {}", e))?;
    
    let args = vec![
        "-f".to_string(), "concat".to_string(),
        "-safe".to_string(), "0".to_string(),
        "-i".to_string(), list_path.to_str().unwrap().to_string(),
        "-c".to_string(), "copy".to_string(),
        "-y".to_string(),
        output.clone()
    ];

    let mut child = Command::new("ffmpeg")
        .args(&args)
        .spawn()
        .map_err(|e| format!("Failed to start ffmpeg merge: {}", e))?;

    let status = child.wait().await.map_err(|e| format!("Process error during merge: {}", e))?;
    let _ = std::fs::remove_file(list_path);

    if !status.success() {
        return Err("FFmpeg merge failed".to_string());
    }

    let _ = app.emit("ffmpeg-progress", Progress {
        percent: 100.0,
        time: 0.0,
        speed: "Done".to_string(),
        size: "Complete".to_string(),
    });

    Ok(())
}

#[tauri::command]
pub async fn check_ffmpeg() -> Result<String, String> {
    let output = Command::new("ffmpeg")
        .args(["-version"])
        .output()
        .await
        .map_err(|_| "FFmpeg not found. Please install FFmpeg.".to_string())?;

    let version = String::from_utf8_lossy(&output.stdout);
    let first_line = version.lines().next().unwrap_or("Unknown version");
    Ok(first_line.to_string())
}

#[tauri::command]
pub async fn download_video(app: AppHandle, url: String, output_dir: String) -> Result<String, String> {
    CANCELLED.store(false, Ordering::SeqCst);
    
    // Check if yt-dlp is available
    let _ = Command::new("yt-dlp")
        .arg("--version")
        .output()
        .await
        .map_err(|_| "yt-dlp not found. Please install yt-dlp.".to_string())?;

    let mut child = Command::new("yt-dlp")
        .args([
            "-o", &format!("{}\\%(title)s.%(ext)s", output_dir),
            "--newline",
            &url
        ])
        .stdout(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to start yt-dlp: {}", e))?;

    let stdout = child.stdout.take().unwrap();
    let mut reader = BufReader::new(stdout).lines();
    let mut last_filename = String::new();

    while let Ok(Some(line)) = reader.next_line().await {
        if CANCELLED.load(Ordering::SeqCst) {
             let _ = child.kill().await;
             return Err("Cancelled by user".to_string());
        }

        if line.starts_with("[download]") {
             let re = regex::Regex::new(r"(\d+\.?\d*)%").unwrap();
             if let Some(caps) = re.captures(&line) {
                 if let Ok(percent) = caps[1].parse::<f64>() {
                      let _ = app.emit("download-progress", Progress {
                        percent,
                        time: 0.0,
                        speed: "".to_string(), 
                        size: "".to_string(),
                    });
                 }
             }
             
             if line.contains("Destination: ") {
                 if let Some(path) = line.split("Destination: ").nth(1) {
                     last_filename = path.trim().to_string();
                 }
             } else if line.contains("has already been downloaded") {
                  if let Some(path) = line.split("] ").nth(1).and_then(|s| s.split(" has").next()) {
                      last_filename = path.trim().to_string();
                  }
             }
             
             if line.contains("Merging formats into") {
                 // Logic to handle "Merging formats into "path/to/file""
                 if let Some(path_part) = line.split("into \"").nth(1) {
                     if let Some(path) = path_part.split("\"").next() {
                         last_filename = path.trim().to_string();
                     }
                 }
             }
        }
    }

    let status = child.wait().await.map_err(|e| format!("yt-dlp process error: {}", e))?;

    if !status.success() {
        return Err("Download failed".to_string());
    }

    // Attempt to find the file if last_filename is empty or partial
    if last_filename.is_empty() {
        return Ok("Download complete (check output folder)".to_string());
    }

    Ok(last_filename)
}

/// Generate a preview frame for the current settings
#[tauri::command]
pub async fn generate_preview(_app: AppHandle, options: ConvertOptions, timestamp: f64) -> Result<String, String> {
    
    // Build ffmpeg command
    let mut args = Vec::new();

    args.push("-y".to_string());
    args.push("-ss".to_string());
    args.push(format!("{:.3}", timestamp));
    
    args.push("-i".to_string());
    args.push(options.input.clone());

    // Image Overlay Input
    if let Some(ref overlays) = options.overlays {
        if let Some(ref img) = overlays.image {
            args.push("-i".to_string());
            args.push(img.path.clone());
        }
    }

    // Filter Chain
    let (filter_args, _) = build_filter_chain(&options, 0.0); // Duration doesn't matter for single frame preview except for fade, which uses options.end_time or duration calc 
    // Optimization: Exclude audio filters for image preview
    let filter_args_video: Vec<String> = filter_args.into_iter().filter(|a| !a.contains("afade") && !a.contains("atempo") && !a.contains("volume") && !a.contains("equalizer") && !a.contains("acompressor") && !a.contains("loudnorm") && !a.contains("afftdn") && !a.eq("-af") && !a.eq("-map") && !a.eq("0:a")).collect();
    
    args.extend(filter_args_video);

    args.push("-vframes".to_string());
    args.push("1".to_string());
    
    // Output format: JPEG pipe
    args.push("-f".to_string());
    args.push("image2".to_string());
    args.push("-".to_string()); // Output to stdout

    let mut cmd = Command::new("ffmpeg");
    cmd.args(&args);
    
    // Tauri's Command::output() returns a Result<Output, CommandError>
    // We need to map errors correctly
    let output = cmd.output().await.map_err(|e| format!("Failed to run ffmpeg preview: {}", e))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(format!("FFmpeg preview failed: {}", stderr));
    }

    // Convert to base64
    use base64::{Engine as _, engine::general_purpose};
    let b64 = general_purpose::STANDARD.encode(&output.stdout);
    Ok(format!("data:image/jpeg;base64,{}", b64))
}

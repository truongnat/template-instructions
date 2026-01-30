// FFmpeg Editor - Tauri Backend
// Provides FFmpeg command execution and progress tracking

mod models;
mod utils;
mod ffmpeg;
mod commands;

use commands::*;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            get_media_info,
            convert_media,
            merge_media,
            cancel_conversion,
            check_ffmpeg,
            download_video,
            generate_preview
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

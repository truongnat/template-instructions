import { useState, useCallback } from 'react';
import { open, save } from '@tauri-apps/plugin-dialog';
import { Scissors, Download, Keyboard, FolderOpen } from 'lucide-react';

// Components
import { Header } from './components/Header';
import { MediaPlayer } from './components/MediaPlayer';
import { MediaInfoView } from './components/MediaInfoView';
import { Timeline } from './components/Timeline';
import { ExportDialog } from './components/ExportDialog';
import { BatchQueue } from './components/BatchQueue';
import { MergeDialog } from './components/MergeDialog';
import { ErrorBoundary } from './components/ErrorBoundary';
import { EnhancedDropZone } from './components/EnhancedDropZone';
import { ShortcutHelpDialog } from './components/ShortcutHelpDialog';
import { ErrorDialog, FFmpegError } from './components/ErrorDialog';
import { Button } from './components/ui/button';
import { DownloadPanel } from './components/DownloadPanel';

// Hooks
import { useMediaControls } from './hooks/useMediaControls';
import { useFFmpeg } from './hooks/useFFmpeg';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';

// Types & Constants
import {
  MediaInfo,
  ConvertOptions,
  PRESETS,
  OUTPUT_FORMATS,
  AudioFilterSettings,
  VideoTransformSettings,
  DEFAULT_FILTER_SETTINGS,
  DEFAULT_AUDIO_FILTERS,
  DEFAULT_VIDEO_TRANSFORM,
} from './types';

import './App.css';

function App() {
  // --- Hooks ---
  const media = useMediaControls();
  const ffmpeg = useFFmpeg();

  // --- State ---
  const [inputFile, setInputFile] = useState<string>('');
  const [mediaInfo, setMediaInfo] = useState<MediaInfo | null>(null);
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(0);

  // Dialog states
  const [showExport, setShowExport] = useState(false);
  const [showMerge, setShowMerge] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [currentError, setCurrentError] = useState<FFmpegError | null>(null);

  // Export options
  const [selectedFormat, setSelectedFormat] = useState(OUTPUT_FORMATS[0]);
  const [selectedPreset, setSelectedPreset] = useState<keyof typeof PRESETS>('medium');
  const [selectedResolution, setSelectedResolution] = useState<{ w: number | null, h: number | null }>({ w: null, h: null });
  const [selectedSubtitle, setSelectedSubtitle] = useState<string | null>(null);
  const [filterSettings, setFilterSettings] = useState(DEFAULT_FILTER_SETTINGS);
  const [audioFilters, setAudioFilters] = useState<AudioFilterSettings>(DEFAULT_AUDIO_FILTERS);
  const [videoTransform, setVideoTransform] = useState<VideoTransformSettings>(DEFAULT_VIDEO_TRANSFORM);
  const [overlaySettings, setOverlaySettings] = useState({});
  const [audioVolume, setAudioVolume] = useState(1.0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);
  const [hwAccel, setHwAccel] = useState(false);
  const [isGif, setIsGif] = useState(false);
  const [isThumbnail, setIsThumbnail] = useState(false);

  // Queues
  const [mergeQueue, setMergeQueue] = useState<string[]>([]);
  const [batchQueue, setBatchQueue] = useState<ConvertOptions[]>([]);
  const [isBatchProcessing, setIsBatchProcessing] = useState(false);

  // --- Handlers ---

  const handleOpenFile = async () => {
    const file = await open({
      multiple: false,
      filters: [{
        name: 'Media',
        extensions: ['mp4', 'mkv', 'avi', 'mov', 'webm', 'mp3', 'wav', 'flac', 'ogg']
      }]
    });

    if (file) {
      setInputFile(file as string);
      try {
        const info = await ffmpeg.getMediaInfo(file as string);
        setMediaInfo(info);
        setTrimEnd(info.duration);
      } catch (err) {
        console.error('Failed to get media info:', err);
      }
    }
  };

  const handleOpenSubtitle = async () => {
    const file = await open({
      multiple: false,
      filters: [{ name: 'Subtitles', extensions: ['srt', 'vtt', 'ass'] }]
    });
    if (file) setSelectedSubtitle(file as string);
  };

  const handleExport = async () => {
    const outputPath = await save({
      filters: [{ name: selectedFormat.label, extensions: [selectedFormat.value] }],
      defaultPath: `output.${selectedFormat.value}`
    });

    if (!outputPath) return;

    const preset = PRESETS[selectedPreset];
    const options: ConvertOptions = {
      input: inputFile,
      output: outputPath,
      video_codec: selectedFormat.codec,
      audio_codec: selectedFormat.audioOnly ? selectedFormat.codec : 'aac',
      crf: preset.crf,
      preset: preset.preset,
      start_time: trimStart > 0 ? trimStart : undefined,
      end_time: trimEnd < (mediaInfo?.duration || 0) ? trimEnd : undefined,
      width: selectedResolution.w || undefined,
      height: selectedResolution.h || undefined,
      audio_only: !!selectedFormat.audioOnly,
      subtitle_path: selectedSubtitle || undefined,
      filters: filterSettings,
      overlays: Object.keys(overlaySettings).length > 0 ? overlaySettings : undefined,
      audio_volume: audioVolume !== 1.0 ? audioVolume : undefined,
      playback_speed: playbackSpeed !== 1.0 ? playbackSpeed : undefined,
      hw_accel: hwAccel,
      export_gif: isGif,
      extract_thumbnail: isThumbnail,
      audio_filters: audioFilters,
      video_transform: videoTransform,
    };

    try {
      await ffmpeg.convertMedia(options);
      setShowExport(false);
    } catch (err) {
      console.error('Conversion failed:', err);
    }
  };

  const handleAddToBatch = () => {
    const preset = PRESETS[selectedPreset];
    const options: ConvertOptions = {
      input: inputFile,
      output: `${inputFile}_out_${Date.now()}.${selectedFormat.value}`,
      video_codec: selectedFormat.codec,
      audio_codec: selectedFormat.audioOnly ? selectedFormat.codec : 'aac',
      crf: preset.crf,
      preset: preset.preset,
      start_time: trimStart > 0 ? trimStart : undefined,
      end_time: trimEnd < (mediaInfo?.duration || 0) ? trimEnd : undefined,
      width: selectedResolution.w || undefined,
      height: selectedResolution.h || undefined,
      audio_only: !!selectedFormat.audioOnly,
      subtitle_path: selectedSubtitle || undefined,
      filters: filterSettings,
      overlays: Object.keys(overlaySettings).length > 0 ? overlaySettings : undefined,
      audio_volume: audioVolume !== 1.0 ? audioVolume : undefined,
      playback_speed: playbackSpeed !== 1.0 ? playbackSpeed : undefined,
      hw_accel: hwAccel,
      export_gif: isGif,
      extract_thumbnail: isThumbnail,
      // Phase 1 Expansion
      audio_filters: audioFilters,
      video_transform: videoTransform,
    };
    setBatchQueue([...batchQueue, options]);
    setShowExport(false);
  };

  const processBatch = async () => {
    if (batchQueue.length === 0) return;
    setIsBatchProcessing(true);
    for (const options of batchQueue) {
      try {
        await ffmpeg.convertMedia(options);
      } catch (err) {
        console.error('Batch conversion failed for file:', options.input, err);
      }
    }
    setBatchQueue([]);
    setIsBatchProcessing(false);
  };

  const handleMergeAction = async () => {
    if (mergeQueue.length < 2) return;
    const outputPath = await save({
      filters: [{ name: 'Merged Video', extensions: ['mp4'] }],
      defaultPath: `merged_${Date.now()}.mp4`
    });
    if (!outputPath) return;

    try {
      await ffmpeg.mergeMedia(mergeQueue, outputPath);
      setShowMerge(false);
      setMergeQueue([]);
    } catch (err) {
      console.error('Merge failed:', err);
    }
  };

  const handleOpenMultiMerge = async () => {
    const files = await open({
      multiple: true,
      filters: [{ name: 'Videos', extensions: ['mp4', 'mkv', 'avi', 'mov'] }]
    });
    if (files && Array.isArray(files)) {
      setMergeQueue(files);
      setShowMerge(true);
    }
  };

  const formatTime = useCallback((seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return h > 0
      ? `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
      : `${m}:${s.toString().padStart(2, '0')}`;
  }, []);

  // Frame stepping (approximate 30fps)
  const FRAME_DURATION = 1 / 30;

  const handleFrameBack = useCallback(() => {
    if (media.videoRef.current) {
      media.videoRef.current.currentTime = Math.max(0, media.currentTime - FRAME_DURATION);
    }
  }, [media.currentTime, media.videoRef]);

  const handleFrameForward = useCallback(() => {
    if (media.videoRef.current && mediaInfo) {
      media.videoRef.current.currentTime = Math.min(mediaInfo.duration, media.currentTime + FRAME_DURATION);
    }
  }, [media.currentTime, media.videoRef, mediaInfo]);

  // Keyboard shortcuts
  useKeyboardShortcuts({
    onPlayPause: media.togglePlay,
    onFrameBack: handleFrameBack,
    onFrameForward: handleFrameForward,
    onSetIn: () => setTrimStart(media.currentTime),
    onSetOut: () => setTrimEnd(media.currentTime),
    onExport: () => inputFile && setShowExport(true),
    onOpenFile: handleOpenFile,
    onEscape: () => {
      setShowExport(false);
      setShowMerge(false);
      setShowShortcuts(false);
      setCurrentError(null);
    }
  }, !showExport && !showMerge); // Disable shortcuts when dialogs are open

  // Handle file drop
  const handleFileDrop = async (files: string[]) => {
    if (files.length > 0) {
      const file = files[0];
      setInputFile(file);
      try {
        const info = await ffmpeg.getMediaInfo(file);
        setMediaInfo(info);
        setTrimEnd(info.duration);
      } catch (err) {
        setCurrentError({ message: String(err) });
      }
    }
  };

  // --- Render ---


  return (
    <ErrorBoundary>
      <div className="app">
        <Header version={ffmpeg.ffmpegVersion} error={ffmpeg.ffmpegError} />

        <main className="main">
          {!inputFile ? (
            <div className="flex flex-col gap-6 max-w-3xl mx-auto w-full">
              <EnhancedDropZone
                onVideoFiles={handleFileDrop}
                onAudioFiles={handleFileDrop}
                onClick={handleOpenFile}
              />
              <DownloadPanel onAddFile={(path) => handleFileDrop([path])} />
            </div>
          ) : (
            <>
              <MediaPlayer
                videoRef={media.videoRef}
                inputFile={inputFile}
                subtitleFile={selectedSubtitle}
                isPlaying={media.isPlaying}
                currentTime={media.currentTime}
                duration={mediaInfo?.duration || 0}
                volume={media.volume}
                isMuted={media.isMuted}
                onTimeUpdate={media.handleTimeUpdate}
                onEnded={() => media.setIsPlaying(false)}
                onTogglePlay={media.togglePlay}
                onSeek={media.handleSeek}
                onToggleMute={media.toggleMute}
                onVolumeChange={media.handleVolumeChange}
                formatTime={formatTime}
              />

              {mediaInfo && (
                <MediaInfoView info={mediaInfo} formatTime={formatTime} />
              )}

              <Timeline
                duration={mediaInfo?.duration || 0}
                currentTime={media.currentTime}
                trimStart={trimStart}
                trimEnd={trimEnd}
                onTrimStartChange={setTrimStart}
                onTrimEndChange={setTrimEnd}
                formatTime={formatTime}
              />

              <div className="actions">
                <Button onClick={handleOpenFile} variant="secondary">
                  <FolderOpen className="mr-2 h-4 w-4" /> Open Another
                </Button>
                <Button onClick={() => setShowExport(true)}>
                  <Download className="mr-2 h-4 w-4" /> Export Settings
                </Button>
                <Button onClick={handleOpenMultiMerge} variant="secondary">
                  <Scissors className="mr-2 h-4 w-4" /> Merge Clips
                </Button>
                <Button onClick={() => setShowShortcuts(true)} variant="ghost" size="icon" title="Keyboard Shortcuts">
                  <Keyboard className="h-4 w-4" />
                </Button>
              </div>

              <BatchQueue
                queue={batchQueue}
                onRemove={(idx) => setBatchQueue(batchQueue.filter((_, i) => i !== idx))}
                onProcess={processBatch}
                isProcessing={isBatchProcessing}
              />
            </>
          )}
        </main>

        {showExport && (
          <ExportDialog
            onClose={() => setShowExport(false)}
            onExport={handleExport}
            onAddToBatch={handleAddToBatch}
            onCancel={ffmpeg.cancelConversion}
            inputFile={inputFile}
            selectedFormat={selectedFormat}
            onFormatChange={setSelectedFormat}
            selectedPreset={selectedPreset}
            onPresetChange={setSelectedPreset}
            selectedResolution={selectedResolution}
            onResolutionChange={setSelectedResolution}
            selectedSubtitle={selectedSubtitle}
            onOpenSubtitle={handleOpenSubtitle}
            onClearSubtitle={() => setSelectedSubtitle(null)}
            filterSettings={filterSettings}
            onFilterChange={setFilterSettings}
            overlaySettings={overlaySettings}
            onOverlayChange={setOverlaySettings}
            audioVolume={audioVolume}
            onAudioVolumeChange={setAudioVolume}
            playbackSpeed={playbackSpeed}
            onPlaybackSpeedChange={setPlaybackSpeed}
            hwAccel={hwAccel}
            onHwAccelChange={setHwAccel}
            isGif={isGif}
            onIsGifChange={setIsGif}
            isThumbnail={isThumbnail}
            onIsThumbnailChange={setIsThumbnail}
            trimStart={trimStart}
            trimEnd={trimEnd}
            duration={mediaInfo?.duration || 0}
            isConverting={ffmpeg.isConverting}
            progress={ffmpeg.progress}
            mediaInfo={mediaInfo}
            formatTime={formatTime}
            // New props
            audioFilters={audioFilters}
            onAudioFiltersChange={setAudioFilters}
            videoTransform={videoTransform}
            onVideoTransformChange={setVideoTransform}
          />
        )}

        {showMerge && (
          <MergeDialog
            queue={mergeQueue}
            onClose={() => setShowMerge(false)}
            onRemove={(idx) => setMergeQueue(mergeQueue.filter((_, i) => i !== idx))}
            onAddMore={async () => {
              const files = await open({ multiple: true });
              if (files && Array.isArray(files)) setMergeQueue([...mergeQueue, ...files]);
            }}
            onMerge={handleMergeAction}
            isConverting={ffmpeg.isConverting}
          />
        )}

        <ShortcutHelpDialog
          isOpen={showShortcuts}
          onClose={() => setShowShortcuts(false)}
        />

        <ErrorDialog
          error={currentError}
          onClose={() => setCurrentError(null)}
          onRetry={inputFile ? () => handleFileDrop([inputFile]) : undefined}
        />
      </div>
    </ErrorBoundary>
  );
}

export default App;

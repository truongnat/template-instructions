import { useState, useMemo } from 'react';
import { X, Download, Volume2, FastForward, Cpu, ImageIcon, Layers, Music, Type, Scissors } from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "./ui/select";
import { Progress, PRESETS, OUTPUT_FORMATS, MediaInfo, FilterSettings, OverlaySettings, AudioFilterSettings, VideoTransformSettings, ConvertOptions } from '../types';
import { usePreview } from '../hooks/usePreview';
import { FilterPanel } from './FilterPanel';
import { OverlayPanel } from './OverlayPanel';
import { AudioFiltersPanel } from './AudioFiltersPanel';
import { VideoTransformPanel } from './VideoTransformPanel';

interface ExportDialogProps {
    onClose: () => void;
    onExport: () => void;
    onAddToBatch: () => void;
    onCancel: () => void;
    inputFile: string | null;
    selectedFormat: typeof OUTPUT_FORMATS[0];
    onFormatChange: (format: typeof OUTPUT_FORMATS[0]) => void;
    selectedPreset: keyof typeof PRESETS;
    onPresetChange: (preset: keyof typeof PRESETS) => void;
    selectedResolution: { w: number | null, h: number | null };
    onResolutionChange: (res: { w: number | null, h: number | null }) => void;
    selectedSubtitle: string | null;
    onOpenSubtitle: () => void;
    onClearSubtitle: () => void;

    // Settings
    filterSettings: FilterSettings;
    onFilterChange: (settings: FilterSettings) => void;
    overlaySettings: OverlaySettings;
    onOverlayChange: (settings: OverlaySettings) => void;

    // New Settings
    audioFilters: AudioFilterSettings;
    onAudioFiltersChange: (settings: AudioFilterSettings) => void;
    videoTransform: VideoTransformSettings;
    onVideoTransformChange: (settings: VideoTransformSettings) => void;

    audioVolume: number;
    onAudioVolumeChange: (vol: number) => void;
    playbackSpeed: number;
    onPlaybackSpeedChange: (speed: number) => void;
    hwAccel: boolean;
    onHwAccelChange: (enabled: boolean) => void;
    isGif: boolean;
    onIsGifChange: (isGif: boolean) => void;
    isThumbnail: boolean;
    onIsThumbnailChange: (isThumbnail: boolean) => void;

    trimStart: number;
    trimEnd: number;
    duration: number;
    isConverting: boolean;
    progress: Progress | null;
    mediaInfo: MediaInfo | null;
    formatTime: (seconds: number) => string;
}

type Tab = 'general' | 'video' | 'audio' | 'overlays';

export function ExportDialog({
    onClose,
    onExport,
    onAddToBatch,
    onCancel,
    inputFile,
    selectedFormat,
    onFormatChange,
    selectedPreset,
    onPresetChange,
    selectedResolution,
    onResolutionChange,
    selectedSubtitle,
    onOpenSubtitle,
    onClearSubtitle,
    filterSettings,
    onFilterChange,
    overlaySettings,
    onOverlayChange,
    audioFilters,
    onAudioFiltersChange,
    videoTransform,
    onVideoTransformChange,
    audioVolume,
    onAudioVolumeChange,
    playbackSpeed,
    onPlaybackSpeedChange,
    hwAccel,
    onHwAccelChange,
    isGif,
    onIsGifChange,
    trimStart,
    trimEnd,
    duration,
    isConverting,
    progress,
    mediaInfo,
    formatTime
}: ExportDialogProps) {
    const [activeTab, setActiveTab] = useState<Tab>('general');
    const [previewTime, setPreviewTime] = useState(0);

    const isAudioOnly = !!selectedFormat.audioOnly;

    // Use useMemo to avoid reconstructing options on every render unless dependencies change
    const previewOptions: ConvertOptions = useMemo(() => ({
        input: inputFile || '',
        output: 'preview.jpg', // Dummy output
        width: selectedResolution.w ?? undefined,
        height: selectedResolution.h ?? undefined,
        filters: filterSettings,
        overlays: overlaySettings,
        video_transform: videoTransform,
        // Crucial: ensure audio filters don't break preview generation
        // audio_filters: audioFilters, 
        // We generally shouldn't pass audio filters for image preview as it might complicate the pipe
        // But the backend filters them out anyway for generate_preview
        subtitle_path: selectedSubtitle || undefined,
        start_time: trimStart,
        end_time: trimEnd > 0 ? trimEnd : undefined,
        audio_only: false,
    }), [inputFile, selectedResolution, filterSettings, overlaySettings, videoTransform, selectedSubtitle, trimStart, trimEnd]);

    const { previewUrl, isLoading: isPreviewLoading, error: previewError } = usePreview(previewOptions, previewTime);

    return (
        <div className="modal-overlay">
            <div className="modal output-dialog">
                <div className="modal-header">
                    <h2>Export Settings</h2>
                    <Button variant="ghost" size="icon" onClick={onClose} disabled={isConverting}>
                        <X size={20} />
                    </Button>
                </div>

                <div className="modal-tabs">
                    <button
                        className={`tab-btn ${activeTab === 'general' ? 'active' : ''}`}
                        onClick={() => setActiveTab('general')}
                    >
                        General
                    </button>
                    {!isAudioOnly && (
                        <button
                            className={`tab-btn ${activeTab === 'video' ? 'active' : ''}`}
                            onClick={() => setActiveTab('video')}
                        >
                            <Layers size={14} /> Video Effects
                        </button>
                    )}
                    <button
                        className={`tab-btn ${activeTab === 'audio' ? 'active' : ''}`}
                        onClick={() => setActiveTab('audio')}
                    >
                        <Music size={14} /> Audio
                    </button>
                    {!isAudioOnly && (
                        <button
                            className={`tab-btn ${activeTab === 'overlays' ? 'active' : ''}`}
                            onClick={() => setActiveTab('overlays')}
                        >
                            <Type size={14} /> Overlays
                        </button>
                    )}
                </div>

                <div className="modal-body scrollable">
                    {activeTab === 'general' && (
                        <div className="general-tab">
                            {/* Format */}
                            <div className="form-group">
                                <Label>Output Format</Label>
                                <Select
                                    value={selectedFormat.value}
                                    onValueChange={(val) => onFormatChange(
                                        OUTPUT_FORMATS.find(f => f.value === val) || OUTPUT_FORMATS[0]
                                    )}
                                    disabled={isConverting}
                                >
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select format" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {OUTPUT_FORMATS.map(f => (
                                            <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {/* Quality Preset */}
                            {!isAudioOnly && (
                                <div className="form-group">
                                    <label>Quality</label>
                                    <div className="grid grid-cols-3 gap-2">
                                        {Object.entries(PRESETS).map(([key, preset]) => (
                                            <Button
                                                key={key}
                                                variant={selectedPreset === key ? "default" : "outline"}
                                                size="sm"
                                                onClick={() => onPresetChange(key as keyof typeof PRESETS)}
                                                disabled={isConverting}
                                                className="w-full"
                                            >
                                                {preset.label}
                                            </Button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Resolution */}
                            {!isAudioOnly && (
                                <div className="form-group">
                                    <Label>Resolution</Label>
                                    <Select
                                        value={`${selectedResolution.w ?? 'original'}x${selectedResolution.h ?? 'original'}`}
                                        onValueChange={(val) => {
                                            if (val === 'original') {
                                                onResolutionChange({ w: null, h: null });
                                            } else {
                                                const [w, h] = val.split('x').map(Number);
                                                onResolutionChange({ w, h });
                                            }
                                        }}
                                        disabled={isConverting}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select resolution" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="original">
                                                Original ({mediaInfo?.width ? `${mediaInfo.width}x${mediaInfo.height}` : 'Auto'})
                                            </SelectItem>
                                            <SelectItem value="1920x1080">1080p (1920x1080)</SelectItem>
                                            <SelectItem value="1280x720">720p (1280x720)</SelectItem>
                                            <SelectItem value="854x480">480p (854x480)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            )}

                            {/* Basic Audio/Speed (can also remain here or move to Audio tab) */}
                            <div className="advanced-settings grid grid-cols-2 gap-4">
                                <div className="form-group">
                                    <Label className="flex items-center gap-2"><Volume2 size={14} /> Master Volume ({Math.round(audioVolume * 100)}%)</Label>
                                    <Slider
                                        min={0}
                                        max={2}
                                        step={0.1}
                                        value={[audioVolume]}
                                        onValueChange={(vals) => onAudioVolumeChange(vals[0])}
                                        disabled={isConverting}
                                        className="py-4"
                                    />
                                </div>
                                <div className="form-group">
                                    <Label className="flex items-center gap-2"><FastForward size={14} /> Speed ({playbackSpeed}x)</Label>
                                    <Select
                                        value={playbackSpeed.toString()}
                                        onValueChange={(val) => onPlaybackSpeedChange(parseFloat(val))}
                                        disabled={isConverting}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select speed" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="0.5">0.5x</SelectItem>
                                            <SelectItem value="1">1.0x</SelectItem>
                                            <SelectItem value="1.5">1.5x</SelectItem>
                                            <SelectItem value="2">2.0x</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            {/* Hardware & Extras */}
                            <div className="checkbox-group grid grid-cols-2 gap-4 mt-4">
                                <div className="flex items-center space-x-2">
                                    <Switch
                                        id="hw-accel"
                                        checked={hwAccel}
                                        onCheckedChange={onHwAccelChange}
                                        disabled={isConverting}
                                    />
                                    <Label htmlFor="hw-accel" className="flex items-center gap-1 cursor-pointer">
                                        <Cpu size={14} /> Hardware Acceleration
                                    </Label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <Switch
                                        id="export-gif"
                                        checked={isGif}
                                        onCheckedChange={onIsGifChange}
                                        disabled={isConverting || !!selectedFormat.audioOnly}
                                    />
                                    <Label htmlFor="export-gif" className="flex items-center gap-1 cursor-pointer">
                                        <ImageIcon size={14} /> Export as GIF
                                    </Label>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'video' && !isAudioOnly && (
                        <div className="video-tab">
                            {/* Preview Section */}
                            <div className="preview-section" style={{ marginBottom: '20px', padding: '15px', background: 'rgba(0,0,0,0.2)', borderRadius: '8px' }}>
                                <h3 style={{ marginBottom: '10px', fontSize: '0.9rem', color: '#aaa' }}>Preview</h3>
                                <div className="preview-container" style={{
                                    width: '100%',
                                    aspectRatio: '16/9',
                                    background: '#000',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    borderRadius: '4px',
                                    marginBottom: '10px',
                                    position: 'relative',
                                    overflow: 'hidden'
                                }}>
                                    {isPreviewLoading && <div style={{ color: '#888' }}>Generating Preview...</div>}
                                    {previewError && <div style={{ color: '#ff4444', fontSize: '0.8rem', padding: '10px', textAlign: 'center' }}>Error: {previewError}</div>}
                                    {previewUrl && !isPreviewLoading && !previewError && (
                                        <img src={previewUrl} alt="Preview" style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                                    )}
                                    {!previewUrl && !isPreviewLoading && !previewError && <div style={{ color: '#444' }}>No Preview</div>}
                                </div>

                                <div className="preview-controls" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <span style={{ fontSize: '0.75rem', minWidth: '40px' }}>{formatTime(previewTime)}</span>
                                    <input
                                        type="range"
                                        min={0}
                                        max={duration || 60}
                                        step={0.1}
                                        value={previewTime}
                                        onChange={(e) => setPreviewTime(parseFloat(e.target.value))}
                                        style={{ flex: 1 }}
                                    />
                                    <span style={{ fontSize: '0.75rem', minWidth: '40px', textAlign: 'right' }}>{formatTime(duration)}</span>
                                </div>
                            </div>

                            <div className="panels-container">
                                <VideoTransformPanel
                                    transform={videoTransform}
                                    onChange={onVideoTransformChange}
                                    disabled={isConverting}
                                    duration={duration}
                                    videoWidth={mediaInfo?.width || 1920}
                                    videoHeight={mediaInfo?.height || 1080}
                                />
                                <FilterPanel
                                    filters={filterSettings}
                                    onChange={onFilterChange}
                                    disabled={isConverting}
                                />
                            </div>
                        </div>
                    )}

                    {activeTab === 'audio' && (
                        <div className="audio-tab">
                            <AudioFiltersPanel
                                filters={audioFilters}
                                onChange={onAudioFiltersChange}
                                disabled={isConverting}
                                duration={duration}
                            />
                        </div>
                    )}

                    {activeTab === 'overlays' && !isAudioOnly && (
                        <div className="overlays-tab">
                            <div className="form-group">
                                <label>Subtitle File</label>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <input
                                        type="text"
                                        readOnly
                                        value={selectedSubtitle ? selectedSubtitle.split(/[\\/]/).pop() : 'None'}
                                        style={{ flex: 1, fontSize: '0.75rem' }}
                                    />
                                    <Button onClick={onOpenSubtitle} variant="secondary" size="sm" disabled={isConverting}>
                                        Browse
                                    </Button>
                                    {selectedSubtitle && (
                                        <Button onClick={onClearSubtitle} variant="destructive" size="sm" disabled={isConverting}>
                                            <X size={14} />
                                        </Button>
                                    )}
                                </div>
                            </div>
                            <OverlayPanel
                                overlays={overlaySettings}
                                onChange={onOverlayChange}
                            />
                        </div>
                    )}

                    {/* Progress & Trim Info always visible at bottom of body? Or sticking to footer? */}
                    {(trimStart > 0 || trimEnd < duration) && (
                        <div className="trim-preview">
                            <Scissors size={14} />
                            <span>
                                Trimming: {formatTime(trimStart)} → {formatTime(trimEnd)} ({formatTime(trimEnd - trimStart)})
                            </span>
                        </div>
                    )}

                    {isConverting && progress && (
                        <div className="progress-section">
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${progress.percent}%` }}
                                />
                            </div>
                            <div className="progress-info">
                                <span>{progress.percent.toFixed(1)}%</span>
                                <span>{progress.speed}</span>
                                <span>{progress.size}</span>
                            </div>
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    {isConverting ? (
                        <Button onClick={onCancel} variant="destructive">
                            Cancel
                        </Button>
                    ) : (
                        <>
                            <Button onClick={onClose} variant="secondary">
                                Cancel
                            </Button>
                            <Button onClick={onExport}>
                                <Download className="mr-2 h-4 w-4" /> Export Now
                            </Button>
                            <Button onClick={onAddToBatch} variant="outline" className="text-accent border-accent hover:text-accent hover:bg-accent/10">
                                Add to Queue
                            </Button>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

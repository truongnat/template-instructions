
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { VideoTransformSettings } from '../types';
import {
    RotateCw,
    Crop,
    FlipHorizontal,
    FlipVertical,
    Layers,
    Sparkles,
    Clock,
    RotateCcw
} from 'lucide-react';

interface VideoTransformPanelProps {
    transform: VideoTransformSettings;
    onChange: (transform: VideoTransformSettings) => void;
    disabled?: boolean;
    duration?: number;
    videoWidth?: number;
    videoHeight?: number;
}

export function VideoTransformPanel({
    transform,
    onChange,
    disabled,
    duration = 0,
    videoWidth = 1920,
    videoHeight = 1080
}: VideoTransformPanelProps) {
    const handleChange = <K extends keyof VideoTransformSettings>(key: K, value: VideoTransformSettings[K]) => {
        onChange({ ...transform, [key]: value });
    };

    const resetTransform = () => {
        onChange({
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
        });
    };

    const rotationOptions: Array<0 | 90 | 180 | 270> = [0, 90, 180, 270];

    // Calculate max crop values (prevent cropping more than half the video)
    const maxCropH = Math.floor(videoWidth / 3);
    const maxCropV = Math.floor(videoHeight / 3);

    return (
        <div className="panel video-transform-panel p-4 space-y-6">
            <div className="panel-header flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2"><Layers size={18} /> Video Transform</h3>
                <Button variant="ghost" size="sm" onClick={resetTransform} disabled={disabled}>
                    <RotateCcw size={14} className="mr-2" /> Reset
                </Button>
            </div>

            {/* Rotation */}
            <div className="space-y-2">
                <Label className="flex items-center gap-2 font-medium">
                    <RotateCw size={16} /> Rotation
                </Label>
                <div className="flex gap-2">
                    {rotationOptions.map((angle) => (
                        <Button
                            key={angle}
                            variant={transform.rotation === angle ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => handleChange('rotation', angle)}
                            disabled={disabled}
                            className={transform.rotation === angle ? "flex-1" : "flex-1 text-muted-foreground hover:text-foreground"}
                        >
                            {angle}°
                        </Button>
                    ))}
                </div>
            </div>

            {/* Flip */}
            <div className="space-y-2">
                <Label className="flex items-center gap-2 font-medium">
                    <FlipHorizontal size={16} /> Flip / Mirror
                </Label>
                <div className="flex gap-2">
                    <Button
                        variant={transform.flipHorizontal ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => handleChange('flipHorizontal', !transform.flipHorizontal)}
                        disabled={disabled}
                        className="flex-1"
                    >
                        <FlipHorizontal size={16} className="mr-2" />
                        Horizontal
                    </Button>
                    <Button
                        variant={transform.flipVertical ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => handleChange('flipVertical', !transform.flipVertical)}
                        disabled={disabled}
                        className="flex-1"
                    >
                        <FlipVertical size={16} className="mr-2" />
                        Vertical
                    </Button>
                </div>
            </div>

            {/* Crop */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-4">
                    <Label htmlFor="crop" className="flex items-center gap-2 font-medium cursor-pointer">
                        <Crop size={16} /> Crop Video
                    </Label>
                    <Switch
                        id="crop"
                        checked={transform.cropEnabled}
                        onCheckedChange={(checked) => handleChange('cropEnabled', checked)}
                        disabled={disabled}
                    />
                </div>
                {transform.cropEnabled && (
                    <div className="crop-controls space-y-4">
                        <div className="crop-grid grid grid-rows-3 gap-2">
                            {/* Top row */}
                            <div className="flex justify-center">
                                <div className="w-1/2 space-y-1">
                                    <Label className="text-xs text-center block">Top ({transform.cropTop}px)</Label>
                                    <Slider
                                        min={0}
                                        max={maxCropV}
                                        step={2}
                                        value={[transform.cropTop]}
                                        onValueChange={(vals) => handleChange('cropTop', vals[0])}
                                        disabled={disabled}
                                    />
                                </div>
                            </div>

                            {/* Middle row */}
                            <div className="flex items-center gap-4">
                                <div className="w-1/4 space-y-1">
                                    <Label className="text-xs text-center block">Left ({transform.cropLeft}px)</Label>
                                    <Slider
                                        min={0}
                                        max={maxCropH}
                                        step={2}
                                        value={[transform.cropLeft]}
                                        onValueChange={(vals) => handleChange('cropLeft', vals[0])}
                                        disabled={disabled}
                                    />
                                </div>
                                <div className="flex-1 aspect-video relative bg-muted/20 border border-muted rounded overflow-hidden flex items-center justify-center">
                                    <div
                                        className="absolute inset-0 border-2 border-primary bg-primary/10"
                                        style={{
                                            top: `${(transform.cropTop / videoHeight) * 100}%`,
                                            bottom: `${(transform.cropBottom / videoHeight) * 100}%`,
                                            left: `${(transform.cropLeft / videoWidth) * 100}%`,
                                            right: `${(transform.cropRight / videoWidth) * 100}%`,
                                        }}
                                    />
                                    <span className="text-xs text-muted-foreground z-10">Preview</span>
                                </div>
                                <div className="w-1/4 space-y-1">
                                    <Label className="text-xs text-center block">Right ({transform.cropRight}px)</Label>
                                    <Slider
                                        min={0}
                                        max={maxCropH}
                                        step={2}
                                        value={[transform.cropRight]}
                                        onValueChange={(vals) => handleChange('cropRight', vals[0])}
                                        disabled={disabled}
                                    />
                                </div>
                            </div>

                            {/* Bottom row */}
                            <div className="flex justify-center">
                                <div className="w-1/2 space-y-1">
                                    <Label className="text-xs text-center block">Bottom ({transform.cropBottom}px)</Label>
                                    <Slider
                                        min={0}
                                        max={maxCropV}
                                        step={2}
                                        value={[transform.cropBottom]}
                                        onValueChange={(vals) => handleChange('cropBottom', vals[0])}
                                        disabled={disabled}
                                    />
                                </div>
                            </div>
                        </div>
                        <div className="text-center text-sm text-muted-foreground">
                            Output: {videoWidth - transform.cropLeft - transform.cropRight} x {videoHeight - transform.cropTop - transform.cropBottom}
                        </div>
                    </div>
                )}
            </div>

            {/* Deinterlace */}
            <div className="panel p-4 rounded-lg bg-card border border-border flex items-center justify-between">
                <Label htmlFor="deinterlace" className="flex items-center gap-2 font-medium cursor-pointer">
                    <Layers size={16} /> Deinterlace
                </Label>
                <Switch
                    id="deinterlace"
                    checked={transform.deinterlace}
                    onCheckedChange={(checked) => handleChange('deinterlace', checked)}
                    disabled={disabled}
                />
            </div>

            {/* Denoise */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-2">
                    <Label htmlFor="denoise" className="flex items-center gap-2 font-medium cursor-pointer">
                        <Sparkles size={16} /> Video Denoise
                    </Label>
                    <Switch
                        id="denoise"
                        checked={transform.denoise}
                        onCheckedChange={(checked) => handleChange('denoise', checked)}
                        disabled={disabled}
                    />
                </div>
                {transform.denoise && (
                    <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                            <Label>Strength</Label>
                            <span className="text-sm text-muted-foreground">{transform.denoiseStrength}</span>
                        </div>
                        <Slider
                            min={1}
                            max={10}
                            step={1}
                            value={[transform.denoiseStrength]}
                            onValueChange={(vals) => handleChange('denoiseStrength', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                )}
            </div>

            {/* Video Fade */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center gap-2 mb-4">
                    <Clock size={16} />
                    <h4 className="font-medium m-0">Video Fade</h4>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label>Fade In ({transform.fadeInDuration.toFixed(1)}s)</Label>
                        <Slider
                            min={0}
                            max={Math.min(duration / 2, 5)}
                            step={0.1}
                            value={[transform.fadeInDuration]}
                            onValueChange={(vals) => handleChange('fadeInDuration', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Fade Out ({transform.fadeOutDuration.toFixed(1)}s)</Label>
                        <Slider
                            min={0}
                            max={Math.min(duration / 2, 5)}
                            step={0.1}
                            value={[transform.fadeOutDuration]}
                            onValueChange={(vals) => handleChange('fadeOutDuration', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

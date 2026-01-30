import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { AudioFilterSettings } from '../types';
import {
    Volume2,
    SlidersHorizontal,
    Waves,
    Gauge,
    Clock,
    RotateCcw
} from 'lucide-react';

interface AudioFiltersPanelProps {
    filters: AudioFilterSettings;
    onChange: (filters: AudioFilterSettings) => void;
    disabled?: boolean;
    duration?: number;
}

export function AudioFiltersPanel({ filters, onChange, disabled, duration = 0 }: AudioFiltersPanelProps) {
    const handleChange = <K extends keyof AudioFilterSettings>(key: K, value: AudioFilterSettings[K]) => {
        onChange({ ...filters, [key]: value });
    };

    const resetFilters = () => {
        onChange({
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
        });
    };

    return (
        <div className="panel audio-filters-panel p-4 space-y-6">
            <div className="panel-header flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center gap-2"><Volume2 size={18} /> Audio Processing</h3>
                <Button variant="ghost" size="sm" onClick={resetFilters} disabled={disabled}>
                    <RotateCcw size={14} className="mr-2" /> Reset
                </Button>
            </div>

            {/* Normalize / Loudness */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-4">
                    <Label htmlFor="normalize" className="flex items-center gap-2 font-medium cursor-pointer">
                        <Gauge size={16} /> Normalize Audio (EBU R128)
                    </Label>
                    <Switch
                        id="normalize"
                        checked={filters.normalize}
                        onCheckedChange={(checked) => handleChange('normalize', checked)}
                        disabled={disabled}
                    />
                </div>
                {filters.normalize && (
                    <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                            <Label>Target LUFS</Label>
                            <span className="text-sm text-muted-foreground">{filters.targetLufs} LUFS</span>
                        </div>
                        <Slider
                            min={-24}
                            max={-14}
                            step={1}
                            value={[filters.targetLufs]}
                            onValueChange={(vals) => handleChange('targetLufs', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                )}
            </div>

            {/* Equalizer */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <SlidersHorizontal size={16} />
                        <h4 className="font-medium m-0">Equalizer</h4>
                    </div>
                    <Switch
                        checked={filters.eqEnabled}
                        onCheckedChange={(checked) => handleChange('eqEnabled', checked)}
                        disabled={disabled}
                    />
                </div>
                {filters.eqEnabled && (
                    <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <Label className="text-xs">Bass ({filters.bassGain > 0 ? '+' : ''}{filters.bassGain}dB)</Label>
                            <Slider
                                min={-20}
                                max={20}
                                step={1}
                                value={[filters.bassGain]}
                                onValueChange={(vals) => handleChange('bassGain', vals[0])}
                                disabled={disabled}
                                orientation="vertical"
                                className="h-24"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs">Mid ({filters.midGain > 0 ? '+' : ''}{filters.midGain}dB)</Label>
                            <Slider
                                min={-20}
                                max={20}
                                step={1}
                                value={[filters.midGain]}
                                onValueChange={(vals) => handleChange('midGain', vals[0])}
                                disabled={disabled}
                                orientation="vertical"
                                className="h-24"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label className="text-xs">Treble ({filters.trebleGain > 0 ? '+' : ''}{filters.trebleGain}dB)</Label>
                            <Slider
                                min={-20}
                                max={20}
                                step={1}
                                value={[filters.trebleGain]}
                                onValueChange={(vals) => handleChange('trebleGain', vals[0])}
                                disabled={disabled}
                                orientation="vertical"
                                className="h-24"
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Noise Reduction */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-2">
                    <Label htmlFor="noise-reduction" className="flex items-center gap-2 font-medium cursor-pointer">
                        <Waves size={16} /> Noise Reduction
                    </Label>
                    <Switch
                        id="noise-reduction"
                        checked={filters.noiseReduction}
                        onCheckedChange={(checked) => handleChange('noiseReduction', checked)}
                        disabled={disabled}
                    />
                </div>
                {filters.noiseReduction && (
                    <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                            <Label>Strength</Label>
                            <span className="text-sm text-muted-foreground">{filters.noiseReductionStrength}%</span>
                        </div>
                        <Slider
                            min={0}
                            max={100}
                            step={5}
                            value={[filters.noiseReductionStrength]}
                            onValueChange={(vals) => handleChange('noiseReductionStrength', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                )}
            </div>

            {/* Compressor */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center justify-between mb-2">
                    <Label htmlFor="compressor" className="flex items-center gap-2 font-medium cursor-pointer">
                        <Gauge size={16} /> Dynamic Compressor
                    </Label>
                    <Switch
                        id="compressor"
                        checked={filters.compressorEnabled}
                        onCheckedChange={(checked) => handleChange('compressorEnabled', checked)}
                        disabled={disabled}
                    />
                </div>
                {filters.compressorEnabled && (
                    <div className="grid grid-cols-2 gap-6 mt-4">
                        <div className="space-y-2">
                            <Label>Threshold ({filters.compressorThreshold}dB)</Label>
                            <Slider
                                min={-50}
                                max={0}
                                step={1}
                                value={[filters.compressorThreshold]}
                                onValueChange={(vals) => handleChange('compressorThreshold', vals[0])}
                                disabled={disabled}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Ratio ({filters.compressorRatio}:1)</Label>
                            <Slider
                                min={1}
                                max={20}
                                step={1}
                                value={[filters.compressorRatio]}
                                onValueChange={(vals) => handleChange('compressorRatio', vals[0])}
                                disabled={disabled}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Fade In/Out */}
            <div className="panel p-4 rounded-lg bg-card border border-border">
                <div className="flex items-center gap-2 mb-4">
                    <Clock size={16} />
                    <h4 className="font-medium m-0">Audio Fade</h4>
                </div>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <Label>Fade In ({filters.fadeInDuration.toFixed(1)}s)</Label>
                        <Slider
                            min={0}
                            max={Math.min(duration / 2, 10)}
                            step={0.1}
                            value={[filters.fadeInDuration]}
                            onValueChange={(vals) => handleChange('fadeInDuration', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                    <div className="space-y-2">
                        <Label>Fade Out ({filters.fadeOutDuration.toFixed(1)}s)</Label>
                        <Slider
                            min={0}
                            max={Math.min(duration / 2, 10)}
                            step={0.1}
                            value={[filters.fadeOutDuration]}
                            onValueChange={(vals) => handleChange('fadeOutDuration', vals[0])}
                            disabled={disabled}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

import { FilterSettings } from '../types';
import { Sun, Contrast, Droplets, Wind, Zap, Palette, CircleDot, Target } from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Label } from './ui/label';
import { Switch } from './ui/switch';

interface FilterPanelProps {
    filters: FilterSettings;
    onChange: (filters: FilterSettings) => void;
    disabled?: boolean;
}

export function FilterPanel({ filters, onChange, disabled }: FilterPanelProps) {
    const handleChange = <K extends keyof FilterSettings>(key: K, value: FilterSettings[K]) => {
        onChange({ ...filters, [key]: value });
    };

    const resetFilters = () => {
        onChange({
            brightness: 0,
            contrast: 1,
            saturation: 1,
            blur: 0,
            sharpen: 0,
            gamma: 1,
            hue: 0,
            vignette: false,
            vignetteStrength: 0.3,
        });
    };

    return (
        <div className="panel filter-panel p-4 space-y-6">
            <div className="panel-header flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Video Filters</h3>
                <Button variant="ghost" size="sm" onClick={resetFilters} disabled={disabled}>Reset</Button>
            </div>

            <div className="space-y-4">
                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Sun size={16} /> Brightness</Label>
                        <span className="text-sm text-muted-foreground">{filters.brightness.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={-1}
                        max={1}
                        step={0.1}
                        value={[filters.brightness]}
                        onValueChange={(vals) => handleChange('brightness', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Contrast size={16} /> Contrast</Label>
                        <span className="text-sm text-muted-foreground">{filters.contrast.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={0}
                        max={2}
                        step={0.1}
                        value={[filters.contrast]}
                        onValueChange={(vals) => handleChange('contrast', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Droplets size={16} /> Saturation</Label>
                        <span className="text-sm text-muted-foreground">{filters.saturation.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={0}
                        max={3}
                        step={0.1}
                        value={[filters.saturation]}
                        onValueChange={(vals) => handleChange('saturation', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Target size={16} /> Gamma</Label>
                        <span className="text-sm text-muted-foreground">{filters.gamma.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={0.1}
                        max={3}
                        step={0.1}
                        value={[filters.gamma]}
                        onValueChange={(vals) => handleChange('gamma', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Palette size={16} /> Hue</Label>
                        <span className="text-sm text-muted-foreground">{filters.hue}°</span>
                    </div>
                    <Slider
                        min={-180}
                        max={180}
                        step={5}
                        value={[filters.hue]}
                        onValueChange={(vals) => handleChange('hue', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Wind size={16} /> Blur</Label>
                        <span className="text-sm text-muted-foreground">{filters.blur.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={0}
                        max={10}
                        step={0.5}
                        value={[filters.blur]}
                        onValueChange={(vals) => handleChange('blur', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="filter-group">
                    <div className="flex items-center justify-between mb-2">
                        <Label className="flex items-center gap-2"><Zap size={16} /> Sharpen</Label>
                        <span className="text-sm text-muted-foreground">{filters.sharpen.toFixed(1)}</span>
                    </div>
                    <Slider
                        min={0}
                        max={10}
                        step={0.5}
                        value={[filters.sharpen]}
                        onValueChange={(vals) => handleChange('sharpen', vals[0])}
                        disabled={disabled}
                    />
                </div>

                <div className="panel p-4 rounded-lg bg-card border border-border">
                    <div className="flex items-center justify-between mb-2">
                        <Label htmlFor="vignette" className="flex items-center gap-2 font-medium cursor-pointer">
                            <CircleDot size={16} /> Vignette Effect
                        </Label>
                        <Switch
                            id="vignette"
                            checked={filters.vignette}
                            onCheckedChange={(checked) => handleChange('vignette', checked)}
                            disabled={disabled}
                        />
                    </div>
                    {filters.vignette && (
                        <div className="mt-4">
                            <div className="flex items-center justify-between mb-2">
                                <Label>Strength</Label>
                                <span className="text-sm text-muted-foreground">{(filters.vignetteStrength * 100).toFixed(0)}%</span>
                            </div>
                            <Slider
                                min={0.1}
                                max={1}
                                step={0.05}
                                value={[filters.vignetteStrength]}
                                onValueChange={(vals) => handleChange('vignetteStrength', vals[0])}
                                disabled={disabled}
                            />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

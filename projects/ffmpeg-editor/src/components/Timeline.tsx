import { Scissors } from 'lucide-react';

interface TimelineProps {
    duration: number;
    currentTime: number;
    trimStart: number;
    trimEnd: number;
    onTrimStartChange: (val: number) => void;
    onTrimEndChange: (val: number) => void;
    formatTime: (seconds: number) => string;
}

export function Timeline({
    duration,
    currentTime,
    trimStart,
    trimEnd,
    onTrimStartChange,
    onTrimEndChange,
    formatTime
}: TimelineProps) {
    const durationSafe = duration || 1;

    return (
        <div className="trim-section">
            <h3><Scissors size={16} /> Visual Timeline</h3>
            <div className="timeline-visual">
                <div
                    className="trim-overlay"
                    style={{
                        left: `${(trimStart / durationSafe) * 100}%`,
                        width: `${((trimEnd - trimStart) / durationSafe) * 100}%`
                    }}
                />
                <div
                    className="playhead"
                    style={{ left: `${(currentTime / durationSafe) * 100}%` }}
                />
            </div>

            <div className="trim-controls">
                <div className="trim-inputs">
                    <label>
                        Start:
                        <input
                            type="number"
                            min={0}
                            max={trimEnd}
                            step={0.1}
                            value={trimStart}
                            onChange={(e) => onTrimStartChange(parseFloat(e.target.value))}
                        />
                    </label>
                    <label>
                        End:
                        <input
                            type="number"
                            min={trimStart}
                            max={duration}
                            step={0.1}
                            value={trimEnd}
                            onChange={(e) => onTrimEndChange(parseFloat(e.target.value))}
                        />
                    </label>
                </div>
                <div className="trim-info-text">
                    <span>Selection: {formatTime(trimEnd - trimStart)}</span>
                </div>
            </div>
        </div>
    );
}

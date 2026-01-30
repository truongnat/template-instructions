import { FileVideo, Maximize2 } from 'lucide-react';
import { MediaInfo } from '../types';

interface MediaInfoViewProps {
    info: MediaInfo;
    formatTime: (seconds: number) => string;
}

export function MediaInfoView({ info, formatTime }: MediaInfoViewProps) {
    return (
        <div className="media-info">
            <div className="info-item">
                <FileVideo size={16} />
                <span>{info.format} • {info.codec}</span>
            </div>
            {info.width && (
                <div className="info-item">
                    <Maximize2 size={16} />
                    <span>{info.width}×{info.height}</span>
                </div>
            )}
            <div className="info-item">
                <span>Duration: {formatTime(info.duration)}</span>
            </div>
        </div>
    );
}

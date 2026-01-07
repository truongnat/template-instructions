import { FolderOpen, Film, Music, FileText, Image } from 'lucide-react';
import { useDragAndDrop } from '../hooks/useDragAndDrop';

interface EnhancedDropZoneProps {
    onVideoFiles?: (files: string[]) => void;
    onAudioFiles?: (files: string[]) => void;
    onSubtitleFiles?: (files: string[]) => void;
    onImageFiles?: (files: string[]) => void;
    onClick?: () => void;
}

export function EnhancedDropZone({
    onVideoFiles,
    onAudioFiles,
    onSubtitleFiles,
    onImageFiles,
    onClick
}: EnhancedDropZoneProps) {
    const { isDragging, dropZoneProps } = useDragAndDrop({
        onVideoFiles,
        onAudioFiles,
        onSubtitleFiles,
        onImageFiles
    });

    return (
        <div
            className={`drop-zone enhanced-drop-zone ${isDragging ? 'dragging' : ''}`}
            onClick={onClick}
            {...dropZoneProps}
        >
            {isDragging ? (
                <div className="drop-zone-active">
                    <div className="drop-icons">
                        <Film size={32} className="icon-video" />
                        <Music size={32} className="icon-audio" />
                        <FileText size={32} className="icon-subtitle" />
                        <Image size={32} className="icon-image" />
                    </div>
                    <p className="drop-text">Drop files here!</p>
                    <span className="drop-hint">Videos, Audio, Subtitles, or Images</span>
                </div>
            ) : (
                <>
                    <FolderOpen size={48} />
                    <p>Click or drop a media file</p>
                    <span>Supports MP4, MKV, AVI, MOV, WebM, MP3, WAV...</span>
                    <div className="supported-formats">
                        <span className="format-badge video">Video</span>
                        <span className="format-badge audio">Audio</span>
                        <span className="format-badge subtitle">Subtitles</span>
                        <span className="format-badge image">Images</span>
                    </div>
                </>
            )}
        </div>
    );
}

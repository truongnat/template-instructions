import { useCallback, useState } from 'react';

export interface DragDropOptions {
    accept?: string[];
    onDrop?: (files: string[]) => void;
    onVideoFiles?: (files: string[]) => void;
    onAudioFiles?: (files: string[]) => void;
    onSubtitleFiles?: (files: string[]) => void;
    onImageFiles?: (files: string[]) => void;
}

const VIDEO_EXTENSIONS = ['mp4', 'mkv', 'avi', 'mov', 'webm', 'wmv', 'flv'];
const AUDIO_EXTENSIONS = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'm4a'];
const SUBTITLE_EXTENSIONS = ['srt', 'vtt', 'ass', 'sub'];
const IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'];

export function useDragAndDrop(options: DragDropOptions = {}) {
    const [isDragging, setIsDragging] = useState(false);

    const getExtension = (path: string): string => {
        const parts = path.split('.');
        return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
    };

    const categorizeFiles = useCallback((files: string[]) => {
        const videoFiles: string[] = [];
        const audioFiles: string[] = [];
        const subtitleFiles: string[] = [];
        const imageFiles: string[] = [];
        const otherFiles: string[] = [];

        files.forEach(file => {
            const ext = getExtension(file);
            if (VIDEO_EXTENSIONS.includes(ext)) {
                videoFiles.push(file);
            } else if (AUDIO_EXTENSIONS.includes(ext)) {
                audioFiles.push(file);
            } else if (SUBTITLE_EXTENSIONS.includes(ext)) {
                subtitleFiles.push(file);
            } else if (IMAGE_EXTENSIONS.includes(ext)) {
                imageFiles.push(file);
            } else {
                otherFiles.push(file);
            }
        });

        return { videoFiles, audioFiles, subtitleFiles, imageFiles, otherFiles };
    }, []);

    const handleDrop = useCallback((files: string[]) => {
        const categorized = categorizeFiles(files);

        options.onDrop?.(files);

        if (categorized.videoFiles.length > 0) {
            options.onVideoFiles?.(categorized.videoFiles);
        }
        if (categorized.audioFiles.length > 0) {
            options.onAudioFiles?.(categorized.audioFiles);
        }
        if (categorized.subtitleFiles.length > 0) {
            options.onSubtitleFiles?.(categorized.subtitleFiles);
        }
        if (categorized.imageFiles.length > 0) {
            options.onImageFiles?.(categorized.imageFiles);
        }
    }, [options, categorizeFiles]);

    const handleDragEnter = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        // Only set to false if we're leaving the drop zone entirely
        if (e.currentTarget.contains(e.relatedTarget as Node)) return;
        setIsDragging(false);
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDropEvent = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files)
            .map(file => (file as any).path || file.name)
            .filter(Boolean);

        if (files.length > 0) {
            handleDrop(files);
        }
    }, [handleDrop]);

    const dropZoneProps = {
        onDragEnter: handleDragEnter,
        onDragLeave: handleDragLeave,
        onDragOver: handleDragOver,
        onDrop: handleDropEvent,
    };

    return {
        isDragging,
        dropZoneProps,
        handleDrop,
        categorizeFiles
    };
}

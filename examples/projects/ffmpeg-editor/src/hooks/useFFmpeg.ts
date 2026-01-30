import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Progress, ConvertOptions, MediaInfo } from '../types';

export function useFFmpeg() {
    const [ffmpegVersion, setFfmpegVersion] = useState<string>('');
    const [ffmpegError, setFfmpegError] = useState<string>('');
    const [isConverting, setIsConverting] = useState(false);
    const [progress, setProgress] = useState<Progress | null>(null);

    useEffect(() => {
        invoke<string>('check_ffmpeg')
            .then(setFfmpegVersion)
            .catch((err) => setFfmpegError(err as string));

        const unlisten = listen<Progress>('ffmpeg-progress', (event) => {
            setProgress(event.payload);
        });

        return () => {
            unlisten.then(fn => fn());
        };
    }, []);

    const getMediaInfo = useCallback(async (path: string) => {
        return await invoke<MediaInfo>('get_media_info', { path });
    }, []);

    const convertMedia = useCallback(async (options: ConvertOptions) => {
        setIsConverting(true);
        setProgress({ percent: 0, time: 0, speed: 'Starting...', size: '0KB' });
        try {
            await invoke('convert_media', { options });
        } finally {
            setIsConverting(false);
            setProgress(null);
        }
    }, []);

    const mergeMedia = useCallback(async (files: string[], output: string) => {
        setIsConverting(true);
        setProgress({ percent: 0, time: 0, speed: 'Merging...', size: '0KB' });
        try {
            await invoke('merge_media', { files, output });
        } finally {
            setIsConverting(false);
            setProgress(null);
        }
    }, []);

    const cancelConversion = useCallback(() => {
        invoke('cancel_conversion');
    }, []);

    return {
        ffmpegVersion,
        ffmpegError,
        isConverting,
        progress,
        getMediaInfo,
        convertMedia,
        mergeMedia,
        cancelConversion
    };
}

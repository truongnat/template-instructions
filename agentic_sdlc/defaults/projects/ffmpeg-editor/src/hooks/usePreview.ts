import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { ConvertOptions } from '../types';
import { useDebounce } from './useDebounce';

export function usePreview(options: ConvertOptions, timestamp: number) {
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Debounce options and timestamp to avoid rapid calls during slider dragging
    const debouncedOptions = useDebounce(options, 500);
    const debouncedTimestamp = useDebounce(timestamp, 500);

    useEffect(() => {
        if (!debouncedOptions.input) {
            setPreviewUrl(null);
            return;
        }

        let isMounted = true;
        setIsLoading(true);
        setError(null);

        invoke<string>('generate_preview', {
            options: debouncedOptions,
            timestamp: debouncedTimestamp
        })
            .then((url) => {
                if (isMounted) {
                    setPreviewUrl(url);
                    setIsLoading(false);
                }
            })
            .catch((err) => {
                if (isMounted) {
                    console.error("Preview generation failed:", err);
                    // Don't clear the old preview on error, just show error state
                    setError(err as string);
                    setIsLoading(false);
                }
            });

        return () => {
            isMounted = false;
        };
    }, [debouncedOptions, debouncedTimestamp]);

    return { previewUrl, isLoading, error };
}

import { useState, useRef, useCallback } from 'react';

export function useMediaControls() {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const videoRef = useRef<HTMLVideoElement>(null);

    const togglePlay = useCallback(() => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause();
            } else {
                videoRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    }, [isPlaying]);

    const handleTimeUpdate = useCallback(() => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    }, []);

    const handleSeek = useCallback((time: number) => {
        if (videoRef.current) {
            videoRef.current.currentTime = time;
            setCurrentTime(time);
        }
    }, []);

    const toggleMute = useCallback(() => {
        if (videoRef.current) {
            const newMuted = !isMuted;
            videoRef.current.muted = newMuted;
            setIsMuted(newMuted);
        }
    }, [isMuted]);

    const handleVolumeChange = useCallback((v: number) => {
        setVolume(v);
        if (videoRef.current) {
            videoRef.current.volume = v;
            if (v > 0) {
                videoRef.current.muted = false;
                setIsMuted(false);
            }
        }
    }, []);

    return {
        videoRef,
        isPlaying,
        setIsPlaying,
        currentTime,
        setCurrentTime,
        volume,
        isMuted,
        togglePlay,
        handleTimeUpdate,
        handleSeek,
        toggleMute,
        handleVolumeChange
    };
}

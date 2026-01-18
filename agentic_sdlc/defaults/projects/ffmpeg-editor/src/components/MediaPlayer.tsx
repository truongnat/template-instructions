import React from 'react';
import { Play, Pause, Volume2, VolumeX } from 'lucide-react';
import { convertFileSrc } from '@tauri-apps/api/core';

interface MediaPlayerProps {
    videoRef: React.RefObject<HTMLVideoElement | null>;
    inputFile: string;
    subtitleFile: string | null;
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    volume: number;
    isMuted: boolean;
    onTimeUpdate: () => void;
    onEnded: () => void;
    onTogglePlay: () => void;
    onSeek: (time: number) => void;
    onToggleMute: () => void;
    onVolumeChange: (volume: number) => void;
    formatTime: (seconds: number) => string;
}

export function MediaPlayer({
    videoRef,
    inputFile,
    subtitleFile,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    onTimeUpdate,
    onEnded,
    onTogglePlay,
    onSeek,
    onToggleMute,
    onVolumeChange,
    formatTime
}: MediaPlayerProps) {
    return (
        <div className="player-container">
            <video
                ref={videoRef}
                src={convertFileSrc(inputFile)}
                onTimeUpdate={onTimeUpdate}
                onEnded={onEnded}
                className="video-player"
            >
                {subtitleFile && (
                    <track
                        kind="subtitles"
                        src={convertFileSrc(subtitleFile)}
                        default
                    />
                )}
            </video>

            <div className="player-controls">
                <button onClick={onTogglePlay} className="control-btn">
                    {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                </button>

                <span className="time-display">
                    {formatTime(currentTime)} / {formatTime(duration)}
                </span>

                <input
                    type="range"
                    min={0}
                    max={duration}
                    step={0.1}
                    value={currentTime}
                    onChange={(e) => onSeek(parseFloat(e.target.value))}
                    className="seek-bar"
                />

                <button onClick={onToggleMute} className="control-btn">
                    {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                </button>

                <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.1}
                    value={isMuted ? 0 : volume}
                    onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
                    className="volume-bar"
                />
            </div>
        </div>
    );
}

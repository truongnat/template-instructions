import { Check, AlertCircle } from 'lucide-react';

interface HeaderProps {
    version: string;
    error: string;
}

export function Header({ version, error }: HeaderProps) {
    return (
        <header className="header">
            <h1 className="logo">🎬 FFmpeg Editor</h1>
            <div className="ffmpeg-status">
                {version ? (
                    <span className="status-ok">
                        <Check size={14} /> {version.split(' ')[2]}
                    </span>
                ) : error ? (
                    <span className="status-error">
                        <AlertCircle size={14} /> {error}
                    </span>
                ) : (
                    <span>Checking FFmpeg...</span>
                )}
            </div>
        </header>
    );
}

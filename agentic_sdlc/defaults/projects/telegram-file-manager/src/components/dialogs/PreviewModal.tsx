/**
 * File Preview Modal Component - Enhanced with CSS Animations & Full File Support
 * @module components/dialogs/PreviewModal
 */

import { useState, useEffect, useCallback } from 'react';
import {
    X,
    Download,
    Star,
    Trash2,
    ChevronLeft,
    ChevronRight,
    ZoomIn,
    ZoomOut,
    RotateCw,
    Loader2,
    Music,
    FileText,
    Eye,
    FileArchive,
    Code,
    FileJson,
} from 'lucide-react';
import type { TelegramFile } from '../../lib/telegram/types';
import { formatFileSize } from '../../lib/telegram/types';
import { fileMetadata } from '../../lib/telegram/metadata';
import { gramjsClient } from '../../lib/telegram/gramjs-client';
import { useResponsive } from '../../hooks/useResponsive';

// ============================================================================
// TYPES
// ============================================================================

interface PreviewModalProps {
    file: TelegramFile | null;
    files: TelegramFile[];
    isOpen: boolean;
    onClose: () => void;
    onDownload: (file: TelegramFile) => void;
    onDelete: (file: TelegramFile) => void;
    onToggleFavorite: (file: TelegramFile) => void;
    onNavigate: (file: TelegramFile) => void;
}

// ============================================================================
// COMPONENT
// ============================================================================

export function PreviewModal({
    file,
    files,
    isOpen,
    onClose,
    onDownload,
    onDelete,
    onToggleFavorite,
    onNavigate,
}: PreviewModalProps) {
    const [zoom, setZoom] = useState(1);
    const [rotation, setRotation] = useState(0);
    const [blobUrl, setBlobUrl] = useState<string | null>(null);
    const [textContent, setTextContent] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isExiting, setIsExiting] = useState(false);
    const { isMobile } = useResponsive();

    // Securely handle modal closing with animation
    const handleClose = useCallback(() => {
        setIsExiting(true);
        setTimeout(() => {
            onClose();
            setIsExiting(false);
        }, 200); // Duration matches CSS exit animation
    }, [onClose]);

    // Reset zoom and rotation when file changes
    useEffect(() => {
        setZoom(1);
        setRotation(0);
        setTextContent(null);
    }, [file]);

    // Load blob URL or text content for preview
    useEffect(() => {
        if (!file || !isOpen) {
            setBlobUrl(null);
            setTextContent(null);
            return;
        }

        let active = true;
        setIsLoading(true);
        setBlobUrl(null);
        setTextContent(null);

        const isTextFile =
            file.mime_type.startsWith('text/') ||
            file.file_name.endsWith('.md') ||
            file.file_name.endsWith('.json') ||
            file.file_name.endsWith('.js') ||
            file.file_name.endsWith('.ts') ||
            file.file_name.endsWith('.css');

        // For demo files (legacy support, but we are moving away)
        if (file.file_id.startsWith('demo-')) {
            fileMetadata.getBlob(file.file_unique_id).then(async (blob) => {
                if (active && blob) {
                    if (isTextFile) {
                        const text = await blob.text();
                        setTextContent(text);
                    } else {
                        const url = URL.createObjectURL(blob);
                        setBlobUrl(url);
                    }
                }
                setIsLoading(false);
            }).catch(() => {
                setIsLoading(false);
            });
        } else {
            // For Telegram files, download on demand
            if (file.message_id) {
                gramjsClient.downloadFile(file.message_id).then(async (blob) => {
                    if (active && blob) {
                        if (isTextFile) {
                            const text = await blob.text();
                            setTextContent(text);
                        } else {
                            const url = URL.createObjectURL(blob);
                            setBlobUrl(url);
                        }
                    }
                    setIsLoading(false);
                }).catch(err => {
                    console.error('Failed to download file', err);
                    setIsLoading(false);
                });
            } else {
                setIsLoading(false);
            }
        }

        return () => {
            active = false;
            // Cleanup blob URL on unmount or file change
            if (blobUrl) {
                URL.revokeObjectURL(blobUrl);
            }
        };
    }, [file?.file_unique_id, isOpen]);

    // Keyboard navigation
    useEffect(() => {
        if (!isOpen || !file || isExiting) return;

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') handleClose();
            if (e.key === 'ArrowLeft') navigatePrev();
            if (e.key === 'ArrowRight') navigateNext();
            if (e.key === '+' || e.key === '=') setZoom(z => Math.min(z + 0.25, 3));
            if (e.key === '-') setZoom(z => Math.max(z - 0.25, 0.5));
            if (e.key === 'r') setRotation(r => (r + 90) % 360);
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, file, handleClose, isExiting]);

    if (!isOpen && !isExiting) return null;
    if (!file) return null;

    const currentIndex = files.findIndex(f => f.file_unique_id === file.file_unique_id);
    const hasPrev = currentIndex > 0;
    const hasNext = currentIndex < files.length - 1;

    const navigatePrev = () => {
        if (hasPrev) onNavigate(files[currentIndex - 1]);
    };

    const navigateNext = () => {
        if (hasNext) onNavigate(files[currentIndex + 1]);
    };

    const isImage = file.mime_type.startsWith('image/');
    const isVideo = file.mime_type.startsWith('video/');
    const isAudio = file.mime_type.startsWith('audio/');
    const isPDF = file.mime_type === 'application/pdf';
    const isArchive = file.mime_type.includes('zip') || file.mime_type.includes('rar') || file.mime_type.includes('7z');
    const isJson = file.mime_type === 'application/json' || file.file_name.endsWith('.json');
    const isCode = file.file_name.endsWith('.js') || file.file_name.endsWith('.ts') || file.file_name.endsWith('.py') || file.file_name.endsWith('.css');
    const isTextContent = textContent !== null;

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center overflow-hidden transition-all duration-300 ${isExiting ? 'animate-fade-out' : 'animate-fade-in'
                }`}
            style={{ background: 'rgba(0, 0, 0, 0.95)' }}
            onClick={handleClose}
        >
            {/* Header */}
            <div
                className="absolute top-0 left-0 right-0 flex items-center justify-between p-4 z-10 safe-top bg-gradient-to-b from-black/80 to-transparent"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center gap-4">
                    <button onClick={handleClose} className="btn-icon">
                        <X size={24} />
                    </button>
                    <div>
                        <h3 className="font-medium text-white truncate max-w-[200px] sm:max-w-md">{file.file_name}</h3>
                        <p className="text-sm text-white/70">
                            {formatFileSize(file.file_size)} • {currentIndex + 1} of {files.length}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {!isMobile && (isImage || isPDF) && (
                        <>
                            <button onClick={() => setZoom(z => Math.max(z - 0.25, 0.5))} className="btn-icon">
                                <ZoomOut size={20} />
                            </button>
                            <span className="text-sm px-2 text-white tabular-nums">{Math.round(zoom * 100)}%</span>
                            <button onClick={() => setZoom(z => Math.min(z + 0.25, 3))} className="btn-icon">
                                <ZoomIn size={20} />
                            </button>
                            {isImage && (
                                <button onClick={() => setRotation(r => (r + 90) % 360)} className="btn-icon">
                                    <RotateCw size={20} />
                                </button>
                            )}
                            <div className="w-px h-6 mx-2 bg-white/20" />
                        </>
                    )}

                    <button
                        onClick={() => onToggleFavorite(file)}
                        className={`btn-icon transition-colors ${file.is_favorite ? 'text-yellow-500' : ''}`}
                    >
                        <Star size={20} fill={file.is_favorite ? 'currentColor' : 'none'} />
                    </button>
                    <button onClick={() => onDownload(file)} className="btn-icon">
                        <Download size={20} />
                    </button>
                    {!isMobile && (
                        <button
                            onClick={() => { onDelete(file); handleClose(); }}
                            className="btn-icon text-red-400"
                        >
                            <Trash2 size={20} />
                        </button>
                    )}
                </div>
            </div>

            {/* Navigation Arrows */}
            {hasPrev && !isMobile && (
                <button
                    onClick={(e) => { e.stopPropagation(); navigatePrev(); }}
                    className="absolute left-4 p-3 rounded-full transition-all z-10 bg-white/10 hover:bg-white/20 backdrop-blur-md"
                >
                    <ChevronLeft size={24} />
                </button>
            )}
            {hasNext && !isMobile && (
                <button
                    onClick={(e) => { e.stopPropagation(); navigateNext(); }}
                    className="absolute right-4 p-3 rounded-full transition-all z-10 bg-white/10 hover:bg-white/20 backdrop-blur-md"
                >
                    <ChevronRight size={24} />
                </button>
            )}

            {/* Mobile Navigation Hit Zones */}
            {isMobile && (
                <>
                    {hasPrev && (
                        <div
                            className="absolute left-0 top-1/4 bottom-1/4 w-16 z-10"
                            onClick={(e) => { e.stopPropagation(); navigatePrev(); }}
                        />
                    )}
                    {hasNext && (
                        <div
                            className="absolute right-0 top-1/4 bottom-1/4 w-16 z-10"
                            onClick={(e) => { e.stopPropagation(); navigateNext(); }}
                        />
                    )}
                </>
            )}

            {/* Content Container */}
            <div
                className={`flex items-center justify-center p-4 ${isMobile ? 'w-full h-full' : 'max-w-[90vw] max-h-[85vh]'} ${isExiting ? 'animate-scale-out' : 'animate-scale-in'
                    }`}
                onClick={e => e.stopPropagation()}
            >
                {/* Loading State */}
                {isLoading && (
                    <div className="flex flex-col items-center gap-4">
                        <Loader2 size={48} className="animate-spin text-accent-purple" />
                        <p className="text-white/40 animate-pulse">Downloading for preview...</p>
                    </div>
                )}

                {/* Image Preview */}
                {isImage && !isLoading && (
                    <div
                        className="w-full h-full flex items-center justify-center overflow-hidden transition-transform duration-200"
                        style={{
                            transform: `scale(${zoom}) rotate(${rotation}deg)`,
                            touchAction: 'none'
                        }}
                    >
                        {blobUrl ? (
                            <img
                                src={blobUrl}
                                alt={file.file_name}
                                className="max-w-full max-h-full object-contain rounded-lg shadow-2xl gpu-accelerated"
                                draggable={false}
                            />
                        ) : (
                            <PreviewFallback file={file} />
                        )}
                    </div>
                )}

                {/* Video Preview */}
                {isVideo && !isLoading && (
                    <div className="w-full h-full flex items-center justify-center">
                        {blobUrl ? (
                            <video
                                src={blobUrl}
                                controls
                                playsInline
                                className="max-w-full max-h-full rounded-lg bg-black shadow-2xl"
                            />
                        ) : (
                            <PreviewFallback file={file} />
                        )}
                    </div>
                )}

                {/* Audio Preview */}
                {isAudio && !isLoading && (
                    <div className="w-full max-w-lg bg-dark-700/80 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-2xl">
                        <div className="flex justify-center mb-8">
                            <div className="w-32 h-32 rounded-3xl bg-gradient-to-br from-accent-purple/20 to-accent-blue/20 flex items-center justify-center animate-pulse-glow">
                                <Music size={56} className="text-accent-purple" />
                            </div>
                        </div>
                        <p className="mb-2 text-center text-white font-semibold text-lg truncate">{file.file_name}</p>
                        <p className="mb-8 text-center text-white/40 text-sm">{formatFileSize(file.file_size)}</p>
                        {blobUrl ? (
                            <audio src={blobUrl} controls className="w-full" autoPlay />
                        ) : (
                            <PreviewFallback file={file} />
                        )}
                    </div>
                )}

                {/* Text / Code Preview */}
                {isTextContent && !isLoading && (
                    <div className="w-full max-w-4xl max-h-[70vh] bg-dark-800 border border-white/10 rounded-2xl overflow-hidden flex flex-col shadow-2xl">
                        <div className="bg-dark-700/50 p-3 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                {isJson ? <FileJson size={16} className="text-yellow-400" /> : isCode ? <Code size={16} className="text-blue-400" /> : <FileText size={16} className="text-gray-400" />}
                                <span className="text-xs font-mono text-white/50">{file.file_name}</span>
                            </div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-white/20 px-2 py-0.5 rounded-md bg-white/5">
                                {file.mime_type.split('/')[1] || 'text'}
                            </span>
                        </div>
                        <pre className="p-6 overflow-auto text-sm text-white/80 font-mono leading-relaxed scroll-container selection:bg-accent-purple/30">
                            {textContent}
                        </pre>
                    </div>
                )}

                {/* PDF Preview */}
                {isPDF && !isLoading && (
                    <div className="w-full h-full flex items-center justify-center overflow-auto">
                        {blobUrl ? (
                            <iframe
                                src={`${blobUrl}#toolbar=0&view=FitH`}
                                className="w-full h-full rounded-lg bg-white shadow-2xl"
                                title={file.file_name}
                            />
                        ) : (
                            <PreviewFallback file={file} />
                        )}
                    </div>
                )}

                {/* Archive / Generic Fallback */}
                {!isImage && !isVideo && !isAudio && !isTextContent && !isPDF && !isLoading && (
                    <div className="w-full max-w-md bg-dark-700/80 backdrop-blur-xl p-10 rounded-3xl border border-white/10 text-center shadow-2xl">
                        <div className="flex justify-center mb-8">
                            <div className="w-24 h-24 rounded-3xl bg-white/5 flex items-center justify-center">
                                {isArchive ? <FileArchive size={40} className="text-accent-blue" /> : <FileText size={40} className="text-white/30" />}
                            </div>
                        </div>
                        <h4 className="text-white font-bold text-xl mb-2 truncate">{file.file_name}</h4>
                        <p className="text-white/40 mb-10">
                            Preview not available for this {isArchive ? 'archive' : 'file type'} ({formatFileSize(file.file_size)})
                        </p>
                        <div className="flex flex-col gap-3">
                            <button
                                onClick={() => onDownload(file)}
                                className="btn-gradient w-full flex items-center justify-center gap-2 py-3.5"
                            >
                                <Download size={20} />
                                Download & Open
                            </button>
                            <button
                                onClick={handleClose}
                                className="btn-ghost w-full py-3"
                            >
                                Go Back
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function PreviewFallback({ file }: { file: TelegramFile }) {
    return (
        <div className="flex flex-col items-center justify-center rounded-3xl bg-dark-700/50 p-12 text-center border border-white/5">
            <Eye size={56} className="mb-6 text-white/10" />
            <h4 className="text-white/60 font-medium mb-1">{file.file_name}</h4>
            <p className="text-sm text-white/30 max-w-[200px]">
                Preview failed to load. Try downloading the file directly.
            </p>
        </div>
    );
}

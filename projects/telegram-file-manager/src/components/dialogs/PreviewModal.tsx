/**
 * File Preview Modal Component
 * @module components/dialogs/PreviewModal
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
    Maximize2,
    Loader2,
} from 'lucide-react';
import type { TelegramFile } from '../../lib/telegram/types';
import { formatFileSize } from '../../lib/telegram/types';
import { fileMetadata } from '../../lib/telegram/metadata';

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
    const [isLoading, setIsLoading] = useState(false);

    // Reset zoom and rotation when file changes
    useEffect(() => {
        setZoom(1);
        setRotation(0);
    }, [file]);

    // Load blob URL for preview
    useEffect(() => {
        if (!file) {
            setBlobUrl(null);
            return;
        }

        let active = true;
        setIsLoading(true);
        setBlobUrl(null);

        // For demo files, try to get the stored blob
        if (file.file_id.startsWith('demo-')) {
            fileMetadata.getBlob(file.file_unique_id).then(blob => {
                if (active && blob) {
                    const url = URL.createObjectURL(blob);
                    setBlobUrl(url);
                }
                setIsLoading(false);
            }).catch(() => {
                setIsLoading(false);
            });
        } else {
            // For Telegram files, we would need to download first
            setIsLoading(false);
        }

        return () => {
            active = false;
            // Cleanup blob URL on unmount or file change
            if (blobUrl) {
                URL.revokeObjectURL(blobUrl);
            }
        };
    }, [file?.file_unique_id]);

    // Keyboard navigation
    useEffect(() => {
        if (!isOpen || !file) return;

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowLeft') navigatePrev();
            if (e.key === 'ArrowRight') navigateNext();
            if (e.key === '+' || e.key === '=') setZoom(z => Math.min(z + 0.25, 3));
            if (e.key === '-') setZoom(z => Math.max(z - 0.25, 0.5));
            if (e.key === 'r') setRotation(r => (r + 90) % 360);
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, file, onClose]);

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

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center"
                    style={{ background: 'rgba(0, 0, 0, 0.9)' }}
                    onClick={onClose}
                >
                    {/* Header */}
                    <div
                        className="absolute top-0 left-0 right-0 flex items-center justify-between p-4"
                        style={{ background: 'linear-gradient(to bottom, rgba(0,0,0,0.8), transparent)' }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center gap-4">
                            <button onClick={onClose} className="btn-icon">
                                <X size={24} />
                            </button>
                            <div>
                                <h3 className="font-medium">{file.file_name}</h3>
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                    {formatFileSize(file.file_size)} • {currentIndex + 1} of {files.length}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            {isImage && (
                                <>
                                    <button onClick={() => setZoom(z => Math.max(z - 0.25, 0.5))} className="btn-icon">
                                        <ZoomOut size={20} />
                                    </button>
                                    <span className="text-sm px-2">{Math.round(zoom * 100)}%</span>
                                    <button onClick={() => setZoom(z => Math.min(z + 0.25, 3))} className="btn-icon">
                                        <ZoomIn size={20} />
                                    </button>
                                    <button onClick={() => setRotation(r => (r + 90) % 360)} className="btn-icon">
                                        <RotateCw size={20} />
                                    </button>
                                    <div className="w-px h-6 mx-2" style={{ background: 'rgba(255,255,255,0.2)' }} />
                                </>
                            )}
                            <button
                                onClick={() => onToggleFavorite(file)}
                                className="btn-icon"
                                style={{ color: file.is_favorite ? '#eab308' : undefined }}
                            >
                                <Star size={20} style={{ fill: file.is_favorite ? '#eab308' : 'none' }} />
                            </button>
                            <button onClick={() => onDownload(file)} className="btn-icon">
                                <Download size={20} />
                            </button>
                            <button
                                onClick={() => { onDelete(file); onClose(); }}
                                className="btn-icon"
                                style={{ color: '#f87171' }}
                            >
                                <Trash2 size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Navigation Arrows */}
                    {hasPrev && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigatePrev(); }}
                            className="absolute left-4 p-3 rounded-full transition-all"
                            style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(4px)' }}
                        >
                            <ChevronLeft size={24} />
                        </button>
                    )}
                    {hasNext && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigateNext(); }}
                            className="absolute right-4 p-3 rounded-full transition-all"
                            style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(4px)' }}
                        >
                            <ChevronRight size={24} />
                        </button>
                    )}

                    {/* Content */}
                    <div
                        className="max-w-4xl max-h-[80vh] flex items-center justify-center"
                        onClick={e => e.stopPropagation()}
                    >
                        {/* Loading State */}
                        {isLoading && (
                            <div className="flex items-center justify-center" style={{ width: 400, height: 300 }}>
                                <Loader2 size={48} className="animate-spin" style={{ color: 'rgba(255,255,255,0.5)' }} />
                            </div>
                        )}

                        {/* Image Preview */}
                        {isImage && !isLoading && (
                            <motion.div
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                style={{
                                    transform: `scale(${zoom}) rotate(${rotation}deg)`,
                                    transition: 'transform 0.2s ease-out',
                                }}
                            >
                                {blobUrl ? (
                                    <img
                                        src={blobUrl}
                                        alt={file.file_name}
                                        className="max-w-full max-h-[70vh] rounded-lg shadow-2xl"
                                        style={{ objectFit: 'contain' }}
                                    />
                                ) : (
                                    <div
                                        className="flex items-center justify-center rounded-lg"
                                        style={{
                                            width: 400,
                                            height: 300,
                                            background: 'rgba(37, 37, 37, 1)',
                                        }}
                                    >
                                        <div className="text-center">
                                            <Maximize2 size={48} style={{ color: 'rgba(255,255,255,0.3)', marginBottom: 8 }} />
                                            <p style={{ color: 'rgba(255,255,255,0.5)' }}>{file.file_name}</p>
                                            <p className="text-sm" style={{ color: 'rgba(255,255,255,0.3)' }}>
                                                {file.file_id.startsWith('demo-')
                                                    ? 'Blob not found - try re-uploading'
                                                    : 'Connect Telegram to preview'}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {/* Video Preview */}
                        {isVideo && !isLoading && (
                            <div className="rounded-lg overflow-hidden" style={{ maxWidth: 800 }}>
                                {blobUrl ? (
                                    <video
                                        src={blobUrl}
                                        controls
                                        autoPlay={false}
                                        className="max-w-full max-h-[70vh]"
                                        style={{ background: 'rgba(37, 37, 37, 1)' }}
                                    />
                                ) : (
                                    <div
                                        className="flex items-center justify-center rounded-lg"
                                        style={{
                                            width: 640,
                                            height: 360,
                                            background: 'rgba(37, 37, 37, 1)',
                                        }}
                                    >
                                        <div className="text-center">
                                            <p style={{ color: 'rgba(255,255,255,0.5)' }}>{file.file_name}</p>
                                            <p className="text-sm" style={{ color: 'rgba(255,255,255,0.3)' }}>
                                                {file.file_id.startsWith('demo-')
                                                    ? 'Video not found - try re-uploading'
                                                    : 'Connect Telegram to preview'}
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Audio Preview */}
                        {isAudio && !isLoading && (
                            <div
                                className="flex flex-col items-center justify-center rounded-lg p-8"
                                style={{
                                    width: 400,
                                    background: 'rgba(37, 37, 37, 1)',
                                }}
                            >
                                <p className="mb-4" style={{ color: 'rgba(255,255,255,0.7)' }}>{file.file_name}</p>
                                {blobUrl ? (
                                    <audio
                                        src={blobUrl}
                                        controls
                                        className="w-full"
                                    />
                                ) : (
                                    <p className="text-sm" style={{ color: 'rgba(255,255,255,0.3)' }}>
                                        {file.file_id.startsWith('demo-')
                                            ? 'Audio not found - try re-uploading'
                                            : 'Connect Telegram to preview'}
                                    </p>
                                )}
                            </div>
                        )}

                        {!isImage && !isVideo && !isAudio && (
                            <div
                                className="flex items-center justify-center rounded-lg p-8"
                                style={{
                                    width: 400,
                                    background: 'rgba(37, 37, 37, 1)',
                                }}
                            >
                                <div className="text-center">
                                    <p style={{ color: 'rgba(255,255,255,0.5)' }}>{file.file_name}</p>
                                    <p className="text-sm" style={{ color: 'rgba(255,255,255,0.3)' }}>
                                        Click download to view this file
                                    </p>
                                    <button
                                        onClick={() => onDownload(file)}
                                        className="btn-gradient mt-4 inline-flex items-center gap-2"
                                    >
                                        <Download size={18} />
                                        Download
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

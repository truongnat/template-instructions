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
    Music,
    FileText,
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
    const [isLoading, setIsLoading] = useState(false);
    const { isMobile } = useResponsive();

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
            // For Telegram files, download on demand
            if (file.message_id) {
                gramjsClient.downloadFile(file.message_id).then(blob => {
                    if (active && blob) {
                        const url = URL.createObjectURL(blob);
                        setBlobUrl(url);
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
                    className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden"
                    style={{ background: 'rgba(0, 0, 0, 0.95)' }}
                    onClick={onClose}
                >
                    {/* Header */}
                    <div
                        className="absolute top-0 left-0 right-0 flex items-center justify-between p-4 z-10 safe-top"
                        style={{ background: 'linear-gradient(to bottom, rgba(0,0,0,0.8), transparent)' }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="flex items-center gap-4">
                            <button onClick={onClose} className="btn-icon">
                                <X size={24} />
                            </button>
                            <div>
                                <h3 className="font-medium text-white truncate max-w-[200px]">{file.file_name}</h3>
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.7)' }}>
                                    {formatFileSize(file.file_size)} • {currentIndex + 1} of {files.length}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            {/* Desktop Zoom Controls - Hide on Mobile */}
                            {!isMobile && isImage && (
                                <>
                                    <button onClick={() => setZoom(z => Math.max(z - 0.25, 0.5))} className="btn-icon">
                                        <ZoomOut size={20} />
                                    </button>
                                    <span className="text-sm px-2 text-white">{Math.round(zoom * 100)}%</span>
                                    <button onClick={() => setZoom(z => Math.min(z + 0.25, 3))} className="btn-icon">
                                        <ZoomIn size={20} />
                                    </button>
                                    <button onClick={() => setRotation(r => (r + 90) % 360)} className="btn-icon">
                                        <RotateCw size={20} />
                                    </button>
                                    <div className="w-px h-6 mx-2" style={{ background: 'rgba(255,255,255,0.2)' }} />
                                </>
                            )}

                            {/* Actions - Always show standard actions */}
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
                            {!isMobile && (
                                <button
                                    onClick={() => { onDelete(file); onClose(); }}
                                    className="btn-icon text-red-400"
                                >
                                    <Trash2 size={20} />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Navigation Arrows - Hide on mobile if swipe is implemented (TODO: Swipe) or keep simple taps */}
                    {hasPrev && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigatePrev(); }}
                            className={`absolute left-4 p-3 rounded-full transition-all z-10 ${isMobile ? 'hidden' : ''}`}
                            style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(4px)' }}
                        >
                            <ChevronLeft size={24} />
                        </button>
                    )}
                    {hasNext && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigateNext(); }}
                            className={`absolute right-4 p-3 rounded-full transition-all z-10 ${isMobile ? 'hidden' : ''}`}
                            style={{ background: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(4px)' }}
                        >
                            <ChevronRight size={24} />
                        </button>
                    )}

                    {/* Mobile Navigation Hit Zones (Transparent overlays) */}
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

                    {/* Content */}
                    <div
                        className={`flex items-center justify-center p-4 ${isMobile ? 'w-full h-full' : 'max-w-4xl max-h-[80vh]'}`}
                        onClick={e => e.stopPropagation()}
                    >
                        {/* Loading State */}
                        {isLoading && (
                            <div className="flex items-center justify-center">
                                <Loader2 size={48} className="animate-spin text-white/50" />
                            </div>
                        )}

                        {/* Image Preview */}
                        {isImage && !isLoading && (
                            <motion.div
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                drag={isMobile}
                                dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
                                dragElastic={0.2}
                                style={{
                                    transform: `scale(${zoom}) rotate(${rotation}deg)`,
                                    transition: isMobile ? undefined : 'transform 0.2s ease-out',
                                    touchAction: 'none'
                                }}
                                className="w-full h-full flex items-center justify-center"
                            >
                                {blobUrl ? (
                                    <img
                                        src={blobUrl}
                                        alt={file.file_name}
                                        className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
                                    />
                                ) : (
                                    <div
                                        className="flex flex-col items-center justify-center rounded-lg bg-dark-800 p-8 text-center"
                                        style={{ maxWidth: '100%' }}
                                    >
                                        <Maximize2 size={48} className="mb-4 text-white/30" />
                                        <p className="text-white/50">{file.file_name}</p>
                                        <p className="text-sm text-white/30 mt-2">
                                            {file.file_id.startsWith('demo-')
                                                ? 'Blob not found - try re-uploading'
                                                : 'Connect Telegram to preview'}
                                        </p>
                                    </div>
                                )}
                            </motion.div>
                        )}

                        {/* Video Preview */}
                        {isVideo && !isLoading && (
                            <div className="w-full max-w-4xl flex items-center justify-center">
                                {blobUrl ? (
                                    <video
                                        src={blobUrl}
                                        controls
                                        autoPlay={false}
                                        className="max-w-full max-h-[80vh] w-auto h-auto rounded-lg bg-black"
                                    />
                                ) : (
                                    <div className="flex flex-col items-center justify-center rounded-lg bg-dark-800 p-12 text-center">
                                        <p className="text-white/50 mb-2">{file.file_name}</p>
                                        <p className="text-sm text-white/30">
                                            {file.file_id.startsWith('demo-')
                                                ? 'Video not found - try re-uploading'
                                                : 'Connect Telegram to preview'}
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Audio Preview */}
                        {isAudio && !isLoading && (
                            <div className="w-full max-w-md bg-dark-800/80 backdrop-blur-md p-8 rounded-2xl border border-white/10">
                                <div className="flex justify-center mb-6">
                                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                                        <Music size={40} className="text-purple-400" />
                                    </div>
                                </div>
                                <p className="mb-6 text-center text-white/80 font-medium truncate">{file.file_name}</p>
                                {blobUrl ? (
                                    <audio src={blobUrl} controls className="w-full" />
                                ) : (
                                    <p className="text-sm text-center text-white/30">
                                        {file.file_id.startsWith('demo-')
                                            ? 'Audio not found - try re-uploading'
                                            : 'Connect Telegram to preview'}
                                    </p>
                                )}
                            </div>
                        )}

                        {!isImage && !isVideo && !isAudio && (
                            <div className="w-full max-w-md bg-dark-800/80 backdrop-blur-md p-8 rounded-2xl border border-white/10 text-center">
                                <div className="flex justify-center mb-6">
                                    <div className="w-20 h-20 rounded-2xl bg-white/5 flex items-center justify-center">
                                        <FileText size={32} className="text-white/40" />
                                    </div>
                                </div>
                                <p className="text-white/60 mb-2 font-medium truncate">{file.file_name}</p>
                                <p className="text-sm text-white/30 mb-6">
                                    Preview not available for this file type
                                </p>
                                <button
                                    onClick={() => onDownload(file)}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 py-3"
                                >
                                    <Download size={18} />
                                    Download File
                                </button>
                            </div>
                        )}
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

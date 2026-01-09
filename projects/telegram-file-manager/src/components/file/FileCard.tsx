/**
 * File Card Component - Responsive with touch gestures
 * @module components/file/FileCard
 */

import { useState, useEffect, memo, useRef } from 'react';
import { motion, useMotionValue, useTransform, AnimatePresence } from 'framer-motion';
import {
    File,
    Image,
    Video,
    Music,
    FileText,
    Archive,
    Download,
    Trash2,
    Star,
    MoreVertical,
    Eye,
    Check,
} from 'lucide-react';
import type { TelegramFile } from '../../lib/telegram/types';
import { formatFileSize } from '../../lib/telegram/types';
import { useResponsive } from '../../hooks/useResponsive';
import { fileMetadata } from '../../lib/telegram/metadata';
import { gramjsClient } from '../../lib/telegram/gramjs-client';

// ============================================================================
// TYPES
// ============================================================================

interface FileCardProps {
    file: TelegramFile;
    isSelected: boolean;
    onSelect: (multiSelect: boolean) => void;
    onPreview: () => void;
    onDownload: () => void;
    onDelete: () => void;
    onToggleFavorite: () => void;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getFileIcon(mimeType: string) {
    if (mimeType.startsWith('image/')) return <Image size={24} style={{ color: '#ec4899' }} />;
    if (mimeType.startsWith('video/')) return <Video size={24} style={{ color: '#3b82f6' }} />;
    if (mimeType.startsWith('audio/')) return <Music size={24} style={{ color: '#22c55e' }} />;
    if (mimeType.includes('pdf')) return <FileText size={24} style={{ color: '#ef4444' }} />;
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) {
        return <Archive size={24} style={{ color: '#eab308' }} />;
    }
    if (mimeType.includes('document') || mimeType.includes('text')) {
        return <FileText size={24} style={{ color: '#3b82f6' }} />;
    }
    return <File size={24} style={{ color: 'rgba(255,255,255,0.6)' }} />;
}

function formatDate(date: Date): string {
    const now = new Date();
    const d = new Date(date);
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;

    return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: days > 365 ? 'numeric' : undefined,
    });
}

function getFileExtension(fileName: string): string {
    const parts = fileName.split('.');
    return parts.length > 1 ? parts.pop()?.toUpperCase() || '' : '';
}

// ============================================================================
// COMPONENT
// ============================================================================

export const FileCard = memo(function FileCard({
    file,
    isSelected,
    onSelect,
    onPreview,
    onDownload,
    onDelete,
    onToggleFavorite,
}: FileCardProps) {
    const [showActions, setShowActions] = useState(false);
    const [isHovered, setIsHovered] = useState(false);
    const { isMobile } = useResponsive();
    const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);

    // Swipe state for mobile
    const x = useMotionValue(0);
    const swipeProgress = useTransform(x, [-120, 0], [1, 0]);
    const actionOpacity = useTransform(swipeProgress, [0, 0.5, 1], [0, 0.5, 1]);
    const constraintsRef = useRef(null);

    // Long press for mobile selection
    const longPressTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
    const [isLongPressed, setIsLongPressed] = useState(false);

    const isImage = file.mime_type.startsWith('image/');
    const isVideo = file.mime_type.startsWith('video/');

    // Load thumbnail for images
    useEffect(() => {
        let objectUrl: string | null = null;
        let isMounted = true;

        async function loadThumbnail() {
            if (!isImage) return;

            try {
                let blob: Blob | undefined | null;

                if (file.file_id.startsWith('demo-')) {
                    blob = await fileMetadata.getBlob(file.file_unique_id);
                } else {
                    // Only try downloading if we have a message ID (real file)
                    if (file.message_id) {
                        blob = await gramjsClient.downloadThumbnail(file.message_id);
                    }
                }

                if (isMounted && blob) {
                    objectUrl = URL.createObjectURL(blob);
                    setThumbnailUrl(objectUrl);
                }
            } catch (error) {
                console.error('Failed to load thumbnail:', error);
            }
        }

        loadThumbnail();

        // Cleanup object URL on unmount
        return () => {
            isMounted = false;
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [file.file_unique_id, isImage, file.message_id, file.file_id]);

    const handleClick = (e: React.MouseEvent) => {
        if (isMobile) {
            // On mobile, single tap opens action sheet
            window.dispatchEvent(new CustomEvent('open-action-sheet', { detail: file }));
        } else {
            if (e.ctrlKey || e.metaKey) {
                onSelect(true);
            } else if (e.detail === 2) {
                onPreview();
            } else {
                onSelect(false);
            }
        }
    };

    const handleTouchStart = () => {
        if (!isMobile) return;
        longPressTimer.current = setTimeout(() => {
            setIsLongPressed(true);
            onSelect(true);
            // Haptic feedback if available
            if ('vibrate' in navigator) {
                navigator.vibrate(50);
            }
        }, 500);
    };

    const handleTouchEnd = () => {
        if (longPressTimer.current) {
            clearTimeout(longPressTimer.current);
            longPressTimer.current = null;
        }
        setIsLongPressed(false);
    };

    const handleDragEnd = () => {
        if (x.get() < -80) {
            // Swiped far enough - trigger delete
            onDelete();
        }
        x.set(0);
    };

    // Mobile Swipeable Card
    if (isMobile) {
        return (
            <div ref={constraintsRef} className="relative overflow-hidden rounded-xl">
                {/* Swipe reveal actions */}
                <motion.div
                    style={{ opacity: actionOpacity }}
                    className="absolute inset-y-0 right-0 flex items-center"
                >
                    <button
                        onClick={onToggleFavorite}
                        className="h-full w-16 flex items-center justify-center"
                        style={{ background: '#eab308' }}
                    >
                        <Star size={22} className="text-white" />
                    </button>
                    <button
                        onClick={onDelete}
                        className="h-full w-16 flex items-center justify-center"
                        style={{ background: '#ef4444' }}
                    >
                        <Trash2 size={22} className="text-white" />
                    </button>
                </motion.div>

                {/* Main Card Content */}
                <motion.div
                    drag="x"
                    dragConstraints={{ left: -120, right: 0 }}
                    dragElastic={0.1}
                    onDragEnd={handleDragEnd}
                    onTouchStart={handleTouchStart}
                    onTouchEnd={handleTouchEnd}
                    onClick={handleClick}
                    className={`file-card relative cursor-pointer ${isSelected ? 'selected' : ''} ${isLongPressed ? 'scale-95' : ''}`}
                    style={{
                        x,
                        transition: isLongPressed ? 'transform 0.1s' : undefined,
                    }}
                >
                    {/* Selection Checkbox */}
                    <AnimatePresence>
                        {isSelected && (
                            <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                exit={{ scale: 0 }}
                                className="absolute top-2 left-2 z-10 w-6 h-6 rounded-full flex items-center justify-center"
                                style={{ background: '#7c3aed' }}
                            >
                                <Check size={14} className="text-white" />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Favorite Star */}
                    {file.is_favorite && (
                        <div className="absolute top-2 right-2 z-10">
                            <Star size={14} style={{ color: '#eab308', fill: '#eab308' }} />
                        </div>
                    )}

                    {/* Thumbnail / Icon */}
                    <div
                        className="aspect-square rounded-lg overflow-hidden flex items-center justify-center mb-2 relative"
                        style={{ background: 'rgba(37, 37, 37, 1)' }}
                    >
                        {isImage && thumbnailUrl ? (
                            <img
                                src={thumbnailUrl}
                                alt={file.file_name}
                                className="w-full h-full object-cover"
                                loading="lazy"
                            />
                        ) : (isImage || isVideo) ? (
                            <>
                                <div className="flex flex-col items-center gap-1">
                                    {getFileIcon(file.mime_type)}
                                    <span className="text-[10px] uppercase" style={{ color: 'rgba(255,255,255,0.4)' }}>
                                        {getFileExtension(file.file_name)}
                                    </span>
                                </div>
                                {isVideo && (
                                    <div
                                        className="absolute inset-0 flex items-center justify-center"
                                        style={{ background: 'rgba(0,0,0,0.3)' }}
                                    >
                                        <div
                                            className="w-10 h-10 rounded-full flex items-center justify-center"
                                            style={{ background: 'rgba(255,255,255,0.2)' }}
                                        >
                                            <Video size={20} className="text-white" />
                                        </div>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className="flex flex-col items-center gap-1">
                                {getFileIcon(file.mime_type)}
                                <span className="text-[10px] uppercase" style={{ color: 'rgba(255,255,255,0.4)' }}>
                                    {getFileExtension(file.file_name)}
                                </span>
                            </div>
                        )}
                    </div>

                    {/* File Info */}
                    <div className="space-y-0.5">
                        <h3 className="text-xs font-medium truncate" title={file.file_name}>
                            {file.file_name}
                        </h3>
                        <div className="text-[10px]" style={{ color: 'rgba(255,255,255,0.5)' }}>
                            {formatFileSize(file.file_size)}
                        </div>
                    </div>

                    {/* More button */}
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            window.dispatchEvent(new CustomEvent('open-action-sheet', { detail: file }));
                        }}
                        className="absolute bottom-2 right-1 p-1.5 touch-target"
                    >
                        <MoreVertical size={14} style={{ color: 'rgba(255,255,255,0.4)' }} />
                    </button>
                </motion.div>
            </div>
        );
    }

    // Desktop Card (original)
    return (
        <motion.div
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            whileHover={{ scale: 1.02 }}
            onHoverStart={() => setIsHovered(true)}
            onHoverEnd={() => { setIsHovered(false); setShowActions(false); }}
            onClick={handleClick}
            className={`file-card relative group cursor-pointer ${isSelected ? 'selected' : ''}`}
        >
            {/* Selection Checkbox */}
            <div
                className="absolute top-3 left-3 z-10 w-5 h-5 rounded-md flex items-center justify-center transition-all duration-200"
                style={{
                    background: isSelected ? '#7c3aed' : 'rgba(26, 26, 26, 0.5)',
                    border: isSelected ? '2px solid #7c3aed' : '2px solid rgba(255,255,255,0.3)',
                    opacity: isSelected ? 1 : (isHovered ? 1 : 0),
                }}
                onClick={(e) => {
                    e.stopPropagation();
                    onSelect(true);
                }}
            >
                {isSelected && <Check size={12} className="text-white" />}
            </div>

            {/* Favorite Star */}
            {file.is_favorite && (
                <div className="absolute top-3 right-3 z-10">
                    <Star size={16} style={{ color: '#eab308', fill: '#eab308' }} />
                </div>
            )}

            {/* Thumbnail / Icon */}
            <div
                className="aspect-square rounded-xl overflow-hidden flex items-center justify-center mb-3 relative"
                style={{ background: 'rgba(37, 37, 37, 1)' }}
            >
                {isImage && thumbnailUrl ? (
                    <img
                        src={thumbnailUrl}
                        alt={file.file_name}
                        className="w-full h-full object-cover"
                        loading="lazy"
                    />
                ) : (isImage || isVideo) ? (
                    <>
                        <div className="flex flex-col items-center gap-2">
                            {getFileIcon(file.mime_type)}
                            <span className="text-xs uppercase" style={{ color: 'rgba(255,255,255,0.4)' }}>
                                {getFileExtension(file.file_name)}
                            </span>
                        </div>
                        {isVideo && (
                            <div
                                className="absolute inset-0 flex items-center justify-center"
                                style={{ background: 'rgba(0,0,0,0.3)' }}
                            >
                                <div
                                    className="w-12 h-12 rounded-full flex items-center justify-center"
                                    style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(4px)' }}
                                >
                                    <Video size={24} className="text-white" />
                                </div>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        {getFileIcon(file.mime_type)}
                        <span className="text-xs uppercase" style={{ color: 'rgba(255,255,255,0.4)' }}>
                            {getFileExtension(file.file_name)}
                        </span>
                    </div>
                )}


                {/* Hover Actions Overlay */}
                <motion.div
                    initial={false}
                    animate={{ opacity: isHovered ? 1 : 0 }}
                    className="absolute inset-0 flex items-center justify-center gap-2"
                    style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
                >
                    <button
                        onClick={(e) => { e.stopPropagation(); onPreview(); }}
                        className="p-2 rounded-lg transition-colors"
                        style={{ background: 'rgba(255,255,255,0.1)' }}
                        title="Preview"
                    >
                        <Eye size={18} />
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); onDownload(); }}
                        className="p-2 rounded-lg transition-colors"
                        style={{ background: 'rgba(255,255,255,0.1)' }}
                        title="Download"
                    >
                        <Download size={18} />
                    </button>
                    <button
                        onClick={(e) => { e.stopPropagation(); onToggleFavorite(); }}
                        className="p-2 rounded-lg transition-colors"
                        style={{
                            background: file.is_favorite ? 'rgba(234, 179, 8, 0.2)' : 'rgba(255,255,255,0.1)',
                            color: file.is_favorite ? '#eab308' : 'white',
                        }}
                        title="Favorite"
                    >
                        <Star size={18} style={{ fill: file.is_favorite ? '#eab308' : 'none' }} />
                    </button>
                </motion.div>
            </div>

            {/* File Info */}
            <div className="space-y-1">
                <h3 className="text-sm font-medium truncate" title={file.file_name}>
                    {file.file_name}
                </h3>
                <div className="flex items-center justify-between text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
                    <span>{formatFileSize(file.file_size)}</span>
                    <span>{formatDate(file.created_at)}</span>
                </div>
            </div>

            {/* Context Menu Button */}
            <button
                onClick={(e) => {
                    e.stopPropagation();
                    setShowActions(!showActions);
                }}
                className="absolute bottom-3 right-3 p-1 rounded-lg transition-all"
                style={{
                    opacity: isHovered ? 1 : 0,
                    background: isHovered ? 'rgba(255,255,255,0.1)' : 'transparent',
                }}
            >
                <MoreVertical size={16} style={{ color: 'rgba(255,255,255,0.5)' }} />
            </button>

            {/* Quick Actions Dropdown */}
            {
                showActions && (
                    <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="dropdown-menu absolute bottom-12 right-0 z-20"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <button onClick={onPreview} className="dropdown-item">
                            <Eye size={16} /> Preview
                        </button>
                        <button onClick={onDownload} className="dropdown-item">
                            <Download size={16} /> Download
                        </button>
                        <button onClick={onToggleFavorite} className="dropdown-item">
                            <Star size={16} /> {file.is_favorite ? 'Unfavorite' : 'Favorite'}
                        </button>
                        <button onClick={onDelete} className="dropdown-item-danger">
                            <Trash2 size={16} /> Delete
                        </button>
                    </motion.div>
                )
            }
        </motion.div >
    );
});

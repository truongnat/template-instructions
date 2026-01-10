/**
 * File Card Component - Updated with CSS Animations
 * @module components/file/FileCard
 */

import { useState, useEffect, memo } from 'react';
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
    if (mimeType.startsWith('image/')) return <Image size={24} className="text-pink-500" />;
    if (mimeType.startsWith('video/')) return <Video size={24} className="text-accent-blue" />;
    if (mimeType.startsWith('audio/')) return <Music size={24} className="text-green-500" />;
    if (mimeType.includes('pdf')) return <FileText size={24} className="text-red-500" />;
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) {
        return <Archive size={24} className="text-yellow-500" />;
    }
    if (mimeType.includes('document') || mimeType.includes('text')) {
        return <FileText size={24} className="text-accent-blue" />;
    }
    return <File size={24} className="text-white/40" />;
}

function formatDate(date: Date | string): string {
    const d = new Date(date);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days}d ago`;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function getFileExtension(fileName: string): string {
    return fileName.split('.').pop()?.toUpperCase() || 'FILE';
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

    const isImage = file.mime_type.startsWith('image/');
    const isVideo = file.mime_type.startsWith('video/');

    // Load thumbnail
    useEffect(() => {
        let objectUrl: string | null = null;
        let isMounted = true;

        async function loadThumbnail() {
            if (!isImage) return;
            try {
                let blob: Blob | undefined | null;
                if (file.message_id) {
                    blob = await gramjsClient.downloadThumbnail(file.message_id);
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
        return () => {
            isMounted = false;
            if (objectUrl) URL.revokeObjectURL(objectUrl);
        };
    }, [file.file_unique_id, isImage, file.message_id]);

    const handleActionClick = (e: React.MouseEvent, action: () => void) => {
        e.stopPropagation();
        action();
        setShowActions(false);
    };

    if (isMobile) {
        return (
            <div
                className={`relative rounded-2xl overflow-hidden glass transition-all active:scale-[0.98] ${isSelected ? 'ring-2 ring-accent-purple shadow-lg shadow-accent-purple/20' : ''} animate-fade-in`}
                onClick={() => window.dispatchEvent(new CustomEvent('open-action-sheet', { detail: file }))}
            >
                {/* Checkbox for selection mode */}
                {isSelected && (
                    <div className="absolute top-2 left-2 z-10 w-6 h-6 rounded-full bg-accent-purple flex items-center justify-center animate-scale-in">
                        <Check size={14} className="text-white" />
                    </div>
                )}

                {/* Favorite badge */}
                {file.is_favorite && (
                    <div className="absolute top-2 right-2 z-10">
                        <Star size={14} className="text-yellow-500 fill-yellow-500" />
                    </div>
                )}

                {/* Media Preview */}
                <div className="aspect-square bg-black/40 flex items-center justify-center relative overflow-hidden group">
                    {isImage && thumbnailUrl ? (
                        <img src={thumbnailUrl} alt="" className="w-full h-full object-cover" />
                    ) : (
                        <div className="flex flex-col items-center gap-2">
                            {getFileIcon(file.mime_type)}
                            <span className="text-[10px] font-black uppercase text-white/20">{getFileExtension(file.file_name)}</span>
                        </div>
                    )}
                    {isVideo && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                            <div className="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/20">
                                <Video size={20} className="text-white" />
                            </div>
                        </div>
                    )}
                </div>

                {/* Info Bar */}
                <div className="p-3 bg-white/5 border-t border-white/5">
                    <h3 className="text-[11px] font-bold text-white truncate leading-tight mb-1">{file.file_name}</h3>
                    <div className="flex items-center justify-between text-[10px] text-white/40">
                        <span>{formatFileSize(file.file_size)}</span>
                        <span>{formatDate(file.created_at)}</span>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div
            className={`file-card relative group cursor-pointer animate-fade-in ${isSelected ? 'selected ring-2 ring-accent-purple' : ''}`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => { setIsHovered(false); setShowActions(false); }}
            onClick={(e) => {
                if (e.detail === 2) onPreview();
                else onSelect(e.ctrlKey || e.metaKey);
            }}
        >
            {/* Desktop UI */}
            <div className="absolute top-3 left-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <div
                    className={`w-5 h-5 rounded-lg flex items-center justify-center border-2 transition-all ${isSelected ? 'bg-accent-purple border-accent-purple shadow-lg shadow-accent-purple/30' : 'bg-black/40 border-white/30'
                        }`}
                    onClick={(e) => handleActionClick(e, () => onSelect(true))}
                >
                    {isSelected && <Check size={12} className="text-white" />}
                </div>
            </div>

            {file.is_favorite && (
                <div className="absolute top-3 right-3 z-10 animate-scale-in">
                    <Star size={16} className="text-yellow-500 fill-yellow-500" />
                </div>
            )}

            <div className="aspect-square rounded-2xl overflow-hidden bg-black/40 flex items-center justify-center mb-3 relative group-hover:shadow-2xl transition-all">
                {isImage && thumbnailUrl ? (
                    <img src={thumbnailUrl} alt="" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                ) : (
                    <div className="flex flex-col items-center gap-2 group-hover:scale-110 transition-transform duration-500">
                        {getFileIcon(file.mime_type)}
                        <span className="text-[10px] font-bold text-white/20 uppercase tracking-widest">{getFileExtension(file.file_name)}</span>
                    </div>
                )}

                {/* Desktop Hover Actions */}
                <div className={`absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center gap-3 transition-all duration-300 ${isHovered ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
                    <button onClick={(e) => handleActionClick(e, onPreview)} className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 transition-all hover:scale-110" title="Preview">
                        <Eye size={20} className="text-white" />
                    </button>
                    <button onClick={(e) => handleActionClick(e, onDownload)} className="p-3 rounded-2xl bg-white/10 hover:bg-white/20 transition-all hover:scale-110" title="Download">
                        <Download size={20} className="text-accent-blue" />
                    </button>
                    <button onClick={(e) => handleActionClick(e, onDelete)} className="p-3 rounded-2xl bg-red-500/10 hover:bg-red-500/20 transition-all hover:scale-110" title="Delete">
                        <Trash2 size={20} className="text-red-500" />
                    </button>
                </div>
            </div>

            <div className="px-1 text-left">
                <h3 className="text-sm font-bold text-white truncate max-w-full group-hover:text-accent-purple transition-colors">{file.file_name}</h3>
                <div className="flex items-center gap-2 text-[11px] text-white/30 font-bold mt-1 uppercase tracking-tighter">
                    <span>{formatFileSize(file.file_size)}</span>
                    <span className="opacity-30">•</span>
                    <span>{formatDate(file.created_at)}</span>
                </div>
            </div>

            {/* Context Menu Trigger */}
            <button
                onClick={(e) => handleActionClick(e, () => setShowActions(!showActions))}
                className="absolute bottom-3 right-1 p-1 opacity-0 group-hover:opacity-100 transition-opacity text-white/30 hover:text-white"
            >
                <MoreVertical size={16} />
            </button>

            {/* Quick Context Menu */}
            {showActions && (
                <div className="absolute bottom-12 right-0 z-50 glass rounded-2xl border border-white/10 p-2 shadow-2xl min-w-[140px] animate-scale-in">
                    <button onClick={(e) => handleActionClick(e, onToggleFavorite)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-white/5 text-xs font-bold text-white/70">
                        <Star size={14} className={file.is_favorite ? 'text-yellow-500 fill-yellow-500' : ''} />
                        {file.is_favorite ? 'Unfavorite' : 'Add Favorite'}
                    </button>
                    <button onClick={(e) => handleActionClick(e, onDelete)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-red-500/10 text-xs font-bold text-red-400">
                        <Trash2 size={14} /> Delete File
                    </button>
                </div>
            )}
        </div>
    );
});

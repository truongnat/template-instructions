/**
 * Mobile Action Sheet - iOS-style bottom action menu with CSS Animations
 * @module components/mobile/MobileActionSheet
 */

import { useState, useEffect, useCallback } from 'react';
import {
    Download,
    Share2,
    Star,
    StarOff,
    FolderInput,
    Edit3,
    Trash2,
    X,
    FileIcon,
    Image,
    Video,
    Music,
    FileText,
} from 'lucide-react';
import type { TelegramFile } from '../../lib/telegram/types';
import { formatFileSize } from '../../lib/telegram/types';

interface MobileActionSheetProps {
    file: TelegramFile | null;
    isOpen: boolean;
    onClose: () => void;
    onDownload: (file: TelegramFile) => void;
    onShare?: (file: TelegramFile) => void;
    onToggleFavorite: (file: TelegramFile) => void;
    onMove?: (file: TelegramFile) => void;
    onRename?: (file: TelegramFile) => void;
    onDelete: (file: TelegramFile) => void;
}

// Get icon based on mime type
function getFileIcon(mimeType: string) {
    if (mimeType.startsWith('image/')) return Image;
    if (mimeType.startsWith('video/')) return Video;
    if (mimeType.startsWith('audio/')) return Music;
    if (mimeType.includes('pdf') || mimeType.includes('document')) return FileText;
    return FileIcon;
}

export function MobileActionSheet({
    file,
    isOpen,
    onClose,
    onDownload,
    onShare,
    onToggleFavorite,
    onMove,
    onRename,
    onDelete,
}: MobileActionSheetProps) {
    const [isExiting, setIsExiting] = useState(false);

    const handleClose = useCallback(() => {
        setIsExiting(true);
        setTimeout(() => {
            onClose();
            setIsExiting(false);
        }, 300);
    }, [onClose]);

    // Handle escape key
    useEffect(() => {
        if (!isOpen) return;
        const handleEsc = (e: KeyboardEvent) => e.key === 'Escape' && handleClose();
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [isOpen, handleClose]);

    if (!file || (!isOpen && !isExiting)) return null;

    const FileTypeIcon = getFileIcon(file.mime_type);
    const fileExtension = file.file_name.split('.').pop()?.toUpperCase() || 'FILE';

    const actions = [
        {
            icon: Download,
            label: 'Download',
            onClick: () => { onDownload(file); handleClose(); },
            color: 'text-white/80',
        },
        ...(onShare ? [{
            icon: Share2,
            label: 'Share',
            onClick: () => { onShare(file); handleClose(); },
            color: 'text-white/80',
        }] : []),
        {
            icon: file.is_favorite ? StarOff : Star,
            label: file.is_favorite ? 'Remove from Favorites' : 'Add to Favorites',
            onClick: () => { onToggleFavorite(file); handleClose(); },
            color: file.is_favorite ? 'text-yellow-500' : 'text-white/80',
        },
        ...(onMove ? [{
            icon: FolderInput,
            label: 'Move to Folder',
            onClick: () => { onMove(file); handleClose(); },
            color: 'text-white/80',
        }] : []),
        ...(onRename ? [{
            icon: Edit3,
            label: 'Rename',
            onClick: () => { onRename(file); handleClose(); },
            color: 'text-white/80',
        }] : []),
    ];

    return (
        <div className="fixed inset-0 z-50 flex flex-col justify-end">
            {/* Backdrop */}
            <div
                onClick={handleClose}
                className={`absolute inset-0 transition-opacity duration-300 ${isExiting ? 'opacity-0' : 'opacity-100'
                    }`}
                style={{ background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(4px)' }}
            />

            {/* Action Sheet */}
            <div
                className={`relative glass w-full rounded-t-[2rem] overflow-hidden pb-safe transition-transform duration-300 ${isExiting ? 'animate-slide-down-to-bottom' : 'animate-slide-up-from-bottom'
                    }`}
            >
                {/* Drag Handle */}
                <div className="flex justify-center py-3">
                    <div className="w-10 h-1 rounded-full bg-white/20" />
                </div>

                {/* File Info Header */}
                <div className="flex items-center gap-4 px-6 pb-4 border-b border-white/10">
                    <div className="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 bg-accent-purple/10">
                        <FileTypeIcon size={28} className="text-accent-purple" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="font-bold text-white truncate">{file.file_name}</div>
                        <div className="text-xs text-white/40 mt-0.5">
                            {formatFileSize(file.file_size)} • {fileExtension}
                        </div>
                    </div>
                    <button onClick={handleClose} className="btn-icon">
                        <X size={20} />
                    </button>
                </div>

                {/* Actions List */}
                <div className="py-2">
                    {actions.map((action, index) => {
                        const Icon = action.icon;
                        return (
                            <button
                                key={index}
                                onClick={action.onClick}
                                className={`w-full flex items-center gap-4 px-6 py-4 transition-colors active:bg-white/5 ${action.color}`}
                            >
                                <Icon size={22} />
                                <span className="font-semibold text-sm">{action.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Divider */}
                <div className="h-2 bg-black/20" />

                {/* Delete Action (Danger) */}
                <button
                    onClick={() => { onDelete(file); handleClose(); }}
                    className="w-full flex items-center gap-4 px-6 py-4 transition-colors active:bg-red-500/10 text-red-500"
                >
                    <Trash2 size={22} />
                    <span className="font-semibold text-sm">Delete File</span>
                </button>

                {/* Cancel Button */}
                <div className="p-4">
                    <button
                        onClick={handleClose}
                        className="w-full py-4 rounded-2xl font-bold bg-white/5 text-white/60 hover:text-white transition-all active:scale-95 shadow-sm"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    );
}

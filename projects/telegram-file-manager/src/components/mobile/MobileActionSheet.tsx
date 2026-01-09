/**
 * Mobile Action Sheet - iOS-style bottom action menu
 * @module components/mobile/MobileActionSheet
 */

import { motion, AnimatePresence } from 'framer-motion';
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
    if (!file) return null;

    const FileTypeIcon = getFileIcon(file.mime_type);
    const fileExtension = file.file_name.split('.').pop()?.toUpperCase() || 'FILE';

    const actions = [
        {
            icon: Download,
            label: 'Download',
            onClick: () => { onDownload(file); onClose(); },
            color: 'rgba(255, 255, 255, 0.8)',
        },
        ...(onShare ? [{
            icon: Share2,
            label: 'Share',
            onClick: () => { onShare(file); onClose(); },
            color: 'rgba(255, 255, 255, 0.8)',
        }] : []),
        {
            icon: file.is_favorite ? StarOff : Star,
            label: file.is_favorite ? 'Remove from Favorites' : 'Add to Favorites',
            onClick: () => { onToggleFavorite(file); onClose(); },
            color: file.is_favorite ? '#eab308' : 'rgba(255, 255, 255, 0.8)',
        },
        ...(onMove ? [{
            icon: FolderInput,
            label: 'Move to Folder',
            onClick: () => { onMove(file); onClose(); },
            color: 'rgba(255, 255, 255, 0.8)',
        }] : []),
        ...(onRename ? [{
            icon: Edit3,
            label: 'Rename',
            onClick: () => { onRename(file); onClose(); },
            color: 'rgba(255, 255, 255, 0.8)',
        }] : []),
    ];

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 z-50"
                        style={{ background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(4px)' }}
                    />

                    {/* Action Sheet */}
                    <motion.div
                        initial={{ y: '100%' }}
                        animate={{ y: 0 }}
                        exit={{ y: '100%' }}
                        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                        className="fixed bottom-0 left-0 right-0 z-50 glass"
                        style={{
                            borderTopLeftRadius: '1.5rem',
                            borderTopRightRadius: '1.5rem',
                            paddingBottom: 'env(safe-area-inset-bottom)',
                        }}
                    >
                        {/* Drag Handle */}
                        <div className="flex justify-center py-3">
                            <div
                                className="w-10 h-1 rounded-full"
                                style={{ background: 'rgba(255, 255, 255, 0.3)' }}
                            />
                        </div>

                        {/* File Info Header */}
                        <div className="flex items-center gap-4 px-6 pb-4 border-b border-white/10">
                            <div
                                className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0"
                                style={{ background: 'rgba(124, 58, 237, 0.2)' }}
                            >
                                <FileTypeIcon size={28} style={{ color: '#7c3aed' }} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="font-medium truncate">{file.file_name}</div>
                                <div
                                    className="text-sm"
                                    style={{ color: 'rgba(255, 255, 255, 0.5)' }}
                                >
                                    {formatFileSize(file.file_size)} • {fileExtension}
                                </div>
                            </div>
                            <button onClick={onClose} className="btn-icon">
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
                                        className="w-full flex items-center gap-4 px-6 py-4 transition-colors touch-target"
                                        style={{ color: action.color }}
                                    >
                                        <Icon size={22} />
                                        <span className="font-medium">{action.label}</span>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Divider */}
                        <div className="h-2 bg-black/20" />

                        {/* Delete Action (Danger) */}
                        <button
                            onClick={() => { onDelete(file); onClose(); }}
                            className="w-full flex items-center gap-4 px-6 py-4 transition-colors touch-target"
                            style={{ color: '#f87171' }}
                        >
                            <Trash2 size={22} />
                            <span className="font-medium">Delete</span>
                        </button>

                        {/* Cancel Button */}
                        <div className="p-4">
                            <button
                                onClick={onClose}
                                className="w-full py-3 rounded-xl font-semibold transition-colors"
                                style={{
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    color: 'rgba(255, 255, 255, 0.8)',
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

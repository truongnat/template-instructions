/**
 * Swipeable Drawer Component for Mobile
 * @module components/mobile/SwipeableDrawer
 */

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { PanInfo } from 'framer-motion';
import {
    FolderOpen,
    Image,
    Video,
    FileText,
    Music,
    Star,
    Trash2,
    Settings,
    HardDrive,
    X,
} from 'lucide-react';
import { useFileStore } from '../../store/files';
import { formatFileSize } from '../../lib/telegram/types';

interface SwipeableDrawerProps {
    isOpen: boolean;
    onClose: () => void;
}

export function SwipeableDrawer({ isOpen, onClose }: SwipeableDrawerProps) {
    const { files, filterType, navigateToFolder, setFilterType } = useFileStore();
    const drawerRef = useRef<HTMLDivElement>(null);
    const [dragX, setDragX] = useState(0);

    // Calculate stats
    const activeFiles = files.filter(f => !f.is_deleted);
    const stats = {
        total: activeFiles.length,
        images: activeFiles.filter(f => f.mime_type.startsWith('image/')).length,
        videos: activeFiles.filter(f => f.mime_type.startsWith('video/')).length,
        documents: activeFiles.filter(f =>
            f.mime_type.includes('pdf') || f.mime_type.includes('document') || f.mime_type.includes('text')
        ).length,
        audio: activeFiles.filter(f => f.mime_type.startsWith('audio/')).length,
        favorites: activeFiles.filter(f => f.is_favorite).length,
        trash: files.filter(f => f.is_deleted).length,
        totalSize: activeFiles.reduce((sum, f) => sum + f.file_size, 0),
    };

    const navItems = [
        { id: 'all', label: 'All Files', icon: FolderOpen, badge: stats.total },
        { id: 'images', label: 'Photos', icon: Image, badge: stats.images },
        { id: 'videos', label: 'Videos', icon: Video, badge: stats.videos },
        { id: 'documents', label: 'Documents', icon: FileText, badge: stats.documents },
        { id: 'audio', label: 'Music', icon: Music, badge: stats.audio },
    ];

    // Lock body scroll when drawer is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    const handleNavClick = (filter: string) => {
        navigateToFolder(null);
        setFilterType(filter as never);
        onClose();
    };

    const handleDragEnd = (_: MouseEvent | TouchEvent, info: PanInfo) => {
        if (info.velocity.x < -500 || info.offset.x < -100) {
            onClose();
        }
        setDragX(0);
    };

    const drawerWidth = Math.min(window.innerWidth * 0.85, 320);

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

                    {/* Drawer */}
                    <motion.div
                        ref={drawerRef}
                        initial={{ x: -drawerWidth }}
                        animate={{ x: dragX }}
                        exit={{ x: -drawerWidth }}
                        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                        drag="x"
                        dragConstraints={{ left: -drawerWidth, right: 0 }}
                        dragElastic={0.1}
                        onDrag={(_, info) => setDragX(Math.min(0, info.offset.x))}
                        onDragEnd={handleDragEnd}
                        className="fixed top-0 left-0 bottom-0 z-50 glass flex flex-col"
                        style={{
                            width: drawerWidth,
                            paddingTop: 'env(safe-area-inset-top)',
                            paddingBottom: 'env(safe-area-inset-bottom)',
                            borderRight: '1px solid rgba(255, 255, 255, 0.1)',
                        }}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4 border-b border-white/10">
                            <div className="flex items-center gap-3">
                                <div
                                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                                    style={{ background: 'linear-gradient(135deg, #7c3aed, #2563eb)' }}
                                >
                                    <HardDrive size={20} className="text-white" />
                                </div>
                                <span className="font-semibold text-lg gradient-text">TeleCloud</span>
                            </div>
                            <button onClick={onClose} className="btn-icon">
                                <X size={20} />
                            </button>
                        </div>

                        {/* Navigation */}
                        <nav className="flex-1 p-3 space-y-1 overflow-y-auto scrollbar-hide">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = filterType === item.id;

                                return (
                                    <button
                                        key={item.id}
                                        onClick={() => handleNavClick(item.id)}
                                        className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 touch-target"
                                        style={{
                                            background: isActive ? 'rgba(124, 58, 237, 0.2)' : 'transparent',
                                            border: isActive ? '1px solid rgba(124, 58, 237, 0.3)' : '1px solid transparent',
                                        }}
                                    >
                                        <Icon
                                            size={22}
                                            style={{ color: isActive ? '#7c3aed' : 'rgba(255, 255, 255, 0.6)' }}
                                        />
                                        <span
                                            className="flex-1 text-left font-medium"
                                            style={{ color: isActive ? 'white' : 'rgba(255, 255, 255, 0.8)' }}
                                        >
                                            {item.label}
                                        </span>
                                        <span
                                            className="text-sm"
                                            style={{ color: 'rgba(255, 255, 255, 0.5)' }}
                                        >
                                            {item.badge}
                                        </span>
                                    </button>
                                );
                            })}

                            {/* Divider */}
                            <div className="h-px my-3 bg-white/10" />

                            {/* Favorites */}
                            <button
                                onClick={() => {/* TODO */ }}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all touch-target"
                            >
                                <Star size={22} style={{ color: '#eab308' }} />
                                <span className="flex-1 text-left font-medium" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                                    Favorites
                                </span>
                                <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                                    {stats.favorites}
                                </span>
                            </button>

                            {/* Trash */}
                            <button
                                onClick={() => {/* TODO */ }}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all touch-target"
                            >
                                <Trash2 size={22} style={{ color: '#f87171' }} />
                                <span className="flex-1 text-left font-medium" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                                    Trash
                                </span>
                                <span className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                                    {stats.trash}
                                </span>
                            </button>
                        </nav>

                        {/* Storage Info */}
                        <div className="p-4 border-t border-white/10">
                            <div className="flex items-center gap-2 mb-2" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                                <HardDrive size={16} />
                                <span className="text-sm">Storage</span>
                            </div>
                            <div className="text-xl font-semibold mb-1">
                                {formatFileSize(stats.totalSize)}
                            </div>
                            <div className="text-xs" style={{ color: 'rgba(255, 255, 255, 0.4)' }}>
                                {stats.total} files • Unlimited
                            </div>
                        </div>

                        {/* Settings */}
                        <div className="p-3 border-t border-white/10">
                            <button
                                onClick={() => {
                                    window.dispatchEvent(new CustomEvent('open-settings'));
                                    onClose();
                                }}
                                className="w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all touch-target"
                                style={{ color: 'rgba(255, 255, 255, 0.8)' }}
                            >
                                <Settings size={22} />
                                <span className="font-medium">Settings</span>
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}

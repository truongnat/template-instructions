/**
 * Swipeable Drawer Component for Mobile - Updated with CSS Animations
 * @module components/mobile/SwipeableDrawer
 */

import { useEffect, useState, useCallback } from 'react';
import {
    FolderOpen,
    Image as ImageIcon,
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
    const [isExiting, setIsExiting] = useState(false);

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
        { id: 'images', label: 'Photos', icon: ImageIcon, badge: stats.images },
        { id: 'videos', label: 'Videos', icon: Video, badge: stats.videos },
        { id: 'documents', label: 'Documents', icon: FileText, badge: stats.documents },
        { id: 'audio', label: 'Music', icon: Music, badge: stats.audio },
    ];

    const handleClose = useCallback(() => {
        setIsExiting(true);
        setTimeout(() => {
            onClose();
            setIsExiting(false);
        }, 300);
    }, [onClose]);

    // Lock body scroll when drawer is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
            window.addEventListener('keydown', handleEsc);
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
            window.removeEventListener('keydown', handleEsc);
        };
    }, [isOpen]);

    const handleEsc = (e: KeyboardEvent) => e.key === 'Escape' && handleClose();

    const handleNavClick = (filter: string) => {
        navigateToFolder(null);
        setFilterType(filter as never);
        handleClose();
    };

    if (!isOpen && !isExiting) return null;

    return (
        <div className="fixed inset-0 z-50 flex overflow-hidden">
            {/* Backdrop */}
            <div
                onClick={handleClose}
                className={`absolute inset-0 transition-opacity duration-300 ${isExiting ? 'opacity-0' : 'opacity-100'
                    }`}
                style={{ background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(4px)' }}
            />

            {/* Sidebar Drawer */}
            <div
                className={`relative glass w-[280px] h-full flex flex-col transition-transform duration-300 border-r border-white/10 ${isExiting ? '-translate-x-full' : 'translate-x-0 outline-none'
                    } ${!isOpen && !isExiting ? '-translate-x-full' : 'animate-slide-in-left'}`}
                style={{
                    paddingTop: 'env(safe-area-inset-top)',
                    paddingBottom: 'env(safe-area-inset-bottom)',
                }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center shadow-lg shadow-accent-purple/20">
                            <HardDrive size={20} className="text-white" />
                        </div>
                        <span className="font-black text-lg gradient-text tracking-tight">TeleCloud</span>
                    </div>
                    <button onClick={handleClose} className="btn-icon">
                        <X size={20} />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1 overflow-y-auto scroll-container">
                    <p className="text-[10px] font-black uppercase text-white/20 px-4 mb-2 tracking-widest">Library</p>
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = filterType === item.id;

                        return (
                            <button
                                key={item.id}
                                onClick={() => handleNavClick(item.id)}
                                className={`w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl transition-all duration-200 ${isActive
                                        ? 'bg-accent-purple/10 text-white border border-accent-purple/20'
                                        : 'text-white/60 hover:text-white hover:bg-white/5 border border-transparent'
                                    }`}
                            >
                                <Icon
                                    size={20}
                                    className={isActive ? 'text-accent-purple' : 'text-white/40'}
                                />
                                <span className="flex-1 text-left font-bold text-sm">
                                    {item.label}
                                </span>
                                <span className="text-xs font-mono opacity-40">
                                    {item.badge}
                                </span>
                            </button>
                        );
                    })}

                    <div className="h-px my-6 bg-white/5" />

                    <p className="text-[10px] font-black uppercase text-white/20 px-4 mb-2 tracking-widest">Organize</p>

                    {/* Favorites */}
                    <button
                        onClick={() => {/* TODO */ }}
                        className="w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-white/60 hover:text-white hover:bg-white/5 transition-all"
                    >
                        <Star size={20} className="text-yellow-500" />
                        <span className="flex-1 text-left font-bold text-sm">Favorites</span>
                        <span className="text-xs font-mono opacity-40">{stats.favorites}</span>
                    </button>

                    {/* Trash */}
                    <button
                        onClick={() => {/* TODO */ }}
                        className="w-full flex items-center gap-3 px-4 py-3.5 rounded-2xl text-white/60 hover:text-white hover:bg-white/5 transition-all"
                    >
                        <Trash2 size={20} className="text-red-500" />
                        <span className="flex-1 text-left font-bold text-sm">Trash</span>
                        <span className="text-xs font-mono opacity-40">{stats.trash}</span>
                    </button>
                </nav>

                {/* Storage Info */}
                <div className="p-6 border-t border-white/5 bg-black/5">
                    <div className="flex items-center gap-2 mb-3 text-white/30">
                        <HardDrive size={14} />
                        <span className="text-[10px] uppercase font-bold tracking-widest">Cloud Usage</span>
                    </div>
                    <div className="text-2xl font-black text-white mb-1">
                        {formatFileSize(stats.totalSize)}
                    </div>
                    <div className="text-[10px] font-bold text-white/20 uppercase">
                        {stats.total} Objects • <span className="text-accent-purple">Unlimited</span>
                    </div>
                </div>

                {/* Settings */}
                <div className="p-4 border-t border-white/5">
                    <button
                        onClick={() => {
                            window.dispatchEvent(new CustomEvent('open-settings'));
                            handleClose();
                        }}
                        className="w-full flex items-center gap-3 px-5 py-4 rounded-2xl bg-white/5 hover:bg-white/10 transition-all font-bold text-sm text-white/80"
                    >
                        <Settings size={20} />
                        <span>Settings</span>
                    </button>
                </div>
            </div>
        </div>
    );
}

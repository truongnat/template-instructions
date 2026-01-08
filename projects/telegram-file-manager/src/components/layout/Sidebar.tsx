/**
 * Sidebar Layout Component
 * @module components/layout/Sidebar
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    FolderOpen,
    Image,
    Video,
    FileText,
    Music,
    Star,
    Trash2,
    Settings,
    ChevronLeft,
    ChevronRight,
    HardDrive,
    FolderPlus,
} from 'lucide-react';
import { useFileStore } from '../../store/files';
import { useSettingsStore } from '../../store/settings';
import { formatFileSize } from '../../lib/telegram/types';

// ============================================================================
// TYPES
// ============================================================================

interface NavItem {
    id: string;
    label: string;
    icon: React.ReactNode;
    filter?: string;
    badge?: number;
}

// ============================================================================
// COMPONENT
// ============================================================================

export function Sidebar() {
    const {
        files,
        folders,
        currentFolder,
        filterType,
        navigateToFolder,
        setFilterType,
        createFolder,
    } = useFileStore();

    const { sidebarCollapsed, toggleSidebar } = useSettingsStore();
    const [showNewFolderInput, setShowNewFolderInput] = useState(false);
    const [newFolderName, setNewFolderName] = useState('');

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

    const navItems: NavItem[] = [
        { id: 'all', label: 'All Files', icon: <FolderOpen size={20} />, badge: stats.total },
        { id: 'images', label: 'Photos', icon: <Image size={20} />, filter: 'images', badge: stats.images },
        { id: 'videos', label: 'Videos', icon: <Video size={20} />, filter: 'videos', badge: stats.videos },
        { id: 'documents', label: 'Documents', icon: <FileText size={20} />, filter: 'documents', badge: stats.documents },
        { id: 'audio', label: 'Music', icon: <Music size={20} />, filter: 'audio', badge: stats.audio },
    ];

    const handleNavClick = (item: NavItem) => {
        navigateToFolder(null);
        setFilterType((item.filter as never) || 'all');
    };

    const handleCreateFolder = async () => {
        if (newFolderName.trim()) {
            await createFolder(newFolderName.trim());
            setNewFolderName('');
            setShowNewFolderInput(false);
        }
    };

    const isActive = (item: NavItem) => {
        return filterType === (item.filter || 'all') && !currentFolder;
    };

    return (
        <motion.aside
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="h-full glass flex flex-col transition-all duration-300"
            style={{
                width: sidebarCollapsed ? '4rem' : '16rem',
                borderRight: '1px solid rgba(255,255,255,0.1)',
            }}
        >
            {/* Header */}
            <div
                className="p-4 flex items-center justify-between"
                style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}
            >
                <AnimatePresence>
                    {!sidebarCollapsed && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center gap-2"
                        >
                            <div
                                className="w-8 h-8 rounded-lg flex items-center justify-center"
                                style={{ background: 'linear-gradient(135deg, #7c3aed, #2563eb)' }}
                            >
                                <HardDrive size={18} />
                            </div>
                            <span className="font-semibold gradient-text">TeleCloud</span>
                        </motion.div>
                    )}
                </AnimatePresence>

                <button onClick={toggleSidebar} className="btn-icon">
                    {sidebarCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-2 space-y-1 overflow-y-auto scrollbar-hide">
                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => handleNavClick(item)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200"
                        style={{
                            background: isActive(item) ? 'rgba(124, 58, 237, 0.2)' : 'transparent',
                            border: isActive(item) ? '1px solid rgba(124, 58, 237, 0.3)' : '1px solid transparent',
                            color: isActive(item) ? 'white' : 'rgba(255,255,255,0.7)',
                        }}
                    >
                        <span style={{ color: isActive(item) ? '#7c3aed' : 'rgba(255,255,255,0.5)' }}>
                            {item.icon}
                        </span>

                        <AnimatePresence>
                            {!sidebarCollapsed && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="flex-1 flex items-center justify-between"
                                >
                                    <span className="text-sm font-medium">{item.label}</span>
                                    {item.badge !== undefined && item.badge > 0 && (
                                        <span className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>{item.badge}</span>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </button>
                ))}

                {/* Divider */}
                <div className="h-px my-3" style={{ background: 'rgba(255,255,255,0.1)' }} />

                {/* Favorites */}
                <button
                    onClick={() => {
                        navigateToFolder(null);
                        // TODO: Show favorites filter
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200"
                    style={{ color: 'rgba(255,255,255,0.7)' }}
                >
                    <Star size={20} style={{ color: '#eab308' }} />
                    {!sidebarCollapsed && (
                        <div className="flex-1 flex items-center justify-between">
                            <span className="text-sm font-medium">Favorites</span>
                            <span className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>{stats.favorites}</span>
                        </div>
                    )}
                </button>

                {/* Trash */}
                <button
                    onClick={() => {
                        // TODO: Show trash
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200"
                    style={{ color: 'rgba(255,255,255,0.7)' }}
                >
                    <Trash2 size={20} style={{ color: '#f87171' }} />
                    {!sidebarCollapsed && (
                        <div className="flex-1 flex items-center justify-between">
                            <span className="text-sm font-medium">Trash</span>
                            <span className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>{stats.trash}</span>
                        </div>
                    )}
                </button>

                {/* Divider */}
                <div className="h-px my-3" style={{ background: 'rgba(255,255,255,0.1)' }} />

                {/* Folders Header */}
                {!sidebarCollapsed && (
                    <div className="flex items-center justify-between px-3 py-2">
                        <span className="text-xs uppercase tracking-wider" style={{ color: 'rgba(255,255,255,0.4)' }}>
                            Folders
                        </span>
                        <button
                            onClick={() => setShowNewFolderInput(true)}
                            className="p-1 rounded transition-colors"
                            style={{ color: 'rgba(255,255,255,0.4)' }}
                        >
                            <FolderPlus size={14} />
                        </button>
                    </div>
                )}

                {/* New Folder Input */}
                <AnimatePresence>
                    {showNewFolderInput && !sidebarCollapsed && (
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="px-2"
                        >
                            <input
                                type="text"
                                value={newFolderName}
                                onChange={(e) => setNewFolderName(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleCreateFolder();
                                    if (e.key === 'Escape') setShowNewFolderInput(false);
                                }}
                                placeholder="Folder name..."
                                className="input-glass text-sm py-2"
                                autoFocus
                            />
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Folder List */}
                {folders.filter(f => !f.parent_id).map((folder) => (
                    <button
                        key={folder.id}
                        onClick={() => navigateToFolder(folder.id)}
                        className="w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all duration-200"
                        style={{
                            background: currentFolder === folder.id ? 'rgba(124, 58, 237, 0.2)' : 'transparent',
                            border: currentFolder === folder.id ? '1px solid rgba(124, 58, 237, 0.3)' : '1px solid transparent',
                            color: currentFolder === folder.id ? 'white' : 'rgba(255,255,255,0.7)',
                        }}
                    >
                        <FolderOpen size={18} style={{ color: 'rgba(234, 179, 8, 0.8)' }} />
                        {!sidebarCollapsed && (
                            <span className="text-sm truncate">{folder.name}</span>
                        )}
                    </button>
                ))}
            </nav>

            {/* Storage Info */}
            {!sidebarCollapsed && (
                <div className="p-4" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                    <div className="flex items-center gap-2 text-sm mb-2" style={{ color: 'rgba(255,255,255,0.6)' }}>
                        <HardDrive size={16} />
                        <span>Storage</span>
                    </div>
                    <div className="text-lg font-semibold">
                        {formatFileSize(stats.totalSize)}
                    </div>
                    <div className="text-xs" style={{ color: 'rgba(255,255,255,0.4)' }}>
                        {stats.total} files • Unlimited
                    </div>
                </div>
            )}

            {/* Settings Button */}
            <div className="p-2" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                <button
                    onClick={() => window.dispatchEvent(new CustomEvent('open-settings'))}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200"
                    style={{ color: 'rgba(255,255,255,0.7)' }}
                >
                    <Settings size={20} />
                    {!sidebarCollapsed && <span className="text-sm font-medium">Settings</span>}
                </button>
            </div>
        </motion.aside>
    );
}

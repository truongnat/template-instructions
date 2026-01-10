/**
 * Sidebar Layout Component - Updated with CSS Animations
 * @module components/layout/Sidebar
 */

import { useState } from 'react';
import {
    FolderOpen,
    Image as ImageIcon,
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
        { id: 'images', label: 'Photos', icon: <ImageIcon size={20} />, filter: 'images', badge: stats.images },
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
        <aside
            className={`h-full glass flex flex-col transition-all duration-300 border-r border-white/10 overflow-hidden ${sidebarCollapsed ? 'w-20' : 'w-72'
                }`}
        >
            {/* Header */}
            <div className="p-6 flex items-center justify-between border-b border-white/5">
                {!sidebarCollapsed && (
                    <div className="flex items-center gap-3 animate-fade-in truncate">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center shadow-lg shadow-accent-purple/20">
                            <HardDrive size={22} className="text-white" />
                        </div>
                        <span className="font-black text-lg gradient-text tracking-tighter">TeleCloud</span>
                    </div>
                )}
                <button
                    onClick={toggleSidebar}
                    className={`p-2 rounded-xl transition-all hover:bg-white/5 text-white/40 hover:text-white ${sidebarCollapsed ? 'mx-auto' : ''}`}
                >
                    {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto scroll-container">
                <p className={`text-[10px] font-black uppercase text-white/20 px-4 mb-2 tracking-widest transition-opacity ${sidebarCollapsed ? 'opacity-0' : 'opacity-100'}`}>Library</p>

                {navItems.map((item) => (
                    <button
                        key={item.id}
                        onClick={() => handleNavClick(item)}
                        className={`group w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all ${isActive(item)
                                ? 'bg-accent-purple/10 text-white border border-accent-purple/20 shadow-lg shadow-accent-purple/10'
                                : 'text-white/40 hover:text-white/80 hover:bg-white/5 border border-transparent'
                            }`}
                        title={sidebarCollapsed ? item.label : undefined}
                    >
                        <span className={`transition-colors ${isActive(item) ? 'text-accent-purple' : 'group-hover:text-white'}`}>
                            {item.icon}
                        </span>

                        {!sidebarCollapsed && (
                            <div className="flex-1 flex items-center justify-between animate-fade-in truncate">
                                <span className="text-xs font-bold">{item.label}</span>
                                {item.badge !== undefined && item.badge > 0 && (
                                    <span className="text-[10px] font-mono opacity-40">{item.badge}</span>
                                )}
                            </div>
                        )}
                    </button>
                ))}

                <div className="h-px my-6 bg-white/5" />

                <p className={`text-[10px] font-black uppercase text-white/20 px-4 mb-2 tracking-widest transition-opacity ${sidebarCollapsed ? 'opacity-0' : 'opacity-100'}`}>Organize</p>

                {/* Favorites */}
                <button
                    onClick={() => navigateToFolder(null)}
                    className="group w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl text-white/40 hover:text-white/80 hover:bg-white/5 transition-all"
                    title={sidebarCollapsed ? 'Favorites' : undefined}
                >
                    <Star size={20} className="text-yellow-500" />
                    {!sidebarCollapsed && (
                        <div className="flex-1 flex items-center justify-between animate-fade-in truncate">
                            <span className="text-xs font-bold">Favorites</span>
                            <span className="text-[10px] font-mono opacity-40">{stats.favorites}</span>
                        </div>
                    )}
                </button>

                {/* Trash */}
                <button
                    className="group w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl text-white/40 hover:text-white/80 hover:bg-white/5 transition-all"
                    title={sidebarCollapsed ? 'Trash' : undefined}
                >
                    <Trash2 size={20} className="text-red-500" />
                    {!sidebarCollapsed && (
                        <div className="flex-1 flex items-center justify-between animate-fade-in truncate">
                            <span className="text-xs font-bold">Trash Bin</span>
                            <span className="text-[10px] font-mono opacity-40">{stats.trash}</span>
                        </div>
                    )}
                </button>

                <div className="h-px my-6 bg-white/5" />

                {/* Folders Section */}
                {!sidebarCollapsed && (
                    <div className="flex items-center justify-between px-4 mb-2 animate-fade-in">
                        <span className="text-[10px] font-black uppercase text-white/20 tracking-widest">
                            Collections
                        </span>
                        <button
                            onClick={() => setShowNewFolderInput(true)}
                            className="p-1 hover:bg-white/10 rounded-md transition-colors text-white/30 hover:text-white"
                        >
                            <FolderPlus size={16} />
                        </button>
                    </div>
                )}

                {/* New Folder Input */}
                {showNewFolderInput && !sidebarCollapsed && (
                    <div className="px-2 animate-slide-up">
                        <input
                            type="text"
                            value={newFolderName}
                            onChange={(e) => setNewFolderName(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') handleCreateFolder();
                                if (e.key === 'Escape') setShowNewFolderInput(false);
                            }}
                            placeholder="Type name..."
                            className="input-glass text-xs py-3 px-4 mb-2"
                            autoFocus
                        />
                    </div>
                )}

                {/* Folder List */}
                {folders.filter(f => !f.parent_id).map((folder) => (
                    <button
                        key={folder.id}
                        onClick={() => navigateToFolder(folder.id)}
                        className={`w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all ${currentFolder === folder.id
                                ? 'bg-white/10 text-white shadow-xl'
                                : 'text-white/40 hover:text-white/80 hover:bg-white/5'
                            }`}
                        title={sidebarCollapsed ? folder.name : undefined}
                    >
                        <FolderOpen size={20} className="text-yellow-500/80" />
                        {!sidebarCollapsed && (
                            <span className="text-xs font-bold truncate animate-fade-in">{folder.name}</span>
                        )}
                    </button>
                ))}
            </nav>

            {/* Storage Info */}
            {!sidebarCollapsed && (
                <div className="p-6 bg-black/5 animate-fade-in">
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-white/20 mb-3">
                        <HardDrive size={12} />
                        <span>Cloud Storage</span>
                    </div>
                    <div className="text-2xl font-black text-white mb-1">
                        {formatFileSize(stats.totalSize)}
                    </div>
                    <div className="text-[10px] font-bold text-white/20 uppercase">
                        Object Storage • <span className="text-accent-purple">Active</span>
                    </div>
                </div>
            )}

            {/* Footer / Settings */}
            <div className={`p-4 border-t border-white/5 ${sidebarCollapsed ? 'p-2' : ''}`}>
                <button
                    onClick={() => window.dispatchEvent(new CustomEvent('open-settings'))}
                    className={`w-full flex items-center gap-4 px-4 py-4 rounded-2xl hover:bg-white/5 transition-all text-white/60 hover:text-white ${sidebarCollapsed ? 'justify-center' : ''}`}
                >
                    <Settings size={20} />
                    {!sidebarCollapsed && <span className="text-xs font-bold animate-fade-in">System Settings</span>}
                </button>
            </div>
        </aside>
    );
}

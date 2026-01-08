/**
 * Header Component
 * @module components/layout/Header
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Search,
    LayoutGrid,
    List,
    SortAsc,
    SortDesc,
    Upload,
    Moon,
    Sun,
    ChevronDown,
    X,
} from 'lucide-react';
import { useFileStore } from '../../store/files';
import { useSettingsStore } from '../../store/settings';
import { triggerUpload } from '../upload/DropZone';

// ============================================================================
// COMPONENT
// ============================================================================

export function Header() {
    const {
        viewMode,
        setViewMode,
        sortBy,
        setSortBy,
        sortOrder,
        setSortOrder,
        searchQuery,
        setSearchQuery,
        currentFolder,
        folders,
        filterType,
    } = useFileStore();

    const { theme, setTheme } = useSettingsStore();

    const [showSortMenu, setShowSortMenu] = useState(false);
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const searchRef = useRef<HTMLInputElement>(null);
    const sortMenuRef = useRef<HTMLDivElement>(null);

    // Get current view title
    const getTitle = () => {
        if (currentFolder) {
            const folder = folders.find(f => f.id === currentFolder);
            return folder?.name || 'Folder';
        }
        switch (filterType) {
            case 'images': return 'Photos';
            case 'videos': return 'Videos';
            case 'documents': return 'Documents';
            case 'audio': return 'Music';
            default: return 'All Files';
        }
    };

    // Close sort menu on click outside
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (sortMenuRef.current && !sortMenuRef.current.contains(e.target as Node)) {
                setShowSortMenu(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Keyboard shortcut for search
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
                return;
            }
            if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                searchRef.current?.focus();
            }
            if (e.key === 'Escape' && isSearchFocused) {
                setSearchQuery('');
                searchRef.current?.blur();
            }
            // Ctrl+U for upload
            if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
                e.preventDefault();
                triggerUpload();
            }
        };
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isSearchFocused, setSearchQuery]);

    const sortOptions = [
        { value: 'date', label: 'Date' },
        { value: 'name', label: 'Name' },
        { value: 'size', label: 'Size' },
        { value: 'type', label: 'Type' },
    ] as const;

    return (
        <header className="glass" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', padding: '1rem 1.5rem' }}>
            <div className="flex items-center justify-between gap-4">
                {/* Left: Title */}
                <div className="flex items-center gap-4">
                    <h1 className="text-xl font-semibold">{getTitle()}</h1>
                </div>

                {/* Center: Search */}
                <div className="flex-1 max-w-md">
                    <div className={`relative flex items-center transition-all duration-200 ${isSearchFocused ? 'scale-105' : ''}`}>
                        <Search
                            size={18}
                            className="absolute left-4"
                            style={{ color: isSearchFocused ? '#7c3aed' : 'rgba(255,255,255,0.4)' }}
                        />
                        <input
                            ref={searchRef}
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onFocus={() => setIsSearchFocused(true)}
                            onBlur={() => setIsSearchFocused(false)}
                            placeholder="Search files... (press /)"
                            className="input-glass pl-11 pr-10 text-sm"
                        />
                        <AnimatePresence>
                            {searchQuery && (
                                <motion.button
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.8 }}
                                    onClick={() => setSearchQuery('')}
                                    className="absolute right-3 p-1 rounded-full"
                                    style={{ color: 'rgba(255,255,255,0.4)' }}
                                >
                                    <X size={14} />
                                </motion.button>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-2">
                    {/* View Mode Toggle */}
                    <div className="flex items-center glass-sm rounded-lg p-1 gap-1">
                        <button
                            onClick={() => setViewMode('grid')}
                            className="p-2 rounded-md transition-all"
                            style={{
                                background: viewMode === 'grid' ? 'rgba(124, 58, 237, 0.3)' : 'transparent',
                                color: viewMode === 'grid' ? '#7c3aed' : 'rgba(255,255,255,0.5)',
                            }}
                            title="Grid view (Ctrl+1)"
                        >
                            <LayoutGrid size={18} />
                        </button>
                        <button
                            onClick={() => setViewMode('list')}
                            className="p-2 rounded-md transition-all"
                            style={{
                                background: viewMode === 'list' ? 'rgba(124, 58, 237, 0.3)' : 'transparent',
                                color: viewMode === 'list' ? '#7c3aed' : 'rgba(255,255,255,0.5)',
                            }}
                            title="List view (Ctrl+2)"
                        >
                            <List size={18} />
                        </button>
                    </div>

                    {/* Sort Dropdown */}
                    <div className="relative" ref={sortMenuRef}>
                        <button
                            onClick={() => setShowSortMenu(!showSortMenu)}
                            className="btn-ghost flex items-center gap-2 text-sm"
                        >
                            {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
                            <span className="hidden sm:inline">
                                {sortOptions.find(o => o.value === sortBy)?.label}
                            </span>
                            <ChevronDown size={14} className={`transition-transform ${showSortMenu ? 'rotate-180' : ''}`} />
                        </button>

                        <AnimatePresence>
                            {showSortMenu && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="dropdown-menu"
                                    style={{ right: 0, marginTop: '0.5rem' }}
                                >
                                    {sortOptions.map((option) => (
                                        <button
                                            key={option.value}
                                            onClick={() => {
                                                if (sortBy === option.value) {
                                                    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
                                                } else {
                                                    setSortBy(option.value);
                                                }
                                                setShowSortMenu(false);
                                            }}
                                            className="dropdown-item"
                                            style={{ color: sortBy === option.value ? '#7c3aed' : undefined }}
                                        >
                                            <span className="flex-1">{option.label}</span>
                                            {sortBy === option.value && (
                                                sortOrder === 'asc' ? <SortAsc size={14} /> : <SortDesc size={14} />
                                            )}
                                        </button>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    {/* Theme Toggle */}
                    <button
                        onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                        className="btn-icon"
                        title="Toggle theme"
                    >
                        {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
                    </button>

                    {/* Upload Button */}
                    <button
                        onClick={triggerUpload}
                        className="btn-gradient flex items-center gap-2"
                    >
                        <Upload size={18} />
                        <span className="hidden sm:inline">Upload</span>
                    </button>
                </div>
            </div>
        </header>
    );
}

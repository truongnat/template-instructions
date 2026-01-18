/**
 * Header Component - Updated with CSS Animations
 * @module components/layout/Header
 */

import { useState, useRef, useEffect } from 'react';
import {
    Search,
    LayoutGrid,
    List,
    SortAsc,
    SortDesc,
    Upload,
    ChevronDown,
    X,
} from 'lucide-react';
import { useFileStore } from '../../store/files';
import { triggerUpload } from '../upload/DropZone';
import { useResponsive } from '../../hooks/useResponsive';

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

    const { isMobile } = useResponsive();

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
        <header className="glass sticky top-0 z-30 border-b border-white/10 px-6 py-4">
            <div className="flex items-center justify-between gap-6">
                {/* Left: Title */}
                <div className="flex items-center gap-4 min-w-[120px]">
                    <h1 className="text-xl font-black gradient-text tracking-tight animate-fade-in">{getTitle()}</h1>
                </div>

                {/* Center: Search */}
                <div className="flex-1 max-w-xl hidden sm:block">
                    <div className={`relative flex items-center transition-all duration-500 rounded-2xl ${isSearchFocused ? 'scale-[1.02] ring-4 ring-accent-purple/10' : ''}`}>
                        <Search
                            size={18}
                            className="absolute left-4 transition-colors duration-300"
                            style={{ color: isSearchFocused ? 'var(--accent-purple)' : 'rgba(255,255,255,0.2)' }}
                        />
                        <input
                            ref={searchRef}
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            onFocus={() => setIsSearchFocused(true)}
                            onBlur={() => setIsSearchFocused(false)}
                            placeholder="Search your cloud... (press /)"
                            className="input-glass pl-12 pr-12 py-3 text-sm font-medium placeholder:text-white/20"
                        />
                        {searchQuery && (
                            <button
                                onClick={() => setSearchQuery('')}
                                className="absolute right-3 p-1.5 rounded-xl hover:bg-white/10 transition-all text-white/30 hover:text-white active:scale-90 animate-scale-in"
                            >
                                <X size={16} />
                            </button>
                        )}
                    </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center gap-3">
                    {/* View Mode Toggle - Only on desktop */}
                    {!isMobile && (
                        <div className="flex items-center bg-black/20 rounded-xl p-1 gap-1 border border-white/5">
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`p-2 rounded-lg transition-all ${viewMode === 'grid' ? 'bg-white/10 text-white shadow-lg' : 'text-white/30 hover:text-white/60'
                                    }`}
                                title="Grid (Ctrl+1)"
                            >
                                <LayoutGrid size={18} />
                            </button>
                            <button
                                onClick={() => setViewMode('list')}
                                className={`p-2 rounded-lg transition-all ${viewMode === 'list' ? 'bg-white/10 text-white shadow-lg' : 'text-white/30 hover:text-white/60'
                                    }`}
                                title="List (Ctrl+2)"
                            >
                                <List size={18} />
                            </button>
                        </div>
                    )}

                    {/* Sort Dropdown */}
                    <div className="relative" ref={sortMenuRef}>
                        <button
                            onClick={() => setShowSortMenu(!showSortMenu)}
                            className="glass-sm px-4 py-2 flex items-center gap-2 text-sm font-bold text-white/70 hover:text-white transition-all rounded-xl active:scale-95"
                        >
                            {sortOrder === 'asc' ? <SortAsc size={16} /> : <SortDesc size={16} />}
                            <span className="hidden lg:inline">
                                {sortOptions.find(o => o.value === sortBy)?.label}
                            </span>
                            <ChevronDown size={14} className={`transition-transform duration-300 ${showSortMenu ? 'rotate-180' : ''}`} />
                        </button>

                        {showSortMenu && (
                            <div className="absolute right-0 mt-3 w-48 glass rounded-2xl border border-white/10 p-2 shadow-2xl animate-scale-in origin-top-right">
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
                                        className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all text-xs font-bold ${sortBy === option.value ? 'bg-accent-purple/10 text-accent-purple' : 'text-white/50 hover:bg-white/5 hover:text-white'
                                            }`}
                                    >
                                        <span>{option.label}</span>
                                        {sortBy === option.value && (
                                            sortOrder === 'asc' ? <SortAsc size={14} /> : <SortDesc size={14} />
                                        )}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Upload Button */}
                    <button
                        onClick={triggerUpload}
                        className="btn-gradient px-6 py-2.5 flex items-center gap-2 group"
                    >
                        <Upload size={18} className="group-hover:-translate-y-0.5 transition-transform" />
                        <span className="hidden sm:inline">Upload</span>
                    </button>
                </div>
            </div>
        </header>
    );
}

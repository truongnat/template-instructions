/**
 * Mobile Header Component - Updated with CSS Animations
 * @module components/mobile/MobileHeader
 */

import { useState, useRef, useEffect } from 'react';
import { Menu, Search, X, ArrowLeft, HardDrive } from 'lucide-react';
import { useFileStore } from '../../store/files';

interface MobileHeaderProps {
    onMenuClick: () => void;
    title?: string;
}

export function MobileHeader({ onMenuClick, title = 'TeleCloud' }: MobileHeaderProps) {
    const { searchQuery, setSearchQuery, currentFolder, folders, filterType, navigateToFolder } = useFileStore();
    const [isSearchExpanded, setIsSearchExpanded] = useState(false);
    const searchInputRef = useRef<HTMLInputElement>(null);

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
            default: return title;
        }
    };

    // Focus input when search expands
    useEffect(() => {
        if (isSearchExpanded && searchInputRef.current) {
            searchInputRef.current.focus();
        }
    }, [isSearchExpanded]);

    const handleSearchToggle = () => {
        if (isSearchExpanded && searchQuery) {
            setSearchQuery('');
        }
        setIsSearchExpanded(!isSearchExpanded);
    };

    const handleBack = () => {
        if (currentFolder) {
            navigateToFolder(null);
        }
    };

    const showBackButton = !!currentFolder;

    return (
        <header
            className="fixed top-0 left-0 right-0 z-40 glass safe-top"
            style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}
        >
            <div className="flex items-center h-16 px-5 gap-4">
                {isSearchExpanded ? (
                    /* Expanded Search Mode */
                    <div className="flex items-center gap-3 flex-1 animate-fade-in">
                        <button onClick={handleSearchToggle} className="btn-icon">
                            <ArrowLeft size={22} className="text-white/60" />
                        </button>
                        <div className="relative flex-1 bg-white/5 rounded-2xl px-4 flex items-center border border-white/5">
                            <input
                                ref={searchInputRef}
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search your cloud..."
                                className="w-full py-2.5 bg-transparent text-white font-bold placeholder:text-white/20 outline-none text-[16px]"
                            />
                            {searchQuery && (
                                <button onClick={() => setSearchQuery('')} className="p-1 hover:text-white text-white/40">
                                    <X size={18} />
                                </button>
                            )}
                        </div>
                    </div>
                ) : (
                    /* Normal Header Mode */
                    <div className="flex items-center gap-4 flex-1 animate-fade-in">
                        {/* Menu or Back Button */}
                        {showBackButton ? (
                            <button onClick={handleBack} className="btn-icon">
                                <ArrowLeft size={22} className="text-white/80" />
                            </button>
                        ) : (
                            <button onClick={onMenuClick} className="btn-icon">
                                <Menu size={22} className="text-white/80" />
                            </button>
                        )}

                        {/* Logo & Title */}
                        <div className="flex-1 min-w-0 flex items-center gap-3">
                            {!showBackButton && (
                                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center flex-shrink-0 shadow-lg shadow-accent-purple/20">
                                    <HardDrive size={18} className="text-white" />
                                </div>
                            )}
                            <span className="font-black text-lg truncate gradient-text tracking-tighter uppercase leading-none">
                                {getTitle()}
                            </span>
                        </div>

                        {/* Search Button */}
                        <button onClick={handleSearchToggle} className="btn-icon">
                            <Search size={22} className="text-white/60" />
                        </button>
                    </div>
                )}
            </div>
        </header>
    );
}

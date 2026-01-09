/**
 * Mobile Header Component
 * @module components/mobile/MobileHeader
 */

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
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
            className="fixed top-0 left-0 right-0 z-40 glass"
            style={{
                paddingTop: 'env(safe-area-inset-top)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}
        >
            <div className="flex items-center h-14 px-4 gap-3">
                <AnimatePresence mode="wait">
                    {isSearchExpanded ? (
                        // Expanded Search Mode
                        <motion.div
                            key="search"
                            initial={{ opacity: 0, width: 0 }}
                            animate={{ opacity: 1, width: '100%' }}
                            exit={{ opacity: 0, width: 0 }}
                            className="flex items-center gap-2 flex-1"
                        >
                            <button
                                onClick={handleSearchToggle}
                                className="btn-icon touch-target"
                            >
                                <ArrowLeft size={22} />
                            </button>

                            <div className="relative flex-1">
                                <input
                                    ref={searchInputRef}
                                    type="text"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    placeholder="Search files..."
                                    className="w-full py-2 px-4 bg-transparent text-white placeholder:text-white/40 outline-none"
                                    style={{ fontSize: '16px' }} // Prevents iOS zoom
                                />
                                {searchQuery && (
                                    <button
                                        onClick={() => setSearchQuery('')}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1"
                                    >
                                        <X size={18} style={{ color: 'rgba(255,255,255,0.5)' }} />
                                    </button>
                                )}
                            </div>
                        </motion.div>
                    ) : (
                        // Normal Header Mode
                        <motion.div
                            key="header"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center gap-3 flex-1"
                        >
                            {/* Menu or Back Button */}
                            {showBackButton ? (
                                <button onClick={handleBack} className="btn-icon touch-target">
                                    <ArrowLeft size={22} />
                                </button>
                            ) : (
                                <button onClick={onMenuClick} className="btn-icon touch-target">
                                    <Menu size={22} />
                                </button>
                            )}

                            {/* Logo & Title */}
                            <div className="flex items-center gap-2 flex-1">
                                {!showBackButton && (
                                    <div
                                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                        style={{ background: 'linear-gradient(135deg, #7c3aed, #2563eb)' }}
                                    >
                                        <HardDrive size={16} className="text-white" />
                                    </div>
                                )}
                                <span className="font-semibold text-lg truncate gradient-text">
                                    {getTitle()}
                                </span>
                            </div>

                            {/* Search Button */}
                            <button onClick={handleSearchToggle} className="btn-icon touch-target">
                                <Search size={22} />
                            </button>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </header>
    );
}

/**
 * File Grid Component - Responsive Layout
 * @module components/file/FileGrid
 */

import { useMemo, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FolderOpen, RefreshCw } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { FileCard } from './FileCard';
import { triggerUpload } from '../upload/DropZone';
import { useResponsive } from '../../hooks/useResponsive';

// ============================================================================
// ANIMATION VARIANTS
// ============================================================================

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.03,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

// ============================================================================
// PULL TO REFRESH HOOK
// ============================================================================

function usePullToRefresh(onRefresh: () => Promise<void>) {
    const [isPulling, setIsPulling] = useState(false);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [pullDistance, setPullDistance] = useState(0);
    const startY = useRef(0);
    const containerRef = useRef<HTMLDivElement>(null);

    const handleTouchStart = (e: React.TouchEvent) => {
        if (containerRef.current?.scrollTop === 0) {
            startY.current = e.touches[0].clientY;
            setIsPulling(true);
        }
    };

    const handleTouchMove = (e: React.TouchEvent) => {
        if (!isPulling || isRefreshing) return;

        const currentY = e.touches[0].clientY;
        const diff = currentY - startY.current;

        if (diff > 0 && diff < 150) {
            setPullDistance(diff);
        }
    };

    const handleTouchEnd = async () => {
        if (pullDistance > 80 && !isRefreshing) {
            setIsRefreshing(true);
            await onRefresh();
            setIsRefreshing(false);
        }
        setPullDistance(0);
        setIsPulling(false);
    };

    return {
        containerRef,
        isPulling,
        isRefreshing,
        pullDistance,
        handleTouchStart,
        handleTouchMove,
        handleTouchEnd,
    };
}

// ============================================================================
// COMPONENT
// ============================================================================

export function FileGrid() {
    const {
        files: storeFiles,
        getFilteredFiles,
        selectedFiles,
        selectFile,
        downloadFile,
        moveToTrash,
        toggleFavorite,
        isLoading,
        loadFiles,
        viewMode,
        filterType,
        searchQuery,
        currentFolder,
        sortBy,
        sortOrder,
    } = useFileStore();

    const { isMobile, isTablet, breakpoint } = useResponsive();

    // Pull to refresh
    const {
        containerRef,
        isRefreshing,
        pullDistance,
        handleTouchStart,
        handleTouchMove,
        handleTouchEnd,
    } = usePullToRefresh(async () => {
        await loadFiles();
    });

    // Re-compute filtered files when dependencies change
    const files = useMemo(() => getFilteredFiles(), [
        storeFiles,
        filterType,
        searchQuery,
        currentFolder,
        sortBy,
        sortOrder,
        getFilteredFiles
    ]);

    // Get grid columns based on breakpoint
    const getGridClass = () => {
        if (viewMode === 'list') return 'space-y-2';

        switch (breakpoint) {
            case 'xs':
                return 'grid grid-cols-2 gap-3';
            case 'sm':
                return 'grid grid-cols-2 gap-3';
            case 'md':
                return 'grid grid-cols-3 gap-4';
            case 'lg':
                return 'grid grid-cols-4 gap-4';
            case 'xl':
            default:
                return 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4';
        }
    };

    // Empty State
    if (!isLoading && files.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex-1 flex flex-col items-center justify-center p-6 ${isMobile ? 'pt-header pb-nav' : 'p-8'}`}
            >
                <div className="glass p-6 md:p-8 rounded-3xl text-center max-w-md w-full">
                    <div
                        className="w-16 h-16 md:w-20 md:h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 md:mb-6"
                        style={{ background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(37, 99, 235, 0.2))' }}
                    >
                        <FolderOpen size={isMobile ? 32 : 40} style={{ color: '#7c3aed' }} />
                    </div>
                    <h2 className="text-lg md:text-xl font-semibold mb-2">No files here</h2>
                    <p className="mb-4 md:mb-6 text-sm md:text-base" style={{ color: 'rgba(255,255,255,0.6)' }}>
                        {isMobile
                            ? 'Tap the upload button to get started'
                            : 'Drop files here or click the upload button to get started'
                        }
                    </p>
                    <button
                        onClick={triggerUpload}
                        className="btn-gradient inline-flex items-center gap-2 touch-target"
                    >
                        <Upload size={18} />
                        Upload Files
                    </button>
                </div>
            </motion.div>
        );
    }

    // Loading State
    if (isLoading) {
        const skeletonCount = isMobile ? 6 : 12;
        return (
            <div className={`flex-1 p-4 md:p-6 ${isMobile ? 'pt-header pb-nav' : ''}`}>
                <div className={getGridClass()}>
                    {Array.from({ length: skeletonCount }).map((_, i) => (
                        <div key={i} className="glass p-3 md:p-4 rounded-xl">
                            <div className="aspect-square rounded-lg md:rounded-xl skeleton mb-2 md:mb-3" />
                            <div className="h-3 md:h-4 skeleton rounded mb-1 md:mb-2" />
                            <div className="h-2 md:h-3 skeleton rounded w-2/3" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <motion.div
            ref={containerRef}
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className={`flex-1 p-4 md:p-6 overflow-y-auto scroll-container relative ${isMobile ? '' : ''}`}
            onTouchStart={isMobile ? handleTouchStart : undefined}
            onTouchMove={isMobile ? handleTouchMove : undefined}
            onTouchEnd={isMobile ? handleTouchEnd : undefined}
        >
            {/* Pull to Refresh Indicator */}
            {isMobile && pullDistance > 0 && (
                <motion.div
                    className="absolute top-0 left-0 right-0 flex justify-center py-4 z-10"
                    style={{
                        transform: `translateY(${pullDistance - 40}px)`,
                        opacity: pullDistance / 80,
                    }}
                >
                    <motion.div
                        animate={{ rotate: isRefreshing ? 360 : pullDistance * 2 }}
                        transition={isRefreshing ? { repeat: Infinity, duration: 1 } : { duration: 0 }}
                    >
                        <RefreshCw
                            size={24}
                            style={{
                                color: pullDistance > 80 ? '#7c3aed' : 'rgba(255,255,255,0.5)'
                            }}
                        />
                    </motion.div>
                </motion.div>
            )}

            {/* Selected count indicator for mobile */}
            {isMobile && selectedFiles.length > 0 && (
                <motion.div
                    initial={{ y: -50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -50, opacity: 0 }}
                    className="sticky top-0 z-20 mb-4 py-2 px-4 rounded-xl glass text-center"
                    style={{ background: 'rgba(124, 58, 237, 0.2)', border: '1px solid rgba(124, 58, 237, 0.3)' }}
                >
                    <span className="font-medium">{selectedFiles.length} selected</span>
                    <button
                        onClick={() => moveToTrash(selectedFiles)}
                        className="ml-4 text-red-400 font-medium"
                    >
                        Delete
                    </button>
                </motion.div>
            )}

            {/* File Grid */}
            <div className={getGridClass()}>
                <AnimatePresence mode="popLayout">
                    {files.map((file) => (
                        <motion.div key={file.file_unique_id} variants={itemVariants} layout>
                            <FileCard
                                file={file}
                                isSelected={selectedFiles.includes(file.file_unique_id)}
                                onSelect={(multi) => selectFile(file.file_unique_id, multi)}
                                onPreview={() => {
                                    window.dispatchEvent(new CustomEvent('preview-file', { detail: file }));
                                }}
                                onDownload={() => downloadFile(file)}
                                onDelete={() => moveToTrash([file.file_unique_id])}
                                onToggleFavorite={() => toggleFavorite(file.file_unique_id)}
                            />
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* Bottom padding for mobile nav */}
            {isMobile && <div className="h-4" />}
        </motion.div>
    );
}

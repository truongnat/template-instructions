/**
 * File Grid Component - Responsive Layout with CSS Animations
 * @module components/file/FileGrid
 */

import { useMemo, useState, useRef } from 'react';
import { Upload as UploadIcon, FolderOpen, RefreshCw } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { FileCard } from './FileCard';
import { triggerUpload } from '../upload/DropZone';
import { useResponsive } from '../../hooks/useResponsive';

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
        if (diff > 0 && diff < 150) setPullDistance(diff);
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

    const { isMobile, breakpoint } = useResponsive();

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

    const files = useMemo(() => getFilteredFiles(), [
        storeFiles,
        filterType,
        searchQuery,
        currentFolder,
        sortBy,
        sortOrder,
        getFilteredFiles
    ]);

    const getGridClass = () => {
        if (viewMode === 'list') return 'space-y-3';
        switch (breakpoint) {
            case 'xs': return 'grid grid-cols-2 gap-4';
            case 'sm': return 'grid grid-cols-2 gap-4';
            case 'md': return 'grid grid-cols-3 gap-5';
            case 'lg': return 'grid grid-cols-4 gap-6';
            case 'xl':
            default: return 'grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6';
        }
    };

    if (!isLoading && files.length === 0) {
        return (
            <div className={`flex-1 flex flex-col items-center justify-center p-8 animate-fade-in`}>
                <div className="glass p-10 rounded-[3rem] text-center max-w-md w-full border border-white/5 relative overflow-hidden group">
                    <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-accent-purple to-accent-blue" />
                    <div className="w-24 h-24 rounded-[2.5rem] bg-gradient-to-br from-accent-purple/10 to-accent-blue/10 flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-500">
                        <FolderOpen size={48} className="text-accent-purple" />
                    </div>
                    <h2 className="text-2xl font-black text-white mb-3">No Files Found</h2>
                    <p className="mb-8 text-white/40 font-medium px-4">
                        Your cloud storage is empty. Tap upload to start storing unlimited data.
                    </p>
                    <button
                        onClick={triggerUpload}
                        className="btn-gradient px-8 py-3.5 flex items-center justify-center gap-3 mx-auto shadow-xl shadow-accent-purple/20"
                    >
                        <UploadIcon size={20} />
                        <span>Upload Now</span>
                    </button>
                </div>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="flex-1 p-6 animate-fade-in">
                <div className={getGridClass()}>
                    {Array.from({ length: isMobile ? 6 : 12 }).map((_, i) => (
                        <div key={i} className="glass rounded-3xl p-4 min-h-[160px] animate-pulse">
                            <div className="aspect-square bg-white/5 rounded-2xl mb-4" />
                            <div className="h-4 bg-white/5 rounded-lg w-3/4 mb-2" />
                            <div className="h-3 bg-white/5 rounded-lg w-1/2" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div
            ref={containerRef}
            className={`flex-1 p-6 overflow-y-auto scroll-container relative`}
            onTouchStart={isMobile ? handleTouchStart : undefined}
            onTouchMove={isMobile ? handleTouchMove : undefined}
            onTouchEnd={isMobile ? handleTouchEnd : undefined}
        >
            {/* Pull to Refresh */}
            {isMobile && pullDistance > 0 && (
                <div
                    className="absolute top-0 left-0 right-0 flex justify-center py-6 z-10 pointer-events-none"
                    style={{
                        opacity: Math.min(1, pullDistance / 100),
                        transform: `translateY(${Math.min(20, pullDistance - 40)}px)`
                    }}
                >
                    <div className={`${isRefreshing ? 'animate-spin' : ''} transition-transform`}>
                        <RefreshCw size={24} className={pullDistance > 80 ? 'text-accent-purple' : 'text-white/20'} />
                    </div>
                </div>
            )}

            {/* Selection Toolbar for Mobile */}
            {isMobile && selectedFiles.length > 0 && (
                <div className="sticky top-0 z-20 mb-6 py-4 px-6 rounded-2xl glass border border-accent-purple/30 bg-accent-purple/10 flex items-center justify-between shadow-2xl animate-slide-up">
                    <span className="font-black text-sm text-white">{selectedFiles.length} Selected</span>
                    <button onClick={() => moveToTrash(selectedFiles)} className="text-red-500 font-black text-xs uppercase tracking-widest">
                        Delete
                    </button>
                </div>
            )}

            {/* Grid Content */}
            <div className={getGridClass()}>
                {files.map((file, idx) => (
                    <div
                        key={file.file_unique_id}
                        className="animate-fade-in"
                        style={{ animationDelay: `${idx * 20}ms` }}
                    >
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
                    </div>
                ))}
            </div>

            {isMobile && <div className="h-6" />}
        </div>
    );
}

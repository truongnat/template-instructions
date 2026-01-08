/**
 * File Grid Component
 * @module components/file/FileGrid
 */

import { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FolderOpen } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { FileCard } from './FileCard';
import { triggerUpload } from '../upload/DropZone';

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
        viewMode,
        filterType,
        searchQuery,
        currentFolder,
        sortBy,
        sortOrder,
    } = useFileStore();

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

    // Empty State
    if (!isLoading && files.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex-1 flex flex-col items-center justify-center p-8"
            >
                <div className="glass p-8 rounded-3xl text-center max-w-md">
                    <div
                        className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
                        style={{ background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(37, 99, 235, 0.2))' }}
                    >
                        <FolderOpen size={40} style={{ color: '#7c3aed' }} />
                    </div>
                    <h2 className="text-xl font-semibold mb-2">No files here</h2>
                    <p className="mb-6" style={{ color: 'rgba(255,255,255,0.6)' }}>
                        Drop files here or click the upload button to get started
                    </p>
                    <button
                        onClick={triggerUpload}
                        className="btn-gradient inline-flex items-center gap-2"
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
        return (
            <div className="flex-1 p-6">
                <div className={viewMode === 'grid'
                    ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
                    : "space-y-2"
                }>
                    {Array.from({ length: 12 }).map((_, i) => (
                        <div key={i} className="glass p-4">
                            <div className="aspect-square rounded-xl skeleton mb-3" />
                            <div className="h-4 skeleton rounded mb-2" />
                            <div className="h-3 skeleton rounded w-2/3" />
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="flex-1 p-6 overflow-y-auto"
        >
            <div className={viewMode === 'grid'
                ? "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
                : "space-y-2"
            }>
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
        </motion.div>
    );
}

/**
 * Upload Drop Zone Component
 * @module components/upload/DropZone
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { formatFileSize } from '../../lib/telegram/types';

// ============================================================================
// CONSTANTS
// ============================================================================

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

// ============================================================================
// TYPES
// ============================================================================

interface UploadItem {
    id: string;
    file: File;
    progress: number;
    status: 'pending' | 'uploading' | 'complete' | 'error';
    error?: string;
}

// ============================================================================
// COMPONENT
// ============================================================================

export function DropZone() {
    const [isDragging, setIsDragging] = useState(false);
    const [uploads, setUploads] = useState<UploadItem[]>([]);
    const [showPanel, setShowPanel] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { uploadFile } = useFileStore();

    // Expose file input trigger globally
    useEffect(() => {
        const handleTriggerUpload = () => {
            fileInputRef.current?.click();
        };

        window.addEventListener('trigger-upload', handleTriggerUpload);
        return () => window.removeEventListener('trigger-upload', handleTriggerUpload);
    }, []);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDragEnter = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();

        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        const x = e.clientX;
        const y = e.clientY;

        if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
            setIsDragging(false);
        }
    }, []);

    const processFiles = useCallback(async (files: FileList | File[]) => {
        const fileArray = Array.from(files);

        if (fileArray.length === 0) return;

        // Create upload items
        const newUploads: UploadItem[] = fileArray.map(file => ({
            id: crypto.randomUUID(),
            file,
            progress: 0,
            status: file.size > MAX_FILE_SIZE ? 'error' : 'pending',
            error: file.size > MAX_FILE_SIZE
                ? `File too large (max ${formatFileSize(MAX_FILE_SIZE)})`
                : undefined,
        }));

        setUploads(prev => [...prev, ...newUploads]);
        setShowPanel(true);

        // Upload each file sequentially
        for (const upload of newUploads) {
            if (upload.status === 'error') continue;

            setUploads(prev =>
                prev.map(u => u.id === upload.id ? { ...u, status: 'uploading' } : u)
            );

            try {
                await uploadFile(upload.file, (progress) => {
                    setUploads(prev =>
                        prev.map(u => u.id === upload.id ? { ...u, progress } : u)
                    );
                });

                setUploads(prev =>
                    prev.map(u => u.id === upload.id ? { ...u, status: 'complete', progress: 100 } : u)
                );
            } catch (error) {
                setUploads(prev =>
                    prev.map(u => u.id === upload.id ? {
                        ...u,
                        status: 'error',
                        error: error instanceof Error ? error.message : 'Upload failed'
                    } : u)
                );
            }
        }
    }, [uploadFile]);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);

        const { files } = e.dataTransfer;
        if (files.length > 0) {
            processFiles(files);
        }
    }, [processFiles]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { files } = e.target;
        if (files && files.length > 0) {
            processFiles(files);
        }
        // Reset input so same file can be selected again
        e.target.value = '';
    }, [processFiles]);

    const clearCompleted = useCallback(() => {
        const remaining = uploads.filter(u => u.status !== 'complete' && u.status !== 'error');
        setUploads(remaining);
        if (remaining.length === 0) {
            setShowPanel(false);
        }
    }, [uploads]);

    const removeUpload = useCallback((id: string) => {
        setUploads(prev => {
            const remaining = prev.filter(u => u.id !== id);
            if (remaining.length === 0) {
                setShowPanel(false);
            }
            return remaining;
        });
    }, []);

    const completedCount = uploads.filter(u => u.status === 'complete').length;
    const errorCount = uploads.filter(u => u.status === 'error').length;
    const uploadingCount = uploads.filter(u => u.status === 'uploading').length;

    return (
        <>
            {/* Hidden File Input */}
            <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload-input"
            />

            {/* Global Drag Listener */}
            <div
                className="fixed inset-0 pointer-events-none z-40"
                onDragEnter={(e) => {
                    e.preventDefault();
                    setIsDragging(true);
                }}
            />

            {/* Drag Overlay */}
            <AnimatePresence>
                {isDragging && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="drag-overlay pointer-events-auto"
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                    >
                        <div className="text-center">
                            <motion.div
                                animate={{ y: [0, -10, 0] }}
                                transition={{ repeat: Infinity, duration: 1.5 }}
                                className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4"
                                style={{ background: 'rgba(124, 58, 237, 0.2)' }}
                            >
                                <FileUp size={40} style={{ color: '#7c3aed' }} />
                            </motion.div>
                            <h2 className="text-2xl font-semibold mb-2">Drop files here</h2>
                            <p style={{ color: 'rgba(255,255,255,0.6)' }}>Release to upload</p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Floating Upload Panel */}
            <AnimatePresence>
                {showPanel && uploads.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, y: 100, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 100, scale: 0.9 }}
                        className="fixed bottom-6 right-6 w-96 glass rounded-2xl overflow-hidden z-50"
                        style={{ boxShadow: '0 8px 40px rgba(0, 0, 0, 0.3)' }}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                            <div className="flex items-center gap-3">
                                <Upload size={18} style={{ color: '#7c3aed' }} />
                                <span className="font-medium">Uploads</span>
                                {uploadingCount > 0 && (
                                    <span className="badge badge-accent">{uploadingCount} uploading</span>
                                )}
                                {completedCount > 0 && (
                                    <span className="badge" style={{ background: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' }}>
                                        {completedCount} done
                                    </span>
                                )}
                            </div>
                            <button
                                onClick={() => setShowPanel(false)}
                                className="btn-icon"
                            >
                                <X size={16} />
                            </button>
                        </div>

                        {/* Upload List */}
                        <div className="max-h-80 overflow-y-auto p-3 space-y-2">
                            {uploads.map((upload) => (
                                <motion.div
                                    key={upload.id}
                                    layout
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className="p-3 rounded-xl"
                                    style={{ background: 'rgba(26, 26, 26, 0.5)' }}
                                >
                                    <div className="flex items-start gap-3">
                                        <div
                                            className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                                            style={{
                                                background: upload.status === 'error'
                                                    ? 'rgba(239, 68, 68, 0.2)'
                                                    : upload.status === 'complete'
                                                        ? 'rgba(34, 197, 94, 0.2)'
                                                        : 'rgba(124, 58, 237, 0.2)'
                                            }}
                                        >
                                            {upload.status === 'error' ? (
                                                <AlertCircle size={20} style={{ color: '#f87171' }} />
                                            ) : upload.status === 'complete' ? (
                                                <CheckCircle2 size={20} style={{ color: '#22c55e' }} />
                                            ) : (
                                                <FileUp size={20} style={{ color: '#7c3aed' }} />
                                            )}
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm font-medium truncate">{upload.file.name}</p>
                                            <p className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                {upload.status === 'error'
                                                    ? upload.error
                                                    : upload.status === 'complete'
                                                        ? `${formatFileSize(upload.file.size)} • Complete`
                                                        : upload.status === 'uploading'
                                                            ? `${formatFileSize(upload.file.size)} • ${upload.progress}%`
                                                            : `${formatFileSize(upload.file.size)} • Pending`
                                                }
                                            </p>

                                            {upload.status === 'uploading' && (
                                                <div className="progress-bar mt-2">
                                                    <motion.div
                                                        className="progress-bar-fill"
                                                        initial={{ width: 0 }}
                                                        animate={{ width: `${upload.progress}%` }}
                                                    />
                                                </div>
                                            )}
                                        </div>

                                        {(upload.status === 'complete' || upload.status === 'error') && (
                                            <button
                                                onClick={() => removeUpload(upload.id)}
                                                className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                                                style={{ color: 'rgba(255,255,255,0.4)' }}
                                            >
                                                <X size={14} />
                                            </button>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </div>

                        {/* Footer */}
                        {(completedCount > 0 || errorCount > 0) && (
                            <div className="p-3" style={{ borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                                <button
                                    onClick={clearCompleted}
                                    className="w-full btn-ghost text-sm"
                                >
                                    Clear completed
                                </button>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}

// Export trigger function for use by other components
export function triggerUpload() {
    window.dispatchEvent(new CustomEvent('trigger-upload'));
}

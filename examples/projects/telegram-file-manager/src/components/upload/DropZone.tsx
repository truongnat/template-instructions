/**
 * Upload Drop Zone Component - Updated with CSS Animations
 * @module components/upload/DropZone
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Upload as UploadIcon, X, FileUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { formatFileSize } from '../../lib/telegram/types';

// ============================================================================
// CONSTANTS
// ============================================================================

const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2GB (MTProto limit)

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

    const processFiles = useCallback(async (files: FileList | File[]) => {
        const fileArray = Array.from(files);
        if (fileArray.length === 0) return;

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
        if (files.length > 0) processFiles(files);
    }, [processFiles]);

    const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { files } = e.target;
        if (files && files.length > 0) processFiles(files);
        e.target.value = '';
    }, [processFiles]);

    const clearCompleted = useCallback(() => {
        const remaining = uploads.filter(u => u.status !== 'complete' && u.status !== 'error');
        setUploads(remaining);
        if (remaining.length === 0) setShowPanel(false);
    }, [uploads]);

    const removeUpload = useCallback((id: string) => {
        setUploads(prev => {
            const remaining = prev.filter(u => u.id !== id);
            if (remaining.length === 0) setShowPanel(false);
            return remaining;
        });
    }, []);

    const uploadingCount = uploads.filter(u => u.status === 'uploading').length;
    const completedCount = uploads.filter(u => u.status === 'complete').length;
    const errorCount = uploads.filter(u => u.status === 'error').length;

    return (
        <>
            <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
            />

            {/* Drag Overlay */}
            {isDragging && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center animate-fade-in"
                    style={{ background: 'rgba(124, 58, 237, 0.2)', backdropFilter: 'blur(10px)' }}
                    onDragOver={e => e.preventDefault()}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                >
                    <div className="text-center animate-scale-in">
                        <div className="w-24 h-24 rounded-[2rem] bg-accent-purple/20 flex items-center justify-center mx-auto mb-6 border-2 border-dashed border-accent-purple animate-pulse">
                            <FileUp size={48} className="text-accent-purple" />
                        </div>
                        <h2 className="text-3xl font-black text-white mb-2">Drop it here</h2>
                        <p className="text-white/40 font-bold uppercase tracking-widest text-xs">Ready for Telegram storage</p>
                    </div>
                </div>
            )}

            {/* Background Trigger */}
            <div
                className="fixed inset-0 pointer-events-none z-40"
                onDragEnter={() => setIsDragging(true)}
            />

            {/* Progress Panel */}
            {showPanel && uploads.length > 0 && (
                <div className="fixed bottom-6 right-6 w-96 glass rounded-2xl overflow-hidden z-50 shadow-2xl border border-white/10 animate-slide-up-from-bottom">
                    <div className="p-5 border-b border-white/5 bg-black/5 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-accent-purple/10 flex items-center justify-center">
                                <UploadIcon size={16} className="text-accent-purple" />
                            </div>
                            <div>
                                <h3 className="text-xs font-black uppercase tracking-widest text-white/40">Upload Queue</h3>
                                <div className="flex gap-2 text-[10px] font-bold">
                                    {uploadingCount > 0 && <span className="text-accent-blue">{uploadingCount} Transferring</span>}
                                    {completedCount > 0 && <span className="text-green-500">{completedCount} Finished</span>}
                                    {errorCount > 0 && <span className="text-red-500">{errorCount} Failed</span>}
                                </div>
                            </div>
                        </div>
                        <button onClick={() => setShowPanel(false)} className="btn-icon">
                            <X size={16} />
                        </button>
                    </div>

                    <div className="max-h-96 overflow-y-auto p-4 space-y-3 scroll-container">
                        {uploads.map((upload) => (
                            <div key={upload.id} className="p-4 rounded-2xl bg-white/5 border border-white/5 transition-all group">
                                <div className="flex items-start gap-4">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${upload.status === 'error' ? 'bg-red-500/10 text-red-500' :
                                            upload.status === 'complete' ? 'bg-green-500/10 text-green-500' :
                                                'bg-accent-purple/10 text-accent-purple'
                                        }`}>
                                        {upload.status === 'error' ? <AlertCircle size={20} /> :
                                            upload.status === 'complete' ? <CheckCircle2 size={20} /> :
                                                <FileUp size={20} className="animate-bounce" />}
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center justify-between mb-1">
                                            <p className="text-sm font-bold truncate text-white/90">{upload.file.name}</p>
                                            <button onClick={() => removeUpload(upload.id)} className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-red-400">
                                                <X size={12} />
                                            </button>
                                        </div>

                                        <div className="flex items-center justify-between text-[10px] uppercase font-bold text-white/30 tracking-tight">
                                            <span>{formatFileSize(upload.file.size)}</span>
                                            {upload.status === 'uploading' && <span>{upload.progress}%</span>}
                                        </div>

                                        {upload.status === 'uploading' && (
                                            <div className="h-1 w-full bg-white/5 rounded-full mt-3 overflow-hidden">
                                                <div
                                                    className="h-full bg-accent-purple transition-all duration-300 shadow-[0_0_10px_rgba(124,58,237,0.5)]"
                                                    style={{ width: `${upload.progress}%` }}
                                                />
                                            </div>
                                        )}

                                        {upload.status === 'error' && (
                                            <p className="text-[10px] text-red-400 mt-2 font-bold">{upload.error}</p>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {(completedCount > 0 || errorCount > 0) && (
                        <div className="p-4 bg-black/20 border-t border-white/5 text-center">
                            <button onClick={clearCompleted} className="text-[10px] font-black uppercase tracking-widest text-white/30 hover:text-white transition-colors">
                                Clear Finished Tasks
                            </button>
                        </div>
                    )}
                </div>
            )}
        </>
    );
}

export function triggerUpload() {
    window.dispatchEvent(new CustomEvent('trigger-upload'));
}

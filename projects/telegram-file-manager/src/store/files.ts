/**
 * File Store - Zustand State Management
 * @module store/files
 * 
 * Supports both Bot API and GramJS (MTProto) for file operations.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { TelegramFile, VirtualFolder, ViewMode, SortBy, SortOrder, FileType } from '../lib/telegram/types';
import { fileMetadata, folderMetadata } from '../lib/telegram/metadata';
import { telegramClient } from '../lib/telegram/client';
import { gramjsClient } from '../lib/telegram/gramjs-client';

// ============================================================================
// TYPES
// ============================================================================

interface FileState {
    // Data
    files: TelegramFile[];
    folders: VirtualFolder[];
    selectedFiles: string[];
    currentFolder: string | null;

    // View settings
    viewMode: ViewMode;
    sortBy: SortBy;
    sortOrder: SortOrder;
    filterType: FileType;
    searchQuery: string;

    // UI State
    isLoading: boolean;
    error: string | null;

    // Actions
    loadFiles: () => Promise<void>;
    loadFolders: () => Promise<void>;
    uploadFile: (file: File, onProgress?: (progress: number) => void) => Promise<TelegramFile>;
    deleteFiles: (fileIds: string[]) => Promise<void>;
    downloadFile: (file: TelegramFile) => Promise<void>;

    // Selection
    selectFile: (fileId: string, multiSelect?: boolean) => void;
    selectAll: () => void;
    clearSelection: () => void;

    // Folder operations
    createFolder: (name: string) => Promise<VirtualFolder>;
    navigateToFolder: (folderId: string | null) => void;
    moveFilesToFolder: (fileIds: string[], folderId: string) => Promise<void>;

    // View settings
    setViewMode: (mode: ViewMode) => void;
    setSortBy: (sortBy: SortBy) => void;
    setSortOrder: (order: SortOrder) => void;
    setFilterType: (type: FileType) => void;
    setSearchQuery: (query: string) => void;

    // Favorites & Trash
    toggleFavorite: (fileId: string) => Promise<void>;
    moveToTrash: (fileIds: string[]) => Promise<void>;
    restoreFromTrash: (fileIds: string[]) => Promise<void>;
    emptyTrash: () => Promise<void>;

    // Utilities
    getFilteredFiles: () => TelegramFile[];
    clearError: () => void;
}

// ============================================================================
// STORE
// ============================================================================

export const useFileStore = create<FileState>()(
    persist(
        (set, get) => ({
            // Initial State
            files: [],
            folders: [],
            selectedFiles: [],
            currentFolder: null,
            viewMode: 'grid',
            sortBy: 'date',
            sortOrder: 'desc',
            filterType: 'all',
            searchQuery: '',
            isLoading: false,
            error: null,

            // Load files from local database
            loadFiles: async () => {
                set({ isLoading: true, error: null });
                try {
                    const files = await fileMetadata.getAll({ isDeleted: false });
                    set({ files, isLoading: false });
                } catch (error) {
                    set({
                        error: error instanceof Error ? error.message : 'Failed to load files',
                        isLoading: false
                    });
                }
            },

            // Load folders from local database
            loadFolders: async () => {
                try {
                    const folders = await folderMetadata.getAll();
                    set({ folders });
                } catch (error) {
                    console.error('Failed to load folders:', error);
                }
            },

            // Upload a file
            uploadFile: async (file, onProgress) => {
                const { currentFolder, folders } = get();

                // Preferred: GramJS (MTProto)
                if (gramjsClient.connected) {
                    set({ error: null });
                    try {
                        const result = await gramjsClient.uploadFile(file, (progress) => {
                            onProgress?.(progress);
                        });

                        if (currentFolder) {
                            const folder = folders.find(f => f.id === currentFolder);
                            if (folder) result.folder_path = folder.path;
                        }

                        await fileMetadata.upsert(result);
                        set(s => ({ files: [result, ...s.files] }));
                        return result;
                    } catch (error) {
                        const msg = error instanceof Error ? error.message : 'Upload failed';
                        set({ error: msg });
                        throw error;
                    }
                }

                // Legacy: Bot API
                if (telegramClient.connected) {
                    set({ error: null });
                    try {
                        const result = await telegramClient.uploadFile(file, (progress) => {
                            onProgress?.(progress.progress);
                        });

                        if (currentFolder) {
                            const folder = folders.find(f => f.id === currentFolder);
                            if (folder) result.folder_path = folder.path;
                        }

                        await fileMetadata.upsert(result);
                        set(s => ({ files: [result, ...s.files] }));
                        return result;
                    } catch (error) {
                        const msg = error instanceof Error ? error.message : 'Upload failed';
                        set({ error: msg });
                        throw error;
                    }
                }

                throw new Error('No Telegram connection available. Please connect first.');
            },

            // Delete files
            deleteFiles: async (fileIds) => {
                set({ isLoading: true, error: null });
                try {
                    const { files } = get();

                    for (const fileId of fileIds) {
                        const file = files.find(f => f.file_unique_id === fileId);
                        if (file) {
                            // Try deleting from Telegram if possible
                            if (telegramClient.connected) {
                                try { await telegramClient.deleteFile(file.message_id); } catch (e) { /* Ignore */ }
                            }
                            await fileMetadata.permanentDelete(fileId);
                        }
                    }

                    set(state => ({
                        files: state.files.filter(f => !fileIds.includes(f.file_unique_id)),
                        selectedFiles: [],
                        isLoading: false,
                    }));
                } catch (error) {
                    set({
                        error: error instanceof Error ? error.message : 'Delete failed',
                        isLoading: false
                    });
                    throw error;
                }
            },

            // Download a file
            downloadFile: async (file) => {
                try {
                    set({ isLoading: true });
                    const blob = await telegramClient.downloadFile(file.file_id);
                    set({ isLoading: false });

                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = file.file_name;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } catch (error) {
                    set({
                        error: error instanceof Error ? error.message : 'Download failed',
                        isLoading: false
                    });
                    throw error;
                }
            },

            // Selection
            selectFile: (fileId, multiSelect = false) => {
                set(state => {
                    if (multiSelect) {
                        const isSelected = state.selectedFiles.includes(fileId);
                        return {
                            selectedFiles: isSelected
                                ? state.selectedFiles.filter(id => id !== fileId)
                                : [...state.selectedFiles, fileId],
                        };
                    }
                    return { selectedFiles: [fileId] };
                });
            },

            selectAll: () => {
                const filtered = get().getFilteredFiles();
                set({ selectedFiles: filtered.map(f => f.file_unique_id) });
            },

            clearSelection: () => {
                set({ selectedFiles: [] });
            },

            // Folder operations
            createFolder: async (name) => {
                const { currentFolder } = get();
                const folder = await folderMetadata.create(name, currentFolder);
                set(state => ({ folders: [...state.folders, folder] }));
                return folder;
            },

            navigateToFolder: (folderId) => {
                set({ currentFolder: folderId, selectedFiles: [] });
            },

            moveFilesToFolder: async (fileIds, folderId) => {
                const { folders } = get();
                const folder = folders.find(f => f.id === folderId);
                const folderPath = folder?.path || '/';

                for (const fileId of fileIds) {
                    await fileMetadata.moveToFolder(fileId, folderPath);
                }

                set(state => ({
                    files: state.files.map(f =>
                        fileIds.includes(f.file_unique_id)
                            ? { ...f, folder_path: folderPath }
                            : f
                    ),
                    selectedFiles: [],
                }));
            },

            // View settings
            setViewMode: (mode) => set({ viewMode: mode }),
            setSortBy: (sortBy) => set({ sortBy }),
            setSortOrder: (order) => set({ sortOrder: order }),
            setFilterType: (type) => set({ filterType: type, currentFolder: null }),
            setSearchQuery: (query) => set({ searchQuery: query }),

            // Favorites & Trash
            toggleFavorite: async (fileId) => {
                const newStatus = await fileMetadata.toggleFavorite(fileId);
                set(state => ({
                    files: state.files.map(f =>
                        f.file_unique_id === fileId ? { ...f, is_favorite: newStatus } : f
                    ),
                }));
            },

            moveToTrash: async (fileIds) => {
                for (const fileId of fileIds) {
                    await fileMetadata.moveToTrash(fileId);
                }
                set(state => ({
                    files: state.files.map(f =>
                        fileIds.includes(f.file_unique_id)
                            ? { ...f, is_deleted: true, deleted_at: new Date() }
                            : f
                    ),
                    selectedFiles: [],
                }));
            },

            restoreFromTrash: async (fileIds) => {
                for (const fileId of fileIds) {
                    await fileMetadata.restoreFromTrash(fileId);
                }
                set(state => ({
                    files: state.files.map(f =>
                        fileIds.includes(f.file_unique_id)
                            ? { ...f, is_deleted: false, deleted_at: undefined }
                            : f
                    ),
                }));
            },

            emptyTrash: async () => {
                const { files } = get();
                const trashedFiles = files.filter(f => f.is_deleted);

                for (const file of trashedFiles) {
                    if (telegramClient.connected) {
                        try { await telegramClient.deleteFile(file.message_id); } catch { /* Ignore */ }
                    }
                }

                await fileMetadata.emptyTrash();
                set(state => ({
                    files: state.files.filter(f => !f.is_deleted),
                }));
            },

            // Get filtered and sorted files
            getFilteredFiles: () => {
                const { files, currentFolder, folders, filterType, searchQuery, sortBy, sortOrder } = get();

                const currentFolderPath = currentFolder
                    ? folders.find(f => f.id === currentFolder)?.path
                    : undefined;

                let filtered = files.filter(file => {
                    if (file.is_deleted) return false;
                    if (currentFolderPath && file.folder_path !== currentFolderPath) return false;

                    if (filterType !== 'all') {
                        const isImage = file.mime_type.startsWith('image/');
                        const isVideo = file.mime_type.startsWith('video/');
                        const isAudio = file.mime_type.startsWith('audio/');
                        const isDocument = file.mime_type.includes('pdf') ||
                            file.mime_type.includes('document') ||
                            file.mime_type.includes('text');

                        switch (filterType) {
                            case 'images': if (!isImage) return false; break;
                            case 'videos': if (!isVideo) return false; break;
                            case 'audio': if (!isAudio) return false; break;
                            case 'documents': if (!isDocument) return false; break;
                        }
                    }

                    if (searchQuery && !file.file_name.toLowerCase().includes(searchQuery.toLowerCase())) {
                        return false;
                    }

                    return true;
                });

                filtered.sort((a, b) => {
                    let comparison = 0;
                    switch (sortBy) {
                        case 'name': comparison = a.file_name.localeCompare(b.file_name); break;
                        case 'date': comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime(); break;
                        case 'size': comparison = a.file_size - b.file_size; break;
                        case 'type': comparison = a.mime_type.localeCompare(b.mime_type); break;
                    }
                    return sortOrder === 'asc' ? comparison : -comparison;
                });

                return filtered;
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: 'file-manager-store',
            partialize: (state) => ({
                viewMode: state.viewMode,
                sortBy: state.sortBy,
                sortOrder: state.sortOrder,
            }),
        }
    )
);

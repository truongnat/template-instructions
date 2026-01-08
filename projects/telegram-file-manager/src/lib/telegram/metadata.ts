/**
 * Local Metadata Storage using IndexedDB (Dexie.js)
 * @module lib/telegram/metadata
 * 
 * Stores file metadata and virtual folder structure locally for fast access.
 */

import Dexie, { type Table } from 'dexie';
import type { TelegramFile, VirtualFolder, TelegramSettings } from './types';

// ============================================================================
// DATABASE SCHEMA
// ============================================================================

interface FileBlob {
    file_unique_id: string;
    blob: Blob;
    created_at: Date;
}

class FileManagerDatabase extends Dexie {
    files!: Table<TelegramFile, string>;
    folders!: Table<VirtualFolder, string>;
    settings!: Table<{ key: string; value: unknown }, string>;
    blobs!: Table<FileBlob, string>;

    constructor() {
        super('TelegramFileManager');

        this.version(1).stores({
            files: 'file_unique_id, file_name, mime_type, created_at, folder_path, is_favorite, is_deleted',
            folders: 'id, name, parent_id, path',
            settings: 'key',
        });

        // Version 2: Add blobs table for demo mode file storage
        this.version(2).stores({
            files: 'file_unique_id, file_name, mime_type, created_at, folder_path, is_favorite, is_deleted',
            folders: 'id, name, parent_id, path',
            settings: 'key',
            blobs: 'file_unique_id, created_at',
        });
    }
}

const db = new FileManagerDatabase();

// ============================================================================
// FILE OPERATIONS
// ============================================================================

export const fileMetadata = {
    /**
     * Add or update a file in the local database
     */
    async upsert(file: TelegramFile): Promise<void> {
        await db.files.put(file);
    },

    /**
     * Add multiple files at once
     */
    async bulkUpsert(files: TelegramFile[]): Promise<void> {
        await db.files.bulkPut(files);
    },

    /**
     * Get a file by its unique ID
     */
    async get(fileUniqueId: string): Promise<TelegramFile | undefined> {
        return db.files.get(fileUniqueId);
    },

    /**
     * Get all files (optionally filtered)
     */
    async getAll(options?: {
        folderPath?: string;
        mimeType?: string;
        isDeleted?: boolean;
        isFavorite?: boolean;
    }): Promise<TelegramFile[]> {
        // Get all files first, then filter in memory
        // IndexedDB stores booleans, not integers
        const allFiles = await db.files.toArray();

        return allFiles.filter(file => {
            // Filter by deleted status (handle both undefined and boolean cases)
            if (options?.isDeleted !== undefined) {
                const fileIsDeleted = file.is_deleted === true;
                if (fileIsDeleted !== options.isDeleted) return false;
            } else {
                // Default: exclude deleted files
                if (file.is_deleted === true) return false;
            }

            if (options?.folderPath && file.folder_path !== options.folderPath) return false;
            if (options?.mimeType && !file.mime_type.startsWith(options.mimeType)) return false;
            if (options?.isFavorite && !file.is_favorite) return false;
            return true;
        });
    },

    /**
     * Get files in a specific folder
     */
    async getByFolder(folderPath: string): Promise<TelegramFile[]> {
        return db.files.where('folder_path').equals(folderPath).toArray();
    },

    /**
     * Get favorite files
     */
    async getFavorites(): Promise<TelegramFile[]> {
        const allFiles = await db.files.toArray();
        return allFiles.filter(f => f.is_favorite === true && f.is_deleted !== true);
    },

    /**
     * Get deleted files (trash)
     */
    async getTrash(): Promise<TelegramFile[]> {
        const allFiles = await db.files.toArray();
        return allFiles.filter(f => f.is_deleted === true);
    },

    /**
     * Search files by name
     */
    async search(query: string): Promise<TelegramFile[]> {
        const lowerQuery = query.toLowerCase();
        return db.files
            .filter(file =>
                file.file_name.toLowerCase().includes(lowerQuery) &&
                !file.is_deleted
            )
            .toArray();
    },

    /**
     * Move file to folder
     */
    async moveToFolder(fileUniqueId: string, folderPath: string): Promise<void> {
        await db.files.update(fileUniqueId, { folder_path: folderPath });
    },

    /**
     * Toggle favorite status
     */
    async toggleFavorite(fileUniqueId: string): Promise<boolean> {
        const file = await db.files.get(fileUniqueId);
        if (!file) return false;

        const newStatus = !file.is_favorite;
        await db.files.update(fileUniqueId, { is_favorite: newStatus });
        return newStatus;
    },

    /**
     * Move file to trash
     */
    async moveToTrash(fileUniqueId: string): Promise<void> {
        await db.files.update(fileUniqueId, {
            is_deleted: true,
            deleted_at: new Date(),
        });
    },

    /**
     * Restore file from trash
     */
    async restoreFromTrash(fileUniqueId: string): Promise<void> {
        await db.files.update(fileUniqueId, {
            is_deleted: false,
            deleted_at: undefined,
        });
    },

    /**
     * Permanently delete file from local database
     */
    async permanentDelete(fileUniqueId: string): Promise<void> {
        await db.files.delete(fileUniqueId);
    },

    /**
     * Empty trash (delete all trashed files)
     */
    async emptyTrash(): Promise<number> {
        const trashed = await this.getTrash();
        await db.files.bulkDelete(trashed.map(f => f.file_unique_id));
        return trashed.length;
    },

    /**
     * Get file count by type
     */
    async getStats(): Promise<{
        total: number;
        images: number;
        videos: number;
        documents: number;
        other: number;
        totalSize: number;
    }> {
        const files = (await db.files.toArray()).filter(f => f.is_deleted !== true);

        return {
            total: files.length,
            images: files.filter(f => f.mime_type.startsWith('image/')).length,
            videos: files.filter(f => f.mime_type.startsWith('video/')).length,
            documents: files.filter(f =>
                f.mime_type.includes('pdf') ||
                f.mime_type.includes('document') ||
                f.mime_type.includes('text')
            ).length,
            other: files.filter(f =>
                !f.mime_type.startsWith('image/') &&
                !f.mime_type.startsWith('video/') &&
                !f.mime_type.includes('pdf') &&
                !f.mime_type.includes('document')
            ).length,
            totalSize: files.reduce((sum, f) => sum + f.file_size, 0),
        };
    },

    /**
     * Save file blob for demo mode preview
     */
    async saveBlob(fileUniqueId: string, blob: Blob): Promise<void> {
        await db.blobs.put({
            file_unique_id: fileUniqueId,
            blob,
            created_at: new Date(),
        });
    },

    /**
     * Get file blob for preview
     */
    async getBlob(fileUniqueId: string): Promise<Blob | undefined> {
        const record = await db.blobs.get(fileUniqueId);
        return record?.blob;
    },

    /**
     * Delete file blob
     */
    async deleteBlob(fileUniqueId: string): Promise<void> {
        await db.blobs.delete(fileUniqueId);
    },
};

// ============================================================================
// FOLDER OPERATIONS
// ============================================================================

export const folderMetadata = {
    /**
     * Create a new folder
     */
    async create(name: string, parentId: string | null = null): Promise<VirtualFolder> {
        const parent = parentId ? await db.folders.get(parentId) : null;
        const path = parent ? `${parent.path}/${name}` : `/${name}`;

        const folder: VirtualFolder = {
            id: crypto.randomUUID(),
            name,
            parent_id: parentId,
            path,
            created_at: new Date(),
            updated_at: new Date(),
        };

        await db.folders.add(folder);
        return folder;
    },

    /**
     * Get all folders
     */
    async getAll(): Promise<VirtualFolder[]> {
        return db.folders.toArray();
    },

    /**
     * Get folder by ID
     */
    async get(id: string): Promise<VirtualFolder | undefined> {
        return db.folders.get(id);
    },

    /**
     * Get child folders
     */
    async getChildren(parentId: string | null): Promise<VirtualFolder[]> {
        if (parentId === null) {
            return db.folders.where('parent_id').equals('').toArray();
        }
        return db.folders.where('parent_id').equals(parentId).toArray();
    },

    /**
     * Rename a folder
     */
    async rename(id: string, newName: string): Promise<void> {
        const folder = await db.folders.get(id);
        if (!folder) return;

        const pathParts = folder.path.split('/');
        pathParts[pathParts.length - 1] = newName;
        const newPath = pathParts.join('/');

        await db.folders.update(id, {
            name: newName,
            path: newPath,
            updated_at: new Date(),
        });

        // Update all files in this folder
        const files = await db.files.where('folder_path').equals(folder.path).toArray();
        for (const file of files) {
            await db.files.update(file.file_unique_id, { folder_path: newPath });
        }
    },

    /**
     * Delete a folder (and move files to parent)
     */
    async delete(id: string): Promise<void> {
        const folder = await db.folders.get(id);
        if (!folder) return;

        // Move files to parent folder
        const files = await db.files.where('folder_path').equals(folder.path).toArray();
        const parentPath = folder.parent_id
            ? (await db.folders.get(folder.parent_id))?.path || '/'
            : '/';

        for (const file of files) {
            await db.files.update(file.file_unique_id, { folder_path: parentPath });
        }

        // Delete child folders recursively
        const children = await this.getChildren(id);
        for (const child of children) {
            await this.delete(child.id);
        }

        await db.folders.delete(id);
    },
};

// ============================================================================
// SETTINGS OPERATIONS
// ============================================================================

export const settingsMetadata = {
    /**
     * Get a setting value
     */
    async get<T>(key: string, defaultValue?: T): Promise<T | undefined> {
        const result = await db.settings.get(key);
        return (result?.value as T) ?? defaultValue;
    },

    /**
     * Set a setting value
     */
    async set<T>(key: string, value: T): Promise<void> {
        await db.settings.put({ key, value });
    },

    /**
     * Get Telegram settings
     */
    async getTelegramSettings(): Promise<TelegramSettings | undefined> {
        return this.get<TelegramSettings>('telegram');
    },

    /**
     * Save Telegram settings
     */
    async saveTelegramSettings(settings: TelegramSettings): Promise<void> {
        await this.set('telegram', settings);
    },

    /**
     * Clear all settings
     */
    async clear(): Promise<void> {
        await db.settings.clear();
    },
};

// ============================================================================
// DATABASE UTILITIES
// ============================================================================

export const database = {
    /**
     * Clear all data
     */
    async clearAll(): Promise<void> {
        await db.files.clear();
        await db.folders.clear();
        await db.settings.clear();
    },

    /**
     * Export all data as JSON
     */
    async export(): Promise<string> {
        const data = {
            files: await db.files.toArray(),
            folders: await db.folders.toArray(),
            settings: await db.settings.toArray(),
        };
        return JSON.stringify(data, null, 2);
    },

    /**
     * Import data from JSON
     */
    async import(jsonData: string): Promise<void> {
        const data = JSON.parse(jsonData);
        if (data.files) await db.files.bulkPut(data.files);
        if (data.folders) await db.folders.bulkPut(data.folders);
        if (data.settings) await db.settings.bulkPut(data.settings);
    },
};

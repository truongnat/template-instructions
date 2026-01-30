/**
 * Telegram File Manager - Type Definitions
 * @module lib/telegram/types
 */

// ============================================================================
// FILE TYPES
// ============================================================================

export interface TelegramFile {
    /** Unique identifier for this file (from Telegram) */
    file_id: string;
    /** Unique identifier for this file (persists across bot restarts) */
    file_unique_id: string;
    /** File size in bytes */
    file_size: number;
    /** Original filename */
    file_name: string;
    /** MIME type of the file */
    mime_type: string;
    /** When the file was uploaded */
    created_at: Date;
    /** Message ID in the storage channel */
    message_id: number;
    /** Thumbnail file ID (for images/videos) */
    thumbnail_id?: string;
    /** Virtual folder path */
    folder_path?: string;
    /** User-defined tags */
    tags?: string[];
    /** Is this file favorited */
    is_favorite?: boolean;
    /** Is this file in trash */
    is_deleted?: boolean;
    /** Deletion timestamp (for trash) */
    deleted_at?: Date;
}

export interface TelegramPhoto {
    file_id: string;
    file_unique_id: string;
    width: number;
    height: number;
    file_size?: number;
}

export interface TelegramVideo {
    file_id: string;
    file_unique_id: string;
    width: number;
    height: number;
    duration: number;
    thumbnail?: TelegramPhoto;
    file_name?: string;
    mime_type?: string;
    file_size?: number;
}

export interface TelegramDocument {
    file_id: string;
    file_unique_id: string;
    thumbnail?: TelegramPhoto;
    file_name?: string;
    mime_type?: string;
    file_size?: number;
}

// ============================================================================
// UPLOAD TYPES
// ============================================================================

export type UploadStatus = 'pending' | 'uploading' | 'processing' | 'complete' | 'error' | 'cancelled';

export interface FileUploadProgress {
    /** Unique ID for this upload */
    id: string;
    /** Original file */
    file: File;
    /** Current status */
    status: UploadStatus;
    /** Upload progress 0-100 */
    progress: number;
    /** Error message if failed */
    error?: string;
    /** Resulting Telegram file if complete */
    result?: TelegramFile;
    /** Start time */
    started_at: Date;
    /** Completion time */
    completed_at?: Date;
    /** If this is a chunked upload */
    is_chunked?: boolean;
    /** Current chunk being uploaded */
    current_chunk?: number;
    /** Total chunks */
    total_chunks?: number;
}

export interface ChunkInfo {
    /** Chunk index */
    index: number;
    /** Total chunks */
    total: number;
    /** Original file name */
    original_name: string;
    /** Original file size */
    original_size: number;
    /** This chunk's size */
    chunk_size: number;
    /** Checksum for verification */
    checksum: string;
}

// ============================================================================
// VIRTUAL FOLDER TYPES
// ============================================================================

export interface VirtualFolder {
    /** Unique folder ID */
    id: string;
    /** Folder name */
    name: string;
    /** Parent folder ID (null for root) */
    parent_id: string | null;
    /** Full path (e.g., "/Documents/Work") */
    path: string;
    /** Folder color (for UI) */
    color?: string;
    /** Folder icon */
    icon?: string;
    /** Creation date */
    created_at: Date;
    /** Last modified date */
    updated_at: Date;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface TelegramApiResponse<T> {
    ok: boolean;
    result?: T;
    error_code?: number;
    description?: string;
}

export interface TelegramMessage {
    message_id: number;
    date: number;
    chat: {
        id: number;
        type: string;
    };
    document?: TelegramDocument;
    photo?: TelegramPhoto[];
    video?: TelegramVideo;
}

export interface TelegramFileInfo {
    file_id: string;
    file_unique_id: string;
    file_size?: number;
    file_path?: string;
}

// ============================================================================
// SETTINGS TYPES
// ============================================================================

export interface TelegramSettings {
    /** Bot token */
    bot_token: string;
    /** Storage channel ID */
    channel_id: string;
    /** Is connected and verified */
    is_connected: boolean;
    /** Last verification timestamp */
    last_verified?: Date;
    /** Bot username */
    bot_username?: string;
}

// ============================================================================
// VIEW TYPES
// ============================================================================

export type ViewMode = 'grid' | 'list';
export type SortBy = 'name' | 'date' | 'size' | 'type';
export type SortOrder = 'asc' | 'desc';

export type FileType = 'all' | 'images' | 'videos' | 'documents' | 'audio' | 'archives';

export interface ViewSettings {
    mode: ViewMode;
    sortBy: SortBy;
    sortOrder: SortOrder;
    fileType: FileType;
    showHidden: boolean;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

export function getFileType(mimeType: string): FileType {
    if (mimeType.startsWith('image/')) return 'images';
    if (mimeType.startsWith('video/')) return 'videos';
    if (mimeType.startsWith('audio/')) return 'audio';
    if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text')) return 'documents';
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar') || mimeType.includes('7z')) return 'archives';
    return 'all';
}

export function getFileExtension(fileName: string): string {
    const parts = fileName.split('.');
    return parts.length > 1 ? parts.pop()?.toLowerCase() || '' : '';
}

export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

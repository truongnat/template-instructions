/**
 * Telegram Bot API Client
 * @module lib/telegram/client
 * 
 * Handles all communication with Telegram Bot API for file storage operations.
 */

import type {
    TelegramApiResponse,
    TelegramMessage,
    TelegramFileInfo,
    TelegramFile,
    TelegramSettings,
    FileUploadProgress,
} from './types';

// ============================================================================
// CONSTANTS
// ============================================================================

const TELEGRAM_API_BASE = 'https://api.telegram.org';
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const CHUNK_SIZE = 45 * 1024 * 1024; // 45MB per chunk

// ============================================================================
// TELEGRAM CLIENT CLASS
// ============================================================================

export class TelegramClient {
    private botToken: string = '';
    private channelId: string = '';
    private isConnected: boolean = false;

    // --------------------------------------------------------------------------
    // INITIALIZATION
    // --------------------------------------------------------------------------

    /**
     * Initialize the client with bot token and channel ID
     */
    async connect(settings: TelegramSettings): Promise<boolean> {
        this.botToken = settings.bot_token;
        this.channelId = settings.channel_id;

        // Verify connection by getting bot info
        try {
            const response = await this.apiCall<{ username: string }>('getMe');
            if (response.ok && response.result) {
                this.isConnected = true;
                return true;
            }
            throw new Error(response.description || 'Failed to connect');
        } catch (error) {
            this.isConnected = false;
            throw error;
        }
    }

    /**
     * Check if currently connected
     */
    get connected(): boolean {
        return this.isConnected;
    }

    /**
     * Disconnect and clear credentials
     */
    disconnect(): void {
        this.botToken = '';
        this.channelId = '';
        this.isConnected = false;
    }

    // --------------------------------------------------------------------------
    // FILE OPERATIONS
    // --------------------------------------------------------------------------

    /**
     * Upload a file to the storage channel
     */
    async uploadFile(
        file: File,
        onProgress?: (progress: FileUploadProgress) => void
    ): Promise<TelegramFile> {
        this.ensureConnected();

        const progressState: FileUploadProgress = {
            id: crypto.randomUUID(),
            file,
            status: 'uploading',
            progress: 0,
            started_at: new Date(),
        };

        onProgress?.(progressState);

        // Check if chunking is needed
        if (file.size > MAX_FILE_SIZE) {
            return this.uploadChunked(file, progressState, onProgress);
        }

        try {
            const formData = new FormData();
            formData.append('chat_id', this.channelId);
            formData.append('document', file);
            formData.append('caption', JSON.stringify({
                name: file.name,
                size: file.size,
                type: file.type,
                uploaded: new Date().toISOString(),
            }));

            const response = await this.apiCall<TelegramMessage>('sendDocument', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok || !response.result) {
                throw new Error(response.description || 'Upload failed');
            }

            const message = response.result;
            const doc = message.document;

            if (!doc) {
                throw new Error('No document in response');
            }

            const telegramFile: TelegramFile = {
                file_id: doc.file_id,
                file_unique_id: doc.file_unique_id,
                file_size: doc.file_size || file.size,
                file_name: file.name,
                mime_type: file.type,
                created_at: new Date(),
                message_id: message.message_id,
                thumbnail_id: doc.thumbnail?.file_id,
            };

            progressState.status = 'complete';
            progressState.progress = 100;
            progressState.result = telegramFile;
            progressState.completed_at = new Date();
            onProgress?.(progressState);

            return telegramFile;
        } catch (error) {
            progressState.status = 'error';
            progressState.error = error instanceof Error ? error.message : 'Unknown error';
            onProgress?.(progressState);
            throw error;
        }
    }

    /**
     * Upload a file in chunks (for files > 50MB)
     */
    private async uploadChunked(
        file: File,
        progressState: FileUploadProgress,
        onProgress?: (progress: FileUploadProgress) => void
    ): Promise<TelegramFile> {
        const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
        progressState.is_chunked = true;
        progressState.total_chunks = totalChunks;

        const chunkFiles: TelegramFile[] = [];

        for (let i = 0; i < totalChunks; i++) {
            progressState.current_chunk = i + 1;
            progressState.progress = Math.round((i / totalChunks) * 100);
            onProgress?.(progressState);

            const start = i * CHUNK_SIZE;
            const end = Math.min(start + CHUNK_SIZE, file.size);
            const chunk = file.slice(start, end);
            const chunkName = `${file.name}.part${i + 1}of${totalChunks}`;

            const chunkFile = new File([chunk], chunkName, { type: 'application/octet-stream' });

            const formData = new FormData();
            formData.append('chat_id', this.channelId);
            formData.append('document', chunkFile);
            formData.append('caption', JSON.stringify({
                chunk: i + 1,
                total: totalChunks,
                original_name: file.name,
                original_size: file.size,
                original_type: file.type,
            }));

            const response = await this.apiCall<TelegramMessage>('sendDocument', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok || !response.result?.document) {
                throw new Error(`Failed to upload chunk ${i + 1}`);
            }

            const doc = response.result.document;
            chunkFiles.push({
                file_id: doc.file_id,
                file_unique_id: doc.file_unique_id,
                file_size: doc.file_size || chunk.size,
                file_name: chunkName,
                mime_type: 'application/octet-stream',
                created_at: new Date(),
                message_id: response.result.message_id,
            });
        }

        // Create a manifest file that references all chunks
        const manifest = {
            type: 'chunked_file',
            original_name: file.name,
            original_size: file.size,
            original_type: file.type,
            chunks: chunkFiles.map(c => ({
                file_id: c.file_id,
                message_id: c.message_id,
            })),
        };

        const manifestBlob = new Blob([JSON.stringify(manifest)], { type: 'application/json' });
        const manifestFile = new File([manifestBlob], `${file.name}.manifest.json`);

        const formData = new FormData();
        formData.append('chat_id', this.channelId);
        formData.append('document', manifestFile);

        const manifestResponse = await this.apiCall<TelegramMessage>('sendDocument', {
            method: 'POST',
            body: formData,
        });

        if (!manifestResponse.ok || !manifestResponse.result?.document) {
            throw new Error('Failed to upload manifest');
        }

        const manifestDoc = manifestResponse.result.document;
        const result: TelegramFile = {
            file_id: manifestDoc.file_id,
            file_unique_id: manifestDoc.file_unique_id,
            file_size: file.size,
            file_name: file.name,
            mime_type: file.type,
            created_at: new Date(),
            message_id: manifestResponse.result.message_id,
        };

        progressState.status = 'complete';
        progressState.progress = 100;
        progressState.result = result;
        progressState.completed_at = new Date();
        onProgress?.(progressState);

        return result;
    }

    /**
     * Download a file by its file_id
     */
    async downloadFile(fileId: string): Promise<Blob> {
        this.ensureConnected();

        // Get file path from Telegram
        const fileInfo = await this.apiCall<TelegramFileInfo>('getFile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_id: fileId }),
        });

        if (!fileInfo.ok || !fileInfo.result?.file_path) {
            throw new Error(fileInfo.description || 'Failed to get file info');
        }

        // Download the file
        const downloadUrl = `${TELEGRAM_API_BASE}/file/bot${this.botToken}/${fileInfo.result.file_path}`;
        const response = await fetch(downloadUrl);

        if (!response.ok) {
            throw new Error(`Download failed: ${response.statusText}`);
        }

        return response.blob();
    }

    /**
     * Delete a file (actually deletes the message from channel)
     */
    async deleteFile(messageId: number): Promise<boolean> {
        this.ensureConnected();

        const response = await this.apiCall<boolean>('deleteMessage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: this.channelId,
                message_id: messageId,
            }),
        });

        if (!response.ok) {
            throw new Error(response.description || 'Failed to delete file');
        }

        return true;
    }

    /**
     * Get bot information
     */
    async getBotInfo(): Promise<{ id: number; username: string; first_name: string }> {
        const response = await this.apiCall<{ id: number; username: string; first_name: string }>('getMe');
        if (!response.ok || !response.result) {
            throw new Error(response.description || 'Failed to get bot info');
        }
        return response.result;
    }

    // --------------------------------------------------------------------------
    // INTERNAL HELPERS
    // --------------------------------------------------------------------------

    private ensureConnected(): void {
        if (!this.isConnected) {
            throw new Error('Not connected. Call connect() first.');
        }
    }

    private async apiCall<T>(
        method: string,
        options?: RequestInit
    ): Promise<TelegramApiResponse<T>> {
        const url = `${TELEGRAM_API_BASE}/bot${this.botToken}/${method}`;

        try {
            const response = await fetch(url, options);
            return response.json();
        } catch (error) {
            return {
                ok: false,
                description: error instanceof Error ? error.message : 'Network error',
            };
        }
    }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

export const telegramClient = new TelegramClient();

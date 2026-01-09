/**
 * GramJS MTProto Client
 * @module lib/telegram/gramjs-client
 * 
 * User-based Telegram authentication using MTProto protocol.
 * Allows login with phone number + OTP, no bot required.
 */

import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions";
import { Api } from "telegram/tl";
import { CustomFile } from "telegram/client/uploads";
import type { TelegramFile } from "./types";

// ============================================================================
// CONSTANTS
// ============================================================================

// Users must provide their own API credentials
// Get yours at https://my.telegram.org/apps

// ============================================================================
// TYPES
// ============================================================================

export interface GramJSConfig {
    apiId?: number;
    apiHash?: string;
}

export interface LoginCallbacks {
    onPhoneNumber: () => Promise<string>;
    onPhoneCode: () => Promise<string>;
    onPassword: () => Promise<string>;
    onError: (error: Error) => void;
}

export interface ChatInfo {
    id: string;
    title: string;
    type: 'user' | 'chat' | 'channel' | 'saved';
    unreadCount?: number;
    photo?: string;
}

export interface UserInfo {
    id: string;
    firstName: string;
    lastName?: string;
    username?: string;
    phone?: string;
}

// ============================================================================
// GRAMJS CLIENT CLASS  
// ============================================================================

class GramJSClient {
    private client: TelegramClient | null = null;
    private apiId: number | null = null;
    private apiHash: string | null = null;
    private _isConnected: boolean = false;
    private _currentUser: UserInfo | null = null;
    private _storageChat: ChatInfo | null = null;
    private _resolvedEntities: Map<string, Api.TypeInputPeer> = new Map();

    constructor(config?: GramJSConfig) {
        if (config?.apiId && config?.apiHash) {
            this.apiId = config.apiId;
            this.apiHash = config.apiHash;
        }
    }

    // --------------------------------------------------------------------------
    // CREDENTIALS
    // --------------------------------------------------------------------------

    /**
     * Set API credentials (required before login)
     */
    setCredentials(apiId: number, apiHash: string): void {
        this.apiId = apiId;
        this.apiHash = apiHash;
    }

    /**
     * Check if credentials are set
     */
    get hasCredentials(): boolean {
        return this.apiId !== null && this.apiHash !== null;
    }

    /**
     * Get current credentials
     */
    getCredentials(): { apiId: number; apiHash: string } | null {
        if (this.apiId && this.apiHash) {
            return { apiId: this.apiId, apiHash: this.apiHash };
        }
        return null;
    }

    // --------------------------------------------------------------------------
    // GETTERS
    // --------------------------------------------------------------------------

    get connected(): boolean {
        return this._isConnected && this.client !== null;
    }

    get currentUser(): UserInfo | null {
        return this._currentUser;
    }

    get storageChat(): ChatInfo | null {
        return this._storageChat;
    }

    // --------------------------------------------------------------------------
    // SESSION MANAGEMENT
    // --------------------------------------------------------------------------

    /**
     * Load session from saved string
     */
    async loadSession(sessionString: string): Promise<boolean> {
        if (!this.apiId || !this.apiHash) {
            throw new Error("API credentials not set. Call setCredentials() first.");
        }

        try {
            const session = new StringSession(sessionString);
            this.client = new TelegramClient(session, this.apiId, this.apiHash, {
                connectionRetries: 5,
                useWSS: true, // Use WebSocket for browser
            });

            await this.client.connect();

            // Check if actually authenticated
            const me = await this.client.getMe();
            if (me) {
                this._isConnected = true;
                this._currentUser = this.parseUser(me);
                return true;
            }
            return false;
        } catch (error) {
            console.error("Failed to load session:", error);
            return false;
        }
    }

    /**
     * Save current session as string
     */
    saveSession(): string {
        if (!this.client) return "";
        return (this.client.session as StringSession).save();
    }

    // --------------------------------------------------------------------------
    // AUTHENTICATION
    // --------------------------------------------------------------------------

    /**
     * Start login flow with phone number
     */
    async login(callbacks: LoginCallbacks): Promise<boolean> {
        if (!this.apiId || !this.apiHash) {
            throw new Error("API credentials not set. Call setCredentials() first.");
        }

        try {
            const session = new StringSession("");
            this.client = new TelegramClient(session, this.apiId, this.apiHash, {
                connectionRetries: 5,
                useWSS: true,
            });

            await this.client.start({
                phoneNumber: callbacks.onPhoneNumber,
                phoneCode: callbacks.onPhoneCode,
                password: callbacks.onPassword,
                onError: callbacks.onError,
            });

            // client.start() already calls getMe internally and caches the result
            // We can access it via client.session.save() being non-empty
            // But we need user info, so we call getMe once here (it's cached in GramJS)
            if (this.client.connected) {
                const me = await this.client.getMe();
                if (me) {
                    this._isConnected = true;
                    this._currentUser = this.parseUser(me);
                    return true;
                }
            }
            return false;
        } catch (error) {
            callbacks.onError(error instanceof Error ? error : new Error(String(error)));
            return false;
        }
    }

    /**
     * Logout and clear session
     */
    async logout(): Promise<void> {
        if (this.client) {
            try {
                await this.client.invoke(new Api.auth.LogOut());
            } catch {
                // Ignore logout errors
            }
            await this.client.disconnect();
        }
        this.client = null;
        this._isConnected = false;
        this._currentUser = null;
        this._storageChat = null;
        this._resolvedEntities.clear();
    }

    // --------------------------------------------------------------------------
    // CHAT OPERATIONS
    // --------------------------------------------------------------------------

    /**
     * Get list of dialogs (chats) for user to pick storage
     */
    async getDialogs(limit: number = 50): Promise<ChatInfo[]> {
        if (!this.client) throw new Error("Not connected");

        const dialogs = await this.client.getDialogs({ limit });
        const chats: ChatInfo[] = [];

        // Add "Saved Messages" as first option
        chats.push({
            id: "me",
            title: "Saved Messages",
            type: "saved",
        });

        for (const dialog of dialogs) {
            const entity = dialog.entity;
            if (!entity) continue;

            let chatInfo: ChatInfo;

            if (entity instanceof Api.User) {
                chatInfo = {
                    id: entity.id.toString(),
                    title: `${entity.firstName || ""} ${entity.lastName || ""}`.trim() || entity.username || "Unknown",
                    type: "user",
                    unreadCount: dialog.unreadCount,
                };
            } else if (entity instanceof Api.Chat) {
                chatInfo = {
                    id: `-${entity.id}`,
                    title: entity.title,
                    type: "chat",
                    unreadCount: dialog.unreadCount,
                };
            } else if (entity instanceof Api.Channel) {
                const prefix = entity.megagroup ? "-100" : "-100";
                chatInfo = {
                    id: `${prefix}${entity.id}`,
                    title: entity.title,
                    type: "channel",
                    unreadCount: dialog.unreadCount,
                };
            } else {
                continue;
            }

            chats.push(chatInfo);
        }

        return chats;
    }

    /**
     * Set storage chat
     */
    setStorageChat(chat: ChatInfo): void {
        this._storageChat = chat;
    }

    // --------------------------------------------------------------------------
    // FILE OPERATIONS
    // --------------------------------------------------------------------------

    /**
     * Resolve chat entity for API calls
     * Caches resolved entities to avoid repeated lookups
     */
    private async resolveEntity(chatId: string): Promise<Api.TypeInputPeer> {
        if (!this.client) throw new Error("Not connected");

        // Check cache first
        if (this._resolvedEntities.has(chatId)) {
            return this._resolvedEntities.get(chatId)!;
        }

        // Resolve "me" to current user
        if (chatId === "me") {
            const me = await this.client.getMe();
            const inputPeer = new Api.InputPeerUser({
                userId: me.id,
                accessHash: (me as Api.User).accessHash || BigInt(0),
            });
            this._resolvedEntities.set(chatId, inputPeer);
            return inputPeer;
        }

        // Try to get input entity from GramJS
        try {
            const entity = await this.client.getInputEntity(chatId);
            this._resolvedEntities.set(chatId, entity);
            return entity;
        } catch {
            // If that fails, try parsing the ID and getting from dialogs
            const numericId = BigInt(chatId.replace(/^-100/, "-").replace(/^-/, ""));
            const entity = await this.client.getInputEntity(numericId);
            this._resolvedEntities.set(chatId, entity);
            return entity;
        }
    }

    /**
     * Upload file to storage chat
     */
    async uploadFile(
        file: File,
        onProgress?: (progress: number) => void
    ): Promise<TelegramFile> {
        if (!this.client) throw new Error("Not connected");
        if (!this._storageChat) throw new Error("No storage chat selected");

        // Resolve the chat entity properly
        const chatId = this._storageChat.id;
        const entity = await this.resolveEntity(chatId);

        // Convert File to Uint8Array for upload (browser-compatible)
        const buffer = new Uint8Array(await file.arrayBuffer());

        // Wrap buffer in CustomFile to include filename metadata
        const customFile = new CustomFile(file.name, file.size, "", buffer);

        const result = await this.client.sendFile(entity, {
            file: customFile,
            caption: JSON.stringify({
                name: file.name,
                size: file.size,
                type: file.type,
                uploaded: new Date().toISOString(),
            }),
            progressCallback: (progress: number) => {
                onProgress?.(Math.round(progress * 100));
            },
        });

        // Extract file info from result
        const message = result as Api.Message;
        const media = message.media;

        let fileId = "";
        let fileUniqueId = "";
        let fileSize = file.size;
        let thumbnailId: string | undefined;

        if (media instanceof Api.MessageMediaDocument && media.document instanceof Api.Document) {
            fileId = media.document.id.toString();
            fileUniqueId = `${media.document.id}_${media.document.accessHash}`;
            fileSize = Number(media.document.size);
        }

        const telegramFile: TelegramFile = {
            file_id: fileId,
            file_unique_id: fileUniqueId || crypto.randomUUID(),
            file_size: fileSize,
            file_name: file.name,
            mime_type: file.type || "application/octet-stream",
            created_at: new Date(),
            message_id: message.id,
            thumbnail_id: thumbnailId,
        };

        return telegramFile;
    }

    /**
     * Download file from storage chat
     */
    async downloadFile(messageId: number): Promise<Blob> {
        if (!this.client) throw new Error("Not connected");
        if (!this._storageChat) throw new Error("No storage chat selected");

        // Resolve the chat entity properly
        const entity = await this.resolveEntity(this._storageChat.id);

        // Get the message
        const messages = await this.client.getMessages(entity, { ids: [messageId] });
        if (!messages.length || !messages[0]) {
            throw new Error("Message not found");
        }

        const message = messages[0];
        if (!message.media) {
            throw new Error("No media in message");
        }

        // Download the file
        const buffer = await this.client.downloadMedia(message, {});
        if (!buffer) throw new Error("Failed to download");

        // Convert to Uint8Array and create a new ArrayBuffer copy for Blob compatibility
        // This ensures we have a pure ArrayBuffer, not SharedArrayBuffer
        const data = buffer as Uint8Array;
        const copy = new Uint8Array(data);
        return new Blob([copy]);
    }

    /**
     * Download file thumbnail
     */
    async downloadThumbnail(messageId: number): Promise<Blob | null> {
        if (!this.client || !this._storageChat) return null;

        try {
            const entity = await this.resolveEntity(this._storageChat.id);
            const messages = await this.client.getMessages(entity, { ids: [messageId] });
            if (!messages.length || !messages[0]) return null;

            const message = messages[0];

            // Attempt to download thumbnail (size 's' for small)
            // @ts-ignore - GramJS types might be incomplete for downloadMedia options
            const buffer = await this.client.downloadMedia(message, { thumb: 's' });

            if (!buffer) return null;

            const data = buffer as Uint8Array;
            const copy = new Uint8Array(data);
            return new Blob([copy], { type: 'image/jpeg' });
        } catch (error) {
            console.warn("Thumbnail download failed:", error);
            return null;
        }
    }

    /**
     * Delete file from storage chat
     */
    async deleteFile(messageId: number): Promise<boolean> {
        if (!this.client) throw new Error("Not connected");
        if (!this._storageChat) throw new Error("No storage chat selected");

        try {
            // Resolve the chat entity properly
            const entity = await this.resolveEntity(this._storageChat.id);
            await this.client.deleteMessages(entity, [messageId], { revoke: true });
            return true;
        } catch (error) {
            console.error("Failed to delete message:", error);
            return false;
        }
    }

    /**
     * Get messages with files from storage chat
     */
    async getStoredFiles(limit: number = 100): Promise<TelegramFile[]> {
        if (!this.client) throw new Error("Not connected");
        if (!this._storageChat) throw new Error("No storage chat selected");

        // Resolve the chat entity properly
        const entity = await this.resolveEntity(this._storageChat.id);

        const messages = await this.client.getMessages(entity, {
            limit,
            filter: new Api.InputMessagesFilterDocument(),
        });

        const files: TelegramFile[] = [];

        for (const message of messages) {
            if (!message.media) continue;

            const media = message.media;
            if (!(media instanceof Api.MessageMediaDocument)) continue;
            if (!(media.document instanceof Api.Document)) continue;

            const doc = media.document;

            // Parse caption for metadata
            let fileName = "Unknown";
            let mimeType = "application/octet-stream";

            for (const attr of doc.attributes) {
                if (attr instanceof Api.DocumentAttributeFilename) {
                    fileName = attr.fileName;
                }
            }

            mimeType = doc.mimeType;

            // Try to parse caption JSON
            try {
                if (message.message) {
                    const meta = JSON.parse(message.message);
                    if (meta.name) fileName = meta.name;
                    if (meta.type) mimeType = meta.type;
                }
            } catch {
                // Caption not JSON, use filename from attributes
            }

            files.push({
                file_id: doc.id.toString(),
                file_unique_id: `${doc.id}_${doc.accessHash}`,
                file_size: Number(doc.size),
                file_name: fileName,
                mime_type: mimeType,
                created_at: new Date(message.date * 1000),
                message_id: message.id,
            });
        }

        return files;
    }

    // --------------------------------------------------------------------------
    // HELPERS
    // --------------------------------------------------------------------------

    private parseUser(user: Api.User): UserInfo {
        return {
            id: user.id.toString(),
            firstName: user.firstName || "",
            lastName: user.lastName,
            username: user.username,
            phone: user.phone,
        };
    }
}

// ============================================================================
// SINGLETON INSTANCE
// ============================================================================

export const gramjsClient = new GramJSClient();

/**
 * Settings Store - Zustand State Management
 * @module store/settings
 * 
 * Supports both Bot API (legacy) and GramJS (MTProto) authentication.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { TelegramSettings } from '../lib/telegram/types';
import { settingsMetadata } from '../lib/telegram/metadata';
import { telegramClient } from '../lib/telegram/client';
import { gramjsClient, type ChatInfo } from '../lib/telegram/gramjs-client';

// ============================================================================
// TYPES
// ============================================================================

type Theme = 'dark' | 'light' | 'system';
type AuthMethod = 'bot' | 'gramjs';

interface GramJSSettings {
    session: string;
    chatId: string;
    chatTitle: string;
    chatType: 'user' | 'chat' | 'channel' | 'saved';
    userName?: string;
    userPhone?: string;
}

interface SettingsState {
    // Telegram (Bot API - legacy)
    telegram: TelegramSettings | null;

    // GramJS (MTProto - new)
    gramjs: GramJSSettings | null;
    authMethod: AuthMethod | null;

    // Connection state
    isConnecting: boolean;
    connectionError: string | null;

    // Appearance
    theme: Theme;

    // UI
    sidebarCollapsed: boolean;
    showHiddenFiles: boolean;
    confirmDelete: boolean;

    // Actions - Bot API (legacy)
    connectTelegram: (botToken: string, channelId: string) => Promise<boolean>;

    // Actions - GramJS
    connectGramJS: (session: string, chat: ChatInfo) => Promise<boolean>;
    loadGramJSSession: () => Promise<boolean>;

    // Actions - Common
    disconnectTelegram: () => Promise<void>;
    loadSettings: () => Promise<void>;
    isConnected: () => boolean;

    setTheme: (theme: Theme) => void;
    toggleSidebar: () => void;
    setShowHiddenFiles: (show: boolean) => void;
    setConfirmDelete: (confirm: boolean) => void;
}

// ============================================================================
// STORE
// ============================================================================

export const useSettingsStore = create<SettingsState>()(
    persist(
        (set, get) => ({
            // Initial State
            telegram: null,
            gramjs: null,
            authMethod: null,
            isConnecting: false,
            connectionError: null,
            theme: 'dark',
            sidebarCollapsed: false,
            showHiddenFiles: false,
            confirmDelete: true,

            // Connect via Bot API (legacy)
            connectTelegram: async (botToken: string, channelId: string) => {
                set({ isConnecting: true, connectionError: null });

                try {
                    const settings: TelegramSettings = {
                        bot_token: botToken,
                        channel_id: channelId,
                        is_connected: false,
                    };

                    // Try to connect
                    await telegramClient.connect(settings);

                    // Get bot info
                    const botInfo = await telegramClient.getBotInfo();

                    const connectedSettings: TelegramSettings = {
                        ...settings,
                        is_connected: true,
                        bot_username: botInfo.username,
                        last_verified: new Date(),
                    };

                    // Save to IndexedDB
                    await settingsMetadata.saveTelegramSettings(connectedSettings);

                    set({
                        telegram: connectedSettings,
                        authMethod: 'bot',
                        isConnecting: false,
                    });

                    return true;
                } catch (error) {
                    set({
                        connectionError: error instanceof Error ? error.message : 'Connection failed',
                        isConnecting: false,
                    });
                    return false;
                }
            },

            // Connect via GramJS (new)
            connectGramJS: async (session: string, chat: ChatInfo) => {
                set({ isConnecting: true, connectionError: null });

                try {
                    const user = gramjsClient.currentUser;

                    const gramjsSettings: GramJSSettings = {
                        session,
                        chatId: chat.id,
                        chatTitle: chat.title,
                        chatType: chat.type,
                        userName: user?.firstName,
                        userPhone: user?.phone,
                    };

                    // Save to IndexedDB
                    await settingsMetadata.set('gramjs', gramjsSettings);

                    set({
                        gramjs: gramjsSettings,
                        authMethod: 'gramjs',
                        telegram: null, // Clear bot settings
                        isConnecting: false,
                    });

                    return true;
                } catch (error) {
                    set({
                        connectionError: error instanceof Error ? error.message : 'Connection failed',
                        isConnecting: false,
                    });
                    return false;
                }
            },

            // Load existing GramJS session
            loadGramJSSession: async () => {
                try {
                    const gramjsSettings = await settingsMetadata.get('gramjs') as GramJSSettings | null;

                    if (gramjsSettings?.session) {
                        const success = await gramjsClient.loadSession(gramjsSettings.session);

                        if (success) {
                            // Restore storage chat
                            gramjsClient.setStorageChat({
                                id: gramjsSettings.chatId,
                                title: gramjsSettings.chatTitle,
                                type: gramjsSettings.chatType,
                            });

                            set({
                                gramjs: gramjsSettings,
                                authMethod: 'gramjs',
                            });
                            return true;
                        }
                    }
                    return false;
                } catch (error) {
                    console.error('Failed to load GramJS session:', error);
                    return false;
                }
            },

            // Disconnect from Telegram
            disconnectTelegram: async () => {
                const state = get();

                if (state.authMethod === 'gramjs') {
                    await gramjsClient.logout();
                    await settingsMetadata.set('gramjs', null);
                    set({ gramjs: null, authMethod: null });
                } else {
                    telegramClient.disconnect();
                    await settingsMetadata.set('telegram', null);
                    set({ telegram: null, authMethod: null });
                }
            },

            // Load settings from IndexedDB
            loadSettings: async () => {
                try {
                    // Try GramJS first (preferred)
                    const gramjsLoaded = await get().loadGramJSSession();
                    if (gramjsLoaded) return;

                    // Fall back to Bot API
                    const telegram = await settingsMetadata.getTelegramSettings();

                    if (telegram?.is_connected && telegram.bot_token) {
                        try {
                            await telegramClient.connect(telegram);
                            set({ telegram, authMethod: 'bot' });
                        } catch {
                            set({ telegram: { ...telegram, is_connected: false }, authMethod: null });
                        }
                    } else if (telegram) {
                        set({ telegram });
                    }
                } catch (error) {
                    console.error('Failed to load settings:', error);
                }
            },

            // Check if connected (any method)
            isConnected: () => {
                const state = get();
                if (state.authMethod === 'gramjs') {
                    return gramjsClient.connected;
                }
                if (state.authMethod === 'bot') {
                    return telegramClient.connected;
                }
                return false;
            },

            // Theme
            setTheme: (theme) => {
                set({ theme });

                // Apply theme to document
                if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                } else if (theme === 'light') {
                    document.documentElement.classList.remove('dark');
                } else {
                    // System preference
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    if (prefersDark) {
                        document.documentElement.classList.add('dark');
                    } else {
                        document.documentElement.classList.remove('dark');
                    }
                }
            },

            // UI Settings
            toggleSidebar: () => set(state => ({ sidebarCollapsed: !state.sidebarCollapsed })),
            setShowHiddenFiles: (show) => set({ showHiddenFiles: show }),
            setConfirmDelete: (confirm) => set({ confirmDelete: confirm }),
        }),
        {
            name: 'file-manager-settings',
            partialize: (state) => ({
                theme: state.theme,
                sidebarCollapsed: state.sidebarCollapsed,
                showHiddenFiles: state.showHiddenFiles,
                confirmDelete: state.confirmDelete,
            }),
        }
    )
);

// Initialize theme on load
if (typeof window !== 'undefined') {
    const settings = useSettingsStore.getState();
    settings.setTheme(settings.theme);
}

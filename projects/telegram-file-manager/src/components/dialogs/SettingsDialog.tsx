/**
 * Settings Dialog Component
 * @module components/dialogs/SettingsDialog
 * 
 * Updated to support both Bot API and GramJS authentication
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X,
    Settings,
    Bot,
    Palette,
    Trash2,
    Download,
    Upload,
    AlertTriangle,
    CheckCircle2,
    Loader2,
    Key,
    Hash,
    Smartphone,
    MessageSquare,
    Save,
    Users,
    ChevronRight,
} from 'lucide-react';
import { useSettingsStore } from '../../store/settings';
import { database } from '../../lib/telegram/metadata';
import { TelegramLoginDialog } from './TelegramLoginDialog';
import type { ChatInfo } from '../../lib/telegram/gramjs-client';

// ============================================================================
// TYPES
// ============================================================================

interface SettingsDialogProps {
    isOpen: boolean;
    onClose: () => void;
}

type Tab = 'telegram' | 'appearance' | 'data';

// ============================================================================
// COMPONENT
// ============================================================================

export function SettingsDialog({ isOpen, onClose }: SettingsDialogProps) {
    const [activeTab, setActiveTab] = useState<Tab>('telegram');
    const [showBotLogin, setShowBotLogin] = useState(false);
    const [showGramJSLogin, setShowGramJSLogin] = useState(false);
    const [botToken, setBotToken] = useState('');
    const [channelId, setChannelId] = useState('');
    const [showClearConfirm, setShowClearConfirm] = useState(false);

    const {
        telegram,
        gramjs,
        authMethod,
        isConnecting,
        connectionError,
        connectTelegram,
        connectGramJS,
        disconnectTelegram,
        theme,
        setTheme,
    } = useSettingsStore();

    const isConnected = authMethod !== null && (telegram?.is_connected || gramjs !== null);

    const handleBotConnect = async () => {
        if (botToken && channelId) {
            const success = await connectTelegram(botToken, channelId);
            if (success) {
                setBotToken('');
                setChannelId('');
                setShowBotLogin(false);
            }
        }
    };

    const handleGramJSSuccess = async (session: string, chat: ChatInfo) => {
        await connectGramJS(session, chat);
        setShowGramJSLogin(false);
    };

    const handleExportData = async () => {
        const data = await database.export();
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `telecloud-backup-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleImportData = async () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
                const text = await file.text();
                await database.import(text);
                window.location.reload();
            }
        };
        input.click();
    };

    const handleClearData = async () => {
        await database.clearAll();
        await disconnectTelegram();
        window.location.reload();
    };

    const getChatIcon = (type: string) => {
        switch (type) {
            case 'saved': return <Save size={16} style={{ color: '#7c3aed' }} />;
            case 'channel': return <MessageSquare size={16} style={{ color: '#3b82f6' }} />;
            case 'chat': return <Users size={16} style={{ color: '#22c55e' }} />;
            default: return <MessageSquare size={16} style={{ color: '#f59e0b' }} />;
        }
    };

    const tabs = [
        { id: 'telegram' as Tab, label: 'Telegram', icon: <MessageSquare size={18} /> },
        { id: 'appearance' as Tab, label: 'Appearance', icon: <Palette size={18} /> },
        { id: 'data' as Tab, label: 'Data', icon: <Download size={18} /> },
    ];

    return (
        <>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="modal-overlay"
                        onClick={onClose}
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="glass w-full max-w-lg rounded-2xl overflow-hidden"
                            onClick={e => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div
                                className="flex items-center justify-between p-4"
                                style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}
                            >
                                <div className="flex items-center gap-3">
                                    <Settings size={20} style={{ color: '#7c3aed' }} />
                                    <h2 className="text-lg font-semibold">Settings</h2>
                                </div>
                                <button onClick={onClose} className="btn-icon">
                                    <X size={20} />
                                </button>
                            </div>

                            {/* Tabs */}
                            <div
                                className="flex p-2 gap-1"
                                style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}
                            >
                                {tabs.map(tab => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className="flex items-center gap-2 px-4 py-2 rounded-lg transition-all text-sm"
                                        style={{
                                            background: activeTab === tab.id ? 'rgba(124, 58, 237, 0.2)' : 'transparent',
                                            color: activeTab === tab.id ? 'white' : 'rgba(255,255,255,0.6)',
                                        }}
                                    >
                                        {tab.icon}
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            {/* Content */}
                            <div className="p-4 max-h-96 overflow-y-auto">
                                {/* Telegram Tab */}
                                {activeTab === 'telegram' && (
                                    <div className="space-y-4">
                                        {isConnected ? (
                                            <div
                                                className="p-4 rounded-xl"
                                                style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)' }}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <CheckCircle2 size={20} style={{ color: '#22c55e' }} />
                                                    <div className="flex-1">
                                                        <p className="font-medium">Connected to Telegram</p>
                                                        {authMethod === 'gramjs' && gramjs && (
                                                            <div className="flex items-center gap-2 mt-1">
                                                                {getChatIcon(gramjs.chatType)}
                                                                <span className="text-sm" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                                    {gramjs.chatTitle}
                                                                </span>
                                                                <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(124, 58, 237, 0.3)', color: '#a78bfa' }}>
                                                                    MTProto
                                                                </span>
                                                            </div>
                                                        )}
                                                        {authMethod === 'bot' && telegram && (
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <Bot size={16} style={{ color: 'rgba(255,255,255,0.4)' }} />
                                                                <span className="text-sm" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                                    @{telegram.bot_username}
                                                                </span>
                                                                <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(59, 130, 246, 0.3)', color: '#93c5fd' }}>
                                                                    Bot API
                                                                </span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={disconnectTelegram}
                                                    className="mt-4 btn-ghost text-sm w-full"
                                                    style={{ color: '#f87171' }}
                                                >
                                                    Disconnect
                                                </button>
                                            </div>
                                        ) : showBotLogin ? (
                                            <>
                                                <div className="flex items-center gap-2 mb-2">
                                                    <button
                                                        onClick={() => setShowBotLogin(false)}
                                                        className="text-sm flex items-center gap-1"
                                                        style={{ color: 'rgba(255,255,255,0.5)' }}
                                                    >
                                                        ← Back
                                                    </button>
                                                </div>
                                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                                    Connect using a Telegram bot (legacy method).
                                                </p>

                                                <div className="space-y-3">
                                                    <div>
                                                        <label className="text-sm mb-1 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                                            Bot Token
                                                        </label>
                                                        <div className="relative">
                                                            <Key size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'rgba(255,255,255,0.4)' }} />
                                                            <input
                                                                type="password"
                                                                value={botToken}
                                                                onChange={e => setBotToken(e.target.value)}
                                                                placeholder="123456789:ABCdef..."
                                                                className="input-glass pl-10 text-sm"
                                                            />
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="text-sm mb-1 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                                            Channel ID
                                                        </label>
                                                        <div className="relative">
                                                            <Hash size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'rgba(255,255,255,0.4)' }} />
                                                            <input
                                                                type="text"
                                                                value={channelId}
                                                                onChange={e => setChannelId(e.target.value)}
                                                                placeholder="-1001234567890"
                                                                className="input-glass pl-10 text-sm"
                                                            />
                                                        </div>
                                                    </div>

                                                    {connectionError && (
                                                        <div
                                                            className="p-3 rounded-lg text-sm"
                                                            style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}
                                                        >
                                                            {connectionError}
                                                        </div>
                                                    )}

                                                    <button
                                                        onClick={handleBotConnect}
                                                        disabled={!botToken || !channelId || isConnecting}
                                                        className="btn-gradient w-full flex items-center justify-center gap-2"
                                                        style={{ opacity: (!botToken || !channelId || isConnecting) ? 0.5 : 1 }}
                                                    >
                                                        {isConnecting ? (
                                                            <>
                                                                <Loader2 size={18} className="animate-spin" />
                                                                Connecting...
                                                            </>
                                                        ) : (
                                                            'Connect'
                                                        )}
                                                    </button>
                                                </div>
                                            </>
                                        ) : (
                                            <>
                                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                                    Connect your Telegram account to store files securely.
                                                </p>

                                                <div className="space-y-2">
                                                    {/* GramJS Login - Recommended */}
                                                    <button
                                                        onClick={() => setShowGramJSLogin(true)}
                                                        className="w-full flex items-center gap-3 p-4 rounded-xl transition-all group"
                                                        style={{
                                                            background: 'linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2))',
                                                            border: '1px solid rgba(124, 58, 237, 0.4)',
                                                        }}
                                                    >
                                                        <div
                                                            className="w-12 h-12 rounded-xl flex items-center justify-center"
                                                            style={{ background: 'rgba(124, 58, 237, 0.3)' }}
                                                        >
                                                            <Smartphone size={24} style={{ color: '#a78bfa' }} />
                                                        </div>
                                                        <div className="flex-1 text-left">
                                                            <div className="flex items-center gap-2">
                                                                <p className="font-medium">Login with Phone</p>
                                                                <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(34, 197, 94, 0.3)', color: '#86efac' }}>
                                                                    Recommended
                                                                </span>
                                                            </div>
                                                            <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                                Login with your Telegram account • No bot required • 2GB file limit
                                                            </p>
                                                        </div>
                                                        <ChevronRight size={20} style={{ color: 'rgba(255,255,255,0.4)' }} className="group-hover:translate-x-1 transition-transform" />
                                                    </button>

                                                    {/* Bot Login - Legacy */}
                                                    <button
                                                        onClick={() => setShowBotLogin(true)}
                                                        className="w-full flex items-center gap-3 p-4 rounded-xl transition-all group"
                                                        style={{
                                                            background: 'rgba(255,255,255,0.05)',
                                                            border: '1px solid rgba(255,255,255,0.1)',
                                                        }}
                                                    >
                                                        <div
                                                            className="w-12 h-12 rounded-xl flex items-center justify-center"
                                                            style={{ background: 'rgba(255,255,255,0.1)' }}
                                                        >
                                                            <Bot size={24} style={{ color: 'rgba(255,255,255,0.6)' }} />
                                                        </div>
                                                        <div className="flex-1 text-left">
                                                            <p className="font-medium">Connect Bot</p>
                                                            <p className="text-xs mt-0.5" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                                Use a Telegram bot token • 50MB file limit
                                                            </p>
                                                        </div>
                                                        <ChevronRight size={20} style={{ color: 'rgba(255,255,255,0.4)' }} className="group-hover:translate-x-1 transition-transform" />
                                                    </button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )}

                                {/* Appearance Tab */}
                                {activeTab === 'appearance' && (
                                    <div className="space-y-4">
                                        <div>
                                            <label className="text-sm mb-2 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                                Theme
                                            </label>
                                            <div className="flex gap-2">
                                                {(['dark', 'light', 'system'] as const).map(t => (
                                                    <button
                                                        key={t}
                                                        onClick={() => setTheme(t)}
                                                        className="flex-1 py-2 px-4 rounded-lg text-sm capitalize transition-all"
                                                        style={{
                                                            background: theme === t ? 'rgba(124, 58, 237, 0.2)' : 'rgba(255,255,255,0.05)',
                                                            border: theme === t ? '1px solid rgba(124, 58, 237, 0.5)' : '1px solid rgba(255,255,255,0.1)',
                                                        }}
                                                    >
                                                        {t}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Data Tab */}
                                {activeTab === 'data' && (
                                    <div className="space-y-4">
                                        <div className="space-y-2">
                                            <button
                                                onClick={handleExportData}
                                                className="w-full flex items-center gap-3 p-3 rounded-lg transition-all"
                                                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                                            >
                                                <Download size={18} style={{ color: '#22c55e' }} />
                                                <div className="text-left">
                                                    <p className="font-medium text-sm">Export Data</p>
                                                    <p className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                        Download all your file metadata as JSON
                                                    </p>
                                                </div>
                                            </button>

                                            <button
                                                onClick={handleImportData}
                                                className="w-full flex items-center gap-3 p-3 rounded-lg transition-all"
                                                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                                            >
                                                <Upload size={18} style={{ color: '#3b82f6' }} />
                                                <div className="text-left">
                                                    <p className="font-medium text-sm">Import Data</p>
                                                    <p className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                        Restore from a backup file
                                                    </p>
                                                </div>
                                            </button>
                                        </div>

                                        <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                                            {!showClearConfirm ? (
                                                <button
                                                    onClick={() => setShowClearConfirm(true)}
                                                    className="w-full flex items-center gap-3 p-3 rounded-lg transition-all"
                                                    style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}
                                                >
                                                    <Trash2 size={18} style={{ color: '#f87171' }} />
                                                    <div className="text-left">
                                                        <p className="font-medium text-sm" style={{ color: '#f87171' }}>Clear All Data</p>
                                                        <p className="text-xs" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                            Delete all local data and reset the app
                                                        </p>
                                                    </div>
                                                </button>
                                            ) : (
                                                <div
                                                    className="p-4 rounded-lg"
                                                    style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}
                                                >
                                                    <div className="flex items-start gap-3 mb-4">
                                                        <AlertTriangle size={20} style={{ color: '#f87171' }} />
                                                        <div>
                                                            <p className="font-medium" style={{ color: '#f87171' }}>Are you sure?</p>
                                                            <p className="text-sm" style={{ color: 'rgba(255,255,255,0.5)' }}>
                                                                This will permanently delete all your local data.
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => setShowClearConfirm(false)}
                                                            className="flex-1 btn-ghost text-sm"
                                                        >
                                                            Cancel
                                                        </button>
                                                        <button
                                                            onClick={handleClearData}
                                                            className="flex-1 py-2 px-4 rounded-lg text-sm"
                                                            style={{ background: '#ef4444', color: 'white' }}
                                                        >
                                                            Clear Data
                                                        </button>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* GramJS Login Dialog */}
            <TelegramLoginDialog
                isOpen={showGramJSLogin}
                onClose={() => setShowGramJSLogin(false)}
                onSuccess={handleGramJSSuccess}
            />
        </>
    );
}

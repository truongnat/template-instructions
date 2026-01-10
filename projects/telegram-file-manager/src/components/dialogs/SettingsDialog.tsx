/**
 * Settings Dialog Component - Updated with CSS Animations & GramJS focus
 * @module components/dialogs/SettingsDialog
 */

import { useState, useCallback, useEffect } from 'react';
import {
    X,
    Settings,
    Palette,
    Trash2,
    Download,
    Upload,
    AlertTriangle,
    CheckCircle2,
    Smartphone,
    MessageSquare,
    Save,
    Users,
    ChevronRight,
    Monitor,
    Sun,
    Moon,
} from 'lucide-react';
import { useSettingsStore } from '../../store/settings';
import { database } from '../../lib/telegram/metadata';
import { TelegramLoginDialog } from './TelegramLoginDialog';
import type { ChatInfo } from '../../lib/telegram/gramjs-client';
import { useResponsive } from '../../hooks/useResponsive';

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
    const [showGramJSLogin, setShowGramJSLogin] = useState(false);
    const [showClearConfirm, setShowClearConfirm] = useState(false);
    const [isExiting, setIsExiting] = useState(false);
    const { isMobile } = useResponsive();

    const {
        gramjs,
        authMethod,
        connectGramJS,
        disconnectTelegram,
        theme,
        setTheme,
    } = useSettingsStore();

    const isConnected = authMethod === 'gramjs' && gramjs !== null;

    // Securely handle modal closing with animation
    const handleClose = useCallback(() => {
        setIsExiting(true);
        setTimeout(() => {
            onClose();
            setIsExiting(false);
        }, 300);
    }, [onClose]);

    // Handle escape key
    useEffect(() => {
        if (!isOpen) return;
        const handleEsc = (e: KeyboardEvent) => e.key === 'Escape' && handleClose();
        window.addEventListener('keydown', handleEsc);
        return () => window.removeEventListener('keydown', handleEsc);
    }, [isOpen, handleClose]);

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
            case 'saved': return <Save size={16} className="text-accent-purple" />;
            case 'channel': return <MessageSquare size={16} className="text-accent-blue" />;
            case 'chat': return <Users size={16} className="text-green-500" />;
            default: return <MessageSquare size={16} className="text-yellow-500" />;
        }
    };

    if (!isOpen && !isExiting) return null;

    const tabs = [
        { id: 'telegram' as Tab, label: 'Account', icon: <MessageSquare size={18} /> },
        { id: 'appearance' as Tab, label: 'Theme', icon: <Palette size={18} /> },
        { id: 'data' as Tab, label: 'System', icon: <Download size={18} /> },
    ];

    return (
        <div
            className={`fixed inset-0 z-50 flex items-center justify-center p-4 transition-all duration-300 ${isMobile ? 'items-end p-0' : ''} ${isExiting ? 'animate-fade-out' : 'animate-fade-in'
                }`}
            style={{ background: 'rgba(0, 0, 0, 0.4)', backdropFilter: 'blur(8px)' }}
            onClick={handleClose}
        >
            <div
                className={`glass w-full max-w-lg overflow-hidden flex flex-col shadow-2xl safe-bottom ${isMobile ? 'h-[85vh] rounded-t-[2.5rem]' : 'max-h-[85vh] rounded-3xl'
                    } ${isExiting ? 'animate-slide-down-to-bottom' : 'animate-slide-up-from-bottom'}`}
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-accent-purple/10">
                            <Settings size={22} className="text-accent-purple" />
                        </div>
                        <h2 className="text-xl font-bold gradient-text">Settings</h2>
                    </div>
                    <button onClick={handleClose} className="btn-icon">
                        <X size={24} />
                    </button>
                    {isMobile && (
                        <div className="absolute top-2 left-1/2 -translate-x-1/2 w-12 h-1 bg-white/20 rounded-full" />
                    )}
                </div>

                {/* Tabs */}
                <div className="flex p-2 gap-1 bg-black/20 border-b border-white/5">
                    {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-3 rounded-xl transition-all text-sm font-medium flex-1 justify-center ${activeTab === tab.id
                                ? 'bg-white/10 text-white shadow-lg'
                                : 'text-white/50 hover:text-white/80 hover:bg-white/5'
                                }`}
                        >
                            {tab.icon}
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 scroll-container">
                    {/* Telegram Tab */}
                    {activeTab === 'telegram' && (
                        <div className="space-y-6 animate-fade-in">
                            <div>
                                <h3 className="text-white/40 text-xs font-bold uppercase tracking-widest mb-4">Telegram Connection</h3>
                                {isConnected ? (
                                    <div className="p-5 rounded-2xl bg-green-500/10 border border-green-500/20 group">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center shrink-0">
                                                <CheckCircle2 size={24} className="text-green-500" />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="font-bold text-white">Authenticated</p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    {getChatIcon(gramjs?.chatType || 'saved')}
                                                    <span className="text-sm text-white/50 truncate">
                                                        {gramjs?.chatTitle || 'Saved Messages'}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={disconnectTelegram}
                                            className="mt-6 w-full py-3 rounded-xl bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors text-sm font-bold flex items-center justify-center gap-2"
                                        >
                                            <Trash2 size={16} />
                                            Sign Out Account
                                        </button>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        <div className="p-5 rounded-2xl bg-white/5 border border-white/10 text-center py-8">
                                            <Smartphone size={40} className="mx-auto mb-4 text-white/20" />
                                            <p className="text-white/60 text-sm mb-6 max-w-xs mx-auto">
                                                Sign in with your phone number to enable high-speed cloud storage.
                                            </p>
                                            <button
                                                onClick={() => setShowGramJSLogin(true)}
                                                className="btn-gradient w-full py-4 flex items-center justify-center gap-2"
                                            >
                                                Connect Telegram <ChevronRight size={18} />
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Appearance Tab */}
                    {activeTab === 'appearance' && (
                        <div className="space-y-6 animate-fade-in">
                            <div>
                                <h3 className="text-white/40 text-xs font-bold uppercase tracking-widest mb-4">Theme Preference</h3>
                                <div className="grid grid-cols-1 gap-3">
                                    {[
                                        { id: 'dark', label: 'Dark Mode', icon: <Moon size={20} />, color: 'bg-[#0a0a0a]' },
                                        { id: 'light', label: 'Light Mode', icon: <Sun size={20} />, color: 'bg-white' },
                                        { id: 'system', label: 'System Default', icon: <Monitor size={20} />, color: 'bg-gradient-to-r from-[#0a0a0a] to-white' },
                                    ].map(t => (
                                        <button
                                            key={t.id}
                                            onClick={() => setTheme(t.id as any)}
                                            className={`flex items-center gap-4 p-4 rounded-2xl border transition-all ${theme === t.id
                                                ? 'bg-accent-purple/10 border-accent-purple/50 ring-2 ring-accent-purple/20'
                                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${t.id === 'light' ? 'bg-black/5 text-black' : 'bg-black/40 text-white'}`}>
                                                {t.icon}
                                            </div>
                                            <div className="flex-1 text-left">
                                                <p className="font-bold text-white">{t.label}</p>
                                                <p className="text-xs text-white/40">Switch app appearance</p>
                                            </div>
                                            {theme === t.id && <div className="w-4 h-4 rounded-full bg-accent-purple ring-4 ring-accent-purple/20" />}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Data Tab */}
                    {activeTab === 'data' && (
                        <div className="space-y-8 animate-fade-in">
                            <div className="space-y-4">
                                <h3 className="text-white/40 text-xs font-bold uppercase tracking-widest mb-1">Metadata Backup</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    <button
                                        onClick={handleExportData}
                                        className="flex flex-col items-center gap-3 p-5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-center"
                                    >
                                        <Download size={24} className="text-green-400" />
                                        <p className="font-bold text-sm text-white">Export</p>
                                    </button>
                                    <button
                                        onClick={handleImportData}
                                        className="flex flex-col items-center gap-3 p-5 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all text-center"
                                    >
                                        <Upload size={24} className="text-accent-blue" />
                                        <p className="font-bold text-sm text-white">Import</p>
                                    </button>
                                </div>
                            </div>

                            <div className="pt-6 border-t border-white/5">
                                {!showClearConfirm ? (
                                    <button
                                        onClick={() => setShowClearConfirm(true)}
                                        className="w-full flex items-center gap-4 p-5 rounded-2xl bg-red-500/5 border border-red-500/10 hover:bg-red-500/10 transition-all group"
                                    >
                                        <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center shrink-0">
                                            <Trash2 size={24} className="text-red-400" />
                                        </div>
                                        <div className="text-left">
                                            <p className="font-bold text-sm text-red-400">Clear Storage</p>
                                            <p className="text-xs text-red-400/50">Delete all local files and metadata</p>
                                        </div>
                                    </button>
                                ) : (
                                    <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 animate-scale-in">
                                        <div className="flex items-start gap-4 mb-6">
                                            <div className="p-2 rounded-lg bg-red-500/20 text-red-400">
                                                <AlertTriangle size={24} />
                                            </div>
                                            <div>
                                                <p className="font-bold text-white">Critical Action</p>
                                                <p className="text-sm text-white/50">
                                                    This will wipe all data. Are you absolutely sure?
                                                </p>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <button
                                                onClick={() => setShowClearConfirm(false)}
                                                className="py-3 rounded-xl bg-white/5 text-white/60 hover:text-white transition-colors text-sm font-bold"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                onClick={handleClearData}
                                                className="py-3 rounded-xl bg-red-500 text-white hover:bg-red-600 transition-colors text-sm font-bold shadow-lg shadow-red-500/20"
                                            >
                                                Wipe Now
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 bg-black/10 text-center">
                    <p className="text-[10px] text-white/20 uppercase font-black tracking-[0.2em]">TeleCloud v1.0 • Built with GramJS</p>
                </div>
            </div>

            {/* Sub-modals */}
            <TelegramLoginDialog
                isOpen={showGramJSLogin}
                onClose={() => setShowGramJSLogin(false)}
                onSuccess={handleGramJSSuccess}
            />
        </div>
    );
}

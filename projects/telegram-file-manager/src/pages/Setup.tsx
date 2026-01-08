/**
 * Setup Page - First-time Telegram Bot Configuration
 * @module pages/Setup
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Bot,
    Key,
    Hash,
    CheckCircle2,
    AlertCircle,
    Loader2,
    ArrowRight,
    ExternalLink,
    Sparkles,
} from 'lucide-react';
import { useSettingsStore } from '../store/settings';

// ============================================================================
// TYPES
// ============================================================================

type Step = 'intro' | 'token' | 'channel' | 'verify' | 'complete';

// ============================================================================
// COMPONENT
// ============================================================================

export function SetupPage() {
    const [step, setStep] = useState<Step>('intro');
    const [botToken, setBotToken] = useState('');
    const [channelId, setChannelId] = useState('');
    const [error, setError] = useState('');

    const { connectTelegram, isConnecting, telegram } = useSettingsStore();

    const handleConnect = async () => {
        setError('');

        if (!botToken.trim()) {
            setError('Please enter your bot token');
            return;
        }

        if (!channelId.trim()) {
            setError('Please enter your channel ID');
            return;
        }

        const success = await connectTelegram(botToken.trim(), channelId.trim());

        if (success) {
            setStep('complete');
        } else {
            setError('Failed to connect. Please check your credentials and try again.');
        }
    };

    // If already connected, redirect to app
    if (telegram?.is_connected) {
        return null; // Will be handled by parent routing
    }

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-lg"
            >
                {/* Header */}
                <div className="text-center mb-8">
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', delay: 0.2 }}
                        className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center mx-auto mb-4"
                    >
                        <Bot size={40} />
                    </motion.div>
                    <h1 className="text-3xl font-bold gradient-text mb-2">TeleCloud</h1>
                    <p className="text-white/60">Unlimited file storage powered by Telegram</p>
                </div>

                {/* Card */}
                <div className="glass p-6 rounded-2xl">
                    <AnimatePresence mode="wait">
                        {/* Step: Intro */}
                        {step === 'intro' && (
                            <motion.div
                                key="intro"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-6"
                            >
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">Welcome!</h2>
                                    <p className="text-white/60 text-sm">
                                        To use TeleCloud, you need to create a Telegram Bot and a private channel for storage.
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-start gap-3 p-4 bg-dark-700/50 rounded-xl">
                                        <div className="w-8 h-8 rounded-lg bg-accent-purple/20 flex items-center justify-center flex-shrink-0">
                                            <span className="text-sm font-bold text-accent-purple">1</span>
                                        </div>
                                        <div>
                                            <h3 className="font-medium mb-1">Create a Bot</h3>
                                            <p className="text-sm text-white/60">
                                                Open <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer" className="text-accent-purple hover:underline">@BotFather</a> on Telegram and create a new bot
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-start gap-3 p-4 bg-dark-700/50 rounded-xl">
                                        <div className="w-8 h-8 rounded-lg bg-accent-purple/20 flex items-center justify-center flex-shrink-0">
                                            <span className="text-sm font-bold text-accent-purple">2</span>
                                        </div>
                                        <div>
                                            <h3 className="font-medium mb-1">Create a Private Channel</h3>
                                            <p className="text-sm text-white/60">
                                                Create a channel in Telegram and add your bot as an admin
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-start gap-3 p-4 bg-dark-700/50 rounded-xl">
                                        <div className="w-8 h-8 rounded-lg bg-accent-purple/20 flex items-center justify-center flex-shrink-0">
                                            <span className="text-sm font-bold text-accent-purple">3</span>
                                        </div>
                                        <div>
                                            <h3 className="font-medium mb-1">Get Channel ID</h3>
                                            <p className="text-sm text-white/60">
                                                Forward any message from your channel to <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer" className="text-accent-purple hover:underline">@userinfobot</a>
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={() => setStep('token')}
                                    className="btn-gradient w-full flex items-center justify-center gap-2"
                                >
                                    I'm ready <ArrowRight size={18} />
                                </button>
                            </motion.div>
                        )}

                        {/* Step: Token */}
                        {step === 'token' && (
                            <motion.div
                                key="token"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-6"
                            >
                                <div>
                                    <h2 className="text-xl font-semibold mb-2">Bot Token</h2>
                                    <p className="text-white/60 text-sm">
                                        Paste the token you received from @BotFather
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <div className="relative">
                                        <Key size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                                        <input
                                            type="password"
                                            value={botToken}
                                            onChange={(e) => setBotToken(e.target.value)}
                                            placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz..."
                                            className="input-glass pl-12"
                                        />
                                    </div>

                                    <a
                                        href="https://t.me/BotFather"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-2 text-sm text-accent-purple hover:underline"
                                    >
                                        <ExternalLink size={14} />
                                        Open @BotFather
                                    </a>
                                </div>

                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setStep('intro')}
                                        className="btn-ghost flex-1"
                                    >
                                        Back
                                    </button>
                                    <button
                                        onClick={() => setStep('channel')}
                                        disabled={!botToken.trim()}
                                        className="btn-gradient flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        Next <ArrowRight size={18} />
                                    </button>
                                </div>
                            </motion.div>
                        )}

                        {/* Step: Channel */}
                        {step === 'channel' && (
                            <motion.div
                                key="channel"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-6"
                            >
                                <div>
                                    <h2 className="text-xl font-semibold mb-2">Channel ID</h2>
                                    <p className="text-white/60 text-sm">
                                        Enter your private channel ID (starts with -100)
                                    </p>
                                </div>

                                <div className="space-y-4">
                                    <div className="relative">
                                        <Hash size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                                        <input
                                            type="text"
                                            value={channelId}
                                            onChange={(e) => setChannelId(e.target.value)}
                                            placeholder="-1001234567890"
                                            className="input-glass pl-12"
                                        />
                                    </div>

                                    {error && (
                                        <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
                                            <AlertCircle size={16} />
                                            {error}
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setStep('token')}
                                        className="btn-ghost flex-1"
                                    >
                                        Back
                                    </button>
                                    <button
                                        onClick={handleConnect}
                                        disabled={!channelId.trim() || isConnecting}
                                        className="btn-gradient flex-1 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        {isConnecting ? (
                                            <>
                                                <Loader2 size={18} className="animate-spin" />
                                                Connecting...
                                            </>
                                        ) : (
                                            <>
                                                Connect <ArrowRight size={18} />
                                            </>
                                        )}
                                    </button>
                                </div>
                            </motion.div>
                        )}

                        {/* Step: Complete */}
                        {step === 'complete' && (
                            <motion.div
                                key="complete"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="text-center py-8 space-y-6"
                            >
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring', delay: 0.2 }}
                                    className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto"
                                >
                                    <CheckCircle2 size={40} className="text-green-400" />
                                </motion.div>

                                <div>
                                    <h2 className="text-xl font-semibold mb-2">You're all set!</h2>
                                    <p className="text-white/60 text-sm">
                                        Your TeleCloud is ready to use. Start uploading your files!
                                    </p>
                                </div>

                                <button
                                    onClick={() => window.location.reload()}
                                    className="btn-gradient inline-flex items-center gap-2"
                                >
                                    <Sparkles size={18} />
                                    Start Using TeleCloud
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Footer */}
                <p className="text-center text-xs text-white/40 mt-6">
                    Your credentials are stored locally and never sent to any server except Telegram.
                </p>
            </motion.div>
        </div>
    );
}

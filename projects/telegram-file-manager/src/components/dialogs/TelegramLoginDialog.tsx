/**
 * Telegram Login Dialog Component
 * @module components/dialogs/TelegramLoginDialog
 * 
 * Multi-step login flow: Phone → OTP → 2FA (if enabled) → Chat Picker
 */

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    X,
    Phone,
    Key,
    Lock,
    MessageSquare,
    CheckCircle2,
    Loader2,
    ArrowLeft,
    Save,
    Users,
    User,
    Megaphone,
} from 'lucide-react';
import { gramjsClient, type ChatInfo } from '../../lib/telegram/gramjs-client';

// ============================================================================
// TYPES
// ============================================================================

interface TelegramLoginDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (session: string, chat: ChatInfo) => void;
}

type Step = 'phone' | 'code' | 'password' | 'chat' | 'success';

// ============================================================================
// COMPONENT
// ============================================================================

export function TelegramLoginDialog({ isOpen, onClose, onSuccess }: TelegramLoginDialogProps) {
    const [step, setStep] = useState<Step>('phone');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [phoneCode, setPhoneCode] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [chats, setChats] = useState<ChatInfo[]>([]);
    const [selectedChat, setSelectedChat] = useState<ChatInfo | null>(null);

    // Refs for resolving promises
    const codeResolve = useRef<((value: string) => void) | null>(null);
    const passwordResolve = useRef<((value: string) => void) | null>(null);

    // Reset state when dialog opens
    useEffect(() => {
        if (isOpen) {
            setStep('phone');
            setPhoneNumber('');
            setPhoneCode('');
            setPassword('');
            setError(null);
            setIsLoading(false);
            setChats([]);
            setSelectedChat(null);
        }
    }, [isOpen]);

    // Start login when phone is submitted
    const handlePhoneSubmit = async () => {
        if (!phoneNumber.trim()) {
            setError('Please enter your phone number');
            return;
        }

        setError(null);
        setIsLoading(true);

        // Start the login flow
        gramjsClient.login({
            onPhoneNumber: async () => {
                return phoneNumber;
            },
            onPhoneCode: async () => {
                setStep('code');
                setIsLoading(false);
                // Wait for user to enter code
                return new Promise((resolve) => {
                    codeResolve.current = resolve;
                });
            },
            onPassword: async () => {
                setStep('password');
                setIsLoading(false);
                // Wait for user to enter password
                return new Promise((resolve) => {
                    passwordResolve.current = resolve;
                });
            },
            onError: (err) => {
                setError(err.message);
                setIsLoading(false);
            },
        }).then(async (success) => {
            if (success) {
                // Load chats for selection
                setIsLoading(true);
                try {
                    const dialogList = await gramjsClient.getDialogs(50);
                    setChats(dialogList);
                    setStep('chat');
                } catch (err) {
                    setError(err instanceof Error ? err.message : 'Failed to load chats');
                }
                setIsLoading(false);
            }
        });
    };

    // Submit OTP code
    const handleCodeSubmit = () => {
        if (!phoneCode.trim()) {
            setError('Please enter the verification code');
            return;
        }
        setError(null);
        setIsLoading(true);
        codeResolve.current?.(phoneCode);
    };

    // Submit 2FA password
    const handlePasswordSubmit = () => {
        if (!password.trim()) {
            setError('Please enter your 2FA password');
            return;
        }
        setError(null);
        setIsLoading(true);
        passwordResolve.current?.(password);
    };

    // Select storage chat
    const handleChatSelect = (chat: ChatInfo) => {
        setSelectedChat(chat);
    };

    // Confirm chat selection
    const handleConfirmChat = () => {
        if (!selectedChat) return;

        gramjsClient.setStorageChat(selectedChat);
        const session = gramjsClient.saveSession();

        setStep('success');

        // Call success after brief animation
        setTimeout(() => {
            onSuccess(session, selectedChat);
        }, 1500);
    };

    // Get chat icon
    const getChatIcon = (chat: ChatInfo) => {
        switch (chat.type) {
            case 'saved': return <Save size={20} style={{ color: '#7c3aed' }} />;
            case 'channel': return <Megaphone size={20} style={{ color: '#3b82f6' }} />;
            case 'chat': return <Users size={20} style={{ color: '#22c55e' }} />;
            default: return <User size={20} style={{ color: '#f59e0b' }} />;
        }
    };

    if (!isOpen) return null;

    return (
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
                className="glass w-full max-w-md rounded-2xl overflow-hidden"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-4"
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}
                >
                    <div className="flex items-center gap-3">
                        {step !== 'phone' && step !== 'success' && (
                            <button
                                onClick={() => {
                                    if (step === 'code') setStep('phone');
                                    if (step === 'password') setStep('code');
                                    if (step === 'chat') setStep('code');
                                }}
                                className="btn-icon"
                            >
                                <ArrowLeft size={20} />
                            </button>
                        )}
                        <MessageSquare size={20} style={{ color: '#0088cc' }} />
                        <h2 className="text-lg font-semibold">
                            {step === 'phone' && 'Connect Telegram'}
                            {step === 'code' && 'Verification Code'}
                            {step === 'password' && 'Two-Factor Auth'}
                            {step === 'chat' && 'Select Storage'}
                            {step === 'success' && 'Connected!'}
                        </h2>
                    </div>
                    <button onClick={onClose} className="btn-icon">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    <AnimatePresence mode="wait">
                        {/* Step 1: Phone Number */}
                        {step === 'phone' && (
                            <motion.div
                                key="phone"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-4"
                            >
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    Enter your phone number to login with your Telegram account.
                                    No bot required!
                                </p>

                                <div>
                                    <label className="text-sm mb-1 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                        Phone Number
                                    </label>
                                    <div className="relative">
                                        <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'rgba(255,255,255,0.4)' }} />
                                        <input
                                            type="tel"
                                            value={phoneNumber}
                                            onChange={e => setPhoneNumber(e.target.value)}
                                            placeholder="+1234567890"
                                            className="input-glass pl-10 text-sm"
                                            autoFocus
                                            onKeyDown={e => e.key === 'Enter' && handlePhoneSubmit()}
                                        />
                                    </div>
                                    <p className="text-xs mt-1" style={{ color: 'rgba(255,255,255,0.4)' }}>
                                        Include country code (e.g., +1 for US, +84 for VN)
                                    </p>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}>
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handlePhoneSubmit}
                                    disabled={isLoading || !phoneNumber.trim()}
                                    className="btn-gradient w-full flex items-center justify-center gap-2"
                                    style={{ opacity: (isLoading || !phoneNumber.trim()) ? 0.5 : 1 }}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Connecting...
                                        </>
                                    ) : (
                                        'Send Code'
                                    )}
                                </button>
                            </motion.div>
                        )}

                        {/* Step 2: OTP Code */}
                        {step === 'code' && (
                            <motion.div
                                key="code"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-4"
                            >
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    We sent a code to your Telegram app. Enter it below.
                                </p>

                                <div>
                                    <label className="text-sm mb-1 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                        Verification Code
                                    </label>
                                    <div className="relative">
                                        <Key size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'rgba(255,255,255,0.4)' }} />
                                        <input
                                            type="text"
                                            value={phoneCode}
                                            onChange={e => setPhoneCode(e.target.value.replace(/\D/g, ''))}
                                            placeholder="12345"
                                            className="input-glass pl-10 text-sm text-center tracking-widest"
                                            maxLength={5}
                                            autoFocus
                                            onKeyDown={e => e.key === 'Enter' && handleCodeSubmit()}
                                        />
                                    </div>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}>
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handleCodeSubmit}
                                    disabled={isLoading || phoneCode.length < 5}
                                    className="btn-gradient w-full flex items-center justify-center gap-2"
                                    style={{ opacity: (isLoading || phoneCode.length < 5) ? 0.5 : 1 }}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Verifying...
                                        </>
                                    ) : (
                                        'Verify Code'
                                    )}
                                </button>
                            </motion.div>
                        )}

                        {/* Step 3: 2FA Password */}
                        {step === 'password' && (
                            <motion.div
                                key="password"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-4"
                            >
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    Your account has Two-Factor Authentication enabled.
                                    Please enter your password.
                                </p>

                                <div>
                                    <label className="text-sm mb-1 block" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                        2FA Password
                                    </label>
                                    <div className="relative">
                                        <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'rgba(255,255,255,0.4)' }} />
                                        <input
                                            type="password"
                                            value={password}
                                            onChange={e => setPassword(e.target.value)}
                                            placeholder="Your 2FA password"
                                            className="input-glass pl-10 text-sm"
                                            autoFocus
                                            onKeyDown={e => e.key === 'Enter' && handlePasswordSubmit()}
                                        />
                                    </div>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg text-sm" style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#f87171' }}>
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handlePasswordSubmit}
                                    disabled={isLoading || !password.trim()}
                                    className="btn-gradient w-full flex items-center justify-center gap-2"
                                    style={{ opacity: (isLoading || !password.trim()) ? 0.5 : 1 }}
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Verifying...
                                        </>
                                    ) : (
                                        'Continue'
                                    )}
                                </button>
                            </motion.div>
                        )}

                        {/* Step 4: Chat Selection */}
                        {step === 'chat' && (
                            <motion.div
                                key="chat"
                                initial={{ opacity: 0, x: 20 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -20 }}
                                className="space-y-4"
                            >
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    Choose where to store your files. "Saved Messages" is recommended.
                                </p>

                                <div className="max-h-64 overflow-y-auto space-y-2">
                                    {chats.map(chat => (
                                        <button
                                            key={chat.id}
                                            onClick={() => handleChatSelect(chat)}
                                            className="w-full flex items-center gap-3 p-3 rounded-xl transition-all"
                                            style={{
                                                background: selectedChat?.id === chat.id
                                                    ? 'rgba(124, 58, 237, 0.2)'
                                                    : 'rgba(255,255,255,0.05)',
                                                border: selectedChat?.id === chat.id
                                                    ? '1px solid rgba(124, 58, 237, 0.5)'
                                                    : '1px solid rgba(255,255,255,0.1)',
                                            }}
                                        >
                                            <div
                                                className="w-10 h-10 rounded-full flex items-center justify-center"
                                                style={{ background: 'rgba(255,255,255,0.1)' }}
                                            >
                                                {getChatIcon(chat)}
                                            </div>
                                            <div className="flex-1 text-left">
                                                <p className="font-medium text-sm">{chat.title}</p>
                                                <p className="text-xs" style={{ color: 'rgba(255,255,255,0.4)' }}>
                                                    {chat.type === 'saved' && 'Private storage'}
                                                    {chat.type === 'channel' && 'Channel'}
                                                    {chat.type === 'chat' && 'Group'}
                                                    {chat.type === 'user' && 'Private chat'}
                                                </p>
                                            </div>
                                            {selectedChat?.id === chat.id && (
                                                <CheckCircle2 size={20} style={{ color: '#7c3aed' }} />
                                            )}
                                        </button>
                                    ))}
                                </div>

                                <button
                                    onClick={handleConfirmChat}
                                    disabled={!selectedChat}
                                    className="btn-gradient w-full flex items-center justify-center gap-2"
                                    style={{ opacity: !selectedChat ? 0.5 : 1 }}
                                >
                                    Use This Chat
                                </button>
                            </motion.div>
                        )}

                        {/* Step 5: Success */}
                        {step === 'success' && (
                            <motion.div
                                key="success"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="text-center py-8"
                            >
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    transition={{ type: 'spring', delay: 0.2 }}
                                    className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4"
                                    style={{ background: 'rgba(34, 197, 94, 0.2)' }}
                                >
                                    <CheckCircle2 size={40} style={{ color: '#22c55e' }} />
                                </motion.div>
                                <h3 className="text-xl font-semibold mb-2">Connected!</h3>
                                <p className="text-sm" style={{ color: 'rgba(255,255,255,0.6)' }}>
                                    Your files will be stored in "{selectedChat?.title}"
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </motion.div>
    );
}

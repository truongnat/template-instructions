/**
 * Telegram Login Dialog Component - Updated with CSS Animations
 * @module components/dialogs/TelegramLoginDialog
 * 
 * Multi-step login flow: API Credentials → Phone → OTP → 2FA (if enabled) → Chat Picker
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
    X,
    Phone,
    Key,
    Lock,
    CheckCircle2,
    Loader2,
    ArrowLeft,
    Save,
    Users,
    User,
    Megaphone,
    HelpCircle,
    ChevronRight,
} from 'lucide-react';
import { gramjsClient, type ChatInfo } from '../../lib/telegram/gramjs-client';
import { useResponsive } from '../../hooks/useResponsive';

// ============================================================================
// TYPES
// ============================================================================

interface TelegramLoginDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (session: string, chat: ChatInfo) => void;
}

type Step = 'credentials' | 'phone' | 'code' | 'password' | 'chat' | 'success';

// ============================================================================
// COMPONENT
// ============================================================================

export function TelegramLoginDialog({ isOpen, onClose, onSuccess }: TelegramLoginDialogProps) {
    const [step, setStep] = useState<Step>('credentials');
    const [apiId, setApiId] = useState('');
    const [apiHash, setApiHash] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [phoneCode, setPhoneCode] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [chats, setChats] = useState<ChatInfo[]>([]);
    const [selectedChat, setSelectedChat] = useState<ChatInfo | null>(null);
    const [isExiting, setIsExiting] = useState(false);
    const [transitionDir, setTransitionDir] = useState<'next' | 'prev'>('next');
    const { isMobile } = useResponsive();

    // Refs for resolving promises
    const codeResolve = useRef<((value: string) => void) | null>(null);
    const passwordResolve = useRef<((value: string) => void) | null>(null);

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

    // Transition between steps
    const transitionToStep = (newStep: Step, direction: 'next' | 'prev' = 'next') => {
        setTransitionDir(direction);
        setStep(newStep);
    };

    // Reset state when dialog opens
    useEffect(() => {
        if (isOpen) {
            setStep('credentials');
            setApiId(localStorage.getItem('tg_api_id') || '');
            setApiHash(localStorage.getItem('tg_api_hash') || '');
            setPhoneNumber('');
            setPhoneCode('');
            setPassword('');
            setError(null);
            setIsLoading(false);
            setChats([]);
            setSelectedChat(null);
        }
    }, [isOpen]);

    // Submit API credentials
    const handleCredentialsSubmit = () => {
        if (!apiId.trim()) {
            setError('Please enter your API ID');
            return;
        }
        if (!apiHash.trim()) {
            setError('Please enter your API Hash');
            return;
        }

        const numericApiId = parseInt(apiId.trim(), 10);
        if (isNaN(numericApiId)) {
            setError('API ID must be a number');
            return;
        }

        setError(null);
        gramjsClient.setCredentials(numericApiId, apiHash.trim());
        localStorage.setItem('tg_api_id', apiId.trim());
        localStorage.setItem('tg_api_hash', apiHash.trim());
        transitionToStep('phone');
    };

    // Start login when phone is submitted
    const handlePhoneSubmit = async () => {
        if (!phoneNumber.trim()) {
            setError('Please enter your phone number');
            return;
        }

        setError(null);
        setIsLoading(true);

        gramjsClient.login({
            onPhoneNumber: async () => phoneNumber,
            onPhoneCode: async () => {
                transitionToStep('code');
                setIsLoading(false);
                return new Promise((resolve) => {
                    codeResolve.current = resolve;
                });
            },
            onPassword: async () => {
                transitionToStep('password');
                setIsLoading(false);
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
                setIsLoading(true);
                try {
                    const dialogList = await gramjsClient.getDialogs(50);
                    setChats(dialogList);
                    transitionToStep('chat');
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

        transitionToStep('success');
        setTimeout(() => {
            onSuccess(session, selectedChat);
        }, 1500);
    };

    // Get chat icon
    const getChatIcon = (chat: ChatInfo) => {
        switch (chat.type) {
            case 'saved': return <Save size={18} className="text-accent-purple" />;
            case 'channel': return <Megaphone size={18} className="text-accent-blue" />;
            case 'chat': return <Users size={18} className="text-green-500" />;
            default: return <User size={18} className="text-yellow-500" />;
        }
    };

    if (!isOpen && !isExiting) return null;

    return (
        <div
            className={`fixed inset-0 z-[100] flex items-center justify-center p-4 transition-all duration-300 ${isMobile ? 'items-end p-0' : ''} ${isExiting ? 'animate-fade-out' : 'animate-fade-in'
                }`}
            style={{ background: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(10px)' }}
            onClick={handleClose}
        >
            <div
                className={`glass w-full max-w-md overflow-hidden flex flex-col shadow-2xl safe-bottom ${isMobile ? 'h-[90vh] rounded-t-[2.5rem]' : 'max-h-[90vh] rounded-3xl'
                    } ${isExiting ? 'animate-slide-down-to-bottom' : 'animate-slide-up-from-bottom'}`}
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/10">
                    <div className="flex items-center gap-3">
                        {step !== 'credentials' && step !== 'success' && (
                            <button
                                onClick={() => {
                                    if (step === 'phone') transitionToStep('credentials', 'prev');
                                    if (step === 'code') transitionToStep('phone', 'prev');
                                    if (step === 'password') transitionToStep('code', 'prev');
                                    if (step === 'chat') transitionToStep('code', 'prev');
                                }}
                                className="btn-icon"
                            >
                                <ArrowLeft size={20} />
                            </button>
                        )}
                        <h2 className="text-lg font-bold">
                            {step === 'credentials' && 'API Settings'}
                            {step === 'phone' && 'Phone Login'}
                            {step === 'code' && 'Verification'}
                            {step === 'password' && 'Two-Factor Auth'}
                            {step === 'chat' && 'Storage Picker'}
                            {step === 'success' && 'Welcome!'}
                        </h2>
                    </div>
                    <button onClick={handleClose} className="btn-icon">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 scroll-container">
                    <div className={transitionDir === 'next' ? 'animate-slide-in-right' : 'animate-slide-in-left'} key={step}>
                        {/* Step: API Credentials */}
                        {step === 'credentials' && (
                            <div className="space-y-6">
                                <p className="text-sm text-white/50 leading-relaxed">
                                    To connect, you'll need an API ID and Hash from{' '}
                                    <a href="https://my.telegram.org/apps" target="_blank" rel="noreferrer" className="text-accent-blue underline flex items-center gap-1 mt-1">
                                        my.telegram.org <HelpCircle size={14} />
                                    </a>
                                </p>

                                <div className="space-y-4">
                                    <div>
                                        <label className="text-xs font-bold uppercase tracking-wider text-white/30 mb-2 block">API ID</label>
                                        <div className="relative">
                                            <Key size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20" />
                                            <input
                                                type="text"
                                                value={apiId}
                                                onChange={e => setApiId(e.target.value.replace(/\D/g, ''))}
                                                placeholder="12345678"
                                                className="input-glass pl-12 py-3.5"
                                                autoFocus
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="text-xs font-bold uppercase tracking-wider text-white/30 mb-2 block">API Hash</label>
                                        <div className="relative">
                                            <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20" />
                                            <input
                                                type="text"
                                                value={apiHash}
                                                onChange={e => setApiHash(e.target.value)}
                                                placeholder="32 characters..."
                                                className="input-glass pl-12 py-3.5 font-mono text-xs"
                                            />
                                        </div>
                                    </div>
                                </div>

                                {error && <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm animate-shake">{error}</div>}

                                <button
                                    onClick={handleCredentialsSubmit}
                                    disabled={!apiId.trim() || !apiHash.trim()}
                                    className="btn-gradient w-full py-4 flex items-center justify-center gap-2"
                                >
                                    Login with API <ChevronRight size={18} />
                                </button>
                            </div>
                        )}

                        {/* Step: Phone Number */}
                        {step === 'phone' && (
                            <div className="space-y-6">
                                <p className="text-sm text-white/50">Enter your phone number with country code.</p>
                                <div className="space-y-4">
                                    <div className="relative">
                                        <Phone size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20" />
                                        <input
                                            type="tel"
                                            value={phoneNumber}
                                            onChange={e => setPhoneNumber(e.target.value)}
                                            placeholder="+1 234..."
                                            className="input-glass pl-12 py-3.5"
                                            autoFocus
                                        />
                                    </div>
                                    <p className="text-[10px] text-white/30 italic">Example: +84 912345678</p>
                                </div>

                                {error && <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm">{error}</div>}

                                <button
                                    onClick={handlePhoneSubmit}
                                    disabled={isLoading || !phoneNumber.trim()}
                                    className="btn-gradient w-full py-4 flex items-center justify-center gap-2"
                                >
                                    {isLoading ? <Loader2 size={18} className="animate-spin" /> : 'Send Code'}
                                </button>
                            </div>
                        )}

                        {/* Step: OTP Code */}
                        {step === 'code' && (
                            <div className="space-y-6">
                                <div className="text-center py-4">
                                    <p className="text-white/60 mb-2">Verification Code</p>
                                    <p className="text-xs text-white/40">Check your Telegram app for the code</p>
                                </div>
                                <input
                                    type="text"
                                    value={phoneCode}
                                    onChange={e => setPhoneCode(e.target.value.replace(/\D/g, ''))}
                                    placeholder="•••••"
                                    className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-center text-3xl font-bold tracking-[0.5em] focus:border-accent-purple/50 focus:ring-4 focus:ring-accent-purple/10 outline-none transition-all"
                                    maxLength={5}
                                    autoFocus
                                />

                                {error && <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm">{error}</div>}

                                <button
                                    onClick={handleCodeSubmit}
                                    disabled={isLoading || phoneCode.length < 5}
                                    className="btn-gradient w-full py-4"
                                >
                                    {isLoading ? <Loader2 size={18} className="animate-spin mx-auto" /> : 'Verify Account'}
                                </button>
                            </div>
                        )}

                        {/* Step: 2FA Password */}
                        {step === 'password' && (
                            <div className="space-y-6">
                                <div className="flex justify-center mb-6">
                                    <div className="w-20 h-20 rounded-2xl bg-accent-purple/10 flex items-center justify-center">
                                        <Lock size={32} className="text-accent-purple" />
                                    </div>
                                </div>
                                <p className="text-sm text-white/50 text-center">Your account is protected with 2FA.</p>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    placeholder="Enter your cloud password"
                                    className="input-glass py-4 px-6 text-center"
                                    autoFocus
                                />

                                {error && <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm text-center">{error}</div>}

                                <button
                                    onClick={handlePasswordSubmit}
                                    disabled={isLoading || !password.trim()}
                                    className="btn-gradient w-full py-4"
                                >
                                    {isLoading ? <Loader2 size={18} className="animate-spin mx-auto" /> : 'Confirm Password'}
                                </button>
                            </div>
                        )}

                        {/* Step: Chat Selection */}
                        {step === 'chat' && (
                            <div className="space-y-6">
                                <p className="text-xs text-white/40 uppercase font-black">Available Storage Destinations</p>
                                <div className="space-y-2 max-h-[40vh] overflow-y-auto scroll-container pr-2">
                                    {chats.map(chat => (
                                        <button
                                            key={chat.id}
                                            onClick={() => handleChatSelect(chat)}
                                            className={`w-full flex items-center gap-4 p-4 rounded-2xl border transition-all ${selectedChat?.id === chat.id
                                                ? 'bg-accent-purple/10 border-accent-purple/50'
                                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center shrink-0">
                                                {getChatIcon(chat)}
                                            </div>
                                            <div className="flex-1 text-left min-w-0">
                                                <p className="font-bold text-sm truncate">{chat.title}</p>
                                                <p className="text-[10px] text-white/30 uppercase tracking-tighter">{chat.type}</p>
                                            </div>
                                            {selectedChat?.id === chat.id && <CheckCircle2 size={20} className="text-accent-purple" />}
                                        </button>
                                    ))}
                                </div>

                                <button
                                    onClick={handleConfirmChat}
                                    disabled={!selectedChat || isLoading}
                                    className="btn-gradient w-full py-4"
                                >
                                    Finish Setup
                                </button>
                            </div>
                        )}

                        {/* Step: Success */}
                        {step === 'success' && (
                            <div className="text-center py-10 animate-scale-in">
                                <div className="w-24 h-24 rounded-full bg-green-500/10 flex items-center justify-center mx-auto mb-6 border border-green-500/20">
                                    <CheckCircle2 size={48} className="text-green-500" />
                                </div>
                                <h3 className="text-2xl font-black text-white mb-2">You're In!</h3>
                                <p className="text-white/40 text-sm">Synchronizing your cloud vault...</p>
                                <div className="mt-8 flex justify-center">
                                    <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-green-500 animate-shimmer w-1/2"></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

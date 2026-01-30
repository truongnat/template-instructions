/**
 * Onboarding Page - New User Setup Flow with CSS Animations
 * @module pages/Onboarding
 * 
 * Flow: API Credentials → Phone → OTP → 2FA (if enabled) → Chat Selection → Success
 * Replaces Framer Motion with pure CSS animations for better performance
 */

import { useState, useEffect, useRef } from 'react';
import {
    Phone,
    Key,
    Lock,
    MessageSquare,
    CheckCircle2,
    Loader2,
    ArrowRight,
    Save,
    Users,
    User,
    Megaphone,
    HelpCircle,
} from 'lucide-react';
import { gramjsClient, type ChatInfo } from '../lib/telegram/gramjs-client';
import { useSettingsStore } from '../store/settings';
import { useResponsive } from '../hooks/useResponsive';

// ============================================================================
// TYPES
// ============================================================================

type Step = 'credentials' | 'phone' | 'code' | 'password' | 'chat' | 'success';

// ============================================================================
// COMPONENT
// ============================================================================

export function OnboardingPage() {
    const [step, setStep] = useState<Step>('credentials');
    const [animatingOut, setAnimatingOut] = useState(false);

    // Form states
    const [apiId, setApiId] = useState('');
    const [apiHash, setApiHash] = useState('');
    const [phoneNumber, setPhoneNumber] = useState('');
    const [phoneCode, setPhoneCode] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [chats, setChats] = useState<ChatInfo[]>([]);
    const [selectedChat, setSelectedChat] = useState<ChatInfo | null>(null);

    const { connectGramJS } = useSettingsStore();
    const { isMobile } = useResponsive();

    // Refs for resolving promises
    const codeResolve = useRef<((value: string) => void) | null>(null);
    const passwordResolve = useRef<((value: string) => void) | null>(null);

    // Smooth step transitions with CSS animations
    const transitionToStep = (newStep: Step) => {
        setAnimatingOut(true);
        setTimeout(() => {
            setStep(newStep);
            setAnimatingOut(false);
        }, 300); // Match CSS animation duration
    };

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

        // Set credentials on the client
        gramjsClient.setCredentials(numericApiId, apiHash.trim());

        // Save to localStorage
        localStorage.setItem('tg_api_id', apiId.trim());
        localStorage.setItem('tg_api_hash', apiHash.trim());

        // Proceed to phone step
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

        // Start the login flow
        gramjsClient.login({
            onPhoneNumber: async () => {
                return phoneNumber;
            },
            onPhoneCode: async () => {
                transitionToStep('code');
                setIsLoading(false);
                // Wait for user to enter code
                return new Promise((resolve) => {
                    codeResolve.current = resolve;
                });
            },
            onPassword: async () => {
                transitionToStep('password');
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
    const handleConfirmChat = async () => {
        if (!selectedChat) return;

        setIsLoading(true);
        gramjsClient.setStorageChat(selectedChat);
        const session = gramjsClient.saveSession();

        // Save to settings store
        const success = await connectGramJS(session, selectedChat);

        if (success) {
            transitionToStep('success');
            // Reload page after brief animation
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            setError('Failed to save session');
            setIsLoading(false);
        }
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

    // Load saved credentials on mount
    useEffect(() => {
        const savedApiId = localStorage.getItem('tg_api_id');
        const savedApiHash = localStorage.getItem('tg_api_hash');
        if (savedApiId) setApiId(savedApiId);
        if (savedApiHash) setApiHash(savedApiHash);
    }, []);

    const containerClass = isMobile ? 'min-h-screen flex items-center justify-center p-4' : 'min-h-screen flex items-center justify-center p-4';

    return (
        <div className={containerClass}>
            <div className={`w-full max-w-lg ${animatingOut ? 'animate-fade-out' : 'animate-fade-in'}`}>
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center mx-auto mb-4 animate-scale-in">
                        <MessageSquare size={40} />
                    </div>
                    <h1 className="text-3xl font-bold gradient-text mb-2">TeleCloud</h1>
                    <p className="text-white/60">Unlimited file storage powered by Telegram</p>
                </div>

                {/* Card */}
                <div className={`glass p-6 rounded-2xl ${isMobile ? 'max-h-[70vh] overflow-y-auto' : ''}`}>
                    {/* Step: API Credentials */}
                    {step === 'credentials' && (
                        <div className={animatingOut ? 'animate-slide-out-left' : 'animate-slide-in-right'} key="credentials">
                            <div className="space-y-4">
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">API Credentials</h2>
                                    <p className="text-white/60 text-sm">
                                        Get your credentials from{' '}
                                        <a
                                            href="https://my.telegram.org/apps"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-accent-purple hover:underline inline-flex items-center gap-1"
                                        >
                                            my.telegram.org
                                            <HelpCircle size={14} />
                                        </a>
                                    </p>
                                </div>

                                <div>
                                    <label className="text-sm mb-1 block text-white/60">API ID</label>
                                    <div className="relative">
                                        <Key size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                                        <input
                                            type="text"
                                            value={apiId}
                                            onChange={e => setApiId(e.target.value.replace(/\D/g, ''))}
                                            placeholder="12345678"
                                            className="input-glass pl-10 text-sm"
                                            autoFocus
                                            onKeyDown={e => e.key === 'Enter' && handleCredentialsSubmit()}
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="text-sm mb-1 block text-white/60">API Hash</label>
                                    <div className="relative">
                                        <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                                        <input
                                            type="text"
                                            value={apiHash}
                                            onChange={e => setApiHash(e.target.value)}
                                            placeholder="0123456789abcdef0123456789abcdef"
                                            className="input-glass pl-10 text-sm font-mono"
                                            onKeyDown={e => e.key === 'Enter' && handleCredentialsSubmit()}
                                        />
                                    </div>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg text-sm bg-red-500/10 text-red-400 animate-slide-down">
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handleCredentialsSubmit}
                                    disabled={!apiId.trim() || !apiHash.trim()}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Continue <ArrowRight size={18} />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step: Phone Number */}
                    {step === 'phone' && (
                        <div className={animatingOut ? 'animate-slide-out-left' : 'animate-slide-in-right'} key="phone">
                            <div className="space-y-4">
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">Phone Number</h2>
                                    <p className="text-white/60 text-sm">
                                        Enter your phone number to receive a verification code
                                    </p>
                                </div>

                                <div>
                                    <label className="text-sm mb-1 block text-white/60">Phone Number</label>
                                    <div className="relative">
                                        <Phone size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
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
                                    <p className="text-xs mt-1 text-white/40">
                                        Include country code (e.g., +1 for US, +84 for VN)
                                    </p>
                                </div>

                                {error && (
                                    <div className="p-3 rounded-lg text-sm bg-red-500/10 text-red-400 animate-slide-down">
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handlePhoneSubmit}
                                    disabled={isLoading || !phoneNumber.trim()}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Sending Code...
                                        </>
                                    ) : (
                                        <>
                                            Send Code <ArrowRight size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step: OTP Code */}
                    {step === 'code' && (
                        <div className={animatingOut ? 'animate-slide-out-left' : 'animate-slide-in-right'} key="code">
                            <div className="space-y-4">
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">Verification Code</h2>
                                    <p className="text-white/60 text-sm">
                                        We sent a code to your Telegram app
                                    </p>
                                </div>

                                <div>
                                    <label className="text-sm mb-1 block text-white/60">Code</label>
                                    <div className="relative">
                                        <Key size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
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
                                    <div className="p-3 rounded-lg text-sm bg-red-500/10 text-red-400 animate-slide-down">
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handleCodeSubmit}
                                    disabled={isLoading || phoneCode.length < 5}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Verifying...
                                        </>
                                    ) : (
                                        <>
                                            Verify <ArrowRight size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step: 2FA Password */}
                    {step === 'password' && (
                        <div className={animatingOut ? 'animate-slide-out-left' : 'animate-slide-in-right'} key="password">
                            <div className="space-y-4">
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">Two-Factor Auth</h2>
                                    <p className="text-white/60 text-sm">
                                        Your account has 2FA enabled. Please enter your password.
                                    </p>
                                </div>

                                <div>
                                    <label className="text-sm mb-1 block text-white/60">Password</label>
                                    <div className="relative">
                                        <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
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
                                    <div className="p-3 rounded-lg text-sm bg-red-500/10 text-red-400 animate-slide-down">
                                        {error}
                                    </div>
                                )}

                                <button
                                    onClick={handlePasswordSubmit}
                                    disabled={isLoading || !password.trim()}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Verifying...
                                        </>
                                    ) : (
                                        <>
                                            Continue <ArrowRight size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step: Chat Selection */}
                    {step === 'chat' && (
                        <div className={animatingOut ? 'animate-slide-out-left' : 'animate-slide-in-right'} key="chat">
                            <div className="space-y-4">
                                <div className="text-center">
                                    <h2 className="text-xl font-semibold mb-2">Select Storage Chat</h2>
                                    <p className="text-white/60 text-sm">
                                        Choose where to store your files. "Saved Messages" is recommended.
                                    </p>
                                </div>

                                <div className="max-h-64 overflow-y-auto space-y-2 scrollbar-hide">
                                    {chats.map(chat => (
                                        <button
                                            key={chat.id}
                                            onClick={() => handleChatSelect(chat)}
                                            className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${selectedChat?.id === chat.id
                                                ? 'bg-accent-purple/20 border border-accent-purple/50'
                                                : 'bg-white/5 border border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className="w-10 h-10 rounded-full flex items-center justify-center bg-white/10">
                                                {getChatIcon(chat)}
                                            </div>
                                            <div className="flex-1 text-left">
                                                <p className="font-medium text-sm">{chat.title}</p>
                                                <p className="text-xs text-white/40">
                                                    {chat.type === 'saved' && 'Private storage'}
                                                    {chat.type === 'channel' && 'Channel'}
                                                    {chat.type === 'chat' && 'Group'}
                                                    {chat.type === 'user' && 'Private chat'}
                                                </p>
                                            </div>
                                            {selectedChat?.id === chat.id && (
                                                <CheckCircle2 size={20} className="text-accent-purple" />
                                            )}
                                        </button>
                                    ))}
                                </div>

                                <button
                                    onClick={handleConfirmChat}
                                    disabled={!selectedChat || isLoading}
                                    className="btn-gradient w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? (
                                        <>
                                            <Loader2 size={18} className="animate-spin" />
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            Use This Chat <ArrowRight size={18} />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Step: Success */}
                    {step === 'success' && (
                        <div className="text-center py-8 animate-scale-in" key="success">
                            <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4 animate-scale-in">
                                <CheckCircle2 size={40} className="text-green-400" />
                            </div>
                            <h2 className="text-xl font-semibold mb-2">You're all set!</h2>
                            <p className="text-white/60 text-sm mb-4">
                                Your files will be stored in "{selectedChat?.title}"
                            </p>
                            <div className="spinner mx-auto"></div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <p className="text-center text-xs text-white/40 mt-6">
                    Your credentials are stored locally and never sent to any server except Telegram.
                </p>
            </div>
        </div>
    );
}

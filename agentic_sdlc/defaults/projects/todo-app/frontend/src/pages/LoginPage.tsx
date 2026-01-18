import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, Lock, User, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export default function LoginPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const { login, signup, isLoading } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isSignup) {
        await signup(email, password, name);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 overflow-hidden relative">
      {/* Background Orbs */}
      <div className="absolute top-1/4 -left-20 w-80 h-80 bg-sky-500/20 rounded-full blur-[100px] animate-pulse" />
      <div className="absolute bottom-1/4 -right-20 w-80 h-80 bg-purple-500/20 rounded-full blur-[100px] animate-pulse delay-700" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full z-10"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="w-16 h-16 bg-sky-500/20 text-sky-400 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-sky-500/20"
          >
            <Zap size={32} />
          </motion.div>
          <h1 className="text-4xl font-black text-white tracking-tight mb-2">
            Focus Hub
          </h1>
          <p className="text-slate-400 font-medium">
            {isSignup ? 'Start your journey to peak productivity.' : 'Welcome back to your command center.'}
          </p>
        </div>

        <motion.div
          layout
          className="glass-card !p-8 border-white/5 shadow-2xl"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="bg-rose-500/10 border border-rose-500/20 text-rose-500 p-3 rounded-xl text-sm flex items-center gap-2"
                >
                  <ShieldCheck size={16} />
                  {error}
                </motion.div>
              )}
            </AnimatePresence>

            {isSignup && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 ml-1">
                  Full Name
                </label>
                <div className="relative group">
                  <User size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-sky-400 transition-colors" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="input-premium w-full pl-11"
                    placeholder="Enter your name"
                  />
                </div>
              </motion.div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-1.5 ml-1">
                Email Address
              </label>
              <div className="relative group">
                <Mail size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-sky-400 transition-colors" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-premium w-full pl-11"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-1.5 ml-1">
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest">
                  Secure Password
                </label>
                {!isSignup && (
                  <button type="button" className="text-[10px] text-sky-400 hover:text-sky-300 font-bold uppercase tracking-widest">
                    Forgot?
                  </button>
                )}
              </div>
              <div className="relative group">
                <Lock size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-sky-400 transition-colors" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-premium w-full pl-11"
                  placeholder="••••••••"
                />
              </div>
              {isSignup && (
                <p className="mt-2 text-[10px] text-slate-500 flex items-center gap-1">
                  <ShieldCheck size={10} />
                  Use at least 8 characters with numbers & symbols.
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-premium py-3 flex items-center justify-center gap-2 mt-4"
            >
              <span>{isLoading ? 'Syncing...' : isSignup ? 'Initialize Account' : 'Access Hub'}</span>
              {!isLoading && <ArrowRight size={18} />}
            </button>

            <div className="text-center pt-4">
              <button
                type="button"
                onClick={() => {
                  setIsSignup(!isSignup);
                  setError('');
                }}
                className="text-sm font-semibold text-slate-500 hover:text-white transition-colors"
              >
                {isSignup ? "Already have an account? Login" : "Don't have an account? Sign Up"}
              </button>
            </div>
          </form>
        </motion.div>
      </motion.div>
    </div>
  );
}


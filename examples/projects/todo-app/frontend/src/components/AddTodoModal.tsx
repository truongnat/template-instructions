import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Sparkles, AlertCircle } from 'lucide-react';
import { useTodoStore } from '../store/todoStore';

interface Props {
  onClose: () => void;
}

export default function AddTodoModal({ onClose }: Props) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { createTodo } = useTodoStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting) return;

    setError('');

    if (!title.trim()) {
      setError('A title is required to focus your task.');
      return;
    }

    try {
      setIsSubmitting(true);
      await createTodo(title, description || undefined);
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="glass-card max-w-md w-full !p-0 overflow-hidden relative"
      >
        {/* Glow Header */}
        <div className="h-1.5 w-full bg-gradient-to-r from-sky-500 via-purple-500 to-sky-500 animate-gradient-x" />

        <div className="p-8">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-sky-500/20 text-sky-400 rounded-lg">
                <Sparkles size={20} />
              </div>
              <h2 className="text-xl font-bold text-white">New Objective</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-500 hover:text-white hover:bg-white/5 rounded-lg transition-all"
            >
              <X size={20} />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="bg-rose-500/10 border border-rose-500/20 text-rose-500 p-3 rounded-xl text-sm flex items-center gap-2"
              >
                <AlertCircle size={16} />
                {error}
              </motion.div>
            )}

            <div>
              <label htmlFor="title" className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">
                Objective Title
              </label>
              <input
                id="title"
                type="text"
                autoFocus
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="input-premium w-full text-lg"
                placeholder="What needs to be done?"
                maxLength={200}
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">
                Context (Optional)
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input-premium w-full !py-3 min-h-[100px] resize-none"
                placeholder="Add details, links, or notes..."
                maxLength={1000}
              />
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-3 text-slate-400 font-medium hover:text-white transition-colors"
              >
                Discard
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-[2] btn-premium"
              >
                {isSubmitting ? 'Syncing...' : 'Establish Objective'}
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  );
}


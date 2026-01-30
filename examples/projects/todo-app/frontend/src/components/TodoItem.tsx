import { useState } from 'react';
import { motion } from 'framer-motion';
import { Edit2, Trash2, CheckCircle2, Circle, Calendar, AlertCircle } from 'lucide-react';
import { useTodoStore } from '../store/todoStore';
import { Todo } from '../types';

interface Props {
  todo: Todo;
  onEdit: (todo: Todo) => void;
}

export default function TodoItem({ todo, onEdit }: Props) {
  const { toggleTodo, deleteTodo } = useTodoStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const isCompleted = todo.status === 'completed';

  const handleDelete = async () => {
    await deleteTodo(todo.id);
    setShowDeleteConfirm(false);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
      className={`glass-card p-5 group flex flex-col gap-4 ${isCompleted ? 'opacity-70 grayscale-[0.3]' : ''
        }`}
    >
      <div className="flex items-start gap-4">
        {/* Custom Checkbox */}
        <button
          onClick={() => toggleTodo(todo.id)}
          className={`mt-1 transition-all duration-300 ${isCompleted ? 'text-sky-500' : 'text-slate-600 group-hover:text-slate-400'
            }`}
        >
          {isCompleted ? <CheckCircle2 size={22} /> : <Circle size={22} />}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-semibold transition-all duration-300 ${isCompleted ? 'line-through text-slate-500' : 'text-slate-100'
              }`}
          >
            {todo.title}
          </h3>
          {todo.description && (
            <p
              className={`mt-1 text-sm leading-relaxed ${isCompleted ? 'text-slate-500' : 'text-slate-400'
                }`}
            >
              {todo.description}
            </p>
          )}

          <div className="mt-4 flex items-center gap-4 text-[11px] font-medium uppercase tracking-wider text-slate-500">
            <span className="flex items-center gap-1.5">
              <Calendar size={12} />
              {new Date(todo.createdAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            </span>
            <span className={`px-2 py-0.5 rounded-full border ${isCompleted
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
                : 'bg-amber-500/10 border-amber-500/20 text-amber-500'
              }`}>
              {todo.status}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(todo)}
            className="p-2 text-slate-500 hover:text-white hover:bg-white/5 rounded-lg transition-all"
            title="Edit Task"
          >
            <Edit2 size={16} />
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="p-2 text-slate-500 hover:text-rose-500 hover:bg-rose-500/10 rounded-lg transition-all"
            title="Delete Task"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Delete Confirmation Overlay inside card */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="mt-2 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center justify-between animate-in fade-in slide-in-from-top-1"
          >
            <div className="flex items-center gap-2 text-sm text-rose-500">
              <AlertCircle size={16} />
              <span>Are you sure?</span>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="text-xs font-semibold text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-3 py-1.5 bg-rose-500 text-white text-xs font-bold rounded-lg hover:bg-rose-600 transition-colors shadow-lg shadow-rose-500/20"
              >
                Delete
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

import { AnimatePresence } from 'framer-motion';


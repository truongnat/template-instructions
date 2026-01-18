import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, ClipboardList } from 'lucide-react';
import { useTodoStore } from '../store/todoStore';
import TodoItem from './TodoItem';
import { Todo } from '../types';

interface Props {
  onEdit: (todo: Todo) => void;
}

export default function TodoList({ onEdit }: Props) {
  const { todos, isLoading, error } = useTodoStore();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-500">
        <Loader2 className="animate-spin mb-4" size={32} />
        <p className="text-lg">Loading your workflow...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-2xl backdrop-blur-md">
        <p className="font-medium text-center">Error: {error}</p>
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex flex-col items-center justify-center py-20 text-slate-600 glass-card"
      >
        <ClipboardList size={48} className="mb-4 opacity-20" />
        <p className="text-xl font-medium text-slate-400">No tasks on the horizon</p>
        <p className="text-sm">Create your first todo to get started.</p>
      </motion.div>
    );
  }

  return (
    <div className="grid gap-4">
      <AnimatePresence mode="popLayout" initial={false}>
        {todos.map((todo) => (
          <TodoItem key={todo.id} todo={todo} onEdit={onEdit} />
        ))}
      </AnimatePresence>
    </div>
  );
}


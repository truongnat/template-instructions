import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LogOut, Plus, Filter, CheckCircle2, Circle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useTodoStore } from '../store/todoStore';
import TodoList from '../components/TodoList';
import AddTodoModal from '../components/AddTodoModal';
import EditTodoModal from '../components/EditTodoModal';
import { Todo } from '../types';

export default function TodoPage() {
  const { user, logout } = useAuthStore();
  const { fetchTodos, filter, setFilter } = useTodoStore();
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return (
    <div className="min-h-screen">
      {/* Header */}
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="sticky top-0 z-30 w-full glass border-b border-white/5"
      >
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/20 flex items-center justify-center text-sky-400">
              <CheckCircle2 size={24} />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
              Focus Hub
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1.5 glass rounded-xl text-sm border-white/5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-slate-400">{user?.email}</span>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-colors"
              title="Logout"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="flex flex-col gap-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between"
          >
            <div>
              <h2 className="text-3xl font-bold text-white mb-1">Your Workflow</h2>
              <p className="text-slate-500">Stay organized and focused on your goals.</p>
            </div>

            <div className="flex items-center gap-3">
              <div className="relative group">
                <Filter size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-hover:text-sky-400 transition-colors" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as any)}
                  className="pl-10 pr-4 py-2 bg-slate-800/50 border border-white/5 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/30 transition-all appearance-none text-slate-300"
                >
                  <option value="all">All Tasks</option>
                  <option value="pending">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <button
                onClick={() => setShowAddModal(true)}
                className="btn-premium flex items-center gap-2"
              >
                <Plus size={18} />
                <span>Create Task</span>
              </button>
            </div>
          </motion.div>

          <TodoList onEdit={setEditingTodo} />
        </div>
      </main>

      {/* Modals */}
      <AnimatePresence>
        {showAddModal && (
          <AddTodoModal onClose={() => setShowAddModal(false)} />
        )}
        {editingTodo && (
          <EditTodoModal todo={editingTodo} onClose={() => setEditingTodo(null)} />
        )}
      </AnimatePresence>
    </div>
  );
}


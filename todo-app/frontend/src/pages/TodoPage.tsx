import { useEffect, useState } from 'react';
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">📝 Todo App</h1>
          <div className="flex items-center gap-4">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-primary focus:border-primary"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
            <button
              onClick={() => setShowAddModal(true)}
              className="px-4 py-2 bg-primary text-white rounded-md hover:bg-blue-600 text-sm font-medium"
            >
              + Add Todo
            </button>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={logout}
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <TodoList onEdit={setEditingTodo} />
      </main>

      {/* Modals */}
      {showAddModal && <AddTodoModal onClose={() => setShowAddModal(false)} />}
      {editingTodo && (
        <EditTodoModal todo={editingTodo} onClose={() => setEditingTodo(null)} />
      )}
    </div>
  );
}

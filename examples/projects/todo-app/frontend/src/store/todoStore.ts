import { create } from 'zustand';
import { Todo } from '../types';
import { api } from '../services/api';

interface TodoState {
  todos: Todo[];
  filter: 'all' | 'pending' | 'completed';
  isLoading: boolean;
  error: string | null;
  fetchTodos: () => Promise<void>;
  createTodo: (title: string, description?: string) => Promise<void>;
  updateTodo: (id: string, data: Partial<Todo>) => Promise<void>;
  deleteTodo: (id: string) => Promise<void>;
  toggleTodo: (id: string) => Promise<void>;
  setFilter: (filter: 'all' | 'pending' | 'completed') => void;
}

export const useTodoStore = create<TodoState>((set, get) => ({
  todos: [],
  filter: 'all',
  isLoading: false,
  error: null,

  fetchTodos: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getTodos(get().filter);
      set({ todos: data.todos, isLoading: false });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  createTodo: async (title, description) => {
    try {
      const todo = await api.createTodo(title, description);
      set((state) => ({ todos: [todo, ...state.todos] }));
    } catch (error: any) {
      set({ error: error.message });
      throw error;
    }
  },

  updateTodo: async (id, data) => {
    try {
      const updated = await api.updateTodo(id, data);
      set((state) => ({
        todos: state.todos.map((t) => (t.id === id ? updated : t)),
      }));
    } catch (error: any) {
      set({ error: error.message });
      throw error;
    }
  },

  deleteTodo: async (id) => {
    try {
      await api.deleteTodo(id);
      set((state) => ({
        todos: state.todos.filter((t) => t.id !== id),
      }));
    } catch (error: any) {
      set({ error: error.message });
      throw error;
    }
  },

  toggleTodo: async (id) => {
    const todo = get().todos.find((t) => t.id === id);
    if (!todo) return;

    const newStatus = todo.status === 'pending' ? 'completed' : 'pending';
    await get().updateTodo(id, { status: newStatus });
  },

  setFilter: (filter) => {
    set({ filter });
    get().fetchTodos();
  },
}));

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTodoStore } from '../todoStore';
import type { Todo } from '../../types';

// Mock API
vi.mock('../../services/api', () => ({
  api: {
    getTodos: vi.fn(),
    createTodo: vi.fn(),
    updateTodo: vi.fn(),
    deleteTodo: vi.fn(),
  },
}));

describe('TodoStore', () => {
  beforeEach(() => {
    // Reset store state
    useTodoStore.setState({
      todos: [],
      filter: 'all',
      isLoading: false,
      error: null,
    });
  });

  it('should initialize with empty todos', () => {
    const state = useTodoStore.getState();
    expect(state.todos).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should set filter', () => {
    useTodoStore.getState().setFilter('completed');
    const state = useTodoStore.getState();
    expect(state.filter).toBe('completed');
  });

  it('should handle loading state', () => {
    useTodoStore.setState({ isLoading: true });
    expect(useTodoStore.getState().isLoading).toBe(true);
  });

  it('should handle error state', () => {
    const error = 'Something went wrong';
    useTodoStore.setState({ error });
    expect(useTodoStore.getState().error).toBe(error);
  });

  it('should update todos list', () => {
    const mockTodos: Todo[] = [
      {
        id: '1',
        title: 'Test Todo',
        description: 'Description',
        status: 'pending',
        userId: 'user-1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    useTodoStore.setState({ todos: mockTodos });
    expect(useTodoStore.getState().todos).toEqual(mockTodos);
  });
});

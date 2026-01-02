import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import TodoList from '../TodoList';
import type { Todo } from '../../types';

// Mock the store
vi.mock('../../store/todoStore', () => ({
  useTodoStore: vi.fn(() => ({
    todos: [],
    isLoading: false,
    error: null,
  })),
}));

// Mock TodoItem component
vi.mock('../TodoItem', () => ({
  default: ({ todo }: { todo: Todo }) => <div data-testid="todo-item">{todo.title}</div>,
}));

describe('TodoList', () => {
  const mockOnEdit = vi.fn();

  it('should render loading state', () => {
    const { useTodoStore } = require('../../store/todoStore');
    useTodoStore.mockReturnValue({
      todos: [],
      isLoading: true,
      error: null,
    });

    render(<TodoList onEdit={mockOnEdit} />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should render error state', () => {
    const { useTodoStore } = require('../../store/todoStore');
    useTodoStore.mockReturnValue({
      todos: [],
      isLoading: false,
      error: 'Failed to load todos',
    });

    render(<TodoList onEdit={mockOnEdit} />);
    expect(screen.getByText(/error/i)).toBeInTheDocument();
  });

  it('should render empty state when no todos', () => {
    const { useTodoStore } = require('../../store/todoStore');
    useTodoStore.mockReturnValue({
      todos: [],
      isLoading: false,
      error: null,
    });

    render(<TodoList onEdit={mockOnEdit} />);
    expect(screen.getByText(/no todos yet/i)).toBeInTheDocument();
  });

  it('should render todos list', () => {
    const mockTodos: Todo[] = [
      {
        id: '1',
        title: 'Todo 1',
        description: 'Description 1',
        status: 'pending',
        userId: 'user-1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: '2',
        title: 'Todo 2',
        description: 'Description 2',
        status: 'completed',
        userId: 'user-1',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    const { useTodoStore } = require('../../store/todoStore');
    useTodoStore.mockReturnValue({
      todos: mockTodos,
      isLoading: false,
      error: null,
    });

    render(<TodoList onEdit={mockOnEdit} />);
    expect(screen.getAllByTestId('todo-item')).toHaveLength(2);
  });
});

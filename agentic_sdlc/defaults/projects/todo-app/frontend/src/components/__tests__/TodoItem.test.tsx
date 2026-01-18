import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TodoItem from '../TodoItem';
import type { Todo } from '../../types';

// Mock the store
const mockToggleTodo = vi.fn();
const mockDeleteTodo = vi.fn();

vi.mock('../../store/todoStore', () => ({
  useTodoStore: () => ({
    toggleTodo: mockToggleTodo,
    deleteTodo: mockDeleteTodo,
  }),
}));

describe('TodoItem', () => {
  const mockTodo: Todo = {
    id: '1',
    title: 'Test Todo',
    description: 'Test Description',
    status: 'pending',
    userId: 'user-1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const mockOnEdit = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render todo item with title and description', () => {
    render(<TodoItem todo={mockTodo} onEdit={mockOnEdit} />);

    expect(screen.getByText('Test Todo')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('should call toggleTodo when checkbox is clicked', () => {
    render(<TodoItem todo={mockTodo} onEdit={mockOnEdit} />);

    const checkbox = screen.getByRole('checkbox');
    fireEvent.click(checkbox);

    expect(mockToggleTodo).toHaveBeenCalledWith('1');
  });

  it('should call onEdit when edit button is clicked', () => {
    render(<TodoItem todo={mockTodo} onEdit={mockOnEdit} />);

    const editButton = screen.getByTitle('Edit');
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(mockTodo);
  });

  it('should show delete confirmation when delete button is clicked', () => {
    render(<TodoItem todo={mockTodo} onEdit={mockOnEdit} />);

    const deleteButton = screen.getByTitle('Delete');
    fireEvent.click(deleteButton);

    expect(screen.getByText(/delete this todo/i)).toBeInTheDocument();
  });

  it('should call deleteTodo when confirming delete', async () => {
    render(<TodoItem todo={mockTodo} onEdit={mockOnEdit} />);

    // Click delete button
    const deleteButton = screen.getByTitle('Delete');
    fireEvent.click(deleteButton);

    // Confirm delete
    const confirmButton = screen.getByText('Delete');
    fireEvent.click(confirmButton);

    expect(mockDeleteTodo).toHaveBeenCalledWith('1');
  });

  it('should show completed styling when todo is completed', () => {
    const completedTodo = { ...mockTodo, status: 'completed' as const };
    render(<TodoItem todo={completedTodo} onEdit={mockOnEdit} />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).toBeChecked();
  });
});

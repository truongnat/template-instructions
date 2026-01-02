import * as todoService from '../services/todo.service';
import prisma from '../models/prisma';

jest.mock('../models/prisma', () => ({
  __esModule: true,
  default: {
    todo: {
      findMany: jest.fn(),
      findUnique: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn(),
    },
  },
}));

describe('TodoService', () => {
  const mockUserId = 'user-123';
  const mockTodo = {
    id: 'todo-1',
    title: 'Test Todo',
    description: 'Test Description',
    status: 'pending',
    userId: mockUserId,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getTodos', () => {
    it('should return all todos for a user', async () => {
      (prisma.todo.findMany as jest.Mock).mockResolvedValue([mockTodo]);

      const result = await todoService.getTodos(mockUserId, {});

      expect(result.todos).toHaveLength(1);
      expect(result.todos[0]).toEqual(mockTodo);
      expect(result.count).toBe(1);
    });

    it('should return empty array when no todos exist', async () => {
      (prisma.todo.findMany as jest.Mock).mockResolvedValue([]);

      const result = await todoService.getTodos(mockUserId, {});

      expect(result.todos).toHaveLength(0);
      expect(result.count).toBe(0);
    });

    it('should filter by status', async () => {
      (prisma.todo.findMany as jest.Mock).mockResolvedValue([mockTodo]);

      await todoService.getTodos(mockUserId, { status: 'pending' });

      expect(prisma.todo.findMany).toHaveBeenCalledWith({
        where: { userId: mockUserId, status: 'pending' },
        orderBy: { createdAt: 'desc' },
      });
    });
  });

  describe('createTodo', () => {
    it('should create a new todo', async () => {
      (prisma.todo.create as jest.Mock).mockResolvedValue(mockTodo);

      const result = await todoService.createTodo(mockUserId, {
        title: 'Test Todo',
        description: 'Test Description',
      });

      expect(result).toEqual(mockTodo);
      expect(prisma.todo.create).toHaveBeenCalled();
    });
  });

  describe('updateTodo', () => {
    it('should update an existing todo', async () => {
      const updatedTodo = { ...mockTodo, status: 'completed' };
      (prisma.todo.findUnique as jest.Mock).mockResolvedValue(mockTodo);
      (prisma.todo.update as jest.Mock).mockResolvedValue(updatedTodo);

      const result = await todoService.updateTodo('todo-1', mockUserId, {
        status: 'completed',
      });

      expect(result.status).toBe('completed');
    });

    it('should throw error if todo not found', async () => {
      (prisma.todo.findUnique as jest.Mock).mockResolvedValue(null);

      await expect(
        todoService.updateTodo('nonexistent', mockUserId, { status: 'completed' })
      ).rejects.toThrow('Todo not found');
    });

    it('should throw error if user does not own todo', async () => {
      const otherUserTodo = { ...mockTodo, userId: 'other-user' };
      (prisma.todo.findUnique as jest.Mock).mockResolvedValue(otherUserTodo);

      await expect(
        todoService.updateTodo('todo-1', mockUserId, { status: 'completed' })
      ).rejects.toThrow('Forbidden');
    });
  });

  describe('deleteTodo', () => {
    it('should delete a todo', async () => {
      (prisma.todo.findUnique as jest.Mock).mockResolvedValue(mockTodo);
      (prisma.todo.delete as jest.Mock).mockResolvedValue(mockTodo);

      await todoService.deleteTodo('todo-1', mockUserId);

      expect(prisma.todo.delete).toHaveBeenCalledWith({
        where: { id: 'todo-1' },
      });
    });

    it('should throw error if todo not found', async () => {
      (prisma.todo.findUnique as jest.Mock).mockResolvedValue(null);

      await expect(
        todoService.deleteTodo('nonexistent', mockUserId)
      ).rejects.toThrow('Todo not found');
    });
  });
});

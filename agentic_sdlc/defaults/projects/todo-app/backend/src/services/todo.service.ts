import prisma from '../models/prisma';

interface TodoQuery {
  status?: 'pending' | 'completed' | 'all';
  sort?: 'createdAt' | 'updatedAt';
  order?: 'asc' | 'desc';
}

export const getTodos = async (userId: string, query: TodoQuery) => {
  const { status = 'all', sort = 'createdAt', order = 'desc' } = query;

  const where: any = { userId };
  if (status !== 'all') {
    where.status = status;
  }

  const todos = await prisma.todo.findMany({
    where,
    orderBy: { [sort]: order },
  });

  return { todos, count: todos.length };
};

export const getTodoById = async (todoId: string, userId: string) => {
  const todo = await prisma.todo.findUnique({ where: { id: todoId } });

  if (!todo) {
    const error: any = new Error('Todo not found');
    error.statusCode = 404;
    error.code = 'NOT_FOUND';
    throw error;
  }

  if (todo.userId !== userId) {
    const error: any = new Error('Forbidden');
    error.statusCode = 403;
    error.code = 'FORBIDDEN';
    throw error;
  }

  return todo;
};

export const createTodo = async (
  userId: string,
  data: { title: string; description?: string }
) => {
  const todo = await prisma.todo.create({
    data: {
      ...data,
      userId,
    },
  });

  return todo;
};

export const updateTodo = async (
  todoId: string,
  userId: string,
  data: { title?: string; description?: string; status?: string }
) => {
  // Check ownership
  await getTodoById(todoId, userId);

  const todo = await prisma.todo.update({
    where: { id: todoId },
    data,
  });

  return todo;
};

export const deleteTodo = async (todoId: string, userId: string) => {
  // Check ownership
  await getTodoById(todoId, userId);

  await prisma.todo.delete({ where: { id: todoId } });
};

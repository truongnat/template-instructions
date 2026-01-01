import { Response, NextFunction } from 'express';
import * as todoService from '../services/todo.service';
import { AuthRequest } from '../middleware/auth';

export const getTodos = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const userId = req.user!.userId;
    const query = req.query as any;
    const result = await todoService.getTodos(userId, query);
    res.status(200).json(result);
  } catch (error) {
    next(error);
  }
};

export const getTodoById = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const userId = req.user!.userId;
    const { id } = req.params;
    const todo = await todoService.getTodoById(id, userId);
    res.status(200).json(todo);
  } catch (error) {
    next(error);
  }
};

export const createTodo = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const userId = req.user!.userId;
    const data = req.body;
    const todo = await todoService.createTodo(userId, data);
    res.status(201).json(todo);
  } catch (error) {
    next(error);
  }
};

export const updateTodo = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const userId = req.user!.userId;
    const { id } = req.params;
    const data = req.body;
    const todo = await todoService.updateTodo(id, userId, data);
    res.status(200).json(todo);
  } catch (error) {
    next(error);
  }
};

export const deleteTodo = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const userId = req.user!.userId;
    const { id } = req.params;
    await todoService.deleteTodo(id, userId);
    res.status(204).send();
  } catch (error) {
    next(error);
  }
};

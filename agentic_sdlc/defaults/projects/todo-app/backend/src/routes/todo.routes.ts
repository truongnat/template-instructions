import { Router } from 'express';
import * as todoController from '../controllers/todo.controller';
import { validate } from '../middleware/validate';
import { createTodoSchema, updateTodoSchema } from '../utils/validation';
import { authMiddleware } from '../middleware/auth';

const router = Router();

// All todo routes require authentication
router.use(authMiddleware);

router.get('/', todoController.getTodos);
router.get('/:id', todoController.getTodoById);
router.post('/', validate(createTodoSchema), todoController.createTodo);
router.patch('/:id', validate(updateTodoSchema), todoController.updateTodo);
router.delete('/:id', todoController.deleteTodo);

export default router;

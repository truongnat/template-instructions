import { useTodoStore } from '../store/todoStore';
import TodoItem from './TodoItem';
import { Todo } from '../types';

interface Props {
  onEdit: (todo: Todo) => void;
}

export default function TodoList({ onEdit }: Props) {
  const { todos, isLoading, error } = useTodoStore();

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        <p className="mt-2 text-gray-600">Loading todos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-lg">
        Error: {error}
      </div>
    );
  }

  if (todos.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 text-lg">No todos yet. Create your first one!</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} onEdit={onEdit} />
      ))}
    </div>
  );
}

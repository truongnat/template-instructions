import { useState } from 'react';
import { useTodoStore } from '../store/todoStore';
import { Todo } from '../types';

interface Props {
  todo: Todo;
  onEdit: (todo: Todo) => void;
}

export default function TodoItem({ todo, onEdit }: Props) {
  const { toggleTodo, deleteTodo } = useTodoStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleDelete = async () => {
    await deleteTodo(todo.id);
    setShowDeleteConfirm(false);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={todo.status === 'completed'}
          onChange={() => toggleTodo(todo.id)}
          className="mt-1 h-5 w-5 text-primary rounded focus:ring-primary cursor-pointer"
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium ${
              todo.status === 'completed'
                ? 'line-through text-gray-400'
                : 'text-gray-900'
            }`}
          >
            {todo.title}
          </h3>
          {todo.description && (
            <p
              className={`mt-1 text-sm ${
                todo.status === 'completed' ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              {todo.description}
            </p>
          )}
          <p className="mt-2 text-xs text-gray-400">
            Created {new Date(todo.createdAt).toLocaleDateString()}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(todo)}
            className="p-2 text-gray-600 hover:text-primary"
            title="Edit"
          >
            ✏️
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="p-2 text-gray-600 hover:text-danger"
            title="Delete"
          >
            🗑️
          </button>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="mt-3 p-3 bg-red-50 rounded flex items-center justify-between">
          <span className="text-sm text-red-600">Delete this todo?</span>
          <div className="flex gap-2">
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
            >
              Cancel
            </button>
            <button
              onClick={handleDelete}
              className="px-3 py-1 text-sm bg-danger text-white rounded hover:bg-red-600"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

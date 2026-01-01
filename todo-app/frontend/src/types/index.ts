export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface TodosResponse {
  todos: Todo[];
  count: number;
}

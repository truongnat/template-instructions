const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api';

export class ApiError extends Error {
  constructor(public statusCode: number, message: string, public code?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: 'Unknown error' } }));
    throw new ApiError(
      response.status,
      error.error?.message || 'Request failed',
      error.error?.code
    );
  }
  if (response.status === 204) return null;
  return response.json();
};

export const api = {
  // Auth
  signup: async (email: string, password: string, name?: string) => {
    const response = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name }),
    });
    return handleResponse(response);
  },

  login: async (email: string, password: string) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
  },

  getMe: async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: getAuthHeader(),
    });
    return handleResponse(response);
  },

  // Todos
  getTodos: async (status?: string, sort?: string, order?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (sort) params.append('sort', sort);
    if (order) params.append('order', order);
    
    const response = await fetch(`${API_URL}/todos?${params}`, {
      headers: getAuthHeader(),
    });
    return handleResponse(response);
  },

  createTodo: async (title: string, description?: string) => {
    const response = await fetch(`${API_URL}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({ title, description }),
    });
    return handleResponse(response);
  },

  updateTodo: async (id: string, data: { title?: string; description?: string; status?: string }) => {
    const response = await fetch(`${API_URL}/todos/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  deleteTodo: async (id: string) => {
    const response = await fetch(`${API_URL}/todos/${id}`, {
      method: 'DELETE',
      headers: getAuthHeader(),
    });
    return handleResponse(response);
  },
};

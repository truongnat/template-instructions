import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../authStore';

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      isLoading: false,
      error: null,
    });
    localStorage.clear();
  });

  it('should initialize with no user', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isLoading).toBe(false);
  });

  it('should set user and token', () => {
    const user = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      createdAt: new Date().toISOString(),
    };
    const token = 'mock-token';

    useAuthStore.setState({ user, token });

    const state = useAuthStore.getState();
    expect(state.user).toEqual(user);
    expect(state.token).toBe(token);
  });

  it('should clear auth on logout', () => {
    const user = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      createdAt: new Date().toISOString(),
    };
    const token = 'mock-token';

    useAuthStore.setState({ user, token });
    localStorage.setItem('token', token);
    
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.token).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('should handle loading state', () => {
    useAuthStore.setState({ isLoading: true });
    expect(useAuthStore.getState().isLoading).toBe(true);
  });

  it('should handle error state', () => {
    const error = 'Login failed';
    useAuthStore.setState({ error });
    expect(useAuthStore.getState().error).toBe(error);
  });
});

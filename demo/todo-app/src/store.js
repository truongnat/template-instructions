/**
 * Simple Observable Store for state management.
 */
class Store {
  constructor() {
    this.state = {
      todos: JSON.parse(localStorage.getItem('todos')) || [],
      filter: 'all' // all, active, completed
    };
    this.listeners = [];
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
    localStorage.setItem('todos', JSON.stringify(this.state.todos));
  }

  addTodo(text) {
    if (!text.trim()) return;
    const todo = {
      id: crypto.randomUUID(),
      text: text.trim(),
      completed: false,
      createdAt: new Date().toISOString()
    };
    this.state.todos = [todo, ...this.state.todos];
    this.notify();
  }

  toggleTodo(id) {
    this.state.todos = this.state.todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    );
    this.notify();
  }

  deleteTodo(id) {
    this.state.todos = this.state.todos.filter(todo => todo.id !== id);
    this.notify();
  }

  setFilter(filter) {
    this.state.filter = filter;
    this.notify();
  }

  getFilteredTodos() {
    const { todos, filter } = this.state;
    if (filter === 'active') return todos.filter(t => !t.completed);
    if (filter === 'completed') return todos.filter(t => t.completed);
    return todos;
  }
}

export const store = new Store();

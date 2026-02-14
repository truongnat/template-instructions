import { useState, useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { useGSAP } from '@gsap/react';
import './App.css';

gsap.registerPlugin(useGSAP);

function App() {
  const [todos, setTodos] = useState(() => {
    const saved = localStorage.getItem('react-todos');
    return saved ? JSON.parse(saved) : [
      { id: 1, text: 'Learn React', completed: true },
      { id: 2, text: 'Master GSAP', completed: false },
      { id: 3, text: 'Build Awesome Apps', completed: false }
    ];
  });
  const [inputValue, setInputValue] = useState('');
  const containerRef = useRef();
  const listRef = useRef();

  useEffect(() => {
    localStorage.setItem('react-todos', JSON.stringify(todos));
  }, [todos]);

  // Entrance animation
  useGSAP(() => {
    gsap.from('.app-container', {
      y: 100,
      opacity: 0,
      duration: 1.2,
      ease: 'elastic.out(1, 0.8)'
    });

    gsap.from('.todo-item', {
      x: -50,
      opacity: 0,
      stagger: 0.1,
      duration: 0.8,
      ease: 'power2.out',
      delay: 0.5
    });
  }, { scope: containerRef });

  const addTodo = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const newTodo = {
      id: Date.now(),
      text: inputValue.trim(),
      completed: false
    };

    setTodos([newTodo, ...todos]);
    setInputValue('');
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const deleteTodo = (id, e) => {
    e.stopPropagation();

    // Animation before delete
    gsap.to(`.todo-item[data-id="${id}"]`, {
      x: 100,
      opacity: 0,
      duration: 0.4,
      onComplete: () => {
        setTodos(todos.filter(t => t.id !== id));
      }
    });
  };

  return (
    <div className="main-wrapper" ref={containerRef}>
      <div className="app-container">
        <h1>
          Todo
          <span style={{ color: 'var(--primary)', fontSize: '1rem' }}>React + GSAP</span>
        </h1>

        <form className="input-wrapper" onSubmit={addTodo}>
          <input
            type="text"
            placeholder="New task..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button type="submit" className="add-button">Add</button>
        </form>

        <div className="todo-list" ref={listRef}>
          {todos.map((todo) => (
            <div
              key={todo.id}
              className={`todo-item ${todo.completed ? 'completed' : ''}`}
              onClick={() => toggleTodo(todo.id)}
              data-id={todo.id}
            >
              <div className="checkbox">
                <svg width="14" height="10" viewBox="0 0 14 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 5L5 9L13 1" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <span className="todo-text">{todo.text}</span>
              <button className="delete-btn" onClick={(e) => deleteTodo(todo.id, e)}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;

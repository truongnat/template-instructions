import './style.css';
import { store } from './store.js';

const todoInput = document.getElementById('todo-input');
const addBtn = document.getElementById('add-btn');
const todoList = document.getElementById('todo-list');
const filterBtns = document.querySelectorAll('.filter-btn');

function render() {
  const todos = store.getFilteredTodos();
  const filter = store.state.filter;

  // Update filter buttons
  filterBtns.forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === filter);
  });

  if (todos.length === 0) {
    todoList.innerHTML = `<li class="empty-state">No tasks here. Enjoy your day!</li>`;
    return;
  }

  todoList.innerHTML = todos.map(todo => `
    <li class="todo-item ${todo.completed ? 'completed' : ''}" data-id="${todo.id}">
      <div class="checkbox"></div>
      <span class="todo-text">${todo.text}</span>
      <button class="delete-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
      </button>
    </li>
  `).join('');

  // Re-attach event listeners
  todoList.querySelectorAll('.todo-item').forEach(item => {
    const id = item.dataset.id;

    item.querySelector('.checkbox').onclick = () => store.toggleTodo(id);
    item.querySelector('.todo-text').onclick = () => store.toggleTodo(id);
    item.querySelector('.delete-btn').onclick = (e) => {
      e.stopPropagation();
      store.deleteTodo(id);
    };
  });
}

// Initial render
store.subscribe(render);
render();

// Event Listeners
addBtn.onclick = () => {
  store.addTodo(todoInput.value);
  todoInput.value = '';
  todoInput.focus();
};

todoInput.onkeypress = (e) => {
  if (e.key === 'Enter') {
    addBtn.click();
  }
};

filterBtns.forEach(btn => {
  btn.onclick = () => {
    store.setFilter(btn.dataset.filter);
  };
});

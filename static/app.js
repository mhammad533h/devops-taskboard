const form = document.querySelector('#add-form');
const input = document.querySelector('#task-title');
const list = document.querySelector('#task-list');
const empty = document.querySelector('#empty');
const status = document.querySelector('#status');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  status.textContent = '';
  try {
    const body = new URLSearchParams({ title: input.value.trim() });
    const response = await fetch('/tasks', { method: 'POST', body });
    if (!response.ok) throw new Error('Could not save task');
    const task = await response.json();
    const item = document.createElement('li');
    item.dataset.id = task.id;
    const button = document.createElement('button');
    button.className = 'toggle';
    button.type = 'button';
    button.setAttribute('aria-label', `Toggle ${task.title}`);
    button.textContent = '○';
    const title = document.createElement('span');
    title.className = 'task-title';
    title.textContent = task.title;
    item.append(button, title);
    list.prepend(item);
    input.value = '';
    empty.hidden = true;
    status.textContent = 'Task added';
  } catch (error) {
    status.textContent = error.message;
  }
});

list.addEventListener('click', async (event) => {
  const button = event.target.closest('button.toggle');
  if (!button) return;
  const item = button.closest('li');
  try {
    const response = await fetch(`/tasks/${item.dataset.id}/toggle`, { method: 'POST' });
    if (!response.ok) throw new Error('Could not update task');
    const task = await response.json();
    item.classList.toggle('done', task.completed);
    button.textContent = task.completed ? '✓' : '○';
    status.textContent = task.completed ? 'Task completed' : 'Task reopened';
  } catch (error) {
    status.textContent = error.message;
  }
});

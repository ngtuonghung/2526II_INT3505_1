const API = 'http://localhost:5000';
let editingId = null;

const notesList   = document.getElementById('notes-list');
const createForm  = document.getElementById('create-form');
const editModal   = document.getElementById('edit-modal');
const editTitle   = document.getElementById('edit-title');
const editContent = document.getElementById('edit-content');

function formatTime(iso) {
  return new Date(iso).toLocaleString();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function renderNotes(notes) {
  if (!notes.length) {
    notesList.innerHTML = '<p class="empty-state">No notes yet. Create one above!</p>';
    return;
  }
  notesList.innerHTML = notes.map(n => `
    <div class="note-card" data-id="${n.id}">
      <div class="card-actions">
        <button class="btn-edit"   onclick="openEdit(${n.id})">Edit</button>
        <button class="btn-delete" onclick="deleteNote(${n.id})">Delete</button>
      </div>
      <div class="note-title">${escHtml(n.title)}</div>
      <div class="note-content">${escHtml(n.content || '')}</div>
      <div class="note-time">${formatTime(n.time)}</div>
    </div>
  `).join('');
}

async function loadNotes() {
  const res = await fetch(`${API}/notes`);
  const data = await res.json();
  renderNotes(data);
}

createForm.addEventListener('submit', async e => {
  e.preventDefault();
  const title   = document.getElementById('new-title').value.trim();
  const content = document.getElementById('new-content').value.trim();
  await fetch(`${API}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });
  createForm.reset();
  loadNotes();
});

function openEdit(id) {
  const card = document.querySelector(`.note-card[data-id="${id}"]`);
  editingId = id;
  editTitle.value   = card.querySelector('.note-title').textContent;
  editContent.value = card.querySelector('.note-content').textContent;
  editModal.classList.add('open');
  editTitle.focus();
}

document.getElementById('modal-cancel').addEventListener('click', () => {
  editModal.classList.remove('open');
});

editModal.addEventListener('click', e => {
  if (e.target === editModal) editModal.classList.remove('open');
});

document.getElementById('modal-save').addEventListener('click', async () => {
  const title   = editTitle.value.trim();
  const content = editContent.value.trim();
  if (!title) { editTitle.focus(); return; }
  await fetch(`${API}/notes/${editingId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content }),
  });
  editModal.classList.remove('open');
  loadNotes();
});

async function deleteNote(id) {
  if (!confirm('Delete this note?')) return;
  await fetch(`${API}/notes/${id}`, { method: 'DELETE' });
  loadNotes();
}

loadNotes();

const API = 'http://localhost:5000';
let editingId = null;

// JWT stored in memory — lost on refresh (by design for REST statelessness).
let authToken = null;

// ── DOM refs ─────────────────────────────────────────────────────────────────
const loginPage   = document.getElementById('login-page');
const loginForm   = document.getElementById('login-form');
const loginError  = document.getElementById('login-error');
const appDiv      = document.getElementById('app');
const notesList   = document.getElementById('notes-list');
const createForm  = document.getElementById('create-form');
const editModal   = document.getElementById('edit-modal');
const editTitle   = document.getElementById('edit-title');
const editContent = document.getElementById('edit-content');

// ── Auth helpers ──────────────────────────────────────────────────────────────
function authHeaders(extra = {}) {
  return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}`, ...extra };
}

function showLogin(errorMsg = '') {
  loginError.textContent = errorMsg;
  loginPage.style.display = 'flex';
  appDiv.style.display = 'none';
  authToken = null;
}

function showApp() {
  loginPage.style.display = 'none';
  appDiv.style.display = 'block';
}

// ── Login form ────────────────────────────────────────────────────────────────
loginForm.addEventListener('submit', async e => {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  loginError.textContent = '';

  const res = await fetch(`${API}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    showLogin(data.error || 'Login failed');
    return;
  }

  const { token } = await res.json();
  authToken = token;
  loginForm.reset();
  showApp();
  loadNotes();
});

// ── Logout ────────────────────────────────────────────────────────────────────
document.getElementById('btn-logout').addEventListener('click', () => {
  showLogin();
});

// ── Utility ───────────────────────────────────────────────────────────────────
function formatTime(iso) {
  return new Date(iso).toLocaleString();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Redirects to login on 401.
async function handleResponse(res) {
  if (res.status === 401) {
    showLogin('Session expired. Please sign in again.');
    return null;
  }
  return res;
}

// ── Notes rendering ──────────────────────────────────────────────────────────
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
  const res = await fetch(`${API}/notes`, { headers: authHeaders() });
  if (!await handleResponse(res)) return;
  renderNotes(await res.json());
}

// ── Create note ───────────────────────────────────────────────────────────────
createForm.addEventListener('submit', async e => {
  e.preventDefault();
  const title   = document.getElementById('new-title').value.trim();
  const content = document.getElementById('new-content').value.trim();
  const res = await fetch(`${API}/notes`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ title, content }),
  });
  if (!await handleResponse(res)) return;
  createForm.reset();
  loadNotes();
});

// ── Edit note ─────────────────────────────────────────────────────────────────
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
  const res = await fetch(`${API}/notes/${editingId}`, {
    method: 'PATCH',
    headers: authHeaders(),
    body: JSON.stringify({ title, content }),
  });
  if (!await handleResponse(res)) return;
  editModal.classList.remove('open');
  loadNotes();
});

// ── Delete note ───────────────────────────────────────────────────────────────
async function deleteNote(id) {
  if (!confirm('Delete this note?')) return;
  const res = await fetch(`${API}/notes/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  if (!await handleResponse(res)) return;
  loadNotes();
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
showLogin();


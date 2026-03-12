// Constants
const API       = 'http://127.0.0.1:5000';
const NOTES_API = `${API}/api/v2/notes`;
const AUTH_API  = `${API}/auth`;

// State
// Access token lives in memory only. Refresh token lives in an HttpOnly
// cookie managed by the browser — JS never touches it directly.
let authToken  = null;
let editingId  = null;

// DOM refs
const loginPage   = document.getElementById('login-page');
const loginForm   = document.getElementById('login-form');
const loginError  = document.getElementById('login-error');
const appDiv      = document.getElementById('app');
const notesList   = document.getElementById('notes-list');
const createForm  = document.getElementById('create-form');
const editModal      = document.getElementById('edit-modal');
const editTitle      = document.getElementById('edit-title');
const editContent    = document.getElementById('edit-content');
const editImage      = document.getElementById('edit-image');
const editImgPreview = document.getElementById('edit-image-preview');
const newImage       = document.getElementById('new-image');

// Auth helpers
function authHeaders() {
  return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${authToken}` };
}

function bearerHeader() {
  return { 'Authorization': `Bearer ${authToken}` };
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

// Sends the HttpOnly refresh_token cookie to get a new access token.
// Returns true on success.
async function tryRefresh() {
  const res = await fetch(`${AUTH_API}/refresh`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) return false;
  const { access_token } = await res.json();
  authToken = access_token;
  return true;
}

// Wraps a fetch call. On 401, attempts one silent token refresh then retries.
// Returns the Response, or null if the user must log in again.
async function apiCall(requestFn) {
  let res = await requestFn();
  if (res.status === 401) {
    if (await tryRefresh()) {
      res = await requestFn();
    } else {
      showLogin('Session expired. Please sign in again.');
      return null;
    }
  }
  return res;
}

// Session restore on page load
async function checkSession() {
  if (await tryRefresh()) {
    showApp();
    loadNotes();
  } else {
    showLogin();
  }
}

// Login form
loginForm.addEventListener('submit', async e => {
  e.preventDefault();
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  loginError.textContent = '';

  const res = await fetch(`${AUTH_API}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    showLogin(data.error || 'Login failed');
    return;
  }

  const { access_token } = await res.json();
  authToken = access_token;
  loginForm.reset();
  showApp();
  loadNotes();
});

// Logout
document.getElementById('btn-logout').addEventListener('click', async () => {
  await fetch(`${AUTH_API}/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  showLogin();
});

// Utility
function formatTime(iso) {
  return new Date(iso).toLocaleString();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Notes rendering
async function loadNoteImage(noteId, imgEl) {
  const res = await apiCall(() => fetch(`${NOTES_API}/${noteId}/image`, { headers: bearerHeader() }));
  if (!res || !res.ok) return;
  const blob = await res.blob();
  imgEl.src = URL.createObjectURL(blob);
  imgEl.style.display = 'block';
}

function renderNotes(notes) {
  if (!notes.length) {
    notesList.innerHTML = '<p class="empty-state">No notes yet. Create one above!</p>';
    return;
  }
  notesList.innerHTML = notes.map(n => `
    <div class="note-card" data-id="${n.id}" data-has-image="${n.has_image || false}">
      <div class="card-actions">
        <button class="btn-edit"   onclick="openEdit(${n.id})">Edit</button>
        <button class="btn-delete" onclick="deleteNote(${n.id})">Delete</button>
      </div>
      <div class="note-title">${escHtml(n.title)}</div>
      <div class="note-content">${escHtml(n.content || '')}</div>
      ${n.has_image ? `<img class="note-image" id="note-img-${n.id}" style="display:none; max-width:100%; margin-top:8px;" />` : ''}
      <div class="note-time">${formatTime(n.time)}</div>
    </div>
  `).join('');
  notes.filter(n => n.has_image).forEach(n =>
    loadNoteImage(n.id, document.getElementById(`note-img-${n.id}`))
  );
}

async function loadNotes() {
  const res = await apiCall(() => fetch(NOTES_API, { headers: bearerHeader() }));
  if (!res) return;
  renderNotes(await res.json());
}

// Create note
createForm.addEventListener('submit', async e => {
  e.preventDefault();
  const fd = new FormData();
  fd.append('title',   document.getElementById('new-title').value.trim());
  fd.append('content', document.getElementById('new-content').value.trim());
  if (newImage.files[0]) fd.append('image', newImage.files[0]);
  const res = await apiCall(() => fetch(NOTES_API, {
    method: 'POST',
    headers: bearerHeader(),
    body: fd,
  }));
  if (!res) return;
  createForm.reset();
  loadNotes();
});

// Edit note
function openEdit(id) {
  const card = document.querySelector(`.note-card[data-id="${id}"]`);
  editingId = id;
  editTitle.value   = card.querySelector('.note-title').textContent;
  editContent.value = card.querySelector('.note-content').textContent;
  editImage.value   = '';
  if (card.dataset.hasImage === 'true') {
    loadNoteImage(id, editImgPreview);
  } else {
    editImgPreview.style.display = 'none';
    editImgPreview.src = '';
  }
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
  const fd = new FormData();
  fd.append('title', title);
  fd.append('content', content);
  if (editImage.files[0]) fd.append('image', editImage.files[0]);
  const res = await apiCall(() => fetch(`${NOTES_API}/${editingId}`, {
    method: 'PATCH',
    headers: bearerHeader(),
    body: fd,
  }));
  if (!res) return;
  editModal.classList.remove('open');
  loadNotes();
});

// Delete note
async function deleteNote(id) {
  if (!confirm('Delete this note?')) return;
  const res = await apiCall(() => fetch(`${NOTES_API}/${id}`, {
    method: 'DELETE',
    headers: bearerHeader(),
  }));
  if (!res) return;
  loadNotes();
}

// Bootstrap
checkSession();


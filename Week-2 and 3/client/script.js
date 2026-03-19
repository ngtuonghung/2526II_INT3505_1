// Constants
const API       = 'http://127.0.0.1:5000';
const NOTES_API = `${API}/api/v2/notes`;
const AUTH_API  = `${API}/auth`;

// State
let editingId  = null;

// DOM refs
const appDiv      = document.getElementById('app');
const notesList   = document.getElementById('notes-list');
const createForm  = document.getElementById('create-form');
const editModal      = document.getElementById('edit-modal');
const editTitle      = document.getElementById('edit-title');
const editContent    = document.getElementById('edit-content');
const editImage      = document.getElementById('edit-image');
const editImgPreview = document.getElementById('edit-image-preview');
const newImage       = document.getElementById('new-image');

// Redirect to login page (called when the refresh token is invalid or user logs out).
function redirectToLogin() {
  window.location.href = 'index.html';
}

// Sends the HttpOnly refresh_token cookie to get a new access token.
// Returns true on success.
async function tryRefresh() {
  const res = await fetch(`${AUTH_API}/refresh`, {
    method: 'POST',
    credentials: 'include',
  });
  return res.ok;
}

// Wraps a fetch call. On 401, attempts one silent token refresh then retries.
// Returns the Response, or null if the session has expired.
async function apiCall(requestFn) {
  let res = await requestFn();
  if (res.status === 401) {
    if (await tryRefresh()) {
      res = await requestFn();
    } else {
      redirectToLogin();
      return null;
    }
  }
  return res;
}

// Session restore on page load.
// Use the existing access token if it is still valid; otherwise fall back to
// the refresh token. Redirect to login only when the refresh token is invalid.
async function checkSession() {
  if (await tryRefresh()) {
    appDiv.style.display = 'block';
    loadNotes();
  } else {
    redirectToLogin();
  }
}

// Logout
document.getElementById('btn-logout').addEventListener('click', async () => {
  await fetch(`${AUTH_API}/logout`, {
    method: 'POST',
    credentials: 'include',
  });
  redirectToLogin();
});

// Utility
function formatTime(iso) {
  return new Date(iso).toLocaleString();
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// Notes rendering
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
      ${n.image_data ? `<img class="note-image" src="${n.image_data}" style="max-width:100%; margin-top:8px;" />` : ''}
      <div class="note-time">${formatTime(n.time)}</div>
    </div>
  `).join('');
}

async function loadNotes() {
  const res = await apiCall(() => fetch(NOTES_API, { credentials: 'include' }));
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
    credentials: 'include',
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
  const cardImg = card.querySelector('.note-image');
  if (cardImg) {
    editImgPreview.src = cardImg.src;
    editImgPreview.style.display = 'block';
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
    credentials: 'include',
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
    credentials: 'include',
  }));
  if (!res) return;
  loadNotes();
}

// Bootstrap
checkSession();


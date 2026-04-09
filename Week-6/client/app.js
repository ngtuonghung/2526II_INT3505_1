const API_BASE_URL = "http://127.0.0.1:5000";

let accessToken = null; // stored in memory, cleared on page refresh

const loginView = document.getElementById("login-view");
const helloView = document.getElementById("hello-view");
const loginForm = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const helloText = document.getElementById("hello-text");
const roleText = document.getElementById("role-text");
const scopeText = document.getElementById("scope-text");
const statusText = document.getElementById("status");
const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");

function setStatus(message, isError = false) {
  statusText.textContent = message;
  statusText.classList.toggle("error", isError);
}

function showLogin() {
  loginView.classList.remove("hidden");
  helloView.classList.add("hidden");
  passwordInput.value = "";
}

function showHello(user) {
  helloText.textContent = `Hello ${user.username}`;
  roleText.textContent = `Role: ${user.role || ""}`;
  scopeText.textContent = `Scope: ${(user.scope || []).join(", ")}`;
  loginView.classList.add("hidden");
  helloView.classList.remove("hidden");
}

function sha256Hex(value) {
  return CryptoJS.SHA256(value).toString(CryptoJS.enc.Hex);
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(accessToken ? { "Authorization": `Bearer ${accessToken}` } : {}),
    ...(options.headers || {}),
  };
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include", // sends httpOnly refresh token cookie automatically
    headers,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data;
}

async function restoreSession() {
  try {
    // Browser automatically sends the httpOnly refresh token cookie
    const result = await api("/auth/refresh", { method: "POST", body: "{}" });
    accessToken = result.access_token;
    const user = await api("/auth/me");
    showHello(user);
  } catch (_) {
    showLogin();
  }
}

restoreSession();

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginButton.disabled = true;
  setStatus("Logging in...");

  try {
    const username = usernameInput.value.trim();
    const passwordHash = sha256Hex(passwordInput.value);

    const result = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password: passwordHash }),
    });

    accessToken = result.access_token;
    showHello({
      username: result.username || username,
      role: result.role,
      scope: result.scope,
    });
    setStatus("");
  } catch (error) {
    showLogin();
    setStatus(error.message, true);
  } finally {
    loginButton.disabled = false;
  }
});

logoutButton.addEventListener("click", async () => {
  logoutButton.disabled = true;
  setStatus("Logging out...");

  try {
    await api("/auth/logout", { method: "POST", body: "{}" });
  } catch (_) {
    // Clear the UI even if the server-side session is already gone.
  } finally {
    accessToken = null;
    showLogin();
    setStatus("");
    logoutButton.disabled = false;
  }
});

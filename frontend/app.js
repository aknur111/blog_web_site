console.log("Cosmic app.js loaded ✅ v999");

const API_BASE =
  window.__API_BASE__ ||
  (location.protocol === "file:" ? "http://127.0.0.1:8000/api" : "http://127.0.0.1:8000/api");

const STORAGE_TOKEN = "cb_token";
const STORAGE_USER = "cb_user";

// ----------------- helpers -----------------
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

function escapeHtml(str = "") {
  return String(str)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function showNotification(text, isError = false) {
  const notif = $("#notif");
  if (!notif) return console.log(isError ? "❌" : "✅", text);

  notif.textContent = text;
  notif.style.background = isError ? "linear-gradient(90deg,#ff6b6b,#d94b4b)" : "";
  notif.classList.add("show");
  notif.setAttribute("aria-hidden", "false");
  setTimeout(() => {
    notif.classList.remove("show");
    notif.setAttribute("aria-hidden", "true");
    notif.style.background = "";
  }, 3200);
}

function getToken() {
  return localStorage.getItem(STORAGE_TOKEN) || "";
}
function setToken(token) {
  if (token) localStorage.setItem(STORAGE_TOKEN, token);
  else localStorage.removeItem(STORAGE_TOKEN);
  updateAuthUI();
}

function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function apiFetch(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) {
    let msg = `Server ${res.status}`;
    try {
      const jd = await res.json();
      msg = jd.detail || jd.message || JSON.stringify(jd);
    } catch {
      const txt = await res.text();
      if (txt) msg = txt;
    }
    throw new Error(msg);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) return await res.json();
  return null;
}

// ----------------- find buttons even without ids -----------------
function findButtonByIdOrText(id, text) {
  // 1) by id
  if (id) {
    const el = document.getElementById(id);
    if (el) return el;
  }
  // 2) by text (first match)
  const t = String(text || "").trim().toLowerCase();
  if (!t) return null;
  return $$("button, a").find((b) => (b.textContent || "").trim().toLowerCase() === t) || null;
}

function safeOn(el, event, fn) {
  if (!el) return;
  el.addEventListener(event, fn);
}

// ----------------- sections -----------------
function setDisplay(sel, visible) {
  const el = $(sel);
  if (!el) return;
  el.style.display = visible ? "" : "none";
}

function showSection(name) {
  // these selectors support both your old layout and new layout
  setDisplay("#homeSection", name === "home");
  setDisplay("#myPostsSection", name === "my");
  setDisplay("#analyticsSection", name === "analytics");
  setDisplay("#searchSection", name === "search");
  setDisplay("#profileSection", name === "profile");

  if (name === "home") loadHome();
  if (name === "my") loadMy();
  if (name === "analytics") loadAnalytics();
  if (name === "search") loadSearch();
  if (name === "profile") renderProfile();
}

// ----------------- render posts -----------------
function extractTitleFromContent(content) {
  const lines = String(content || "")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);
  return lines.length ? lines[0].slice(0, 120) : "Untitled";
}

function excerpt(content) {
  const txt = String(content || "").replaceAll("\n", " ").trim();
  return txt.length > 180 ? txt.slice(0, 180) + "…" : txt;
}

function createCard(p, allowEdit = true) {
  const el = document.createElement("article");
  el.className = "post-card";

  const title = escapeHtml(p.title || extractTitleFromContent(p.content));
  const body = escapeHtml(excerpt(p.content));
  const thumb = p.media_url
    ? `<div class="thumb" style="background-image:url('${escapeHtml(p.media_url)}')"></div>`
    : "";

  el.innerHTML = `
    ${thumb}
    <h3 class="title">${title}</h3>
    <div class="excerpt">${body}</div>
    <div style="margin-top:10px;display:flex;gap:8px">
      <button class="btn btn-ghost view-btn">View</button>
      ${allowEdit ? `<button class="btn btn-ghost edit-btn">Edit</button>
      <button class="btn btn-ghost delete-btn">Delete</button>` : ``}
    </div>
  `;

  el.querySelector(".view-btn")?.addEventListener("click", () => openViewModal(p));
  el.querySelector(".edit-btn")?.addEventListener("click", () => openEdit(p));
  el.querySelector(".delete-btn")?.addEventListener("click", () => deletePost(p));
  return el;
}

function renderPosts(containerSel, posts, allowEdit = true) {
  const box = $(containerSel);
  if (!box) return;
  box.innerHTML = "";
  (posts || []).forEach((p) => box.appendChild(createCard(p, allowEdit)));
}

// ----------------- modals -----------------
let editing = null;

function openModal(sel) {
  const el = $(sel);
  if (!el) return;
  el.setAttribute("aria-hidden", "false");
}
function closeModal(sel) {
  const el = $(sel);
  if (!el) return;
  el.setAttribute("aria-hidden", "true");
}

function openCreate() {
  editing = null;
  const form = $("#createForm");
  if (form) form.reset();
  openModal("#modal");
}

function openEdit(p) {
  editing = p;
  const form = $("#createForm");
  if (!form) return;

  const title = extractTitleFromContent(p.content || "");
  const body = String(p.content || "").replace(title, "").trim();

  form.elements.title && (form.elements.title.value = title);
  form.elements.content && (form.elements.content.value = body);
  form.elements.image && (form.elements.image.value = p.media_url || "");
  form.elements.category && (form.elements.category.value = p.category_id || "general");
  form.elements.tags && (form.elements.tags.value = (p.tags || []).join(", "));

  openModal("#modal");
}

function openViewModal(p) {
  const t = $("#viewTitle");
  const img = $("#viewImage");
  const c = $("#viewContent");

  if (t) t.textContent = p.title || extractTitleFromContent(p.content || "");
  if (img) img.innerHTML = p.media_url ? `<div class="thumb" style="height:220px;background-image:url('${escapeHtml(p.media_url)}')"></div>` : "";
  if (c) c.textContent = p.content || "";

  openModal("#viewModal");
}

// ----------------- load data -----------------
async function loadHome() {
  try {
    const data = await apiFetch(`/posts?limit=20&skip=0`);
    renderPosts("#posts", data, true);
  } catch (e) {
    showNotification("Home load failed: " + e.message, true);
  }
}

async function loadMy() {
  try {
    const data = await apiFetch(`/posts/me?limit=20&skip=0`, {
      method: "GET",
      headers: { ...authHeaders() },
    });
    renderPosts("#myPosts", data, true);
  } catch (e) {
    showNotification("My posts failed: " + e.message, true);
  }
}

async function loadAnalytics() {
  const ul = $("#topTags");
  if (!ul) return;
  try {
    const data = await apiFetch(`/posts/analytics/top-tags?limit=10`);
    ul.innerHTML = data.map((t) => `<li>${escapeHtml(t.tag)} — <b>${t.count}</b></li>`).join("");
  } catch {
    ul.innerHTML = "<li>Failed to load analytics</li>";
  }
}

async function loadSearch() {
  const input = $("#searchInput");
  const q = input ? input.value.trim() : "";
  try {
    const qs = new URLSearchParams({ limit: "20", skip: "0" });
    if (q) qs.set("q", q);
    const data = await apiFetch(`/posts?${qs.toString()}`);
    renderPosts("#searchResults", data, true);
  } catch (e) {
    showNotification("Search failed: " + e.message, true);
  }
}

function renderProfile() {
  const box = $("#profileBox");
  if (!box) return;

  const token = getToken();
  let user = null;
  try { user = JSON.parse(localStorage.getItem(STORAGE_USER) || "null"); } catch {}

  box.innerHTML = `
    <div class="post-card">
      <h3 class="title">Profile</h3>
      <p><b>Status:</b> ${token ? "Authenticated ✅" : "Not signed in ❌"}</p>
      <p><b>Username:</b> ${escapeHtml(user?.username || "-")}</p>
      <p><b>Email:</b> ${escapeHtml(user?.email || "-")}</p>
    </div>
  `;
}

// ----------------- crud -----------------
async function deletePost(p) {
  if (!p?.id) return;
  if (!confirm("Delete post?")) return;

  try {
    await apiFetch(`/posts/${p.id}`, { method: "DELETE", headers: { ...authHeaders() } });
    showNotification("Deleted ✅");
    loadHome();
    loadMy();
  } catch (e) {
    showNotification("Delete failed: " + e.message, true);
  }
}

async function submitPost(e) {
  e.preventDefault();

  if (!getToken()) return showNotification("Sign in first", true);

  const form = $("#createForm");
  if (!form) return;

  const title = form.elements.title?.value?.trim() || "";
  const content = form.elements.content?.value?.trim() || "";
  const media_url = form.elements.image?.value?.trim() || "";
  const category_id = form.elements.category?.value?.trim() || "general";
  const tags = (form.elements.tags?.value || "").split(",").map(t => t.trim()).filter(Boolean);

  if (!title || !content) return showNotification("Fill Title + Content", true);

  const payload = {
    author_id: "web",
    content: `${title}\n\n${content}`,
    media_url,
    category_id,
    status: "published",
    tags,
  };

  try {
    if (editing?.id) {
      await apiFetch(`/posts/${editing.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify(payload),
      });
      showNotification("Updated ✅");
    } else {
      await apiFetch(`/posts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders() },
        body: JSON.stringify(payload),
      });
      showNotification("Published ✅");
    }

    editing = null;
    form.reset();
    closeModal("#modal");
    loadHome();
    loadMy();
  } catch (e) {
    showNotification("Save failed: " + e.message, true);
  }
}

// ----------------- login -----------------
async function submitLogin(e) {
  e.preventDefault();

  const form = $("#loginForm");
  if (!form) return;

  const username = form.elements.username?.value?.trim() || "";
  const email = form.elements.email?.value?.trim() || "";
  if (!username || !email) return showNotification("Enter username + email", true);

  try {
    const qs = new URLSearchParams({ username, email });
    const data = await apiFetch(`/register?${qs.toString()}`, { method: "POST" });

    if (!data?.token) throw new Error("No token returned");
    localStorage.setItem(STORAGE_USER, JSON.stringify({ username, email }));
    setToken(data.token);

    showNotification("Token saved ✅");
    closeModal("#loginModal");
    form.reset();
    loadMy();
  } catch (e) {
    showNotification("Register failed: " + e.message, true);
  }
}

function logout() {
  setToken("");
  showNotification("Logged out");
}

// ----------------- ui -----------------
function updateAuthUI() {
  const token = getToken();
  const signBtn = findButtonByIdOrText("openLogin", "Sign in") || findButtonByIdOrText(null, "Signed");
  const logoutBtn = document.getElementById("logoutBtn") || findButtonByIdOrText(null, "Logout");

  if (signBtn) signBtn.textContent = token ? "Signed" : "Sign in";
  if (logoutBtn) logoutBtn.style.display = token ? "" : "none";
}

function wire() {
  // header buttons (try by id, else by text)
  safeOn(findButtonByIdOrText("openCreate", "Create Post"), "click", openCreate);
  safeOn(findButtonByIdOrText("openLogin", "Sign in"), "click", () => openModal("#loginModal"));
  safeOn(document.getElementById("logoutBtn") || findButtonByIdOrText(null, "Logout"), "click", logout);

  // nav (try old ids first)
  safeOn(document.getElementById("navHome") || findButtonByIdOrText(null, "Home"), "click", () => showSection("home"));
  safeOn(document.getElementById("navMy") || findButtonByIdOrText(null, "My Posts"), "click", () => showSection("my"));
  safeOn(document.getElementById("navAnalytics") || findButtonByIdOrText(null, "Analytics"), "click", () => showSection("analytics"));
  safeOn(document.getElementById("navSearch") || findButtonByIdOrText(null, "Search"), "click", () => showSection("search"));
  safeOn(document.getElementById("navProfile") || findButtonByIdOrText(null, "Profile"), "click", () => showSection("profile"));
  safeOn(document.getElementById("navPost") || findButtonByIdOrText(null, "Post"), "click", openCreate);

  // modal close (ids from your old layout)
  safeOn(document.getElementById("closeModal"), "click", () => closeModal("#modal"));
  safeOn(document.getElementById("modalBackdrop"), "click", () => closeModal("#modal"));
  safeOn(document.getElementById("closeView"), "click", () => closeModal("#viewModal"));
  safeOn(document.getElementById("viewBackdrop"), "click", () => closeModal("#viewModal"));
  safeOn(document.getElementById("closeLogin"), "click", () => closeModal("#loginModal"));
  safeOn(document.getElementById("loginBackdrop"), "click", () => closeModal("#loginModal"));

  // forms
  $("#createForm")?.addEventListener("submit", submitPost);
  $("#loginForm")?.addEventListener("submit", submitLogin);

  // if you have optional search button
  $("#searchBtn")?.addEventListener("click", loadSearch);
}

document.addEventListener("DOMContentLoaded", () => {
  updateAuthUI();
  wire();
  showSection("home");
});

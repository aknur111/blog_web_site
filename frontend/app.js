console.log("Cosmic app.js loaded ✅ fixed-for-your-HTML");

const API_BASE =
  window.__API_BASE__ ||
  "http://127.0.0.1:8000/api";

const STORAGE_TOKEN = "cb_token";
const STORAGE_USER = "cb_user";

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
  notif.style.background = isError
    ? "linear-gradient(90deg,#ff6b6b,#d94b4b)"
    : "";
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
  renderProfile();
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_USER) || "null");
  } catch {
    return null;
  }
}
function setUser(user) {
  if (user) localStorage.setItem(STORAGE_USER, JSON.stringify(user));
  else localStorage.removeItem(STORAGE_USER);
  renderProfile();
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

const PAGES = {
  home: "#pageHome",
  my: "#pageMy",
  search: "#pageSearch",
  post: "#pagePost",
  analytics: "#pageAnalytics",
  profile: "#pageProfile",
};

function showPage(name) {
  Object.entries(PAGES).forEach(([k, sel]) => {
    const el = $(sel);
    if (el) el.style.display = k === name ? "" : "none";
  });

  $$("#tabs .btn").forEach((b) => {
    b.removeAttribute("aria-current");
  });
  const active = $(`#tabs .btn[data-page="${name}"]`);
  if (active) active.setAttribute("aria-current", "page");

  if (name === "home") loadHome(true);
  if (name === "my") loadMy(true);
  if (name === "search") loadSearch(true);
  if (name === "analytics") loadAnalytics();
  if (name === "profile") renderProfile();
}

async function pingAPI() {
  const badge = $("#apiStatus");
  if (!badge) return;

  try {
    await apiFetch("/health");
    badge.textContent = "API: online ✅";
  } catch {
    badge.textContent = "API: offline ❌";
  }
}

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

function postCard(p, allowEdit = true) {
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
    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
      <button class="btn btn-ghost view-btn">Open</button>
      ${
        allowEdit
          ? `<button class="btn btn-ghost edit-btn">Edit</button>
             <button class="btn btn-ghost delete-btn">Delete</button>`
          : ""
      }
    </div>
  `;

  el.querySelector(".view-btn")?.addEventListener("click", () => {
    showPage("post");
    $("#openPostId").value = p.id;
    openPostById(p.id, true);
  });

  el.querySelector(".edit-btn")?.addEventListener("click", () => openEditModal(p));
  el.querySelector(".delete-btn")?.addEventListener("click", () => deletePost(p.id));

  return el;
}

function renderPosts(containerSel, posts, allowEdit = true) {
  const box = $(containerSel);
  if (!box) return;
  box.innerHTML = "";

  if (!posts || posts.length === 0) {
    box.innerHTML = `<div class="panel muted">No posts yet.</div>`;
    return;
  }

  posts.forEach((p) => box.appendChild(postCard(p, allowEdit)));
}

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

let editingPostId = null;

function openCreateModal() {
  editingPostId = null;
  const form = $("#createForm");
  if (form) {
    form.reset();
    form.elements.id && (form.elements.id.value = "");
  }
  $("#postModalTitle").textContent = "New Post";
  openModal("#modal");
}

function openEditModal(p) {
  editingPostId = p.id;
  const form = $("#createForm");
  if (!form) return;

  const title = extractTitleFromContent(p.content || "");
  const body = String(p.content || "").replace(title, "").trim();

  form.elements.id && (form.elements.id.value = p.id);
  form.elements.title && (form.elements.title.value = title);
  form.elements.content && (form.elements.content.value = body);
  form.elements.image && (form.elements.image.value = p.media_url || "");
  form.elements.category && (form.elements.category.value = p.category_id || "general");
  form.elements.tags && (form.elements.tags.value = (p.tags || []).join(", "));

  $("#postModalTitle").textContent = "Edit Post";
  openModal("#modal");
}

const state = {
  home: { skip: 0, limit: 20, tag: "" },
  my: { skip: 0, limit: 20 },
  search: { skip: 0, limit: 20, q: "", tag: "" },
};

function buildQuery(params) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    const s = String(v).trim();
    if (!s) return;
    qs.set(k, s);
  });
  return qs.toString();
}

async function loadHome(reset = false) {
  const tag = ($("#homeTag")?.value || "").trim();
  if (reset) state.home.skip = 0;
  state.home.tag = tag;

  const qs = buildQuery({
    limit: state.home.limit,
    skip: state.home.skip,
    tag: state.home.tag,
  });

  try {
    const data = await apiFetch(`/posts?${qs}`);
    if (reset) renderPosts("#homePosts", data, true);
    else appendPosts("#homePosts", data, true);

    state.home.skip += data.length;
  } catch (e) {
    showNotification("Home load failed: " + e.message, true);
  }
}

async function loadMy(reset = false) {
  if (!getToken()) {
    renderPosts("#myPosts", [], true);
    showNotification("Sign in to see My Posts 🔐", true);
    return;
  }

  if (reset) state.my.skip = 0;

  const qs = buildQuery({
    limit: state.my.limit,
    skip: state.my.skip,
  });

  try {
    const data = await apiFetch(`/posts/me?${qs}`, {
      method: "GET",
      headers: { ...authHeaders() },
    });

    if (reset) renderPosts("#myPosts", data, true);
    else appendPosts("#myPosts", data, true);

    state.my.skip += data.length;
  } catch (e) {
    showNotification("My posts failed: " + e.message, true);
  }
}

async function loadSearch(reset = false) {
  const q = ($("#searchQuery")?.value || "").trim();
  const tag = ($("#searchTag")?.value || "").trim();

  if (reset) state.search.skip = 0;
  state.search.q = q;
  state.search.tag = tag;

  const qs = buildQuery({
    limit: state.search.limit,
    skip: state.search.skip,
    q: state.search.q,
    tag: state.search.tag,
  });

  try {
    const data = await apiFetch(`/posts?${qs}`);
    if (reset) renderPosts("#searchPosts", data, true);
    else appendPosts("#searchPosts", data, true);

    state.search.skip += data.length;
  } catch (e) {
    showNotification("Search failed: " + e.message, true);
  }
}

function appendPosts(containerSel, posts, allowEdit = true) {
  const box = $(containerSel);
  if (!box) return;

  if (!posts || posts.length === 0) {
    showNotification("No more posts 🙃");
    return;
  }

  posts.forEach((p) => box.appendChild(postCard(p, allowEdit)));
}

let currentPostId = null;

function fillPostView(p) {
  $("#postView").style.display = "";

  $("#postTitle").textContent = extractTitleFromContent(p.content || "");
  $("#postMeta").textContent = `author: ${p.author_id || "-"} • category: ${p.category_id || "-"} • views: ${p.views ?? 0}`;

  $("#postImage").innerHTML = p.media_url
    ? `<div class="thumb" style="height:220px;background-image:url('${escapeHtml(p.media_url)}')"></div>`
    : "";

  $("#postContent").textContent = p.content || "";
}

async function openPostById(id, incView = false) {
  if (!id) return;

  currentPostId = id;

  try {
    if (incView) {
      try {
        await apiFetch(`/posts/${id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json", ...authHeaders() },
          body: JSON.stringify({ inc_views: 1 }),
        });
      } catch {
      }
    }

    const p = await apiFetch(`/posts/${id}`);
    fillPostView(p);

    await loadComments(id);
    await loadReactions(id);
  } catch (e) {
    showNotification("Open post failed: " + e.message, true);
    $("#postView").style.display = "none";
  }
}

async function loadComments(postId) {
  const list = $("#commentsList");
  if (!list) return;

  try {
    const data = await apiFetch(`/posts/${postId}/comments`);

    if (!Array.isArray(data) || data.length === 0) {
      list.innerHTML = `<li class="muted">No comments yet.</li>`;
      return;
    }

    list.innerHTML = data
      .filter(c => c && typeof c === "object")
      .map(c => {
        const who = escapeHtml(c.user_id ?? "user");
        const text = escapeHtml(c.content ?? "");
        return `<li><b>${who}:</b> ${text}</li>`;
      })
      .join("");

  } catch (e) {
    console.error("loadComments error:", e);
    list.innerHTML = `<li class="muted">Failed to load comments.</li>`;
  }
}


async function submitComment(e) {
  e.preventDefault();
  const txt = ($("#commentText")?.value || "").trim();

  if (!currentPostId) return showNotification("Open a post first", true);
  if (!getToken()) return showNotification("Sign in to comment 🔐", true);
  if (!txt) return;

  try {
    await apiFetch(`/posts/${currentPostId}/comments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({
      content: txt
      }),
    });


    $("#commentText").value = "";
    showNotification("Comment added ✅");
    await loadComments(currentPostId);
  } catch (e) {
    showNotification("Comment failed: " + e.message, true);
  }
}


async function deletePost(id) {
  if (!id) return;
  if (!confirm("Delete post?")) return;
  if (!getToken()) return showNotification("Sign in first 🔐", true);

  try {
    await apiFetch(`/posts/${id}`, {
      method: "DELETE",
      headers: { ...authHeaders() },
    });
    showNotification("Deleted ✅");

    if ($("#pageHome").style.display !== "none") loadHome(true);
    if ($("#pageMy").style.display !== "none") loadMy(true);

    if (currentPostId === id) {
      $("#postView").style.display = "none";
      currentPostId = null;
    }
  } catch (e) {
    showNotification("Delete failed: " + e.message, true);
  }
}

async function submitPost(e) {
  e.preventDefault();
  if (!getToken()) return showNotification("Sign in first 🔐", true);

  const form = $("#createForm");
  if (!form) return;

  const title = form.elements.title?.value?.trim() || "";
  const body = form.elements.content?.value?.trim() || "";
  const media_url = form.elements.image?.value?.trim() || "";
  const category_id = form.elements.category?.value?.trim() || "general";
  const tags = (form.elements.tags?.value || "")
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  if (!title || !body) return showNotification("Fill Title + Content", true);

  const payload = {
    author_id: "web",
    content: `${title}\n\n${body}`,
    media_url,
    category_id,
    status: "published",
    tags,
  };

  try {
    if (editingPostId) {
      await apiFetch(`/posts/${editingPostId}`, {
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

    editingPostId = null;
    form.reset();
    closeModal("#modal");

    loadHome(true);
    loadMy(true);
  } catch (e) {
    showNotification("Save failed: " + e.message, true);
  }
}

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

    setUser({ username, email });
    setToken(data.token);

    showNotification("Token saved ✅");
    closeModal("#loginModal");
    form.reset();

    loadMy(true);
  } catch (e) {
    showNotification("Register failed: " + e.message, true);
  }
}

function logout() {
  setToken("");
  setUser(null);
  showNotification("Logged out");
}

function renderProfile() {
  const u = getUser();
  const token = getToken();

  $("#profileUsername").textContent = u?.username || "—";
  $("#profileEmail").textContent = u?.email || "—";
  $("#profileToken").textContent = token || "—";
}

async function copyToken() {
  const token = getToken();
  if (!token) return showNotification("No token to copy", true);
  try {
    await navigator.clipboard.writeText(token);
    showNotification("Token copied ✅");
  } catch {
    showNotification("Copy failed (browser blocked)", true);
  }
}

function clearProfile() {
  setToken("");
  setUser(null);
  showNotification("Profile cleared");
}

function updateAuthUI() {
  const token = getToken();
  const loginBtn = $("#openLogin");
  const logoutBtn = $("#logoutBtn");

  if (loginBtn) loginBtn.style.display = token ? "none" : "";
  if (logoutBtn) logoutBtn.style.display = token ? "" : "none";
}

function wire() {
  $$("#tabs .btn").forEach((b) => {
    b.addEventListener("click", () => {
      const page = b.getAttribute("data-page");
      if (page) showPage(page);
    });
  });

  $("#openCreate")?.addEventListener("click", openCreateModal);
  $("#openLogin")?.addEventListener("click", () => openModal("#loginModal"));
  $("#logoutBtn")?.addEventListener("click", logout);

  $("#closeModal")?.addEventListener("click", () => closeModal("#modal"));
  $("#modalBackdrop")?.addEventListener("click", () => closeModal("#modal"));
  $("#closeLogin")?.addEventListener("click", () => closeModal("#loginModal"));
  $("#loginBackdrop")?.addEventListener("click", () => closeModal("#loginModal"));

  $("#createForm")?.addEventListener("submit", submitPost);
  $("#loginForm")?.addEventListener("submit", submitLogin);

  $("#homeReload")?.addEventListener("click", () => loadHome(true));
  $("#homeLoadMore")?.addEventListener("click", () => loadHome(false));

  $("#myReload")?.addEventListener("click", () => loadMy(true));
  $("#myLoadMore")?.addEventListener("click", () => loadMy(false));

  $("#searchBtn")?.addEventListener("click", () => loadSearch(true));
  $("#searchLoadMore")?.addEventListener("click", () => loadSearch(false));

  $("#openPostBtn")?.addEventListener("click", () => {
    const id = ($("#openPostId")?.value || "").trim();
    openPostById(id, true);
  });

  $("#postRefreshBtn")?.addEventListener("click", () => {
    if (!currentPostId) return;
    openPostById(currentPostId, false);
  });

  $("#postDeleteBtn")?.addEventListener("click", () => {
    if (!currentPostId) return;
    deletePost(currentPostId);
  });

  $("#postEditBtn")?.addEventListener("click", async () => {
    if (!currentPostId) return;
    try {
      const p = await apiFetch(`/posts/${currentPostId}`);
      openEditModal(p);
    } catch (e) {
      showNotification("Edit open failed: " + e.message, true);
    }
  });

  $("#commentForm")?.addEventListener("submit", submitComment);
  $("#commentsReload")?.addEventListener("click", () => {
    if (!currentPostId) return;
    loadComments(currentPostId);
  });

  $("#analyticsReload")?.addEventListener("click", loadAnalytics);

  $("#copyToken")?.addEventListener("click", copyToken);
  $("#clearProfile")?.addEventListener("click", clearProfile);
}

async function loadAnalytics() {
  const ul = $("#topTags");
  const kpi = $("#analyticsKPIs");
  if (!ul) return;

  const limit = Math.max(1, Math.min(50, parseInt($("#analyticsLimit")?.value || "10", 10) || 10));

  try {
    const data = await apiFetch(`/posts/analytics/top-tags?limit=${limit}`);

    ul.innerHTML = data
      .map((t) => `<li>${escapeHtml(t.tag)} — <b>${t.count}</b></li>`)
      .join("");

    if (kpi) {
      const totalTop = data.reduce((s, x) => s + (x.count || 0), 0);
      kpi.innerHTML = `
        <div class="card"><div class="label">Top tags shown</div><div class="value">${data.length}</div></div>
        <div class="card"><div class="label">Total posts (sum in list)</div><div class="value">${totalTop}</div></div>
      `;
    }
  } catch (e) {
    ul.innerHTML = `<li class="muted">Failed to load analytics: ${escapeHtml(e.message)}</li>`;
    if (kpi) kpi.innerHTML = "";
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  updateAuthUI();
  renderProfile();
  wire();
  await pingAPI();
  showPage("home");
});

async function loadReactions(postId) {
  const list = document.getElementById("reactionList");
  const status = document.getElementById("reactionStatus");
  if (!list) return;

  try {
    const data = await apiFetch(`/posts/${postId}/reactions`);
    if (!Array.isArray(data) || data.length === 0) {
      list.innerHTML = `<li class="muted">No reactions yet.</li>`;
      status.textContent = "—";
      return;
    }

    list.innerHTML = data
      .map(r => `<li>${r.reaction} — <b>${r.count}</b></li>`)
      .join("");

    const total = data.reduce((s, r) => s + r.count, 0);
    status.textContent = `total: ${total}`;
  } catch (e) {
    list.innerHTML = `<li class="muted">Failed to load reactions</li>`;
  }
}

async function sendReaction(type) {
  if (!currentPostId) return showNotification("Open a post first", true);
  if (!getToken()) return showNotification("Sign in to react 🔐", true);

  try {
    await apiFetch(
      `/posts/${currentPostId}/reactions?reaction_type=${type}`,
      { method: "POST", headers: authHeaders() }
    );
    showNotification(`Reaction "${type}" saved ✅`);
    loadReactions(currentPostId);
  } catch (e) {
    showNotification("Reaction failed: " + e.message, true);
  }
}

async function removeReaction() {
  if (!currentPostId) return;
  if (!getToken()) return showNotification("Sign in first 🔐", true);

  try {
    await apiFetch(`/posts/${currentPostId}/reactions`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    showNotification("Reaction removed ✅");
    loadReactions(currentPostId);
  } catch (e) {
    showNotification("Remove failed: " + e.message, true);
  }
}


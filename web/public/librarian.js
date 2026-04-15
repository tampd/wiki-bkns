/**
 * Librarian (Thủ thư) — chat + drag-drop staging UI.
 * Depends on global lucide and the auth token in localStorage.wiki_token.
 */
(function () {
  'use strict';

  const SESSION_KEY = 'wiki_librarian_session';
  const $ = (sel) => document.querySelector(sel);

  let sessionId = localStorage.getItem(SESSION_KEY) || null;
  let activated = false;

  function authHeaders(extra = {}) {
    const t = localStorage.getItem('wiki_token') || '';
    return { Authorization: `Bearer ${t}`, ...extra };
  }

  function newSession() {
    sessionId = `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(SESSION_KEY, sessionId);
    clearChat();
  }

  function ensureSession() {
    if (!sessionId) newSession();
    return sessionId;
  }

  // ── Chat rendering ──────────────────────────────────────
  const chatEl = () => $('#librarian-chat');
  const emptyEl = () => $('#chat-empty');

  function clearChat() {
    const c = chatEl();
    if (!c) return;
    c.innerHTML = '<div class="chat-empty" id="chat-empty"><i data-lucide="sparkles" aria-hidden="true"></i><p>Phiên mới — gửi tin hoặc kéo file để bắt đầu.</p></div>';
    if (window.lucide) lucide.createIcons();
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }

  function appendBubble(role, content, opts = {}) {
    const c = chatEl();
    if (!c) return;
    if (emptyEl()) emptyEl().remove();

    const div = document.createElement('div');
    div.className = `chat-bubble chat-${role}`;
    const ts = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    const roleLabel = role === 'user' ? 'Bạn' : role === 'assistant' ? 'Thủ thư' : 'Hệ thống';

    let body = '';
    if (opts.html) {
      body = content;
    } else {
      body = escapeHtml(content).replaceAll('\n', '<br>');
    }

    div.innerHTML = `
      <div class="chat-meta"><span class="chat-role">${roleLabel}</span><span class="chat-ts">${ts}</span></div>
      <div class="chat-body">${body}</div>
    `;
    c.appendChild(div);
    c.scrollTop = c.scrollHeight;
    return div;
  }

  function appendTyping() {
    const c = chatEl();
    const div = document.createElement('div');
    div.className = 'chat-bubble chat-assistant chat-typing';
    div.innerHTML = '<div class="chat-meta"><span class="chat-role">Thủ thư</span></div><div class="chat-body"><span class="dot-pulse"></span><span class="dot-pulse"></span><span class="dot-pulse"></span></div>';
    c.appendChild(div);
    c.scrollTop = c.scrollHeight;
    return div;
  }

  function fmtStaged(items) {
    return items.map((it) => {
      const conf = (it.confidence * 100).toFixed(0);
      const review = it.needs_review ? ' ⚠️ <em>cần review</em>' : '';
      return `<div class="staged-item">
        <strong>📎 ${escapeHtml(it.filename)}</strong>
        → <code>${escapeHtml(it.category)}/${escapeHtml(it.type)}</code>
        <span class="staged-conf">${conf}%</span>${review}
        <div class="staged-path">${escapeHtml(it.suggested_path)}</div>
      </div>`;
    }).join('');
  }

  // ── API calls ───────────────────────────────────────────
  async function sendChat(message) {
    const res = await fetch('/api/librarian/chat', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ message, sessionId: ensureSession() }),
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `HTTP ${res.status}`);
    const data = await res.json();
    if (data.sessionId) {
      sessionId = data.sessionId;
      localStorage.setItem(SESSION_KEY, sessionId);
    }
    return data;
  }

  async function uploadFiles(files) {
    const fd = new FormData();
    for (const f of files) fd.append('files', f);
    fd.append('sessionId', ensureSession());
    const res = await fetch('/api/librarian/upload', {
      method: 'POST',
      headers: authHeaders(),
      body: fd,
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `HTTP ${res.status}`);
    return res.json();
  }

  async function loadStatus() {
    try {
      const res = await fetch('/api/librarian/status', { headers: authHeaders() });
      if (!res.ok) return;
      const s = await res.json();
      const set = (id, v) => { const el = $(id); if (el) el.textContent = v; };
      set('#lib-stat-today', s.inbox_today ?? 0);
      set('#lib-stat-review', s.inbox_review ?? 0);
      set('#lib-stat-processed', s.processed_total ?? 0);

      const total = (s.inbox_today || 0) + (s.inbox_review || 0);
      const badge = $('#librarian-badge');
      if (badge) {
        if (total > 0) { badge.textContent = String(total); badge.style.display = ''; }
        else badge.style.display = 'none';
      }
    } catch (_) {}
  }

  async function triggerNow() {
    const btn = $('#btn-librarian-trigger');
    if (btn) { btn.disabled = true; btn.textContent = 'Đang xử lý...'; }
    appendBubble('system', '⏳ Đang chạy processor...', {});
    try {
      const res = await fetch('/api/librarian/trigger', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      const r = data.report || {};
      const summary = `✅ Hoàn tất. Đã xử lý <strong>${r.processed ?? '?'}</strong>, lỗi <strong>${r.errors ?? 0}</strong>, cần review <strong>${r.review ?? 0}</strong>.`;
      appendBubble('system', summary, { html: true });
      loadStatus();
    } catch (e) {
      appendBubble('system', `❌ Lỗi: ${escapeHtml(e.message)}`, { html: true });
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i data-lucide="play" aria-hidden="true"></i> Xử lý ngay';
        if (window.lucide) lucide.createIcons();
      }
    }
  }

  // ── Event wiring ────────────────────────────────────────
  function autoGrow(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 180) + 'px';
  }

  function wire() {
    const form = $('#librarian-composer');
    const input = $('#librarian-input');
    const dropzone = $('#librarian-dropzone');
    const fileInput = $('#librarian-file-input');
    const btnPick = $('#btn-pick-files');
    const btnNew = $('#btn-librarian-new-session');
    const btnTrig = $('#btn-librarian-trigger');

    if (!form || form.dataset.wired) return;
    form.dataset.wired = '1';

    input.addEventListener('input', () => autoGrow(input));
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        form.requestSubmit();
      }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      autoGrow(input);
      appendBubble('user', text);
      const typing = appendTyping();
      try {
        const data = await sendChat(text);
        typing.remove();
        appendBubble('assistant', data.reply || '(không có phản hồi)');
      } catch (err) {
        typing.remove();
        appendBubble('system', `❌ ${escapeHtml(err.message)}`, { html: true });
      }
    });

    btnPick?.addEventListener('click', () => fileInput.click());
    dropzone?.addEventListener('click', (e) => {
      if (e.target.id !== 'btn-pick-files') fileInput.click();
    });
    dropzone?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fileInput.click(); }
    });

    ['dragenter', 'dragover'].forEach((ev) =>
      dropzone?.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); })
    );
    ['dragleave', 'drop'].forEach((ev) =>
      dropzone?.addEventListener(ev, (e) => { e.preventDefault(); dropzone.classList.remove('drag-over'); })
    );
    dropzone?.addEventListener('drop', async (e) => {
      const files = Array.from(e.dataTransfer.files || []);
      if (files.length) await handleFiles(files);
    });
    fileInput?.addEventListener('change', async (e) => {
      const files = Array.from(e.target.files || []);
      if (files.length) await handleFiles(files);
      fileInput.value = '';
    });

    btnNew?.addEventListener('click', () => {
      newSession();
      appendBubble('system', 'Đã bắt đầu phiên mới.');
    });

    btnTrig?.addEventListener('click', triggerNow);
  }

  async function handleFiles(files) {
    appendBubble('user', `📤 Đang upload ${files.length} file...`);
    const typing = appendTyping();
    try {
      const data = await uploadFiles(files);
      typing.remove();
      appendBubble('assistant', `Đã staging ${data.staged.length} file:<br>${fmtStaged(data.staged)}`, { html: true });
      loadStatus();
    } catch (err) {
      typing.remove();
      appendBubble('system', `❌ Upload lỗi: ${escapeHtml(err.message)}`, { html: true });
    }
  }

  function activate() {
    wire();
    loadStatus();
    if (!activated) {
      activated = true;
      setInterval(loadStatus, 30_000);
    }
  }

  window.Librarian = { activate, newSession };
})();

/**
 * BKNS Wiki Admin Portal — Client Application
 * Handles: Login, Wiki Viewer/Editor, Upload, Pipeline, Search
 */

(function () {
  'use strict';

  // ============================================================
  // CONFIG & STATE
  // ============================================================
  const API = '';
  const MAX_FILE_SIZE = 50 * 1024 * 1024;
  const ALLOWED_TYPES = ['.pdf', '.docx', '.xlsx', '.md', '.txt', '.png', '.jpg', '.jpeg'];
  const FILE_TYPE_MAP = {
    '.pdf': { label: 'PDF', cls: 'pdf' }, '.docx': { label: 'DOC', cls: 'doc' },
    '.doc': { label: 'DOC', cls: 'doc' }, '.xlsx': { label: 'XLS', cls: 'xls' },
    '.xls': { label: 'XLS', cls: 'xls' }, '.md': { label: 'MD', cls: 'md' },
    '.txt': { label: 'TXT', cls: 'txt' }, '.png': { label: 'PNG', cls: 'img' },
    '.jpg': { label: 'JPG', cls: 'img' }, '.jpeg': { label: 'JPG', cls: 'img' },
  };

  let state = {
    token: localStorage.getItem('wiki_token') || '',
    fileQueue: [],
    currentPage: 1,
    currentSource: 'all',
    statusInterval: null,
    // App state
    currentTab: 'wiki',
    // Wiki state
    wikiTree: null,
    wikiCurrentCategory: null,
    wikiCurrentPage: null,
    wikiContent: '',
    wikiMode: 'read', // 'read' | 'edit'
    wikiDirty: false,
    wikiEditor: null, // Toast UI Editor instance
    searchDebounce: null,
  };

  // ============================================================
  // HELPERS
  // ============================================================
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);
  function escapeHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }
  function formatSize(b) { if (!b) return '0 B'; const u = ['B', 'KB', 'MB', 'GB']; const i = Math.floor(Math.log(b) / Math.log(1024)); return (b / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + u[i]; }
  function formatDate(iso) { if (!iso) return '—'; return new Date(iso).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }); }
  function getFileExt(n) { const i = n.lastIndexOf('.'); return i > 0 ? n.substring(i).toLowerCase() : ''; }
  function getFileTypeInfo(n) { return FILE_TYPE_MAP[getFileExt(n)] || { label: 'FILE', cls: 'txt' }; }

  async function apiFetch(path, options = {}) {
    const res = await fetch(API + path, {
      ...options,
      headers: { 'Authorization': 'Bearer ' + state.token, ...(options.headers || {}) },
    });
    if (res.status === 401) { logout(); throw new Error('Unauthorized'); }
    return res;
  }

  // ============================================================
  // TOAST SYSTEM
  // ============================================================
  function toast(type, title, message, duration = 5000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ️'}</span>
      <div class="toast-content"><div class="toast-title">${escapeHtml(title)}</div>
      ${message ? '<div class="toast-message">' + escapeHtml(message) + '</div>' : ''}</div>
      <button class="toast-close" aria-label="Đóng">&times;</button>`;
    el.querySelector('.toast-close').addEventListener('click', () => removeToast(el));
    $('#toast-container').appendChild(el);
    if (duration > 0) setTimeout(() => removeToast(el), duration);
    return el;
  }
  function removeToast(el) { if (!el.parentNode) return; el.classList.add('removing'); setTimeout(() => el.remove(), 200); }

  // ============================================================
  // MODAL SYSTEM
  // ============================================================
  let modalResolve = null;
  function showModal(title, message, confirmText = 'Xác nhận') {
    const overlay = $('#modal-overlay');
    $('#modal-title').textContent = title;
    $('#modal-message').textContent = message;
    $('#modal-confirm').textContent = confirmText;
    $('#modal-cancel').style.display = '';
    overlay.classList.add('active');
    $('#modal-confirm').focus();
    return new Promise(r => { modalResolve = r; });
  }
  function closeModal(result) {
    $('#modal-overlay').classList.remove('active');
    if (modalResolve) { modalResolve(result); modalResolve = null; }
  }
  $('#modal-cancel').addEventListener('click', () => closeModal(false));
  $('#modal-confirm').addEventListener('click', () => closeModal(true));
  $('#modal-overlay').addEventListener('click', e => { if (e.target === $('#modal-overlay')) closeModal(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && $('#modal-overlay').classList.contains('active')) closeModal(false); });

  // ============================================================
  // AUTH
  // ============================================================
  $('#login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const pw = $('#login-password').value.trim();
    if (!pw) return;
    $('#login-submit').disabled = true;
    $('#login-btn-text').style.display = 'none';
    $('#login-spinner').style.display = 'block';
    $('#login-error').classList.remove('visible');
    try {
      const res = await fetch(API + '/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pw }) });
      if (res.ok) { const d = await res.json(); state.token = d.token; localStorage.setItem('wiki_token', d.token); showApp(); }
      else { $('#login-error').classList.add('visible'); $('#login-password').focus(); }
    } catch { $('#login-error').textContent = 'Không thể kết nối server.'; $('#login-error').classList.add('visible'); }
    finally { $('#login-submit').disabled = false; $('#login-btn-text').style.display = 'inline'; $('#login-spinner').style.display = 'none'; }
  });

  function logout() {
    state.token = '';
    localStorage.removeItem('wiki_token');
    $('#app').classList.remove('active');
    $('#login-page').style.display = '';
    if (state.statusInterval) clearInterval(state.statusInterval);
  }
  $('#btn-logout').addEventListener('click', async () => { const ok = await showModal('Đăng xuất', 'Bạn có chắc chắn?', 'Đăng xuất'); if (ok) logout(); });

  function showApp() {
    $('#login-page').style.display = 'none';
    $('#app').classList.add('active');
    lucide.createIcons();
    switchTab('wiki');
    loadWikiTree().then(() => setTimeout(updateSidebarHealthDots, 500));
    state.statusInterval = setInterval(loadStatus, 15000);
    loadStatus();
  }

  // ============================================================
  // TAB NAVIGATION
  // ============================================================
  function switchTab(tabName) {
    state.currentTab = tabName;
    $$('.nav-tab').forEach(btn => {
      const active = btn.dataset.tab === tabName;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    // Hide all tabs
    ['wiki', 'dashboard', 'review', 'history', 'librarian'].forEach(t => {
      const el = $(`#tab-${t}`);
      if (el) el.style.display = 'none';
    });
    // Show selected
    const el = $(`#tab-${tabName}`);
    if (el) el.style.display = tabName === 'wiki' ? 'flex' : 'block';

    if (tabName === 'dashboard') { loadDashboard(); loadChangelog(); }
    if (tabName === 'review') { loadReviewStats(); loadReviewQueue(); loadDualQueue(); }
    if (tabName === 'history') { loadHealth(); loadBuilds(); loadActivity(); }
    if (tabName === 'librarian' && window.Librarian) window.Librarian.activate();
    lucide.createIcons();
  }

  $$('.nav-tab').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (btn.dataset.tab === state.currentTab) return;
      // Warn if wiki editor has unsaved changes
      if (state.wikiDirty && state.currentTab === 'wiki') {
        const ok = await showModal('Chưa lưu', 'Bạn có thay đổi chưa lưu. Chuyển tab sẽ mất dữ liệu.', 'Chuyển tab');
        if (!ok) return;
        state.wikiDirty = false;
      }
      switchTab(btn.dataset.tab);
    });
  });

  // ============================================================
  // WIKI — SIDEBAR TREE
  // ============================================================
  async function loadWikiTree() {
    try {
      const res = await apiFetch('/api/wiki/tree');
      if (!res.ok) return;
      const data = await res.json();
      state.wikiTree = data.tree;
      renderTree(data.tree);
      // Show stats on welcome page
      const statsEl = $('#welcome-stats');
      if (statsEl) {
        statsEl.innerHTML = `
          <div class="welcome-stat"><div class="welcome-stat-value">${data.tree.length}</div><div class="welcome-stat-label">Categories</div></div>
          <div class="welcome-stat"><div class="welcome-stat-value">${data.total}</div><div class="welcome-stat-label">Trang wiki</div></div>`;
      }
    } catch { /* silent */ }
  }

  function renderTree(tree) {
    const container = $('#sidebar-tree');
    if (!tree || tree.length === 0) {
      container.innerHTML = '<div class="sidebar-tree-loading">Chưa có wiki nào</div>';
      return;
    }

    const CATEGORY_ICONS = {
      hosting: 'server', vps: 'cloud', ssl: 'shield-check', 'ten-mien': 'globe',
      email: 'mail', server: 'hard-drive', software: 'package', other: 'folder', uncategorized: 'help-circle',
    };

    container.innerHTML = tree.map(cat => {
      const icon = CATEGORY_ICONS[cat.category] || 'folder';
      const pagesHtml = cat.pages.map(p => `
        <button class="tree-page-btn" data-category="${cat.category}" data-page="${p.page}" title="${escapeHtml(p.title)}">
          <i data-lucide="file-text" aria-hidden="true"></i>
          ${escapeHtml(p.label)}
        </button>
      `).join('');

      let productsHtml = '';
      if (cat.products.length > 0) {
        productsHtml = `<div class="tree-product-group"><div class="tree-product-label">Sản phẩm (${cat.products.length})</div>` +
          cat.products.map(p => `
            <button class="tree-page-btn tree-product-btn" data-category="${cat.category}" data-page="${p.page}" title="${escapeHtml(p.title)}">
              <i data-lucide="package" aria-hidden="true"></i>
              ${escapeHtml(p.label)}
            </button>
          `).join('') + '</div>';
      }

      return `
        <div class="tree-category" data-cat="${cat.category}">
          <button class="tree-category-btn" data-cat="${cat.category}">
            <i data-lucide="chevron-right" aria-hidden="true"></i>
            <i data-lucide="${icon}" aria-hidden="true" style="width:16px;height:16px;opacity:0.6"></i>
            <span class="tree-category-label">${escapeHtml(cat.label)}</span>
            <span class="tree-category-count">${cat.totalPages}</span>
          </button>
          <div class="tree-pages" data-cat="${cat.category}">
            ${pagesHtml}
            ${productsHtml}
          </div>
        </div>`;
    }).join('');

    lucide.createIcons();
    bindTreeEvents();
  }

  function bindTreeEvents() {
    $$('.tree-category-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.cat;
        const pages = $(`.tree-pages[data-cat="${cat}"]`);
        const isOpen = pages.classList.contains('open');
        pages.classList.toggle('open');
        btn.classList.toggle('expanded', !isOpen);
      });
    });

    $$('.tree-page-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const cat = btn.dataset.category;
        const page = btn.dataset.page;
        navigateToPage(cat, page);
      });
    });
  }

  // Auto-expand category
  function expandCategory(cat) {
    const pages = $(`.tree-pages[data-cat="${cat}"]`);
    const btn = $(`.tree-category-btn[data-cat="${cat}"]`);
    if (pages && !pages.classList.contains('open')) {
      pages.classList.add('open');
      if (btn) btn.classList.add('expanded');
    }
  }

  function highlightTreeItem(cat, page) {
    $$('.tree-page-btn.active').forEach(b => b.classList.remove('active'));
    const pageKey = page.replace(/\//g, '__');
    const btn = $(`.tree-page-btn[data-category="${cat}"][data-page="${page}"]`);
    if (btn) btn.classList.add('active');
  }

  $('#btn-refresh-tree').addEventListener('click', () => loadWikiTree());

  // ============================================================
  // WIKI — PAGE NAVIGATION
  // ============================================================
  async function navigateToPage(category, page) {
    try {
      const pageParam = page.replace(/\//g, '__');
      const res = await apiFetch(`/api/wiki/${category}/${pageParam}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Lỗi', err.error || 'Không thể tải trang');
        return;
      }
      const data = await res.json();

      state.wikiCurrentCategory = category;
      state.wikiCurrentPage = page;
      state.wikiContent = data.content;
      state.wikiDirty = false;

      // Update UI
      $('#wiki-welcome').style.display = 'none';
      $('#wiki-content').style.display = 'flex';

      // Breadcrumb
      const catTree = state.wikiTree?.find(c => c.category === category);
      $('#bc-category').textContent = catTree?.label || category;
      $('#bc-page').textContent = data.label || page;

      // Meta
      const mtime = data.mtime ? formatDate(data.mtime) : '';
      const size = data.size ? formatSize(data.size) : '';
      $('#wiki-meta').textContent = `${mtime} • ${size}`;

      // Render content
      renderWikiArticle(data.body || data.content);
      expandCategory(category);
      highlightTreeItem(category, page);

      // Switch to read mode
      setMode('read');

      // Hide save button
      $('#btn-save').style.display = 'none';
      lucide.createIcons();

    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  // Wiki rendering
  function renderWikiArticle(markdown) {
    const article = $('#wiki-article');
    if (typeof marked === 'undefined') { article.innerHTML = '<em>marked.js chưa tải</em>'; return; }

    try {
      const html = marked.parse(markdown, { breaks: true, gfm: true });
      const wrapper = document.createElement('div');
      wrapper.innerHTML = html;

      // Process links
      wrapper.querySelectorAll('a[href]').forEach(a => {
        const href = a.getAttribute('href');
        if (href && href.endsWith('.md') && !href.startsWith('http')) {
          let parts = href.replace(/\.md$/, '').split('/');
          // Resolve `..` relative to current page's directory so links from
          // nested pages (e.g. san-pham/foo.md → ../bang-gia.md) work.
          if (parts.includes('..') || parts.includes('.')) {
            const currentPageParts = (state.wikiCurrentPage || 'index').split('/');
            const stack = [state.wikiCurrentCategory, ...currentPageParts.slice(0, -1)];
            for (const p of parts) {
              if (p === '..') { if (stack.length > 0) stack.pop(); }
              else if (p === '.' || p === '') { /* skip */ }
              else { stack.push(p); }
            }
            parts = stack;
          }
          const cat = parts.length >= 2 ? parts[0] : state.wikiCurrentCategory;
          const pg = parts.length >= 2 ? parts.slice(1).join('/') : parts[0];
          a.setAttribute('href', '#');
          a.setAttribute('data-wiki-cat', cat);
          a.setAttribute('data-wiki-page', pg);
          a.style.cursor = 'pointer';
        } else if (href && href.startsWith('http')) {
          a.setAttribute('target', '_blank');
          a.setAttribute('rel', 'noopener noreferrer');
        }
      });

      // Add IDs to headings for ToC
      let headingCount = 0;
      wrapper.querySelectorAll('h1, h2, h3, h4').forEach(h => {
        const id = 'h-' + (++headingCount);
        h.id = id;
      });

      article.innerHTML = wrapper.innerHTML;

      // Bind wiki links
      article.querySelectorAll('[data-wiki-cat]').forEach(a => {
        a.addEventListener('click', e => {
          e.preventDefault();
          navigateToPage(a.dataset.wikiCat, a.dataset.wikiPage);
        });
      });

      // Build ToC
      buildToc(article);

    } catch { article.innerHTML = '<em>Lỗi render markdown</em>'; }
  }

  // Table of Contents
  function buildToc(article) {
    const tocList = $('#toc-list');
    const headings = article.querySelectorAll('h1, h2, h3, h4');
    if (headings.length === 0) {
      tocList.innerHTML = '<li style="font-size:11px;color:var(--color-text-muted)">Không có mục lục</li>';
      return;
    }

    tocList.innerHTML = [...headings].map(h => {
      const level = h.tagName.toLowerCase();
      const cls = level === 'h3' ? ' toc-h3' : level === 'h4' ? ' toc-h4' : '';
      return `<li><a href="#${h.id}" class="${cls}">${escapeHtml(h.textContent)}</a></li>`;
    }).join('');

    // Click handler
    tocList.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', e => {
        e.preventDefault();
        const target = document.getElementById(a.getAttribute('href').slice(1));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Highlight active
        tocList.querySelectorAll('a').forEach(l => l.classList.remove('active'));
        a.classList.add('active');
      });
    });
  }

  // ============================================================
  // WIKI — MODE TOGGLE (Read/Edit)
  // ============================================================
  function setMode(mode) {
    state.wikiMode = mode;
    $$('.mode-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.mode === mode);
    });

    if (mode === 'read') {
      $('#wiki-reader-layout').style.display = 'flex';
      $('#wiki-editor-layout').style.display = 'none';
      $('#btn-save').style.display = 'none';
    } else {
      $('#wiki-reader-layout').style.display = 'none';
      $('#wiki-editor-layout').style.display = 'block';
      $('#btn-save').style.display = '';
      initEditor();
    }
    lucide.createIcons();
  }

  $$('.mode-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.dataset.mode === state.wikiMode) return;
      if (state.wikiMode === 'edit' && state.wikiDirty) {
        showModal('Thay đổi chưa lưu', 'Bạn có muốn rời khỏi editor?', 'Rời đi').then(ok => {
          if (ok) { state.wikiDirty = false; setMode(btn.dataset.mode); }
        });
        return;
      }
      setMode(btn.dataset.mode);
    });
  });

  // ============================================================
  // WIKI — TOAST UI EDITOR
  // ============================================================
  function initEditor() {
    const editorEl = $('#toast-editor');
    editorEl.innerHTML = '';

    // Strip frontmatter for editing
    const content = state.wikiContent || '';
    const fmMatch = content.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
    const bodyContent = fmMatch ? fmMatch[1] : content;
    const frontmatterBlock = fmMatch ? content.slice(0, content.length - fmMatch[1].length) : '';

    // Store frontmatter for later
    editorEl.dataset.frontmatter = frontmatterBlock;

    try {
      const ToastEditor = toastui.Editor;
      state.wikiEditor = new ToastEditor({
        el: editorEl,
        height: 'calc(100dvh - 160px)',
        initialEditType: 'wysiwyg',
        previewStyle: 'vertical',
        initialValue: bodyContent,
        usageStatistics: false,
        hideModeSwitch: false,
        toolbarItems: [
          ['heading', 'bold', 'italic', 'strike'],
          ['hr', 'quote'],
          ['ul', 'ol', 'task'],
          ['table', 'image', 'link'],
          ['code', 'codeblock'],
          ['scrollSync'],
        ],
        events: {
          change: () => {
            if (!state.wikiDirty) {
              state.wikiDirty = true;
              $('#btn-save').classList.add('btn-success');
              $('#btn-save').classList.remove('btn-primary');
            }
          },
        },
      });
    } catch (e) {
      console.error('Toast UI Editor init failed:', e);
      // Fallback to textarea
      editorEl.innerHTML = `<textarea style="width:100%;height:calc(100dvh - 160px);background:var(--color-bg);color:var(--color-text);border:1px solid var(--color-border);padding:1rem;font-family:var(--font-mono);font-size:14px;resize:none" id="fallback-editor">${escapeHtml(bodyContent)}</textarea>`;
      state.wikiEditor = {
        getMarkdown: () => $('#fallback-editor').value,
      };
    }
  }

  // Save
  $('#btn-save').addEventListener('click', async () => {
    if (!state.wikiCurrentCategory || !state.wikiCurrentPage) return;
    if (!state.wikiEditor) return;

    const body = state.wikiEditor.getMarkdown();
    const frontmatter = $('#toast-editor').dataset.frontmatter || '';

    // Update frontmatter dates
    let updatedFm = frontmatter;
    const today = new Date().toISOString().slice(0, 10);
    if (updatedFm.includes('updated:')) {
      updatedFm = updatedFm.replace(/updated:.*/, `updated: "${today}"`);
    }
    const fullContent = updatedFm + body;

    try {
      const pageParam = state.wikiCurrentPage.replace(/\//g, '__');
      const res = await apiFetch(`/api/wiki/${state.wikiCurrentCategory}/${pageParam}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: fullContent }),
      });

      if (res.ok) {
        state.wikiContent = fullContent;
        state.wikiDirty = false;
        toast('success', 'Đã lưu', `${state.wikiCurrentCategory}/${state.wikiCurrentPage}`);
        $('#btn-save').classList.remove('btn-success');
        $('#btn-save').classList.add('btn-primary');
        // Re-render reader
        const fmMatch2 = fullContent.match(/^---\n[\s\S]*?\n---\n([\s\S]*)$/);
        renderWikiArticle(fmMatch2 ? fmMatch2[1] : fullContent);
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Lưu thất bại', err.error || 'Lỗi');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  });

  // Keyboard shortcut: Ctrl+S
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's' && state.wikiMode === 'edit') {
      e.preventDefault();
      $('#btn-save').click();
    }
  });

  // ============================================================
  // WIKI — SEARCH
  // ============================================================
  const searchInput = $('#wiki-search-input');
  const searchResultsEl = $('#search-results');
  const searchListEl = $('#search-results-list');

  searchInput.addEventListener('input', () => {
    clearTimeout(state.searchDebounce);
    const q = searchInput.value.trim();
    if (q.length < 2) {
      searchResultsEl.style.display = 'none';
      $('#sidebar-tree').style.display = '';
      return;
    }
    state.searchDebounce = setTimeout(() => performSearch(q), 300);
  });

  async function performSearch(query) {
    try {
      const res = await apiFetch(`/api/wiki/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) return;
      const data = await res.json();

      $('#search-results-count').textContent = `${data.total} kết quả`;
      searchResultsEl.style.display = '';
      $('#sidebar-tree').style.display = 'none';

      if (data.results.length === 0) {
        searchListEl.innerHTML = '<li class="search-result-item" style="text-align:center;color:var(--color-text-muted)">Không tìm thấy</li>';
        return;
      }

      searchListEl.innerHTML = data.results.map(r => {
        const snippet = r.snippet ? escapeHtml(r.snippet).replace(new RegExp(`(${escapeHtml(query)})`, 'gi'), '<mark>$1</mark>') : '';
        return `<li class="search-result-item" data-cat="${r.category}" data-page="${r.page}">
          <div class="search-result-title">${escapeHtml(r.title)}</div>
          <div class="search-result-path">${r.categoryLabel} / ${r.page}</div>
          ${snippet ? '<div class="search-result-snippet">' + snippet + '</div>' : ''}
        </li>`;
      }).join('');

      searchListEl.querySelectorAll('.search-result-item[data-cat]').forEach(item => {
        item.addEventListener('click', () => {
          navigateToPage(item.dataset.cat, item.dataset.page);
          clearSearch();
        });
      });
    } catch { /* silent */ }
  }

  function clearSearch() {
    searchInput.value = '';
    searchResultsEl.style.display = 'none';
    $('#sidebar-tree').style.display = '';
  }

  $('#btn-clear-search').addEventListener('click', clearSearch);

  // Ctrl+K shortcut
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (!state.token) return; // Not logged in
      if (state.currentTab !== 'wiki') switchTab('wiki');
      searchInput.focus();
    }
  });

  // ============================================================
  // WIKI — BACKUPS
  // ============================================================
  $('#btn-backups').addEventListener('click', async () => {
    if (!state.wikiCurrentCategory || !state.wikiCurrentPage) return;
    const drawer = $('#backups-drawer');
    const isOpen = drawer.style.display !== 'none';
    if (isOpen) { drawer.style.display = 'none'; return; }

    try {
      const pageParam = state.wikiCurrentPage.replace(/\//g, '__');
      const res = await apiFetch(`/api/wiki/${state.wikiCurrentCategory}/${pageParam}/backups`);
      if (!res.ok) return;
      const data = await res.json();

      const listEl = $('#backups-list');
      if (data.backups.length === 0) {
        listEl.innerHTML = '<li class="backups-empty">Chưa có backup nào</li>';
      } else {
        listEl.innerHTML = data.backups.map(b =>
          `<li data-filename="${escapeHtml(b.filename)}">
            <div style="display:flex;align-items:center;justify-content:space-between;gap:var(--space-2)">
              <div>
                <div style="font-weight:500">${escapeHtml(b.filename)}</div>
                <div style="color:var(--color-text-muted);margin-top:2px">${formatDate(b.mtime)} • ${formatSize(b.size)}</div>
              </div>
              <button class="btn btn-ghost btn-xs backup-restore-btn" data-file="${escapeHtml(b.filename)}" title="Khôi phục">
                <i data-lucide="undo-2" aria-hidden="true"></i> Restore
              </button>
            </div>
          </li>`
        ).join('');

        // Restore handlers
        listEl.querySelectorAll('.backup-restore-btn').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const filename = btn.dataset.file;
            const ok = await showModal('Khôi phục backup', `Khôi phục từ ${filename}? Phiên bản hiện tại sẽ được backup trước.`, 'Khôi phục');
            if (!ok) return;
            try {
              const pageParam = state.wikiCurrentPage.replace(/\//g, '__');
              const r = await apiFetch(`/api/wiki/${state.wikiCurrentCategory}/${pageParam}/restore`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename }),
              });
              if (r.ok) {
                toast('success', 'Đã khôi phục', filename);
                state.wikiDirty = false;
                navigateToPage(state.wikiCurrentCategory, state.wikiCurrentPage);
                drawer.style.display = 'none';
              } else {
                const err = await r.json().catch(() => ({}));
                toast('error', 'Restore thất bại', err.error || 'Lỗi');
              }
            } catch (ex) { toast('error', 'Lỗi', ex.message); }
          });
        });
      }
      drawer.style.display = '';
      lucide.createIcons();
    } catch { toast('error', 'Lỗi tải backups'); }
  });

  $('#btn-close-backups').addEventListener('click', () => { $('#backups-drawer').style.display = 'none'; });

  // ============================================================
  // WIKI — CREATE PAGE
  // ============================================================
  const createModal = $('#create-page-modal');

  $('#btn-new-page').addEventListener('click', () => {
    // Populate category dropdown
    const select = $('#cp-category');
    select.innerHTML = (state.wikiTree || []).map(c =>
      `<option value="${c.category}">${escapeHtml(c.label)}</option>`
    ).join('');
    if (state.wikiCurrentCategory) select.value = state.wikiCurrentCategory;
    createModal.style.display = 'flex';
    lucide.createIcons();
  });

  $('#cp-cancel').addEventListener('click', () => { createModal.style.display = 'none'; });
  createModal.addEventListener('click', e => { if (e.target === createModal) createModal.style.display = 'none'; });

  $('#create-page-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const category = $('#cp-category').value;
    const page = $('#cp-page').value.trim();
    const title = $('#cp-title').value.trim();
    const template = $('#cp-template').value;

    if (!page || !title) return;

    try {
      const res = await apiFetch(`/api/wiki/${category}/${page}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, template }),
      });

      if (res.ok) {
        const data = await res.json();
        toast('success', 'Tạo trang thành công', `${category}/${page}`);
        createModal.style.display = 'none';
        await loadWikiTree();
        navigateToPage(category, page);
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Tạo trang thất bại', err.error || 'Lỗi');
      }
    } catch (e) {
      toast('error', 'Lỗi', e.message);
    }
  });

  // ============================================================
  // DASHBOARD
  // ============================================================
  async function loadBuildsHistory() {
    const tbody = $('#build-history-tbody');
    if (!tbody) return;
    try {
      const res = await apiFetch('/api/builds');
      if (!res.ok) { tbody.innerHTML = '<tr><td colspan="6" class="files-empty">Không thể tải</td></tr>'; return; }
      const data = await res.json();
      if (!data.builds?.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="files-empty">Chưa có build nào</td></tr>';
        return;
      }
      tbody.innerHTML = data.builds.map((b, i) => {
        const isLatest = i === 0;
        const tokens = b.wiki_token_estimate > 0
          ? (b.wiki_token_estimate / 1000).toFixed(1) + 'K'
          : '—';
        const date = b.build_date ? new Date(b.build_date).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—';
        return `<tr>
          <td><code style="font-size:var(--text-xs)">${escapeHtml(b.display)}</code>${isLatest ? ' <span style="font-size:0.6rem;background:#00b894;color:#fff;padding:1px 5px;border-radius:3px;vertical-align:middle">LATEST</span>' : ''}</td>
          <td style="font-weight:600">${escapeHtml(b.version || '—')}</td>
          <td>${b.wiki_files || 0}</td>
          <td>${b.claims_count || 0}</td>
          <td style="color:var(--color-text-muted)">${tokens}</td>
          <td style="color:var(--color-text-muted);font-size:var(--text-xs)">${date}</td>
        </tr>`;
      }).join('');
    } catch (e) {
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" class="files-empty">Lỗi: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  async function loadDashboard() {
    loadBuildsHistory();
    // Fetch status and review stats in parallel
    const [statusRes, reviewRes] = await Promise.allSettled([
      apiFetch('/api/status').catch(() => null),
      apiFetch('/api/review/stats').catch(() => null),
    ]);

    // Populate status stats
    try {
      const res = statusRes.status === 'fulfilled' ? statusRes.value : null;
      if (res && res.ok) {
        const data = await res.json();
        if (data.wiki_stats) {
          const s = data.wiki_stats;
          if ($('#stat-wiki-categories')) $('#stat-wiki-categories').textContent = s.wiki_categories || '0';
          if ($('#stat-wiki-pages')) $('#stat-wiki-pages').textContent = s.wiki_pages || '0';
          if ($('#stat-claims')) $('#stat-claims').textContent = s.total_claims || '0';
          if ($('#stat-last-build')) $('#stat-last-build').textContent = s.build_version || '—';
        }
      }
    } catch { /* silent */ }

    // Populate review quality stats
    try {
      const res = reviewRes.status === 'fulfilled' ? reviewRes.value : null;
      if (res && res.ok) {
        const s = await res.json();
        if ($('#stat-gt-ratio')) $('#stat-gt-ratio').textContent = (s.ground_truth_ratio || '0') + '%';
        if ($('#stat-review-pending')) $('#stat-review-pending').textContent = s.by_state?.pending || '0';
        if ($('#stat-review-approved')) $('#stat-review-approved').textContent = s.by_state?.approved || '0';
        if ($('#stat-conflicts')) $('#stat-conflicts').textContent = s.conflicts || '0';

        // Build quality grid
        const grid = $('#quality-grid');
        if (grid && s.by_confidence) {
          const total = s.total || 1;
          const conf = s.by_confidence;
          const confItems = [
            { label: 'Ground Truth', key: 'ground_truth', color: '#00b894' },
            { label: 'High', key: 'high', color: '#0984e3' },
            { label: 'Medium', key: 'medium', color: '#fdcb6e' },
            { label: 'Low', key: 'low', color: '#e17055' },
          ];
          grid.innerHTML = confItems.map(item => {
            const count = conf[item.key] || 0;
            const pct = ((count / total) * 100).toFixed(1);
            return `<div class="quality-item">
              <div class="quality-label">${escapeHtml(item.label)}</div>
              <div class="quality-bar-wrap">
                <div class="quality-bar" style="width:${pct}%;background:${item.color}" title="${count} claims"></div>
              </div>
              <div class="quality-count">${count} <span style="color:var(--color-text-muted)">(${pct}%)</span></div>
            </div>`;
          }).join('') + (s.by_state ? `<div class="quality-item" style="margin-top:var(--space-3);border-top:1px solid var(--color-border);padding-top:var(--space-3)">
            <div class="quality-label" style="font-weight:600">Review Status</div>
            <div class="quality-count" style="gap:var(--space-3);display:flex;flex-wrap:wrap">
              <span style="color:#00b894">✓ ${s.by_state.approved || 0} approved</span>
              <span style="color:#fdcb6e">⏳ ${s.by_state.pending || 0} pending</span>
              <span style="color:#e17055">⚑ ${s.by_state.flagged || 0} flagged</span>
              <span style="color:#b2bec3">✗ ${s.by_state.rejected || 0} rejected</span>
            </div>
          </div>` : '');
        }
      }
    } catch { /* silent */ }
  }

  // ============================================================
  // INTEGRITY CHECKER
  // ============================================================
  $('#btn-integrity-check')?.addEventListener('click', async () => {
    const btn = $('#btn-integrity-check');
    const resultsEl = $('#integrity-results');
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader-2" class="spin" aria-hidden="true"></i> Đang quét...';
    lucide.createIcons();
    resultsEl.innerHTML = '<div style="color:var(--color-text-muted);padding:var(--space-3)">Đang kiểm tra...</div>';

    try {
      const res = await apiFetch('/api/wiki/integrity');
      if (!res.ok) { toast('error', 'Kiểm tra thất bại'); return; }
      const data = await res.json();
      const { summary, issues } = data;

      // Summary
      $('#integrity-summary').style.display = '';
      $('#integrity-errors').textContent = summary.errors;
      $('#integrity-warnings').textContent = summary.warnings;
      $('#integrity-info').textContent = summary.info;
      $('#integrity-pages').textContent = summary.total_pages;

      if (issues.length === 0) {
        resultsEl.innerHTML = '<div style="color:#00b894;padding:var(--space-3);font-weight:600">✅ Không phát hiện vấn đề nào!</div>';
        return;
      }

      const severityIcons = {
        error: '🔴',
        warning: '🟡',
        info: '🔵',
      };

      resultsEl.innerHTML = issues.map(issue => {
        const icon = severityIcons[issue.severity] || '⚪';
        const pageLink = issue.type !== 'duplicate_title'
          ? `<a href="#" class="integrity-link" data-cat="${escapeHtml(issue.category)}" data-page="${escapeHtml(issue.page)}" style="color:var(--color-accent);text-decoration:underline;cursor:pointer">${escapeHtml(issue.category)}/${escapeHtml(issue.page)}</a>`
          : `<span style="color:var(--color-text-muted)">${escapeHtml(issue.page)}</span>`;
        return `<div style="display:flex;gap:var(--space-2);padding:var(--space-2) var(--space-3);border-bottom:1px solid var(--color-border);font-size:var(--text-sm);align-items:flex-start">
          <span style="flex-shrink:0">${icon}</span>
          <div style="flex:1;min-width:0">
            <div>${escapeHtml(issue.message)}</div>
            <div style="color:var(--color-text-muted);font-size:var(--text-xs);margin-top:2px">${pageLink} • ${escapeHtml(issue.type)}</div>
          </div>
        </div>`;
      }).join('');

      // Navigate to page on click
      resultsEl.querySelectorAll('.integrity-link').forEach(link => {
        link.addEventListener('click', (e) => {
          e.preventDefault();
          const cat = link.dataset.cat;
          const page = link.dataset.page;
          if (cat && page) {
            switchTab('wiki');
            navigateToPage(cat, page);
          }
        });
      });
    } catch (e) {
      toast('error', 'Lỗi', e.message);
      resultsEl.innerHTML = '<div style="color:#e17055;padding:var(--space-3)">Lỗi khi kiểm tra dữ liệu.</div>';
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="play" aria-hidden="true"></i> Quét';
      lucide.createIcons();
    }
  });

  async function loadChangelog() {
    try {
      const res = await apiFetch('/api/wiki/changelog?limit=20');
      if (!res.ok) return;
      const data = await res.json();
      const el = $('#changelog-list');
      if (!data.entries || data.entries.length === 0) {
        el.innerHTML = '<div class="changelog-empty">Chưa có thay đổi nào.</div>';
        return;
      }
      el.innerHTML = data.entries.map(e => {
        const isCreate = e.action === 'wiki_create';
        return `<div class="changelog-item">
          <div class="changelog-dot ${isCreate ? 'create' : ''}"></div>
          <div class="changelog-info">
            <div class="changelog-title">${isCreate ? '🆕' : '✏️'} ${escapeHtml(e.category || '')}/${escapeHtml(e.page || 'tong-quan')}</div>
            <div class="changelog-time">${formatDate(e.edited_at || e.created_at)} • ${e.editor || '—'}</div>
          </div>
        </div>`;
      }).join('');
    } catch { /* silent */ }
  }


  // ============================================================
  // BREADCRUMB CLICK — go back to category index
  // ============================================================
  $('#bc-category')?.addEventListener('click', () => {
    if (state.wikiCurrentCategory) navigateToPage(state.wikiCurrentCategory, 'tong-quan');
  });

  // ============================================================
  // REVIEW QUEUE
  // ============================================================
  let reviewState = { page: 1, filter: 'all', category: '' };

  async function loadReviewStats() {
    try {
      const res = await apiFetch('/api/review/stats');
      if (!res.ok) return;
      const stats = await res.json();

      $('#review-stat-total').textContent = stats.total || 0;
      $('#review-stat-gt').textContent = `${stats.by_confidence?.ground_truth || 0} (${stats.ground_truth_ratio}%)`;
      $('#review-stat-img').textContent = stats.by_source?.image || 0;
      $('#review-stat-conflicts').textContent = stats.conflicts || 0;

      // Update badge
      const flagged = stats.by_state?.flagged || 0;
      const badge = $('#review-badge');
      if (badge) {
        if (flagged > 0) {
          badge.textContent = flagged;
          badge.style.display = '';
        } else {
          badge.style.display = 'none';
        }
      }
    } catch { /* silent */ }
  }

  async function loadConflictsView() {
    const tbody = $('#review-tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="files-empty">Đang tải conflicts...</td></tr>';
    $('#review-pagination').style.display = 'none';

    try {
      const res = await apiFetch('/api/review/conflicts');
      if (!res.ok) return;
      const data = await res.json();

      if (!data.groups?.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="files-empty">✅ Không có conflicts nào!</td></tr>';
        return;
      }

      tbody.innerHTML = data.groups.map(group => {
        const vals = group.values.map((v, i) => {
          const confBadge = {
            ground_truth: '<span class="conf-badge gt">GT</span>',
            high: '<span class="conf-badge high">High</span>',
            medium: '<span class="conf-badge med">Med</span>',
            low: '<span class="conf-badge low">Low</span>',
          }[v.confidence] || `<span class="conf-badge">${escapeHtml(v.confidence || '?')}</span>`;

          const valDisplay = typeof v.value === 'number'
            ? v.value.toLocaleString('vi-VN')
            : escapeHtml(String(v.value ?? ''));

          const loserIds = group.values
            .filter((_, j) => j !== i)
            .map(x => x.claim_id);

          return `<span class="conflict-option">
            ${valDisplay} ${confBadge}
            <button class="btn btn-xs btn-success" data-winner="${escapeHtml(v.claim_id)}" data-losers="${escapeHtml(JSON.stringify(loserIds))}" title="Chọn giá trị này là đúng">✓ Chọn</button>
          </span>`;
        }).join('<span class="conflict-vs">vs</span>');

        return `<tr>
          <td title="${escapeHtml(group.entity_id)}">${escapeHtml(group.entity_name || group.entity_id)}</td>
          <td>${escapeHtml(group.attribute)}</td>
          <td colspan="4" class="conflict-values">${vals}</td>
          <td></td>
        </tr>`;
      }).join('');

      // Bind resolve buttons
      tbody.querySelectorAll('[data-winner]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const winnerId = btn.dataset.winner;
          const loserIds = JSON.parse(btn.dataset.losers || '[]');
          try {
            const r = await apiFetch('/api/review/resolve-conflict', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ winner_claim_id: winnerId, loser_claim_ids: loserIds }),
            });
            if (r.ok) {
              toast('success', 'Resolved', `Winner: ${winnerId}`);
              loadConflictsView();
              loadReviewStats();
            } else {
              const err = await r.json().catch(() => ({}));
              toast('error', 'Lỗi', err.error || 'Failed');
            }
          } catch (e) {
            toast('error', 'Lỗi kết nối', e.message);
          }
        });
      });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="7" class="files-empty">Lỗi: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  async function loadReviewQueue() {
    // Use dedicated conflict view for better UX
    if (reviewState.filter === 'conflicts') {
      return loadConflictsView();
    }

    try {
      const params = new URLSearchParams({
        filter: reviewState.filter,
        category: reviewState.category,
        page: reviewState.page,
        limit: 30,
      });
      const res = await apiFetch(`/api/review/queue?${params}`);
      if (!res.ok) return;
      const data = await res.json();

      const tbody = $('#review-tbody');
      if (!data.items?.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="files-empty">Không có claims nào</td></tr>';
        $('#review-pagination').style.display = 'none';
        return;
      }

      tbody.innerHTML = data.items.map(c => {
        const confBadge = {
          ground_truth: '<span class="conf-badge gt">GT</span>',
          high: '<span class="conf-badge high">High</span>',
          medium: '<span class="conf-badge med">Med</span>',
          low: '<span class="conf-badge low">Low</span>',
        }[c.confidence] || '<span class="conf-badge">' + escapeHtml(c.confidence || '?') + '</span>';

        const sources = (c.source_ids || []).join(', ');
        let sourceIcon = '🤖';
        if (sources.includes('EXCEL')) sourceIcon = '📊';
        else if (sources.includes('IMG')) sourceIcon = '📸';

        const stateBadge = {
          approved: '<span class="state-badge approved">✅</span>',
          flagged: '<span class="state-badge flagged">🚩</span>',
          rejected: '<span class="state-badge rejected">❌</span>',
        }[c.review_state] || '<span class="state-badge pending">⏳</span>';

        const val = typeof c.value === 'number' ? c.value.toLocaleString('vi-VN') : escapeHtml(String(c.value || ''));

        return `<tr data-claim-id="${escapeHtml(c.claim_id || '')}" data-risk-class="${escapeHtml(c.risk_class || '')}">
          <td style="width:36px"><input type="checkbox" class="review-checkbox review-row-check" data-claim-id="${escapeHtml(c.claim_id || '')}" data-risk-class="${escapeHtml(c.risk_class || '')}" aria-label="Chọn claim"></td>
          <td title="${escapeHtml(c.entity_id || '')}">${escapeHtml(c.entity_name || c.entity_id || '—')}</td>
          <td>${escapeHtml(c.attribute || '')}</td>
          <td class="review-value">${val}</td>
          <td>${confBadge}</td>
          <td>${sourceIcon}</td>
          <td>${stateBadge}</td>
          <td style="display:flex;gap:4px">
            <button class="btn btn-ghost btn-icon btn-xs" data-action="approve" title="Approve"><i data-lucide="check"></i></button>
            <button class="btn btn-ghost btn-icon btn-xs" data-action="flag" title="Flag"><i data-lucide="flag"></i></button>
            <button class="btn btn-ghost btn-icon btn-xs" data-action="reject" title="Reject"><i data-lucide="x"></i></button>
          </td>
        </tr>`;
      }).join('');

      // Bind row checkboxes for bulk select
      tbody.querySelectorAll('.review-row-check').forEach(cb => {
        cb.checked = selectedClaims.has(cb.dataset.claimId);
        cb.addEventListener('change', () => {
          const id = cb.dataset.claimId;
          if (cb.checked) selectedClaims.add(id);
          else selectedClaims.delete(id);
          // Update header state
          const allChecks = [...$$('.review-row-check')];
          const checkedCount = allChecks.filter(c => c.checked).length;
          const hdr = $('#review-select-all');
          if (hdr) {
            hdr.checked = checkedCount === allChecks.length && allChecks.length > 0;
            hdr.indeterminate = checkedCount > 0 && checkedCount < allChecks.length;
          }
          updateBulkBar();
        });
      });

      // Bind action buttons
      tbody.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const row = btn.closest('tr');
          const claimId = row?.dataset.claimId;
          if (!claimId) return;
          const action = btn.dataset.action;

          if (action === 'approve') {
            await reviewAction('/api/review/approve', { claim_id: claimId });
          } else if (action === 'flag') {
            const reason = prompt('Lý do flag:');
            if (reason !== null) await reviewAction('/api/review/flag', { claim_id: claimId, reason });
          } else if (action === 'reject') {
            const ok = await showModal('Reject Claim', `Bạn có chắc muốn reject claim ${claimId}?`, 'Reject');
            if (ok) await reviewAction('/api/review/reject', { claim_id: claimId, reason: 'manual_rejection' });
          }
        });
      });

      lucide.createIcons();

      // Pagination
      if (data.pages > 1) {
        $('#review-pagination').style.display = 'flex';
        const start = (data.page - 1) * 30 + 1;
        const end = Math.min(data.page * 30, data.total);
        $('#review-info').textContent = `${start}-${end} / ${data.total}`;
        $('#btn-review-prev').disabled = data.page <= 1;
        $('#btn-review-next').disabled = data.page >= data.pages;
      } else {
        $('#review-pagination').style.display = 'none';
      }
    } catch (e) { console.error('[ReviewQueue] Load error:', e); }
  }

  async function reviewAction(endpoint, body) {
    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        const action = endpoint.split('/').pop();
        toast('success', 'Done', `${body.claim_id} → ${action}`);
        // Immediately remove the row with animation for instant feedback
        removeClaimRow(body.claim_id);
        // Then refresh data in background
        setTimeout(() => { loadReviewQueue(); loadReviewStats(); }, 600);
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Lỗi', err.error || 'Failed');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  /**
   * Animate-remove a claim row from the review table
   */
  function removeClaimRow(claimId) {
    const row = document.querySelector(`tr[data-claim-id="${CSS.escape(claimId)}"]`);
    if (!row) return;
    row.style.transition = 'opacity 0.3s, transform 0.3s';
    row.style.opacity = '0';
    row.style.transform = 'translateX(30px)';
    setTimeout(() => row.remove(), 350);
    // Also remove from selectedClaims set
    selectedClaims.delete(claimId);
    updateBulkBar();
  }

  // Review filters
  $('#review-filter')?.addEventListener('change', (e) => {
    reviewState.filter = e.target.value;
    reviewState.page = 1;
    clearSelection();
    loadReviewQueue();
  });
  $('#review-category')?.addEventListener('change', (e) => {
    reviewState.category = e.target.value;
    reviewState.page = 1;
    clearSelection();
    loadReviewQueue();
  });
  $('#btn-refresh-review')?.addEventListener('click', () => {
    loadReviewStats();
    loadReviewQueue();
  });
  $('#btn-review-prev')?.addEventListener('click', () => {
    if (reviewState.page > 1) { reviewState.page--; loadReviewQueue(); }
  });
  $('#btn-review-next')?.addEventListener('click', () => {
    reviewState.page++; loadReviewQueue();
  });

  // History tab is handled by the updated switchTab above.

  // ============================================================
  // CONTENT HEALTH
  // ============================================================
  const HEALTH_LABELS = {
    good:    { dot: '🟢', text: 'Tốt',       cls: 'good' },
    warning: { dot: '🟡', text: 'Cảnh báo',  cls: 'warning' },
    stale:   { dot: '🔴', text: 'Cũ',        cls: 'stale' },
    error:   { dot: '🔴', text: 'Lỗi',       cls: 'error' },
    empty:   { dot: '⚪', text: 'Trống',     cls: 'empty' },
    unknown: { dot: '⚫', text: 'Chưa rõ',   cls: 'unknown' },
  };

  const CATEGORY_LABELS_HEALTH = {
    hosting: 'Hosting', vps: 'VPS', ssl: 'SSL',
    'ten-mien': 'Tên Miền', email: 'Email',
    server: 'Server', software: 'Software',
    other: 'Khác', uncategorized: 'Chưa phân loại',
  };

  async function loadHealth() {
    const grid = $('#health-grid');
    if (!grid) return;
    try {
      const res = await apiFetch('/api/wiki/health');
      if (!res.ok) { grid.innerHTML = '<div class="health-loading">Không thể tải dữ liệu sức khoẻ</div>'; return; }
      const data = await res.json();
      const entries = Object.values(data.health || {});

      if (!entries.length) {
        grid.innerHTML = '<div class="health-loading">Chưa có dữ liệu</div>';
        return;
      }

      grid.innerHTML = entries.map(h => {
        const info = HEALTH_LABELS[h.health_status] || HEALTH_LABELS.unknown;
        const daysMod = h.days_since_modified !== null ? `${h.days_since_modified} ngày` : '—';
        const daysVer = h.days_since_verify !== null ? `${h.days_since_verify} ngày` : '—';
        const lintBadge = h.lint_errors === null ? '—'
          : h.lint_errors === 0 && (!h.lint_warnings || h.lint_warnings === 0)
            ? '<span class="health-ok">✓ Sạch</span>'
          : h.lint_errors === 0
            ? `<span class="health-warn">${h.lint_warnings} cảnh báo</span>`
          : `<span class="health-err">${h.lint_errors} lỗi${h.lint_warnings ? ` +${h.lint_warnings} cảnh báo` : ''}</span>`;

        return `<div class="health-card health-${info.cls}">
          <div class="health-card-header">
            <span class="health-dot">${info.dot}</span>
            <span class="health-cat">${escapeHtml(CATEGORY_LABELS_HEALTH[h.category] || h.category)}</span>
            <span class="health-status-tag ${info.cls}">${info.text}</span>
          </div>
          <div class="health-card-stats">
            <div class="health-stat">
              <span class="health-stat-label">Trang</span>
              <span class="health-stat-val">${h.pages}</span>
            </div>
            <div class="health-stat">
              <span class="health-stat-label">Sửa đổi</span>
              <span class="health-stat-val">${daysMod} trước</span>
            </div>
            <div class="health-stat">
              <span class="health-stat-label">Verify</span>
              <span class="health-stat-val">${daysVer} trước</span>
            </div>
            <div class="health-stat">
              <span class="health-stat-label">Lint</span>
              <span class="health-stat-val">${lintBadge}</span>
            </div>
          </div>
        </div>`;
      }).join('');
    } catch (e) {
      grid.innerHTML = `<div class="health-loading">Lỗi: ${escapeHtml(e.message)}</div>`;
    }
  }

  $('#btn-refresh-health')?.addEventListener('click', loadHealth);

  // ============================================================
  // VERSION DIFF
  // ============================================================
  let buildsCache = [];

  async function loadBuilds() {
    if (buildsCache.length > 0) return; // Already loaded
    try {
      const res = await apiFetch('/api/builds');
      if (!res.ok) return;
      const data = await res.json();
      buildsCache = data.builds || [];
      populateBuildSelectors(buildsCache);
    } catch { /* silent */ }
  }

  function populateBuildSelectors(builds) {
    const v1 = $('#diff-v1');
    const v2 = $('#diff-v2');
    if (!v1 || !v2) return;

    const opts = builds.map(b =>
      `<option value="${escapeHtml(b.id)}">${escapeHtml(b.display)} — ${escapeHtml(b.version || '—')}</option>`
    ).join('');

    v1.innerHTML = '<option value="">-- Chọn phiên bản --</option>' + opts;
    v2.innerHTML = '<option value="">-- Chọn phiên bản --</option>' + opts;

    // Default: v1 = second latest, v2 = latest
    if (builds.length >= 2) {
      v1.value = builds[1].id;
      v2.value = builds[0].id;
    } else if (builds.length === 1) {
      v2.value = builds[0].id;
    }
  }

  $('#btn-diff')?.addEventListener('click', async () => {
    const v1 = $('#diff-v1')?.value;
    const v2 = $('#diff-v2')?.value;
    if (!v1 || !v2) { toast('warning', 'Chọn đủ 2 phiên bản'); return; }
    if (v1 === v2) { toast('warning', 'Chọn 2 phiên bản khác nhau'); return; }

    try {
      const res = await apiFetch(`/api/builds/diff?v1=${encodeURIComponent(v1)}&v2=${encodeURIComponent(v2)}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Không thể so sánh', err.error || 'Lỗi'); return;
      }
      const data = await res.json();
      renderDiff(data);
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  });

  function renderDiff(data) {
    const result = $('#diff-result');
    const empty = $('#diff-empty');
    if (!result) return;

    $('#diff-label-v1').textContent = data.base.display;
    $('#diff-label-v2').textContent = data.compare.display;
    $('#diff-th-v1').textContent = data.base.display;
    $('#diff-th-v2').textContent = data.compare.display;

    const changes = data.changes;
    const rows = [
      { label: 'Wiki pages', key: 'wiki_files' },
      { label: 'Claims', key: 'claims_count' },
      { label: 'Tokens (ước tính)', key: 'wiki_token_estimate' },
    ];

    $('#diff-tbody').innerHTML = rows.map(r => {
      const c = changes[r.key];
      if (!c) return '';
      const delta = c.delta;
      const deltaCls = delta > 0 ? 'diff-added' : delta < 0 ? 'diff-removed' : 'diff-same';
      const deltaStr = delta > 0 ? `+${delta}` : String(delta);
      return `<tr>
        <td>${escapeHtml(r.label)}</td>
        <td>${c.before.toLocaleString('vi-VN')}</td>
        <td>${c.after.toLocaleString('vi-VN')}</td>
        <td><span class="diff-delta ${deltaCls}">${deltaStr}</span></td>
      </tr>`;
    }).join('');

    // Version row
    if (data.base.version !== data.compare.version) {
      $('#diff-tbody').innerHTML += `<tr>
        <td>Version</td>
        <td>${escapeHtml(data.base.version)}</td>
        <td>${escapeHtml(data.compare.version)}</td>
        <td><span class="diff-delta diff-added">↑ mới</span></td>
      </tr>`;
    }

    result.style.display = '';
    empty.style.display = 'none';

    if (data.same_version) {
      toast('info', 'Hai phiên bản giống nhau', 'Không có thay đổi nào được phát hiện');
    }
    lucide.createIcons();
  }

  // ============================================================
  // ACTIVITY LOG
  // ============================================================
  const ACTIVITY_ICON_MAP = {
    edit: 'pencil', create: 'plus-circle', pipeline: 'workflow',
    upload: 'upload-cloud', review: 'shield-check', build: 'package',
  };

  async function loadActivity() {
    const timeline = $('#activity-timeline');
    if (!timeline) return;
    try {
      const res = await apiFetch('/api/activity?limit=60');
      if (!res.ok) { timeline.innerHTML = '<div class="health-loading">Không thể tải nhật ký</div>'; return; }
      const data = await res.json();

      if (!data.events?.length) {
        timeline.innerHTML = '<div class="health-loading">Chưa có hoạt động nào</div>';
        return;
      }

      // Group events by date
      const groups = {};
      for (const e of data.events) {
        const d = e.ts ? new Date(e.ts).toLocaleDateString('vi-VN', { weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric' }) : 'Không rõ ngày';
        if (!groups[d]) groups[d] = [];
        groups[d].push(e);
      }

      timeline.innerHTML = Object.entries(groups).map(([date, evts]) => {
        const items = evts.map(e => {
          const icon = e.icon || ACTIVITY_ICON_MAP[e.type] || 'circle';
          const okCls = e.ok === false ? 'act-fail' : e.ok === true ? 'act-ok' : '';
          const time = e.ts ? new Date(e.ts).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) : '';
          const detailHtml = e.detail ? `<span class="act-detail">${escapeHtml(e.detail)}</span>` : '';
          return `<div class="act-item ${okCls}">
            <div class="act-icon-wrap"><i data-lucide="${icon}" aria-hidden="true"></i></div>
            <div class="act-body">
              <span class="act-label">${escapeHtml(e.label)}</span>
              ${detailHtml}
            </div>
            <span class="act-time">${time}</span>
          </div>`;
        }).join('');

        return `<div class="act-group">
          <div class="act-group-date">${escapeHtml(date)}</div>
          ${items}
        </div>`;
      }).join('');

      lucide.createIcons();
    } catch (e) {
      timeline.innerHTML = `<div class="health-loading">Lỗi: ${escapeHtml(e.message)}</div>`;
    }
  }

  $('#btn-refresh-activity')?.addEventListener('click', loadActivity);

  // ============================================================
  // BULK CLAIM ACTIONS
  // ============================================================
  let selectedClaims = new Set();

  function updateBulkBar() {
    const bar = $('#bulk-bar');
    const countEl = $('#bulk-count');
    if (!bar || !countEl) return;
    const n = selectedClaims.size;
    if (n === 0) {
      bar.style.display = 'none';
    } else {
      bar.style.display = 'flex';
      countEl.textContent = `${n} đã chọn`;
    }
  }

  function clearSelection() {
    selectedClaims.clear();
    $$('.review-row-check').forEach(c => c.checked = false);
    const all = $('#review-select-all');
    if (all) { all.checked = false; all.indeterminate = false; }
    updateBulkBar();
  }

  // Header checkbox — select/deselect all visible
  $('#review-select-all')?.addEventListener('change', (e) => {
    const checked = e.target.checked;
    $$('.review-row-check').forEach(cb => {
      cb.checked = checked;
      const claimId = cb.dataset.claimId;
      if (claimId) {
        if (checked) selectedClaims.add(claimId);
        else selectedClaims.delete(claimId);
      }
    });
    updateBulkBar();
  });

  async function doBulkAction(action) {
    if (!selectedClaims.size) return;
    const ids = [...selectedClaims];

    let confirmMsg = `${action === 'approve' ? 'Duyệt' : action === 'reject' ? 'Từ chối' : 'Flag'} ${ids.length} claims?`;

    // Extra warning for high-risk (price) items
    const highRiskSelected = [...$$('.review-row-check')]
      .filter(cb => cb.checked && cb.dataset.riskClass === 'high');
    if (highRiskSelected.length > 0) {
      confirmMsg += `\n\n⚠️ ${highRiskSelected.length} claim có risk_class: high (giá tiền). Tiếp tục?`;
    }

    const ok = await showModal(`Bulk ${action}`, confirmMsg, action === 'reject' ? 'Từ chối tất cả' : 'Xác nhận');
    if (!ok) return;

    // Show loading state
    const bulkBtns = $$('#bulk-bar button');
    bulkBtns.forEach(b => b.disabled = true);
    const loadingToast = toast('info', `Đang ${action === 'approve' ? 'duyệt' : action === 'reject' ? 'từ chối' : 'flag'}...`, `${ids.length} claims`, 0);

    try {
      const res = await apiFetch('/api/review/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, claim_ids: ids }),
      });
      removeToast(loadingToast);
      bulkBtns.forEach(b => b.disabled = false);

      if (res.ok) {
        const data = await res.json();
        toast('success', `Bulk ${action} xong`,
          `${data.success_count}/${data.total} thành công${data.failed_count > 0 ? ` • ${data.failed_count} thất bại` : ''}`
        );
        // Animate-remove all successfully processed rows
        for (const id of ids) {
          removeClaimRow(id);
        }
        clearSelection();
        // Refresh data in background after animations
        setTimeout(() => { loadReviewQueue(); loadReviewStats(); }, 600);
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Bulk action thất bại', err.error || 'Lỗi');
      }
    } catch (e) {
      removeToast(loadingToast);
      bulkBtns.forEach(b => b.disabled = false);
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  $('#btn-bulk-approve')?.addEventListener('click', () => doBulkAction('approve'));
  $('#btn-bulk-flag')?.addEventListener('click', () => doBulkAction('flag'));
  $('#btn-bulk-reject')?.addEventListener('click', () => doBulkAction('reject'));
  $('#btn-bulk-clear')?.addEventListener('click', () => clearSelection());


  // Also expose health dot in sidebar (after health loads)
  async function updateSidebarHealthDots() {
    try {
      const res = await apiFetch('/api/wiki/health');
      if (!res.ok) return;
      const data = await res.json();
      for (const [cat, h] of Object.entries(data.health || {})) {
        const btn = $(`.tree-category-btn[data-cat="${cat}"]`);
        if (!btn) continue;
        let dot = btn.querySelector('.health-indicator');
        if (!dot) {
          dot = document.createElement('span');
          dot.className = 'health-indicator';
          btn.appendChild(dot);
        }
        const info = HEALTH_LABELS[h.health_status] || HEALTH_LABELS.unknown;
        dot.textContent = info.dot;
        dot.title = `Sức khoẻ: ${info.text} | Sửa đổi: ${h.days_since_modified !== null ? h.days_since_modified + ' ngày trước' : 'không rõ'}`;
      }
    } catch { /* silent */ }
  }

  // ============================================================
  // DUAL-VOTE QUEUE
  // ============================================================
  let dualModalCurrentId = null;

  async function loadDualQueue() {
    const tbody = $('#dual-queue-tbody');
    tbody.innerHTML = '<tr><td colspan="8" class="files-empty">Đang tải...</td></tr>';
    try {
      const res = await apiFetch('/api/review/dual-queue');
      if (!res.ok) {
        tbody.innerHTML = '<tr><td colspan="8" class="files-empty">Lỗi tải dữ liệu</td></tr>';
        return;
      }
      const ct = res.headers.get('content-type') || '';
      if (!ct.includes('application/json')) {
        tbody.innerHTML = '<tr><td colspan="8" class="files-empty">API chưa sẵn sàng — cần restart server để kích hoạt route dual-queue</td></tr>';
        return;
      }
      const data = await res.json();

      // Update stat
      const count = data.total || 0;
      const countEl = $('#dual-queue-count');
      if (countEl) countEl.textContent = count;
      const badge = $('#dual-queue-badge');
      if (badge) {
        if (count > 0) { badge.textContent = count; badge.style.display = ''; }
        else badge.style.display = 'none';
      }

      if (!data.items?.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="files-empty">✅ Không có items nào chờ review</td></tr>';
        return;
      }

      tbody.innerHTML = data.items.map(item => {
        const statusBadge = {
          DISAGREE: '<span class="dv-badge dv-disagree">DISAGREE</span>',
          PARTIAL:  '<span class="dv-badge dv-partial">PARTIAL</span>',
        }[item.status] || `<span class="dv-badge">${escapeHtml(item.status || '?')}</span>`;

        const score = item.score != null ? (item.score * 100).toFixed(0) + '%' : '—';
        const ts = item.ts ? new Date(item.ts).toLocaleString('vi-VN', { hour12: false }) : '—';
        const preview = escapeHtml((item.prompt_preview || '').slice(0, 80));
        const modelA = escapeHtml((item.model_a || '').replace('gemini-', 'gem-').slice(0, 20));
        const modelB = escapeHtml((item.model_b || '').slice(0, 12));

        return `<tr class="dual-queue-row" data-dual-id="${escapeHtml(item.id)}" style="cursor:pointer" title="Nhấp để xem side-by-side">
          <td style="font-size:var(--text-xs);color:var(--color-text-muted)">${ts}</td>
          <td><code style="font-size:var(--text-xs)">${escapeHtml(item.skill || '—')}</code></td>
          <td>${statusBadge}</td>
          <td style="font-family:var(--font-mono);font-size:var(--text-sm)">${escapeHtml(score)}</td>
          <td style="font-size:var(--text-xs);color:var(--color-text-muted)">${modelA}</td>
          <td style="font-size:var(--text-xs);color:var(--color-text-muted)">${modelB}</td>
          <td style="font-size:var(--text-xs);max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${preview}</td>
          <td>
            <button class="btn btn-xs btn-ghost" data-dual-open="${escapeHtml(item.id)}" title="Xem chi tiết">
              <i data-lucide="eye"></i>
            </button>
          </td>
        </tr>`;
      }).join('');

      lucide.createIcons();

      // Row click → open modal
      tbody.querySelectorAll('.dual-queue-row').forEach(row => {
        row.addEventListener('click', (e) => {
          if (e.target.closest('button')) return;
          openDualModal(row.dataset.dualId);
        });
      });
      tbody.querySelectorAll('[data-dual-open]').forEach(btn => {
        btn.addEventListener('click', () => openDualModal(btn.dataset.dualOpen));
      });
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="8" class="files-empty">Lỗi: ${escapeHtml(e.message)}</td></tr>`;
    }
  }

  // Strip markdown fences (```json ... ```) from LLM output — see LESSONS BUG-003
  function stripMarkdownFence(text) {
    if (!text) return '';
    return text.replace(/^\s*```[a-z]*\s*\n?/i, '').replace(/\n?\s*```\s*$/i, '').trim();
  }

  function tryParseJSON(text) {
    try { return JSON.parse(stripMarkdownFence(text)); } catch { return null; }
  }

  // Compute algorithmic disagreement between two LLM outputs.
  // Returns { diffs: [{type, path, a, b}], summary: string } or null.
  function computeDisagreement(textA, textB) {
    const jA = tryParseJSON(textA);
    const jB = tryParseJSON(textB);
    if (jA !== null && jB !== null) return diffStructured(jA, jB);
    return diffLineCount(textA, textB);
  }

  function diffStructured(a, b) {
    const diffs = [];
    const walk = (va, vb, path) => {
      const tA = Array.isArray(va) ? 'array' : (va === null ? 'null' : typeof va);
      const tB = Array.isArray(vb) ? 'array' : (vb === null ? 'null' : typeof vb);
      if (tA !== tB) { diffs.push({ type: 'type', path, a: va, b: vb }); return; }
      if (tA === 'object') {
        const keys = new Set([...Object.keys(va || {}), ...Object.keys(vb || {})]);
        for (const k of keys) {
          const sub = path ? `${path}.${k}` : k;
          if (!(k in va)) { diffs.push({ type: 'missing_a', path: sub, b: vb[k] }); continue; }
          if (!(k in vb)) { diffs.push({ type: 'missing_b', path: sub, a: va[k] }); continue; }
          walk(va[k], vb[k], sub);
        }
      } else if (tA === 'array') {
        const n = Math.max(va.length, vb.length);
        for (let i = 0; i < n; i++) {
          const sub = `${path}[${i}]`;
          if (i >= va.length) { diffs.push({ type: 'missing_a', path: sub, b: vb[i] }); continue; }
          if (i >= vb.length) { diffs.push({ type: 'missing_b', path: sub, a: va[i] }); continue; }
          walk(va[i], vb[i], sub);
        }
      } else if (va !== vb) {
        diffs.push({ type: 'value', path, a: va, b: vb });
      }
    };
    walk(a, b, '');
    return { diffs, kind: 'structured' };
  }

  function diffLineCount(a, b) {
    const la = (a || '').split('\n').length;
    const lb = (b || '').split('\n').length;
    return { diffs: [], kind: 'text', line_a: la, line_b: lb };
  }

  function renderDisagreement(result) {
    const el = $('#dual-disagreement');
    if (!el) return;
    if (!result) { el.innerHTML = ''; return; }
    if (result.kind === 'text') {
      el.innerHTML = `<div class="dv-headline">Không parse được JSON — so sánh dạng text</div>
        <ul><li>A: ${result.line_a} dòng · B: ${result.line_b} dòng</li>
        <li>Hãy đối chiếu 2 panel bên dưới thủ công.</li></ul>`;
      return;
    }
    const { diffs } = result;
    if (!diffs.length) {
      el.innerHTML = `<div class="dv-headline">Dữ liệu JSON match — không có sai khác về cấu trúc</div>
        <ul><li>Có thể LLM khác nhau về format/whitespace. Chọn bên nào cũng được.</li></ul>`;
      return;
    }
    const counts = diffs.reduce((acc, d) => { acc[d.type] = (acc[d.type] || 0) + 1; return acc; }, {});
    const headline = [
      counts.value ? `${counts.value} giá trị khác` : null,
      counts.type ? `${counts.type} sai kiểu` : null,
      counts.missing_a ? `${counts.missing_a} trường A thiếu` : null,
      counts.missing_b ? `${counts.missing_b} trường B thiếu` : null,
    ].filter(Boolean).join(' · ');
    const fmt = (v) => {
      if (v === undefined) return '∅';
      if (typeof v === 'string') return `"${v.length > 40 ? v.slice(0, 40) + '…' : v}"`;
      if (v === null) return 'null';
      if (typeof v === 'object') return Array.isArray(v) ? `[${v.length}]` : '{…}';
      return String(v);
    };
    const tagMap = {
      value: { cls: 'dv-tag-diff', label: 'DIFF' },
      type: { cls: 'dv-tag-type', label: 'TYPE' },
      missing_a: { cls: 'dv-tag-missing-a', label: 'A∅' },
      missing_b: { cls: 'dv-tag-missing-b', label: 'B∅' },
    };
    const items = diffs.slice(0, 12).map(d => {
      const tag = tagMap[d.type];
      const tagHtml = `<span class="dv-tag ${tag.cls}">${tag.label}</span>`;
      const key = `<span class="dv-key">${escapeHtml(d.path || '(root)')}</span>`;
      const aHtml = d.type === 'missing_a' ? '' : ` · A=<span class="dv-a">${escapeHtml(fmt(d.a))}</span>`;
      const bHtml = d.type === 'missing_b' ? '' : ` · B=<span class="dv-b">${escapeHtml(fmt(d.b))}</span>`;
      return `<li>${tagHtml}${key}${aHtml}${bHtml}</li>`;
    }).join('');
    const more = diffs.length > 12 ? `<li>… và ${diffs.length - 12} sai khác khác</li>` : '';
    el.innerHTML = `<div class="dv-headline">${escapeHtml(headline)}</div><ul>${items}${more}</ul>`;
  }

  async function openDualModal(id) {
    dualModalCurrentId = id;
    try {
      const res = await apiFetch(`/api/review/dual/${encodeURIComponent(id)}`);
      if (!res.ok) { toast('error', 'Lỗi', 'Không tải được item'); return; }
      const data = await res.json();

      // Fill modal fields
      $('#dual-modal-meta').textContent = [
        `Score: ${data.score != null ? (data.score * 100).toFixed(1) + '%' : '—'}`,
        `Status: ${data.status || '—'}`,
        `Skill: ${data.skill || '—'}`,
        data.ts ? new Date(data.ts).toLocaleString('vi-VN', { hour12: false }) : '',
      ].filter(Boolean).join('  |  ');

      const sourceEl = $('#dual-modal-source');
      if (data.source_file) {
        sourceEl.textContent = `📄 Source: ${data.source_file}${data.category ? ' · ' + data.category : ''}`;
        sourceEl.classList.add('has-source');
      } else {
        sourceEl.textContent = '⚠️ Legacy item — không có source_file (sẽ không auto-apply downstream)';
        sourceEl.classList.remove('has-source');
      }

      $('#dual-modal-prompt').textContent = data.prompt_preview || '(không có prompt)';

      $('#dual-model-a-name').textContent = data.model_a || '';
      $('#dual-model-b-name').textContent = data.model_b || '';
      const cleanA = stripMarkdownFence(data.text_a || '');
      const cleanB = stripMarkdownFence(data.text_b || '');
      $('#dual-output-a').textContent = cleanA || '(empty)';
      $('#dual-output-b').textContent = cleanB || '(empty)';

      // Algorithmic disagreement card
      renderDisagreement(computeDisagreement(data.text_a, data.text_b));

      // Reset note
      const noteEl = $('#dual-modal-note-text');
      if (noteEl) noteEl.value = '';

      // Show modal
      const overlay = $('#dual-modal-overlay');
      overlay.style.display = 'flex';
      overlay.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      lucide.createIcons();
    } catch (e) {
      toast('error', 'Lỗi', e.message);
    }
  }

  function closeDualModal() {
    const overlay = $('#dual-modal-overlay');
    overlay.style.display = 'none';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    dualModalCurrentId = null;
  }

  async function submitDualDecision(decision) {
    if (!dualModalCurrentId) return;
    const id = dualModalCurrentId;
    const note = ($('#dual-modal-note-text')?.value || '').trim();
    try {
      const res = await apiFetch(`/api/review/dual/${encodeURIComponent(id)}/decide`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, note: note || undefined }),
      });
      if (res.ok) {
        const labels = { pick_a: 'Chọn A (Gemini)', pick_b: 'Chọn B (GPT)', reject_both: 'Loại bỏ cả hai' };
        toast('success', 'Đã quyết định', `${id}: ${labels[decision] || decision}`);
        closeDualModal();
        loadDualQueue();
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Lỗi', err.error || 'Thất bại');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  // Dual modal bindings — event delegation (script loads before modal HTML is parsed)
  document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('[data-dv-close]');
    if (closeBtn) { closeDualModal(); return; }
    const actionBtn = e.target.closest('[data-dv-action]');
    if (actionBtn) { submitDualDecision(actionBtn.dataset.dvAction); return; }
    const overlay = e.target.closest('#dual-modal-overlay');
    if (overlay && e.target === overlay) closeDualModal();
  });
  document.addEventListener('keydown', (e) => {
    if (!dualModalCurrentId) return;
    if (e.key === 'Escape') { closeDualModal(); return; }
    if (e.target.matches('textarea, input')) return;
    if (e.key === 'a' || e.key === 'A') submitDualDecision('pick_a');
    else if (e.key === 'b' || e.key === 'B') submitDualDecision('pick_b');
    else if (e.key === 'r' || e.key === 'R') submitDualDecision('reject_both');
  });
  $('#btn-refresh-dual')?.addEventListener('click', loadDualQueue);

  // ============================================================
  // GROUND TRUTH PROMOTION
  // ============================================================
  function getPromoSources() {
    const src = [];
    if ($('#promo-high')?.checked) src.push('high');
    if ($('#promo-medium')?.checked) src.push('medium');
    if ($('#promo-low')?.checked) src.push('low');
    return src;
  }

  $('#btn-promote-dryrun')?.addEventListener('click', async () => {
    const src = getPromoSources();
    if (!src.length) { toast('warning', 'Chọn ít nhất 1 confidence level'); return; }
    const resultEl = $('#promote-result');
    if (resultEl) resultEl.textContent = 'Đang kiểm tra...';
    try {
      const res = await apiFetch('/api/review/promote-groundtruth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_confidence: src, dry_run: true }),
      });
      const data = await res.json();
      if (res.ok) {
        const parts = Object.entries(data.breakdown || {}).map(([k, v]) => `${v} ${k}`).join(', ');
        if (resultEl) resultEl.textContent = `Dry run: ${data.total_candidates} claims sẽ promote (${parts || '0'})`;
        toast('info', 'Dry Run', `${data.total_candidates} claims eligible → ${src.join(', ')} → ground_truth`);
      } else {
        if (resultEl) resultEl.textContent = '';
        toast('error', 'Lỗi', data.error || 'Thất bại');
      }
    } catch (e) {
      if (resultEl) resultEl.textContent = '';
      toast('error', 'Lỗi kết nối', e.message);
    }
  });

  $('#btn-promote-confirm')?.addEventListener('click', async () => {
    const src = getPromoSources();
    if (!src.length) { toast('warning', 'Chọn ít nhất 1 confidence level'); return; }
    const ok = await showModal(
      'Promote → Ground Truth',
      `Upgrade tất cả claims approved có confidence [${src.join(', ')}] lên ground_truth. Hành động này không thể hoàn tác tự động.`,
      'Confirm Promote'
    );
    if (!ok) return;
    const resultEl = $('#promote-result');
    if (resultEl) resultEl.textContent = 'Đang promote...';
    try {
      const res = await apiFetch('/api/review/promote-groundtruth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_confidence: src, dry_run: false }),
      });
      const data = await res.json();
      if (res.ok) {
        if (resultEl) resultEl.textContent = data.message;
        toast('success', 'Promoted!', data.message);
        // Reload stats to reflect new GT ratio
        loadReviewStats();
        loadDashboard();
      } else {
        if (resultEl) resultEl.textContent = '';
        toast('error', 'Lỗi', data.error || 'Thất bại');
      }
    } catch (e) {
      if (resultEl) resultEl.textContent = '';
      toast('error', 'Lỗi kết nối', e.message);
    }
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && $('#dual-modal-overlay')?.style.display !== 'none') {
      closeDualModal();
    }
  });

  // ============================================================
  // INIT
  // ============================================================
  if (state.token) {
    // Auto-login with stored token
    apiFetch('/api/status').then(res => {
      if (res.ok) showApp();
      else logout();
    }).catch(() => logout());
  }

})();

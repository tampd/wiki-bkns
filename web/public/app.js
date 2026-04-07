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
    loadWikiTree();
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
    $('#tab-wiki').style.display = 'none';
    $('#tab-dashboard').style.display = 'none';
    $('#tab-upload').style.display = 'none';
    $('#tab-pipeline').style.display = 'none';
    $('#tab-review').style.display = 'none';
    // Show selected
    const el = $(`#tab-${tabName}`);
    if (el) el.style.display = tabName === 'wiki' ? 'flex' : 'block';

    if (tabName === 'dashboard') { loadDashboard(); loadChangelog(); }
    if (tabName === 'upload') loadFiles();
    if (tabName === 'review') { loadReviewStats(); loadReviewQueue(); }
    lucide.createIcons();
  }

  $$('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.dataset.tab === state.currentTab) return;
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
          const parts = href.replace(/\.md$/, '').split('/');
          const cat = parts.length >= 2 ? parts[parts.length - 2] : state.wikiCurrentCategory;
          const pg = parts[parts.length - 1];
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
        hooks: {
          addImageBlobHook: async (blob, callback) => {
            try {
              const formData = new FormData();
              formData.append('image', blob);
              const res = await apiFetch('/api/upload/image', { method: 'POST', body: formData });
              if (res.ok) {
                const data = await res.json();
                callback(data.url, blob.name || 'image');
              } else {
                toast('error', 'Upload ảnh thất bại');
              }
            } catch (e) {
              toast('error', 'Lỗi upload', e.message);
            }
          },
        },
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
        const snippet = r.snippet ? r.snippet.replace(new RegExp(`(${escapeHtml(query)})`, 'gi'), '<mark>$1</mark>') : '';
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
            <div style="font-weight:500">${escapeHtml(b.filename)}</div>
            <div style="color:var(--color-text-muted);margin-top:2px">${formatDate(b.mtime)} • ${formatSize(b.size)}</div>
          </li>`
        ).join('');
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
  async function loadDashboard() {
    try {
      const res = await apiFetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();
      if (data.wiki_stats) {
        const s = data.wiki_stats;
        if ($('#stat-total-files')) $('#stat-total-files').textContent = s.total_files || '0';
        if ($('#stat-wiki-pages')) $('#stat-wiki-pages').textContent = s.wiki_pages || '0';
        if ($('#stat-claims')) $('#stat-claims').textContent = s.total_claims || '0';
        if ($('#stat-last-build')) $('#stat-last-build').textContent = s.build_version || '—';
      }
    } catch { /* silent */ }
  }

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
  // STATUS
  // ============================================================
  async function loadStatus() {
    try {
      const res = await apiFetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();

      const cls = data.pipeline || 'idle';
      const labels = { idle: 'Idle', running: 'Đang chạy', success: 'Thành công', failed: 'Thất bại' };

      [$('#pipeline-status-badge'), $('#pipeline-status-header')].forEach(el => {
        if (el) el.className = 'pipeline-badge ' + cls;
      });
      if ($('#pipeline-status-text')) $('#pipeline-status-text').textContent = labels[cls] || cls;
      const headerSpan = $('#pipeline-status-header');
      if (headerSpan) headerSpan.querySelector('span:last-child').textContent = labels[cls] || cls;

      if ($('#pipeline-last-run')) $('#pipeline-last-run').textContent = formatDate(data.last_run);
      if ($('#pipeline-last-result')) $('#pipeline-last-result').textContent = data.last_result || '—';
      if ($('#pipeline-build-version')) $('#pipeline-build-version').textContent = data.build_version || '—';
    } catch { /* silent */ }
  }

  // ============================================================
  // PIPELINE CONTROL
  // ============================================================
  async function triggerPipeline(action) {
    try {
      const res = await apiFetch('/api/trigger', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action }) });
      if (res.ok) { toast('success', 'Pipeline triggered', `Action: ${action}`); loadStatus(); }
      else { const err = await res.json().catch(() => ({})); toast('error', 'Trigger thất bại', err.error || 'Lỗi'); }
    } catch (e) { toast('error', 'Lỗi kết nối', e.message); }
  }

  $('#btn-trigger-full')?.addEventListener('click', async () => {
    const ok = await showModal('Chạy Full Pipeline', 'Extract → Compile → Build. Tiếp tục?', 'Chạy');
    if (ok) triggerPipeline('full');
  });
  $('#btn-trigger-extract')?.addEventListener('click', () => triggerPipeline('extract'));
  $('#btn-trigger-compile')?.addEventListener('click', () => triggerPipeline('compile'));

  // ============================================================
  // UPLOAD
  // ============================================================
  const uploadZone = $('#upload-zone');
  const fileInput = $('#file-input');

  if (uploadZone) {
    uploadZone.addEventListener('click', () => fileInput.click());
    uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
    uploadZone.addEventListener('drop', e => { e.preventDefault(); uploadZone.classList.remove('drag-over'); addFilesToQueue(e.dataTransfer.files); });
  }
  if (fileInput) fileInput.addEventListener('change', () => { addFilesToQueue(fileInput.files); fileInput.value = ''; });

  function addFilesToQueue(fileList) {
    for (const file of fileList) {
      const ext = getFileExt(file.name);
      if (!ALLOWED_TYPES.includes(ext)) { toast('warning', 'Định dạng không hỗ trợ', file.name); continue; }
      if (file.size > MAX_FILE_SIZE) { toast('warning', 'File quá lớn', file.name); continue; }
      if (state.fileQueue.some(f => f.name === file.name && f.size === file.size)) continue;
      state.fileQueue.push(file);
    }
    renderQueue();
  }

  function renderQueue() {
    const queueEl = $('#file-queue');
    const actionsEl = $('#upload-actions');
    if (!state.fileQueue.length) { queueEl.style.display = 'none'; actionsEl.style.display = 'none'; return; }
    queueEl.style.display = 'block'; actionsEl.style.display = 'flex';
    queueEl.innerHTML = state.fileQueue.map((file, i) => {
      const info = getFileTypeInfo(file.name);
      return `<div class="file-queue-item"><div class="file-icon ${info.cls}">${info.label}</div>
        <div class="file-info"><div class="file-name">${escapeHtml(file.name)}</div><div class="file-size">${formatSize(file.size)}</div></div>
        <button class="remove-btn" data-index="${i}">&times;</button></div>`;
    }).join('');
    queueEl.querySelectorAll('.remove-btn').forEach(b => b.addEventListener('click', () => { state.fileQueue.splice(+b.dataset.index, 1); renderQueue(); }));
  }

  $('#btn-clear-queue')?.addEventListener('click', () => { state.fileQueue = []; renderQueue(); });

  async function uploadFiles(trigger) {
    if (!state.fileQueue.length) return;
    const formData = new FormData();
    state.fileQueue.forEach(f => formData.append('files', f));
    formData.append('trigger', trigger ? 'true' : 'false');
    const loading = toast('info', 'Đang upload...', `${state.fileQueue.length} file`, 0);
    try {
      const res = await apiFetch('/api/upload', { method: 'POST', body: formData });
      removeToast(loading);
      if (res.ok) {
        const data = await res.json();
        state.fileQueue = []; renderQueue();
        toast('success', trigger ? 'Upload & Trigger OK' : 'Upload OK', `${data.uploaded.length} file`);
        loadFiles(); loadStatus();
      } else { toast('error', 'Upload thất bại'); }
    } catch (e) { removeToast(loading); toast('error', 'Lỗi', e.message); }
  }

  $('#btn-upload-trigger')?.addEventListener('click', () => uploadFiles(true));
  $('#btn-upload-only')?.addEventListener('click', () => uploadFiles(false));

  // ============================================================
  // FILE BROWSER
  // ============================================================
  async function loadFiles() {
    try {
      const res = await apiFetch(`/api/files?source=${state.currentSource}&page=${state.currentPage}&limit=15`);
      if (!res.ok) return;
      const data = await res.json();
      const tbody = $('#files-tbody');

      if (!data.files?.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="files-empty">Chưa có file nào</td></tr>';
        $('#files-pagination').style.display = 'none';
        return;
      }

      tbody.innerHTML = data.files.map(f => {
        const info = getFileTypeInfo(f.filename || f.name || '');
        const source = f.source === 'web' ? '🌐 Web' : '📁 Manual';
        const fname = f.filename || f.name || '';
        const fid = f.id || '';
        const ext = getFileExt(fname);
        const viewable = ['.md', '.txt', '.csv', '.json', '.yaml', '.yml'].includes(ext);
        return `<tr>
          <td><div class="file-name-cell"><div class="file-icon ${info.cls}" style="width:28px;height:28px;font-size:0.6rem">${info.label}</div>
            <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;display:inline-block">${escapeHtml(fname)}</span></div></td>
          <td>${source}</td>
          <td>${formatSize(f.size || 0)}</td>
          <td>${formatDate(f.uploaded_at || f.mtime)}</td>
          <td style="display:flex;gap:4px">
            ${viewable && fid ? `<button class="btn btn-ghost btn-icon btn-xs" data-action="view" data-id="${escapeHtml(fid)}" data-name="${escapeHtml(fname)}" title="Xem"><i data-lucide="eye"></i></button>` : ''}
            <button class="btn btn-ghost btn-icon btn-xs" data-action="delete" data-id="${escapeHtml(fid)}" title="Xóa" ${!fid ? 'disabled' : ''}><i data-lucide="trash-2"></i></button>
          </td></tr>`;
      }).join('');

      tbody.querySelectorAll('[data-action="view"]').forEach(b => b.addEventListener('click', () => viewFile(b.dataset.id, b.dataset.name)));
      tbody.querySelectorAll('[data-action="delete"]').forEach(b => b.addEventListener('click', () => deleteFile(b.dataset.id)));
      lucide.createIcons();

      const total = data.total || 0;
      const pages = Math.ceil(total / 15);
      if (pages > 1) {
        $('#files-pagination').style.display = 'flex';
        $('#files-info').textContent = `${(state.currentPage - 1) * 15 + 1}-${Math.min(state.currentPage * 15, total)} / ${total}`;
        $('#btn-prev-page').disabled = state.currentPage <= 1;
        $('#btn-next-page').disabled = state.currentPage >= pages;
      } else { $('#files-pagination').style.display = 'none'; }
    } catch { /* silent */ }
  }

  $$('.files-tab').forEach(tab => tab.addEventListener('click', () => {
    $$('.files-tab').forEach(t => { t.classList.remove('active'); t.setAttribute('aria-selected', 'false'); });
    tab.classList.add('active'); tab.setAttribute('aria-selected', 'true');
    state.currentSource = tab.dataset.source; state.currentPage = 1; loadFiles();
  }));
  $('#btn-prev-page')?.addEventListener('click', () => { if (state.currentPage > 1) { state.currentPage--; loadFiles(); } });
  $('#btn-next-page')?.addEventListener('click', () => { state.currentPage++; loadFiles(); });

  async function deleteFile(id) {
    if (!id) return;
    const ok = await showModal('Xóa file', 'File sẽ bị xóa vĩnh viễn.', 'Xóa');
    if (!ok) return;
    try {
      const res = await apiFetch('/api/files/' + encodeURIComponent(id), { method: 'DELETE' });
      if (res.ok) { toast('success', 'Đã xóa'); loadFiles(); } else toast('error', 'Xóa thất bại');
    } catch (e) { toast('error', 'Lỗi', e.message); }
  }

  async function viewFile(id, filename) {
    if (!id) return;
    try {
      const res = await apiFetch('/api/files/' + encodeURIComponent(id) + '/content');
      if (!res.ok) { toast('error', 'Không thể xem file'); return; }
      const data = await res.json();
      $('#modal-title').textContent = filename;
      const msgEl = $('#modal-message');
      msgEl.innerHTML = '';
      const pre = document.createElement('pre');
      pre.textContent = data.content || '';
      msgEl.appendChild(pre);
      $('#modal-confirm').textContent = 'Đóng';
      $('#modal-cancel').style.display = 'none';
      const mod = $('#modal-overlay');
      const card = mod.querySelector('.modal');
      if (card) card.style.maxWidth = '800px';
      mod.classList.add('active');
      modalResolve = () => { if (card) card.style.maxWidth = ''; };
    } catch (e) { toast('error', 'Lỗi', e.message); }
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

  async function loadReviewQueue() {
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

        return `<tr data-claim-id="${escapeHtml(c.claim_id || '')}">
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
    } catch { /* silent */ }
  }

  async function reviewAction(endpoint, body) {
    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        toast('success', 'Done', `${body.claim_id} → ${endpoint.split('/').pop()}`);
        loadReviewQueue();
        loadReviewStats();
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Lỗi', err.error || 'Failed');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  // Review filters
  $('#review-filter')?.addEventListener('change', (e) => {
    reviewState.filter = e.target.value;
    reviewState.page = 1;
    loadReviewQueue();
  });
  $('#review-category')?.addEventListener('change', (e) => {
    reviewState.category = e.target.value;
    reviewState.page = 1;
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

/**
 * BKNS Wiki Data Portal — Client Application
 * Handles: Login, Upload (drag/drop), Pipeline control, File browser
 */

(function () {
  'use strict';

  // ============================================================
  // CONFIG & STATE
  // ============================================================
  const API = '';
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
  const ALLOWED_TYPES = ['.pdf', '.docx', '.xlsx', '.md', '.txt', '.png', '.jpg', '.jpeg'];
  const FILE_TYPE_MAP = {
    '.pdf': { label: 'PDF', cls: 'pdf' },
    '.docx': { label: 'DOC', cls: 'doc' },
    '.doc': { label: 'DOC', cls: 'doc' },
    '.xlsx': { label: 'XLS', cls: 'xls' },
    '.xls': { label: 'XLS', cls: 'xls' },
    '.md': { label: 'MD', cls: 'md' },
    '.txt': { label: 'TXT', cls: 'txt' },
    '.png': { label: 'PNG', cls: 'img' },
    '.jpg': { label: 'JPG', cls: 'img' },
    '.jpeg': { label: 'JPG', cls: 'img' },
  };

  let state = {
    token: localStorage.getItem('wiki_token') || '',
    fileQueue: [],
    currentPage: 1,
    currentSource: 'all',
    pipelineStatus: 'idle',
    statusInterval: null,
    // Wiki editor state
    currentTab: 'dashboard',
    wikiCurrentCategory: null,
    wikiOriginalContent: '',
    wikiDirty: false,
    wikiSaveDebounce: null,
  };

  // ============================================================
  // DOM REFS
  // ============================================================
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  const dom = {
    loginPage: $('#login-page'),
    app: $('#app'),
    loginForm: $('#login-form'),
    loginPassword: $('#login-password'),
    loginError: $('#login-error'),
    loginSubmit: $('#login-submit'),
    loginBtnText: $('#login-btn-text'),
    loginSpinner: $('#login-spinner'),
    btnLogout: $('#btn-logout'),
    uploadZone: $('#upload-zone'),
    fileInput: $('#file-input'),
    fileQueue: $('#file-queue'),
    uploadActions: $('#upload-actions'),
    btnUploadTrigger: $('#btn-upload-trigger'),
    btnUploadOnly: $('#btn-upload-only'),
    btnClearQueue: $('#btn-clear-queue'),
    pipelineStatusBadge: $('#pipeline-status-badge'),
    pipelineStatusHeader: $('#pipeline-status-header'),
    pipelineStatusText: $('#pipeline-status-text'),
    pipelineLastRun: $('#pipeline-last-run'),
    pipelineLastResult: $('#pipeline-last-result'),
    pipelineBuildVersion: $('#pipeline-build-version'),
    btnTriggerFull: $('#btn-trigger-full'),
    btnTriggerExtract: $('#btn-trigger-extract'),
    btnTriggerCompile: $('#btn-trigger-compile'),
    filesTbody: $('#files-tbody'),
    filesPagination: $('#files-pagination'),
    filesInfo: $('#files-info'),
    btnPrevPage: $('#btn-prev-page'),
    btnNextPage: $('#btn-next-page'),
    toastContainer: $('#toast-container'),
    modalOverlay: $('#modal-overlay'),
    modalTitle: $('#modal-title'),
    modalMessage: $('#modal-message'),
    modalCancel: $('#modal-cancel'),
    modalConfirm: $('#modal-confirm'),
    statTotalFiles: $('#stat-total-files'),
    statWikiPages: $('#stat-wiki-pages'),
    statClaims: $('#stat-claims'),
    statLastBuild: $('#stat-last-build'),
  };

  // ============================================================
  // UTILITIES
  // ============================================================
  function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0) + ' ' + units[i];
  }

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }

  function getFileExt(name) {
    const i = name.lastIndexOf('.');
    return i > 0 ? name.substring(i).toLowerCase() : '';
  }

  function getFileTypeInfo(name) {
    const ext = getFileExt(name);
    return FILE_TYPE_MAP[ext] || { label: 'FILE', cls: 'txt' };
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  async function apiFetch(path, options = {}) {
    const res = await fetch(API + path, {
      ...options,
      headers: {
        'Authorization': 'Bearer ' + state.token,
        ...(options.headers || {}),
      },
    });
    if (res.status === 401) {
      logout();
      throw new Error('Unauthorized');
    }
    return res;
  }

  // ============================================================
  // TOAST SYSTEM
  // ============================================================
  function toast(type, title, message, duration = 5000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.innerHTML = `
      <span class="toast-icon" aria-hidden="true">${icons[type] || 'ℹ️'}</span>
      <div class="toast-content">
        <div class="toast-title">${escapeHtml(title)}</div>
        ${message ? '<div class="toast-message">' + escapeHtml(message) + '</div>' : ''}
      </div>
      <button class="toast-close" aria-label="Đóng thông báo">&times;</button>
    `;
    el.querySelector('.toast-close').addEventListener('click', () => removeToast(el));
    dom.toastContainer.appendChild(el);

    if (duration > 0) {
      setTimeout(() => removeToast(el), duration);
    }
    return el;
  }

  function removeToast(el) {
    if (!el.parentNode) return;
    el.classList.add('removing');
    setTimeout(() => el.remove(), 200);
  }

  // ============================================================
  // MODAL SYSTEM
  // ============================================================
  let modalResolve = null;

  function showModal(title, message, confirmText = 'Xác nhận') {
    dom.modalTitle.textContent = title;
    dom.modalMessage.textContent = message;
    dom.modalConfirm.textContent = confirmText;
    dom.modalCancel.style.display = '';
    const modalCard = dom.modalOverlay.querySelector('.modal');
    if (modalCard) modalCard.style.maxWidth = '';
    dom.modalOverlay.classList.add('active');
    dom.modalConfirm.focus();
    return new Promise((resolve) => { modalResolve = resolve; });
  }

  function closeModal(result) {
    dom.modalOverlay.classList.remove('active');
    if (modalResolve) { modalResolve(result); modalResolve = null; }
  }

  dom.modalCancel.addEventListener('click', () => closeModal(false));
  dom.modalConfirm.addEventListener('click', () => closeModal(true));
  dom.modalOverlay.addEventListener('click', (e) => {
    if (e.target === dom.modalOverlay) closeModal(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && dom.modalOverlay.classList.contains('active')) {
      closeModal(false);
    }
  });

  // ============================================================
  // AUTH
  // ============================================================
  dom.loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const pw = dom.loginPassword.value.trim();
    if (!pw) return;

    dom.loginSubmit.disabled = true;
    dom.loginBtnText.style.display = 'none';
    dom.loginSpinner.style.display = 'block';
    dom.loginError.classList.remove('visible');

    try {
      const res = await fetch(API + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: pw }),
      });

      if (res.ok) {
        const data = await res.json();
        state.token = data.token;
        localStorage.setItem('wiki_token', data.token);
        showApp();
      } else {
        dom.loginError.classList.add('visible');
        dom.loginPassword.focus();
      }
    } catch {
      dom.loginError.textContent = 'Không thể kết nối server.';
      dom.loginError.classList.add('visible');
    } finally {
      dom.loginSubmit.disabled = false;
      dom.loginBtnText.style.display = 'inline';
      dom.loginSpinner.style.display = 'none';
    }
  });

  function logout() {
    state.token = '';
    localStorage.removeItem('wiki_token');
    dom.app.classList.remove('active');
    dom.loginPage.style.display = '';
    dom.loginPassword.value = '';
    if (state.statusInterval) clearInterval(state.statusInterval);
  }

  dom.btnLogout.addEventListener('click', async () => {
    const confirmed = await showModal('Đăng xuất', 'Bạn có chắc chắn muốn đăng xuất?', 'Đăng xuất');
    if (confirmed) logout();
  });

  function showApp() {
    dom.loginPage.style.display = 'none';
    dom.app.classList.add('active');
    lucide.createIcons();
    loadDashboard();
    bindWikiEvents();
    state.statusInterval = setInterval(loadStatus, 10000);
  }

  // ============================================================
  // UPLOAD — DRAG & DROP
  // ============================================================
  dom.uploadZone.addEventListener('click', () => dom.fileInput.click());
  dom.uploadZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      dom.fileInput.click();
    }
  });

  dom.uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dom.uploadZone.classList.add('drag-over');
  });

  dom.uploadZone.addEventListener('dragleave', () => {
    dom.uploadZone.classList.remove('drag-over');
  });

  dom.uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dom.uploadZone.classList.remove('drag-over');
    addFilesToQueue(e.dataTransfer.files);
  });

  dom.fileInput.addEventListener('change', () => {
    addFilesToQueue(dom.fileInput.files);
    dom.fileInput.value = '';
  });

  function addFilesToQueue(fileList) {
    for (const file of fileList) {
      const ext = getFileExt(file.name);
      if (!ALLOWED_TYPES.includes(ext)) {
        toast('warning', 'Định dạng không hỗ trợ', `${file.name} — Chỉ hỗ trợ: ${ALLOWED_TYPES.join(', ')}`);
        continue;
      }
      if (file.size > MAX_FILE_SIZE) {
        toast('warning', 'File quá lớn', `${file.name} — Tối đa 50MB/file`);
        continue;
      }
      if (state.fileQueue.some(f => f.name === file.name && f.size === file.size)) {
        continue; // skip duplicates
      }
      state.fileQueue.push(file);
    }
    renderQueue();
  }

  function renderQueue() {
    if (state.fileQueue.length === 0) {
      dom.fileQueue.style.display = 'none';
      dom.uploadActions.style.display = 'none';
      return;
    }

    dom.fileQueue.style.display = 'block';
    dom.uploadActions.style.display = 'flex';

    dom.fileQueue.innerHTML = state.fileQueue.map((file, i) => {
      const info = getFileTypeInfo(file.name);
      return `
        <div class="file-queue-item" data-index="${i}">
          <div class="file-icon ${info.cls}">${info.label}</div>
          <div class="file-info">
            <div class="file-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</div>
            <div class="file-size">${formatSize(file.size)}</div>
            <div class="progress-bar"><div class="progress-fill" id="progress-${i}"></div></div>
          </div>
          <button class="remove-btn" data-index="${i}" aria-label="Xóa ${escapeHtml(file.name)}">&times;</button>
        </div>
      `;
    }).join('');

    dom.fileQueue.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        state.fileQueue.splice(parseInt(btn.dataset.index), 1);
        renderQueue();
      });
    });
  }

  dom.btnClearQueue.addEventListener('click', () => {
    state.fileQueue = [];
    renderQueue();
  });

  // ============================================================
  // UPLOAD — EXECUTION
  // ============================================================
  async function uploadFiles(triggerPipeline) {
    if (state.fileQueue.length === 0) return;

    const files = [...state.fileQueue];
    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('trigger', triggerPipeline ? 'true' : 'false');

    // Disable buttons during upload
    dom.btnUploadTrigger.disabled = true;
    dom.btnUploadOnly.disabled = true;

    try {
      const loadingToast = toast('info', 'Đang upload...', `${files.length} file`, 0);

      const res = await apiFetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      removeToast(loadingToast);

      if (res.ok) {
        const data = await res.json();
        state.fileQueue = [];
        renderQueue();

        if (triggerPipeline) {
          toast('success', 'Upload & Trigger thành công',
            `${data.uploaded.length} file đã upload. Pipeline đang chạy...`);
        } else {
          toast('success', 'Upload thành công',
            `${data.uploaded.length} file đã upload. Chờ xử lý.`);
        }

        loadFiles();
        loadStatus();
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Upload thất bại', err.error || 'Lỗi không xác định');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    } finally {
      dom.btnUploadTrigger.disabled = false;
      dom.btnUploadOnly.disabled = false;
    }
  }

  dom.btnUploadTrigger.addEventListener('click', () => uploadFiles(true));
  dom.btnUploadOnly.addEventListener('click', () => uploadFiles(false));

  // ============================================================
  // PIPELINE CONTROL
  // ============================================================
  async function triggerPipeline(action) {
    try {
      const res = await apiFetch('/api/trigger', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action }),
      });

      if (res.ok) {
        toast('success', 'Pipeline triggered', `Action: ${action}`);
        loadStatus();
      } else {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Trigger thất bại', err.error || 'Lỗi');
      }
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  }

  dom.btnTriggerFull.addEventListener('click', async () => {
    const ok = await showModal('Chạy Full Pipeline',
      'Extract tất cả file pending → Compile wiki → Build. Tiếp tục?',
      'Chạy Pipeline');
    if (ok) triggerPipeline('full');
  });

  dom.btnTriggerExtract.addEventListener('click', () => triggerPipeline('extract'));
  dom.btnTriggerCompile.addEventListener('click', () => triggerPipeline('compile'));

  // ============================================================
  // STATUS & STATS
  // ============================================================
  async function loadStatus() {
    try {
      const res = await apiFetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();

      // Update badges
      const statusClass = data.pipeline || 'idle';
      const statusLabels = { idle: 'Idle', running: 'Đang chạy', success: 'Thành công', failed: 'Thất bại' };

      [dom.pipelineStatusBadge, dom.pipelineStatusHeader].forEach(el => {
        el.className = 'pipeline-status-badge ' + statusClass;
      });
      dom.pipelineStatusText.textContent = statusLabels[statusClass] || statusClass;
      dom.pipelineStatusHeader.querySelector('span:last-child').textContent = statusLabels[statusClass] || statusClass;

      // Update info
      dom.pipelineLastRun.textContent = formatDate(data.last_run);
      dom.pipelineLastResult.textContent = data.last_result || '—';
      dom.pipelineBuildVersion.textContent = data.build_version || '—';

      // Stats
      if (data.wiki_stats) {
        dom.statTotalFiles.textContent = data.wiki_stats.total_files || '0';
        dom.statWikiPages.textContent = data.wiki_stats.wiki_pages || '0';
        dom.statClaims.textContent = data.wiki_stats.total_claims || '0';
        dom.statLastBuild.textContent = data.wiki_stats.build_version || '—';
      }
    } catch { /* silent */ }
  }

  // ============================================================
  // FILE BROWSER
  // ============================================================
  async function loadFiles() {
    try {
      const res = await apiFetch(`/api/files?source=${state.currentSource}&page=${state.currentPage}&limit=15`);
      if (!res.ok) return;
      const data = await res.json();

      if (!data.files || data.files.length === 0) {
        dom.filesTbody.innerHTML = `
          <tr><td colspan="6" class="files-empty">
            <div style="opacity:0.3;font-size:2rem;margin-bottom:var(--space-2)">📂</div>
            Chưa có file nào
          </td></tr>`;
        dom.filesPagination.style.display = 'none';
        return;
      }

      dom.filesTbody.innerHTML = data.files.map(f => {
        const info = getFileTypeInfo(f.filename || f.name || '');
        const source = f.source === 'web' ? '🌐 Web' : '📁 Manual';
        const fileId = escapeHtml(f.id || '');
        const fname = f.filename || f.name || '';
        const ext = getFileExt(fname).toLowerCase();
        const isViewable = ['.md', '.txt', '.csv', '.json', '.yaml', '.yml'].includes(ext);
        return `
          <tr>
            <td>
              <div class="file-name-cell">
                <input type="checkbox" class="file-row-checkbox" data-id="${fileId}" aria-label="Chọn ${escapeHtml(fname)}" style="margin-right:6px;cursor:pointer;flex-shrink:0;">
                <div class="file-icon ${info.cls}" style="width:28px;height:28px;font-size:0.6rem;flex-shrink:0">${info.label}</div>
                <span class="file-name-text" title="${escapeHtml(fname)}" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;display:inline-block">${escapeHtml(fname)}</span>
              </div>
            </td>
            <td>${source}</td>
            <td class="file-size-cell">${formatSize(f.size || 0)}</td>
            <td class="file-date">${formatDate(f.uploaded_at || f.mtime)}</td>
            <td class="file-actions-cell" style="display:flex;gap:4px;align-items:center">
              ${isViewable && fileId ? `<button class="btn btn-ghost btn-icon" onclick="viewFile('${fileId}','${escapeHtml(fname)}')" aria-label="Xem nội dung ${escapeHtml(fname)}" title="Xem nội dung">
                <i data-lucide="eye" aria-hidden="true"></i>
              </button>` : ''}
              <button class="btn btn-ghost btn-icon" onclick="deleteFile('${fileId}')" aria-label="Xóa file" ${!fileId ? 'disabled' : ''} title="Xóa file">
                <i data-lucide="trash-2" aria-hidden="true"></i>
              </button>
            </td>
          </tr>`;
      }).join('');

      lucide.createIcons();

      // Wire up Select All checkbox
      const selectAll = document.getElementById('select-all-files');
      if (selectAll) {
        selectAll.checked = false;
        selectAll.addEventListener('change', () => {
          document.querySelectorAll('.file-row-checkbox').forEach(cb => {
            cb.checked = selectAll.checked;
          });
          updateBulkDeleteBtn();
        });
      }
      document.querySelectorAll('.file-row-checkbox').forEach(cb => {
        cb.addEventListener('change', () => {
          if (selectAll) selectAll.checked = [...document.querySelectorAll('.file-row-checkbox')].every(c => c.checked);
          updateBulkDeleteBtn();
        });
      });

      // Pagination
      const total = data.total || 0;
      const totalPages = Math.ceil(total / 15);
      if (totalPages > 1) {
        dom.filesPagination.style.display = 'flex';
        const start = (state.currentPage - 1) * 15 + 1;
        const end = Math.min(state.currentPage * 15, total);
        dom.filesInfo.textContent = `${start}-${end} / ${total}`;
        dom.btnPrevPage.disabled = state.currentPage <= 1;
        dom.btnNextPage.disabled = state.currentPage >= totalPages;
      } else {
        dom.filesPagination.style.display = 'none';
      }
    } catch { /* silent */ }
  }

  // File source tabs
  $$('.files-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      $$('.files-tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
      });
      tab.classList.add('active');
      tab.setAttribute('aria-selected', 'true');
      state.currentSource = tab.dataset.source;
      state.currentPage = 1;
      loadFiles();
    });
  });

  dom.btnPrevPage.addEventListener('click', () => {
    if (state.currentPage > 1) { state.currentPage--; loadFiles(); }
  });

  dom.btnNextPage.addEventListener('click', () => {
    state.currentPage++;
    loadFiles();
  });

  // Delete file (exposed globally for inline onclick)
  window.deleteFile = async function (id) {
    if (!id) return;
    const ok = await showModal('Xóa file', 'File sẽ bị xóa vĩnh viễn. Tiếp tục?', 'Xóa');
    if (!ok) return;

    try {
      const res = await apiFetch('/api/files/' + encodeURIComponent(id), { method: 'DELETE' });
      if (res.ok) {
        toast('success', 'Đã xóa file');
        loadFiles();
        loadStatus();
      } else {
        toast('error', 'Xóa thất bại');
      }
    } catch (e) {
      toast('error', 'Lỗi', e.message);
    }
  };

  // View file content in modal (text files only)
  window.viewFile = async function (id, filename) {
    if (!id) return;
    try {
      const res = await apiFetch('/api/files/' + encodeURIComponent(id) + '/content');
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast('error', 'Không thể xem file', err.error || 'Lỗi');
        return;
      }
      const data = await res.json();
      const content = data.content || '';
      const lines = content.split('\n').length;

      // Show file content in wider modal
      dom.modalTitle.textContent = filename;
      dom.modalMessage.innerHTML = '';

      const pre = document.createElement('pre');
      pre.style.cssText = 'max-height:60vh;overflow:auto;font-size:0.75rem;white-space:pre-wrap;word-break:break-word;text-align:left;background:var(--surface-2,#1a1a2e);padding:var(--space-3);border-radius:6px;margin:0 0 var(--space-2)';
      pre.textContent = content;
      dom.modalMessage.appendChild(pre);

      const meta = document.createElement('div');
      meta.style.cssText = 'font-size:0.75rem;opacity:0.5';
      meta.textContent = `${lines} dòng · ${formatSize(data.size || content.length)}`;
      dom.modalMessage.appendChild(meta);

      // Expand modal for file viewing
      const modalCard = dom.modalOverlay.querySelector('.modal');
      if (modalCard) modalCard.style.maxWidth = '800px';

      dom.modalConfirm.textContent = 'Đóng';
      dom.modalCancel.style.display = 'none';
      dom.modalOverlay.classList.add('active');
      dom.modalConfirm.focus();
      // Override confirm to close and restore modal
      const cleanup = () => {
        dom.modalConfirm.textContent = 'Xác nhận';
        dom.modalCancel.style.display = '';
        if (modalCard) modalCard.style.maxWidth = '';
      };
      modalResolve = () => { cleanup(); };
    } catch (e) {
      toast('error', 'Lỗi kết nối', e.message);
    }
  };

  // Update selection counter (checkboxes are for selection only — no bulk action)
  function updateBulkDeleteBtn() {
    const info = document.getElementById('files-selected-info');
    if (!info) return;
    const checked = [...document.querySelectorAll('.file-row-checkbox:checked')];
    if (checked.length > 0) {
      info.style.display = 'inline';
      info.textContent = `Đã chọn ${checked.length} file`;
    } else {
      info.style.display = 'none';
    }
  }

  // ============================================================
  // TAB NAVIGATION
  // ============================================================
  function switchTab(tabName) {
    state.currentTab = tabName;

    // Update nav buttons
    $$('.nav-tab').forEach(btn => {
      const active = btn.dataset.tab === tabName;
      btn.classList.toggle('active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    // Show/hide main panels
    const mainEl = $('#main-content');
    const wikiEl = $('#wiki-page');

    if (tabName === 'dashboard') {
      mainEl.style.display = '';
      wikiEl.style.display = 'none';
    } else if (tabName === 'wiki') {
      mainEl.style.display = 'none';
      wikiEl.style.display = 'flex';
      loadWikiList();
    }
    lucide.createIcons();
  }

  $$('.nav-tab').forEach(btn => {
    btn.addEventListener('click', async () => {
      if (btn.dataset.tab === state.currentTab) return;
      // Warn about unsaved changes when leaving wiki tab
      if (state.currentTab === 'wiki' && state.wikiDirty) {
        const ok = await showModal(
          'Thay đổi chưa lưu',
          'Bạn có thay đổi chưa lưu. Rời khỏi trang này?',
          'Rời đi'
        );
        if (!ok) return;
        state.wikiDirty = false;
      }
      switchTab(btn.dataset.tab);
    });
  });

  // ============================================================
  // WIKI EDITOR — HELPERS
  // ============================================================
  const CATEGORY_LABELS = {
    hosting: 'Hosting',
    vps: 'VPS',
    ssl: 'SSL',
    'ten-mien': 'Tên Miền',
    email: 'Email',
    server: 'Server',
    software: 'Software',
    other: 'Other',
    uncategorized: 'Chưa phân loại',
  };

  const REVIEW_STATE_CONFIG = {
    approved:   { label: 'Approved',   cls: 'badge-success' },
    pending:    { label: 'Pending',    cls: 'badge-warning' },
    unknown:    { label: 'Unknown',    cls: 'badge-muted' },
  };

  function renderWikiPreview(markdown) {
    if (typeof marked === 'undefined') return '<em>marked.js chưa tải</em>';
    try {
      const html = marked.parse(markdown, { breaks: true, gfm: true });
      // Open all links in new tab so they don't navigate away from the app
      return html.replace(/<a href=/g, '<a target="_blank" rel="noopener noreferrer" href=');
    } catch {
      return '<em>Lỗi render markdown</em>';
    }
  }

  function updateWordCount(text) {
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const chars = text.length;
    $('#wiki-word-count').textContent = words.toLocaleString('vi-VN') + ' từ';
    $('#wiki-char-count').textContent = chars.toLocaleString('vi-VN') + ' ký tự';
  }

  function setSaveStatus(status, message) {
    const el = $('#wiki-save-status');
    if (!el) return;
    el.className = 'wiki-save-status ' + (status || '');
    el.textContent = message || '';
  }

  function markDirty() {
    if (!state.wikiDirty) {
      state.wikiDirty = true;
      setSaveStatus('dirty', '● Chưa lưu');
    }
  }

  function markClean() {
    state.wikiDirty = false;
    state.wikiOriginalContent = $('#wiki-textarea') ? $('#wiki-textarea').value : '';
    setSaveStatus('saved', '✓ Đã lưu');
    setTimeout(() => setSaveStatus('', ''), 3000);
  }

  // ============================================================
  // WIKI EDITOR — LIST
  // ============================================================
  async function loadWikiList() {
    const listEl = $('#wiki-page-list');
    listEl.innerHTML = '<li class="wiki-page-list-empty"><i data-lucide="loader" style="animation:spin 1s linear infinite"></i> Đang tải...</li>';
    lucide.createIcons();

    try {
      const res = await apiFetch('/api/wiki');
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();

      if (!data.pages || data.pages.length === 0) {
        listEl.innerHTML = '<li class="wiki-page-list-empty">Không có wiki page nào</li>';
        return;
      }

      listEl.innerHTML = data.pages.map(p => {
        const label = CATEGORY_LABELS[p.category] || p.category;
        const rc = REVIEW_STATE_CONFIG[p.review_state] || REVIEW_STATE_CONFIG.unknown;
        const existsIcon = p.exists ? '' : ' wiki-page-missing';
        const activeClass = p.category === state.wikiCurrentCategory ? ' active' : '';
        return `
          <li class="wiki-page-item${existsIcon}${activeClass}"
              data-category="${escapeHtml(p.category)}"
              role="option"
              aria-selected="${p.category === state.wikiCurrentCategory ? 'true' : 'false'}"
              tabindex="0">
            <div class="wiki-page-item-name">
              <i data-lucide="${p.exists ? 'file-text' : 'file-x'}" class="wiki-page-item-icon" aria-hidden="true"></i>
              <span>${escapeHtml(label)}</span>
            </div>
            <div class="wiki-page-item-meta">
              <span class="wiki-badge ${rc.cls}">${rc.label}</span>
              ${p.sensitivity === 'high' ? '<span class="wiki-badge badge-error">Nhạy cảm</span>' : ''}
            </div>
            ${p.exists ? `<div class="wiki-page-item-date">${p.updated || ''}</div>` : '<div class="wiki-page-item-date">Chưa compile</div>'}
          </li>`;
      }).join('');

      lucide.createIcons();

      // Click & keyboard handlers
      listEl.querySelectorAll('.wiki-page-item:not(.wiki-page-missing)').forEach(item => {
        item.addEventListener('click', () => loadWikiPage(item.dataset.category));
        item.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            loadWikiPage(item.dataset.category);
          }
        });
      });
    } catch {
      listEl.innerHTML = '<li class="wiki-page-list-empty">Lỗi tải danh sách</li>';
    }
  }

  // ============================================================
  // WIKI EDITOR — LOAD PAGE
  // ============================================================
  async function loadWikiPage(category) {
    // Warn about unsaved changes
    if (state.wikiDirty) {
      const ok = await showModal(
        'Thay đổi chưa lưu',
        'Chuyển sang trang khác sẽ mất thay đổi chưa lưu. Tiếp tục?',
        'Tiếp tục'
      );
      if (!ok) return;
    }

    state.wikiCurrentCategory = category;
    state.wikiDirty = false;
    setSaveStatus('', '');

    // Update active state in sidebar
    $$('.wiki-page-item').forEach(el => {
      const active = el.dataset.category === category;
      el.classList.toggle('active', active);
      el.setAttribute('aria-selected', active ? 'true' : 'false');
    });

    // Show editor panel, hide empty state
    $('#wiki-empty-state').style.display = 'none';
    const panel = $('#wiki-editor-panel');
    panel.style.display = 'flex';

    // Show loading state
    const textarea = $('#wiki-textarea');
    const preview = $('#wiki-preview');
    textarea.value = 'Đang tải...';
    textarea.disabled = true;
    preview.innerHTML = '<div class="wiki-preview-loading"><i data-lucide="loader" style="animation:spin 1s linear infinite"></i><span>Đang tải nội dung...</span></div>';
    lucide.createIcons();

    try {
      const res = await apiFetch(`/api/wiki/${encodeURIComponent(category)}`);
      if (!res.ok) throw new Error('Failed to load');
      const data = await res.json();

      textarea.value = data.content;
      textarea.disabled = false;
      state.wikiOriginalContent = data.content;

      // Update breadcrumb
      $('#wiki-editor-category').textContent = category;

      // Render frontmatter badges
      renderFrontmatterBadges(data.frontmatter);

      // Render preview
      preview.innerHTML = renderWikiPreview(data.content);

      // Update word count
      updateWordCount(data.content);

      // Focus editor
      textarea.focus();

      lucide.createIcons();
    } catch {
      textarea.value = '';
      textarea.disabled = false;
      preview.innerHTML = '<div class="wiki-preview-error">Lỗi tải nội dung</div>';
      toast('error', 'Lỗi tải wiki page', `Không thể tải ${category}`);
    }
  }

  function renderFrontmatterBadges(fm) {
    const badgesEl = $('#wiki-editor-badges');
    if (!badgesEl || !fm) return;

    const badges = [];

    if (fm.review_state) {
      const rc = REVIEW_STATE_CONFIG[fm.review_state] || REVIEW_STATE_CONFIG.unknown;
      badges.push(`<span class="wiki-badge ${rc.cls}"><i data-lucide="check-circle" aria-hidden="true"></i> ${rc.label}</span>`);
    }
    if (fm.sensitivity === 'high') {
      badges.push('<span class="wiki-badge badge-error"><i data-lucide="alert-triangle" aria-hidden="true"></i> Nhạy cảm cao</span>');
    }
    if (fm.updated) {
      badges.push(`<span class="wiki-badge badge-muted"><i data-lucide="calendar" aria-hidden="true"></i> ${fm.updated}</span>`);
    }

    badgesEl.innerHTML = badges.join('');
    lucide.createIcons();
  }

  // ============================================================
  // WIKI EDITOR — TEXTAREA INPUT (live preview)
  // ============================================================
  document.addEventListener('DOMContentLoaded', () => { /* handled in showApp */ });

  function bindWikiTextarea() {
    const textarea = $('#wiki-textarea');
    if (!textarea || textarea._wikibound) return;
    textarea._wikibound = true;

    let previewTimer = null;

    textarea.addEventListener('input', () => {
      markDirty();
      updateWordCount(textarea.value);

      // Debounced preview update (150ms)
      clearTimeout(previewTimer);
      previewTimer = setTimeout(() => {
        const preview = $('#wiki-preview');
        if (preview && $('#wiki-preview-pane').style.display !== 'none') {
          preview.innerHTML = renderWikiPreview(textarea.value);
          lucide.createIcons();
        }
      }, 150);
    });

    // Ctrl+S / Cmd+S to save
    textarea.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveWikiPage();
      }
      // Tab key inserts 2 spaces
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        textarea.value = textarea.value.slice(0, start) + '  ' + textarea.value.slice(end);
        textarea.selectionStart = textarea.selectionEnd = start + 2;
        markDirty();
      }
    });
  }

  // ============================================================
  // WIKI EDITOR — VIEW TOGGLE
  // ============================================================
  function bindViewToggle() {
    $$('.wiki-view-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        $$('.wiki-view-btn').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');

        const view = btn.dataset.view;
        const editPane = $('#wiki-edit-pane');
        const previewPane = $('#wiki-preview-pane');
        const resizeHandle = $('#wiki-resize-handle');
        const splitPane = $('#wiki-split-pane');

        splitPane.className = 'wiki-split-pane view-' + view;

        if (view === 'split') {
          editPane.style.display = '';
          previewPane.style.display = '';
          resizeHandle.style.display = '';
          // Refresh preview
          const preview = $('#wiki-preview');
          const textarea = $('#wiki-textarea');
          if (preview && textarea) preview.innerHTML = renderWikiPreview(textarea.value);
          lucide.createIcons();
        } else if (view === 'edit') {
          editPane.style.display = '';
          previewPane.style.display = 'none';
          resizeHandle.style.display = 'none';
          $('#wiki-textarea').focus();
        } else if (view === 'preview') {
          editPane.style.display = 'none';
          previewPane.style.display = '';
          resizeHandle.style.display = 'none';
          const preview = $('#wiki-preview');
          const textarea = $('#wiki-textarea');
          if (preview && textarea) preview.innerHTML = renderWikiPreview(textarea.value);
          lucide.createIcons();
        }
      });
    });
  }

  // ============================================================
  // WIKI EDITOR — RESIZE HANDLE
  // ============================================================
  function bindResizeHandle() {
    const handle = $('#wiki-resize-handle');
    const splitPane = $('#wiki-split-pane');
    if (!handle || !splitPane) return;

    let dragging = false;
    let startX = 0;
    let startLeftWidth = 0;

    handle.addEventListener('mousedown', (e) => {
      dragging = true;
      startX = e.clientX;
      const editPane = $('#wiki-edit-pane');
      startLeftWidth = editPane.getBoundingClientRect().width;
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      const totalWidth = splitPane.getBoundingClientRect().width;
      const newLeft = Math.max(200, Math.min(totalWidth - 200, startLeftWidth + dx));
      const pct = (newLeft / totalWidth) * 100;
      $('#wiki-edit-pane').style.flex = `0 0 ${pct}%`;
      $('#wiki-preview-pane').style.flex = `0 0 ${100 - pct - 0.5}%`;
    });

    document.addEventListener('mouseup', () => {
      if (!dragging) return;
      dragging = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    });
  }

  // ============================================================
  // WIKI EDITOR — SAVE
  // ============================================================
  async function saveWikiPage() {
    if (!state.wikiCurrentCategory) return;
    if (!state.wikiDirty) {
      toast('info', 'Không có thay đổi', 'Nội dung chưa được chỉnh sửa');
      return;
    }

    const textarea = $('#wiki-textarea');
    const content = textarea.value;

    if (!content.trim()) {
      toast('warning', 'Nội dung trống', 'Không thể lưu trang wiki trống');
      return;
    }

    const saveBtn = $('#btn-wiki-save');
    saveBtn.disabled = true;
    setSaveStatus('saving', '⏳ Đang lưu...');

    try {
      const res = await apiFetch(`/api/wiki/${encodeURIComponent(state.wikiCurrentCategory)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });

      if (res.ok) {
        const data = await res.json();
        markClean();
        renderFrontmatterBadges(data.frontmatter);
        toast('success', 'Đã lưu thành công',
          `${CATEGORY_LABELS[state.wikiCurrentCategory] || state.wikiCurrentCategory} — ${(data.size / 1024).toFixed(1)} KB`);
        // Refresh sidebar dates
        loadWikiList().then(() => {
          // Re-select current item in list
          const item = $(`[data-category="${state.wikiCurrentCategory}"]`);
          if (item) { item.classList.add('active'); item.setAttribute('aria-selected', 'true'); }
        });
      } else {
        const err = await res.json().catch(() => ({}));
        setSaveStatus('dirty', '● Chưa lưu');
        toast('error', 'Lưu thất bại', err.error || 'Lỗi không xác định');
      }
    } catch (e) {
      setSaveStatus('dirty', '● Chưa lưu');
      toast('error', 'Lỗi kết nối', e.message);
    } finally {
      saveBtn.disabled = false;
    }
  }

  // ============================================================
  // WIKI EDITOR — BACKUPS
  // ============================================================
  async function loadWikiBackups(category) {
    const listEl = $('#wiki-backups-list');
    listEl.innerHTML = '<li class="wiki-backups-empty"><i data-lucide="loader" style="animation:spin 1s linear infinite"></i> Đang tải...</li>';
    lucide.createIcons();

    try {
      const res = await apiFetch(`/api/wiki/${encodeURIComponent(category)}/backups`);
      if (!res.ok) throw new Error('Failed');
      const data = await res.json();

      if (!data.backups || data.backups.length === 0) {
        listEl.innerHTML = '<li class="wiki-backups-empty">Chưa có backup nào</li>';
        return;
      }

      listEl.innerHTML = data.backups.map(b => `
        <li class="wiki-backup-item">
          <i data-lucide="file-clock" class="wiki-backup-icon" aria-hidden="true"></i>
          <div class="wiki-backup-info">
            <div class="wiki-backup-name">${escapeHtml(b.filename)}</div>
            <div class="wiki-backup-meta">${formatDate(b.mtime)} · ${formatSize(b.size)}</div>
          </div>
        </li>`).join('');
      lucide.createIcons();
    } catch {
      listEl.innerHTML = '<li class="wiki-backups-empty">Lỗi tải backups</li>';
    }
  }

  // ============================================================
  // WIKI EDITOR — EVENT BINDING (called after showApp)
  // ============================================================
  function bindWikiEvents() {
    // Save button
    const saveBtn = $('#btn-wiki-save');
    if (saveBtn) saveBtn.addEventListener('click', saveWikiPage);

    // Refresh list
    const refreshBtn = $('#btn-wiki-refresh');
    if (refreshBtn) refreshBtn.addEventListener('click', loadWikiList);

    // Backups toggle
    const backupsBtn = $('#btn-wiki-backups');
    const backupsDrawer = $('#wiki-backups-drawer');
    const closeBackupsBtn = $('#btn-close-backups');

    if (backupsBtn) {
      backupsBtn.addEventListener('click', () => {
        const isOpen = backupsDrawer.style.display !== 'none';
        if (isOpen) {
          backupsDrawer.style.display = 'none';
        } else {
          backupsDrawer.style.display = 'block';
          if (state.wikiCurrentCategory) loadWikiBackups(state.wikiCurrentCategory);
        }
      });
    }

    if (closeBackupsBtn) {
      closeBackupsBtn.addEventListener('click', () => {
        backupsDrawer.style.display = 'none';
      });
    }

    // Bind textarea, view toggle, resize
    bindWikiTextarea();
    bindViewToggle();
    bindResizeHandle();

    // Warn on browser close with unsaved changes
    window.addEventListener('beforeunload', (e) => {
      if (state.wikiDirty) {
        e.preventDefault();
      }
    });
  }

  // ============================================================
  // DASHBOARD LOAD
  // ============================================================
  function loadDashboard() {
    loadStatus();
    loadFiles();
  }

  // ============================================================
  // INIT
  // ============================================================
  if (state.token) {
    // Verify token
    apiFetch('/api/status').then(res => {
      if (res.ok) showApp();
      else logout();
    }).catch(() => logout());
  }

  lucide.createIcons();

})();

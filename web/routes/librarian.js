'use strict';

/**
 * Librarian routes — AI Thủ thư
 *
 *   POST /api/librarian/chat       { message, sessionId? }      → { reply, sessionId, classification? }
 *   POST /api/librarian/upload     multipart files[] + sessionId? → { staged: [...] }
 *   POST /api/librarian/note       { text, hint?, sessionId? }  → { staged }
 *   POST /api/librarian/trigger                                  → { ok, output }
 *   GET  /api/librarian/status                                   → status counts
 *   GET  /api/librarian/session/:id                              → recent messages
 */

const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');

const store = require('../lib/librarian-store');
const gemini = require('../lib/gemini-bridge');

const REPO_ROOT = path.resolve(__dirname, '../..');
const PROCESSOR = path.join(REPO_ROOT, 'tools', 'librarian_processor.py');
const TEMP_UPLOAD_DIR = path.join(store.LIBRARIAN_ROOT, '_tmp');
fs.mkdirSync(TEMP_UPLOAD_DIR, { recursive: true });

const ALLOWED_EXTS = new Set([
  '.md', '.txt', '.yaml', '.yml',
  '.pdf', '.docx', '.xlsx', '.pptx', '.epub',
  '.png', '.jpg', '.jpeg', '.webp', '.gif',
  '.html', '.csv', '.json',
]);
const MAX_FILE_SIZE = 50 * 1024 * 1024;
const MAX_FILES = 10;

const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, TEMP_UPLOAD_DIR),
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      cb(null, `tmp-${uuidv4()}${ext}`);
    },
  }),
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (!ALLOWED_EXTS.has(ext)) {
      return cb(new Error(`Định dạng ${ext} không được phép`));
    }
    cb(null, true);
  },
  limits: { fileSize: MAX_FILE_SIZE, files: MAX_FILES },
});

function readExcerpt(filePath, ext, maxBytes = 4000) {
  const textExts = new Set(['.md', '.txt', '.yaml', '.yml', '.html', '.csv', '.json']);
  if (!textExts.has(ext)) return '';
  try {
    const fd = fs.openSync(filePath, 'r');
    const buf = Buffer.alloc(maxBytes);
    const n = fs.readSync(fd, buf, 0, maxBytes, 0);
    fs.closeSync(fd);
    return buf.slice(0, n).toString('utf8');
  } catch {
    return '';
  }
}

function librarianRoute(app) {
  const router = require('express').Router();

  // ── CHAT ────────────────────────────────────────────────
  router.post('/chat', async (req, res) => {
    const { message, sessionId } = req.body || {};
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'message is required' });
    }
    const safeMsg = store.redactSecrets(message.slice(0, 4000));
    const sid = sessionId || `s-${uuidv4()}`;

    try {
      store.appendChatMessage(sid, 'user', safeMsg);
      const history = store.loadSession(sid, 10).slice(0, -1); // exclude just-appended

      const result = await gemini.chat({ message: safeMsg, history });
      const reply = (result.reply || '').trim() || '(Thủ thư không có phản hồi.)';

      store.appendChatMessage(sid, 'assistant', reply, {
        cost_usd: result.cost_usd,
        tokens_in: result.tokens_in,
        tokens_out: result.tokens_out,
      });

      res.json({
        ok: true,
        sessionId: sid,
        reply,
        meta: {
          model: result.model,
          cost_usd: result.cost_usd,
          tokens_in: result.tokens_in,
          tokens_out: result.tokens_out,
        },
      });
    } catch (err) {
      store.appendLog('chat_error', { sid, error: err.message });
      console.error('[LIBRARIAN] chat error:', err.message);
      res.status(500).json({ error: 'Gemini chat failed', detail: err.message });
    }
  });

  // ── UPLOAD ─────────────────────────────────────────────
  router.post('/upload', upload.array('files', MAX_FILES), async (req, res) => {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'Không có file nào được upload' });
    }
    const sessionId = req.body.sessionId || null;
    const userHint = (req.body.hint || '').toString().slice(0, 500);
    const staged = [];

    for (const file of req.files) {
      const ext = path.extname(file.originalname).toLowerCase();
      let classification = null;

      try {
        const excerpt = readExcerpt(file.path, ext);
        const cls = await gemini.classify({
          name: file.originalname,
          ext,
          excerpt,
          user_hint: userHint,
        });
        classification = cls.classification;
      } catch (err) {
        store.appendLog('classify_error', {
          file: file.originalname,
          error: err.message,
        });
        classification = {
          category: 'uncategorized',
          type: 'raw-doc',
          suggested_path: `raw/librarian/_unclassified/${file.originalname}`,
          summary: '(classify failed — fallback)',
          confidence: 0.0,
          tags: [],
          fallback: true,
        };
      }

      const entry = store.stageFile({
        tempPath: file.path,
        originalName: file.originalname,
        size: file.size,
        classification,
        sessionId,
      });

      staged.push({
        id: entry.id,
        filename: file.originalname,
        size: file.size,
        category: classification.category,
        type: classification.type,
        suggested_path: classification.suggested_path,
        confidence: classification.confidence,
        needs_review: entry.needs_review,
      });
    }

    if (sessionId) {
      const summary = staged
        .map((s) => `📎 ${s.filename} → ${s.category}/${s.type} (${(s.confidence * 100).toFixed(0)}%)`)
        .join('\n');
      store.appendChatMessage(sessionId, 'system', `Đã staging ${staged.length} file:\n${summary}`);
    }

    res.json({ ok: true, staged });
  });

  // ── NOTE (chat-only text staging) ───────────────────────
  router.post('/note', async (req, res) => {
    const { text, hint, sessionId } = req.body || {};
    if (!text || typeof text !== 'string') {
      return res.status(400).json({ error: 'text is required' });
    }
    const safeText = store.redactSecrets(text);

    let classification;
    try {
      const cls = await gemini.classify({
        name: 'note.md',
        ext: '.md',
        excerpt: safeText.slice(0, 4000),
        user_hint: (hint || '').toString().slice(0, 500),
      });
      classification = cls.classification;
    } catch (err) {
      classification = {
        category: 'uncategorized',
        type: 'note',
        suggested_path: 'wiki/products/uncategorized/_notes/note.md',
        summary: '(classify failed)',
        confidence: 0.0,
        tags: [],
        fallback: true,
      };
    }

    const entry = store.stageNote({ text: safeText, classification, sessionId });
    res.json({
      ok: true,
      id: entry.id,
      category: classification.category,
      type: classification.type,
      suggested_path: classification.suggested_path,
      confidence: classification.confidence,
      needs_review: entry.needs_review,
    });
  });

  // ── STATUS ─────────────────────────────────────────────
  router.get('/status', (req, res) => {
    res.json(store.getStatus());
  });

  // ── SESSION HISTORY ────────────────────────────────────
  router.get('/session/:id', (req, res) => {
    const id = req.params.id;
    if (!/^s-[\w-]{8,}$/.test(id)) return res.status(400).json({ error: 'bad session id' });
    res.json({ sessionId: id, messages: store.loadSession(id, 50) });
  });

  // ── TRIGGER PROCESSOR NOW ──────────────────────────────
  // Stale lock auto-expire: if a previous processor crashed and left the lock
  // behind, unblock after LOCK_MAX_AGE_MS instead of requiring manual cleanup.
  const LOCK_MAX_AGE_MS = 60 * 60 * 1000; // 1 hour
  router.post('/trigger', (req, res) => {
    const lockFile = path.join(store.LIBRARIAN_ROOT, '.processor.lock');
    if (fs.existsSync(lockFile)) {
      try {
        const ageMs = Date.now() - fs.statSync(lockFile).mtimeMs;
        if (ageMs > LOCK_MAX_AGE_MS) {
          fs.unlinkSync(lockFile);
          console.warn(`[librarian] Removed stale lock (${Math.round(ageMs / 1000)}s old)`);
        } else {
          const minsLeft = Math.ceil((LOCK_MAX_AGE_MS - ageMs) / 60000);
          return res.status(409).json({
            error: `Processor đang chạy. Lock sẽ tự gỡ sau ${minsLeft} phút nếu treo.`,
          });
        }
      } catch (err) {
        console.error('[librarian] lock stat failed:', err);
        return res.status(500).json({ error: 'Không đọc được lock file' });
      }
    }

    const child = spawn('python3', [PROCESSOR, '--mode', 'now'], {
      cwd: REPO_ROOT,
      env: { ...process.env, PYTHONPATH: REPO_ROOT },
      detached: false,
    });

    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    child.on('close', (code) => {
      // Lock cleanup is processor's job — but defensive remove
      if (fs.existsSync(lockFile)) {
        try { fs.unlinkSync(lockFile); } catch {}
      }
      if (code === 0) {
        let report = null;
        try { report = JSON.parse(stdout); } catch {}
        return res.json({ ok: true, report, raw: report ? undefined : stdout.slice(-500) });
      }
      res.status(500).json({
        ok: false,
        error: `processor exit ${code}`,
        stderr: stderr.slice(-500),
      });
    });

    child.on('error', (err) => {
      res.status(500).json({ ok: false, error: err.message });
    });
  });

  // Multer error handler
  router.use((err, req, res, _next) => {
    if (err instanceof multer.MulterError) {
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(413).json({ error: 'File quá lớn (max 50MB)' });
      }
      return res.status(400).json({ error: err.message });
    }
    if (err) return res.status(400).json({ error: err.message });
  });

  app.use('/api/librarian', router);
}

module.exports = { librarianRoute };

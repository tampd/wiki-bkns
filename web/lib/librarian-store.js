'use strict';

/**
 * Librarian Store — stage files & metadata into wiki/.librarian/inbox/
 * Layout:
 *   .librarian/
 *     inbox/<YYYY-MM-DD>/<id>.<ext>           — payload
 *     inbox/<YYYY-MM-DD>/<id>.meta.json       — metadata
 *     inbox/_review/<id>.{ext,meta.json}      — low-confidence items needing human review
 *     chat-sessions/<session-id>.jsonl        — chat history append-only
 *     logs/librarian-<YYYY-MM-DD>.log         — operational log
 */

const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const LIBRARIAN_ROOT = path.resolve(__dirname, '../../.librarian');
const REVIEW_THRESHOLD = 0.7;

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function inboxDir(forReview = false) {
  const sub = forReview ? '_review' : todayStr();
  return ensureDir(path.join(LIBRARIAN_ROOT, 'inbox', sub));
}

function logsDir() {
  return ensureDir(path.join(LIBRARIAN_ROOT, 'logs'));
}

function chatDir() {
  return ensureDir(path.join(LIBRARIAN_ROOT, 'chat-sessions'));
}

function appendLog(action, payload) {
  const line = JSON.stringify({
    ts: new Date().toISOString(),
    action,
    ...payload,
  }) + '\n';
  const file = path.join(logsDir(), `librarian-${todayStr()}.log`);
  fs.appendFileSync(file, line);
}

/**
 * Stage an already-uploaded file (from multer) into the inbox.
 * @param {object} args
 * @param {string} args.tempPath — multer file.path
 * @param {string} args.originalName
 * @param {number} args.size
 * @param {object} args.classification — { category, type, suggested_path, summary, confidence }
 * @param {string} [args.sessionId]
 * @returns {object} entry { id, stored_path, meta_path, needs_review }
 */
function stageFile({ tempPath, originalName, size, classification, sessionId }) {
  const id = uuidv4();
  const ext = path.extname(originalName).toLowerCase();
  const safeBase = path
    .basename(originalName, ext)
    .replace(/[^a-zA-Z0-9_\-]/g, '_')
    .substring(0, 80) || 'file';

  const needsReview = (classification?.confidence ?? 0) < REVIEW_THRESHOLD;
  const dir = inboxDir(needsReview);
  const storedName = `${id}-${safeBase}${ext}`;
  const storedPath = path.join(dir, storedName);
  const metaPath = path.join(dir, `${id}.meta.json`);

  fs.renameSync(tempPath, storedPath);

  const meta = {
    id,
    original_name: originalName,
    stored_name: storedName,
    size,
    ext,
    staged_at: new Date().toISOString(),
    session_id: sessionId || null,
    source: 'librarian-chat',
    classification: classification || null,
    needs_review: needsReview,
    processed: false,
  };
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));

  appendLog('stage_file', {
    id,
    original_name: originalName,
    size,
    needs_review: needsReview,
    category: classification?.category,
    type: classification?.type,
  });

  return {
    id,
    stored_path: storedPath,
    meta_path: metaPath,
    needs_review: needsReview,
  };
}

/**
 * Stage a raw text note (from chat content, no file attached).
 */
function stageNote({ text, classification, sessionId }) {
  const id = uuidv4();
  const needsReview = (classification?.confidence ?? 0) < REVIEW_THRESHOLD;
  const dir = inboxDir(needsReview);
  const storedName = `${id}-note.md`;
  const storedPath = path.join(dir, storedName);
  const metaPath = path.join(dir, `${id}.meta.json`);

  fs.writeFileSync(storedPath, text);

  const meta = {
    id,
    original_name: storedName,
    stored_name: storedName,
    size: Buffer.byteLength(text, 'utf8'),
    ext: '.md',
    staged_at: new Date().toISOString(),
    session_id: sessionId || null,
    source: 'librarian-chat-note',
    classification: classification || null,
    needs_review: needsReview,
    processed: false,
  };
  fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));

  appendLog('stage_note', {
    id,
    size: meta.size,
    needs_review: needsReview,
    category: classification?.category,
  });

  return { id, stored_path: storedPath, meta_path: metaPath, needs_review: needsReview };
}

function appendChatMessage(sessionId, role, content, extra = {}) {
  if (!sessionId) sessionId = `s-${uuidv4()}`;
  const file = path.join(chatDir(), `${sessionId}.jsonl`);
  const line = JSON.stringify({
    ts: new Date().toISOString(),
    role,
    content,
    ...extra,
  }) + '\n';
  fs.appendFileSync(file, line);
  return sessionId;
}

function loadSession(sessionId, limit = 20) {
  const file = path.join(chatDir(), `${sessionId}.jsonl`);
  if (!fs.existsSync(file)) return [];
  const lines = fs.readFileSync(file, 'utf8').trim().split('\n').filter(Boolean);
  return lines.slice(-limit).map((l) => JSON.parse(l));
}

function getStatus() {
  const today = todayStr();
  const todayDir = path.join(LIBRARIAN_ROOT, 'inbox', today);
  const reviewDir = path.join(LIBRARIAN_ROOT, 'inbox', '_review');
  const processedRoot = path.join(LIBRARIAN_ROOT, 'processed');

  const count = (dir) => {
    if (!fs.existsSync(dir)) return 0;
    return fs.readdirSync(dir).filter((n) => n.endsWith('.meta.json')).length;
  };

  return {
    today,
    inbox_today: count(todayDir),
    inbox_review: count(reviewDir),
    processed_total: fs.existsSync(processedRoot)
      ? fs
          .readdirSync(processedRoot)
          .reduce((acc, day) => acc + count(path.join(processedRoot, day)), 0)
      : 0,
    last_run: readLastRun(),
  };
}

function readLastRun() {
  const file = path.join(LIBRARIAN_ROOT, 'logs', 'last-run.json');
  if (!fs.existsSync(file)) return null;
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return null;
  }
}

// Sanitize: redact obvious secrets before persisting chat
function redactSecrets(text) {
  if (!text) return text;
  return text
    .replace(/sk-[a-zA-Z0-9_-]{20,}/g, 'sk-***REDACTED***')
    .replace(/(api[_-]?key\s*[:=]\s*)['"]?[A-Za-z0-9_\-]{16,}['"]?/gi, '$1***REDACTED***')
    .replace(/(password\s*[:=]\s*)['"]?[^\s'"]{4,}['"]?/gi, '$1***REDACTED***');
}

module.exports = {
  LIBRARIAN_ROOT,
  REVIEW_THRESHOLD,
  stageFile,
  stageNote,
  appendChatMessage,
  loadSession,
  getStatus,
  appendLog,
  redactSecrets,
};

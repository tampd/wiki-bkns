'use strict';

const path = require('path');
const fs = require('fs');

const RAW_WEB_DIR = path.resolve(__dirname, '../../raw/web');
const RAW_MANUAL_DIR = path.resolve(__dirname, '../../raw/manual');
const LOG_FILE = path.resolve(__dirname, '../../logs/web-uploads.jsonl');

/**
 * Scan a directory recursively and return file metadata
 */
function scanDir(dir, source) {
  const results = [];
  if (!fs.existsSync(dir)) return results;

  function walk(current) {
    const entries = fs.readdirSync(current, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (entry.isFile()) {
        // Skip metadata/log files
        if (entry.name.endsWith('.jsonl') || entry.name.startsWith('.')) continue;

        const stat = fs.statSync(full);
        const relativePath = path.relative(path.resolve(__dirname, '../../'), full);

        // Try to extract UUID from web uploads
        let id = '';
        if (source === 'web') {
          const match = entry.name.match(/^([0-9a-f-]{36})-/);
          if (match) id = match[1];
        }

        results.push({
          id: id || '',
          filename: source === 'web' ? entry.name.replace(/^[0-9a-f-]{36}-/, '') : entry.name,
          stored_name: entry.name,
          path: relativePath,
          size: stat.size,
          mtime: stat.mtime.toISOString(),
          source,
        });
      }
    }
  }

  walk(dir);
  return results;
}

/**
 * GET /api/files
 * Query: source=web|manual|all, page=1, limit=15
 */
function filesRoute(router) {
  router.get('/api/files', (req, res) => {
    try {
      const source = req.query.source || 'all';
      const page = parseInt(req.query.page) || 1;
      const limit = Math.min(parseInt(req.query.limit) || 15, 100);

      let files = [];

      if (source === 'web' || source === 'all') {
        files = files.concat(scanDir(RAW_WEB_DIR, 'web'));
      }

      if (source === 'manual' || source === 'all') {
        files = files.concat(scanDir(RAW_MANUAL_DIR, 'manual'));
      }

      // Enrich web files with upload metadata from log
      const uploadLog = loadUploadLog();
      files = files.map(f => {
        if (f.source === 'web' && f.id && uploadLog[f.id]) {
          return { ...f, uploaded_at: uploadLog[f.id].uploaded_at };
        }
        return { ...f, uploaded_at: f.mtime };
      });

      // Sort by date descending
      files.sort((a, b) => new Date(b.uploaded_at || b.mtime) - new Date(a.uploaded_at || a.mtime));

      const total = files.length;
      const start = (page - 1) * limit;
      const paged = files.slice(start, start + limit);

      res.json({
        files: paged,
        total,
        page,
        limit,
      });
    } catch (err) {
      console.error('[FILES] Error:', err);
      res.status(500).json({ error: 'Failed to list files' });
    }
  });

  // DELETE /api/files/:id
  router.delete('/api/files/:id', (req, res) => {
    try {
      const id = req.params.id;
      if (!id || id.length < 10) {
        return res.status(400).json({ error: 'Invalid file ID' });
      }

      // Find the file in raw/web/
      const files = scanDir(RAW_WEB_DIR, 'web');
      const file = files.find(f => f.id === id);

      if (!file) {
        return res.status(404).json({ error: 'File not found' });
      }

      const fullPath = path.resolve(__dirname, '../../', file.path);

      // Validate path is within raw/web/ (prevent path traversal)
      if (!fullPath.startsWith(RAW_WEB_DIR)) {
        return res.status(403).json({ error: 'Access denied' });
      }

      fs.unlinkSync(fullPath);

      // Log deletion
      const logEntry = JSON.stringify({
        action: 'delete',
        id,
        filename: file.stored_name,
        deleted_at: new Date().toISOString(),
        deleter: 'admin',
      }) + '\n';
      fs.appendFileSync(LOG_FILE, logEntry);

      res.json({ deleted: true, filename: file.stored_name });
    } catch (err) {
      console.error('[DELETE] Error:', err);
      res.status(500).json({ error: 'Delete failed' });
    }
  });
}

/**
 * Load upload log for metadata lookup
 */
function loadUploadLog() {
  const index = {};
  if (!fs.existsSync(LOG_FILE)) return index;

  try {
    const lines = fs.readFileSync(LOG_FILE, 'utf8').trim().split('\n');
    for (const line of lines) {
      if (!line) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.id && entry.action === 'upload') {
          index[entry.id] = entry;
        }
      } catch { /* skip malformed lines */ }
    }
  } catch { /* file doesn't exist or read error */ }

  return index;
}

module.exports = { filesRoute };

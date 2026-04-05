'use strict';

const path = require('path');
const fs = require('fs');

const WIKI_DIR = path.resolve(__dirname, '../../wiki/products');
const BACKUP_DIR = path.resolve(__dirname, '../../wiki/.drafts/backups');
const LOG_FILE = path.resolve(__dirname, '../../logs/wiki-edits.jsonl');

// Allowed categories (whitelist — prevent path traversal)
const CATEGORIES = [
  'hosting', 'vps', 'ssl', 'ten-mien',
  'email', 'server', 'software', 'other', 'uncategorized',
];

/**
 * Parse YAML frontmatter from markdown content.
 * Returns { frontmatter: {}, body: '...' }
 */
function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: content };

  const fm = {};
  for (const line of match[1].split('\n')) {
    const sep = line.indexOf(':');
    if (sep === -1) continue;
    const key = line.slice(0, sep).trim();
    const val = line.slice(sep + 1).trim().replace(/^['"]|['"]$/g, '');
    fm[key] = val;
  }
  return { frontmatter: fm, body: match[2] };
}

/**
 * GET /api/wiki
 * Returns list of all wiki pages with metadata
 */
function wikiRoute(router) {
  router.get('/api/wiki', (req, res) => {
    try {
      const pages = [];

      for (const cat of CATEGORIES) {
        const filepath = path.join(WIKI_DIR, cat, 'tong-quan.md');
        if (!fs.existsSync(filepath)) {
          pages.push({ category: cat, exists: false, title: cat });
          continue;
        }

        const content = fs.readFileSync(filepath, 'utf8');
        const stat = fs.statSync(filepath);
        const { frontmatter } = parseFrontmatter(content);

        pages.push({
          category: cat,
          exists: true,
          title: frontmatter.title || cat,
          review_state: frontmatter.review_state || 'unknown',
          sensitivity: frontmatter.sensitivity || '',
          updated: frontmatter.updated || stat.mtime.toISOString().slice(0, 10),
          size: stat.size,
          mtime: stat.mtime.toISOString(),
        });
      }

      res.json({ pages });
    } catch (err) {
      console.error('[WIKI LIST] Error:', err);
      res.status(500).json({ error: 'Failed to list wiki pages' });
    }
  });

  // ----------------------------------------------------------------
  // GET /api/wiki/:category
  // Returns full content + frontmatter of a wiki page
  // ----------------------------------------------------------------
  router.get('/api/wiki/:category', (req, res) => {
    try {
      const { category } = req.params;

      if (!CATEGORIES.includes(category)) {
        return res.status(404).json({ error: 'Category không tồn tại' });
      }

      const filepath = path.join(WIKI_DIR, category, 'tong-quan.md');

      if (!fs.existsSync(filepath)) {
        return res.status(404).json({ error: 'Wiki page chưa được compile' });
      }

      const content = fs.readFileSync(filepath, 'utf8');
      const stat = fs.statSync(filepath);
      const { frontmatter } = parseFrontmatter(content);

      res.json({
        category,
        content,
        frontmatter,
        size: stat.size,
        mtime: stat.mtime.toISOString(),
      });
    } catch (err) {
      console.error('[WIKI GET] Error:', err);
      res.status(500).json({ error: 'Failed to read wiki page' });
    }
  });

  // ----------------------------------------------------------------
  // PUT /api/wiki/:category
  // Saves updated content (with auto-backup)
  // ----------------------------------------------------------------
  router.put('/api/wiki/:category', (req, res) => {
    try {
      const { category } = req.params;
      const { content } = req.body;

      if (!CATEGORIES.includes(category)) {
        return res.status(404).json({ error: 'Category không tồn tại' });
      }

      if (typeof content !== 'string' || content.trim().length === 0) {
        return res.status(400).json({ error: 'Nội dung không được để trống' });
      }

      if (content.length > 500_000) {
        return res.status(400).json({ error: 'Nội dung quá lớn (tối đa 500KB)' });
      }

      const filepath = path.join(WIKI_DIR, category, 'tong-quan.md');

      // Ensure directory exists
      fs.mkdirSync(path.dirname(filepath), { recursive: true });

      // Auto-backup before overwrite
      if (fs.existsSync(filepath)) {
        fs.mkdirSync(BACKUP_DIR, { recursive: true });
        const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const backupPath = path.join(BACKUP_DIR, `${category}-${ts}.md`);
        fs.copyFileSync(filepath, backupPath);
      }

      // Write new content
      fs.writeFileSync(filepath, content, 'utf8');

      // Audit log
      const logEntry = JSON.stringify({
        action: 'wiki_edit',
        category,
        size: content.length,
        edited_at: new Date().toISOString(),
        editor: 'admin',
      }) + '\n';
      fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
      fs.appendFileSync(LOG_FILE, logEntry);

      const { frontmatter } = parseFrontmatter(content);
      res.json({
        saved: true,
        category,
        size: content.length,
        frontmatter,
        saved_at: new Date().toISOString(),
      });
    } catch (err) {
      console.error('[WIKI PUT] Error:', err);
      res.status(500).json({ error: 'Failed to save wiki page' });
    }
  });

  // ----------------------------------------------------------------
  // GET /api/wiki/:category/backups
  // List backup files for a category
  // ----------------------------------------------------------------
  router.get('/api/wiki/:category/backups', (req, res) => {
    try {
      const { category } = req.params;

      if (!CATEGORIES.includes(category)) {
        return res.status(404).json({ error: 'Category không tồn tại' });
      }

      const backups = [];
      if (fs.existsSync(BACKUP_DIR)) {
        const files = fs.readdirSync(BACKUP_DIR)
          .filter(f => f.startsWith(`${category}-`) && f.endsWith('.md'))
          .sort()
          .reverse()
          .slice(0, 20); // last 20 backups

        for (const f of files) {
          const stat = fs.statSync(path.join(BACKUP_DIR, f));
          backups.push({ filename: f, size: stat.size, mtime: stat.mtime.toISOString() });
        }
      }

      res.json({ category, backups });
    } catch (err) {
      console.error('[WIKI BACKUPS] Error:', err);
      res.status(500).json({ error: 'Failed to list backups' });
    }
  });
}

module.exports = { wikiRoute };

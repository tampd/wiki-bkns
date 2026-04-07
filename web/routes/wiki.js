'use strict';

const path = require('path');
const fs = require('fs');

const WIKI_DIR = path.resolve(__dirname, '../../wiki/products');
const BACKUP_DIR = path.resolve(__dirname, '../../wiki/.drafts/backups');
const LOG_FILE = path.resolve(__dirname, '../../logs/wiki-edits.jsonl');
const ASSETS_DIR = path.resolve(__dirname, '../../wiki/assets/images');

// Standard sub-pages in expected order
const STANDARD_PAGES = [
  'index', 'tong-quan', 'bang-gia', 'thong-so', 'tinh-nang',
  'chinh-sach', 'cau-hoi-thuong-gap', 'so-sanh', 'huong-dan'
];

const PAGE_LABELS = {
  'index': 'Trang chính',
  'tong-quan': 'Tổng quan',
  'bang-gia': 'Bảng giá',
  'thong-so': 'Thông số kỹ thuật',
  'tinh-nang': 'Tính năng',
  'chinh-sach': 'Chính sách',
  'cau-hoi-thuong-gap': 'Câu hỏi thường gặp',
  'so-sanh': 'So sánh',
  'huong-dan': 'Hướng dẫn sử dụng',
};

const CATEGORY_LABELS = {
  hosting: 'Hosting',
  vps: 'VPS',
  ssl: 'SSL',
  'ten-mien': 'Tên Miền',
  email: 'Email',
  server: 'Server',
  software: 'Software',
  other: 'Khác',
  uncategorized: 'Chưa phân loại',
};

/**
 *  Scan wiki/products/ and return all existing category names.
 */
function getCategories() {
  if (!fs.existsSync(WIKI_DIR)) return [];
  return fs.readdirSync(WIKI_DIR, { withFileTypes: true })
    .filter(e => e.isDirectory())
    .map(e => e.name)
    .filter(name => !name.startsWith('.'))
    .sort();
}

/**
 * Validate a name to prevent path traversal.
 */
function isValidName(name) {
  return /^[a-zA-Z0-9_-]+$/.test(name);
}

/**
 * Parse YAML frontmatter from markdown content.
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
 * Recursively list all .md files in a directory.
 */
function listMdFiles(dir, base = '') {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const rel = base ? `${base}/${entry.name}` : entry.name;
    if (entry.isDirectory()) {
      results.push(...listMdFiles(path.join(dir, entry.name), rel));
    } else if (entry.name.endsWith('.md')) {
      results.push(rel);
    }
  }
  return results;
}

/**
 * Build category tree structure with all pages.
 */
function buildCategoryTree(category) {
  const catDir = path.join(WIKI_DIR, category);
  if (!fs.existsSync(catDir)) return null;

  const allFiles = listMdFiles(catDir);
  const pages = [];
  const products = [];

  for (const file of allFiles) {
    const pageName = file.replace(/\.md$/, '');
    const filePath = path.join(catDir, file);
    const stat = fs.statSync(filePath);
    const content = fs.readFileSync(filePath, 'utf8');
    const { frontmatter } = parseFrontmatter(content);

    const pageInfo = {
      page: pageName,
      filename: file,
      label: PAGE_LABELS[pageName] || frontmatter.title || pageName,
      title: frontmatter.title || pageName,
      size: stat.size,
      mtime: stat.mtime.toISOString(),
      review_state: frontmatter.review_state || 'unknown',
    };

    if (file.startsWith('san-pham/')) {
      products.push(pageInfo);
    } else {
      pages.push(pageInfo);
    }
  }

  // Sort: standard pages first in order, then custom pages
  pages.sort((a, b) => {
    const ai = STANDARD_PAGES.indexOf(a.page);
    const bi = STANDARD_PAGES.indexOf(b.page);
    if (ai !== -1 && bi !== -1) return ai - bi;
    if (ai !== -1) return -1;
    if (bi !== -1) return 1;
    return a.page.localeCompare(b.page);
  });

  products.sort((a, b) => a.label.localeCompare(b.label));

  return {
    category,
    label: CATEGORY_LABELS[category] || category,
    pages,
    products,
    totalPages: pages.length + products.length,
  };
}

// ============================================================
// IN-MEMORY SEARCH INDEX
// ============================================================
let searchIndex = [];
let indexBuiltAt = null;

function buildSearchIndex() {
  searchIndex = [];
  const categories = getCategories();

  for (const cat of categories) {
    const catDir = path.join(WIKI_DIR, cat);
    const files = listMdFiles(catDir);

    for (const file of files) {
      try {
        const filePath = path.join(catDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        const { frontmatter, body } = parseFrontmatter(content);
        const pageName = file.replace(/\.md$/, '');

        searchIndex.push({
          category: cat,
          categoryLabel: CATEGORY_LABELS[cat] || cat,
          page: pageName,
          title: frontmatter.title || PAGE_LABELS[pageName] || pageName,
          content: body.toLowerCase(),
          rawContent: body,
          size: content.length,
        });
      } catch { /* skip bad files */ }
    }
  }

  indexBuiltAt = new Date().toISOString();
  console.log(`[SEARCH] Index built: ${searchIndex.length} pages indexed at ${indexBuiltAt}`);
}

function searchWiki(query, limit = 20) {
  if (!searchIndex.length) buildSearchIndex();

  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return [];

  const results = [];

  for (const entry of searchIndex) {
    let score = 0;
    let snippets = [];

    for (const term of terms) {
      // Title match (highest weight)
      if (entry.title.toLowerCase().includes(term)) score += 10;
      // Content match
      const idx = entry.content.indexOf(term);
      if (idx !== -1) {
        score += 1;
        // Count occurrences
        let count = 0;
        let pos = 0;
        while ((pos = entry.content.indexOf(term, pos)) !== -1) {
          count++;
          pos += term.length;
        }
        score += Math.min(count, 5); // Cap at 5 extra per term

        // Extract snippet
        const start = Math.max(0, idx - 60);
        const end = Math.min(entry.rawContent.length, idx + term.length + 60);
        let snippet = entry.rawContent.slice(start, end).replace(/\n/g, ' ').trim();
        if (start > 0) snippet = '...' + snippet;
        if (end < entry.rawContent.length) snippet += '...';
        snippets.push(snippet);
      }
    }

    if (score > 0) {
      results.push({
        category: entry.category,
        categoryLabel: entry.categoryLabel,
        page: entry.page,
        title: entry.title,
        score,
        snippet: snippets[0] || '',
      });
    }
  }

  results.sort((a, b) => b.score - a.score);
  return results.slice(0, limit);
}

// ============================================================
// ROUTES
// ============================================================
function wikiRoute(router) {

  // Build index on startup
  setTimeout(() => buildSearchIndex(), 2000);

  // ----------------------------------------------------------
  // GET /api/wiki — List all categories with page counts
  // ----------------------------------------------------------
  router.get('/api/wiki', (req, res) => {
    try {
      const categories = getCategories();
      const pages = categories.map(cat => {
        const catDir = path.join(WIKI_DIR, cat);
        const tqPath = path.join(catDir, 'tong-quan.md');
        const files = listMdFiles(catDir);

        let title = CATEGORY_LABELS[cat] || cat;
        let review_state = 'unknown';
        let updated = '';

        if (fs.existsSync(tqPath)) {
          const content = fs.readFileSync(tqPath, 'utf8');
          const { frontmatter } = parseFrontmatter(content);
          title = frontmatter.title || title;
          review_state = frontmatter.review_state || 'unknown';
          updated = frontmatter.updated || '';
        }

        return {
          category: cat,
          label: CATEGORY_LABELS[cat] || cat,
          title,
          review_state,
          updated,
          totalPages: files.length,
          exists: files.length > 0,
        };
      });

      res.json({ pages });
    } catch (err) {
      console.error('[WIKI LIST] Error:', err);
      res.status(500).json({ error: 'Failed to list wiki pages' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/tree — Full tree structure
  // ----------------------------------------------------------
  router.get('/api/wiki/tree', (req, res) => {
    try {
      const categories = getCategories();
      const tree = categories.map(cat => buildCategoryTree(cat)).filter(Boolean);
      res.json({ tree, total: tree.reduce((s, c) => s + c.totalPages, 0) });
    } catch (err) {
      console.error('[WIKI TREE] Error:', err);
      res.status(500).json({ error: 'Failed to build wiki tree' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/search?q=keyword
  // ----------------------------------------------------------
  router.get('/api/wiki/search', (req, res) => {
    try {
      const q = (req.query.q || '').trim();
      if (!q) return res.json({ results: [], query: '' });

      const limit = Math.min(parseInt(req.query.limit) || 20, 50);
      const results = searchWiki(q, limit);
      res.json({ results, query: q, total: results.length });
    } catch (err) {
      console.error('[WIKI SEARCH] Error:', err);
      res.status(500).json({ error: 'Search failed' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/changelog?limit=20
  // ----------------------------------------------------------
  router.get('/api/wiki/changelog', (req, res) => {
    try {
      const limit = Math.min(parseInt(req.query.limit) || 20, 100);
      const entries = [];

      // Read edit log
      if (fs.existsSync(LOG_FILE)) {
        const lines = fs.readFileSync(LOG_FILE, 'utf8').trim().split('\n').filter(Boolean);
        for (let i = lines.length - 1; i >= Math.max(0, lines.length - limit); i--) {
          try {
            entries.push(JSON.parse(lines[i]));
          } catch { /* skip bad lines */ }
        }
      }

      res.json({ entries, total: entries.length });
    } catch (err) {
      console.error('[WIKI CHANGELOG] Error:', err);
      res.status(500).json({ error: 'Failed to read changelog' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/export — Bulk export for AI consumers
  // ----------------------------------------------------------
  router.get('/api/wiki/export', (req, res) => {
    try {
      const categories = getCategories();
      const catFilter = req.query.category;
      const exportData = {
        exported_at: new Date().toISOString(),
        format: 'bkns-wiki-v1',
        categories: [],
        total_pages: 0,
        total_chars: 0,
      };

      const targetCats = catFilter ? categories.filter(c => c === catFilter) : categories;

      for (const cat of targetCats) {
        const catDir = path.join(WIKI_DIR, cat);
        const files = listMdFiles(catDir);
        const pages = [];

        for (const file of files) {
          try {
            const filePath = path.join(catDir, file);
            const content = fs.readFileSync(filePath, 'utf8');
            const { frontmatter, body } = parseFrontmatter(content);
            const pageName = file.replace(/\.md$/, '');

            pages.push({
              page: pageName,
              title: frontmatter.title || PAGE_LABELS[pageName] || pageName,
              frontmatter,
              content: body,
              chars: body.length,
            });

            exportData.total_chars += body.length;
          } catch { /* skip */ }
        }

        exportData.categories.push({
          name: cat,
          label: CATEGORY_LABELS[cat] || cat,
          pages,
        });
        exportData.total_pages += pages.length;
      }

      exportData.total_tokens_estimate = Math.round(exportData.total_chars / 4);
      res.json(exportData);
    } catch (err) {
      console.error('[WIKI EXPORT] Error:', err);
      res.status(500).json({ error: 'Export failed' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/:category/:page — Read any wiki page
  // ----------------------------------------------------------
  router.get('/api/wiki/:category/:page', (req, res) => {
    try {
      const { category } = req.params;
      let page = req.params.page;

      if (!isValidName(category)) {
        return res.status(400).json({ error: 'Tên category không hợp lệ' });
      }

      // Handle nested product pages: san-pham__product-name → san-pham/product-name
      const pagePath = page.replace(/__/g, '/');

      // Validate each segment
      for (const seg of pagePath.split('/')) {
        if (!isValidName(seg)) {
          return res.status(400).json({ error: 'Tên page không hợp lệ' });
        }
      }

      const filepath = path.join(WIKI_DIR, category, pagePath + '.md');

      if (!fs.existsSync(filepath)) {
        return res.status(404).json({ error: 'Page không tồn tại', category, page: pagePath });
      }

      const content = fs.readFileSync(filepath, 'utf8');
      const stat = fs.statSync(filepath);
      const { frontmatter, body } = parseFrontmatter(content);

      res.json({
        category,
        page: pagePath,
        label: PAGE_LABELS[pagePath] || frontmatter.title || pagePath,
        content,
        body,
        frontmatter,
        size: stat.size,
        mtime: stat.mtime.toISOString(),
      });
    } catch (err) {
      console.error('[WIKI GET PAGE] Error:', err);
      res.status(500).json({ error: 'Failed to read wiki page' });
    }
  });

  // ----------------------------------------------------------
  // PUT /api/wiki/:category/:page — Save any wiki page
  // ----------------------------------------------------------
  router.put('/api/wiki/:category/:page', (req, res) => {
    try {
      const { category } = req.params;
      const page = req.params.page;
      const { content } = req.body;

      if (!isValidName(category)) {
        return res.status(400).json({ error: 'Tên category không hợp lệ' });
      }

      const pagePath = page.replace(/__/g, '/');
      for (const seg of pagePath.split('/')) {
        if (!isValidName(seg)) {
          return res.status(400).json({ error: 'Tên page không hợp lệ' });
        }
      }

      if (typeof content !== 'string' || content.trim().length === 0) {
        return res.status(400).json({ error: 'Nội dung không được để trống' });
      }

      if (content.length > 500_000) {
        return res.status(400).json({ error: 'Nội dung quá lớn (tối đa 500KB)' });
      }

      const filepath = path.join(WIKI_DIR, category, pagePath + '.md');
      fs.mkdirSync(path.dirname(filepath), { recursive: true });

      // Auto-backup before overwrite
      if (fs.existsSync(filepath)) {
        fs.mkdirSync(BACKUP_DIR, { recursive: true });
        const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const safeName = `${category}--${pagePath.replace(/\//g, '--')}--${ts}.md`;
        fs.copyFileSync(filepath, path.join(BACKUP_DIR, safeName));
      }

      // Write
      fs.writeFileSync(filepath, content, 'utf8');

      // Audit log
      const logEntry = JSON.stringify({
        action: 'wiki_edit',
        category,
        page: pagePath,
        size: content.length,
        edited_at: new Date().toISOString(),
        editor: 'admin',
      }) + '\n';
      fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
      fs.appendFileSync(LOG_FILE, logEntry);

      // Rebuild search index (async)
      setTimeout(() => buildSearchIndex(), 500);

      const { frontmatter } = parseFrontmatter(content);
      res.json({
        saved: true,
        category,
        page: pagePath,
        size: content.length,
        frontmatter,
        saved_at: new Date().toISOString(),
      });
    } catch (err) {
      console.error('[WIKI PUT] Error:', err);
      res.status(500).json({ error: 'Failed to save wiki page' });
    }
  });

  // ----------------------------------------------------------
  // POST /api/wiki/:category/:page — Create new page
  // ----------------------------------------------------------
  router.post('/api/wiki/:category/:page', (req, res) => {
    try {
      const { category } = req.params;
      const page = req.params.page;
      const { title, template } = req.body;

      if (!isValidName(category)) {
        return res.status(400).json({ error: 'Tên category không hợp lệ' });
      }

      const pagePath = page.replace(/__/g, '/');
      for (const seg of pagePath.split('/')) {
        if (!isValidName(seg)) {
          return res.status(400).json({ error: 'Tên page không hợp lệ' });
        }
      }

      const filepath = path.join(WIKI_DIR, category, pagePath + '.md');

      if (fs.existsSync(filepath)) {
        return res.status(409).json({ error: 'Page đã tồn tại' });
      }

      // Generate template content
      const pageTitle = title || pagePath.split('/').pop().replace(/-/g, ' ');
      const now = new Date().toISOString().slice(0, 10);
      let content = '';

      if (template === 'product') {
        content = `---
title: "${pageTitle}"
category: "${category}"
type: "product"
created: "${now}"
updated: "${now}"
review_state: "pending"
---

# ${pageTitle}

## Giới thiệu

_Mô tả sản phẩm ở đây._

## Thông số kỹ thuật

| Thông số | Chi tiết |
|----------|----------|
| — | — |

## Bảng giá

| Gói | Giá | Chu kỳ |
|-----|-----|--------|
| — | — | — |

## Câu hỏi thường gặp

**Q: Câu hỏi?**
A: Trả lời.
`;
      } else {
        content = `---
title: "${pageTitle}"
category: "${category}"
created: "${now}"
updated: "${now}"
review_state: "pending"
---

# ${pageTitle}

_Nội dung trang wiki ở đây._
`;
      }

      fs.mkdirSync(path.dirname(filepath), { recursive: true });
      fs.writeFileSync(filepath, content, 'utf8');

      // Audit log
      const logEntry = JSON.stringify({
        action: 'wiki_create',
        category,
        page: pagePath,
        title: pageTitle,
        created_at: new Date().toISOString(),
        editor: 'admin',
      }) + '\n';
      fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
      fs.appendFileSync(LOG_FILE, logEntry);

      // Rebuild search index
      setTimeout(() => buildSearchIndex(), 500);

      res.json({
        created: true,
        category,
        page: pagePath,
        title: pageTitle,
        path: filepath,
      });
    } catch (err) {
      console.error('[WIKI CREATE] Error:', err);
      res.status(500).json({ error: 'Failed to create page' });
    }
  });

  // ----------------------------------------------------------
  // GET /api/wiki/:category/:page/backups
  // ----------------------------------------------------------
  router.get('/api/wiki/:category/:page/backups', (req, res) => {
    try {
      const { category, page } = req.params;
      const pagePath = page.replace(/__/g, '/');
      const prefix = `${category}--${pagePath.replace(/\//g, '--')}--`;

      const backups = [];
      if (fs.existsSync(BACKUP_DIR)) {
        // Also check old-format backups (category-timestamp.md for tong-quan)
        const oldPrefix = `${category}-`;
        const files = fs.readdirSync(BACKUP_DIR)
          .filter(f => (f.startsWith(prefix) || (pagePath === 'tong-quan' && f.startsWith(oldPrefix) && !f.includes('--'))) && f.endsWith('.md'))
          .sort()
          .reverse()
          .slice(0, 20);

        for (const f of files) {
          const stat = fs.statSync(path.join(BACKUP_DIR, f));
          backups.push({ filename: f, size: stat.size, mtime: stat.mtime.toISOString() });
        }
      }

      res.json({ category, page: pagePath, backups });
    } catch (err) {
      console.error('[WIKI BACKUPS] Error:', err);
      res.status(500).json({ error: 'Failed to list backups' });
    }
  });

  // ----------------------------------------------------------
  // POST /api/upload/image — Image upload for editor
  // ----------------------------------------------------------
  router.post('/api/upload/image', (req, res) => {
    // This is handled via multer in server.js
    // Placeholder for route registration
  });
}

module.exports = { wikiRoute };

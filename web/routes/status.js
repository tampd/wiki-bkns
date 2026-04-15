'use strict';

const path = require('path');
const fs = require('fs');

const WIKI_PRODUCTS_DIR = path.resolve(__dirname, '../../wiki/products');
const CLAIMS_DIR = path.resolve(__dirname, '../../claims');
const RAW_WEB_DIR = path.resolve(__dirname, '../../raw/web');
const RAW_MANUAL_DIR = path.resolve(__dirname, '../../raw/manual');
const BUILD_DIR = path.resolve(__dirname, '../../build');

/**
 * Count files in a directory recursively
 */
function countFiles(dir) {
  if (!fs.existsSync(dir)) return 0;
  let count = 0;
  function walk(current) {
    try {
      const entries = fs.readdirSync(current, { withFileTypes: true });
      for (const entry of entries) {
        const full = path.join(current, entry.name);
        if (entry.isDirectory()) walk(full);
        else if (entry.isFile() && !entry.name.startsWith('.') && !entry.name.endsWith('.jsonl')) {
          count++;
        }
      }
    } catch { /* permission error or dir removed */ }
  }
  walk(dir);
  return count;
}

/**
 * GET /api/status
 */
function statusRoute(router) {
  router.get('/api/status', (req, res) => {
    try {
      // Count files
      const webFiles = countFiles(RAW_WEB_DIR);
      const manualFiles = countFiles(RAW_MANUAL_DIR);
      const claims = countFiles(CLAIMS_DIR);

      // Count wiki categories + total pages
      let wikiCategories = 0;
      let wikiTotalPages = 0;
      if (fs.existsSync(WIKI_PRODUCTS_DIR)) {
        const catDirs = fs.readdirSync(WIKI_PRODUCTS_DIR, { withFileTypes: true })
          .filter(e => e.isDirectory() && !e.name.startsWith('.'));
        wikiCategories = catDirs.filter(e =>
          fs.existsSync(path.join(WIKI_PRODUCTS_DIR, e.name, 'tong-quan.md'))
        ).length;
        // Count all .md files recursively
        const countMd = (dir) => {
          let n = 0;
          try {
            for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
              if (entry.isDirectory()) n += countMd(path.join(dir, entry.name));
              else if (entry.name.endsWith('.md')) n++;
            }
          } catch { /* skip */ }
          return n;
        };
        wikiTotalPages = countMd(WIKI_PRODUCTS_DIR);
      }

      // Build version
      let buildVersion = '—';
      if (fs.existsSync(BUILD_DIR)) {
        try {
          const buildDirs = fs.readdirSync(BUILD_DIR, { withFileTypes: true })
            .filter(e => e.isDirectory())
            .map(e => e.name)
            .sort()
            .reverse();
          if (buildDirs.length > 0) buildVersion = buildDirs[0];
        } catch { /* empty dir */ }
      }

      res.json({
        pipeline: 'disabled',
        last_run: null,
        last_result: 'Pipeline đã chuyển sang AI Thủ thư',
        build_version: buildVersion,
        wiki_stats: {
          total_files: webFiles + manualFiles,
          web_files: webFiles,
          manual_files: manualFiles,
          wiki_categories: wikiCategories,
          wiki_pages: wikiTotalPages,
          total_claims: claims,
          build_version: buildVersion,
        },
      });
    } catch (err) {
      console.error('[STATUS] Error:', err);
      res.status(500).json({ error: 'Status check failed' });
    }
  });
}

module.exports = { statusRoute };

'use strict';

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const MANIFESTS_DIR = path.resolve(__dirname, '../../build/manifests');

/**
 * Convert internal BLD-YYYYMMDD-HHMMSS → display BLD-DDMMYYYY HH:MM
 * e.g. BLD-20260404-181433 → "BLD-04042026 18:14"
 */
function toDisplayId(rawId) {
  const m = rawId.match(/BLD-(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})/);
  if (!m) return rawId;
  const [, y, mo, d, h, min] = m;
  return `BLD-${d}${mo}${y} ${h}:${min}`;
}

function buildsRoute(app) {

  // ── GET /api/builds — list all build versions ─────────────────
  app.get('/api/builds', (req, res) => {
    try {
      if (!fs.existsSync(MANIFESTS_DIR)) return res.json({ builds: [] });

      const files = fs.readdirSync(MANIFESTS_DIR)
        .filter(f => /^BLD-\d{8}-\d{6}\.(yaml|yml)$/.test(f))
        .sort()
        .reverse();

      const builds = files.map(f => {
        const id = f.replace(/\.(yaml|yml)$/, '');
        try {
          const data = yaml.load(fs.readFileSync(path.join(MANIFESTS_DIR, f), 'utf8'));
          return {
            id,
            display: toDisplayId(id),
            version: data.version || '—',
            wiki_files: data.wiki_files || 0,
            claims_count: data.claims_count || 0,
            wiki_token_estimate: data.wiki_token_estimate || 0,
            build_date: data.build_date || '',
            status: data.status || '',
          };
        } catch {
          return { id, display: toDisplayId(id), version: '—', wiki_files: 0, claims_count: 0, wiki_token_estimate: 0, build_date: '', status: '' };
        }
      });

      res.json({ builds, total: builds.length });
    } catch (err) {
      console.error('[BUILDS] List error:', err);
      res.status(500).json({ error: 'Failed to list builds' });
    }
  });

  // ── GET /api/builds/diff?v1=BLD-...&v2=BLD-... ────────────────
  app.get('/api/builds/diff', (req, res) => {
    try {
      const { v1, v2 } = req.query;
      if (!v1 || !v2) return res.status(400).json({ error: 'v1 và v2 bắt buộc' });

      // Prevent path traversal
      if (!/^BLD-[\d-]+$/.test(v1) || !/^BLD-[\d-]+$/.test(v2)) {
        return res.status(400).json({ error: 'Build ID không hợp lệ' });
      }

      const load = (id) => {
        const p = path.join(MANIFESTS_DIR, `${id}.yaml`);
        if (!fs.existsSync(p)) return null;
        try { return yaml.load(fs.readFileSync(p, 'utf8')); } catch { return null; }
      };

      const b1 = load(v1);
      const b2 = load(v2);

      if (!b1) return res.status(404).json({ error: `Không tìm thấy build ${toDisplayId(v1)}` });
      if (!b2) return res.status(404).json({ error: `Không tìm thấy build ${toDisplayId(v2)}` });

      const delta = (a, b) => (Number(b) || 0) - (Number(a) || 0);
      const fmtDelta = (n) => n > 0 ? `+${n}` : String(n);

      res.json({
        base: {
          id: v1,
          display: toDisplayId(v1),
          version: b1.version || '—',
          wiki_files: b1.wiki_files || 0,
          claims_count: b1.claims_count || 0,
          wiki_token_estimate: b1.wiki_token_estimate || 0,
          build_date: b1.build_date || '',
          status: b1.status || '',
        },
        compare: {
          id: v2,
          display: toDisplayId(v2),
          version: b2.version || '—',
          wiki_files: b2.wiki_files || 0,
          claims_count: b2.claims_count || 0,
          wiki_token_estimate: b2.wiki_token_estimate || 0,
          build_date: b2.build_date || '',
          status: b2.status || '',
        },
        changes: {
          wiki_files: {
            before: b1.wiki_files || 0,
            after: b2.wiki_files || 0,
            delta: delta(b1.wiki_files, b2.wiki_files),
            delta_str: fmtDelta(delta(b1.wiki_files, b2.wiki_files)),
          },
          claims_count: {
            before: b1.claims_count || 0,
            after: b2.claims_count || 0,
            delta: delta(b1.claims_count, b2.claims_count),
            delta_str: fmtDelta(delta(b1.claims_count, b2.claims_count)),
          },
          wiki_token_estimate: {
            before: b1.wiki_token_estimate || 0,
            after: b2.wiki_token_estimate || 0,
            delta: delta(b1.wiki_token_estimate, b2.wiki_token_estimate),
            delta_str: fmtDelta(delta(b1.wiki_token_estimate, b2.wiki_token_estimate)),
          },
        },
        same_version: b1.version === b2.version && b1.wiki_files === b2.wiki_files && b1.claims_count === b2.claims_count,
      });
    } catch (err) {
      console.error('[BUILDS] Diff error:', err);
      res.status(500).json({ error: 'Failed to compute build diff' });
    }
  });
}

module.exports = { buildsRoute, toDisplayId };

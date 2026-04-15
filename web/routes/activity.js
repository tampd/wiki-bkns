'use strict';

const fs = require('fs');
const path = require('path');

const LOGS_DIR = path.resolve(__dirname, '../../logs');

/**
 * Read last N lines from a JSONL file and parse them.
 */
function readJsonlTail(filepath, n) {
  if (!fs.existsSync(filepath)) return [];
  try {
    const lines = fs.readFileSync(filepath, 'utf8').trim().split('\n').filter(Boolean);
    return lines.slice(-n).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function activityRoute(app) {

  // ── GET /api/activity?limit=50 — Unified activity timeline ────
  app.get('/api/activity', (req, res) => {
    try {
      const limit = Math.min(parseInt(req.query.limit) || 50, 200);
      const events = [];

      // ── 1. Wiki edits & creates ──────────────────────────────
      readJsonlTail(path.join(LOGS_DIR, 'wiki-edits.jsonl'), 50).forEach(e => {
        const isCreate = e.action === 'wiki_create';
        events.push({
          type: isCreate ? 'create' : 'edit',
          icon: isCreate ? 'plus-circle' : 'pencil',
          label: isCreate ? 'Tạo trang mới' : 'Chỉnh sửa trang',
          detail: `${e.category || '—'}/${e.page || 'tong-quan'}`,
          ts: e.edited_at || e.created_at,
        });
      });

      // ── 2. Pipeline runs (only finished events) ──────────────
      readJsonlTail(path.join(LOGS_DIR, 'pipeline-runs.jsonl'), 40).forEach(e => {
        if (e.status !== 'success' && e.status !== 'failed') return;
        const actionLabels = {
          full: 'Full Pipeline',
          extract: 'Extract Claims',
          compile: 'Compile Wiki',
          snapshot: 'Build Snapshot',
        };
        const isOk = e.status === 'success';
        events.push({
          type: 'pipeline',
          icon: isOk ? 'check-circle' : 'alert-circle',
          label: `${actionLabels[e.action] || e.action || 'Pipeline'} — ${isOk ? 'Thành công' : 'Thất bại'}`,
          detail: e.note || e.result || '',
          ts: e.timestamp,
          ok: isOk,
        });
      });

      // ── 3. File uploads ──────────────────────────────────────
      readJsonlTail(path.join(LOGS_DIR, 'web-uploads.jsonl'), 30).forEach(e => {
        if (e.action !== 'upload') return;
        events.push({
          type: 'upload',
          icon: 'upload-cloud',
          label: 'Upload file',
          detail: e.filename || '',
          ts: e.uploaded_at || e.timestamp,
        });
      });

      // ── 4. Claim review actions (recent approve logs) ────────
      const approveLogs = [];
      try {
        approveLogs.push(...fs.readdirSync(LOGS_DIR)
          .filter(f => f.startsWith('approve-') && f.endsWith('.jsonl'))
          .sort().reverse().slice(0, 3));
      } catch { /* empty */ }

      for (const af of approveLogs) {
        readJsonlTail(path.join(LOGS_DIR, af), 20).forEach(e => {
          const stateLabel = { approved: 'Đã duyệt', rejected: 'Từ chối', flagged: 'Đã flag' }[e.review_state] || 'Review';
          const icon = { approved: 'check', rejected: 'x-circle', flagged: 'flag' }[e.review_state] || 'shield-check';
          events.push({
            type: 'review',
            icon,
            label: `Claim ${stateLabel}`,
            detail: e.claim_id || e.entity_id || '',
            ts: e.reviewed_at || e.timestamp,
            ok: e.review_state === 'approved',
          });
        });
      }

      // ── 5. Build snapshots ───────────────────────────────────
      readJsonlTail(path.join(LOGS_DIR, 'build-snapshot-2026-04-04.jsonl'), 10).forEach(e => {
        if (e.action !== 'success') return;
        events.push({
          type: 'build',
          icon: 'package',
          label: 'Build Snapshot',
          detail: e.build_id || '',
          ts: e.ts || e.timestamp,
          ok: true,
        });
      });

      // Try latest build snapshot log
      try {
        const bsLogs = fs.readdirSync(LOGS_DIR)
          .filter(f => f.startsWith('build-snapshot-') && f.endsWith('.jsonl'))
          .sort().reverse();
        if (bsLogs.length > 0) {
          readJsonlTail(path.join(LOGS_DIR, bsLogs[0]), 5).forEach(e => {
            if ((e.action !== 'success' && e.skill !== 'build-snapshot') || events.some(x => x.detail === e.build_id)) return;
            if (e.build_id) {
              events.push({
                type: 'build',
                icon: 'package',
                label: 'Build Snapshot',
                detail: e.build_id,
                ts: e.ts || e.timestamp,
                ok: true,
              });
            }
          });
        }
      } catch { /* skip */ }

      // ── Sort by timestamp descending ─────────────────────────
      events.sort((a, b) => {
        const ta = a.ts ? new Date(a.ts).getTime() : 0;
        const tb = b.ts ? new Date(b.ts).getTime() : 0;
        return tb - ta;
      });

      // Deduplicate by (label + detail + rounded minute)
      const seen = new Set();
      const deduped = events.filter(e => {
        const minKey = e.ts
          ? new Date(e.ts).toISOString().slice(0, 16)
          : 'notime';
        const key = `${e.type}|${e.label}|${e.detail}|${minKey}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });

      res.json({ events: deduped.slice(0, limit), total: deduped.length });
    } catch (err) {
      console.error('[ACTIVITY] Error:', err);
      res.status(500).json({ error: 'Failed to load activity' });
    }
  });
}

module.exports = { activityRoute };

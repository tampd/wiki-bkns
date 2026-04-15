'use strict';

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CLAIMS_DIR = path.resolve(__dirname, '../../claims/approved');
const VERIFY_LOGS_DIR = path.resolve(__dirname, '../../logs/verify');
const LOGS_DIR = path.resolve(__dirname, '../../logs');
const DUAL_QUEUE_DIR = path.resolve(__dirname, '../../.review-queue');
const DUAL_QUEUE_RESOLVED_DIR = path.join(DUAL_QUEUE_DIR, 'resolved');

// ── Claim file index cache (perf: O(1) lookup vs O(n) scan) ──
let _claimIndex = null;
let _claimIndexBuiltAt = 0;
const CLAIM_INDEX_TTL_MS = 2 * 60 * 1000; // 2 minutes

function getClaimIndex() {
  const now = Date.now();
  if (_claimIndex && (now - _claimIndexBuiltAt) < CLAIM_INDEX_TTL_MS) return _claimIndex;
  _claimIndex = new Map();
  if (!fs.existsSync(CLAIMS_DIR)) return _claimIndex;
  const walk = (dir) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) { walk(fullPath); continue; }
      if (!entry.name.endsWith('.yaml') && !entry.name.endsWith('.yml')) continue;
      try {
        const content = fs.readFileSync(fullPath, 'utf-8');
        const claim = yaml.load(content);
        if (claim && claim.claim_id) _claimIndex.set(claim.claim_id, fullPath);
      } catch { /* skip */ }
    }
  };
  walk(CLAIMS_DIR);
  _claimIndexBuiltAt = now;
  console.log(`[REVIEW] Claim index built: ${_claimIndex.size} entries`);
  return _claimIndex;
}

function invalidateClaimIndex() { _claimIndex = null; }

/**
 * Review Queue API — Human-in-the-loop verification
 * 
 * Routes:
 *   GET  /api/review/queue     — Get claims needing review
 *   GET  /api/review/stats     — Get review stats  
 *   POST /api/review/approve   — Approve a claim
 *   POST /api/review/reject    — Reject a claim
 *   POST /api/review/flag      — Flag a claim for further review
 *   GET  /api/review/conflicts — Get detected conflicts
 */
function reviewRoute(app) {

  // ── Get review queue ──────────────────────────────────
  app.get('/api/review/queue', (req, res) => {
    try {
      const filter = req.query.filter || 'all'; // all, flagged, conflicts, unverified
      const category = req.query.category || '';
      const page = parseInt(req.query.page) || 1;
      const limit = parseInt(req.query.limit) || 50;

      const claims = loadAllClaims(category);
      
      let filtered;
      switch (filter) {
        case 'flagged':
          filtered = claims.filter(c => c.review_state === 'flagged');
          break;
        case 'conflicts':
          filtered = findConflicts(claims);
          break;
        case 'unverified':
          filtered = claims.filter(c =>
            c.confidence !== 'ground_truth' &&
            !c.verified_by_layer2
          );
          break;
        case 'image':
          filtered = claims.filter(c =>
            (c.source_ids || []).some(s => s.startsWith('IMG-'))
          );
          break;
        case 'approved':
          filtered = claims.filter(c => c.review_state === 'approved');
          break;
        case 'rejected':
          filtered = claims.filter(c => c.review_state === 'rejected');
          break;
        default:
          // 'all' = pending review items (exclude already approved/rejected)
          filtered = claims.filter(c =>
            !c.review_state || c.review_state === 'pending' || c.review_state === 'flagged'
          );
      }

      // Sort: flagged first, then by confidence (low → high)
      const confidenceOrder = { low: 0, medium: 1, high: 2, ground_truth: 3 };
      filtered.sort((a, b) => {
        if (a.review_state === 'flagged' && b.review_state !== 'flagged') return -1;
        if (b.review_state === 'flagged' && a.review_state !== 'flagged') return 1;
        return (confidenceOrder[a.confidence] || 0) - (confidenceOrder[b.confidence] || 0);
      });

      const total = filtered.length;
      const start = (page - 1) * limit;
      const items = filtered.slice(start, start + limit);

      res.json({
        items,
        total,
        page,
        pages: Math.ceil(total / limit),
        filter,
      });
    } catch (err) {
      console.error('[REVIEW] Queue error:', err);
      res.status(500).json({ error: 'Failed to load review queue' });
    }
  });

  // ── Review stats ──────────────────────────────────────
  app.get('/api/review/stats', (req, res) => {
    try {
      const claims = loadAllClaims();
      
      const stats = {
        total: claims.length,
        by_confidence: {},
        by_source: { excel: 0, image: 0, llm: 0 },
        by_state: { approved: 0, flagged: 0, pending: 0, rejected: 0 },
        by_category: {},
        conflicts: 0,
        ground_truth_ratio: 0,
      };

      for (const c of claims) {
        // Confidence
        const conf = c.confidence || 'unknown';
        stats.by_confidence[conf] = (stats.by_confidence[conf] || 0) + 1;

        // Source
        const sources = c.source_ids || [];
        if (sources.some(s => s.startsWith('EXCEL-'))) stats.by_source.excel++;
        else if (sources.some(s => s.startsWith('IMG-'))) stats.by_source.image++;
        else stats.by_source.llm++;

        // State
        const state = c.review_state || 'pending';
        stats.by_state[state] = (stats.by_state[state] || 0) + 1;

        // Category
        const cat = c._category || 'other';
        if (!stats.by_category[cat]) {
          stats.by_category[cat] = { total: 0, gt: 0, img: 0, flagged: 0 };
        }
        stats.by_category[cat].total++;
        if (c.confidence === 'ground_truth') stats.by_category[cat].gt++;
        if (sources.some(s => s.startsWith('IMG-'))) stats.by_category[cat].img++;
        if (c.review_state === 'flagged') stats.by_category[cat].flagged++;
      }

      stats.ground_truth_ratio = claims.length > 0 
        ? ((stats.by_confidence.ground_truth || 0) / claims.length * 100).toFixed(1)
        : '0';

      // Load latest verification data
      const verifyReport = loadLatestVerifyReport();
      if (verifyReport) {
        stats.conflicts = verifyReport.critical_count || 0;
        stats.last_verify = verifyReport.timestamp;
      }

      res.json(stats);
    } catch (err) {
      console.error('[REVIEW] Stats error:', err);
      res.status(500).json({ error: 'Failed to compute review stats' });
    }
  });

  // ── Approve a claim ───────────────────────────────────
  app.post('/api/review/approve', (req, res) => {
    try {
      const { claim_id, note } = req.body;
      if (!claim_id) return res.status(400).json({ error: 'claim_id required' });

      const result = updateClaimState(claim_id, 'approved', note);
      if (!result) return res.status(404).json({ error: 'Claim not found' });

      res.json({ success: true, claim_id, state: 'approved' });
    } catch (err) {
      console.error('[REVIEW] Approve error:', err);
      res.status(500).json({ error: 'Failed to approve claim' });
    }
  });

  // ── Reject a claim ───────────────────────────────────
  app.post('/api/review/reject', (req, res) => {
    try {
      const { claim_id, reason } = req.body;
      if (!claim_id) return res.status(400).json({ error: 'claim_id required' });

      const result = updateClaimState(claim_id, 'rejected', reason);
      if (!result) return res.status(404).json({ error: 'Claim not found' });

      res.json({ success: true, claim_id, state: 'rejected' });
    } catch (err) {
      console.error('[REVIEW] Reject error:', err);
      res.status(500).json({ error: 'Failed to reject claim' });
    }
  });

  // ── Flag a claim ─────────────────────────────────────
  app.post('/api/review/flag', (req, res) => {
    try {
      const { claim_id, reason } = req.body;
      if (!claim_id) return res.status(400).json({ error: 'claim_id required' });

      const result = updateClaimState(claim_id, 'flagged', reason);
      if (!result) return res.status(404).json({ error: 'Claim not found' });

      res.json({ success: true, claim_id, state: 'flagged' });
    } catch (err) {
      console.error('[REVIEW] Flag error:', err);
      res.status(500).json({ error: 'Failed to flag claim' });
    }
  });

  // ── Get conflicts (grouped diff view) ─────────────────
  app.get('/api/review/conflicts', (req, res) => {
    try {
      const claims = loadAllClaims();
      const conflicts = findConflicts(claims);

      // Group conflicts by entity_id + attribute
      const groupMap = {};
      for (const c of conflicts) {
        const key = `${c.entity_id}:${c.attribute}`;
        if (!groupMap[key]) groupMap[key] = [];
        groupMap[key].push(c);
      }

      // Convert to array format for easier frontend rendering
      const groups = Object.entries(groupMap).map(([key, claimsInGroup]) => {
        const [entityId, attribute] = key.split(':', 2);
        return {
          conflict_key: key,
          entity_id: entityId,
          attribute: attribute,
          entity_name: claimsInGroup[0]?.entity_name || entityId,
          values: claimsInGroup.map(c => ({
            claim_id: c.claim_id,
            value: c.value,
            confidence: c.confidence,
            source_url: c.source_url || '',
            extracted_at: c.extracted_at || '',
            review_state: c.review_state || 'pending',
          })),
        };
      });

      res.json({
        total: groups.length,
        groups,
      });
    } catch (err) {
      console.error('[REVIEW] Conflicts error:', err);
      res.status(500).json({ error: 'Failed to load conflicts' });
    }
  });

  // ── Bulk action on multiple claims ───────────────────────
  // Supports two modes:
  //   atomic=false (default) — continue on error, return failed list
  //   atomic=true             — any error rolls back all successful writes
  app.post('/api/review/bulk', (req, res) => {
    try {
      const { action, claim_ids, reason, atomic } = req.body;
      if (!action || !Array.isArray(claim_ids) || claim_ids.length === 0) {
        return res.status(400).json({ error: 'action và claim_ids bắt buộc' });
      }
      if (!['approve', 'reject', 'flag'].includes(action)) {
        return res.status(400).json({ error: 'action phải là approve | reject | flag' });
      }
      if (claim_ids.length > 300) {
        return res.status(400).json({ error: 'Tối đa 300 claims mỗi lần' });
      }

      const newState = action === 'approve' ? 'approved'
        : action === 'reject' ? 'rejected'
        : 'flagged';
      const atomicMode = atomic === true || atomic === 'true';

      const allClaims = loadAllClaims();
      const claimMap = new Map();
      for (const c of allClaims) {
        if (c.claim_id) claimMap.set(c.claim_id, c);
      }

      const success = [];
      const failed = [];
      // For atomic rollback: keep pre-mutation file bytes per written file
      const snapshots = new Map();
      let abortReason = null;

      for (const claimId of claim_ids) {
        if (typeof claimId !== 'string' || !claimId.trim()) { failed.push(claimId); continue; }
        const trimmedId = claimId.trim();
        const claim = claimMap.get(trimmedId);
        if (!claim || !claim._file) {
          failed.push(trimmedId);
          if (atomicMode) { abortReason = `claim_not_found:${trimmedId}`; break; }
          continue;
        }

        try {
          const before = fs.readFileSync(claim._file, 'utf-8');
          const data = yaml.load(before);

          data.review_state = newState;
          data.reviewed_at = new Date().toISOString();
          data.reviewed_by = 'admin';
          data.review_note = reason || `bulk_${action}`;

          if (atomicMode) snapshots.set(claim._file, before);

          fs.writeFileSync(claim._file, yaml.dump(data, {
            lineWidth: -1, sortKeys: false, noRefs: true,
          }), 'utf-8');

          logReviewAction(trimmedId, newState, reason || `bulk_${action}`);
          success.push(trimmedId);
        } catch (err) {
          console.error(`[REVIEW] Bulk update ${trimmedId} error:`, err);
          failed.push(trimmedId);
          if (atomicMode) { abortReason = `write_error:${trimmedId}:${err.message}`; break; }
        }
      }

      if (atomicMode && abortReason) {
        // Restore original bytes for everything we already wrote
        let rolledBack = 0;
        for (const [filePath, bytes] of snapshots.entries()) {
          try { fs.writeFileSync(filePath, bytes, 'utf-8'); rolledBack++; } catch {}
        }
        invalidateClaimIndex();
        return res.status(409).json({
          error: 'Bulk aborted (atomic mode)',
          abort_reason: abortReason,
          rolled_back: rolledBack,
          total: claim_ids.length,
          success_count: 0,
          failed_count: claim_ids.length,
          failed_ids: claim_ids,
        });
      }

      res.json({
        action,
        new_state: newState,
        atomic: atomicMode,
        total: claim_ids.length,
        success_count: success.length,
        failed_count: failed.length,
        failed_ids: failed,
      });
    } catch (err) {
      console.error('[REVIEW] Bulk error:', err);
      res.status(500).json({ error: 'Bulk action failed' });
    }
  });

  // ── Review audit trail for a single claim ──────────────
  // Reads logs/approve-YYYY-MM-DD.jsonl and returns chronological history.
  app.get('/api/review/audit', (req, res) => {
    try {
      const claimId = String(req.query.claim_id || '').trim();
      if (!claimId) return res.status(400).json({ error: 'claim_id required' });
      const days = Math.min(parseInt(req.query.days, 10) || 30, 365);

      const history = [];
      if (!fs.existsSync(LOGS_DIR)) return res.json({ claim_id: claimId, history });

      const logFiles = fs.readdirSync(LOGS_DIR)
        .filter(f => /^approve-\d{4}-\d{2}-\d{2}\.jsonl$/.test(f))
        .sort()
        .slice(-days);

      for (const f of logFiles) {
        const lines = fs.readFileSync(path.join(LOGS_DIR, f), 'utf-8').split('\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const entry = JSON.parse(line);
            if (entry.claim_id === claimId) history.push(entry);
          } catch {}
        }
      }

      history.sort((a, b) => String(a.reviewed_at).localeCompare(String(b.reviewed_at)));
      res.json({ claim_id: claimId, count: history.length, history });
    } catch (err) {
      console.error('[REVIEW] Audit error:', err);
      res.status(500).json({ error: 'Failed to load audit trail' });
    }
  });

  // ── Dual-Vote Queue: list pending items ───────────────
  app.get('/api/review/dual-queue', (req, res) => {
    try {
      if (!fs.existsSync(DUAL_QUEUE_DIR)) {
        return res.json({ items: [], total: 0 });
      }

      const files = fs.readdirSync(DUAL_QUEUE_DIR)
        .filter(f => f.endsWith('.json'))
        .sort()
        .reverse();

      const items = files.map(filename => {
        try {
          const content = fs.readFileSync(path.join(DUAL_QUEUE_DIR, filename), 'utf-8');
          const data = JSON.parse(content);
          return {
            id: filename.replace('.json', ''),
            filename,
            ts: data.ts,
            skill: data.skill,
            status: data.status,
            flag: data.flag,
            score: data.score,
            model_a: data.model_a,
            model_b: data.model_b,
            prompt_preview: (data.prompt_preview || '').slice(0, 120),
            decided: data.decided || false,
          };
        } catch (e) {
          return null;
        }
      }).filter(Boolean);

      res.json({ items, total: items.length });
    } catch (err) {
      console.error('[DUAL-QUEUE] List error:', err);
      res.status(500).json({ error: 'Failed to load dual queue' });
    }
  });

  // ── Dual-Vote Queue: get one item ─────────────────────
  app.get('/api/review/dual/:id', (req, res) => {
    try {
      const filename = path.basename(req.params.id) + '.json';
      const filePath = path.join(DUAL_QUEUE_DIR, filename);

      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Item not found' });
      }

      const content = fs.readFileSync(filePath, 'utf-8');
      res.json(JSON.parse(content));
    } catch (err) {
      console.error('[DUAL-QUEUE] Get error:', err);
      res.status(500).json({ error: 'Failed to load queue item' });
    }
  });

  // ── Dual-Vote Queue: record human decision ────────────
  app.post('/api/review/dual/:id/decide', (req, res) => {
    try {
      const { decision, note } = req.body;
      if (!['pick_a', 'pick_b', 'reject_both'].includes(decision)) {
        return res.status(400).json({ error: 'decision phải là pick_a | pick_b | reject_both' });
      }

      const filename = path.basename(req.params.id) + '.json';
      const filePath = path.join(DUAL_QUEUE_DIR, filename);

      if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'Item not found' });
      }

      const content = fs.readFileSync(filePath, 'utf-8');
      const data = JSON.parse(content);

      data.decided = true;
      data.decision = decision;
      data.decided_at = new Date().toISOString();
      data.decided_by = 'admin';
      if (note) data.decision_note = note;

      // Move to resolved/
      fs.mkdirSync(DUAL_QUEUE_RESOLVED_DIR, { recursive: true });
      fs.writeFileSync(
        path.join(DUAL_QUEUE_RESOLVED_DIR, filename),
        JSON.stringify(data, null, 2),
        'utf-8'
      );
      fs.unlinkSync(filePath);

      logDualDecision(req.params.id, decision, note, data);

      res.json({ success: true, id: req.params.id, decision });
    } catch (err) {
      console.error('[DUAL-QUEUE] Decide error:', err);
      res.status(500).json({ error: 'Failed to record decision' });
    }
  });

  // ── Promote approved claims → ground_truth ───────────
  app.post('/api/review/promote-groundtruth', (req, res) => {
    try {
      const { from_confidence = ['high'], dry_run = false } = req.body;
      const allowed = ['high', 'medium', 'low'];
      const sources = Array.isArray(from_confidence) ? from_confidence.filter(c => allowed.includes(c)) : [];
      if (sources.length === 0) {
        return res.status(400).json({ error: 'from_confidence phải là mảng chứa high | medium | low' });
      }

      const claims = loadAllClaims();
      const candidates = claims.filter(c =>
        c.review_state === 'approved' && sources.includes(c.confidence)
      );

      if (dry_run) {
        const preview = {};
        for (const c of candidates) {
          preview[c.confidence] = (preview[c.confidence] || 0) + 1;
        }
        return res.json({
          dry_run: true,
          total_candidates: candidates.length,
          breakdown: preview,
          message: `Dry run: ${candidates.length} claims sẽ được promote lên ground_truth`,
        });
      }

      const success = [];
      const failed = [];

      for (const claim of candidates) {
        if (!claim._file) { failed.push(claim.claim_id); continue; }
        try {
          const content = fs.readFileSync(claim._file, 'utf-8');
          const data = yaml.load(content);
          const prevConf = data.confidence;
          data.confidence = 'ground_truth';
          data.promoted_from = prevConf;
          data.promoted_at = new Date().toISOString();
          fs.writeFileSync(claim._file, yaml.dump(data, {
            lineWidth: -1, sortKeys: false, noRefs: true,
          }), 'utf-8');
          success.push(claim.claim_id);
        } catch (e) {
          console.error(`[PROMOTE] ${claim.claim_id}:`, e.message);
          failed.push(claim.claim_id);
        }
      }

      // Log the promotion batch
      try {
        fs.mkdirSync(LOGS_DIR, { recursive: true });
        const dateStr = new Date().toISOString().slice(0, 10);
        const logFile = `${LOGS_DIR}/promote-groundtruth-${dateStr}.jsonl`;
        fs.appendFileSync(logFile, JSON.stringify({
          ts: new Date().toISOString(),
          from_confidence: sources,
          total: candidates.length,
          promoted: success.length,
          failed: failed.length,
        }) + '\n', 'utf-8');
      } catch (_) {}

      res.json({
        promoted: success.length,
        failed: failed.length,
        failed_ids: failed.slice(0, 20),
        message: `Đã promote ${success.length} claims lên ground_truth`,
      });
    } catch (err) {
      console.error('[PROMOTE] Error:', err);
      res.status(500).json({ error: 'Promote failed' });
    }
  });

  // ── Resolve conflict: pick winner, reject losers ───────
  app.post('/api/review/resolve-conflict', (req, res) => {
    try {
      const { winner_claim_id, loser_claim_ids } = req.body;
      if (!winner_claim_id || !Array.isArray(loser_claim_ids)) {
        return res.status(400).json({ error: 'winner_claim_id and loser_claim_ids required' });
      }

      const allIds = [winner_claim_id, ...loser_claim_ids];
      const updated = [];
      const errors = [];

      for (const claimId of allIds) {
        const state = claimId === winner_claim_id ? 'approved' : 'rejected';
        const note = claimId === winner_claim_id
          ? 'conflict_resolved_winner'
          : 'conflict_resolved_loser';
        const result = updateClaimState(claimId, state, note);
        if (result) {
          updated.push({ claim_id: claimId, state });
        } else {
          errors.push(claimId);
        }
      }

      res.json({
        status: errors.length === 0 ? 'success' : 'partial',
        updated,
        errors,
        message: `Conflict resolved: ${winner_claim_id} wins, ${loser_claim_ids.length} rejected`,
      });
    } catch (err) {
      console.error('[REVIEW] Resolve conflict error:', err);
      res.status(500).json({ error: 'Failed to resolve conflict' });
    }
  });
}

// ── Helper Functions ──────────────────────────────────────

function loadAllClaims(categoryFilter = '') {
  const claims = [];
  
  if (!fs.existsSync(CLAIMS_DIR)) return claims;

  const walkDir = (dir, category) => {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walkDir(fullPath, category ? `${category}/${entry.name}` : entry.name);
      } else if (entry.name.endsWith('.yaml') || entry.name.endsWith('.yml')) {
        try {
          const content = fs.readFileSync(fullPath, 'utf-8');
          const claim = yaml.load(content);
          if (claim && claim.claim_id) {
            claim._file = fullPath;
            claim._category = category || '';
            
            if (categoryFilter && !claim._category.includes(categoryFilter)) continue;
            
            claims.push(claim);
          }
        } catch (e) {
          // Skip invalid YAML
        }
      }
    }
  };

  walkDir(CLAIMS_DIR, '');
  return claims;
}

function findConflicts(claims) {
  // Group by entity_id + attribute
  const groups = {};
  for (const c of claims) {
    const key = `${c.entity_id || ''}:${c.attribute || ''}`;
    if (!groups[key]) groups[key] = [];
    groups[key].push(c);
  }

  const conflicts = [];
  for (const [key, group] of Object.entries(groups)) {
    if (group.length < 2) continue;
    
    // Check if values differ
    const values = new Set(group.map(c => String(c.value)));
    if (values.size > 1) {
      for (const c of group) {
        c._conflict_key = key;
        c._conflict_count = group.length;
        conflicts.push(c);
      }
    }
  }

  return conflicts;
}

function updateClaimState(claimId, newState, note) {
  // Use direct file search instead of loading ALL claims
  const filePath = findClaimFile(claimId);
  if (!filePath) return null;

  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    const data = yaml.load(content);

    data.review_state = newState;
    data.reviewed_at = new Date().toISOString();
    data.reviewed_by = 'admin';
    if (note) data.review_note = note;

    fs.writeFileSync(filePath, yaml.dump(data, {
      lineWidth: -1,
      sortKeys: false,
      noRefs: true,
    }), 'utf-8');

    logReviewAction(claimId, newState, note);
    return data;
  } catch (err) {
    console.error(`[REVIEW] Update claim ${claimId} error:`, err);
    return null;
  }
}

function findClaimFile(claimId) {
  const index = getClaimIndex();
  const filePath = index.get(claimId);
  if (filePath && fs.existsSync(filePath)) return filePath;
  // Cache miss or file moved — invalidate and retry once
  if (filePath) {
    invalidateClaimIndex();
    const freshIndex = getClaimIndex();
    return freshIndex.get(claimId) || null;
  }
  return null;
}

/**
 * Append a review action to the daily approve JSONL log.
 */
function logReviewAction(claimId, newState, note) {
  try {
    fs.mkdirSync(LOGS_DIR, { recursive: true });
    const dateStr = new Date().toISOString().slice(0, 10);
    const logFile = path.join(LOGS_DIR, `approve-${dateStr}.jsonl`);
    const entry = JSON.stringify({
      claim_id: claimId,
      review_state: newState,
      review_note: note || '',
      reviewed_by: 'admin',
      reviewed_at: new Date().toISOString(),
    });
    fs.appendFileSync(logFile, entry + '\n', 'utf-8');
  } catch (err) {
    console.error('[REVIEW] Log error:', err);
  }
}

function loadLatestVerifyReport() {
  try {
    if (!fs.existsSync(VERIFY_LOGS_DIR)) return null;
    
    const files = fs.readdirSync(VERIFY_LOGS_DIR)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse();
    
    if (files.length === 0) return null;

    const content = fs.readFileSync(path.join(VERIFY_LOGS_DIR, files[0]), 'utf-8');
    return JSON.parse(content);
  } catch (e) {
    return null;
  }
}

function logDualDecision(id, decision, note, data) {
  try {
    fs.mkdirSync(LOGS_DIR, { recursive: true });
    const dateStr = new Date().toISOString().slice(0, 7);
    const logFile = path.join(LOGS_DIR, `dual-vote-decisions-${dateStr}.jsonl`);
    const entry = JSON.stringify({
      id,
      decision,
      note: note || '',
      decided_by: 'admin',
      decided_at: new Date().toISOString(),
      original_status: data.status,
      original_score: data.score,
      skill: data.skill,
    });
    fs.appendFileSync(logFile, entry + '\n', 'utf-8');
  } catch (err) {
    console.error('[DUAL-QUEUE] Log decision error:', err);
  }
}

module.exports = { reviewRoute };

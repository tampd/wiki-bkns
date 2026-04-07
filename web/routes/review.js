'use strict';

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const CLAIMS_DIR = path.resolve(__dirname, '../../claims/approved');
const VERIFY_LOGS_DIR = path.resolve(__dirname, '../../logs/verify');

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
        default:
          filtered = claims;
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
      res.status(500).json({ error: err.message });
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
      res.status(500).json({ error: err.message });
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
      res.status(500).json({ error: err.message });
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
      res.status(500).json({ error: err.message });
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
      res.status(500).json({ error: err.message });
    }
  });

  // ── Get conflicts ────────────────────────────────────
  app.get('/api/review/conflicts', (req, res) => {
    try {
      const claims = loadAllClaims();
      const conflicts = findConflicts(claims);

      // Group conflicts by entity
      const grouped = {};
      for (const c of conflicts) {
        const key = `${c.entity_id}:${c.attribute}`;
        if (!grouped[key]) grouped[key] = [];
        grouped[key].push(c);
      }

      res.json({
        total: Object.keys(grouped).length,
        groups: grouped,
      });
    } catch (err) {
      console.error('[REVIEW] Conflicts error:', err);
      res.status(500).json({ error: err.message });
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
  const claims = loadAllClaims();
  const claim = claims.find(c => c.claim_id === claimId);
  
  if (!claim || !claim._file) return null;

  try {
    const content = fs.readFileSync(claim._file, 'utf-8');
    const data = yaml.load(content);
    
    data.review_state = newState;
    data.reviewed_at = new Date().toISOString();
    data.reviewed_by = 'admin';
    if (note) data.review_note = note;

    fs.writeFileSync(claim._file, yaml.dump(data, {
      lineWidth: -1,
      sortKeys: false,
      noRefs: true,
    }), 'utf-8');

    return data;
  } catch (err) {
    console.error(`[REVIEW] Update claim ${claimId} error:`, err);
    return null;
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

module.exports = { reviewRoute };

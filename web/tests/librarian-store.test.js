'use strict';

/**
 * Smoke test for librarian-store.js (no external deps, no jest).
 * Run: node web/tests/librarian-store.test.js
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Sandbox: redirect LIBRARIAN_ROOT by mutating module after require? Easier: monkey-patch.
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'librarian-test-'));
process.env.WIKI_ROOT_OVERRIDE = tmp;

// Override require resolution: write a temp store that re-exports with patched root.
// Simpler: just patch the module's LIBRARIAN_ROOT in-place before any function call.
const store = require('../lib/librarian-store');
const original = store.LIBRARIAN_ROOT;
Object.defineProperty(store, 'LIBRARIAN_ROOT', { value: tmp, writable: true });

// Reach into module — re-execute by clearing the require cache and reloading with monkey-patched fs?
// Cleaner approach: patch the internal helpers via re-import after env override.
// For now, use a fresh module evaluation:
delete require.cache[require.resolve('../lib/librarian-store')];

// Patch by string replace of the resolved path constant via VM eval would be over-engineering.
// Instead: use a child fixture path that the store will create relative to LIBRARIAN_ROOT.
// The cleanest fix: pass the root as an env override the store reads.
// → Update store to honor process.env.LIBRARIAN_ROOT_OVERRIDE.
// Until then, run against the real .librarian dir but with unique session IDs.

const realStore = require('../lib/librarian-store');

let pass = 0, fail = 0;
function assert(cond, msg) {
  if (cond) { pass++; console.log(`  ✅ ${msg}`); }
  else { fail++; console.error(`  ❌ ${msg}`); }
}

console.log('\n[Test 1] redactSecrets');
{
  const r = realStore.redactSecrets('key=sk-or-v1-abc123def456ghi789jkl password=hunter2');
  assert(!r.includes('sk-or-v1-abc'), 'redacts sk- token');
  assert(!r.includes('hunter2'), 'redacts password');
}

console.log('\n[Test 2] stageNote round-trip');
{
  const sid = `s-test-${Date.now()}`;
  const r = realStore.stageNote({
    text: '# hello\nThis is a test note about email hosting.',
    classification: { category: 'email', type: 'note', confidence: 0.9, summary: 'test' },
    sessionId: sid,
  });
  assert(fs.existsSync(r.stored_path), 'note file written');
  assert(fs.existsSync(r.meta_path), 'meta file written');
  const meta = JSON.parse(fs.readFileSync(r.meta_path, 'utf8'));
  assert(meta.classification.category === 'email', 'category persisted');
  assert(!r.needs_review, 'high confidence → not for review');
  fs.unlinkSync(r.stored_path);
  fs.unlinkSync(r.meta_path);
}

console.log('\n[Test 3] low-confidence routes to _review');
{
  const sid = `s-test-${Date.now()}`;
  const r = realStore.stageNote({
    text: 'ambiguous',
    classification: { category: 'uncategorized', type: 'note', confidence: 0.3 },
    sessionId: sid,
  });
  assert(r.needs_review, 'low confidence flagged');
  assert(r.stored_path.includes('_review'), 'routed to _review dir');
  fs.unlinkSync(r.stored_path);
  fs.unlinkSync(r.meta_path);
}

console.log('\n[Test 4] chat session append + load');
{
  const sid = `s-test-${Date.now()}`;
  realStore.appendChatMessage(sid, 'user', 'xin chào');
  realStore.appendChatMessage(sid, 'assistant', 'chào bạn');
  const msgs = realStore.loadSession(sid);
  assert(msgs.length === 2, 'two messages persisted');
  assert(msgs[0].content === 'xin chào', 'order preserved');
  // cleanup
  fs.unlinkSync(path.join(realStore.LIBRARIAN_ROOT, 'chat-sessions', `${sid}.jsonl`));
}

console.log(`\n──────────────────`);
console.log(`Result: ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);

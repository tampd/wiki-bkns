'use strict';

/**
 * Gemini Bridge — spawns Python subprocess (tools/librarian_gemini.py)
 * Reuses lib/gemini.py for Vertex AI auth + cost tracking.
 */

const { spawn } = require('child_process');
const path = require('path');

const REPO_ROOT = path.resolve(__dirname, '../..');
const SCRIPT = path.join(REPO_ROOT, 'tools', 'librarian_gemini.py');
const PY = process.env.LIBRARIAN_PY || 'python3';
const DEFAULT_TIMEOUT_MS = 60_000;

function callBridge(mode, payload, timeoutMs = DEFAULT_TIMEOUT_MS) {
  return new Promise((resolve, reject) => {
    const child = spawn(PY, [SCRIPT, '--mode', mode], {
      cwd: REPO_ROOT,
      env: { ...process.env, PYTHONPATH: REPO_ROOT },
    });

    let stdout = '';
    let stderr = '';
    let killed = false;

    const timer = setTimeout(() => {
      killed = true;
      child.kill('SIGKILL');
    }, timeoutMs);

    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    child.on('error', (err) => {
      clearTimeout(timer);
      reject(new Error(`spawn ${PY} failed: ${err.message}`));
    });

    child.on('close', (code) => {
      clearTimeout(timer);
      if (killed) return reject(new Error(`gemini bridge timed out after ${timeoutMs}ms`));
      if (code !== 0) {
        return reject(new Error(`gemini bridge exit ${code}: ${stderr.slice(0, 500)}`));
      }
      try {
        const parsed = JSON.parse(stdout);
        if (parsed.ok === false) return reject(new Error(parsed.error || 'bridge returned ok=false'));
        resolve(parsed);
      } catch (e) {
        reject(new Error(`invalid JSON from bridge: ${e.message} | raw=${stdout.slice(0, 300)}`));
      }
    });

    try {
      child.stdin.write(JSON.stringify(payload));
      child.stdin.end();
    } catch (e) {
      reject(new Error(`stdin write failed: ${e.message}`));
    }
  });
}

const chat = (payload, timeoutMs) => callBridge('chat', payload, timeoutMs);
const classify = (payload, timeoutMs) => callBridge('classify', payload, timeoutMs);

module.exports = { chat, classify };

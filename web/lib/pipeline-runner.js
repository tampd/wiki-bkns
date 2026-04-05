'use strict';

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const PROJECT_ROOT = path.resolve(__dirname, '../../');
const LOG_FILE = path.resolve(PROJECT_ROOT, 'logs/pipeline-runs.jsonl');

class PipelineRunner {
  constructor() {
    this.status = 'idle'; // idle | running | success | failed
    this.lastRun = null;
    this.lastResult = null;
    this.currentProcess = null;
  }

  isRunning() {
    return this.status === 'running';
  }

  getState() {
    return {
      status: this.status,
      lastRun: this.lastRun,
      lastResult: this.lastResult,
    };
  }

  /**
   * Trigger pipeline action
   * @param {string} action - 'extract' | 'compile' | 'full'
   * @returns {string} job ID
   */
  async trigger(action) {
    if (this.isRunning()) {
      throw new Error('Pipeline đang chạy');
    }

    const jobId = uuidv4();
    this.status = 'running';
    this.lastRun = new Date().toISOString();

    // Log start
    this._log({ job_id: jobId, action, status: 'started', started_at: this.lastRun });

    // Build command based on action
    const commands = this._buildCommands(action);

    // Execute commands sequentially (fire and forget)
    this._executeSequential(commands, jobId, action).catch(err => {
      console.error(`[PIPELINE] Job ${jobId} failed:`, err.message);
    });

    return jobId;
  }

  _buildCommands(action) {
    const commands = [];

    // Script locations (relative to PROJECT_ROOT)
    const convertScript = path.join(PROJECT_ROOT, 'tools', 'convert_manual.py');
    const extractScript = path.join(PROJECT_ROOT, 'skills', 'extract-claims', 'scripts', 'extract.py');
    const compileScript = path.join(PROJECT_ROOT, 'skills', 'compile-wiki', 'scripts', 'compile.py');

    if (action === 'extract' || action === 'full') {
      if (fs.existsSync(convertScript)) {
        commands.push({
          name: 'convert',
          cmd: 'python3',
          args: [convertScript],
        });
      }
      if (fs.existsSync(extractScript)) {
        commands.push({
          name: 'extract',
          cmd: 'python3',
          args: [extractScript],
        });
      }
    }

    if (action === 'compile' || action === 'full') {
      if (fs.existsSync(compileScript)) {
        commands.push({
          name: 'compile',
          cmd: 'python3',
          args: [compileScript],
        });
      }
    }

    return commands;
  }

  async _executeSequential(commands, jobId, action) {
    try {
      if (commands.length === 0) {
        console.warn('[PIPELINE] No scripts found to execute. Marking as success.');
        this.status = 'success';
        this.lastResult = 'success (no scripts)';
        this._log({ job_id: jobId, action, status: 'success', note: 'no scripts found' });
        return;
      }

      for (const cmd of commands) {
        console.log(`[PIPELINE] Running: ${cmd.name} — ${cmd.cmd} ${cmd.args.join(' ')}`);
        await this._runCommand(cmd.cmd, cmd.args, cmd.name);
        console.log(`[PIPELINE] ${cmd.name} completed`);
      }

      this.status = 'success';
      this.lastResult = 'success';
      this._log({
        job_id: jobId, action, status: 'success',
        completed_at: new Date().toISOString(),
      });
    } catch (err) {
      this.status = 'failed';
      this.lastResult = `failed: ${err.message}`;
      this._log({
        job_id: jobId, action, status: 'failed',
        error: err.message,
        completed_at: new Date().toISOString(),
      });
    }
  }

  _runCommand(cmd, args, name) {
    return new Promise((resolve, reject) => {
      const proc = spawn(cmd, args, {
        cwd: PROJECT_ROOT,
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        stdio: ['ignore', 'pipe', 'pipe'],
      });

      this.currentProcess = proc;
      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
        // Keep only last 5000 chars
        if (stdout.length > 5000) stdout = stdout.slice(-5000);
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
        if (stderr.length > 5000) stderr = stderr.slice(-5000);
      });

      proc.on('close', (code) => {
        this.currentProcess = null;
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(`${name} exited with code ${code}: ${stderr.slice(0, 500)}`));
        }
      });

      proc.on('error', (err) => {
        this.currentProcess = null;
        reject(new Error(`${name} spawn error: ${err.message}`));
      });

      // Timeout after 10 minutes
      setTimeout(() => {
        if (proc.exitCode === null) {
          proc.kill('SIGTERM');
          reject(new Error(`${name} timed out after 10 minutes`));
        }
      }, 10 * 60 * 1000);
    });
  }

  _log(entry) {
    try {
      const logLine = JSON.stringify({ ...entry, timestamp: new Date().toISOString() }) + '\n';
      fs.appendFileSync(LOG_FILE, logLine);
    } catch (err) {
      console.error('[PIPELINE LOG] Write failed:', err.message);
    }
  }
}

module.exports = { PipelineRunner };

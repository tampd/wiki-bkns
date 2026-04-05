'use strict';

const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const RAW_WEB_DIR = path.resolve(__dirname, '../../raw/web');
const LOG_FILE = path.resolve(__dirname, '../../logs/web-uploads.jsonl');

// Allowed file extensions (whitelist)
const ALLOWED_EXTS = new Set(['.pdf', '.docx', '.xlsx', '.md', '.txt', '.png', '.jpg', '.jpeg']);
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const MAX_FILES = 10;

// Multer storage config
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const today = new Date().toISOString().slice(0, 10);
    const dir = path.join(RAW_WEB_DIR, today);
    fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: function (req, file, cb) {
    const id = uuidv4();
    const ext = path.extname(file.originalname).toLowerCase();
    // Sanitize: only keep alphanumeric, dash, underscore, dot
    const safeName = path.basename(file.originalname, ext)
      .replace(/[^a-zA-Z0-9_\-]/g, '_')
      .substring(0, 80);
    cb(null, `${id}-${safeName}${ext}`);
  }
});

// File filter
function fileFilter(req, file, cb) {
  const ext = path.extname(file.originalname).toLowerCase();
  if (!ALLOWED_EXTS.has(ext)) {
    return cb(new Error(`Định dạng ${ext} không được phép. Cho phép: ${[...ALLOWED_EXTS].join(', ')}`));
  }
  cb(null, true);
}

const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: MAX_FILES,
  }
});

/**
 * POST /api/upload
 * Body: multipart/form-data with 'files' field
 * Query/Body: trigger=true|false
 */
function uploadRoute(router, pipelineRunner) {
  router.post('/api/upload', upload.array('files', MAX_FILES), async (req, res) => {
    try {
      if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'Không có file nào được upload' });
      }

      const shouldTrigger = req.body.trigger === 'true';
      const uploaded = [];

      for (const file of req.files) {
        const entry = {
          id: path.basename(file.filename, path.extname(file.filename)).split('-')[0],
          filename: file.originalname,
          stored_name: file.filename,
          path: file.path,
          size: file.size,
          mime: file.mimetype,
          uploaded_at: new Date().toISOString(),
          source: 'web',
          pipeline_status: shouldTrigger ? 'queued' : 'pending',
        };

        uploaded.push(entry);

        // Audit log
        const logEntry = JSON.stringify({
          ...entry,
          action: 'upload',
          uploader: 'admin',
        }) + '\n';
        fs.appendFileSync(LOG_FILE, logEntry);
      }

      // Trigger pipeline if requested
      if (shouldTrigger && pipelineRunner) {
        // Fire and forget — don't block the response
        pipelineRunner.trigger('full').catch(err => {
          console.error('[PIPELINE] Auto-trigger failed:', err.message);
        });
      }

      res.json({
        uploaded: uploaded.map(u => ({
          id: u.id,
          filename: u.filename,
          size: u.size,
          uploaded_at: u.uploaded_at,
          pipeline_status: u.pipeline_status,
        })),
        trigger: shouldTrigger,
      });
    } catch (err) {
      console.error('[UPLOAD] Error:', err);
      res.status(500).json({ error: err.message || 'Upload failed' });
    }
  });

  // Multer error handling
  router.use((err, req, res, next) => {
    if (err instanceof multer.MulterError) {
      if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(413).json({ error: 'File quá lớn. Tối đa 50MB/file' });
      }
      if (err.code === 'LIMIT_FILE_COUNT') {
        return res.status(400).json({ error: 'Tối đa 10 file/lần upload' });
      }
      return res.status(400).json({ error: err.message });
    }
    if (err) {
      return res.status(400).json({ error: err.message });
    }
    next();
  });
}

module.exports = { uploadRoute };

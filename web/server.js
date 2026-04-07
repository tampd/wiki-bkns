'use strict';

require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const path = require('path');
const multer = require('multer');
const fs = require('fs');

const { authMiddleware, loginHandler } = require('./middleware/auth');
const { uploadRoute } = require('./routes/upload');
const { filesRoute } = require('./routes/files');
const { triggerRoute } = require('./routes/trigger');
const { statusRoute } = require('./routes/status');
const { wikiRoute } = require('./routes/wiki');
const { reviewRoute } = require('./routes/review');
const { PipelineRunner } = require('./lib/pipeline-runner');

// ============================================================
// SETUP
// ============================================================
const app = express();
const PORT = process.env.WEB_PORT || 3000;
const pipelineRunner = new PipelineRunner();

// Wiki assets directory
const WIKI_ASSETS_DIR = path.resolve(__dirname, '../wiki/assets/images');
fs.mkdirSync(WIKI_ASSETS_DIR, { recursive: true });

// Trust Nginx reverse proxy
app.set('trust proxy', 1);

// ============================================================
// SECURITY MIDDLEWARE
// ============================================================

// SEO blocking — noindex on ALL responses
app.use((req, res, next) => {
  res.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive, nosnippet');
  next();
});

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://unpkg.com", "https://uicdn.toast.com", "https://cdn.jsdelivr.net"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://unpkg.com", "https://uicdn.toast.com", "https://cdn.jsdelivr.net"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:", "blob:"],
      connectSrc: ["'self'"],
      workerSrc: ["'self'", "blob:"],
    },
  },
  strictTransportSecurity: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));

app.use(cors({
  origin: process.env.CORS_ORIGIN || false,
  credentials: false,
}));

// Rate limiting
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 200, // Increased for wiki browsing
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Quá nhiều request. Vui lòng thử lại sau.' },
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Quá nhiều lần đăng nhập thất bại. Thử lại sau 15 phút.' },
});

// ============================================================
// BODY PARSERS
// ============================================================
app.use(express.json({ limit: '2mb' }));
app.use(express.urlencoded({ extended: false, limit: '2mb' }));

// ============================================================
// STATIC FILES
// ============================================================
app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: '1h',
  etag: true,
}));

// Serve wiki assets (images uploaded via editor)
app.use('/wiki-assets', express.static(WIKI_ASSETS_DIR, {
  maxAge: '7d',
  etag: true,
}));

// ============================================================
// IMAGE UPLOAD (multer) for wiki editor
// ============================================================
const imageUpload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, WIKI_ASSETS_DIR),
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname).toLowerCase();
      const name = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}${ext}`;
      cb(null, name);
    },
  }),
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max per image
  fileFilter: (req, file, cb) => {
    const allowed = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'];
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, allowed.includes(ext));
  },
});

// ============================================================
// ROUTES
// ============================================================
// Login (no auth required)
app.post('/api/login', loginLimiter, loginHandler);

// Protected API routes
app.use('/api', apiLimiter, authMiddleware);

// Image upload route (needs auth)
app.post('/api/upload/image', authMiddleware, imageUpload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No image file provided' });
  }
  res.json({
    uploaded: true,
    url: `/wiki-assets/${req.file.filename}`,
    filename: req.file.filename,
    size: req.file.size,
  });
});

// Mount routes
uploadRoute(app, pipelineRunner);
filesRoute(app);
triggerRoute(app, pipelineRunner);
statusRoute(app, pipelineRunner);
wikiRoute(app);
reviewRoute(app);

// ============================================================
// FALLBACK — SPA
// ============================================================
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ============================================================
// ERROR HANDLER
// ============================================================
app.use((err, req, res, _next) => {
  console.error('[SERVER] Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// ============================================================
// START
// ============================================================
app.listen(PORT, '127.0.0.1', () => {
  console.log(`\n  📚 BKNS Wiki Admin Portal`);
  console.log(`  ─────────────────────────`);
  console.log(`  🌐 http://127.0.0.1:${PORT}`);
  console.log(`  📂 Wiki dir: ${path.resolve(__dirname, '../wiki/products')}`);
  console.log(`  🔐 Auth: Bearer token`);
  console.log(`  🤖 SEO: Blocked (internal only)`);
  console.log(`  ⏰ Started: ${new Date().toISOString()}\n`);
});

module.exports = app;

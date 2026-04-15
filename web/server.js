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
const { statusRoute } = require('./routes/status');
const { wikiRoute } = require('./routes/wiki');
const { reviewRoute } = require('./routes/review');
const { buildsRoute } = require('./routes/builds');
const { activityRoute } = require('./routes/activity');
const { librarianRoute } = require('./routes/librarian');

// ============================================================
// SETUP
// ============================================================
const app = express();
const PORT = process.env.WEB_PORT || 3000;

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
      // 'unsafe-inline' required: TOAST UI Editor injects inline styles at runtime
      // and cannot be replaced with nonces/hashes without patching the library.
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
  max: 500, // Increased for review + wiki browsing sessions
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
statusRoute(app);
wikiRoute(app);
reviewRoute(app);
buildsRoute(app);
activityRoute(app);
librarianRoute(app);

// ============================================================
// FALLBACK — SPA
// ============================================================
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ============================================================
// ERROR HANDLER
// ============================================================
const logDir = path.resolve(__dirname, '../logs');
app.use((err, req, res, _next) => {
  const today = new Date().toISOString().slice(0, 10);
  const entry = JSON.stringify({
    ts: new Date().toISOString(),
    method: req.method,
    url: req.url,
    error: err.message,
    stack: err.stack?.split('\n')[0],
  }) + '\n';
  try { fs.appendFileSync(`${logDir}/web-errors-${today}.jsonl`, entry); }
  catch (_) {}
  console.error('[SERVER] Error:', err.message);
  res.status(err.status || 500).json({ error: 'Internal server error' });
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

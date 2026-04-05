'use strict';

require('dotenv').config({ path: require('path').resolve(__dirname, '../.env') });

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const path = require('path');

const { authMiddleware, loginHandler } = require('./middleware/auth');
const { uploadRoute } = require('./routes/upload');
const { filesRoute } = require('./routes/files');
const { triggerRoute } = require('./routes/trigger');
const { statusRoute } = require('./routes/status');
const { wikiRoute } = require('./routes/wiki');
const { PipelineRunner } = require('./lib/pipeline-runner');

// ============================================================
// SETUP
// ============================================================
const app = express();
const PORT = process.env.WEB_PORT || 3000;
const pipelineRunner = new PipelineRunner();

// Trust Nginx reverse proxy (fixes X-Forwarded-For rate limit error)
app.set('trust proxy', 1);

// ============================================================
// SECURITY MIDDLEWARE
// ============================================================
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "https://unpkg.com"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://unpkg.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"],
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
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Quá nhiều request. Vui lòng thử lại sau.' },
});

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10, // 10 login attempts per 15 minutes
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Quá nhiều lần đăng nhập thất bại. Thử lại sau 15 phút.' },
});

// ============================================================
// BODY PARSERS
// ============================================================
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false, limit: '1mb' }));

// ============================================================
// STATIC FILES
// ============================================================
app.use(express.static(path.join(__dirname, 'public'), {
  maxAge: '1h',
  etag: true,
}));

// ============================================================
// ROUTES
// ============================================================
// Login (no auth required, rate limited)
app.post('/api/login', loginLimiter, loginHandler);

// Protected API routes
app.use('/api', apiLimiter, authMiddleware);

// Mount routes
uploadRoute(app, pipelineRunner);
filesRoute(app);
triggerRoute(app, pipelineRunner);
statusRoute(app, pipelineRunner);
wikiRoute(app);

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
  console.log(`\n  📡 BKNS Wiki Data Portal`);
  console.log(`  ─────────────────────────`);
  console.log(`  🌐 http://127.0.0.1:${PORT}`);
  console.log(`  📂 Upload dir: ${path.resolve(__dirname, '../raw/web')}`);
  console.log(`  🔐 Auth: Bearer token`);
  console.log(`  ⏰ Started: ${new Date().toISOString()}\n`);
});

module.exports = app;

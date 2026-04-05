'use strict';

const bcrypt = require('bcryptjs');

/**
 * Auth middleware — Bearer token validation
 * Token format: Bearer <ADMIN_TOKEN>
 */
function authMiddleware(req, res, next) {
  // Skip auth for login endpoint
  if (req.path === '/api/login') return next();

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token bắt buộc' });
  }

  const token = authHeader.slice(7);
  const expectedToken = process.env.ADMIN_TOKEN;

  if (!expectedToken) {
    console.error('[AUTH] ADMIN_TOKEN not configured in .env');
    return res.status(500).json({ error: 'Server configuration error' });
  }

  if (token !== expectedToken) {
    return res.status(401).json({ error: 'Token không hợp lệ' });
  }

  next();
}

/**
 * Login endpoint handler
 * Compares password against hashed ADMIN_PASSWORD in env
 */
async function loginHandler(req, res) {
  const { password } = req.body;
  if (!password) {
    return res.status(400).json({ error: 'Mật khẩu bắt buộc' });
  }

  const hashedPassword = process.env.ADMIN_PASSWORD_HASH;
  const plainPassword = process.env.ADMIN_PASSWORD;

  let valid = false;

  if (hashedPassword) {
    // Preferred: compare against bcrypt hash
    valid = await bcrypt.compare(password, hashedPassword);
  } else if (plainPassword) {
    // Fallback for MVP: plain text comparison
    valid = password === plainPassword;
  } else {
    console.error('[AUTH] Neither ADMIN_PASSWORD_HASH nor ADMIN_PASSWORD configured');
    return res.status(500).json({ error: 'Server configuration error' });
  }

  if (!valid) {
    return res.status(401).json({ error: 'Sai mật khẩu' });
  }

  // Return the admin token for subsequent API calls
  return res.json({ token: process.env.ADMIN_TOKEN });
}

/**
 * Hash a password (utility for setup)
 */
async function hashPassword(plain) {
  return bcrypt.hash(plain, 12);
}

module.exports = { authMiddleware, loginHandler, hashPassword };

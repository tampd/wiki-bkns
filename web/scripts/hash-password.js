#!/usr/bin/env node
'use strict';

/**
 * hash-password.js — Generate bcrypt hash for ADMIN_PASSWORD_HASH in .env
 *
 * Usage:
 *   node scripts/hash-password.js <plain-password>
 *   node scripts/hash-password.js                    # reads from stdin
 */

const bcrypt = require('bcryptjs');
const readline = require('readline');

async function main() {
  let plain = process.argv[2];

  if (!plain) {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    plain = await new Promise((resolve) => rl.question('Password: ', (answer) => { rl.close(); resolve(answer); }));
  }

  if (!plain || plain.length < 8) {
    console.error('Error: password must be at least 8 characters');
    process.exit(1);
  }

  const hash = await bcrypt.hash(plain, 12);
  console.log('\nADMIN_PASSWORD_HASH=' + hash);
  console.log('\nPaste the line above into your .env file, then remove ADMIN_PASSWORD.\n');
}

main().catch((err) => { console.error(err); process.exit(1); });

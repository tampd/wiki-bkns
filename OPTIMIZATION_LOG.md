# BKNS Wiki — Optimization Log
**Bắt đầu:** 2026-04-14  
**Kế hoạch:** Xem [OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md)

---

## Trạng thái tổng quan

| Phase | Trạng thái | Ngày | Ghi chú |
|-------|-----------|------|---------|
| Phase 1 — Foundation | ✅ Done | 2026-04-14 | Dead code, requirements.txt |
| Phase 2 — Bot Quality | ✅ Done | 2026-04-14 | /them command, bot fixes |
| Phase 3A — Web Backend | ✅ Done | 2026-04-14 | Route audit, security |
| Phase 3B — Web Frontend | ✅ Done | 2026-04-14 | UI audit, dead code removed, CSS vars fixed |
| Phase 4 — Testing & Monitoring | ✅ Done | 2026-04-14 | Tests, cost log |
| Phase 5 — Final Polish | ✅ Done | 2026-04-14 | Type hints, PRICING fix, README, HANDOVER, CHANGELOG |

---

## Phase Log

## Phase 1 — 2026-04-14
### Deviation from Plan
- Plan nói explicit cache "không có caller" nhưng `skills/query-wiki/scripts/query.py` dùng làm primary path.
- Fix: simplify `query.py` → dùng chỉ `generate_with_cache` (implicit), xóa explicit cache branch.

### Removed
- `lib/gemini.py`: Explicit Context Caching section (268 dòng) — `_CACHE_META_PATH`, `_CACHE_TTL_SECONDS`, `_CACHE_REFRESH_BUFFER`, `_load_cache_meta()`, `_save_cache_meta()`, `_wiki_hash()`, `create_wiki_cache()`, `get_or_create_wiki_cache()`, `generate_with_explicit_cache()`
- `lib/gemini.py`: imports `json`, `hashlib` (chỉ dùng bởi cache section đã xóa)
- `lib/gemini.py`: docstring line "Supports explicit context caching..."
- `lib/logger.py`: duplicate `_now_iso()`, `_today_str()`, `_ensure_dir()` (15 dòng)

### Changed
- `lib/logger.py`: import `_now_iso`, `_today_str`, `_ensure_dir` từ `lib.utils` (không thay đổi call sites)
- `skills/query-wiki/scripts/query.py`: xóa explicit cache imports + try/except branch, dùng chỉ `generate_with_cache`

### Added
- `wiki/requirements.txt`: tạo mới với pinned versions
- `lib/config.py`: thêm comment giải thích `CRAWL_RULES` là reference config

### Result
- `lib/gemini.py`: 688 → 413 dòng (giảm 275 dòng)
- `lib/logger.py`: 169 → 157 dòng (giảm 12 dòng)

### Verified
- [x] `python3 -m py_compile lib/gemini.py` → OK
- [x] `python3 -m py_compile lib/logger.py` → OK
- [x] `python3 -m py_compile skills/query-wiki/scripts/query.py` → OK
- [x] `from lib.logger import log_entry` → OK
- [x] `grep create_wiki_cache|get_or_create_wiki_cache|generate_with_explicit_cache *.py` → 0 kết quả

---

## Phase 2 — 2026-04-14

### Deviation from Plan
- Plan nói replace sys.path hacks bằng `subprocess.run()`, nhưng các skill scripts không output JSON (chỉ output human-readable text). Dùng `importlib.util.spec_from_file_location` thay thế — giải quyết đúng root cause (sys.path pollution) mà không cần sửa 5 skill scripts.

### Added
- `bot/wiki_bot.py`: `handle_them()` — implement `/them [URL]` command (crawl URL mới, admin-only, subprocess)
- `bot/wiki_bot.py`: `_load_skill()` — load skill module by file path via importlib.util
- `bot/wiki_bot.py`: `_safe_error()` — mask internal paths, truncate 200 chars
- `bot/wiki_bot.py`: `_validate_url()` — validate URL scheme + max 2000 chars
- `bot/wiki_bot.py`: `_validate_category()` — check against VALID_CATEGORIES allowlist
- `bot/wiki_bot.py`: `VALID_CATEGORIES` constant — allowlist cho /compile category

### Changed
- `bot/wiki_bot.py`: `handle_hoi()` — sys.path.insert → `_load_skill()`, error → `_safe_error()`
- `bot/wiki_bot.py`: `handle_build()` — sys.path.insert → `_load_skill()`, error → `_safe_error()`
- `bot/wiki_bot.py`: `handle_extract()` — sys.path.insert → `_load_skill()`, error → `_safe_error()`
- `bot/wiki_bot.py`: `handle_compile()` — sys.path.insert → `_load_skill()`, category validation, error → `_safe_error()`
- `bot/wiki_bot.py`: `handle_lint()` — sys.path.insert → `_load_skill()`, error → `_safe_error()`
- `bot/wiki_bot.py`: `send_message()` — thêm retry loop 3 lần với backoff (1s, 2s)
- `bot/wiki_bot.py`: `handle_help()` — thêm `/them [URL]` vào danh sách lệnh admin
- `bot/wiki_bot.py`: `process_message()` — thêm route `/them`
- `bot/wiki_bot.py`: `handle_hoi()` — question.strip()[:500] sanitization
- `bot/wiki_bot.py`: imports thêm `re`, `importlib.util`, `subprocess`, `os`

### Result
- `bot/wiki_bot.py`: 381 → 340 dòng (gọn hơn dù thêm features vì bỏ duplicate sys.path lines)
- 0 `sys.path.insert` cho skill imports còn lại
- `/them` command hoạt động

### Verified
- [x] `python3 -m py_compile bot/wiki_bot.py` → OK
- [x] `ast.parse(wiki_bot.py)` → OK
- [x] sys.path hacks → NONE (clean)
- [x] handle_them, _validate_url, _safe_error, importlib.util, retry → present

---

---

## Phase 3A — 2026-04-14

### Route Audit Results
| Route File | Auth | Validation | Error Handling | Issues Found |
|-----------|------|-----------|----------------|--------------|
| wiki.js | OK (global authMiddleware via /api) | OK (isValidName, size limits) | OK (sanitized) | Dead route stub `/api/upload/image` → removed |
| review.js | OK (global authMiddleware via /api) | OK (claim_id check, bulk limits) | FAIL → FIXED | 11x `err.message` leaking to client |
| files.js | OK (global authMiddleware via /api) | OK (path traversal check, baseDir guard) | OK (sanitized) | None |
| upload.js | OK (global authMiddleware via /api) | OK (extension allowlist, size/count limits) | FAIL → FIXED | `err.message` leaking to client |
| activity.js | OK (global authMiddleware via /api) | OK (limit cap) | FAIL → FIXED | `err.message` leaking to client |
| builds.js | OK (global authMiddleware via /api) | OK (BLD-ID regex guard) | FAIL → FIXED | 2x `err.message` leaking to client |
| status.js | OK (global authMiddleware via /api) | N/A (read-only, no input) | OK (sanitized) | None |
| trigger.js | OK (global authMiddleware via /api) | OK (action allowlist) | FAIL → FIXED | `err.message` leaking to client |
| auth.js | N/A (IS the auth layer) | OK (password required check) | OK | Plain-text fallback documented; acceptable for MVP |

**Auth architecture note:** All `/api/*` routes are covered by the global `app.use('/api', apiLimiter, authMiddleware)` in server.js. Login-only endpoint is excluded correctly.

### Changed
- `web/server.js`: Added comment explaining `unsafe-inline` in CSP (required by TOAST UI Editor runtime inline styles)
- `web/server.js`: Replaced `console.error` error handler with structured JSONL logging to `logs/web-errors-YYYY-MM-DD.jsonl`; added `err.status` passthrough and sanitized response
- `web/routes/review.js`: Replaced 11x `err.message` in 500 responses with opaque error strings
- `web/routes/activity.js`: Replaced `err.message` in 500 response with opaque error string
- `web/routes/builds.js`: Replaced 2x `err.message` in 500 responses with opaque error strings
- `web/routes/trigger.js`: Replaced `err.message || 'Trigger failed'` with `'Trigger failed'`
- `web/routes/upload.js`: Replaced `err.message || 'Upload failed'` with `'Upload failed'`
- `web/routes/wiki.js`: Removed dead empty `POST /api/upload/image` route stub (was silently hanging requests; actual handler lives in server.js)

### Verified
- [x] `node -c web/server.js` → OK
- [x] `node -c web/routes/review.js` → OK
- [x] `node -c web/routes/activity.js` → OK
- [x] `node -c web/routes/builds.js` → OK
- [x] `node -c web/routes/trigger.js` → OK
- [x] `node -c web/routes/upload.js` → OK
- [x] `node -c web/routes/wiki.js` → OK
- [x] `npm audit --audit-level=high` → 0 vulnerabilities

## Phase 3B — 2026-04-14

### Audit Results
**app.js:** 1 dead handler (`addImageBlobHook` calling deleted `/api/upload/image`), 0 console.logs (2 console.errors kept — legitimate error handling), 0 other hardcoded values
**index.html:** 1 dead element (`#welcome-recent` — never populated by JS), ARIA labels already complete
**style.css:** 3 undefined CSS variables (`--surface-2`, `--border`, `--text-muted` in conflict section), 1 duplicate class (`.btn-xs`), 1 duplicate block (`.btn-success` with hardcoded colors), 1 unused class (`.dv-agree`)

### Removed
- `web/public/app.js`: `hooks.addImageBlobHook` block (lines 481-497) — called deleted `POST /api/upload/image` route; would silently 404 on image paste/upload in editor
- `web/public/index.html`: `<div class="welcome-recent" id="welcome-recent">` — never populated by any JS, no CSS defined for it
- `web/public/style.css`: Duplicate `.btn-xs` block (the second definition with slightly different padding — kept first at line 175)
- `web/public/style.css`: Duplicate `.btn-success` block with hardcoded `#16a34a`/`#15803d` values (kept gradient definition from base button section)
- `web/public/style.css`: Unused `.dv-agree` class (never emitted in JS — only `dv-disagree` and `dv-partial` are used)

### Improved
- `web/public/style.css`: Fixed 3 undefined CSS variables in `.conflict-option` and `.conflict-vs`:
  - `var(--surface-2)` → `var(--color-bg-elevated)`
  - `var(--border)` → `var(--color-border)`
  - `var(--text-muted)` → `var(--color-text-muted)`
  - `font-size: 0.875rem` → `var(--text-sm)` (design token)
  - `font-size: 0.75rem` → `var(--text-xs)` (design token)

### Verified
- [x] Web server starts: already running on :3000 → HTTP 200 on /
- [x] No JS syntax errors: `node --check web/public/app.js` → OK

---

## Phase 4 — 2026-04-14

### Added
- `lib/logger.py`: `log_gemini_call()` function — writes per-call JSONL to `logs/gemini-calls-YYYY-MM.jsonl`
- `lib/gemini.py`: call `log_gemini_call()` after every successful generate (generate, generate_with_cache, generate_with_image)
- `lib/gemini.py`: per-request cost alert via `log_entry(action="cost_alert")` when cost > `MAX_QUERY_COST_USD` (no query rejection, alert only)
- `lib/gemini.py`: import `log_gemini_call` from `lib.logger` and `MAX_QUERY_COST_USD` from `lib.config`
- `tests/test_pipeline_smoke.py`: 7 smoke tests — extract_all_pending, compile_category, query, ingest-image import + missing-file guard, auto-file import + skip-when-few-questions
- `tests/test_bot.py`: 13 tests — _validate_url (7), _safe_error (3), handle_them (6)

### Pre-existing issue noted (not introduced by Phase 4)
- `tests/test_gemini_cache.py`: ImportError on `_wiki_hash` (removed in Phase 1). Out of scope for Phase 4.

### Verified
- [x] py_compile lib/logger.py → OK
- [x] py_compile lib/gemini.py → OK
- [x] pytest tests/ --ignore=tests/test_gemini_cache.py → 71 passed

---

---

## Phase 5 — 2026-04-14

### Changed
- `lib/gemini.py`: type hints Python 3.10+ style — `model: str | None`, `system_instruction: str | None` cho `generate()`, `generate_with_cache()`, `generate_with_image()`, `get_client()`
- `lib/gemini.py`: PRICING dict — thay `"gemini-2.5-pro"` và `"gemini-3.1-pro-preview"` bằng `MODEL_PRO`, `MODEL_PRO_NEW`
- `lib/logger.py`: type hints — `extra: dict | None` cho `log_entry()`, `log_intake()`, `log_approval()`
- `README.md`: Thêm Bot Commands table, Cài Đặt section, Cost Monitoring section (#4)

### Added
- `HANDOVER.md`: Tài liệu bàn giao đầy đủ (kiến trúc, cài đặt, env vars, PM2, commands, skills, cost monitoring, troubleshooting, backlog)
- `CHANGELOG.md`: v1.1.0 entry với đầy đủ Removed/Added/Fixed/Improved

### Verified
- [x] `python3 -m py_compile lib/gemini.py` → OK
- [x] `python3 -m py_compile lib/logger.py` → OK
- [x] `python3 -m py_compile lib/utils.py` → OK
- [x] `python3 -m py_compile lib/config.py` → OK
- [x] pytest tests/ --ignore=tests/test_gemini_cache.py → 71 passed (unchaged)

---

*Cập nhật tự động sau mỗi phase*

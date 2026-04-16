# CHANGELOG — BKNS Agent Wiki

All notable changes to this project are documented here.
Format: [Semantic Versioning](https://semver.org/) | dates in YYYY-MM-DD

---

## [v1.2.2] — 2026-04-16 — Fix: SSE Streaming for OpenClaw Responses API

### Fixed
- **incomplete turn detected: payloads=0**: OpenClaw dùng `openai-responses` transport với `stream: true`, nhưng proxy trả về plain JSON thay vì SSE streaming events
  → `vertex-proxy` v1.2.0 giờ convert non-streaming JSON response từ Vertex AI thành SSE events đúng format Responses API

### Root cause
- OpenClaw's `google-vertex` provider dùng `api: openai-responses` (mặc định) → gọi `client.responses.create(params, {stream: true})`
- Client này expect SSE events: `response.created`, `response.output_item.added`, `response.output_text.delta`, `response.output_item.done`, `response.completed`
- Proxy cũ trả về JSON object → OpenAI SDK không parse được → stream yield 0 events → `payloads=0`

### Solution
- Proxy nhận `/responses` với `stream: true` → forward `/chat/completions` với `stream: false` tới Vertex AI → convert JSON response thành SSE events → stream về OpenClaw

### Files Changed
- `tools/vertex-proxy.js` v1.1.0 → v1.2.0: replace `chatToResponsesResponse()` with `emitResponsesSSE()` (SSE writer)

---

## [v1.2.1] — 2026-04-16 — Fix: Responses API Conversion + stream:false

### Fixed
- **HTTP 400**: OpenClaw gọi `POST /responses` (OpenAI Responses API) nhưng Vertex AI chỉ hỗ trợ `POST /chat/completions`
  → `vertex-proxy` v1.1.0 tự động convert `/responses` ↔ `/chat/completions`
- **Missing content**: Vertex AI trả về response không có text khi thiếu `stream:false`
  → proxy inject `stream: false` vào mọi request
- **gemini-3.x không available**: Đã verify tất cả gemini-3.x đều 404 trên Vertex AI cho project `ai-test-491016`
  → Dùng `google/gemini-2.5-pro` (model mạnh nhất available, 1M context, reasoning)

### Documented
- Thêm vào Spec #17: 2 lỗi mới (Responses API + gemini-3.x) với nguyên nhân và cách tránh
- Ghi rõ: không assume Vertex AI hỗ trợ mọi endpoint OpenAI; phải test trực tiếp

---

## [v1.2.0] — 2026-04-16 — OpenClaw Telegram Integration + Gemini 2.5 Pro

### Added
- **OpenClaw v2026.4.14**: Installed as AI gateway platform for Telegram bot
- **Vertex Auth Proxy** (`tools/vertex-proxy.js`): Auto-refresh GCP access token proxy (port 19010)
- **PM2 config** (`ecosystem.openclaw.config.js`): 2 processes — `vertex-proxy` + `openclaw-gateway`
- **Spec** (`trienkhai/17-openclaw-telegram-integration.md`): Full architecture, security, troubleshooting docs

### Changed
- **AI Backend**: `openai/gpt-4o` → `google-vertex/gemini-2.5-pro` (1M context, reasoning mode)
- **Telegram Security**: `dmPolicy: open` → `dmPolicy: allowlist` (only owner ID 882968821)
- **Group Policy**: `disabled` — bot không tham gia group nào

### Fixed
- **HTTP 404**: Sai endpoint URL format (native API vs OpenAI-compatible) + model `gemini-3.1-pro-preview` chưa available
- **HTTP 401**: `gcp-vertex-credentials` không resolve ADC → tạo proxy xử lý auth riêng
- **Port conflict**: Gateway process cũ giữ port khi restart

### Security
- Allowlist chỉ cho Telegram ID `882968821` (@phamduytam)
- Group chat disabled hoàn toàn
- Proxy chỉ listen trên 127.0.0.1
- Gateway auth token-based

---

## [v1.1.1] — 2026-04-16 — Domain Migration & API Configuration

### Changed
- **Domain**: migrated from `upload.trieuphu.biz` → `wiki.bkns.vn` (SSL Let's Encrypt)
- **Server path**: `/home/openclaw/wiki` → `/wiki`
- **Nginx config**: replaced `nginx-upload.trieuphu.biz.conf` with `nginx-wiki.bkns.vn.conf`
- `ecosystem.config.js`, `web/ecosystem.web.config.js`: updated `cwd` and `PYTHONPATH` to `/wiki`
- `web/deploy-nginx.sh`: updated domain and config paths for `wiki.bkns.vn`
- `.env.example`: updated `WIKI_WORKSPACE=/wiki`
- `requirements.txt`: fixed `markitdown>=0.4.0` → `markitdown>=0.1.0` (version 0.4.0 not published)

### Added
- `.env`: configured OpenAI API key (`sk-proj-*`) and Google Vertex AI service account
- `service-account.json`: Google Cloud credentials for Vertex AI (gitignored)
- `.gitignore`: added `service-account.json` to prevent credential leak

### Fixed
- All docs (`README.md`, `HANDOVER.md`, `SPEC-wiki-system.md`): updated domain references, paths, test counts, process names
- `HANDOVER.md`: fixed `WIKI_WORKSPACE` → `WORKSPACE` (matching actual `lib/config.py` variable name)
- `HANDOVER.md`: fixed PM2 process name `wiki-admin` → `wiki-portal`
- `HANDOVER.md`: updated test count 33 → 38

---

## [v1.1.0] — 2026-04-14 — Optimization Release

### Removed
- `lib/gemini.py`: Explicit Context Caching (275 dòng dead code) — `_CACHE_META_PATH`, `create_wiki_cache()`, `generate_with_explicit_cache()`, v.v.
- `lib/logger.py`: Duplicate utility functions (12 dòng) — `_now_iso()`, `_today_str()`, `_ensure_dir()` (thay bằng import từ `lib.utils`)
- `web/routes/wiki.js`: Dead route `POST /api/upload/image` (stub rỗng, gây hanging requests)
- `web/public/app.js`: Dead `addImageBlobHook` handler (gọi route đã xóa)
- `web/public/index.html`: Dead `<div class="welcome-recent">` (không được JS populate)
- `web/public/style.css`: Duplicate `.btn-xs`, duplicate `.btn-success` hardcoded override, unused `.dv-agree`

### Added
- `bot/wiki_bot.py`: `/them [URL]` command — crawl URL mới vào raw/ (admin-only, subprocess, timeout 60s)
- `lib/logger.py`: `log_gemini_call()` — ghi per-call JSONL vào `logs/gemini-calls-YYYY-MM.jsonl`
- `web/server.js`: Structured error logging tới `logs/web-errors-YYYY-MM-DD.jsonl`
- `wiki/requirements.txt`: Python dependency management với pinned versions
- `tests/test_pipeline_smoke.py`: 7 pipeline smoke tests
- `tests/test_bot.py`: 13 bot unit tests (`_validate_url`, `_safe_error`, `handle_them`)
- `HANDOVER.md`: Tài liệu bàn giao đầy đủ

### Fixed
- `bot/wiki_bot.py`: `sys.path.insert` hacks → `importlib.util.spec_from_file_location` (không pollute sys.path)
- `bot/wiki_bot.py`: Input sanitization — URL validation, category allowlist, question length cap (500 chars)
- `bot/wiki_bot.py`: Error messages không còn leak internal file paths (`_safe_error()`)
- `lib/gemini.py`: `PRICING` dict dùng config constants (`MODEL_PRO`, `MODEL_PRO_NEW`) thay vì hardcoded strings
- `web/routes/review.js`: 11x `err.message` không còn expose tới API response
- `web/routes/activity.js`, `builds.js`, `trigger.js`, `upload.js`: `err.message` → opaque error strings
- `web/public/style.css`: 3 undefined CSS variables (`--surface-2`, `--border`, `--text-muted`), 2 hardcoded `font-size` → design tokens

### Improved
- `bot/wiki_bot.py`: `send_message()` retry 3 lần với exponential backoff (1s, 2s) trên network errors
- `lib/gemini.py`: Per-request cost alert khi vượt `MAX_QUERY_COST_USD`
- `lib/gemini.py`, `lib/logger.py`: Type hints Python 3.10+ style (`X | None` thay vì `Optional[X]`)

---

## [v0.4.0] — 2026-04-14

### Breaking Changes
- None. Pipeline v0.3 continues to run unchanged. v0.4 is additive.

### Added

#### Markitdown Integration (PART 02–03)
- `tools/converters/markitdown_adapter.py` — unified converter for 15+ formats
  (DOCX, PDF, XLSX, PPTX, EPUB, HTML, ZIP, MP3, WAV, YouTube, images+EXIF)
- `tools/ingest_youtube.py` — YouTube transcript ingest via yt-dlp
- `tools/ingest_html.py` — HTML page ingest with BeautifulSoup cleanup
- `tools/ingest_audio.py` — audio/video transcript ingest
- `convert_manual.py` now uses markitdown backend (backward compatible with old DOCX/PDF)
- 73 existing raw files re-converted through markitdown for format consistency

#### Gemini 3.1 Pro Support (PART 04)
- `MODEL_PRO_NEW=gemini-3.1-pro-preview` in `.env`
- `MODEL_PRO_NEW_LOCATION=global` (required — not available per-region)
- Feature flag `USE_PRO_NEW=false` (enable after A/B test validation)
- A/B test results in `trienkhai/upgrade-v0.4/ab-test-extract.md` and `ab-test-compile.md`

#### Dual-Vote Cross-Validation (PART 05–06)
- `lib/openai_client.py` — OpenAI GPT-5.4 client with retry, cost tracking, max_completion_tokens
- `lib/dual_vote.py` — semantic similarity + consensus engine
- `skills/dual-vote/scripts/dual_vote_skill.py` — CLI wrapper
- `skills/extract-claims/scripts/extract_dual.py` — dual-vote extract (Gemini + GPT-5.4)
- `skills/compile-wiki/scripts/compile_dual.py` — dual-vote compile
- Feature flag `DUAL_VOTE_ENABLED=true`
- Logs: `logs/dual-vote-YYYY-MM.jsonl` — status (AGREE/PARTIAL/DISAGREE), costs, scores
- Review queue: `claims/.review-queue/*.json` — human review for DISAGREE cases

#### Regression & Testing Tools (PART 07)
- `tools/regression_test.py` — orchestrator for full v0.4 rebuild (extract_dual + compile_dual)
- `tools/wiki_diff.py` — HTML side-by-side diff engine (v0.3 vs v0.4)
- `trienkhai/upgrade-v0.4/benchmark.md` — v0.3 baseline + v0.4 target metrics
- `trienkhai/upgrade-v0.4/bot-qa-test.md` — 30 QA questions across 6 categories
- `trienkhai/upgrade-v0.4/regression-review.md` — human review template

#### Production & Monitoring (PART 08)
- `scripts/rollback-v0.4.sh` — 1-click rollback to v0.3 (with `--dry-run` mode)
- `tools/cron_tasks.py` — added `dual-vote-check` (hourly DISAGREE alert) and `daily-digest` (8h summary)
- `tools/quality_dashboard.py` — added `--v04` tab for dual-vote agreement rate + cost split
- `docs/runbook.md` — operational runbook for v0.4 production

### Changed
- `.env` — `DUAL_VOTE_ENABLED=true` (enabled after PART 06 validation)
- `.env` — Added `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-5.4`, `OPENAI_BASE_URL`
- `PROJECT_SUMMARY.md` — Updated to reflect v0.4 architecture

### Fixed
- `lib/openai_client.py:176` — changed `max_tokens` → `max_completion_tokens` for GPT-5.4 (BUG-001)
- `lib/dual_vote.py` — `_strip_markdown_fence()` before JSON parse for Gemini responses (BUG-003)
- `lib/openai_client.py` — base URL validation: `sk-or-v1-` → OpenRouter, `sk-proj-` → OpenAI (BUG-001)

### Known Issues / Pending USER ACTIONs
- `USE_PRO_NEW=false` — Gemini 3.1 Pro not yet enabled pending API quota confirmation
- Regression test (`tools/regression_test.py --full`) not yet run — requires human to trigger
- Bot QA test (`trienkhai/upgrade-v0.4/bot-qa-test.md`) not yet executed

---

## [v0.3.0] — 2026-04-08

### Summary
Production MVP: 7 categories, 2,252 approved claims, 213 wiki pages, Telegram bot live.

### Architecture
- Single Gemini 2.5 Pro for extract + compile
- Manual DOCX/PDF ingest only
- 25 known conflicts (manual detection)
- Cost per full build: $6.50
- Snapshot: `build/snapshots/v0.3-pre-upgrade-2026-04-13/`

---

## [v0.2.0] — 2026-04-05

### Summary
7-stage pipeline stable. Batch approval workflow. Telegram bot with context caching.

---

## [v0.1.0] — 2026-04-04

### Summary
Initial MVP. Single-category proof of concept (hosting).

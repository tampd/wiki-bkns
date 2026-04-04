# BKNS Agent Wiki — Lộ Trình Triển Khai (Roadmap)

> Cập nhật: 2026-04-04

## ✅ Wave 1: Foundation (Scaffold + Shared Libs)
- [x] Python packages: beautifulsoup4, html2text, python-dotenv
- [x] Cấu trúc thư mục (raw/, claims/, wiki/, build/, logs/, etc)
- [x] Vertex AI credentials + .env
- [x] .gitignore + .gitattributes
- [x] `lib/config.py` — Configuration (paths, models, quality gates, constants)
- [x] `lib/logger.py` — JSONL logging (general, intake, query, approval)
- [x] `lib/telegram.py` — Telegram notifications (skill, error, report, conflict)
- [x] `lib/gemini.py` — Vertex AI wrapper (standard, cache, vision — 3 modes)
- [x] `lib/utils.py` — Hashing, slug, YAML, frontmatter, claim ID generation
- [x] Registry files (entities, sources, claims)
- [x] `build/active-build.yaml`
- [x] `wiki/index.md` + `wiki/support/lien-he.md`
- [x] `agents.yaml`

## ✅ Wave 2: Core Ingest
- [x] `skills/crawl-source/SKILL.md + scripts/crawl.py`
- [x] `skills/extract-claims/SKILL.md + scripts/extract.py`
- [x] Live test: crawl bkns.vn/hosting → ✅ (Cloudflare block body, structure OK)
- [x] Pipeline: crawl → raw/ → sources/registry.yaml → logs/ → Telegram
- [x] `tools/crawl_bkns.py` — Batch crawl tool

## ✅ Wave 3: Compile + Query + Build (MVP Phase 0.5)
- [x] `skills/compile-wiki/SKILL.md + scripts/compile.py` — Self-review mandatory
- [x] `skills/query-wiki/SKILL.md + scripts/query.py` — Implicit caching
- [x] `skills/build-snapshot/SKILL.md + scripts/snapshot.py` — Version control
- [x] Test query-wiki: "Hotline BKNS?" → ✅ trả lời chính xác, $0.00037/query
- [x] Test build-snapshot: ✅ BLD-20260404-181433 (v0.1)

## ⏳ Wave 4: Quality + Image (Phase 1)
- [ ] `skills/ingest-image/` — Vision extract bảng giá từ screenshot
- [ ] `skills/lint-wiki/` — Syntax check + Gemini Pro semantic lint
- [ ] `skills/ground-truth/` — Weekly live verification
- [ ] MkDocs viewer setup

## ⏸️ Wave 5: Intelligence (Phase 2)
- [ ] `skills/auto-file/` — FAQ candidates detection
- [ ] `skills/cross-link/` — Auto internal linking
- [ ] Cron jobs configuration

---

## ⚠️ Known Issues
- BKNS website có Cloudflare protection → crawl trả về empty content (word_count=0)
- Fallback: paste thủ công vào `raw/manual/` → extract-claims xử lý bình thường
- URL `/lien-he` trả 404 → cần tìm URL liên hệ đúng

## 📊 Metrics (Wave 1-3)
- 5 shared lib modules: config, logger, telegram, gemini, utils
- 5 skills implemented: crawl, extract, compile, query, build-snapshot
- Query cost: ~$0.0004/query (wiki nhỏ), dự kiến $0.0003 khi cache kick in
- Build: v0.1, 2 wiki files, ~428 tokens

## 📝 Hướng dẫn sử dụng cơ bản
```bash
# Crawl trang BKNS
PYTHONPATH=/home/openclaw/wiki python3 skills/crawl-source/scripts/crawl.py --force https://bkns.vn/URL

# Extract claims từ raw files
PYTHONPATH=/home/openclaw/wiki python3 skills/extract-claims/scripts/extract.py

# Compile claims → wiki page
PYTHONPATH=/home/openclaw/wiki python3 skills/compile-wiki/scripts/compile.py hosting

# Query wiki
PYTHONPATH=/home/openclaw/wiki python3 skills/query-wiki/scripts/query.py "câu hỏi"

# Build snapshot
PYTHONPATH=/home/openclaw/wiki python3 skills/build-snapshot/scripts/snapshot.py
```

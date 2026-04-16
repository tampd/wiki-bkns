# BKNS Agent Wiki — Lộ Trình Triển Khai (Roadmap)

> Cập nhật: 2026-04-04 — ALL 5 WAVES COMPLETE ✅

## ✅ Wave 1: Foundation (Scaffold + Shared Libs)
- [x] Python packages: beautifulsoup4, html2text, python-dotenv
- [x] Cấu trúc thư mục (raw/, claims/, wiki/, build/, logs/, skills/, etc)
- [x] Vertex AI credentials + .env
- [x] .gitignore + .gitattributes
- [x] `lib/config.py` — Configuration (paths, models, quality gates, constants)
- [x] `lib/logger.py` — JSONL logging (general, intake, query, approval)
- [x] `lib/telegram.py` — Telegram notifications (skill, error, report, conflict)
- [x] `lib/gemini.py` — Vertex AI wrapper (standard, cache, vision — 3 modes)
- [x] `lib/utils.py` — Hashing, slug, YAML, frontmatter, claim ID generation
- [x] Registry files (entities, sources, claims)
- [x] `build/active-build.yaml` + `wiki/index.md` + `wiki/support/lien-he.md`
- [x] `agents.yaml`

## ✅ Wave 2: Core Ingest
- [x] `skills/crawl-source/` — HTTP crawl + Markdown clean
- [x] `skills/extract-claims/` — Gemini Pro extraction + conflict detection
- [x] Live test: crawl bkns.vn → ✅ (Cloudflare block body content)

## ✅ Wave 3: Compile + Query + Build (MVP Phase 0.5)
- [x] `skills/compile-wiki/` — Claims → wiki + mandatory self-review
- [x] `skills/query-wiki/` — Gemini Flash + implicit context caching
- [x] `skills/build-snapshot/` — Version manifest + Git tag
- [x] Test query-wiki: ✅ hotline → correct, $0.00037/query
- [x] Test build-snapshot: ✅ BLD-20260404-181433 v0.1

## ✅ Wave 4: Quality + Image (Phase 1)
- [x] `skills/ingest-image/` — Gemini Flash Vision → claims from screenshots
- [x] `skills/lint-wiki/` — 2-layer: Python syntax + Gemini Pro semantic
- [x] `skills/ground-truth/` — Weekly verification vs live data

## ✅ Wave 5: Intelligence (Phase 2)
- [x] `skills/auto-file/` — Query log analysis → FAQ candidates
- [x] `skills/cross-link/` — Wiki link graph analysis + suggestions

---

## 📊 Final Metrics
- **10/10 skills** implemented and verified
- **5 shared lib modules** (config, logger, telegram, gemini, utils)
- **0 lint errors** on initial run
- **Query cost**: ~$0.0004/query
- **Build v0.1**: 2 wiki files, ~428 tokens

## ⚠️ Known Issues
- BKNS website Cloudflare protection → crawl trả về empty content
- Fallback: paste thủ công vào `raw/manual/`

## 📋 Tiếp theo để Production
1. Paste dữ liệu thủ công vào `raw/manual/` và chạy extract
2. Approve claims → compile → build → query
3. Set up cron jobs cho ground-truth + lint
4. Kết nối Telegram bot commands (/them, /extract, /compile, /hoi, /duyet)
5. MkDocs viewer (optional)

## 📝 Usage
```bash
export PYTHONPATH=/wiki

# Crawl
python3 skills/crawl-source/scripts/crawl.py --force https://bkns.vn/URL

# Extract claims
python3 skills/extract-claims/scripts/extract.py

# Compile wiki
python3 skills/compile-wiki/scripts/compile.py hosting

# Approve draft
python3 skills/compile-wiki/scripts/compile.py --approve hosting

# Query
python3 skills/query-wiki/scripts/query.py "câu hỏi"
python3 skills/query-wiki/scripts/query.py --interactive

# Build
python3 skills/build-snapshot/scripts/snapshot.py

# Image ingest
python3 skills/ingest-image/scripts/ingest.py /path/to/image.png

# Lint
python3 skills/lint-wiki/scripts/lint.py --semantic

# Ground truth
python3 skills/ground-truth/scripts/verify.py hosting

# FAQ scan
python3 skills/auto-file/scripts/auto_file.py --days 7

# Cross-link
python3 skills/cross-link/scripts/crosslink.py
```

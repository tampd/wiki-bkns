# BKNS Knowledge Wiki

> **LLM-Compiled Markdown Knowledge Base** cho hệ sinh thái sản phẩm BKNS.vn
> Dual-vote cross-validation · Gemini Implicit Caching · No RAG, no vector DB

[![Version](https://img.shields.io/badge/version-v1.1.1-blue)]() [![License](https://img.shields.io/badge/license-MIT-green)]() [![Python](https://img.shields.io/badge/python-3.10+-blue)]() [![Node](https://img.shields.io/badge/node-18+-green)]()

---

## Tổng quan

BKNS Wiki là knowledge base tự-compile bằng LLM, phục vụ bot CSKH Telegram + Web Admin Portal nội bộ. Hệ thống **không dùng RAG/vector DB** — toàn bộ wiki (~200k–500k token) được nạp làm prefix cố định mỗi query, Gemini Implicit Caching tự động tiết kiệm ~75% token input.

| Thông tin | Chi tiết |
|-----------|----------|
| **Phiên bản hiện tại** | v1.1.1 (2026-04-16) — xem [CHANGELOG.md](./CHANGELOG.md) |
| **Stack** | Python 3.10+ pipeline · Node.js 18+ web portal · PM2 · Telegram bot |
| **LLM** | Gemini 2.5 Pro/Flash (Vertex AI) + OpenAI GPT-5.4 (dual-vote) |
| **Domain** | [wiki.bkns.vn](https://wiki.bkns.vn) (SSL Let's Encrypt) |
| **Kho dữ liệu** | 2,252 approved claims, 198 wiki pages, builds v0.1 → v0.6 |
| **Web Portal** | Admin Review UI (dual-vote resolution, bulk actions) |
| **Bot Telegram** | `/hoi`, `/them`, `/extract`, `/compile`, `/build`, `/lint`, `/status` |
| **License** | [MIT](./LICENSE) |

---

## Kiến trúc pipeline

```
[Telegram /them URL]  [File upload]  [Image screenshot]
           │               │                │
           ▼               ▼                ▼
    ┌─────────────────────────────────────────────┐
    │  1. crawl-source     → raw/ (Markdown thô)  │
    │  2. ingest-image     → Gemini Flash Vision  │
    │  3. extract-claims   → claims/.drafts/      │  ← Dual-vote
    │     (Gemini Pro + GPT-5.4 cross-validate)   │     cross-check
    │  4. [Review queue]   → claims/approved/     │  ← Human review
    │     (Web Portal: approve/reject/conflict)   │     (25 conflicts
    │  5. compile-wiki     → wiki/products/*.md   │     resolved manually)
    │     (Gemini Pro + self-review)              │
    │  6. build-snapshot   → build/manifests/     │
    │  7. query-wiki       → /hoi answers         │
    │     (Flash + Implicit Cache, ~$0.0004/q)    │
    └─────────────────────────────────────────────┘
```

**Chi tiết:** xem [docs/SPEC-wiki-system.md](./docs/SPEC-wiki-system.md) (v2.0) và [docs/runbook.md](./docs/runbook.md).

---

## Tính năng chính

### 1. LLM-Compiled Wiki (ý tưởng Andrej Karpathy)
Toàn bộ kiến thức BKNS biên soạn thành Markdown có cấu trúc, metadata, nguồn trích dẫn. Gemini Pro vừa compile vừa tự-review từng page trước khi publish.

### 2. Dual-Vote Cross-Validation (v0.4+)
Mỗi claim được extract/compile bởi **cả 2 model độc lập**: Gemini 2.5 Pro + OpenAI GPT-5.4. Kết quả được so sánh ngữ nghĩa (semantic similarity). Trạng thái:
- **AGREE** → auto-approve
- **PARTIAL** → flag low confidence
- **DISAGREE** → vào review queue cho con người giải quyết

Log per-call tại `logs/dual-vote-YYYY-MM.jsonl`.

### 3. Gemini Implicit Context Caching
Wiki đặt cố định ở đầu mỗi query request. Gemini tự động nhận diện prefix lặp lại và cache — không cần quản lý thủ công, không phí storage, tiết kiệm ~75% chi phí token input.

### 4. Markitdown Multi-Format Ingest (v0.4+)
Convert 15+ formats qua `tools/converters/markitdown_adapter.py`: DOCX, PDF, XLSX, PPTX, EPUB, HTML, ZIP, MP3, WAV, YouTube transcript, ảnh kèm EXIF. Xem [docs/converters.md](./docs/converters.md).

### 5. Web Admin Portal
Portal nội bộ (Express + vanilla JS SPA) phục vụ review workflow:
- Sidebar tree theo category
- Reader + Toast UI Editor
- Dual-vote conflict resolution với bulk actions
- Quality dashboard: lint errors, ground-truth drift, cost split

### 6. Cost Monitoring
- `lib/logger.py::log_gemini_call()` ghi per-call JSONL vào `logs/gemini-calls-YYYY-MM.jsonl`
- Alert khi 1 query vượt `MAX_QUERY_COST_USD` (mặc định $0.01)
- Monthly budget cap `MONTHLY_BUDGET_USD` trong `lib/config.py`

---

## Quick Start

```bash
# 1. Clone
git clone git@github.com:tampd/wiki-bkns.git wiki && cd wiki

# 2. Python + Node dependencies
pip install -r requirements.txt
cd web && npm install && cd ..

# 3. Environment config
cp .env.example .env
# Điền TELEGRAM_BOT_TOKEN, GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT, v.v.

# 4. Smoke test
python3 -c "from lib.config import WORKSPACE; print('OK:', WORKSPACE)"
pytest tests/ -q

# 5. Start services
pm2 start ecosystem.config.js           # web portal + cron jobs
python3 bot/wiki_bot.py                 # Telegram bot (hoặc qua PM2)
```

**Yêu cầu hệ thống:** Python 3.10+, Node.js 18+, PM2 (`npm install -g pm2`), Google Cloud service account có quyền Vertex AI.

---

## Bot Commands (Telegram)

| Command | Quyền | Mô tả |
|---------|-------|-------|
| `/hoi [câu hỏi]` | Mọi người | Hỏi đáp về sản phẩm BKNS |
| `/status` | Mọi người | Trạng thái hệ thống + build version |
| `/help` | Mọi người | Hướng dẫn sử dụng |
| `/them [URL]` | Admin | Crawl URL mới vào `raw/` (v1.1.0) |
| `/extract` | Admin | Extract claims từ raw files mới |
| `/compile [category]` | Admin | Compile wiki (hoặc `--all`) |
| `/build` | Admin | Tạo build snapshot mới |
| `/lint` | Admin | Kiểm tra chất lượng wiki |

---

## Cấu trúc thư mục

```
wiki/
├── bot/              Telegram bot (wiki_bot.py)
├── lib/              Shared libs: config, logger, gemini, openai_client, dual_vote, utils
├── skills/           14 skills: crawl-source, extract-claims, compile-wiki, query-wiki,
│                     build-snapshot, ingest-image, lint-wiki, ground-truth, auto-file,
│                     cross-link, dual-vote, verify-claims, audit-wiki
├── tools/            Adhoc tools: converters, regression_test, quality_dashboard, cron_tasks
├── web/              Express + vanilla JS Admin Portal
├── claims/
│   ├── .drafts/      Draft claims đang chờ review
│   ├── .review-queue/ Dual-vote DISAGREE cases
│   └── approved/     Claims đã duyệt (theo category)
├── wiki/             Markdown wiki pages (wiki/products/<category>/*.md)
├── build/
│   ├── active-build.yaml  Manifest active hiện tại
│   ├── manifests/    Build history (BLD-YYYYMMDD-HHMMSS.yaml)
│   └── snapshots/    Snapshot files
├── raw/              Dữ liệu thô (crawl, manual, images)
├── assets/
│   ├── images/       Thumbnails ≤100KB
│   └── evidence/     Full-res screenshots (Git LFS)
├── logs/             Lint, verify, dual-vote, gemini-calls JSONL
├── docs/             SPEC, runbook, REVIEWER_GUIDE, converters
├── scripts/          rollback-v0.4.sh, utility scripts
└── tests/            pytest suites (test_pipeline_smoke, test_bot, ...)
```

---

## Tài liệu

| File | Nội dung |
|------|----------|
| [docs/SPEC-wiki-system.md](./docs/SPEC-wiki-system.md) | Spec kiến trúc đầy đủ v2.0 — skills matrix, API, infra |
| [docs/runbook.md](./docs/runbook.md) | Operations runbook v0.4 (monitoring, rollback) |
| [docs/REVIEWER_GUIDE.md](./docs/REVIEWER_GUIDE.md) | Hướng dẫn review dual-vote conflicts |
| [docs/converters.md](./docs/converters.md) | 15+ format ingest qua markitdown |
| [HANDOVER.md](./HANDOVER.md) | Tài liệu bàn giao v1.1.0 — cài đặt + bot commands |
| [CHANGELOG.md](./CHANGELOG.md) | Lịch sử thay đổi (SemVer) |
| [LESSONS.md](./LESSONS.md) | Bài học quan trọng (≤10 entries) |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Quy trình đóng góp |
| [OPTIMIZATION_PLAN.md](./OPTIMIZATION_PLAN.md) | Lộ trình tối ưu 5 phases |
| [OPTIMIZATION_LOG.md](./OPTIMIZATION_LOG.md) | Log thực thi optimization |

---

## Chi phí vận hành (thực tế)

| Hoạt động | Chi phí |
|-----------|---------|
| Extract 1 URL (Gemini Pro) | ~$0.015 |
| Extract dual-vote (Gemini + GPT-5.4) | ~$0.030 |
| Compile 1 category | ~$0.10 |
| Query 1 câu (Flash + Implicit Cache) | ~$0.0004 |
| Build snapshot | gần như miễn phí |

Monthly budget cap mặc định: **$50** (xem `lib/config.py`).

---

## Trạng thái dự án

| Phase | Nội dung | Trạng thái |
|-------|----------|-----------|
| **Phase 0 — Foundation** | 5 shared libs, registries, scaffold | ✅ Complete |
| **Phase 1 — Core Ingest** | crawl + extract + compile + query + build | ✅ Complete (v0.3) |
| **Phase 2 — Quality** | lint 2-layer, ground-truth, image vision | ✅ Complete |
| **Phase 2.5 — Web Portal** | Admin portal, Toast UI, review queue | ✅ Complete |
| **Phase 3 — Dual-Vote v0.4** | Gemini + GPT-5.4 cross-validation | ✅ Complete |
| **Phase 4 — Optimization v1.1.0** | Dead code removal, type hints, error logging | ✅ Complete |
| **Phase 5 — Intelligence** | auto-file FAQ, cross-link graph | 🔲 Disabled (code ready, not active) |

**Tổng metrics (2026-04-16):**
- 2,252 approved claims (21.8% ground-truth, 77.9% high-confidence)
- 198 wiki pages (7 categories)
- 14 skills (11 active / tested, 3 pending/disabled)
- 38 tests pass (100%)
- 6 build snapshots (v0.1 → v0.6)

---

## License

MIT — xem [LICENSE](./LICENSE). Copyright © 2026 Tampd (BKNS).

---

## Liên hệ

- **Maintainer:** Tampd (BKNS) — `duytam@bkns.vn`
- **Issues:** https://github.com/tampd/wiki-bkns/issues
- **Security:** Email trực tiếp thay vì mở issue công khai

---

*BKNS Knowledge Wiki v1.1.1 — LLM-Compiled + Dual-Vote + Implicit Caching*
*Domain: wiki.bkns.vn | Cập nhật: 2026-04-16*

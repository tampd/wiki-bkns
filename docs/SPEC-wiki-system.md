# BKNS Agent Wiki — System Design Document (SDD v3.0)

> **Version:** 3.0.0
> **Updated:** 2026-04-16
> **Status:** Production — Active (v1.1.0 / Build v0.6)
> **Maintainer:** Tampd · duytam@bkns.vn

---

## 1. Executive Summary

**BKNS Agent Wiki** là knowledge base nội bộ tự động phục vụ bot CSKH và nhân viên tra cứu thông tin sản phẩm/dịch vụ BKNS. Pipeline compile wiki từ tài liệu thô qua LLM, không dùng RAG hay vector DB.

### Trạng thái hiện tại (Build v0.6 — 2026-04-15)

| Metric | Giá trị |
|--------|---------|
| Wiki pages | **198** (7 categories) |
| Approved claims | **2,252** (21.8% ground-truth, 77.9% high-confidence) |
| Draft claims | 809 (pending review) |
| Review queue | 25 conflicts (DISAGREE) |
| Build | v0.6 — BLD-20260415-135355 |
| Wiki tokens | 127,199 |
| Test suite | 33 tests, 100% pass |
| Skills | 14 pipeline skills |

---

## 2. Problem Statement

BKNS có hàng trăm sản phẩm/dịch vụ (VPS, hosting, SSL, domain, email, server, software). Thông tin phân tán trên website, landing pages, docs nội bộ. Không có single source of truth cho AI chatbot và nhân viên support.

**Giải pháp:** Pipeline tự động `Raw → Extract → Review → Compile → Wiki → Query`, phục vụ cả con người (Web Portal) lẫn AI (Telegram Bot).

---

## 3. Goals & Non-Goals

### Goals

| # | Goal | Metric |
|---|------|--------|
| G1 | Single source of truth cho toàn bộ sản phẩm | 100% categories có wiki pages |
| G2 | AI có thể trả lời câu hỏi sản phẩm | Bot `/hoi` hoạt động, ~$0.0004/query |
| G3 | Human có thể review và chỉnh sửa | Web portal WYSIWYG ≤3 clicks |
| G4 | Dual-validation: cross-check Gemini + GPT | AGREE/PARTIAL/DISAGREE với log cost |
| G5 | Audit trail đầy đủ | Claim traceability, backup per edit, cost log |
| G6 | Cost kiểm soát chặt | Monthly budget $50, alert per query |

### Non-Goals

- ❌ SEO / public-facing wiki (internal only, `noindex`)
- ❌ Multi-user auth / RBAC (single admin token)
- ❌ Real-time collaboration
- ❌ RAG / vector database

---

## 4. Architecture

### 4.1 Data Pipeline Flow

```
┌─ INPUT ───────────────────────────────────────────────────────┐
│ Telegram /them [URL]  →  crawl-source  →  raw/*.md            │
│ Web UI upload         →  markitdown_adapter.py                 │
│ (DOCX/PDF/XLSX/PPTX/EPUB/HTML/ZIP/MP3/WAV/YouTube/image)     │
│ ingest_html.py / ingest_youtube.py / ingest_audio.py          │
└───────────────────────────────────────────────────────────────┘
                      ↓
┌─ EXTRACT ─────────────────────────────────────────────────────┐
│ extract.py  →  Gemini 2.5 Pro  →  claims YAML                 │
│ extract_dual.py (khi DUAL_VOTE_ENABLED=true):                  │
│   Gemini 2.5 Pro + GPT-5.4 chạy song song                     │
│   Semantic similarity → AGREE / PARTIAL / DISAGREE             │
│   DISAGREE → claims/.review-queue/  (human review)             │
│   Log: logs/dual-vote-YYYY-MM.jsonl                            │
└───────────────────────────────────────────────────────────────┘
                      ↓
┌─ REVIEW ──────────────────────────────────────────────────────┐
│ AGREE → auto-approve → claims/approved/                        │
│ DISAGREE → Web Portal /api/review/queue → human resolve        │
│   Actions: approve, reject, flag-for-fix, bulk                 │
└───────────────────────────────────────────────────────────────┘
                      ↓
┌─ COMPILE ─────────────────────────────────────────────────────┐
│ compile.py  →  Gemini 2.5 Pro  →  9 sub-pages per category    │
│ Self-review: Gemini re-reads page vs source claims             │
│   Hallucination detected → auto-correct (max 3 attempts)       │
│   ≥5 conflicts → block until human review                      │
│   0 claims → skeleton fallback page với ⏳                     │
│ Multi-page output: wiki/products/{category}/*.md               │
└───────────────────────────────────────────────────────────────┘
                      ↓
┌─ BUILD ───────────────────────────────────────────────────────┐
│ snapshot.py → BLD-YYYYMMDD-HHMMSS → build/manifests/          │
│ Token estimate, wiki hash SHA256, active-build.yaml update     │
└───────────────────────────────────────────────────────────────┘
                      ↓
┌─ QUERY ───────────────────────────────────────────────────────┐
│ query.py: wiki prefix (127K tokens) + câu hỏi user            │
│ Gemini 2.5 Flash + Implicit Context Caching (auto, 5min TTL)  │
│ ~$0.0004/query (75-90% tiết kiệm sau lần đầu)                 │
│ Channels: Telegram /hoi hoặc Web API                           │
└───────────────────────────────────────────────────────────────┘
```

### 4.2 Component Architecture

```
wiki/
├── lib/                        # Python shared libraries (2,555 LOC)
│   ├── config.py               # Central config: env vars, paths, models, category map
│   ├── gemini.py               # Vertex AI Gemini wrapper: generate, retry, cost, caching
│   ├── openai_client.py        # OpenAI GPT-5.4 client: retry, cost, max_completion_tokens
│   ├── dual_vote.py            # Consensus engine: parallel run, semantic similarity
│   ├── logger.py               # JSONL structured logging: gemini, openai, dual-vote, query
│   ├── telegram.py             # Bot notification helpers: notify_skill, notify_error
│   ├── utils.py                # YAML/MD parsing, claim ID, slug, hash, datetime
│   ├── fallback.py             # JSON parse fallback: strip fence, fix JSON, regex
│   └── __init__.py
│
├── bot/                        # Telegram bot daemon (511 LOC)
│   ├── wiki_bot.py             # 7 commands, polling loop, input validation
│   ├── .last_offset            # Telegram update offset (polling state)
│   └── manage.sh               # Start/stop helper
│
├── skills/                     # 14 pipeline skills (612K total)
│   ├── extract-claims/         # raw/ → claims/.drafts/ YAML (Gemini Pro)
│   ├── compile-wiki/           # claims/approved/ → wiki/ MD (Gemini Pro + self-review)
│   ├── query-wiki/             # Q&A từ wiki prefix (Gemini Flash + implicit cache)
│   ├── build-snapshot/         # wiki/ → versioned snapshot + manifest
│   ├── ingest-image/           # screenshot → claims YAML (Gemini Flash Vision)
│   ├── lint-wiki/              # quality checks (frontmatter, links, empty pages)
│   ├── ground-truth/           # Excel SOT validation ⚠️ (Cloudflare-blocked)
│   ├── crawl-source/           # URL → raw/ MD ⚠️ (Cloudflare-blocked)
│   ├── auto-file/              # FAQ auto-categorization 🔲 (Phase 2, disabled)
│   ├── cross-link/             # Internal wiki linking 🔲 (Phase 2, disabled)
│   ├── dual-vote/              # Dual-vote CLI wrapper (v0.4+)
│   ├── verify-claims/          # Claim verification 🔲 (not integrated)
│   ├── audit-wiki/             # Audit trail 🔲 (not integrated)
│   └── (each has SKILL.md spec + scripts/ subfolder)
│
├── tools/                      # Utility scripts (20+)
│   ├── convert_manual.py       # DOCX/PDF/XLSX/PPTX/EPUB → MD (markitdown)
│   ├── cron_tasks.py           # health-check, dual-vote-alert, daily-digest, conflict-scan
│   ├── approve_and_compile.py  # Batch approve + compile workflow
│   ├── quality_dashboard.py    # Cost + agreement rate + lint stats (--v04 flag)
│   ├── regression_test.py      # v0.4 rebuild with extract_dual + compile_dual
│   ├── detect_conflicts.py     # Claim conflict detection
│   ├── batch_pipeline.py       # Orchestrate full pipeline
│   ├── ingest_html.py          # HTML ingest (BeautifulSoup)
│   ├── ingest_youtube.py       # YouTube transcript (yt-dlp)
│   ├── ingest_audio.py         # MP3/WAV transcription (Whisper)
│   ├── librarian_gemini.py     # Librarian assistant backend (web)
│   └── librarian_processor.py  # Librarian processing pipeline
│
├── web/                        # Express.js Admin Portal (Node.js 18+)
│   ├── server.js               # Express app: auth, rate-limit, CSP, error handling
│   ├── middleware/auth.js       # Bearer token + bcrypt password auth
│   ├── routes/                 # 9 API route handlers (2,946 LOC)
│   │   ├── wiki.js             # CRUD, search, tree, changelog, export, image upload
│   │   ├── review.js           # Dual-vote conflict review + bulk actions
│   │   ├── files.js            # File browser, delete, view content
│   │   ├── activity.js         # Activity log
│   │   ├── builds.js           # Build history + snapshots
│   │   ├── status.js           # System status
│   │   ├── librarian.js        # Librarian assistant
│   │   ├── upload.js           # File upload handler (multipart)
│   │   └── trigger.js          # Pipeline trigger API
│   ├── lib/
│   │   ├── pipeline-runner.js  # Python subprocess runner cho skills
│   │   ├── librarian-store.js  # Librarian conversation state
│   │   └── gemini-bridge.js    # Gemini API bridge cho web
│   ├── public/                 # Frontend SPA (vanilla JS + TOAST UI Editor)
│   │   ├── index.html          # 4-tab SPA: Wiki | Review | Upload | Builds
│   │   ├── app.js              # Client-side logic
│   │   ├── librarian.js        # Librarian chat UI
│   │   └── style.css           # Dark theme, glassmorphism
│   ├── nginx-upload.trieuphu.biz.conf  # Nginx reverse proxy config
│   ├── deploy-nginx.sh         # Nginx + Let's Encrypt deployment
│   └── ecosystem.web.config.js # PM2 config cho web server (process: wiki-portal)
│
├── raw/                        # Tài liệu thô (72 files, 15M)
│   └── manual/                 # 72 Markdown files đã convert
│
├── claims/                     # Claims data (33M)
│   ├── .drafts/products/       # Draft claims (809 pending)
│   ├── approved/products/      # Approved claims (2,252)
│   ├── .review-queue/          # DISAGREE cases (25 files)
│   ├── registry.yaml           # Claims index
│   └── .cache/                 # SHA256 incremental cache
│
├── wiki/                       # Compiled wiki (2.1M, 198 pages)
│   └── products/               # 7 categories (xem mục 5.3)
│
├── build/                      # Build artifacts
│   ├── active-build.yaml       # Active build metadata
│   ├── manifests/              # Build history (BLD-YYYYMMDD-HHMMSS.yaml)
│   └── snapshots/              # Immutable wiki snapshots (v0.1 → v0.6)
│
├── logs/                       # JSONL audit logs (2M, growing)
├── docs/                       # Tài liệu (100K)
├── tests/                      # pytest suite (33 tests, 100% pass)
├── entities/registry.yaml      # Entity registry
├── sources/registry.yaml       # Source → claim traceability
├── ecosystem.config.js         # PM2 config (bot + 2 crons)
├── .env                        # Runtime config (KHÔNG commit vào git)
├── .env.example                # Config template
└── requirements.txt            # Python dependencies (pinned)
```

---

## 5. Implementation Details

### 5.1 Data Model — Claim (YAML)

```yaml
# claims/approved/products/{category}/CLM-*.yaml
claim_id: CLM-BKNS:PROMO_S-STORAGE_ABC123
entity_id: bkns:promo_server:config1
entity_type: product_hardware          # product_hardware | product_service | policy | pricing
entity_name: Máy Chủ Tặng Kèm - Cấu hình 1
attribute: storage_size
value: 600
unit: GB
qualifiers:
  storage_type: SAS
source_ids:
  - SRC-DICH_VU_THUE_CHO_AT_MAY_CHU_COLOCATION_TAI_BKNS_2026_04_04
observed_at: '2026-04-04T20:52:19.160810+07:00'
valid_from: '2026-04-04'
confidence: ground_truth              # ground_truth | high | medium | low
review_state: approved                # draft | approved | rejected | conflict
risk_class: low                       # low | medium | high | critical
```

### 5.2 Data Model — Wiki Page Frontmatter

```yaml
# wiki/products/{category}/{page}.md
page_id: wiki.products.hosting.tong-quan
title: Cloud Hosting BKNS — Tổng Quan Chi Tiết
category: products/hosting
updated: '2026-04-14'
review_state: approved                # approved | drafted | rejected
claims_used: 192
compile_cost_usd: 0.0354
self_review: pass                     # pass | fail
corrections: 0
```

### 5.3 Sub-Page Architecture (mỗi category)

Mỗi category compile thành 9 standard sub-pages + product detail pages:

| # | File | Nội dung |
|---|------|---------|
| 1 | `tong-quan.md` | Tổng quan + ToC |
| 2 | `bang-gia.md` | Bảng giá |
| 3 | `thong-so.md` | Thông số kỹ thuật |
| 4 | `tinh-nang.md` | Tính năng |
| 5 | `chinh-sach.md` | Chính sách (SLA, support, thanh toán) |
| 6 | `cau-hoi-thuong-gap.md` | FAQ |
| 7 | `so-sanh.md` | So sánh sản phẩm |
| 8 | `huong-dan.md` | Hướng dẫn |
| 9 | `san-pham/{slug}.md` | Detail page từng sản phẩm |

**7 categories active (v0.6):** `hosting`, `vps`, `ssl`, `email`, `ten-mien`, `server`, `software`

### 5.4 AI Components

| Component | Model | Purpose | Cost ước tính |
|-----------|-------|---------|--------------|
| Extract claims | `gemini-2.5-pro` | Raw text → structured claims YAML | ~$0.015/file |
| Extract dual-vote | `gemini-2.5-pro` + `gpt-5.4` | Parallel cross-validation | ~$0.030/file |
| Compile wiki | `gemini-2.5-pro` | Claims → Markdown pages | ~$0.10/category |
| Self-review | `gemini-2.5-pro` | Verify compiled page vs source | Included |
| Query wiki | `gemini-2.5-flash` | Q&A với Implicit Cache | ~$0.0004/query |
| Ingest image | `gemini-2.5-flash` | Screenshot → claims YAML | Per image |
| Query librarian | `gemini-2.5-flash` | Librarian assistant | Per request |

### 5.5 Dual-Vote Engine (lib/dual_vote.py)

```
run_dual(text_a, text_b):
  1. Tokenize và normalize cả hai outputs
  2. Tính semantic similarity (cosine / token overlap)
  3. Threshold:
     - ≥ 0.9  → AGREE    → auto-approve
     - 0.6-0.89 → PARTIAL → flag low confidence
     - < 0.6  → DISAGREE → .review-queue/ + Telegram alert
  4. Log: logs/dual-vote-YYYY-MM.jsonl
     { ts, skill, action, status, score, cost_usd_gemini, cost_usd_openai, cost_usd_total }
```

### 5.6 Gemini Implicit Context Caching

- Wiki prefix (~127K tokens) được gửi cố định ở đầu mỗi query request
- Gemini tự động nhận diện prefix lặp lại và cache (TTL 5 phút)
- **Không cần quản lý thủ công** — không `create_cache()`, không cache ID
- Tiết kiệm 75–90% chi phí input tokens sau query đầu tiên
- Các kiểm tra cũ về explicit caching đã bị xóa khỏi `lib/gemini.py` (v1.1.0)

### 5.7 JSON Parsing Fallback (lib/fallback.py)

Gemini đôi khi wrap JSON trong markdown fence. `lib/fallback.py` thử theo thứ tự:
1. Parse trực tiếp
2. Strip markdown fence (` ```json ... ``` `) rồi parse
3. Fix malformed JSON (missing quotes, trailing commas)
4. Regex extract từ response text

---

## 6. API Design

### 6.1 Authentication

- **Login:** `POST /api/login` — body `{ password }` → trả về `{ token }`
- **All APIs:** `Authorization: Bearer <ADMIN_TOKEN>`
- **Token:** Bearer token từ env `ADMIN_TOKEN`; password hash dùng bcryptjs

### 6.2 Wiki APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/api/wiki/tree` | Category tree với pages + sub-pages |
| `GET` | `/api/wiki/search?q=` | Full-text search (198 pages) |
| `GET` | `/api/wiki/changelog?limit=` | Edit history |
| `GET` | `/api/wiki/export` | Bulk JSON export cho AI consumption |
| `GET` | `/api/wiki/:category/:page` | Đọc nội dung page |
| `PUT` | `/api/wiki/:category/:page` | Cập nhật page (auto-backup) |
| `POST` | `/api/wiki/:category/:page` | Tạo page mới |
| `GET` | `/api/wiki/:category/:page/backups` | Danh sách backups |
| `POST` | `/api/upload/image` | Upload ảnh vào editor (max 5MB) |

### 6.3 Review APIs (Dual-Vote)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/api/review/queue` | Danh sách DISAGREE conflicts |
| `POST` | `/api/review/resolve/:conflict_id` | Resolve 1 conflict (approve/reject/fix) |
| `POST` | `/api/review/bulk` | Bulk approve/reject nhiều conflicts |

### 6.4 System APIs

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `GET` | `/api/status` | Trạng thái hệ thống + build active |
| `GET` | `/api/activity` | Activity log |
| `GET` | `/api/builds` | Build history + snapshots |
| `POST` | `/api/trigger` | Trigger pipeline (extract/compile/build) |
| `GET` | `/api/files` | File browser |
| `DELETE` | `/api/files/:id` | Xóa file |
| `GET` | `/api/files/:id/content` | Xem nội dung file |
| `POST` | `/api/upload` | Upload files (multipart, max 50MB) |
| `POST` | `/api/librarian/chat` | Librarian assistant chat (v1.1.0+) |

### 6.5 AI Export Format

```json
// GET /api/wiki/export
{
  "exported_at": "2026-04-15T07:00:00Z",
  "total_pages": 198,
  "categories": [
    {
      "category": "vps",
      "label": "VPS",
      "pages": [
        {
          "page": "tong-quan",
          "title": "Cloud VPS BKNS — Tổng Quan",
          "content": "# Markdown content...",
          "frontmatter": { "claims_used": 93, "updated": "2026-04-14" }
        }
      ]
    }
  ]
}
```

---

## 7. UI/UX Design

### 7.1 Layout

Web Portal là 4-tab SPA:

| Tab | Nội dung |
|-----|---------|
| **Wiki** | Sidebar category tree → Reader / TOAST UI Editor |
| **Review** | Dual-vote conflicts: fix / diff / bulk actions |
| **Upload** | File browser + drag-drop upload |
| **Builds** | Build history + snapshot metadata |

### 7.2 Design System

| Token | Giá trị |
|-------|---------|
| Theme | Dark (`#0a1628` bg, `#f1f5f9` text) |
| Primary | Cyan gradient (`#06b6d4` → `#0891b2`) |
| Accent | Emerald (`#10b981`) |
| Fonts | DM Sans (body), Space Grotesk (headings), JetBrains Mono (code) |
| Glass | `blur(16px)`, `rgba(17, 29, 51, 0.5)` |
| Radius | `sm: 0.375rem` / `md: 0.5rem` / `lg: 0.75rem` / `xl: 1rem` |

### 7.3 Editor

- **TOAST UI Editor** (CDN) — WYSIWYG + Markdown dual-mode
- Image upload: drag & drop → `POST /api/upload/image` → serve từ `/wiki-assets/`
- Frontmatter: strip khi edit, re-attach khi save (tự động)
- **CSP constraint:** Dùng `'unsafe-inline'` vì TOAST UI Editor không hỗ trợ nonce. Chấp nhận cho internal portal.

---

## 8. Infrastructure

### 8.1 Server Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| OS | Ubuntu Linux | VPS hoặc dedicated server |
| Process manager | PM2 | Python (bot + crons) + Node.js (web) |
| Reverse proxy | Nginx | TLS 1.2/1.3, rate limiting, HSTS |
| AI — Gemini | Google Cloud Vertex AI | Implicit caching, Gemini 2.5 Flash + Pro |
| AI — GPT | OpenAI API hoặc OpenRouter | Chỉ khi `DUAL_VOTE_ENABLED=true` |
| DNS | upload.trieuphu.biz | Let's Encrypt TLS |

### 8.2 PM2 Processes

**Bot + Crons** (`ecosystem.config.js` — chạy bởi user `openclaw`)

| Tên | Script | Mode | Cron | Mô tả |
|-----|--------|------|------|-------|
| `bkns-wiki-bot` | `bot/wiki_bot.py --daemon` | fork | n/a | Telegram bot daemon |
| `bkns-cron-daily` | `tools/cron_tasks.py --task all` | cron | `0 0 * * *` (7h VN) | Health, digest, conflicts |
| `bkns-cron-promo` | `tools/cron_tasks.py --task promo-scrape` | cron | `0 2 * * 1` (9h VN T2) | Weekly promo scrape |

**Web Portal** (`web/ecosystem.web.config.js` — chạy bởi root PM2)

| Tên | Script | Port | Notes |
|-----|--------|------|-------|
| `wiki-admin` (hoặc `wiki-portal`) | `web/server.js` | 3000 | **Restart bằng `sudo pm2 reload wiki-admin`** |

> **LƯU Ý QUAN TRỌNG:** Web portal chạy dưới root PM2 daemon. Khi restart phải dùng:
> ```bash
> sudo bash -c "export PATH=/home/openclaw/.nvm/versions/node/v24.14.0/bin:\$PATH && pm2 reload wiki-admin"
> ```
> **KHÔNG** dùng `kill PID` hoặc `pm2 restart` của user thường.

### 8.3 Nginx Config

File: `web/nginx-upload.trieuphu.biz.conf`

- TLS: Let's Encrypt, redirect HTTP → HTTPS
- Rate limiting:
  - API: 500 req/15min (`zone=wiki_api`)
  - Login: 10 attempts/15min (`zone=wiki_login`)
  - Upload: 2 req/s (`zone=wiki_upload`)
- Proxy: localhost:3000
- Buffer: `client_max_body_size 55m`

### 8.4 Security

| Feature | Implementation |
|---------|---------------|
| HTTPS | TLS 1.2/1.3 via Let's Encrypt + Nginx |
| Auth | Bearer token (`ADMIN_TOKEN`) + bcrypt password |
| Rate limiting | Nginx (Cloudflare) + Express `express-rate-limit` |
| CSP | `script-src 'self' https://unpkg.com https://cdn.jsdelivr.net` + `'unsafe-inline'` |
| HSTS | `max-age=31536000; includeSubDomains` |
| Anti-SEO | `robots.txt` + `X-Robots-Tag: noindex, nofollow` mọi response |
| Headers | `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` |
| File limits | Max 50MB/upload, 5MB/image, whitelist MIME types |
| Error messages | Opaque (không expose internal paths, stack traces) |

---

## 9. Environment Variables

File: `.env` (xem `.env.example` để template đầy đủ)

### Bắt buộc

| Biến | Mô tả |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token |
| `ADMIN_TELEGRAM_ID` | Telegram user ID của admin |
| `GOOGLE_APPLICATION_CREDENTIALS` | Đường dẫn absolute đến GCP service account JSON |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID |

### Models (optional — defaults ổn định)

| Biến | Default | Mô tả |
|------|---------|-------|
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Vertex AI region |
| `MODEL_FLASH` | `gemini-2.5-flash` | Model nhẹ (query, ingest) |
| `MODEL_PRO` | `gemini-2.5-pro` | Model mạnh (extract, compile) |
| `MODEL_PRO_NEW` | `gemini-3.1-pro-preview` | Thế hệ mới, chưa enable |
| `MODEL_PRO_NEW_LOCATION` | `global` | Bắt buộc `global` cho 3.1 Pro |
| `USE_PRO_NEW` | `false` | Feature flag — bật sau khi xác nhận quota |

### Dual-Vote (optional)

| Biến | Default | Mô tả |
|------|---------|-------|
| `OPENAI_API_KEY` | — | `sk-proj-*` (OpenAI) hoặc `sk-or-v1-*` (OpenRouter) |
| `OPENAI_MODEL` | `gpt-5.4` | GPT model cho dual-vote |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Auto-detect từ key prefix |
| `DUAL_VOTE_ENABLED` | `false` | Bật dual-vote cross-validation |

### Cost & Workspace (optional)

| Biến | Default | Mô tả |
|------|---------|-------|
| `MAX_QUERY_COST_USD` | `0.01` | Alert khi 1 query vượt mức |
| `MONTHLY_BUDGET_USD` | `50` | Budget tháng (alert ngưỡng) |
| `WIKI_WORKSPACE` | `/home/openclaw/wiki` | Root workspace — **cập nhật khi migrate** |
| `WEB_PORT` | `3000` | Port web server |

---

## 10. Pipeline Skills

| # | Skill | Input | Output | Model | Trạng thái |
|---|-------|-------|--------|-------|-----------|
| 1 | `extract-claims` | `raw/*.md` | `claims/.drafts/` YAML | Gemini 2.5 Pro | ✅ Active |
| 2 | `compile-wiki` | `claims/approved/` | `wiki/products/` MD | Gemini 2.5 Pro | ✅ Active |
| 3 | `query-wiki` | Câu hỏi | Trả lời + sources | Gemini 2.5 Flash | ✅ Active |
| 4 | `build-snapshot` | `wiki/` | Versioned snapshot | None | ✅ Active |
| 5 | `ingest-image` | Screenshot | claims YAML | Gemini 2.5 Flash | ✅ Tested |
| 6 | `lint-wiki` | `wiki/products/` | Quality report | Gemini 2.5 Pro | ✅ Active |
| 7 | `ground-truth` | Excel SOT | Validation report | Gemini 2.5 Flash | ⚠️ Blocked |
| 8 | `crawl-source` | URL | `raw/*.md` | None | ⚠️ Blocked |
| 9 | `dual-vote` | Text pair | AGREE/PARTIAL/DISAGREE | Gemini + GPT | ✅ Active |
| 10 | `auto-file` | Raw files | Categorized claims | Gemini 2.5 Flash | 🔲 Disabled |
| 11 | `cross-link` | Wiki pages | Internal links | Gemini 2.5 Flash | 🔲 Disabled |
| 12 | `verify-claims` | Claims | Verification report | None | 🔲 Pending |
| 13 | `audit-wiki` | Wiki | Audit trail | None | 🔲 Pending |

> **⚠️ Blocked = Cloudflare blocks BKNS.vn** — `crawl-source` và `ground-truth` không tự động được. Workaround: upload DOCX/PDF thủ công qua Web UI.

Mỗi skill có:
- `skills/{name}/SKILL.md` — spec chi tiết
- `skills/{name}/scripts/` — code implementation

---

## 11. Telegram Bot Commands

File: `bot/wiki_bot.py` — polling mode, daemon bởi PM2.

| Command | Permission | Handler | Mô tả |
|---------|-----------|---------|-------|
| `/hoi [câu hỏi]` | Public | `handle_hoi()` | Query wiki (max 500 chars) |
| `/status` | Public | `handle_status()` | Build version, wiki files, claims count |
| `/help` | Public | `handle_help()` | Danh sách lệnh |
| `/them [URL]` | Admin | `handle_them()` | Crawl URL → raw/ (timeout 60s) |
| `/extract` | Admin | `handle_extract()` | Extract claims từ pending raw files |
| `/compile [category\|--all]` | Admin | `handle_compile()` | Compile wiki |
| `/build` | Admin | `handle_build()` | Tạo build snapshot |
| `/lint` | Admin | `handle_lint()` | Quality check wiki |

**Categories hợp lệ:** `hosting`, `vps`, `email`, `ssl`, `ten-mien`, `server`, `software`

**Workflow thêm tài liệu:**
```
/them [URL]  →  /extract  →  [review trên Web Portal]  →  /compile [category]  →  /build
```

---

## 12. Testing

### 12.1 Test Suite

```bash
# Chạy tất cả (33 tests, ~5-10 giây)
cd /home/openclaw/wiki
pytest tests/ -q

# Verbose
pytest tests/ -v
```

| File | Tests | Nội dung |
|------|-------|---------|
| `test_bot.py` | 13 | `_validate_url()`, `_safe_error()`, `handle_them()` |
| `test_pipeline_smoke.py` | 7 | Smoke: extract, compile, query, build |
| `test_markitdown_adapter.py` | 6 | Markitdown 15+ formats |
| `test_tools.py` | 5 | Tool utilities |
| `test_utils.py` | 2 | Config + logger |

### 12.2 Acceptance Criteria

| # | Criterion | Trạng thái |
|---|-----------|-----------|
| AC1 | 7/9 categories có wiki pages (other + uncategorized là stub) | ✅ |
| AC2 | Search trả về kết quả đúng | ✅ Tested "vps" → 25+ results |
| AC3 | Editor save không mất frontmatter | ✅ |
| AC4 | Bot `/hoi` trả lời trong <5s (với cache) | ✅ |
| AC5 | SEO hoàn toàn blocked | ✅ robots.txt + X-Robots-Tag |
| AC6 | 33 tests pass 100% | ✅ |

---

## 13. Cost Monitoring

### Log Format

```json
// logs/gemini-calls-YYYY-MM.jsonl
{
  "ts": "2026-04-15T10:30:00+07:00",
  "skill": "query-wiki",
  "action": "llm_call_cached",
  "model": "gemini-2.5-flash",
  "input_tokens": 45000,
  "cached_tokens": 42000,
  "output_tokens": 350,
  "cost_usd": 0.000287,
  "elapsed_ms": 1240
}
```

### Pricing (Vertex AI — tham khảo)

| Model | Input/1M | Output/1M |
|-------|----------|----------|
| `gemini-2.5-flash` | $0.075 | $0.30 |
| `gemini-2.5-pro` | $1.25 | $10.00 |
| `gemini-3.1-pro-preview` | $2.00 | $12.00 |

### Kiểm tra chi phí tháng

```bash
python3 -c "
import json
from pathlib import Path
from datetime import datetime
month = datetime.now().strftime('%Y-%m')
f = Path(f'logs/gemini-calls-{month}.jsonl')
if f.exists():
    lines = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    total = sum(l.get('cost_usd', 0) for l in lines)
    print(f'Total calls: {len(lines)}, Cost: \${total:.4f}')
"
```

---

## 14. Risks & Mitigations

| Risk | Impact | Trạng thái | Mitigation |
|------|--------|-----------|-----------|
| Gemini API downtime | Pipeline gián đoạn | Active | Retry 3x với exponential backoff, Telegram alert |
| Data loss khi edit | Mất nội dung | Active | Auto-backup trước mỗi save |
| Conflicting claims | Sai data trong wiki | Active | 25 conflicts trong `.review-queue/` — cần review thủ công |
| Token leak / auth | Truy cập trái phép | Active | .env không vào git, Nginx rate limit, Bearer token |
| Cloudflare blocks crawl | Không tự crawl BKNS.vn | Permanent | Upload thủ công DOCX/PDF qua Web UI |
| Wiki tăng token | Query chậm, tốn | Low risk hiện tại | 127K tokens hiện tại, xem xét tách nếu >400K |
| DUAL_VOTE_ENABLED=false | Dual-vote không active | Intended | Enable sau regression test, xem runbook |

---

## 15. Roadmap

### Pending (Backlog)

- [ ] Enable `DUAL_VOTE_ENABLED=true` — sau khi regression test pass đầy đủ
- [ ] Enable `USE_PRO_NEW=true` — sau khi xác nhận Gemini 3.1 Pro quota
- [ ] `auto-file` skill (Phase 2) — tự phân loại FAQ từ queries
- [ ] `cross-link` skill (Phase 2) — internal links giữa wiki pages
- [ ] `verify-claims` và `audit-wiki` — tích hợp vào pipeline chính
- [ ] Monitoring dashboard — cost + cache hit rate + query volume
- [ ] CSP nonce-based — khi TOAST UI Editor hỗ trợ

### Non-Scope (confirmed out)

- ❌ Multi-user auth / RBAC
- ❌ RAG / vector DB
- ❌ Public-facing API
- ❌ SQLite/PostgreSQL (flat-file YAML đủ cho scale hiện tại)

---

## 16. Dependencies

### Python (`requirements.txt`)

```
google-cloud-aiplatform>=1.40.0
python-telegram-bot>=20.0
pyyaml>=6.0
python-frontmatter>=1.0.0
markitdown[all]>=0.1.0
yt-dlp>=2024.1.0
openai>=1.0.0
sentence-transformers>=2.0.0
pytest>=7.0.0
```

### Node.js (`web/package.json`)

```
express, multer, helmet, cors, bcryptjs, uuid, express-rate-limit, dotenv
```

### Frontend CDN

- Toast UI Editor (WYSIWYG Markdown)
- Lucide Icons 0.344.0
- Marked.js 12.0.0

---

## Appendix A — Git History (tóm tắt)

```
5634238  feat(review): redesign dual-vote modal (fix + diff + traceability)
4bffd0f  feat(v1.1.0): dual-vote pipeline + markitdown + web portal + optimization
a4cfecc  docs: add v0.4 + v1.1.0 release documentation
0118a99  docs(release): add LICENSE, CONTRIBUTING, .env.example for public release
a1dc75b  feat(review): add bulk action endpoint + resolve-conflict
96e6a08  feat(ui): redesign portal — bit.ai-inspired light theme (later reverted)
1eb90c7  feat(review): add human-in-the-loop review queue tab
c4c8e79  feat(accuracy): add ground-truth Excel enrichment + verify/audit pipeline
d396b23  docs: add SPEC-wiki-system.md — full SDD
940ac66  feat(web): rebuild Wiki Admin Portal (sidebar tree, reader, Toast UI Editor)
```

---

*BKNS Agent Wiki SDD v3.0 — Cập nhật dựa trên code thực tế Build v0.6 (2026-04-16)*

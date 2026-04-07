# BKNS Agent Wiki — System Design Document (SDD)

> **Version:** 2.0.0  
> **Updated:** 2026-04-07  
> **Author:** AI Agent + Admin  
> **Status:** Production (Active)

---

## 1. Executive Summary

**BKNS Agent Wiki** là hệ thống knowledge base nội bộ tự động, chuyên thu thập, trích xuất, kiểm duyệt, và biên soạn thông tin sản phẩm/dịch vụ của BKNS thành wiki có cấu trúc. Hệ thống phục vụ 2 đối tượng chính:

1. **Con người** — Nhân viên chỉnh sửa, bổ sung thông tin sản phẩm qua Web Portal
2. **AI Agent** — Tự động cào bài viết, trích xuất claims, biên soạn wiki, và xuất dữ liệu JSON cho chatbot/tư vấn

### Metrics Hiện Tại
| Metric | Giá trị |
|---|---|
| Wiki pages | 97 |
| Categories | 9 (email, hosting, server, software, ssl, ten-mien, vps, other, uncategorized) |
| Claims extracted | 2,991 |
| Raw source files | 329 |
| Pipeline skills | 10 |
| Bot commands | 7 |
| Daily pipeline | 6:00 AM (cron) |

---

## 2. Problem Statement

### Bối cảnh
BKNS có hàng trăm sản phẩm/dịch vụ (VPS, hosting, SSL, domain, email, server…). Thông tin phân tán trên website, landing pages, docs nội bộ, và kiến thức nhân viên. Không có single source of truth dành cho:
- AI chatbot cần data chuẩn hóa để tư vấn
- Nhân viên support cần tra cứu nhanh
- Pipeline tự động cần update liên tục

### Giải pháp
Pipeline tự động: **Raw → Extract → Approve → Compile → Wiki** + Web Admin Portal cho human editing.

---

## 3. Goals & Non-Goals

### Goals
| # | Goal | Metric |
|---|---|---|
| G1 | Single source of truth cho toàn bộ sản phẩm BKNS | 100% categories có wiki |
| G2 | AI có thể đọc/trích xuất structured data | JSON export API, frontmatter YAML |
| G3 | Con người chỉnh sửa nhanh qua web | WYSIWYG editor, ≤3 clicks to edit |
| G4 | Pipeline tự động chạy daily | 6AM cron, Telegram notifications |
| G5 | Dữ liệu có audit trail | Changelog, backup per edit, claim tracing |

### Non-Goals
- ❌ SEO / public-facing wiki (internal only, noindex)
- ❌ Multi-user auth / role-based access (single admin token)
- ❌ Real-time collaboration (one editor at a time)
- ❌ Version control UI (dùng git + backups)

---

## 4. Architecture

### 4.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        BKNS Agent Wiki                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Nguồn   │    │  Extract  │    │ Compile  │    │   Wiki   │  │
│  │  Dữ Liệu │───▶│  Claims   │───▶│  Pages   │───▶│  Output  │  │
│  └──────────┘    └───────────┘    └──────────┘    └──────────┘  │
│   raw/            claims/          wiki/.drafts/    wiki/products│
│   - crawl/        - .drafts/       (staging)       (published)  │
│   - manual/       - approved/                                    │
│                                                                  │
│  ┌──────────┐    ┌───────────┐    ┌──────────┐                  │
│  │ Telegram │    │   Web     │    │   AI     │                  │
│  │   Bot    │    │  Portal   │    │  Export  │                  │
│  └──────────┘    └───────────┘    └──────────┘                  │
│   bot/            web/             /api/wiki/export              │
│   PM2: bkns-      PM2: wiki-                                    │
│   wiki-bot        portal                                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Data Pipeline Flow

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Sources  │────▶│ Extract  │────▶│ Approve  │────▶│ Compile  │────▶│ Publish  │
│          │     │          │     │          │     │          │     │          │
│ Web crawl│     │ Gemini   │     │ Auto/    │     │ Gemini   │     │ wiki/    │
│ Manual   │     │ Pro API  │     │ Manual   │     │ Pro API  │     │ products/│
│ Upload   │     │          │     │ review   │     │          │     │          │
└─────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
  329 files       2,991 claims    Conflict detect   97 pages       Flat-file MD
```

### 4.3 Component Diagram

```
bkns-wiki/
├── lib/                    # Python shared library
│   ├── config.py           # All paths, constants, env vars
│   ├── gemini.py           # Gemini API wrapper (rate limit, retry)
│   ├── logger.py           # Structured audit logging
│   ├── telegram.py         # Bot notification (notify_skill, notify_error)
│   └── utils.py            # YAML/MD parsing, claim ID generation
│
├── skills/                 # Pipeline skills (10 skills)
│   ├── extract-claims/     # Raw → Claims (Gemini extraction)
│   ├── compile-wiki/       # Claims → Wiki pages (multi-page arch)
│   ├── lint-wiki/          # Wiki quality checking
│   ├── crawl-source/       # Web crawling
│   ├── auto-file/          # Auto-categorization
│   ├── build-snapshot/     # Versioned snapshots
│   ├── cross-link/         # Internal linking
│   ├── ground-truth/       # Excel SOT comparison
│   ├── ingest-image/       # Image processing
│   └── query-wiki/         # Answer questions from wiki
│
├── tools/                  # Utility scripts
│   ├── batch_pipeline.py   # Full pipeline orchestration
│   ├── run_pipeline.sh     # Cron wrapper
│   ├── generate_web_crawl_raw.py  # Web crawler
│   ├── convert_manual.py   # Manual doc conversion
│   ├── recategorize_claims.py     # Entity-based routing
│   ├── approve_and_compile.py     # Quick approve+compile
│   ├── migrate_claim_ids.py       # ID migration utility
│   ├── rotate_logs.py      # Log rotation (weekly cron)
│   └── check_overnight.sh  # Pipeline health check
│
├── bot/                    # Telegram bot (Python)
│   └── wiki_bot.py         # 7 commands: hoi, status, build, extract, compile, lint, help
│
├── web/                    # Web Admin Portal (Node.js/Express)
│   ├── server.js           # Express app, middleware, routes
│   ├── middleware/auth.js   # Bearer token auth, bcrypt login
│   ├── routes/
│   │   ├── wiki.js         # Wiki CRUD, tree, search, changelog, export
│   │   ├── upload.js       # File upload handler
│   │   ├── files.js        # File browser/management
│   │   ├── trigger.js      # Pipeline trigger API
│   │   └── status.js       # System status API
│   ├── lib/pipeline-runner.js  # Pipeline execution from web
│   └── public/
│       ├── index.html      # SPA frontend (4-tab layout)
│       ├── style.css       # Design system (dark theme, tokens)
│       ├── app.js          # Client-side SPA logic
│       ├── favicon.png     # Custom BKNS Wiki logo
│       └── robots.txt      # SEO blocking
│
├── raw/                    # Source documents (329 files)
│   ├── crawl/              # Web-crawled Markdown
│   └── manual/             # Manually uploaded docs
│
├── claims/                 # Extracted claims (2,991)
│   ├── .drafts/            # Pending review
│   │   └── products/       # By category → claim YAML files
│   ├── approved/           # Approved claims
│   └── .cache/             # SHA256 incremental cache
│
├── wiki/                   # Published wiki output (97 pages)
│   ├── products/           # 9 categories
│   │   ├── vps/            # 25 pages (tong-quan, bang-gia, chinh-sach, san-pham/...)
│   │   ├── hosting/        # 9 pages
│   │   ├── email/          # 15 pages
│   │   ├── server/         # 15 pages
│   │   ├── ssl/            # 9 pages
│   │   ├── ten-mien/       # 12 pages
│   │   ├── software/       # 10 pages
│   │   ├── other/          # 1 page
│   │   └── uncategorized/  # 1 page
│   ├── .drafts/            # Pre-review compiled pages
│   └── assets/images/      # Editor-uploaded images
│
├── logs/                   # Application logs
├── .env                    # Environment configuration
├── GEMINI.md               # AI rules (APEX v11.0)
└── docs/                   # Documentation
    └── SPEC-wiki-system.md # This file
```

### 4.4 AI Components

| Component | Model | Purpose | Cost |
|---|---|---|---|
| Extract Claims | `gemini-2.0-flash` | Raw text → structured claims YAML | ~$0.008/file |
| Compile Wiki | `gemini-2.0-pro` | Claims → Markdown wiki pages | ~$0.035/page |
| Query Wiki | `gemini-2.0-flash` | Answer questions from wiki context | per-query |
| Self-Review | `gemini-2.0-pro` | Verify compiled page quality | included in compile |

---

## 5. Implementation Details

### 5.1 Data Model — Claim

```yaml
# Single claim in claims/.drafts/products/{category}/
claim_id: "clm_bkns_cloud_vps_amd_price"
entity_id: "bkns.cloud_vps.amd_epyc"
category: "products/vps"
attribute: "price"
value: "Từ 89.000đ/tháng cho VPS AMD 1C-1G"
source: "https://www.bkns.vn/may-chu-ao-vps.html"
confidence: 0.9
extracted_at: "2026-04-07T05:30:00Z"
review_state: "draft"          # draft | approved | rejected | conflict
```

### 5.2 Data Model — Wiki Page Frontmatter

```yaml
# Every wiki page has YAML frontmatter
page_id: wiki.products.vps.tong-quan
title: "Cloud VPS BKNS — Tổng Quan Chi Tiết"
category: products/vps
updated: "2026-04-07"
review_state: approved
claims_used: 93
compile_cost_usd: 0.0354
self_review: pass              # pass | fail
corrections: 0
approved_at: "2026-04-07T12:53:58Z"
```

### 5.3 Sub-Page Architecture (per category)

| # | File | Purpose |
|---|---|---|
| 1 | `tong-quan.md` | Overview (index with ToC links) |
| 2 | `bang-gia.md` | Pricing tables |
| 3 | `thong-so.md` | Technical specifications |
| 4 | `chinh-sach.md` | Policies (SLA, support, billing) |
| 5 | `tinh-nang.md` | Feature descriptions |
| 6 | `huong-dan.md` | How-to guides |
| 7 | `so-sanh.md` | Product comparisons |
| 8 | `cau-hoi-thuong-gap.md` | FAQ |
| 9 | `san-pham/*.md` | Per-product detail pages |

### 5.4 File Naming Conventions

```
# Claims: clm_{brand}_{product}_{attribute}
clm_bkns_cloud_vps_amd_price.yaml

# Wiki pages: {slug}.md (Vietnamese slug, lowercase, hyphens)
tong-quan.md, bang-gia.md, cloud-vps-amd.md

# Raw files: {source}_{entity}_{date}.md
bkns_vps_20260407.md
```

---

## 6. API Design

### 6.1 Authentication
- **Method:** Bearer token
- **Login:** `POST /api/login` — body: `{ password }` → returns `{ token }`
- **All other APIs:** `Authorization: Bearer <ADMIN_TOKEN>`

### 6.2 Wiki APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/wiki/tree` | Category tree with pages + products |
| `GET` | `/api/wiki/search?q=` | Full-text search (97 pages indexed) |
| `GET` | `/api/wiki/changelog?limit=` | Edit history |
| `GET` | `/api/wiki/export` | Bulk JSON export for AI consumption |
| `GET` | `/api/wiki/:category/:page` | Read page content |
| `PUT` | `/api/wiki/:category/:page` | Update page (auto-backup) |
| `POST` | `/api/wiki/:category/:page` | Create new page |
| `GET` | `/api/wiki/:category/:page/backups` | List backups |

### 6.3 Upload & Pipeline APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/upload` | Upload files (multipart, max 50MB/file) |
| `POST` | `/api/upload/image` | Upload editor images (max 5MB) |
| `GET` | `/api/files?source=&page=&limit=` | File browser |
| `DELETE` | `/api/files/:id` | Delete file |
| `GET` | `/api/files/:id/content` | View file content |
| `POST` | `/api/trigger` | Trigger pipeline (full/extract/compile) |
| `GET` | `/api/status` | System status + pipeline state |

### 6.4 AI Export Format

```json
// GET /api/wiki/export
{
  "exported_at": "2026-04-07T07:00:00Z",
  "total_pages": 97,
  "categories": [
    {
      "category": "vps",
      "label": "VPS",
      "pages": [
        {
          "page": "tong-quan",
          "title": "Cloud VPS BKNS — Tổng Quan",
          "content": "# Full markdown content...",
          "frontmatter": { "claims_used": 93, "updated": "2026-04-07" }
        }
      ]
    }
  ]
}
```

---

## 7. UI/UX Design

### 7.1 Web Portal Layout

```
┌─────────────────────────────────────────────┐
│  🔲 BKNS Wiki    [Wiki][Dash][Upload][Pipe] │  ← Header + Nav tabs
├──────────┬──────────────────────┬────────────┤
│ Sidebar  │     Wiki Content     │    ToC     │  ← Wiki tab (default)
│          │                      │            │
│ 🔍 Search│  Breadcrumb + Mode   │  Mục lục  │
│          │  ─────────────────   │            │
│ 📁 VPS   │  # Page Title       │  • H2      │
│   📄 Tổng│  Content rendered    │  • H3      │
│   📄 Giá │  from Markdown...    │  • H3      │
│   📄 Spec│                      │            │
│   📦 Products                   │            │
│ 📁 Hosting                      │            │
│ 📁 SSL   │                      │            │
│          │                      │            │
│ [+New]   │                      │            │
│ [↻Refresh]                      │            │
└──────────┴──────────────────────┴────────────┘
```

### 7.2 Design System

| Token | Value |
|---|---|
| Theme | Dark (bg: `#0a1628`, text: `#f1f5f9`) |
| Primary | Cyan gradient (`#06b6d4` → `#0891b2`) |
| Accent | Emerald (`#10b981`) |
| Fonts | DM Sans (body), Space Grotesk (headings), JetBrains Mono (code) |
| Border | `rgba(34, 211, 238, 0.15)` |
| Glass | `blur(16px)`, `rgba(17, 29, 51, 0.5)` |
| Radius | `sm: 0.375rem`, `md: 0.5rem`, `lg: 0.75rem`, `xl: 1rem` |

### 7.3 Editor

- **Toast UI Editor** (CDN) — WYSIWYG + Markdown dual mode
- Image upload: drag & drop → `/api/upload/image` → `/wiki-assets/{filename}`
- Keyboard: `Ctrl+S` save, `Ctrl+K` search
- Frontmatter preservation: strip on edit, re-attach on save

---

## 8. Infrastructure

### 8.1 Server Stack

| Layer | Technology | Config |
|---|---|---|
| OS | Ubuntu Linux (VPS) | |
| Reverse proxy | Nginx | SSL (Let's Encrypt), rate limiting |
| Web server | Node.js + Express | Port 3000, PM2 cluster mode |
| Bot | Python 3 | PM2 fork mode |
| AI | Google Cloud Vertex AI | Gemini 2.0 Flash + Pro |
| DNS | upload.trieuphu.biz | Cloudflare/Let's Encrypt |
| Process manager | PM2 | Auto-restart, log rotation |

### 8.2 PM2 Processes

| Name | Type | Script | Mode |
|---|---|---|---|
| `wiki-portal` | Node.js | `web/server.js` | Cluster |
| `bkns-wiki-bot` | Python | `bot/wiki_bot.py` | Fork |

### 8.3 Cron Jobs

| Schedule | Task | Script |
|---|---|---|
| `0 6 * * *` | Daily full pipeline | `tools/run_pipeline.sh` |
| `0 3 * * 0` | Log rotation (Sunday) | `tools/rotate_logs.py` |
| `0 7 * * 1` | Wiki linting (Monday) | `skills/lint-wiki/scripts/lint.py` |

### 8.4 Security

| Feature | Implementation |
|---|---|
| HTTPS | TLS 1.2/1.3 via Let's Encrypt + Nginx |
| Auth | Bearer token (`ADMIN_TOKEN`), bcrypt password |
| Rate limiting | Nginx zones (10r/s API, 5r/m login, 2r/s upload) + Express rate-limit |
| CSP | Strict; allows Toast UI CDN only |
| SEO blocking | `robots.txt` + `X-Robots-Tag: noindex, nofollow` on all responses |
| Headers | HSTS, X-Frame-Options DENY, X-Content-Type-Options, Referrer-Policy |
| File limits | 50MB/file upload, 5MB/image, allowed types whitelist |

### 8.5 Nginx Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=wiki_api:10m    rate=10r/s;   # API general
limit_req_zone $binary_remote_addr zone=wiki_login:10m   rate=5r/m;    # Login (strict)
limit_req_zone $binary_remote_addr zone=wiki_upload:10m  rate=2r/s;    # File upload
```

---

## 9. Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP service account JSON | ✅ |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | ✅ |
| `GOOGLE_CLOUD_LOCATION` | GCP region | ✅ |
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | ✅ |
| `ADMIN_TELEGRAM_ID` | Admin Telegram user ID | ✅ |
| `MODEL_FLASH` | Gemini Flash model name | ✅ |
| `MODEL_PRO` | Gemini Pro model name | ✅ |
| `WIKI_WORKSPACE` | Root workspace path | ✅ |
| `WEB_PORT` | Web portal port (default: 3000) | |
| `ADMIN_TOKEN` | Bearer token for API auth | ✅ |
| `ADMIN_PASSWORD` | Login password (plain text fallback) | ✅ |

---

## 10. Pipeline Skills (10)

| # | Skill | Input | Output | AI Model |
|---|---|---|---|---|
| 1 | `extract-claims` | `raw/` files | `claims/.drafts/` YAML | Gemini Flash |
| 2 | `compile-wiki` | `claims/approved/` | `wiki/products/` MD pages | Gemini Pro |
| 3 | `lint-wiki` | `wiki/products/` | Lint report | — |
| 4 | `crawl-source` | URLs | `raw/crawl/` MD files | — |
| 5 | `auto-file` | Raw files | Categorized claims | Gemini Flash |
| 6 | `build-snapshot` | `wiki/products/` | Versioned snapshots | — |
| 7 | `cross-link` | Wiki pages | Internal links added | Gemini Flash |
| 8 | `ground-truth` | Excel SOT | Validation report | — |
| 9 | `ingest-image` | Images | Text extraction | Gemini Flash |
| 10 | `query-wiki` | Question | Answer from wiki | Gemini Flash |

### Pipeline Execution Order

```
Daily 6AM cron:
  1. batch_pipeline.py full
     ├── convert_manual.py     (docx/pdf → markdown)
     ├── extract.py            (raw → claims, SHA256 cache)
     ├── approve               (auto-approve if no conflict)
     └── compile.py --all      (claims → wiki pages)
```

---

## 11. Telegram Bot Commands

| Command | Handler | Description |
|---|---|---|
| `/hoi <question>` | `handle_hoi()` | Query wiki knowledge base |
| `/status` | `handle_status()` | System status (pages, claims, pipeline) |
| `/build` | `handle_build()` | Trigger full pipeline |
| `/extract` | `handle_extract()` | Run extraction only |
| `/compile <cat>` | `handle_compile()` | Compile specific category |
| `/lint` | `handle_lint()` | Run wiki quality check |
| `/help` | `handle_help()` | Show available commands |

---

## 12. Testing & Verification

### Automated
- Pipeline self-review: Gemini checks compiled pages for accuracy
- Lint skill: validates frontmatter, broken links, empty pages
- SHA256 cache: verifies file integrity before extraction

### Manual
- Web portal visual testing at https://upload.trieuphu.biz/
- API endpoint testing via curl
- Telegram bot command testing

### Acceptance Criteria
| # | Criterion | Status |
|---|---|---|
| AC1 | All 9 categories have wiki pages | ✅ 97 pages |
| AC2 | Search returns relevant results | ✅ Tested "vps" → 20 results |
| AC3 | Editor saves without data loss | ✅ Frontmatter preserved |
| AC4 | Pipeline runs daily without errors | ✅ Cron configured |
| AC5 | Bot responds to /hoi queries | ✅ Tested |
| AC6 | SEO fully blocked | ✅ robots.txt + X-Robots-Tag |

---

## 13. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Gemini API downtime | Pipeline fails | Retry logic in `lib/gemini.py`, Telegram error alerts |
| Data loss during edit | Content lost | Auto-backup before every save in `wiki/.drafts/backups/` |
| Conflicting claims | Wrong data in wiki | Conflict detection in extract, human review gate |
| Token leak | Unauthorized access | `.env` not in git, Nginx rate limiting |
| Large wiki growth | Slow search | In-memory index rebuild, consider SQLite FTS if >1000 pages |

---

## 14. Future Roadmap

### v2.1 — Short Term
- [ ] Multi-user auth (JWT + roles: admin, editor, viewer)
- [ ] Real-time search (debounced, with relevance scoring)
- [ ] Mobile-responsive sidebar (hamburger menu)
- [ ] Page revision history viewer in UI

### v2.2 — Medium Term
- [ ] NotebookLM integration for quality assurance
- [ ] Automated cross-linking between wiki pages
- [ ] Excel SOT comparison dashboard
- [ ] Bulk CSV/JSON import for claims

### v3.0 — Long Term
- [ ] AI chatbot widget (powered by query-wiki skill)
- [ ] Webhook for external integrations
- [ ] Multi-tenant support (multiple wiki instances)
- [ ] SQLite/PostgreSQL for claims storage (if >10k claims)

---

## 15. Appendix

### A. Git History

```
940ac66  feat(web): rebuild Wiki Admin Portal — sidebar tree, reader, Toast UI Editor
ca3b9eb  learn: add L006 — Helmet CSP blocks inline onclick handlers
e5b1df1  fix(portal): replace inline onclick with event delegation for CSP compliance  
1a45d03  feat(wiki): web-crawl 34 sản phẩm + extract 401 claims + compile 7 wiki pages
4dd678f  feat(production): BKNS Wiki MVP v0.3 — full production data commit
d5db360  feat(foundation): BKNS Agent Wiki — 10 skills MVP
```

### B. Dependency Chart

```
Node.js (web/):
  express ^4.21.0, multer ^1.4.5, cors ^2.8.5, dotenv ^16.4.5
  uuid ^9.0.1, bcryptjs ^2.4.3, express-rate-limit ^7.4.1, helmet ^7.1.0

CDN (frontend):
  Toast UI Editor (latest), Lucide Icons 0.344.0, Marked.js 12.0.0

Python (pipeline):
  google-cloud-aiplatform, python-telegram-bot, pyyaml, python-frontmatter
```

### C. Related Docs
- [GEMINI.md](../GEMINI.md) — AI rules and skill system (APEX v11.0)
- [trienkhai/01-setup-infra.md](../trienkhai/01-setup-infra.md) — Infrastructure setup guide

---

*Document auto-generated by APEX Spec Skill. Last verified: 2026-04-07T07:48Z*

# Cấu Trúc Thư Mục + Quy Tắc Phân Quyền

---

## Cây Thư Mục Đầy Đủ

```
/home/openclaw/wiki/
│
├── .env                          ← Secrets — TUYỆT ĐỐI KHÔNG commit
├── .gitignore                    ← Bao gồm: .env, site/, __pycache__/
├── .gitattributes                ← Git LFS cho assets/evidence/**
├── agents.yaml                   ← OpenClaw skill registration
├── mkdocs.yml                    ← Wiki viewer config
│
├── raw/                          ← [BOT GHI TỰ DO] Dữ liệu thô
│   ├── website-crawl/            ← Từ crawl-source (HTML → Markdown)
│   │   └── {slug}-{YYYY-MM-DD}.md  ← Frontmatter + content
│   └── manual/                   ← Text paste thủ công từ admin
│
├── claims/                       ← Source of Truth (facts đã trích xuất)
│   ├── registry.yaml             ← Master index mọi claims
│   ├── .drafts/                  ← [BOT GHI TỰ DO] Chờ review
│   │   └── products/{category}/
│   │       ├── {claim_id}.yaml
│   │       └── {claim_id}.jsonl  ← Audit trace
│   └── products/                 ← [CHỈ SAU REVIEW] Claims approved
│       ├── hosting/
│       ├── vps/
│       ├── ten-mien/
│       ├── email/
│       └── ssl/
│
├── entities/                     ← Entity registry (sản phẩm, công ty)
│   └── registry.yaml
│
├── sources/                      ← Source registry (URLs đã crawl)
│   └── registry.yaml
│
├── wiki/                         ← Wiki compiled (output cuối cùng)
│   ├── index.md                  ← Trang chủ + nav
│   ├── .drafts/                  ← [BOT GHI TỰ DO] Chờ /duyet
│   │   └── {category}/
│   │       └── draft-{datetime}.md
│   ├── company/
│   │   └── gioi-thieu.md
│   ├── products/
│   │   ├── hosting/
│   │   │   ├── tong-quan.md      ← Tổng quan + bảng giá
│   │   │   └── chi-tiet.md       ← Chi tiết kỹ thuật (nếu có)
│   │   ├── vps/
│   │   ├── ten-mien/
│   │   ├── email/
│   │   └── ssl/
│   ├── support/
│   │   └── lien-he.md
│   ├── faq/                      ← FAQ từ auto-file
│   │   ├── hosting-faq.md
│   │   └── vps-faq.md
│   └── onboarding/               ← Phase 3
│       ├── nhan-vien.md
│       ├── khach-hang.md
│       └── team-ky-thuat.md
│
├── build/                        ← Build management
│   ├── active-build.yaml         ← Pointer build hiện tại (bot đọc khi start)
│   ├── manifests/                ← Lịch sử build
│   │   └── build-{date}-{seq}.yaml
│   └── snapshots/                ← Build snapshots (backward compat)
│
├── assets/
│   ├── evidence/                 ← [Git LFS] Ảnh gốc full-res
│   │   └── price-screens/
│   │       └── {name}-original.{ext}
│   └── images/                   ← Thumbnails compressed
│       └── {name}-thumb.{ext}
│
├── logs/                         ← [BOT GHI TỰ DO] Tất cả audit logs
│   ├── query-{YYYY-MM-DD}.jsonl  ← Query traces (cost, cache metrics)
│   ├── intake/                   ← crawl-source logs
│   │   └── {YYYY-MM-DD}.jsonl
│   ├── errors/                   ← Lỗi từ mọi skills
│   │   └── {YYYY-MM-DD}.jsonl
│   ├── lint/                     ← lint-wiki reports
│   │   └── report-{date}.md
│   ├── ground-truth/             ← ground-truth reports
│   │   └── report-{date}.md
│   └── approvals-{YYYY-MM}.jsonl ← /duyet history
│
├── skills/                       ← OpenClaw skill definitions
│   ├── query-wiki/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── query.py          ← Core query logic
│   │       └── test_query.py     ← 20 câu hỏi test
│   ├── ingest-raw/
│   │   ├── SKILL.md
│   │   └── scripts/ingest.py
│   ├── compile-wiki/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── compile.py        ← compile + self-review
│   │       └── review.py         ← /duyet + /xem-draft
│   ├── ingest-image/             ← Phase 2
│   │   ├── SKILL.md
│   │   └── scripts/image_ingest.py
│   ├── lint-wiki/                ← Phase 2
│   │   ├── SKILL.md
│   │   └── scripts/lint.py
│   └── ground-truth/             ← Phase 2
│       ├── SKILL.md
│       └── scripts/ground_truth.py
│
└── tools/                        ← Setup scripts (chạy một lần)
    ├── crawl_bkns.py             ← Batch crawl ban đầu
    ├── extract_claims.py         ← Batch extract ban đầu
    └── compile_wiki_manual.py    ← Compile thủ công Phase 0.5
```

---

## Quy Tắc Phân Quyền Ghi File

### Ma Trận Quyền

| Thư mục | Bot | Admin | Ghi chú |
|---------|-----|-------|---------|
| `raw/` | ✅ Tự do | ✅ | crawl-source, ingest-raw, ingest-image |
| `claims/.drafts/` | ✅ Tự do | ✅ | extract-claims output |
| `claims/approved/` | ❌ KHÔNG | ✅ | Chỉ sau admin review |
| `wiki/.drafts/` | ✅ Tự do | ✅ | compile-wiki, auto-file candidates |
| `wiki/` (ngoài .drafts) | ❌ KHÔNG | ✅ | Chỉ sau `/duyet` |
| `logs/` | ✅ Tự do | ✅ | Mọi skills đều log |
| `assets/evidence/` | ✅ Tự do | ✅ | ingest-image lưu ảnh gốc |
| `assets/images/` | ✅ Tự do | ✅ | ingest-image lưu thumbnail |
| `build/active-build.yaml` | ✅ Sau /duyet | ✅ | build-snapshot cập nhật |
| `.env` | ❌ KHÔNG | ✅ Chỉ đọc | Tạo thủ công trên server |

---

## Schema Frontmatter Chuẩn

### raw/ files
```yaml
---
source_url: https://bkns.vn/hosting
crawled_at: 2026-04-04T10:00:00+07:00
content_type: webpage                 # webpage | image | manual
domain: bkns.vn
page_title: "Hosting BKNS"
content_hash: sha256:abc123...
word_count: 1523
status: pending_extract               # pending_extract | extracted | compiled
suggested_category: products/hosting
crawl_method: http_get                # http_get | vision | manual
---
```

### claims/ files
```yaml
---
claim_id: CLM-HOST-BKCP01-PRICE-20260404
entity_id: product.hosting.bkcp01
attribute: monthly_price              # pricing | specs | policy | contact | description
value: 26000
unit: VND
qualifiers:
  billing_cycle: month
  tax_included: unknown
source_ids:
  - SRC-BKNS-WEB-HOSTING
observed_at: "2026-04-04T10:30:00+07:00"
valid_from: "2026-04-04"
confidence: high                      # high | medium | low
review_state: drafted                 # drafted | approved | superseded | rejected
risk_class: high                      # high (giá/contact) | medium | low
compiler_note: "Trích từ bảng giá: 'BKCP01 - 26.000đ/tháng'"
---
```

### wiki/ files
```yaml
---
page_id: wiki.products.hosting.tong-quan
title: "Hosting BKNS — Tổng Quan & Bảng Giá"
category: hosting                     # hosting|vps|ten-mien|email|ssl|company|support|faq
compiled_from_claims:
  - CLM-HOST-BKCP01-PRICE-20260404
updated: 2026-04-04
review_state: approved               # draft | approved
sensitivity: high                    # high (có pricing) | low
approved_by: phamduytam
approved_at: "2026-04-04T12:00:00+07:00"
---
```

---

## Naming Conventions

```
raw/website-crawl/{slug}-{YYYY-MM-DD}.md
  → hosting-2026-04-04.md

claims/products/{category}/{claim_id_lowercase}.yaml
  → claims/products/hosting/clm_host_bkcp01_price_20260404.yaml

wiki/.drafts/{category}/draft-{YYYYMMDD-HHMMSS}.md
  → wiki/.drafts/products/hosting/draft-20260404-103045.md

wiki/{path}/{slug}.md
  → wiki/products/hosting/tong-quan.md

logs/query-{YYYY-MM-DD}.jsonl
  → logs/query-2026-04-04.jsonl

build/manifests/build-{YYYY-MM-DD}-{seq:02d}.yaml
  → build/manifests/build-2026-04-04-01.yaml
```

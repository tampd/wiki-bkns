# Skill 1: crawl-source

> **Phase:** 0.5 | **Model:** Script Python ($0) | **Trigger:** `/them [URL]` hoặc batch

---

## SKILL.md

```yaml
---
name: crawl-source
description: >
  Thu thập nội dung từ URL (chủ yếu bkns.vn) → lưu raw/website-crawl/ với metadata đầy đủ.
  Validate URL, check duplicate 24h, hash content để tránh crawl lại khi không đổi.
  KHÔNG dùng LLM — chỉ crawl, clean HTML, lưu Markdown.
  Trigger: /them [URL] hoặc batch crawl ban đầu.
version: "1.0"
phase: "0.5"
model: null
admin_only: true
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: [python3]
      install:
        uv: "requests beautifulsoup4 html2text pyyaml"
triggers:
  - command: /them
    arg_pattern: "https?://.+"
---
```

---

## Workflow

```
BƯỚC 1: Nhận + Validate URL
  ├─ Scheme phải là http/https → lỗi nếu không
  ├─ Nếu domain ≠ bkns.vn → CẢNH BÁO admin, hỏi tiếp tục?
  └─ Nếu đã crawl trong 24h → SKIP, báo "Đã crawl gần đây"

BƯỚC 2: HTTP GET
  ├─ User-Agent: BKNSWikiBot/1.0 (+https://bkns.vn)
  ├─ Timeout: 30s | Retry: 1 lần
  ├─ HTTP error → BÁO LỖI Telegram + log
  └─ BeautifulSoup parse, loại bỏ: nav, footer, script, style, aside

BƯỚC 3: Convert → Markdown
  ├─ html2text, body_width=0 (không wrap)
  ├─ SHA256 hash content
  └─ So sánh hash vs file cũ cùng slug → SKIP nếu không đổi

BƯỚC 4: Lưu raw/website-crawl/{slug}-{YYYY-MM-DD}.md
  ├─ Frontmatter đầy đủ (xem schema bên dưới)
  └─ Nội dung Markdown sau frontmatter

BƯỚC 5: Cập nhật sources/registry.yaml
  ├─ Thêm hoặc update entry
  └─ Ghi log: logs/intake/{YYYY-MM-DD}.jsonl

BƯỚC 6: Báo admin Telegram
  └─ "✅ Đã lưu [URL] → raw/website-crawl/{filename}
      ~{word_count} từ | Category: {category}
      Gõ /extract để trích claims."
```

---

## Output: raw/website-crawl/{slug}-{YYYY-MM-DD}.md

```yaml
---
source_url: https://bkns.vn/hosting
crawled_at: 2026-04-04T10:00:00+07:00
content_type: webpage
domain: bkns.vn
page_title: "Hosting BKNS - Giải pháp hosting tốt nhất"
content_hash: sha256:abc123...
word_count: 1523
status: pending_extract
suggested_category: products/hosting
crawl_method: http_get
---

[Nội dung Markdown]
```

---

## sources/registry.yaml Entry

```yaml
- source_id: SRC-BKNS-WEB-HOSTING
  type: official_product_page
  url: https://bkns.vn/hosting
  authority_level: 3
  freshness_sla_days: 7
  last_crawled: 2026-04-04
  raw_file: raw/website-crawl/hosting-2026-04-04.md
  hash: sha256:abc123...
```

---

## Category Auto-Detection

```python
CATEGORY_MAP = {
    "hosting":   "products/hosting",
    "vps":       "products/vps",
    "ten-mien":  "products/ten-mien",
    "domain":    "products/ten-mien",
    "email":     "products/email",
    "ssl":       "products/ssl",
    "gioi-thieu":"company",
    "lien-he":   "support",
    "ho-tro":    "support",
    "chinh-sach":"policies",
}
# Nếu không match → "uncategorized"
```

---

## Error Handling

| Lỗi | Hành động | Telegram |
|-----|----------|----------|
| HTTP 404/500 | Log, skip | ❌ crawl-source: Không truy cập được [URL] (HTTP {code}) |
| Timeout >30s | Retry 1 lần | ⏱️ crawl-source: Timeout [URL] |
| Content trống | Skip, cảnh báo | ⚠️ crawl-source: Trang [URL] không có nội dung |
| Hash trùng | Skip im lặng | — |
| URL ngoài bkns.vn | Hỏi admin | ⚠️ crawl-source: URL ngoài bkns.vn, tiếp tục? |

---

## Batch Crawl Ban Đầu (Phase 0.5)

```bash
# 5 trang ưu tiên crawl đầu tiên
python3 tools/crawl_bkns.py
# hoặc
python3 scripts/crawl.py \
  https://bkns.vn \
  https://bkns.vn/hosting \
  https://bkns.vn/ten-mien \
  https://bkns.vn/vps \
  https://bkns.vn/lien-he
```

> ⚠️ Nếu bkns.vn có Cloudflare → dùng playwright headless hoặc paste thủ công vào `raw/manual/`

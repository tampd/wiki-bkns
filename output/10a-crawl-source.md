# Skill 1: crawl-source — Thu Thập Dữ Liệu Từ bkns.vn

> **Phase:** 0.5 | **Model:** Không cần LLM (Python script) | **Cost:** $0
> **Triết lý Karpathy:** "Index source documents into a raw/ directory"

---

## SKILL.md

```yaml
---
name: crawl-source
description: >
  Thu thập nội dung từ URL (chủ yếu bkns.vn) và lưu vào raw/ với metadata đầy đủ.
  Trigger khi admin gửi /them [URL] hoặc chạy batch crawl ban đầu.
  KHÔNG dùng LLM — chỉ crawl, clean HTML, lưu Markdown.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - python3
      install:
        uv: "requests beautifulsoup4 html2text"
---
```

## Khi Nào Trigger

- Admin gửi `/them [URL]` trên Telegram
- Batch crawl lần đầu (Phase 0.5 setup)
- Cron ground-truth re-crawl (Phase 1+)

## Workflow Chi Tiết

```
BƯỚC 1: Nhận URL
  ├─ Validate URL (phải là http/https)
  ├─ Nếu domain không phải bkns.vn → CẢNH BÁO admin: "URL ngoài bkns.vn, tiếp tục?"
  └─ Nếu URL đã crawl trong 24h → SKIP, báo "Đã crawl gần đây"

BƯỚC 2: Crawl
  ├─ HTTP GET với User-Agent hợp lệ
  ├─ Nếu HTTP error → BÁO LỖI: "❌ crawl-source: Không truy cập được [URL] (HTTP {code})"
  ├─ Extract text bằng BeautifulSoup + html2text
  └─ Loại bỏ: nav, footer, sidebar, ads, scripts

BƯỚC 3: Lưu File
  ├─ Tên file: raw/website-crawl/{slug}-{YYYY-MM-DD}.md
  ├─ Tạo metadata header (xem bên dưới)
  ├─ Content hash SHA256
  └─ Nếu hash trùng file cũ → SKIP, báo "Nội dung không thay đổi"

BƯỚC 4: Cập Nhật Source Registry
  ├─ Thêm/cập nhật entry trong sources/registry.yaml
  └─ Ghi log: logs/intake/{YYYY-MM-DD}.jsonl

BƯỚC 5: Báo Admin
  └─ "✅ Đã lưu [URL] → raw/website-crawl/{filename}. Gõ /extract để trích claims."
```

## Metadata Header (Ghi Vào Đầu File raw/)

```yaml
---
source_url: https://bkns.vn/hosting
crawled_at: 2026-04-04T10:00:00+07:00
content_type: webpage
domain: bkns.vn
page_title: "Hosting BKNS - Giải pháp hosting tốt nhất"
content_hash: sha256:abc123...
word_count: 1523
status: pending_extraction
suggested_category: products/hosting
crawl_method: http_get
---
```

## Source Registry Entry (sources/registry.yaml)

```yaml
- source_id: SRC-BKNS-WEB-HOSTING
  type: official_product_page
  url: https://bkns.vn/hosting
  authority_level: 3          # addon.md §7 — official product page
  freshness_sla_days: 7       # verify lại mỗi 7 ngày
  last_crawled: 2026-04-04
  raw_file: raw/website-crawl/hosting-2026-04-04.md
  hash: sha256:abc123...
```

## Script: scripts/crawl.py

```python
#!/usr/bin/env python3
"""crawl-source: Thu thập nội dung từ URL vào raw/"""
import os, sys, json, hashlib, re, yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import html2text

WIKI_ROOT = Path("/home/openclaw/wiki")
RAW_DIR = WIKI_ROOT / "raw" / "website-crawl"
SOURCES_FILE = WIKI_ROOT / "sources" / "registry.yaml"
LOG_DIR = WIKI_ROOT / "logs" / "intake"

VN_TZ = timezone(timedelta(hours=7))

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[\s]+', '-', text).strip('-')[:60]

def crawl_url(url: str) -> dict:
    """Crawl URL, return dict with content + metadata."""
    parsed = urlparse(url)
    
    # Validate
    if parsed.scheme not in ('http', 'https'):
        return {"error": f"URL scheme không hợp lệ: {parsed.scheme}"}
    
    # Check duplicate within 24h
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    slug = slugify(parsed.path.strip('/') or parsed.netloc)
    filename = f"{slug}-{today}.md"
    filepath = RAW_DIR / filename
    
    if filepath.exists():
        return {"skip": True, "reason": "Đã crawl trong 24h", "file": str(filepath)}
    
    # Crawl
    headers = {"User-Agent": "BKNSWikiBot/1.0 (+https://bkns.vn)"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"HTTP error: {e}"}
    
    # Parse HTML
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string.strip() if soup.title else slug
    
    # Remove noise
    for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
        tag.decompose()
    
    # Convert to Markdown
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    h2t.ignore_images = False
    h2t.body_width = 0
    content = h2t.handle(str(soup))
    
    # Hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # Check if content unchanged from last crawl
    existing_files = sorted(RAW_DIR.glob(f"{slug}-*.md"), reverse=True)
    if existing_files:
        old_content = existing_files[0].read_text().split('---', 2)[-1]
        old_hash = hashlib.sha256(old_content.strip().encode()).hexdigest()
        if old_hash == content_hash:
            return {"skip": True, "reason": "Nội dung không thay đổi"}
    
    # Build metadata
    now = datetime.now(VN_TZ).isoformat()
    metadata = {
        "source_url": url,
        "crawled_at": now,
        "content_type": "webpage",
        "domain": parsed.netloc,
        "page_title": title,
        "content_hash": f"sha256:{content_hash}",
        "word_count": len(content.split()),
        "status": "pending_extraction",
        "suggested_category": guess_category(url),
        "crawl_method": "http_get",
    }
    
    # Write file
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"---\n{yaml.dump(metadata, allow_unicode=True, default_flow_style=False)}---\n\n")
        f.write(content)
    
    # Update source registry
    update_source_registry(url, slug, filepath, metadata)
    
    # Log
    log_entry = {"ts": now, "skill": "crawl-source", "action": "success",
                 "url": url, "file": str(filepath), "words": metadata["word_count"]}
    log_append(log_entry)
    
    return {"success": True, "file": str(filepath), "words": metadata["word_count"], "title": title}


def guess_category(url: str) -> str:
    path = urlparse(url).path.lower()
    mapping = {
        "hosting": "products/hosting", "vps": "products/vps",
        "ten-mien": "products/ten-mien", "domain": "products/ten-mien",
        "email": "products/email", "ssl": "products/ssl",
        "gioi-thieu": "company", "lien-he": "support",
        "ho-tro": "support", "chinh-sach": "policies",
    }
    for key, cat in mapping.items():
        if key in path:
            return cat
    return "uncategorized"


def update_source_registry(url, slug, filepath, metadata):
    SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    registry = yaml.safe_load(SOURCES_FILE.read_text()) if SOURCES_FILE.exists() else []
    registry = registry or []
    
    source_id = f"SRC-BKNS-WEB-{slug.upper()[:30]}"
    existing = next((s for s in registry if s.get("url") == url), None)
    
    entry = {
        "source_id": existing["source_id"] if existing else source_id,
        "type": "official_product_page",
        "url": url,
        "authority_level": 3,
        "freshness_sla_days": 7,
        "last_crawled": metadata["crawled_at"][:10],
        "raw_file": str(filepath.relative_to(WIKI_ROOT)),
        "hash": metadata["content_hash"],
    }
    
    if existing:
        registry[registry.index(existing)] = entry
    else:
        registry.append(entry)
    
    SOURCES_FILE.write_text(yaml.dump(registry, allow_unicode=True, default_flow_style=False))


def log_append(entry):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    with open(LOG_DIR / f"{today}.jsonl", 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawl.py <URL> [URL2] [URL3] ...")
        sys.exit(1)
    for url in sys.argv[1:]:
        result = crawl_url(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
```

## Xử Lý Lỗi

| Lỗi | Hành động | Telegram message |
|-----|----------|-----------------|
| HTTP 404/500 | Ghi log, skip | ❌ `crawl-source`: Không truy cập được [URL] |
| Timeout >30s | Retry 1 lần, nếu fail → skip | ⏱️ `crawl-source`: Timeout [URL] |
| Content trống | Skip, cảnh báo | ⚠️ `crawl-source`: Trang [URL] không có nội dung |
| Hash trùng | Skip im lặng | — (không báo, nội dung chưa thay đổi) |

## Batch Crawl Ban Đầu (Phase 0.5)

```bash
# 5 trang chính cần crawl đầu tiên
python3 scripts/crawl.py \
  https://bkns.vn \
  https://bkns.vn/hosting \
  https://bkns.vn/ten-mien \
  https://bkns.vn/vps \
  https://bkns.vn/lien-he
```

---

*Skill tiếp theo: [10b-extract-claims.md](./10b-extract-claims.md) — Trích xuất facts từ raw/*

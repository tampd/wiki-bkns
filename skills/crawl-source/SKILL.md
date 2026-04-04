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

# crawl-source

## Mô tả
Thu thập trang web từ bkns.vn, clean HTML thành Markdown, lưu vào `raw/website-crawl/`
với frontmatter metadata đầy đủ. Kiểm tra URL hợp lệ, duplicate 24h, hash content.

## Input
- `/them [URL]` — Crawl một URL cụ thể
- Batch mode — Crawl nhiều URLs từ danh sách

## Output
- `raw/website-crawl/{slug}-{YYYY-MM-DD}.md` — File raw với frontmatter
- `sources/registry.yaml` — Cập nhật source entry
- `logs/intake/{YYYY-MM-DD}.jsonl` — Audit log

## Model
Không dùng LLM — pure Python script ($0/lần).

## Files
- scripts/crawl.py: Logic crawl chính

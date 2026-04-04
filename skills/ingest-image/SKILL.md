---
name: ingest-image
description: >
  Trích xuất thông tin từ ảnh chụp bảng giá, panel, hoặc tài liệu.
  Dùng Gemini Flash Vision → extract structured data → claims YAML.
  Lưu ảnh gốc vào assets/evidence/ làm bằng chứng.
  Trigger: /anh [path] hoặc admin gửi ảnh qua Telegram.
version: "1.0"
phase: "1"
model: gemini-2.5-flash
admin_only: true
triggers:
  - command: /anh
---

# ingest-image

## Files
- scripts/ingest.py: Vision extraction logic

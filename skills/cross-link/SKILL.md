---
name: cross-link
description: >
  Tự động phát hiện và thêm internal links giữa các trang wiki.
  Phân tích đồ thị liên kết → tìm orphan pages → đề xuất See Also.
  Trigger: /link-scan hoặc auto sau mỗi build.
version: "1.0"
phase: "2"
model: gemini-2.5-flash
admin_only: true
triggers:
  - command: /link-scan
---

# cross-link

## Files
- scripts/crosslink.py: Cross-linking engine

---
name: auto-file
description: >
  Phân tích logs câu hỏi → phát hiện FAQ candidates.
  Gom nhóm câu hỏi tương tự → đề xuất tạo trang FAQ mới.
  Trigger: /faq-scan hoặc cron hàng tuần.
version: "1.0"
phase: "2"
model: gemini-2.5-flash
admin_only: true
triggers:
  - command: /faq-scan
---

# auto-file

## Files
- scripts/auto_file.py: FAQ candidate detection

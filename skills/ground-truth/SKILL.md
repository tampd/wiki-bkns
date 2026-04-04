---
name: ground-truth
description: >
  Xác minh nội dung wiki vs dữ liệu thực tế trên website BKNS.
  Weekly crawl → so sánh với claims hiện tại → phát hiện thay đổi.
  Trigger: /verify hoặc cron hàng tuần.
version: "1.0"
phase: "1"
model: gemini-2.5-flash
admin_only: true
triggers:
  - command: /verify
---

# ground-truth

## Files
- scripts/verify.py: Ground truth verification

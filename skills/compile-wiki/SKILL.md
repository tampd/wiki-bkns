---
name: compile-wiki
description: >
  Đọc claims/approved/ → compile thành wiki pages (Markdown + frontmatter).
  BẮT BUỘC self-review: bot tự đọc lại draft, so sánh vs claims gốc.
  Nếu phát hiện hallucination → auto-correct hoặc block.
  Kết quả: wiki/.drafts/ → chờ /duyet để publish lên wiki/.
  Trigger: /compile [topic] hoặc auto sau khi claims mới được approve.
version: "1.0"
phase: "0.5"
model: gemini-2.5-pro
admin_only: true
user-invocable: true
triggers:
  - command: /compile
---

# compile-wiki

## Quy trình
1. Collect claims approved cho category
2. Gemini Pro compile → wiki page draft
3. Self-review: Gemini đọc lại draft + so claims
4. Nếu hallucination → auto-correct (tối đa 3 lần)
5. Lưu wiki/.drafts/ → chờ /duyet

## Files
- scripts/compile.py: Compile logic + self-review

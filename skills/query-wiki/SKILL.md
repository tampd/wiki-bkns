---
name: query-wiki
description: >
  Trả lời câu hỏi về sản phẩm BKNS dựa trên wiki đã compile.
  Sử dụng Gemini Flash + Implicit Context Caching để giảm 90% chi phí.
  Pattern: prefix (wiki content) cached + question (user) per-query.
  Trigger: /hoi [câu hỏi] hoặc auto khi user chat.
version: "1.0"
phase: "0.5"
model: gemini-2.5-flash
admin_only: false
user-invocable: true
triggers:
  - command: /hoi
---

# query-wiki

## Cách hoạt động
1. Load ALL wiki/*.md files vào một prefix string
2. Gửi prefix + câu hỏi → Gemini Flash
3. Gemini auto-cache prefix → chỉ tính tiền question tokens
4. Trả lời bằng tiếng Việt, ghi nguồn (wiki page)

## Cost Model
- First query: ~$0.003 (full input)
- Subsequent queries: ~$0.0003 (90% cached)
- Target: <$0.01/ngày cho 30 queries

## Files
- scripts/query.py: Query logic + build integration

# Skill 8: auto-file

> **Phase:** 2 | **Model:** Gemini Flash | **Triết lý Karpathy:** "Filing outputs back into the wiki to enhance it"

---

## SKILL.md

```yaml
---
name: auto-file
description: >
  Phân tích câu trả lời từ query-wiki. Nếu câu hỏi lặp ≥3 lần và
  câu trả lời đầy đủ từ wiki → đề xuất file vào wiki/faq/ như FAQ candidate.
  KHÔNG tự file — tạo candidate → wiki/.drafts/faq/ → admin /file-review.
  Trigger: tự động sau mỗi query hoặc /file-review weekly digest.
version: "1.0"
phase: "2"
model: gemini-2.5-flash
admin_only: false
user-invocable: true
triggers:
  - event: after_query         # Tự động sau mỗi query
  - command: /file-review
  - cron: "0 9 * * 5"         # Friday 09:00 — weekly digest
---
```

---

## Tiêu Chí Auto-File Candidate

```yaml
# ĐỀ XUẤT khi TẤT CẢ các điều kiện đều đúng:
propose_when:
  - question_frequency: ">= 3"          # Câu hỏi tương tự lặp ≥3 lần
  - answer_quality: "complete_from_wiki" # Bot trả lời đầy đủ từ wiki
  - not_in_faq: true                     # Chưa có câu hỏi này trong wiki/faq/

# KHÔNG đề xuất khi BẤT KỲ điều kiện nào đúng:
skip_when:
  - answer_had_fallback: true            # Bot nói "không có thông tin"
  - question_too_specific: true          # Câu hỏi về tài khoản/đơn hàng cụ thể
  - answer_contains_uncertainty: true    # Có ký hiệu ⚠️ trong câu trả lời
```

---

## Workflow

```
SAU MỖI QUERY (background):
  1. Normalize câu hỏi (lowercase, remove stopwords)
  2. Tìm câu hỏi tương tự trong logs/query-*.jsonl
  3. Đếm frequency trong 30 ngày gần nhất

NẾU frequency ≥ 3 + answer complete:
  4. Tạo FAQ draft:
     Q: {câu hỏi được normalize}
     A: {câu trả lời đã clean, bỏ "Theo [file]..." prefix}
     Source claims: {claim_refs từ answer trace}

  5. Lưu: wiki/.drafts/faq/{category}-{question_hash[:8]}.md

WEEKLY DIGEST (Friday 09:00):
  6. Đếm candidates mới trong tuần
  7. Gửi Telegram: "📬 {N} FAQ candidates tuần này. /file-review để xem."

ADMIN /file-review:
  8. Liệt kê candidates: Q + A preview
  9. Admin /duyet → move .drafts/faq/ → wiki/faq/
     Admin /skip → xóa candidate
```

---

## FAQ Draft Format

```markdown
---
title: "Câu hỏi: {normalized question}"
category: faq
subcategory: hosting          # hosting|vps|ten-mien|email|ssl|support
updated: 2026-04-04
filed_from_answer: ANS-20260404-0001
question_frequency: 5
review_state: draft
---

## Câu Hỏi

{normalized question}

## Câu Trả Lời

{clean answer without "Theo [file]..." prefixes}

---
*FAQ candidate — cần admin duyệt trước khi publish*
*Tần suất câu hỏi: 5 lần trong 30 ngày*
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Duplicate candidate | Check hash trước, skip nếu đã có |
| Answer quality thấp | Skip, không tạo candidate |
| wiki/faq/ chưa tồn tại | mkdir -p tự động |

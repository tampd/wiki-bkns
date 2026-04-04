# Skill 3: compile-wiki (+ self-review tích hợp)

> **Phase:** 0.5 | **Model:** Gemini 2.5 Pro | **Cost:** ~$0.02-0.08/page
> **Điểm then chốt:** Bot tự đọc lại draft, so sánh vs claims gốc trước khi gửi admin

---

## SKILL.md

```yaml
---
name: compile-wiki
description: >
  Biên dịch claims đã approved thành wiki Markdown pages.
  Bao gồm SELF-REVIEW bắt buộc: bot đọc lại draft, so sánh từng con số
  với claims gốc, auto-correct nếu sai trước khi gửi admin duyệt.
  Output: wiki/.drafts/ — KHÔNG publish thẳng.
  Trigger: /compile hoặc sau khi claims được approve.
version: "1.0"
phase: "0.5"
model: gemini-2.5-pro
admin_only: true
user-invocable: true
triggers:
  - command: /compile
---
```

---

## Workflow

```
BƯỚC 1: Thu thập claims approved
  ├─ Scan claims/approved/ → group by entity_type + category
  ├─ Load entities/registry.yaml → canonical names
  └─ Load build/active-build.yaml → biết build hiện tại

BƯỚC 2: Quyết định page structure
  ├─ Mỗi entity_type/category → 1 wiki page (tong-quan + bang-gia)
  ├─ Page đã tồn tại trong wiki/ → compile UPDATE (diff mode)
  └─ Page mới → compile CREATE

BƯỚC 3: Gửi Gemini Pro với COMPILE PROMPT
  ├─ Input: claims JSON + entity info + existing page (nếu update)
  └─ Output: Markdown page hoàn chỉnh

★ BƯỚC 4: SELF-REVIEW (bắt buộc — không được skip)
  ├─ Bot đọc lại draft vừa tạo
  ├─ So sánh TỪNG con số trong draft vs claims gốc (giá, RAM, CPU, SSD)
  ├─ Phát hiện hallucination: fact trong draft nhưng KHÔNG CÓ trong claims
  ├─ Phát hiện mismatch: số trong draft ≠ số trong claim
  ├─ Auto-correct: sửa ngay + ghi log "self-correction"
  ├─ Nếu >3 mismatches → báo admin review thủ công
  └─ Ghi self-review report vào logs/compile/{date}.jsonl

BƯỚC 5: Lưu draft
  ├─ wiki/.drafts/{category}/{filename}.md
  └─ Git commit: "draft(wiki): compile {category}/{filename}"

BƯỚC 6: Preview cho admin
  ├─ Tóm tắt: "{N} facts, {M} bảng giá, {K} cần verify"
  ├─ Nếu update → show diff ngắn vs page hiện tại
  └─ Gửi Telegram preview

BƯỚC 7: Chờ /duyet
  ├─ Admin: /duyet {filename} → move .drafts/ → wiki/
  ├─ Cập nhật claims liên quan: review_state → approved
  ├─ Git commit: "feat(wiki): publish {filename}"
  ├─ Gọi build-snapshot tự động
  └─ Báo: "✅ Published. Cache invalidated. Build: v{version}"
```

---

## Compile Prompt

```
Bạn là thủ thư biên tập wiki BKNS. Biên dịch claims thành wiki page Markdown.

INPUT:
- Claims (JSON): {claims_json}
- Entity info: {entity_info}
- Category: {category}
- Existing page (nếu update): {existing_page_content}

QUY TẮC BIÊN DỊCH NGHIÊM NGẶT:
1. ❌ TUYỆT ĐỐI KHÔNG tạo fact mới — chỉ dùng data từ claims
2. ❌ KHÔNG thêm giá, specs, chính sách không có trong claims
3. ❌ KHÔNG dùng marketing language — viết trung lập, chính xác
4. ✅ Mỗi bảng giá phải map chính xác 1:1 với claims
5. ✅ Mỗi fact quan trọng → ghi nguồn: "(Nguồn: {source_id})"
6. ✅ Claim có confidence=low → đánh dấu ⚠️
7. ✅ Cuối file → section "Xem thêm" với links liên quan

OUTPUT FORMAT (frontmatter + nội dung):
---
page_id: wiki.{category}.{slug}
title: {title chính xác}
category: {category}
compiled_from_claims:
  - {claim_id_1}
updated: {today}
review_state: draft
sensitivity: {high nếu có pricing, low nếu không}
---

# {Title}

## Tổng Quan
[2-3 câu mô tả, DỰA TRÊN claims, không bịa]

## Bảng Giá
| Gói | Giá/tháng | RAM | CPU | SSD | Bandwidth |
|-----|-----------|-----|-----|-----|-----------|
[map 1:1 từ claims]

## Tính Năng
[bullet list từ claims]

## Câu Hỏi Thường Gặp
[nếu có FAQ claims]

## Xem Thêm
- [Link liên quan]

---
*Compiled by BKNS Wiki Bot • {date} • Build: {build_id}*
```

---

## Self-Review Prompt (Bước 4 — BẮT BUỘC)

```
Bạn là kiểm toán viên (auditor). So sánh wiki draft với claims gốc.

DRAFT: {draft_content}
CLAIMS GỐC: {original_claims_json}

KIỂM TRA TỪNG ĐIỂM:
1. Mỗi số trong draft (giá, RAM, CPU, SSD...) có KHỚP với claims?
   → Nếu sai: "[MISMATCH] {field}: draft={X} vs claim={Y}"
2. Fact nào trong draft KHÔNG TỒN TẠI trong claims? (hallucination)
   → Nếu có: "[HALLUCINATION] {nội dung sai}"
3. Claim nào BỊ BỎ SÓT không có trong draft?
   → Nếu có: "[MISSING] claim {id}: {attribute}={value}"

OUTPUT (JSON):
{
  "status": "PASS" | "NEEDS_CORRECTION",
  "mismatches": [...],
  "hallucinations": [...],
  "missing_claims": [...],
  "corrected_draft": "{markdown sửa lại nếu NEEDS_CORRECTION}"
}
```

---

## /duyet Workflow Chi Tiết

```python
def approve_draft(filename: str, approved_by: str) -> str:
    # 1. Tìm file trong wiki/.drafts/
    # 2. Đọc frontmatter → xác định category, title
    # 3. Map category → wiki/{path}/
    # 4. Backup nếu file đã tồn tại
    # 5. Move .drafts/ → wiki/
    # 6. Update frontmatter: approved_by, approved_at
    # 7. Log approval → logs/approvals-{YYYY-MM}.jsonl
    # 8. Git add + commit: "feat(wiki): publish {filename}"
    # 9. Gọi build-snapshot
    # 10. Báo admin: "✅ Published. Build: v{version}"
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Gemini output không phải Markdown | Retry 1 lần. Fail → báo admin |
| Self-review phát hiện hallucination | Auto-remove + log "⚠️ Self-correction: removed {N} facts" |
| Self-review phát hiện mismatch | Auto-correct + log. Nếu >3 mismatches → báo admin |
| Claim conflict chưa resolved | Compile với cảnh báo ⚠️ trong page |
| /duyet file không tồn tại | Báo admin danh sách drafts có sẵn |

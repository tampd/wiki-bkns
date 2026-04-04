# Skill 3: compile-wiki — Biên Dịch Claims → Wiki Markdown

> **Phase:** 0.5 | **Model:** Gemini 2.5 Pro | **Cost:** ~$0.02-0.08/page
> **Triết lý Karpathy:** "LLM compiles raw into wiki. You never write the wiki manually."
> **Điểm khác biệt:** Bot compile → tự review → KHÔNG publish thẳng → chờ admin duyệt

---

## SKILL.md

```yaml
---
name: compile-wiki
description: >
  Biên dịch claims đã approved thành wiki Markdown pages.
  Đọc claims/ + entities/ → tạo wiki/.drafts/ với frontmatter chuẩn.
  Bao gồm bước SELF-REVIEW: bot đọc lại draft, so sánh với claims gốc.
  KHÔNG publish thẳng — tất cả output vào wiki/.drafts/, chờ /duyet.
  Trigger: /compile hoặc sau khi batch claims được approve.
user-invocable: true
---
```

## Workflow: claims/ → wiki/.drafts/

```
BƯỚC 1: Thu thập claims approved
  ├─ Scan claims/approved/ → group by entity_type + category
  ├─ Load entities/registry.yaml → canonical names
  └─ Load build/active-build.yaml → biết build hiện tại

BƯỚC 2: Quyết định page structure
  ├─ Mỗi entity_type/category → 1 wiki page (tong-quan + bang-gia)
  ├─ Nếu page đã tồn tại trong wiki/ → compile UPDATE (diff)
  └─ Nếu page mới → compile CREATE

BƯỚC 3: Gửi Gemini Pro với COMPILE PROMPT
  ├─ Input: claims JSON + entity info + existing page (nếu update)
  └─ Output: Markdown page hoàn chỉnh

★ BƯỚC 4: SELF-REVIEW (điểm then chốt)
  ├─ Bot đọc lại draft vừa tạo
  ├─ So sánh TỪNG con số trong draft vs claims gốc
  ├─ Nếu phát hiện sai lệch → SỬA NGAY + log "self-correction"
  ├─ Nếu có fact trong draft KHÔNG CÓ trong claims → XÓA (bot bịa)
  └─ Ghi self-review report vào logs/compile/

BƯỚC 5: Lưu draft
  ├─ wiki/.drafts/{category}/{filename}.md
  └─ Git commit: "draft(wiki): compile {category}/{filename}"

BƯỚC 6: Tạo preview cho admin
  ├─ Tóm tắt: "{N} facts, {M} bảng giá, {K} cần verify"
  ├─ Nếu có update → show diff vs page hiện tại
  └─ Gửi Telegram preview

BƯỚC 7: Chờ /duyet
  ├─ Admin: /duyet {filename} → move .drafts/ → wiki/
  ├─ Auto: cập nhật build manifest, Git tag
  └─ Reload wiki prefix (invalidate cache)
```

## Compile Prompt (Gemini Pro)

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
6. ✅ Nếu claim có confidence=low → đánh dấu ⚠️
7. ✅ Cuối file → section "Xem thêm" với links liên quan

OUTPUT FORMAT:
---
page_id: wiki.{category}.{slug}
title: {title chính xác}
category: {category}
compiled_from_claims:
  - {claim_id_1}
  - {claim_id_2}
updated: {today}
review_state: draft
sensitivity: {high nếu có pricing}
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

## Xem Thêm
- [Link liên quan]

---
*Compiled by BKNS Wiki Bot • {date} • Build: {build_id}*
```

## Self-Review Prompt (Bước 4)

```
Bạn là kiểm toán viên (auditor). So sánh wiki draft với claims gốc.

DRAFT: {draft_content}
CLAIMS GỐC: {original_claims_json}

KIỂM TRA:
1. Mỗi con số trong draft (giá, RAM, CPU, SSD...) có KHỚP CHÍNH XÁC với claims?
   → Nếu sai: liệt kê "[FIELD] draft={X} vs claim={Y}"
2. Có fact nào trong draft KHÔNG TỒN TẠI trong claims? (bot bịa)
   → Nếu có: liệt kê "[HALLUCINATION] {nội dung}"
3. Có claim nào BỊ BỎ SÓT không có trong draft?
   → Nếu có: liệt kê "[MISSING] claim {id}: {attribute}={value}"

OUTPUT FORMAT (JSON):
{
  "status": "PASS" | "NEEDS_CORRECTION",
  "mismatches": [...],
  "hallucinations": [...],
  "missing_claims": [...],
  "corrected_draft": "{markdown sửa lại nếu NEEDS_CORRECTION}"
}
```

## /duyet Workflow (Post-Compile)

```
Admin gửi: /duyet products/hosting/bang-gia

Bot thực hiện:
  1. Kiểm tra wiki/.drafts/products/hosting/bang-gia.md tồn tại
  2. Move file → wiki/products/hosting/bang-gia.md
  3. Cập nhật claims liên quan: review_state → approved
  4. Git add + commit: "feat(wiki): publish products/hosting/bang-gia"
  5. Cập nhật build manifest:
     - Tạo build mới hoặc update existing
     - Git tag: build/v{version}
  6. Reload wiki_content (invalidate implicit cache)
  7. Cập nhật wiki/index.md (thêm link nếu page mới)
  8. Báo admin: "✅ Published. Cache invalidated. Build: v{version}"
```

## Xử Lý Lỗi

| Lỗi | Hành động |
|-----|----------|
| Gemini output không phải Markdown | Retry 1 lần với prompt bổ sung. Nếu fail → báo admin |
| Self-review phát hiện hallucination | Auto-correct. Log "⚠️ Self-correction: removed {N} hallucinated facts" |
| Self-review phát hiện mismatch | Auto-correct giá/specs. Log correction. Nếu >3 mismatches → báo admin review thủ công |
| Claim conflict chưa resolved | Compile với cảnh báo ⚠️ trong page. Không ghi chắc chắn |
| /duyet file không tồn tại | Báo admin danh sách drafts có sẵn |

---

*Skill tiếp: [10d-query-wiki.md](./10d-query-wiki.md) — Trả lời câu hỏi*

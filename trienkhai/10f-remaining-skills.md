# Skills 8-10: auto-file, cross-link, build-snapshot

> **Phase:** 2-3 | Skills hoàn thiện vòng lặp Karpathy

---

## Skill 8: auto-file — Filing Câu Trả Lời Hay Vào Wiki

> **Phase:** 2 | **Model:** Flash | **Triết lý Karpathy:** "Filing outputs back into the wiki to enhance it"

### SKILL.md

```yaml
---
name: auto-file
description: >
  Phân tích câu trả lời từ query-wiki. Nếu câu trả lời có giá trị cao
  (FAQ phổ biến, thông tin bổ sung) → đề xuất file vào wiki/faq/.
  KHÔNG tự file — tạo candidate → admin duyệt.
  Trigger: tự động sau mỗi query hoặc /file-review.
user-invocable: true
---
```

### Tiêu Chí Auto-File Candidate

```yaml
autofile_criteria:
  # Tự động đề xuất khi:
  - question_asked_count: ">= 3"          # Câu hỏi lặp ≥3 lần
  - answer_quality: "complete_from_wiki"   # Trả lời đầy đủ từ wiki
  - not_exists_in_faq: true                # Chưa có trong FAQ hiện tại

  # KHÔNG đề xuất khi:
  - answer_had_fallback: true              # Bot nói "không có thông tin"
  - question_too_specific: true            # Câu hỏi quá riêng lẻ
  - answer_contains_uncertainty: true      # Có cảnh báo ⚠️
```

### Workflow

```
1. Sau mỗi query → đếm frequency câu hỏi tương tự
2. Nếu frequency ≥ 3 + answer complete → flag candidate
3. Tạo FAQ draft:
   Q: {question normalized}
   A: {answer cleaned}
   Source: {claim_refs from answer trace}
4. Lưu: wiki/.drafts/faq/{category}-{hash}.md
5. Weekly digest: "📬 {N} FAQ candidates tuần này. /file-review để xem."
6. Admin: /file-review → duyệt từng cái → /duyet hoặc /skip
```

---

## Skill 9: cross-link — Liên Kết Chéo Tự Động

> **Phase:** 2 | **Model:** Flash | **Karpathy:** "backlinks, categorizes, interlinks everything"

### SKILL.md

```yaml
---
name: cross-link
description: >
  Quét toàn bộ wiki, phát hiện khái niệm/sản phẩm được đề cập nhưng chưa có link.
  Tạo "Xem thêm" section cuối mỗi file. Cập nhật wiki/index.md.
  Output: danh sách thay đổi → admin duyệt.
  Trigger: /crosslink hoặc sau compile mới.
user-invocable: true
---
```

### Workflow

```
1. Load toàn bộ wiki files → build entity mention map
2. Với mỗi file:
   ├─ Tìm mentions entity names/aliases chưa có link
   ├─ Tìm file wiki tương ứng cho entity
   └─ Đề xuất: thêm [[link]] hoặc "Xem thêm" section
3. Cập nhật wiki/index.md nếu có file mới chưa index
4. Output: changeset JSON → admin preview
5. Admin: /apply-links → bot apply + commit
```

### Cross-Link Prompt

```
Đọc wiki BKNS. Tìm mọi chỗ đề cập sản phẩm/khái niệm nhưng CHƯA có link.

Ví dụ: Nếu hosting/bang-gia.md nói "VPS MMO" nhưng không link đến vps/vps-mmo.md
→ Đề xuất thêm link.

Output: JSON array:
[
  {"file": "hosting/bang-gia.md", "mention": "VPS MMO", "link_to": "vps/vps-mmo.md", "line": 42},
  ...
]
```

---

## Skill 10: build-snapshot — Tạo Build Manifest

> **Phase:** 1 | **Model:** Không cần LLM (script) | **Cost:** $0

### SKILL.md

```yaml
---
name: build-snapshot
description: >
  Tạo build manifest sau khi wiki được publish.
  Hash toàn bộ claims + wiki → build ID.
  Cập nhật active-build.yaml. Git tag.
  Trigger: tự động sau /duyet hoặc manual /build.
user-invocable: true
---
```

### Workflow

```
1. Hash claims/approved/** → claims_hash
2. Hash wiki/** (ngoài .drafts) → wiki_hash
3. Tạo build manifest:
   build/manifests/build-{date}-{seq}.yaml
4. Cập nhật build/active-build.yaml → trỏ build mới
5. Git tag: build/v{major}.{minor}
6. Log: "🔨 Build v{version} created. {N} claims, {M} wiki pages."
```

### Build Manifest

```yaml
build_id: build-2026-04-04-01
created_at: "2026-04-04T16:00:00+07:00"
claims_count: 45
wiki_pages_count: 12
claims_hash: "sha256:abc..."
wiki_hash: "sha256:def..."
status: active
parent_build_id: null
lint_summary:
  syntax_passed: true
  semantic_passed: true
  unresolved_conflicts: 0
```

---

## Tổng Kết: Vòng Lặp Karpathy Hoàn Chỉnh

```
         ┌─────────────────────────────────────────┐
         │         KARPATHY LOOP — BKNS            │
         │                                         │
    ┌────┴────┐                              ┌─────┴─────┐
    │ INGEST  │                              │  FILING   │
    │ crawl   │                              │ auto-file │
    │ image   │                              │ cross-link│
    └────┬────┘                              └─────┬─────┘
         │                                         ↑
         ↓                                         │
    ┌────┴────┐                              ┌─────┴─────┐
    │ EXTRACT │                              │  QUERY    │
    │ claims  │                              │ query-wiki│
    └────┬────┘                              └─────┬─────┘
         │                                         ↑
         ↓                                         │
    ┌────┴────┐    ┌──────────┐    ┌──────┐  ┌─────┴─────┐
    │ COMPILE │───→│ SELF-    │───→│/duyet│─→│   BUILD   │
    │  wiki   │    │ REVIEW   │    │admin │  │ snapshot  │
    └─────────┘    └──────────┘    └──────┘  └───────────┘
                                                   │
                                         ┌─────────┴─────────┐
                                         │     LINT/VERIFY    │
                                         │ lint + ground-truth│
                                         └───────────────────┘
```

### Mỗi Skills Đảm Bảo:

| Nguyên tắc | Cách thực hiện |
|-----------|----------------|
| **Bot KHÔNG bịa** | Self-review so sánh draft vs claims gốc |
| **Bot KHÔNG ghi thẳng wiki** | Mọi output → .drafts/ → /duyet |
| **Báo lỗi cho admin** | Telegram alert ở mỗi bước fail |
| **Tự đọc lại trước khi ghi** | Self-review prompt (compile skill) |
| **Audit trail** | JSONL traces + Git commits + build tags |
| **So sánh trước khi chấp nhận** | Conflict detection + ground-truth |
| **Vòng lặp tự cải thiện** | auto-file + cross-link + lint |

---

*Quay lại tổng quan: [10-skills-overview.md](./10-skills-overview.md)*
*Xem kế hoạch: [02-ke-hoach-hanh-dong.md](./02-ke-hoach-hanh-dong.md)*

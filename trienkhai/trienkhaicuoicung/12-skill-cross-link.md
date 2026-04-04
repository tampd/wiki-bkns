# Skill 9: cross-link

> **Phase:** 2 | **Model:** Gemini Flash | **Karpathy:** "backlinks, categorizes, interlinks everything"

---

## SKILL.md

```yaml
---
name: cross-link
description: >
  Quét toàn bộ wiki, phát hiện khái niệm/sản phẩm được đề cập nhưng chưa có link.
  Tạo/cập nhật "Xem thêm" section cuối mỗi file. Cập nhật wiki/index.md.
  Output: changeset JSON → admin preview → /apply-links.
  Trigger: /crosslink hoặc tự động sau compile mới.
version: "1.0"
phase: "2"
model: gemini-2.5-flash
admin_only: true
user-invocable: true
triggers:
  - command: /crosslink
  - event: after_publish      # Sau khi /duyet thành công
---
```

---

## Workflow

```
BƯỚC 1: Load toàn bộ wiki files → build entity mention map
  ├─ Đọc entities/registry.yaml → list tên sản phẩm + aliases
  └─ Scan mỗi file → tìm mentions chưa có [[link]]

BƯỚC 2: Gửi Gemini Flash với CROSS-LINK PROMPT

BƯỚC 3: Nhận changeset JSON
  └─ Danh sách: file + vị trí + mention + link_to

BƯỚC 4: Cập nhật wiki/index.md
  └─ Thêm link nếu có file mới chưa index

BƯỚC 5: Preview cho admin
  └─ Gửi Telegram: "{N} cross-links đề xuất. /apply-links để apply."

BƯỚC 6: Admin /apply-links
  ├─ Bot apply changeset vào wiki files
  ├─ Git commit: "chore(wiki): add {N} cross-links"
  └─ Báo: "✅ {N} links added to wiki"
```

---

## Cross-Link Prompt

```
Đọc wiki BKNS. Tìm mọi chỗ đề cập sản phẩm/khái niệm NHƯNG chưa có link.

Ví dụ: Nếu hosting/bang-gia.md nói "VPS MMO" nhưng không link đến vps/vps-mmo.md
→ Đề xuất thêm link.

Entities cần link: {entities_list}
Wiki files: {file_list}

OUTPUT (JSON array):
[
  {
    "file": "products/hosting/tong-quan.md",
    "mention": "VPS MMO",
    "link_to": "products/vps/vps-mmo.md",
    "action": "add_inline_link",  # add_inline_link | add_see_also
    "context": "...dùng VPS MMO cho...",
    "line_hint": 42
  },
  {
    "file": "products/hosting/tong-quan.md",
    "mention": "SSL Certificate",
    "link_to": "products/ssl/tong-quan.md",
    "action": "add_see_also"
  }
]
```

---

## Xem Thêm Section Format

```markdown
## Xem Thêm

- [VPS BKNS](../vps/tong-quan.md) — Hiệu năng cao hơn hosting
- [Tên miền BKNS](../ten-mien/tong-quan.md) — Đăng ký domain
- [SSL Certificate](../ssl/tong-quan.md) — Bảo mật website
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Link target không tồn tại | Skip link đó, log warning |
| Circular links | Detect và skip |
| Quá nhiều links (>10/file) | Cap tại 5 links quan trọng nhất |

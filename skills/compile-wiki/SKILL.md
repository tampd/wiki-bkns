---
name: compile-wiki
description: >
  Đọc claims/approved/ → compile thành wiki pages (Markdown + frontmatter).
  Multi-page architecture v3.0: 9 sub-pages chuẩn + product detail pages per category.
  BẮT BUỘC self-review: bot tự đọc lại draft, so sánh vs claims gốc.
  Nếu phát hiện hallucination → auto-correct hoặc block.
  Kết quả: wiki/.drafts/ → chờ /duyet để publish lên wiki/.
  Trigger: /compile [topic] hoặc auto sau khi claims mới được approve.
version: "3.0"
phase: "0.5"
model: gemini-2.5-pro
admin_only: true
user-invocable: true
triggers:
  - command: /compile
---

# compile-wiki v3.0

## Kiến trúc output (9 sub-pages + product pages)

Mỗi category tự động tạo:
1. `index.md` — Hub điều hướng
2. `tong-quan.md` — Tổng quan chi tiết
3. `bang-gia.md` — Bảng giá
4. `thong-so.md` — Thông số kỹ thuật
5. `tinh-nang.md` — Tính năng
6. `chinh-sach.md` — Chính sách
7. `cau-hoi-thuong-gap.md` — FAQ
8. `so-sanh.md` — So sánh nội bộ
9. `huong-dan.md` — Hướng dẫn

Plus: `san-pham/<slug>.md` — Trang sản phẩm chi tiết (per entity)

## Categories hỗ trợ (9)
hosting, vps, email, ssl, ten-mien, server, software, other, uncategorized

## Quy trình
1. Collect claims approved + drafts cho category
2. Deduplicate by entity_id + attribute
3. Filter claims → 9 sub-pages + product pages
4. Gemini Pro compile → wiki page draft per sub-page
5. Self-review: Gemini đọc lại draft + so claims (≥5 claims)
6. Nếu 0 claims → tạo skeleton page với ⏳ placeholder
7. Nếu hallucination → auto-correct (tối đa 3 lần)
8. Lưu wiki/.drafts/ → chờ /duyet

## Files
- scripts/compile.py: Compile logic + self-review + skeleton fallback

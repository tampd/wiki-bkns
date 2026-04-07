---
page_id: wiki.index
title: "BKNS Wiki — Trang chủ"
category: system
updated: '2026-04-07'
review_state: drafted
claims_used: 6
---


# BKNS Wiki — Trang chủ

> Đây là trang điều hướng tổng cho toàn bộ bộ sản phẩm BKNS trong dự án wiki compile từ claims.

## Mục tiêu của wiki
- Chuẩn hóa dữ liệu tư vấn / CSKH / nội bộ theo một schema thống nhất
- Tách rõ dữ liệu đã xác minh và dữ liệu đang chờ verify
- Tạo “nguồn sự thật” cho bot trả lời, đội sale và đội kỹ thuật

## Điều hướng sản phẩm
- [Web Hosting](./products/hosting/index.md)
- [Cloud VPS](./products/vps/index.md)
- [Email Doanh Nghiệp](./products/email/index.md)
- [Chứng Chỉ SSL](./products/ssl/index.md)
- [Tên Miền](./products/ten-mien/index.md)
- [Máy Chủ](./products/server/index.md)
- [Bản Quyền Phần Mềm](./products/software/index.md)
- [Dịch vụ Khác](./products/other/index.md)
- [Chưa phân loại](./products/uncategorized/index.md)

## Khu vực hệ thống
- [Liên hệ BKNS](./support/lien-he.md)
- [Hướng dẫn chung](./support/huong-dan-chung.md)
- [Chính sách chung](./support/chinh-sach-chung.md)
- [FAQ tổng hợp](./support/faq-tong-hop.md)
- [Khuyến mãi](./khuyen-mai/index.md)
- [So sánh tổng hợp](./so-sanh-tong-hop.md)

## Checklist vận hành
- Mỗi file có frontmatter chuẩn
- Mỗi bảng giá có đơn vị + VAT rõ ràng
- Mỗi facts có nguồn URL hoặc claim id gắn kèm trong pipeline
- Mỗi file đều có “Sản phẩm liên quan” và CTA

## Gợi ý triển khai cho dev
- Router bám theo `wiki/products/<category>/<subpage>.md`
- Trang sản phẩm con bám theo `wiki/products/<category>/san-pham/<slug>.md`
- Cho phép render trạng thái `⏳ Đang cập nhật` như badge “chưa xác minh”

## Ghi chú
Trang chủ public của BKNS đang dẫn người dùng từ menu danh mục lớn sang từng landing page con, nên wiki nên bám cùng cấu trúc hub → sub-page → product detail thay vì chỉ có một file duy nhất cho mỗi category.

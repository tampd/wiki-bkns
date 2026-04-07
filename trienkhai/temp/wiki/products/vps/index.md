---
page_id: wiki.products.vps.index
title: "Cloud VPS BKNS — Trang tổng quan"
category: products/vps
updated: '2026-04-07'
review_state: drafted
claims_used: 10
---


# Cloud VPS BKNS — Trang tổng quan

> Hub category cho toàn bộ nhóm Cloud VPS tại BKNS. Cấu trúc category này phải cho phép đi xuống cả trang hub theo nhóm và trang riêng cho từng biến thể VPS.

## Nhóm sản phẩm đang theo dõi
- Cloud VPS VM
- Cloud VPS AMD
- VPS Giá Rẻ
- Storage VPS
- VPS N8N AI
- Cloud VPS SEO
- Cloud VPS BK Misa
- VPS MMO
- OpenClaw AI

## Sub-pages chuẩn của category
- [Tổng quan chi tiết](./tong-quan.md)
- [Bảng giá](./bang-gia.md)
- [Thông số kỹ thuật](./thong-so.md)
- [Tính năng](./tinh-nang.md)
- [Chính sách](./chinh-sach.md)
- [FAQ](./cau-hoi-thuong-gap.md)
- [So sánh](./so-sanh.md)
- [Hướng dẫn](./huong-dan.md)

## Vai trò của Cloud VPS trong kiến trúc sản phẩm BKNS
- Là lớp trung gian giữa Hosting và Máy Chủ
- Cho phép scale tài nguyên và quản trị sâu hơn Hosting
- Phù hợp với website tăng trưởng, ứng dụng nội bộ, agent AI, automation, SEO, MISA và các workload cần quyền cấu hình linh hoạt

## Danh sách trang sản phẩm con
- [Cloud VPS VM](./san-pham/cloud-vps-vm.md)
- [Cloud VPS AMD](./san-pham/cloud-vps-amd.md)
- [VPS Giá Rẻ](./san-pham/vps-gia-re.md)
- [Storage VPS](./san-pham/storage-vps.md)
- [VPS N8N AI](./san-pham/vps-n8n.md)
- [Cloud VPS SEO](./san-pham/vps-seo.md)
- [Cloud VPS BK Misa](./san-pham/vps-bk-misa.md)
- [VPS MMO](./san-pham/vps-mmo.md)
- [OpenClaw AI](./san-pham/openclaw-ai.md)

## Notes cho dev
- Category này bắt buộc hỗ trợ nhiều product detail pages
- Nên tách `family` và `variant` trong model dữ liệu: ví dụ `family = cloud-vps`, `variant = amd`
- Bảng giá VM và AMD nên được render thành block riêng vì schema không hoàn toàn giống nhau

## Sản phẩm liên quan

- [Web Hosting](../hosting/index.md)
- [Máy Chủ](../server/index.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

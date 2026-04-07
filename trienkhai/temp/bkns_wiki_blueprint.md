# BKNS Wiki Blueprint

Bộ blueprint này được dựng từ 2 nguồn:
1. brief dự án wiki BKNS bạn đã cung cấp;
2. quan sát kiến trúc public hiện tại của bkns.vn.

## 1. Kết luận nghiên cứu nhanh về kiến trúc public

BKNS đang triển khai kiến trúc **hub-and-spoke** khá rõ:
- menu cấp cao: Tên miền, Hosting, Email, VPS, Máy Chủ, Phần mềm, SSL, Hướng dẫn, Khuyến mại;
- dưới mỗi hub là nhiều landing page sản phẩm con;
- mỗi landing page lặp lại các block rất quen: hero, giá, thông số, tính năng, FAQ, CTA, footer/contact.

=> Vì vậy, wiki nên mirror đúng cấu trúc:
- **category hub**
- **9 sub-pages chuẩn cho mỗi category**
- **product detail pages** cho những nhóm có nhiều biến thể

## 2. Kiến trúc file đề xuất

- `wiki/index.md` — hub toàn wiki
- `wiki/products/<category>/index.md` — hub category
- `wiki/products/<category>/(tong-quan|bang-gia|thong-so|tinh-nang|chinh-sach|cau-hoi-thuong-gap|so-sanh|huong-dan).md`
- `wiki/products/<category>/san-pham/<slug>.md` — trang sản phẩm con
- `wiki/support/*` — trang hệ thống dùng lại nhiều lần
- `wiki/khuyen-mai/index.md`
- `wiki/so-sanh-tong-hop.md`

## 3. Điểm đã chốt để dev có thể code

### 3.1 Routing
- Router chính theo `products/<category>/<subpage>`
- Router trang con theo `products/<category>/san-pham/<slug>`

### 3.2 Schema hiển thị
Frontmatter public giữ đúng 6 trường bạn yêu cầu:
```yaml
---
page_id: wiki.products.<category>.<sub-page>
title: "<Tên Category> BKNS — <Tên Sub-page>"
category: products/<category>
updated: 'YYYY-MM-DD'
review_state: drafted | approved | published
claims_used: <số>
---
```

### 3.3 Quy tắc dữ liệu
- Không bịa giá / specs
- Không để trống: dùng `⏳ Đang cập nhật`
- Cuối mỗi trang luôn có cross-link và CTA
- Bảng giá / thông số phải render table Markdown

### 3.4 Khuyến nghị mở rộng cho pipeline
Dù frontmatter public giữ tối giản, pipeline compile nên âm thầm theo dõi thêm:
- `source_url`
- `source_priority`
- `verification_status`
- `effective_date`
- `billing_cycle`
- `product_scope`
- `field_conflict`

## 4. Vì sao cần `verification_status`

Qua site public hiện tại có các nguy cơ mâu thuẫn:
- địa chỉ công ty xuất hiện nhiều biến thể;
- hotline trong SLA khác hotline contact;
- một số giá teaser SSL khác giá landing page chi tiết;
- một số đơn vị hiển thị giá dạng `đ/Năm/tháng`.

Do đó, ở level code nên chuẩn bị:
- badge `verified / needs-review / draft`
- render source priority
- diff report giữa các claims

## 5. Phạm vi bộ skeleton này

### Đã điền mẫu chi tiết hoàn chỉnh
- `hosting`
- `vps`
- `ssl`

### Đã tạo đủ file nhưng để placeholder an toàn
- `email`
- `ten-mien`
- `server`
- `software`
- `other`
- `uncategorized`

## 6. File tree
Xem file đi kèm: `FILE_TREE.txt`

## 7. Checklist review nhanh trước khi chốt dev

- [ ] Đúng slug category theo hệ thống thật
- [ ] Đúng quy tắc relative link
- [ ] Có trang hệ thống support / khuyến mãi / so sánh tổng hợp
- [ ] Có product pages cho VPS / SSL / Email / Software
- [ ] Compiler biết render placeholder thay vì bỏ trống
- [ ] Có chỗ cho status verify / conflict handling
- [ ] Có quality gate cho giá, specs, ngày cập nhật

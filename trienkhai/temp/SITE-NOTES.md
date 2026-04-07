# Ghi chú nghiên cứu bkns.vn cho thiết kế wiki

## 1) Bản đồ sản phẩm public hiện tại
Website public của BKNS đang bày theo mô hình hub-and-spoke:
- Hub cấp 1: Tên miền, Hosting, Email, VPS, Máy Chủ, Phần mềm, Website, SSL, Đối tác, Hướng dẫn.
- Hub cấp 2: từng nhóm có nhiều landing page sản phẩm con riêng.
- Footer và homepage lặp lại danh mục, cho thấy routing chính nên bám theo slug category + slug sản phẩm.

## 2) Mẫu cấu trúc landing page thường gặp
Qua Hosting, Cloud VPS, Cloud VPS AMD và SSL:
1. Hero / value proposition
2. Giá khởi điểm hoặc bảng giá
3. Danh sách tính năng / USP
4. Bảng so sánh hoặc bảng thông số
5. Đối tượng phù hợp / use case
6. Hướng dẫn hoặc CTA dùng thử
7. FAQ
8. Form tư vấn / đăng ký
9. Footer policy / contact

## 3) Quy tắc compile đề xuất
- Giá, specs, SLA: ưu tiên landing page chuyên biệt hoặc hợp đồng mẫu
- Teaser menu / banner homepage chỉ dùng làm “discovery”, không dùng làm ground truth cuối
- Nếu cùng một trường có nhiều giá trị từ nhiều nguồn public, tạo claim `needs_verification: true`

## 4) Điểm cần verify thủ công trước khi publish
- Địa chỉ BKNS xuất hiện nhiều biến thể giữa contact/footer/trang giới thiệu
- Hotline SLA khác hotline contact
- Một số nhãn đơn vị giá trên trang SSL có dạng `đ/Năm/tháng`, cần normalize

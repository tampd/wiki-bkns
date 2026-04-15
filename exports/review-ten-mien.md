# BKNS Wiki Cross-Verification Request — TEN-MIEN

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (0)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (99)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages (12)**: Trang wiki đã compile — CẦN KIỂM TRA

## Checklist Kiểm Tra

### 1. Kiểm tra giá (QUAN TRỌNG NHẤT)
- Mỗi giá trong wiki phải khớp với Ground Truth claims
- Liệt kê mọi giá sai kèm giá đúng từ claims

### 2. Thông số kỹ thuật
- CPU, RAM, SSD có đúng cho từng gói không?
- Có claim nào tự bịa specs không?

### 3. Chính sách
- SLA, hoàn tiền, hỗ trợ — có đúng với claims không?
- Có thông tin chính sách nào BỊA ĐẶT (không có trong claims)?

### 4. Tính nhất quán
- Cùng sản phẩm ở 2 trang khác nhau → giá/specs phải giống
- Tên sản phẩm phải viết đúng format

### 5. Thông tin thiếu
- Claims nào CHƯA ĐƯỢC compile vào wiki?
- Có gói sản phẩm nào bị bỏ sót?

## OUTPUT FORMAT
```json
{
  "accuracy_score": 0-100,
  "issues": [
    {
      "type": "price_error|spec_error|hallucination|inconsistency|missing",
      "severity": "critical|high|medium|low",
      "page": "bang-gia.md",
      "detail": "...",
      "fix": "..."
    }
  ],
  "summary": "Nhận xét tổng thể"
}
```

---

## GROUND TRUTH CLAIMS (Source of Truth)


## LLM-EXTRACTED CLAIMS (Check these)

- .biz: registration_price = 590000 VND (confidence: high)
- .biz: renewal_price = 740000 VND (confidence: high)
- .biz: setup_fee = 0 VND (confidence: high)
- .biz: transfer_price = 740000 VND (confidence: high)
- .com: registration_price = 380000 VND (confidence: high)
- .com: renewal_price = 429000 VND (confidence: high)
- .com: setup_fee = 0 VND (confidence: high)
- .com: transfer_price = 429000 VND (confidence: high)
- .id: registration_price = 575000 VND (confidence: high)
- .id: renewal_price = 575000 VND (confidence: high)
- .id: setup_fee = 0 VND (confidence: high)
- .id: transfer_price = 575000 VND (confidence: high)
- .info: registration_price = 170000 VND (confidence: high)
- .info: renewal_price = 980000 VND (confidence: high)
- .info: setup_fee = 0 VND (confidence: high)
- .info: transfer_price = 980000 VND (confidence: high)
- .net: registration_price = 435000 VND (confidence: high)
- .net: renewal_price = 505000 VND (confidence: high)
- .net: setup_fee = 0 VND (confidence: high)
- .net: transfer_price = 505000 VND (confidence: high)
- .org: registration_price = 365000 VND (confidence: high)
- .org: renewal_price = 535000 VND (confidence: high)
- .org: setup_fee = 0 VND (confidence: high)
- .org: transfer_price = 535000 VND (confidence: high)
- Tên miền .pro: data_contradiction = Thông tin khuyến mãi cho tên miền .pro ghi 'giá khuyến mại 1.115.000 giá gốc 135.000', trong khi bảng giá niêm yết phí đăng ký mới là 135.000đ và phí duy trì là 1.115.000đ, có thể đã bị ghi ngược. None (confidence: high)
- .asia: registration_fee = 440000 VND (confidence: high)
- .asia: renewal_fee = 545000 VND (confidence: high)
- .asia: setup_fee = 0 VND (confidence: high)
- .asia: transfer_in_fee = 545000 VND (confidence: high)
- .biz: registration_fee = 590000 VND (confidence: high)
- .biz: renewal_fee = 740000 VND (confidence: high)
- .biz: setup_fee = 0 VND (confidence: high)
- .biz: transfer_in_fee = 740000 VND (confidence: high)
- .com: installation_fee = 0 VND (confidence: high)
- .com: registration_fee = 380000 VND (confidence: high)
- .com: renewal_fee = 429000 VND (confidence: high)
- .com: setup_fee = 0 VND (confidence: high)
- .com: transfer_in_fee = 429000 VND (confidence: high)
- .id: registration_fee = 575000 VND (confidence: high)
- .id: renewal_fee = 575000 VND (confidence: high)
- .id: setup_fee = 0 VND (confidence: high)
- .id: transfer_in_fee = 575000 VND (confidence: high)
- .info: list_price = 890000 VND (confidence: high)
- .info: registration_fee = 170000 VND (confidence: high)
- .info: renewal_fee = 980000 VND (confidence: high)
- .info: setup_fee = 0 VND (confidence: high)
- .info: transfer_in_fee = 980000 VND (confidence: high)
- Tên miền Quốc tế: installation_fee = 0 VND (confidence: high)
- .me: registration_fee = 745000 VND (confidence: high)
- .me: renewal_fee = 745000 VND (confidence: high)
- .net: registration_fee = 435000 VND (confidence: high)
- .net: renewal_fee = 505000 VND (confidence: high)
- .net: setup_fee = 0 VND (confidence: high)
- .net: transfer_in_fee = 505000 VND (confidence: high)
- .org: registration_fee = 365000 VND (confidence: high)
- .org: renewal_fee = 535000 VND (confidence: high)
- .org: setup_fee = 0 VND (confidence: high)
- .org: transfer_in_fee = 535000 VND (confidence: high)
- .us: registration_fee = 340000 VND (confidence: high)
- .us: renewal_fee = 380000 VND (confidence: high)
- .us: transfer_in_fee = 380000 VND (confidence: high)
- Tên miền Việt Nam: transfer_in_fee = 0 VND (confidence: high)
- .ws: registration_fee = 505000 VND (confidence: high)
- .ws: renewal_fee = 1075000 VND (confidence: high)
- .ws: transfer_in_fee = 1075000 VND (confidence: high)
- Tên miền: activation_time = 30 seconds (confidence: high)
- Dịch vụ Tên miền BKNS: category = ten-mien None (confidence: high)
- Tên miền: description = Cung cấp bảng giá chi tiết cho việc đăng ký mới, duy trì (gia hạn), và transfer các loại tên miền quốc tế và Việt Nam. None (confidence: high)
- Tên miền: ekyc_process = 100% online None (confidence: high)
- Bảo vệ tên miền cấp cao nhất (Registry Lock): feature = Ngăn chặn thay đổi thông tin liên hệ của tên miền trái phép None (confidence: high)
- Dịch vụ Tên miền BKNS: feature_description = Cho phép thay đổi địa chỉ IPv6 của tên miền thông qua Control Panel.  (confidence: high)
- Dịch vụ Tên miền BKNS: included_feature = DNS có hỗ trợ IPv6 None (confidence: high)
- Bảo vệ tên miền cấp cao nhất (Registry Lock): is_a = dịch vụ bảo mật cao cấp cho tên miền  (confidence: high)
- Dịch Vụ Tên Miền: is_about = Cung cấp bảng giá chi tiết cho việc đăng ký mới, duy trì (gia hạn) và chuyển (transfer) các loại tên miền quốc tế và tên miền Việt Nam tại BKNS.  (confidence: high)
- Tên miền: legal_protection = pháp luật Việt Nam bảo hộ tuyệt đối None (confidence: high)
- Bảo vệ tên miền cấp cao nhất (Registry Lock): limitation = Quy trình mở khóa đòi hỏi thời gian và sự phối hợp giữa các bên  (confidence: high)
- Tên miền: ownership_guarantee = quyền sở hữu hợp pháp tuyệt đối None (confidence: high)
- Tên miền: policy = Giá được tính theo năm. None (confidence: high)
- Xác thực 2 bước (2FA): price_info = Miễn phí  (confidence: high)
- Tên miền Việt Nam: price_list_effective_date = 2025-09-01 None (confidence: high)
- Dịch vụ Tên miền BKNS: pricing_note = Chưa bao gồm thuế VAT  (confidence: high)
- Bảo vệ tên miền cấp cao nhất (Registry Lock): process_dependency = VNNIC thực hiện Mở/Khóa dịch vụ theo yêu cầu đã được xác thực.  (confidence: high)
- Dịch vụ Tên miền: product_name = Bảo vệ Tên miền Cấp cao nhất  (confidence: high)
- Tên miền Quốc tế: promotion_end_date = 2025-01-06 None (confidence: high)
- Xác thực 2 bước (2FA): protection_level = Mức tăng cường  (confidence: high)
- Tên miền Việt Nam: registration_price = 30000 VND (confidence: high)
- Tên miền Việt Nam: renewal_price = 30000 VND (confidence: high)
- Tên miền: security_mechanism = Cung cấp cơ chế bảo mật đa lớp, yêu cầu xác thực từ Chủ thể, Nhà đăng ký (BKNS) và VNNIC để thực hiện bất kỳ thay đổi nào đối với tên miền. None (confidence: high)
- Tên miền: seo_advantage = Lợi thế SEO Local vượt trội None (confidence: high)
- Tên miền: seo_benefit_detail = Google ưu tiên .VN cho IP Việt Nam None (confidence: high)
- Dịch vụ Tên miền BKNS: service_limitation = Dịch vụ đăng ký, duy trì và chuyển đổi tên miền (domain name) cho các website, bao gồm cả tên miền Việt Nam (.vn) và tên miền quốc tế (.com, .net, .org, ...). None (confidence: high)
- Dịch vụ Tên miền BKNS: setup_fee = 0 VND (confidence: high)
- Dịch vụ Tên miền BKNS: source_url = https://www.bkns.vn/ten-mien/dang-ky-ten-mien.html None (confidence: high)
- Bảo vệ tên miền cấp cao nhất (Registry Lock): target_audience = bất kỳ ai sở hữu tên miền quan trọng None (confidence: high)
- Dịch vụ Tên miền BKNS: target_customer = Cá nhân, tổ chức và doanh nghiệp muốn sở hữu địa chỉ website riêng None (confidence: high)
- Dịch vụ Tên miền BKNS: transfer_in_policy = 0 VND (confidence: high)
- Xác thực 2 bước (2FA): unlock_process = Chủ thể tự mở khóa tại nhà đăng ký  (confidence: high)
- Tên miền: description = Đăng ký, quản lý tên miền quốc tế & Việt Nam (.vn) None (confidence: high)
- Tên miền: target_customer = Cá nhân, doanh nghiệp muốn kinh doanh, giới thiệu online None (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.ten-mien.bang-gia
title: Tên Miền BKNS — Bảng Giá
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 69
compile_cost_usd: 0.0177
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:24:43.557784+07:00'
---

# Tên Miền BKNS — Bảng Giá

Trang này cung cấp bảng giá chi tiết cho các dịch vụ đăng ký, duy trì và chuyển đổi tên miền (domain) tại BKNS, bao gồm cả tên miền Việt Nam và tên miền Quốc tế.

Lưu ý: Tất cả các tên miền đều được **miễn phí phí cài đặt**.

## Bảng giá Tên miền Quốc tế

| Tên miền | Phí đăng ký (Năm đầu) | Phí duy trì (Các năm sau) | Phí Transfer về BKNS | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **.com** | 380.000 VNĐ | 429.000 VNĐ | 429.000 VNĐ | |
| **.net** | 435.000 VNĐ | 505.000 VNĐ | 505.000 VNĐ | |
| **.org** | 365.000 VNĐ | 535.000 VNĐ | 535.000 VNĐ | |
| **.biz** | 590.000 VNĐ | 740.000 VNĐ | 740.000 VNĐ | |
| **.info** | 170.000 VNĐ | 980.000 VNĐ | 980.000 VNĐ | Giá đăng ký khuyến mại áp dụng đến 06/01/2025 (giá gốc 890.000 VNĐ). |
| **.asia** | 440.000 VNĐ | 545.000 VNĐ | 545.000 VNĐ | |
| **.id** | 575.000 VNĐ | 575.000 VNĐ | 575.000 VNĐ | |
| **.me** | 745.000 VNĐ | 745.000 VNĐ | Đang cập nhật | |
| **.us** | 340.000 VNĐ | 380.000 VNĐ | 380.000 VNĐ | |
| **.ws** | 505.000 VNĐ | 1.075.000 VNĐ | 1.075.000 VNĐ | |

## Bảng giá Tên miền Việt Nam
*(Bảng giá có hiệu lực từ ngày 01/09/2025)*

| Tên miền | Phí đăng ký | Phí duy trì | Phí Transfer về BKNS |
| :--- | :--- | :--- | :--- |
| **.name.vn** | 30.000 VNĐ | 30.000 VNĐ | Miễn phí |
| **.io.vn** | 30.000 VNĐ | 30.000 VNĐ | Miễn phí |

## Dịch vụ & Chính sách khác
- **Xác thực 2 bước (2FA) cho tên miền:** Miễn phí.
- **Chuyển tên miền Việt Nam về BKNS:** Miễn phí.

### Xem thêm
- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.ten-mien.cau-hoi-thuong-gap
title: Tên Miền BKNS — Câu Hỏi Thường Gặp
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T13:24:43.561443+07:00'
---

# Tên Miền BKNS — Câu Hỏi Thường Gặp

> FAQ cho Tên Miền BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### chinh-sach.md

---
page_id: wiki.products.ten-mien.chinh-sach
title: Tên Miền BKNS — Chính Sách
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 3
compile_cost_usd: 0.0047
self_review: pass
corrections: 0
approved_at: '2026-04-07T13:24:43.564607+07:00'
---

# Tên Miền BKNS — Chính Sách

Tổng hợp các chính sách, điều khoản và cam kết dịch vụ áp dụng cho sản phẩm Tên miền tại BKNS.

## Quyền sở hữu và Thanh toán

- **Quyền sở hữu:** Khách hàng được đảm bảo **quyền sở hữu hợp pháp tuyệt đối** đối với tên miền đã đăng ký thông qua hệ thống định danh eKYC 100% online.
- **Chính sách giá:** Phí đăng ký và gia hạn tên miền được tính theo đơn vị **năm**.

## Chính sách chuyển tên miền (Transfer-in)

| Dịch vụ | Chi phí |
| :--- | :--- |
| Chuyển tên miền Việt Nam về BKNS | 0 VNĐ |

*Lưu ý: Chính sách miễn phí áp dụng cho việc chuyển tên miền quốc gia Việt Nam về quản lý tại BKNS.*

## Cam kết chất lượng dịch vụ (SLA)

Đang cập nhật.

## Chính sách dùng thử (Trial)

Đang cập nhật.

## Chính sách hoàn tiền

Đang cập nhật.

## Hỗ trợ kỹ thuật

- **Kênh hỗ trợ (Hotline, Email, Ticket):** Đang cập nhật.
- **Thời gian phản hồi:** Đang cập nhật.

## Điều khoản sử dụng

Đang cập nhật.

## Chính sách sao lưu (Backup)

Đang cập nhật.

---

### Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### chuyen-doi.md

---
page_id: wiki.products.ten-mien.chuyen-doi
title: Tên Miền — Chuyển Đổi (Transfer)
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 17
compile_cost_usd: 0.0066
self_review: fail
corrections: 2
approved_at: '2026-04-07T13:24:43.568017+07:00'
---

# Tên Miền — Chuyển Đổi (Transfer)

Trang này cung cấp thông tin chi tiết về dịch vụ chuyển đổi (transfer) tên miền về quản lý tại BKNS, bao gồm chính sách và bảng phí áp dụng.

## Phí Transfer Tên Miền

BKNS hỗ trợ chuyển đổi tên miền từ các nhà đăng ký khác về BKNS. Dưới đây là chi phí áp dụng cho từng loại tên miền.

**Chính sách đặc biệt cho tên miền Việt Nam:**

BKNS miễn phí transfer cho tất cả các tên miền Việt Nam khi chuyển về BKNS.

**Bảng phí transfer tên miền Quốc tế:**

| Loại Tên Miền | Phí Transfer về BKNS (VNĐ) |
| :--- | :--- |
| .com | 429.000 |
| .net | 505.000 |
| .org | 535.000 |
| .biz | 740.000 |
| .info | 980.000 |
| .asia | 545.000 |
| .id | 575.000 |
| .us | 380.000 |
| .ws | 1.075.000 |

## Quy trình Transfer

[NỘI DUNG CẦN BỔ SUNG: Các bước chi tiết để transfer tên miền về BKNS.]

## Điều kiện Transfer

[NỘI DUNG CẦN BỔ SUNG: Các điều kiện cần đáp ứng để có thể transfer tên miền (ví dụ: tên miền đã hoạt động trên 60 ngày, không ở trạng thái tranh chấp...).]

## Thời gian hoàn tất

[NỘI DUNG CẦN BỔ SUNG: Thời gian dự kiến để hoàn tất quá trình transfer cho từng loại tên miền.]

## Sản phẩm liên quan

- [Hosting BKNS](../hosting/index.md)
- [Email BKNS](../email/index.md)
- [SSL Certificate BKNS](../ssl/index.md)

---

---

### huong-dan.md

---
page_id: wiki.products.ten-mien.huong-dan
title: Tên Miền BKNS — Hướng Dẫn
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 17
compile_cost_usd: 0.009
self_review: fail
corrections: 2
approved_at: '2026-04-07T13:24:43.570672+07:00'
---

# Tên Miền BKNS — Hướng Dẫn

Hướng dẫn này cung cấp các thông tin cần thiết để đăng ký, kích hoạt và quản lý dịch vụ Tên miền tại BKNS.

Tại BKNS, tất cả các loại tên miền đều được **miễn phí cài đặt**.

### 1. Hướng dẫn Đăng ký Tên miền

Quá trình đăng ký tên miền tại BKNS được thực hiện hoàn toàn trực tuyến. Một bước quan trọng trong quy trình là xác thực định danh điện tử **eKYC 100% online**, giúp đảm bảo quyền sở hữu hợp pháp tuyệt đối cho chủ thể.

*Các bước chi tiết khác: Đang cập nhật.*

### 2. Hướng dẫn Kích hoạt và Triển khai

Sau khi hoàn tất đăng ký và xác thực eKYC thành công, tên miền của bạn sẽ được kích hoạt.

*Hướng dẫn chi tiết về việc trỏ tên miền và cấu hình kỹ thuật: Đang cập nhật.*

### 3. Hướng dẫn Quản lý và Sử dụng

BKNS cung cấp các tùy chọn bảo mật nâng cao để bảo vệ tài sản tên miền của bạn.

*   **Xác thực 2 bước (2FA):** Với tính năng này, chủ thể có thể tự mở khóa tên miền trực tiếp tại nhà đăng ký khi cần thực hiện thay đổi.
*   **Bảo vệ tên miền cấp cao nhất (Registry Lock):** Đây là dịch vụ bảo mật cấp cao nhất. Quy trình Mở/Khóa dịch vụ yêu cầu một quy trình xác thực đa bên phức tạp giữa chủ thể, nhà đăng ký (BKNS) và Trung tâm Internet Việt Nam (VNNIC). VNNIC là đơn vị cuối cùng thực hiện Mở/Khóa dịch vụ theo yêu cầu đã được xác thực.

*Hướng dẫn quản lý các tác vụ khác (gia hạn, transfer, quản lý DNS): Đang cập nhật.*

### Bảng giá Tên miền Quốc tế

BKNS miễn phí hoàn toàn phí cài đặt cho tất cả các loại tên miền. Để biết chi phí đăng ký, duy trì và transfer chi tiết, vui lòng tham khảo bảng giá chính thức trên website BKNS.

| Tên miền | Phí cài đặt |
| :--- | :--- |
| .com | Miễn phí |
| .net | Miễn phí |
| .org | Miễn phí |
| .info (KM) | Miễn phí |
| .biz | Miễn phí |
| .asia | Miễn phí |
| .id | Miễn phí |

### 4. Xử lý sự cố thường gặp

*Đang cập nhật.*

### Sản phẩm liên quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Email Doanh Nghiệp BKNS](../email/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)

---

### index.md

---
page_id: wiki.products.ten-mien.index
title: Tên Miền BKNS — Trang Tổng Quan
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 9
compile_cost_usd: 0.006
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:24:43.573502+07:00'
---

# Tên Miền BKNS — Trang Tổng Quan

Dịch vụ Tên miền (Domain) tại BKNS cho phép khách hàng đăng ký và quản lý tên miền quốc tế & Việt Nam (.vn). Dịch vụ cung cấp bảng giá chi tiết cho việc đăng ký mới, duy trì (gia hạn), và transfer các loại tên miền.

Đối tượng khách hàng chính là các cá nhân, tổ chức và doanh nghiệp muốn sở hữu địa chỉ website riêng để xây dựng thương hiệu, kinh doanh trực tuyến hoặc tạo email theo tên miền riêng.

Một số tính năng nổi bật của dịch vụ bao gồm khả năng quản lý DNS linh hoạt, cho phép thay đổi địa chỉ IPv6 của tên miền thông qua Control Panel.

## Mục Lục

- [Tổng quan về Dịch vụ Tên miền](tong-quan.md)
- [Bảng giá Tên miền](bang-gia.md)
- [Thông số Kỹ thuật](thong-so.md)
- [Tính năng Nổi bật](tinh-nang.md)
- [Chính sách & Quy định](chinh-sach.md)
- [Câu hỏi Thường gặp (FAQ)](cau-hoi-thuong-gap.md)
- [So sánh các Gói dịch vụ](so-sanh.md)
- [Hướng dẫn Sử dụng](huong-dan.md)

## Sản phẩm & Dịch vụ con

- **[Bảo vệ Tên miền Cấp cao nhất](san-pham/bao-ve-ten-mien-cap-cao-nhat.md)**: Dành cho bất kỳ ai sở hữu tên miền quan trọng, bao gồm các tổ chức tài chính, ngân hàng, cơ quan chính phủ, và công ty thương mại điện tử lớn.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/chuyen-ten-mien.md

---
page_id: wiki.products.ten-mien.san-pham.chuyen-ten-mien
title: Chuyển Tên Miền (Transfer)
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 17
compile_cost_usd: 0.007
self_review: fail
corrections: 3
approved_at: '2026-04-07T13:24:43.576396+07:00'
---

# Chuyển Tên Miền (Transfer)

Chuyển tên miền (transfer domain) là quá trình di chuyển quyền quản lý tên miền của bạn từ một nhà đăng ký khác về hệ thống của BKNS. Trang này cung cấp thông tin chi tiết về chi phí và chính sách transfer tại BKNS.

## Phí Chuyển Tên Miền (Transfer Fee)

Chi phí transfer tên miền về BKNS được quy định khác nhau tùy thuộc vào loại tên miền (Quốc tế hoặc Việt Nam).

### Tên miền Quốc tế

Dưới đây là bảng giá chi phí transfer áp dụng cho các tên miền quốc tế phổ biến.

| Tên miền | Phí Transfer về BKNS (VND) |
| :--- | :--- |
| .com | 429.000 |
| .net | 505.000 |
| .org | 535.000 |
| .biz | 740.000 |
| .info | 980.000 |
| .asia | 545.000 |
| .id | 575.000 |
| .us | 380.000 |
| .ws | 1.075.000 |

### Tên miền Việt Nam

BKNS áp dụng chính sách **miễn phí** khi chuyển tên miền Việt Nam về hệ thống.

## Quy trình, Điều kiện và Thời gian Transfer

Nội dung đang được cập nhật.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---

### san-pham/dang-ky-ten-mien.md

---
page_id: wiki.products.ten-mien.san-pham.dang-ky-ten-mien
title: Đăng Ký Tên Miền BKNS
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 17
compile_cost_usd: 0.0074
self_review: fail
corrections: 2
approved_at: '2026-04-07T13:24:43.579658+07:00'
---

# Đăng Ký Tên Miền BKNS

BKNS hỗ trợ đăng ký nhiều loại tên miền Việt Nam và Quốc tế, giúp khách hàng xây dựng và khẳng định thương hiệu trên Internet. Dưới đây là thông tin chi tiết về các đuôi tên miền được hỗ trợ và bảng giá đăng ký.

### Bảng Giá Đăng Ký Tên Miền

Bảng giá dưới đây tổng hợp phí đăng ký mới cho các đuôi tên miền tại BKNS.

| Tên miền | Phí đăng ký (VNĐ) |
| :--- | :--- |
| .asia | 440.000 |
| .biz | 590.000 |
| .com | 380.000 |
| .id | 575.000 |
| .info | 170.000* |
| .io.vn | 30.000 |
| .me | 745.000 |
| .name.vn | 30.000 |
| .net | 435.000 |
| .org | 365.000 |
| .us | 340.000 |
| .ws | 505.000 |

*\* Ghi chú: Tên miền .info áp dụng giá khuyến mại 170.000đ (giá gốc 890.000đ) đến hết ngày 06/01/2025.*

### Quy Trình Đăng Ký

[NỘI DUNG CẦN BỔ SUNG: Mô tả các bước đăng ký tên miền tại BKNS, ví dụ: 1. Kiểm tra tên miền, 2. Thêm vào giỏ hàng, 3. Khai báo thông tin, 4. Thanh toán, 5. Xác thực và kích hoạt.]

### Hồ Sơ Cần Thiết

[NỘI DUNG CẦN BỔ SUNG: Liệt kê các giấy tờ cần thiết cho cá nhân và tổ chức khi đăng ký tên miền Việt Nam và Quốc tế theo quy định.]

### Sản Phẩm Liên Quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Email Doanh Nghiệp BKNS](../email/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • [NGÀY CẬP NHẬT THỰC TẾ]

---

### so-sanh.md

---
page_id: wiki.products.ten-mien.so-sanh
title: Tên Miền BKNS — So Sánh
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 1
compile_cost_usd: 0.0037
self_review: skipped
corrections: 0
approved_at: '2026-04-07T13:24:43.582174+07:00'
---

# Tên Miền BKNS — So sánh

Trang này cung cấp thông tin so sánh giữa các loại tên miền do BKNS cung cấp, giúp người dùng đưa ra lựa chọn phù hợp với nhu cầu.

Do dữ liệu về các loại tên miền khác nhau đang trong quá trình tổng hợp, trang này hiện chỉ cung cấp thông tin nổi bật đã được xác thực.

## Lợi thế nổi bật

Dựa trên dữ liệu hiện có, tên miền do BKNS cung cấp có một lợi thế quan trọng liên quan đến SEO tại thị trường Việt Nam.

| Tính năng | Mô tả | Ghi chú |
| :--- | :--- | :--- |
| **Lợi thế SEO Local** | Lợi thế SEO Local vượt trội | Google ưu tiên hiển thị các website có tên miền `.VN` khi người dùng tìm kiếm từ các địa chỉ IP tại Việt Nam. |

Bảng so sánh chi tiết về giá và tính năng giữa các đuôi tên miền khác nhau (ví dụ: .VN, .COM, .COM.VN, .NET...) đang được cập nhật.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### thong-so.md

---
page_id: wiki.products.ten-mien.thong-so
title: Tên Miền BKNS — Thông Số Kỹ Thuật
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T13:24:43.584676+07:00'
---

# Tên Miền BKNS — Thông Số Kỹ Thuật

> So sánh specs từng gói Tên Miền BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### tinh-nang.md

---
page_id: wiki.products.ten-mien.tinh-nang
title: Tên Miền BKNS — Tính Năng
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 4
compile_cost_usd: 0.004
self_review: skipped
corrections: 0
approved_at: '2026-04-07T13:24:43.587524+07:00'
---

# Tên Miền BKNS — Tính Năng

Trang này tổng hợp các tính năng nổi bật của dịch vụ Tên Miền do BKNS cung cấp, dựa trên các thông tin đã được kiểm duyệt.

### Quản trị

*   **Hỗ trợ DNS IPv6**
    Dịch vụ Tên miền BKNS bao gồm tính năng DNS hỗ trợ IPv6 miễn phí. Người dùng được phép thay đổi địa chỉ IPv6 của tên miền trực tiếp thông qua Control Panel.

### Bảo mật

*   **Bảo vệ tên miền cấp cao nhất (Registry Lock)**
    Tính năng này giúp ngăn chặn các thay đổi trái phép đối với thông tin liên hệ của tên miền, qua đó bảo vệ thông tin của chủ thể đăng ký.

### Hiệu suất

*   **Lợi thế SEO Local**
    Sử dụng tên miền `.VN` mang lại lợi thế về SEO tại thị trường Việt Nam, do Google ưu tiên hiển thị các kết quả từ tên miền này cho người dùng có địa chỉ IP Việt Nam.

### Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### tong-quan.md

---
page_id: wiki.products.ten-mien.tong-quan
title: Tên Miền BKNS — Tổng Quan Chi Tiết
category: products/ten-mien
updated: '2026-04-07'
review_state: approved
claims_used: 12
compile_cost_usd: 0.0125
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:24:43.590238+07:00'
---

# Tên Miền BKNS — Tổng Quan Chi Tiết

Dịch vụ Tên miền của BKNS là giải pháp toàn diện cho cá nhân, tổ chức và doanh nghiệp muốn sở hữu một địa chỉ website riêng, qua đó xây dựng thương hiệu, kinh doanh trực tuyến hoặc tạo email theo tên miền chuyên nghiệp. Dịch vụ này cung cấp các công cụ cần thiết để đăng ký, quản lý và bảo vệ tên miền quốc tế và Việt Nam (.vn).

### 1. Tổng Quan Dịch Vụ

**Dịch vụ Tên miền BKNS là gì?**

Đây là dịch vụ cho phép người dùng đăng ký và quản lý tên miền quốc tế & Việt Nam (.vn). BKNS cung cấp một quy trình hoàn chỉnh từ đăng ký mới, duy trì (gia hạn) cho đến chuyển đổi (transfer) tên miền, giúp khách hàng dễ dàng thiết lập và duy trì sự hiện diện trực tuyến của mình.

**Đối tượng phù hợp:**

*   **Khách hàng phổ thông:** Cá nhân, tổ chức và doanh nghiệp muốn sở hữu địa chỉ website riêng để kinh doanh hoặc giới thiệu trực tuyến.
*   **Khách hàng có yêu cầu bảo mật cao:** Các tổ chức tài chính, ngân hàng, cơ quan chính phủ, công ty thương mại điện tử lớn, tập đoàn, và bất kỳ ai sở hữu tên miền quan trọng cần được bảo vệ ở mức độ cao nhất.

### 2. Các Gói Dịch Vụ và Tính Năng

BKNS cung cấp dịch vụ đăng ký tên miền đi kèm các tính năng quản trị và một dịch vụ bảo mật nâng cao.

**2.1. Dịch vụ chính**
Cung cấp bảng giá chi tiết cho việc đăng ký mới, duy trì (gia hạn), và transfer các loại tên miền quốc tế và Việt Nam.

**2.2. Tính năng đi kèm miễn phí**
*   **DNS hỗ trợ IPv6:** Dịch vụ tên miền tại BKNS được tích hợp sẵn DNS hỗ trợ IPv6, cho phép thay đổi địa chỉ IPv6 của tên miền trực tiếp thông qua Control Panel.

**2.3. Dịch vụ bổ sung: Bảo vệ Tên miền Cấp cao nhất (Registry Lock)**
Đây là một sản phẩm bảo mật chuyên biệt dành cho các tên miền quan trọng.
*   **Tính năng chính:** Ngăn chặn các thay đổi trái phép đối với thông tin liên hệ của chủ thể đăng ký tên miền, đảm bảo an toàn tuyệt đối cho tài sản số.
*   **Đối tượng:** Phù hợp với bất kỳ ai sở hữu tên miền quan trọng.

### 3. Bảng Giá

Dịch vụ cung cấp bảng giá chi tiết cho các hoạt động liên quan đến tên miền.

| Loại Tên miền | Đăng ký mới | Gia hạn | Transfer |
| :--- | :--- | :--- | :--- |
| Tên miền Việt Nam | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Tên miền Quốc tế | Đang cập nhật | Đang cập nhật | Đang cập nhật |

*(Lưu ý: Bảng giá chi tiết có tại trang đăng ký dịch vụ chính thức).*

### 4. Điểm Nổi Bật (USP)

*   **Lợi thế SEO Local vượt trội:** Tên miền `.VN` được Google ưu tiên hiển thị cho người dùng có địa chỉ IP tại Việt Nam, giúp tăng hiệu quả tiếp cận thị trường nội địa.

### 5. Vị Trí Trong Hệ Sinh Thái BKNS

Tên miền là dịch vụ nền tảng và là bước đầu tiên để xây dựng sự hiện diện trên Internet. Khách hàng nên chọn dịch vụ Tên miền khi cần một địa chỉ định danh duy nhất. Sau khi có tên miền, bạn có thể kết hợp với các dịch vụ khác của BKNS như:
*   **[Web Hosting BKNS](../hosting/index.md):** Để xây dựng và vận hành website.
*   **[Email Doanh Nghiệp BKNS](../email/index.md):** Để tạo hệ thống email chuyên nghiệp theo tên miền riêng.
*   **[Chứng Chỉ SSL BKNS](../ssl/index.md):** Để bảo mật website và tăng uy tín thương hiệu.

### Sản Phẩm Liên Quan
- [Web Hosting BKNS](../hosting/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
*Nguồn tham khảo: [https://www.bkns.vn/ten-mien/dang-ky-ten-mien.html](https://www.bkns.vn/ten-mien/dang-ky-ten-mien.html)*

---


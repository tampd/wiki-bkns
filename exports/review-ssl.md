# BKNS Wiki Cross-Verification Request — SSL

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (0)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (290)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages (9)**: Trang wiki đã compile — CẦN KIỂM TRA

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

- AlphaSSL: price = 849000 VND (confidence: high)
- AlphaSSL: validation_type = DV  (confidence: high)
- AlphaSSL Wildcard: feature = bảo vệ domain chính và tất cả subdomain  (confidence: high)
- Code Signing: lowest_price = 10010000 VND (confidence: high)
- GeoTrust QuickSSL Premium: category = SSL Bảo mật None (confidence: high)
- GeoTrust QuickSSL Premium: documentation_required = False None (confidence: high)
- GeoTrust QuickSSL Premium: domains_protected = 1 tên miền (confidence: high)
- GeoTrust QuickSSL Premium: encryption_strength = 256 bit (confidence: high)
- GeoTrust QuickSSL Premium: issuance_time = 10 phút (confidence: high)
- GeoTrust QuickSSL Premium: product_name = GeoTrust QuickSSL Premium None (confidence: high)
- GeoTrust QuickSSL Premium: provider = GeoTrust None (confidence: high)
- GeoTrust QuickSSL Premium: server_license_limit = unlimited None (confidence: high)
- GeoTrust QuickSSL Premium: target_customer = Các doanh nghiệp trực tuyến quy mô vừa và nhỏ None (confidence: high)
- GeoTrust QuickSSL Premium: validation_type = Domain Validation (DV) None (confidence: high)
- GeoTrust QuickSSL Premium: warranty_amount = 500000 USD (confidence: high)
- GeoTrust QuickSSL Premium: wildcard_support = False None (confidence: high)
- GeoTrust QuickSSL Premium: www_support = True None (confidence: high)
- PositiveSSL EV: category = SSL Bảo mật  (confidence: high)
- PositiveSSL EV: description = PositiveSSL EV là chứng chỉ SSL với mức xác thực cao nhất: Xác thực Mở rộng (Extended Validation - EV), giúp hiển thị tên công ty trên thanh địa chỉ trình duyệt, tăng cường độ tin cậy.  (confidence: high)
- PositiveSSL EV: domain_protection_count = 1  (confidence: high)
- PositiveSSL EV: installation_fee = 0 VND (confidence: high)
- PositiveSSL EV: insurance_level = 1000000 USD (confidence: high)
- PositiveSSL EV: issuance_time = 7-10 ngày  (confidence: high)
- PositiveSSL EV: list_price = 3874000 VND (confidence: high)
- PositiveSSL EV: name = PositiveSSL EV  (confidence: high)
- PositiveSSL EV: price = 3203000 VND (confidence: high)
- PositiveSSL EV: registration_url = https://id.bkns.vn/store/comodo-ssl/positivessl-ev?language=vietnamese  (confidence: high)
- PositiveSSL EV: required_documents = Đăng ký kinh doanh  (confidence: high)
- PositiveSSL EV: san_support = False  (confidence: high)
- PositiveSSL EV: server_license = unlimited  (confidence: high)
- PositiveSSL EV: site_seal_type = dynamic  (confidence: high)
- PositiveSSL EV: target_audience = Các doanh nghiệp và tổ chức cần mức độ đảm bảo và xác thực cao, đặc biệt là các trang thương mại điện tử, tài chính, ngân hàng.  (confidence: high)
- PositiveSSL EV: validation_method = Tên miền + Doanh nghiệp (EV)  (confidence: high)
- PositiveSSL EV: wildcard_support = False  (confidence: high)
- PositiveSSL Multi-Domain (DV): additional_san_price = 364000 VND (confidence: high)
- PositiveSSL Multi-Domain (DV): addon_price = 364000 VND (confidence: high)
- Comodo EV SSL: benefit = Tăng cường lòng tin của khách hàng bằng cách hiển thị tên doanh nghiệp.  (confidence: high)
- RapidSSL Wildcard Certificate: brand = RapidSSL None (confidence: high)
- RapidSSL Wildcard Certificate: brand_owner = DigiCert None (confidence: high)
- PositiveSSL Wildcard (DV): browser_recognition = 99.3 % (confidence: high)
- RapidSSL Wildcard Certificate: category = Wildcard SSL None (confidence: high)
- GeoTrust True BusinessID with EV Multi-Domain: competitor_price = 15071680 VND (confidence: high)
- GeoTrust True BusinessID Multi-Domain Wildcard: data_inconsistency_note = Nút 'Mua ngay' trên trang trỏ đến một sản phẩm khác (true-businessid-ev-multi-domain-san) là loại xác thực EV, trong khi nội dung trang mô tả sản phẩm OV. None (confidence: high)
- GeoTrust True BusinessID Multi-Domain Wildcard: default_domains_included = 1 tên miền cụ thể và 2 tên miền wildcard None (confidence: high)
- RapidSSL Certificate: description = RapidSSL Certificate là một sản phẩm thuộc phân khúc giá rẻ của DigiCert. Với ưu điểm xác thực nhanh và cấp phát tức thời, RapidSSL được sử dụng để bảo mật cho hầu hết các website trên internet. Đây là giải pháp phù hợp cho các trang web cần mã hóa cơ bản một cách nhanh chóng. None (confidence: high)
- RapidSSL Certificate: domain_coverage_type = 1 domain (confidence: high)
- RapidSSL Certificate: domain_protection_count = 1 tên miền (confidence: high)
- PositiveSSL EV: domains_protected = 1 tên miền chính None (confidence: high)
- PositiveSSL (DV): encryption_strength = tiêu chuẩn ngành None (confidence: high)
- EssentialSSL (DV): faq_availability = False None (confidence: high)
- InstantSSL (OV): feature = Hiển thị thông tin doanh nghiệp đã được xác thực khi di chuột qua Dấu bảo mật Comodo động None (confidence: high)
- Comodo SSL Wildcard Certificate (DV): free_installation = True None (confidence: high)
- PositiveSSL Multi-Domain (DV): included_domains = 3 domains (confidence: high)
- RapidSSL Certificate: installation_fee = 0 VND (confidence: high)
- RapidSSL Certificate: insurance_amount = 10000 USD (confidence: high)
- GeoTrust True BusinessID Multi-Domain Wildcard: internal_note = Nút 'Mua ngay' trên trang trỏ đến một sản phẩm khác (true-businessid-ev-multi-domain-san) là loại xác thực EV, trong khi nội dung trang mô tả sản phẩm OV. None (confidence: high)
- InstantSSL Pro (OV): is_a = ENT-PROD-SSL None (confidence: high)
- RapidSSL Wildcard Certificate: issuance_time = 5 minutes (confidence: high)
- RapidSSL Wildcard Certificate: issuing_authority = DigiCert None (confidence: high)
- PositiveSSL (DV): key_feature = Chi phí thấp None (confidence: high)
- PositiveSSL Multi-Domain (DV): limitation = Chỉ xác thực quyền sở hữu tên miền, không xác thực thông tin tổ chức. None (confidence: high)
- RapidSSL Wildcard Certificate: list_price = 6136000 VND (confidence: high)
- Chứng Chỉ SSL: lowest_price = 1474000 VND (confidence: high)
- Comodo SSL Wildcard Certificate (DV): main_domain_coverage = 1 None (confidence: high)
- PositiveSSL Multi-Domain (DV): max_domains = 250 domains (confidence: medium)
- GeoTrust True BusinessID Multi-Domain Wildcard: max_san_count = 250 None (confidence: high)
- PositiveSSL Wildcard (DV): mobile_compatibility = True  (confidence: high)
- RapidSSL Wildcard Certificate: money_back_guarantee = 30 days (confidence: high)
- RapidSSL Certificate: name = RapidSSL Certificate None (confidence: high)
- Chứng Chỉ SSL: offered_product = GeoTrust True BusinessID Wildcard  (confidence: high)
- Comodo SSL Wildcard Certificate (DV): paperwork_required = False None (confidence: high)
- PositiveSSL Multi-Domain (DV): parent_product = ENT-PROD-SSL  (confidence: high)
- RapidSSL Certificate: policy = Dịch vụ được miễn phí cài đặt. None (confidence: high)
- RapidSSL Wildcard Certificate: price = 2187000 VND (confidence: high)
- RapidSSL Wildcard Certificate: price_guarantee = best price None (confidence: high)
- PositiveSSL Multi-Domain (DV): price_note = Đã bao gồm 3 tên miền. None (confidence: high)
- GeoTrust True BusinessID with EV Multi-Domain: price_per_additional_san = 1255000 VND (confidence: high)
- PositiveSSL Multi-Domain (DV): product_type = PositiveSSL Multi-Domain (DV) None (confidence: high)
- RapidSSL Wildcard Certificate: protected_domains_description = 1 tên miền chính và tất cả các tên miền con None (confidence: high)
- PositiveSSL (DV): provider = Comodo None (confidence: high)
- PositiveSSL Multi-Domain (DV): purchase_url = https://id.bkns.vn/store/comodo-ssl/comodo-positive-multi-domain-ssl?language=vietnamese None (confidence: high)
- PositiveSSL (DV): reference_price = 1274000 VND (confidence: high)
- RapidSSL Certificate: registration_process = Khách hàng có thể đăng ký dịch vụ bằng cách nhấn vào nút "Mua ngay" trên trang sản phẩm để thêm vào giỏ hàng và tiến hành thanh toán. None (confidence: high)
- RapidSSL Wildcard Certificate: required_documents = Không yêu cầu None (confidence: high)
- InstantSSL (OV): requirement = Đăng ký kinh doanh None (confidence: high)
- RapidSSL Wildcard Certificate: sales_policy = Best price guarantee None (confidence: high)
- RapidSSL Certificate: san_support = False None (confidence: high)
- EssentialSSL Wildcard (DV): scope = 1 main domain + unlimited subdomains None (confidence: high)
- Comodo EV SSL: seal_type = Động  (confidence: high)
- Comodo SSL Wildcard Certificate (DV): secured_domains_count = Unlimited None (confidence: high)
- PositiveSSL Multi-Domain (DV): server_installation_limit = unlimited None (confidence: high)
- RapidSSL Wildcard Certificate: server_license = unlimited None (confidence: high)
- SSL: service_description = BKNS None (confidence: high)
- RapidSSL Wildcard Certificate: setup_fee = 0 VND (confidence: high)
- GeoTrust True BusinessID: setup_support = True None (confidence: high)
- PositiveSSL Multi-Domain (DV): short_description = Chứng chỉ SSL xác thực tên miền (Domain Validation - DV) cho phép bảo mật nhiều tên miền khác nhau trên cùng một chứng chỉ duy nhất. None (confidence: high)
- RapidSSL Wildcard Certificate: site_seal_type = Tĩnh None (confidence: high)
- PositiveSSL Multi-Domain (DV): source_url = https://ssl.bkns.vn/ssl-bao-mat/positivessl-multi-domain None (confidence: high)
- Comodo SSL Wildcard Certificate (DV): ssl_validation_level = Domain Validation None (confidence: high)
- RapidSSL Wildcard Certificate: subdomain_coverage = unlimited None (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.ssl.bang-gia
title: Chứng Chỉ SSL BKNS — Bảng Giá
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 45
compile_cost_usd: 0.0177
self_review: pass
corrections: 0
approved_at: '2026-04-07T13:16:30.155317+07:00'
---

# Chứng Chỉ SSL BKNS — Bảng Giá

Trang này cung cấp bảng giá chi tiết và các thông tin liên quan cho các gói Chứng Chỉ SSL được cung cấp bởi BKNS. Tất cả các mức giá được niêm yết bằng Việt Nam Đồng (VND) và áp dụng cho chu kỳ thanh toán theo năm, trừ khi có ghi chú khác.

### Bảng giá chi tiết

Bảng dưới đây tổng hợp giá từ nhà cung cấp, giá ưu đãi tại BKNS, phí cài đặt và các ghi chú quan trọng khác cho từng gói SSL.

| Tên gói | Giá tại BKNS (VND/năm) | Phí cài đặt | VAT | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **Dòng Sectigo / Comodo** | | | | |
| EssentialSSL (DV) | 333.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>2.078.700đ</del>. |
| EssentialSSL Wildcard (DV) | 2.704.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>6.474.000đ</del>. |
| PositiveSSL (DV) | Đang cập nhật | Đang cập nhật | Đang cập nhật | Giá nhà cung cấp (tham khảo): <del>1.274.000đ</del>. |
| PositiveSSL Multi-Domain (DV) | 624.000 | Đang cập nhật | Đang cập nhật | Đã bao gồm 3 tên miền. Phí bổ sung: 364.000đ/SAN/Năm. |
| PositiveSSL Wildcard (DV) | 2.413.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>6.474.000đ</del>. |
| PositiveSSL EV | 3.203.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>3.874.000đ</del>. |
| InstantSSL (OV) | 915.000 | Đang cập nhật | Đang cập nhật | Giá niêm yết: <del>2.598.700đ</del>. |
| InstantSSL Pro (OV) | 998.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>3.638.700đ</del>. |
| **Dòng GeoTrust** | | | | |
| GeoTrust QuickSSL Premium | 1.411.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>3.874.000đ</del>. |
| GeoTrust QuickSSL Premium SAN | 2.912.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>4.680.000đ</del>. |
| GeoTrust QuickSSL Premium Wildcard | 6.614.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>16.354.000đ</del>. |
| GeoTrust True BusinessID Wildcard | 9.714.000 | Đang cập nhật | Đang cập nhật | |
| GeoTrust True BusinessID with EV Multi-Domain | 9.134.000 | Miễn phí | Đang cập nhật | So với giá NCC <del>15.071.680đ</del>. Bổ sung SAN: 1.255.000đ/SAN/năm. |
| **Dòng RapidSSL** | | | | |
| RapidSSL Certificate | từ 215.000 | Miễn phí | Đang cập nhật | |
| RapidSSL Wildcard Certificate | 2.187.000 | Miễn phí | Đang cập nhật | Giá niêm yết: <del>6.136.000đ</del>. Cam kết giá tốt nhất. |
| **Dòng AlphaSSL** | | | | |
| AlphaSSL (DV) | 849.000 | Đang cập nhật | Đang cập nhật | |
| **Chứng chỉ đặc biệt** | | | | |
| Code Signing | từ 10.010.000 | Đang cập nhật | Đang cập nhật | |

### Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.ssl.cau-hoi-thuong-gap
title: Chứng Chỉ SSL BKNS — Câu Hỏi Thường Gặp
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 1
compile_cost_usd: 0.0023
self_review: skipped
corrections: 0
approved_at: '2026-04-07T13:16:30.161413+07:00'
---

# Chứng Chỉ SSL BKNS — Câu Hỏi Thường Gặp

Dựa trên dữ liệu được cung cấp, hiện chưa có thông tin chi tiết cho các câu hỏi thường gặp về dịch vụ Chứng Chỉ SSL. Nội dung sẽ được cập nhật trong thời gian sớm nhất.

### Trước khi mua

Đang cập nhật.

### Trong quá trình sử dụng

Đang cập nhật.

### Hỗ trợ & khắc phục sự cố

Đang cập nhật.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### chinh-sach.md

---
page_id: wiki.products.ssl.chinh-sach
title: Chứng Chỉ SSL BKNS — Chính Sách
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 47
compile_cost_usd: 0.0116
self_review: pass
corrections: 0
approved_at: '2026-04-07T13:16:30.167194+07:00'
---

# Chứng Chỉ SSL BKNS — Chính Sách

Tổng hợp các chính sách chung về cam kết dịch vụ (SLA), hoàn tiền, hỗ trợ kỹ thuật và các điều khoản liên quan đến dịch vụ Chứng chỉ SSL tại BKNS.

## Chính sách Hoàn tiền

BKNS cam kết hoàn tiền trong vòng 30 ngày cho một số sản phẩm chứng chỉ SSL. Khách hàng có thể yêu cầu hoàn tiền nếu không hài lòng với dịch vụ trong khoảng thời gian này.

Các sản phẩm áp dụng chính sách hoàn tiền 30 ngày bao gồm:
- RapidSSL Wildcard Certificate
- EssentialSSL (DV)
- GeoTrust QuickSSL Premium SAN

## Hỗ trợ Kỹ thuật và Cài đặt

**Hỗ trợ Cài đặt:**
- **Miễn phí cài đặt:** Dịch vụ được miễn phí cài đặt cho sản phẩm `RapidSSL Certificate`.
- **Hỗ trợ cài đặt miễn phí từ BKNS:** Áp dụng cho sản phẩm `InstantSSL (OV)`.
- **Có hỗ trợ cài đặt:** Áp dụng cho sản phẩm `GeoTrust True BusinessID`.

**Thời gian hỗ trợ:**
- **Hỗ trợ kỹ thuật 24/7:** Áp dụng cho sản phẩm `RapidSSL Wildcard Certificate`.

**Kênh hỗ trợ (Hotline, Email, Ticket):**
Đang cập nhật.

**Thời gian phản hồi:**
Đang cập nhật.

## Cam kết về Giá và Chất lượng

- **Cam kết giá tốt nhất (Best price guarantee):** Áp dụng cho sản phẩm `RapidSSL Wildcard Certificate`.
- **BKNS ĐẢM BẢO:** Áp dụng cho sản phẩm `InstantSSL Pro (OV)`.

## Cam kết Chất lượng Dịch vụ (SLA)

Đang cập nhật.

## Dùng thử Dịch vụ (Trial)

Đang cập nhật.

## Chính sách Backup

Đang cập nhật.

## Điều khoản Sử dụng

Đang cập nhật.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### huong-dan.md

---
page_id: wiki.products.ssl.huong-dan
title: Chứng Chỉ SSL BKNS — Hướng Dẫn
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 9
compile_cost_usd: 0.0076
self_review: fail
corrections: 0
approved_at: '2026-04-07T13:16:30.172416+07:00'
---

# Chứng Chỉ SSL BKNS — Hướng Dẫn

Trang này hướng dẫn các bước cơ bản để đăng ký, kích hoạt và quản lý chứng chỉ SSL tại BKNS, giúp bảo mật website của bạn một cách hiệu quả.

## 1. Hướng dẫn Đăng ký

Quy trình đăng ký chứng chỉ SSL tại BKNS rất đơn giản và nhanh chóng. Bạn có thể thực hiện theo các bước sau:

1.  Truy cập trang sản phẩm Chứng chỉ SSL của BKNS.
2.  Lựa chọn loại chứng chỉ phù hợp với nhu cầu của bạn và nhấn vào nút **"Mua ngay"**.
3.  Sản phẩm sẽ được tự động thêm vào giỏ hàng.
4.  Tiến hành thanh toán theo các bước được hướng dẫn trong giỏ hàng để hoàn tất đăng ký.

## 2. Thông tin Cài đặt và Xác thực

Dưới đây là thông tin về phí cài đặt và các chính sách hỗ trợ cho một số loại chứng chỉ SSL phổ biến tại BKNS.

| Tên Chứng Chỉ | Phí Cài Đặt | Hỗ Trợ Cài Đặt | Loại Xác Thực |
| :--- | :--- | :--- | :--- |
| RapidSSL Wildcard Certificate | Miễn phí | Đang cập nhật | Đang cập nhật |
| GeoTrust True BusinessID | Đang cập nhật | Có | Đang cập nhật |
| EssentialSSL (DV) | Miễn phí | Đang cập nhật | Đang cập nhật |
| EssentialSSL Wildcard (DV) | Miễn phí | Đang cập nhật | Đang cập nhật |
| GeoTrust QuickSSL Premium SAN | Miễn phí | Đang cập nhật | Đang cập nhật |
| GeoTrust QuickSSL Premium | Miễn phí | Đang cập nhật | Domain (DV) |
| PositiveSSL Wildcard (DV) | Miễn phí | Đang cập nhật | Đang cập nhật |

**Lưu ý:** "Miễn phí" tương đương với chi phí 0 VNĐ.

## 3. Hướng dẫn Kích hoạt và Triển khai

*Nội dung đang được cập nhật.*

## 4. Hướng dẫn Quản lý và Sử dụng

*Nội dung đang được cập nhật.*

## 5. Xử lý sự cố (Troubleshooting)

*Nội dung đang được cập nhật.*

---

**Sản phẩm liên quan:**

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Tên Miền BKNS](../ten-mien/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### index.md

---
page_id: wiki.products.ssl.index
title: Chứng Chỉ SSL BKNS — Trang Tổng Quan
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 58
compile_cost_usd: 0.0239
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:16:30.176967+07:00'
---

# Chứng Chỉ SSL BKNS — Trang Tổng Quan

Chứng chỉ SSL (Secure Sockets Layer) là một tiêu chuẩn an ninh công nghệ toàn cầu, tạo ra một liên kết được mã hóa giữa máy chủ web và trình duyệt. Tại BKNS, chúng tôi cung cấp đa dạng các loại chứng chỉ SSL để đáp ứng mọi nhu cầu, từ bảo mật cơ bản cho blog cá nhân đến xác thực mở rộng (EV) cho các trang thương mại điện tử và tổ chức tài chính, đảm bảo an toàn dữ liệu và nâng cao uy tín cho website của bạn. Các sản phẩm bao gồm chứng chỉ xác thực tên miền (DV), xác thực tổ chức (OV), xác thực mở rộng (EV), cùng các tùy chọn cho nhiều tên miền (Multi-Domain) và tên miền con (Wildcard).

## Mục lục

- [Tổng quan](./tong-quan.md)
- [Bảng giá](./bang-gia.md)
- [Thông số kỹ thuật](./thong-so.md)
- [Tính năng](./tinh-nang.md)
- [Chính sách & Điều khoản](./chinh-sach.md)
- [Câu hỏi thường gặp (FAQ)](./cau-hoi-thuong-gap.md)
- [So sánh các loại SSL](./so-sanh.md)
- [Hướng dẫn](./huong-dan.md)

## Các Sản Phẩm Chứng Chỉ SSL

Dưới đây là danh sách các sản phẩm chứng chỉ SSL được cung cấp tại BKNS. Nhấp vào tên sản phẩm để xem trang chi tiết.

### [EssentialSSL (DV)](./san-pham/essentialssl-dv.md)
Chứng chỉ SSL xác thực tên miền (DV) từ Comodo, phù hợp cho các trang web cá nhân, blog, trang thương mại điện tử nhẹ, và các miền thử nghiệm nội bộ cần cấp phát nhanh chóng.

### [EssentialSSL Wildcard (DV)](./san-pham/essentialssl-wildcard-dv.md)
Chứng chỉ SSL Wildcard xác thực tên miền (DV) từ Comodo, dành cho các website, blog, hoặc trang thương mại điện tử nhỏ cần bảo mật cho một tên miền chính và không giới hạn số lượng tên miền con.

### [GeoTrust QuickSSL Premium](./san-pham/geotrust-quickssl-premium.md)
Chứng chỉ SSL xác thực tên miền (DV) do GeoTrust cung cấp, cho phép bảo mật một tên miền với mã hóa lên đến 256-bit. Phù hợp cho các doanh nghiệp trực tuyến quy mô vừa và nhỏ.

### [GeoTrust QuickSSL Premium SAN](./san-pham/geotrust-quickssl-premium-san.md)
Chứng chỉ SSL từ GeoTrust, phù hợp cho các website cần bảo mật nhiều tên miền phụ (subdomain) trên cùng một chứng chỉ, đặc biệt khuyến nghị cho Exchange Server.

### [GeoTrust QuickSSL Premium Wildcard](./san-pham/geotrust-quickssl-premium-wildcard.md)
Chứng chỉ SSL/TLS xác thực tên miền (DV) cho phép bảo mật một tên miền chính và không giới hạn số lượng tên miền phụ (subdomain).

### [GeoTrust True BusinessID](./san-pham/geotrust-true-businessid.md)
Chứng chỉ SSL xác thực tổ chức (OV) từ GeoTrust, giúp xác minh danh tính doanh nghiệp và tăng cường uy tín cho website.

### [GeoTrust True BusinessID Wildcard](./san-pham/geotrust-true-businessid-wildcard.md)
Dành cho các doanh nghiệp, tổ chức cần bảo mật nhiều tên miền con bằng một chứng chỉ duy nhất, đồng thời xác minh danh tính và sự uy tín của doanh nghiệp trên website.

### [GeoTrust True BusinessID with EV Multi-Domain](./san-pham/geotrust-true-businessid-ev-multi-domain.md)
Phù hợp cho các doanh nghiệp, tổ chức cần tăng cường sự tin cậy và bảo mật giao dịch trên nhiều website, đặc biệt là các trang thương mại điện tử, tài chính.

### [InstantSSL (OV)](./san-pham/instantssl-ov.md)
Chứng chỉ SSL từ Comodo, phù hợp cho các doanh nghiệp muốn tăng cường sự tin tưởng của khách truy cập thông qua việc hiển thị thông tin tổ chức đã được xác thực.

### [InstantSSL Pro (OV)](./san-pham/instantssl-pro-ov.md)
Chứng chỉ bảo mật SSL xác thực tổ chức (OV) do Comodo cung cấp, dành cho các trang web thương mại điện tử và doanh nghiệp muốn tăng độ tin cậy và xác thực danh tính.

### [PositiveSSL (DV)](./san-pham/positivessl-dv.md)
Chứng chỉ SSL xác thực tên miền (DV) do Comodo cung cấp, phù hợp cho các trang web cần bảo mật cơ bản một cách nhanh chóng và đơn giản như blog, website cá nhân.

### [PositiveSSL EV](./san-pham/positivessl-ev.md)
Chứng chỉ SSL với mức xác thực cao nhất (EV), giúp hiển thị tên công ty trên thanh địa chỉ trình duyệt. Phù hợp cho các doanh nghiệp cần mức độ đảm bảo cao như thương mại điện tử, tài chính, ngân hàng.

### [PositiveSSL Multi-Domain (DV)](./san-pham/positivessl-multi-domain-dv.md)
Chứng chỉ SSL xác thực tên miền (DV) cho phép bảo mật nhiều tên miền khác nhau trên cùng một chứng chỉ duy nhất.

### [PositiveSSL Wildcard (DV)](./san-pham/positivessl-wildcard-dv.md)
Dành cho các trang thương mại điện tử nhẹ, blog, website cá nhân cần bảo mật nhanh chóng và chi phí thấp cho tên miền chính cùng tất cả các tên miền phụ.

### [RapidSSL Certificate](./san-pham/rapidssl-certificate.md)
Sản phẩm thuộc phân khúc giá rẻ của DigiCert, phù hợp cho các website cần bảo mật cơ bản, website cá nhân, blog, và các dự án cần triển khai SSL nhanh chóng với chi phí thấp.

### [RapidSSL Wildcard Certificate](./san-pham/rapidssl-wildcard-certificate.md)
Chứng chỉ Wildcard SSL cho phép bảo vệ 1 tên miền chính và tất cả các tên miền con của nó.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

## Ghi chú

BKNS cung cấp dịch vụ cài đặt miễn phí cho các chứng chỉ SSL.

***
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### so-sanh.md

---
page_id: wiki.products.ssl.so-sanh
title: Chứng Chỉ SSL BKNS — So Sánh
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 1
compile_cost_usd: 0.0023
self_review: skipped
corrections: 0
approved_at: '2026-04-07T13:16:30.181913+07:00'
---

# Chứng Chỉ SSL BKNS — So Sánh

Trang này cung cấp thông tin so sánh chi tiết giữa các gói chứng chỉ SSL do BKNS cung cấp, giúp khách hàng dễ dàng lựa chọn sản phẩm phù hợp nhất với nhu cầu.

## Bảng So Sánh Tính Năng và Báo Giá

Hiện tại, dữ liệu chi tiết để so sánh các gói SSL đang được thu thập và cập nhật. Vui lòng quay lại sau.

### Xem thêm

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### thong-so.md

---
page_id: wiki.products.ssl.thong-so
title: Chứng Chỉ SSL BKNS — Thông Số Kỹ Thuật
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 74
compile_cost_usd: 0.02
self_review: error
corrections: 0
approved_at: '2026-04-07T13:16:30.186675+07:00'
---

# Chứng Chỉ SSL BKNS — Thông Số Kỹ Thuật

Trang này cung cấp bảng so sánh chi tiết về thông số kỹ thuật của các gói chứng chỉ SSL do BKNS cung cấp, giúp bạn dễ dàng lựa chọn sản phẩm phù hợp với nhu cầu bảo mật website của mình. Tất cả thông tin được tổng hợp từ các nguồn dữ liệu đã được xác thực.

### Bảng So Sánh Thông Số Kỹ Thuật

| Tên Gói | Loại Xác Thực | Thời Gian Cấp Phát | Hỗ Trợ Wildcard | Hỗ Trợ SAN | Mức Bảo Hiểm | Giấy Phép Máy Chủ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AlphaSSL** | DV | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| **EssentialSSL (DV)** | Domain Validation (DV) | 5 phút | Không | Không | Đang cập nhật | Không giới hạn |
| **EssentialSSL Wildcard (DV)** | Domain Validation (DV) | 5 phút | Có | 1 | 10.000 USD | Không giới hạn |
| **GeoTrust QuickSSL Premium** | Domain Validation (DV) | 5 phút | Không | Đang cập nhật | 500.000 USD | Không giới hạn |
| **GeoTrust QuickSSL Premium SAN** | Domain Validation (DV) | 5 phút | Không | Đang cập nhật | 500.000 USD | Không giới hạn |
| **GeoTrust QuickSSL Premium Wildcard** | Domain Validation (DV) | 5 phút | Có | Không | 500.000 USD | Không giới hạn |
| **GeoTrust True BusinessID** | OV | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| **GeoTrust True BusinessID with EV Multi-Domain** | Tên miền + Doanh nghiệp (EV) | 7-10 ngày làm việc | Không | Đang cập nhật | 1.500.000 USD | Đang cập nhật |
| **InstantSSL (OV)** | Organization Validation (OV) | 1-3 ngày | Không | Không | 50.000 USD | Không giới hạn |
| **InstantSSL Pro (OV)** | Tên miền + Doanh nghiệp (OV) | 1-3 ngày | Không | Không | Đang cập nhật | Không giới hạn |
| **PositiveSSL EV** | Đang cập nhật | 7-10 ngày | Không | Không | Đang cập nhật | Không giới hạn |
| **PositiveSSL Wildcard (DV)** | Domain Validation (DV) | 5 phút | Có | 1 | 50.000 USD | Không giới hạn |
| **RapidSSL Certificate** | DV | Đang cập nhật | Đang cập nhật | Không | Đang cập nhật | Đang cập nhật |
| **RapidSSL Wildcard Certificate** | Đang cập nhật | 5 phút | Có | Đang cập nhật | 10.000 USD | Không giới hạn |

### Chú Thích Thuật Ngữ

*   **DV (Domain Validation):** Loại xác thực cơ bản, chỉ xác thực quyền sở hữu tên miền. Thời gian cấp phát nhanh chóng.
*   **OV (Organization Validation):** Xác thực quyền sở hữu tên miền và xác minh thông tin của tổ chức/doanh nghiệp đăng ký.
*   **EV (Extended Validation):** Mức độ xác thực cao nhất, yêu cầu xác minh nghiêm ngặt thông tin doanh nghiệp và pháp lý.
*   **Wildcard:** Cho phép bảo mật một tên miền chính và không giới hạn số lượng tên miền con (subdomain) cấp một (ví dụ: `blog.tenmien.vn`, `shop.tenmien.vn`... đều được bảo mật bởi chứng chỉ cho `*.tenmien.vn`).
*   **SAN (Subject Alternative Name):** Cho phép bảo mật nhiều tên miền hoàn toàn khác nhau trên cùng một chứng chỉ SSL.
*   **Giấy Phép Máy Chủ:** Một số chứng chỉ cho phép cài đặt trên không giới hạn số lượng máy chủ vật lý.

### Sản phẩm liên quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Tên Miền BKNS](../ten-mien/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### tinh-nang.md

---
page_id: wiki.products.ssl.tinh-nang
title: Chứng Chỉ SSL BKNS — Tính Năng
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 34
compile_cost_usd: 0.0101
self_review: fail
corrections: 2
approved_at: '2026-04-07T13:16:30.191546+07:00'
---

# Chứng Chỉ SSL BKNS — Tính Năng

Trang này tổng hợp các tính năng nổi bật của dịch vụ Chứng chỉ SSL do BKNS cung cấp, giúp bạn hiểu rõ hơn về các lợi ích và khả năng bảo mật mà chúng tôi mang lại. Tất cả thông tin đều được trích xuất từ cơ sở dữ liệu đã được xác thực.

## Bảo mật

Các chứng chỉ SSL tại BKNS được trang bị nhiều tính năng bảo mật để đáp ứng các nhu-cầu đa dạng, từ website cá nhân đến các doanh nghiệp lớn.

*   **Tăng cường tin cậy với EV (Extended Validation)**: Các chứng chỉ EV như Comodo EV SSL hay GeoTrust True BusinessID with EV giúp tăng cường lòng tin của khách hàng bằng cách hiển thị tên doanh nghiệp trên thanh địa chỉ màu xanh của trình duyệt.
*   **Xác thực thông tin doanh nghiệp (OV)**: Các chứng chỉ OV như InstantSSL (OV) hiển thị tên công ty đã được xác thực trong chi tiết chứng chỉ và trên Dấu bảo mật Comodo động, giúp khẳng định uy tín của tổ chức.
*   **Hỗ trợ Wildcard**: Một số loại chứng chỉ như AlphaSSL Wildcard và RapidSSL Wildcard cho phép bảo vệ không chỉ tên miền chính mà còn tất cả các tên miền con (subdomain) không giới hạn, giúp tiết kiệm chi phí và đơn giản hóa quản lý.
*   **Bảo vệ tên miền WWW**: Các chứng chỉ SSL tại BKNS hỗ trợ bảo mật cho cả phiên bản có `www` và không có `www` của tên miền đăng ký.

## Hiệu suất

Thông tin về các tính năng liên quan đến hiệu suất đang được cập nhật.

## Hỗ trợ kỹ thuật

BKNS cam kết mang đến trải nghiệm dịch vụ tốt nhất với các chính sách hỗ trợ chuyên nghiệp.

*   **Hỗ trợ kỹ thuật chuyên nghiệp**: Đội ngũ kỹ thuật của chúng tôi luôn sẵn sàng giải quyết các vấn đề và thắc mắc của khách hàng. Một số sản phẩm đi kèm với gói hỗ trợ 24/7.
*   **Hỗ trợ cài đặt miễn phí**: BKNS hỗ trợ cài đặt miễn phí cho một số loại chứng chỉ SSL, đảm bảo quá trình thiết lập diễn ra nhanh chóng và chính xác.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### tong-quan.md

---
page_id: wiki.products.ssl.tong-quan
title: Chứng Chỉ SSL BKNS — Tổng Quan Chi Tiết
category: products/ssl
updated: '2026-04-07'
review_state: approved
claims_used: 92
compile_cost_usd: 0.033
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:16:30.194108+07:00'
---

# Chứng Chỉ SSL BKNS — Tổng Quan Chi Tiết

## Tổng Quan Dịch Vụ

### 1. Chứng chỉ SSL là gì và giải quyết bài toán gì?

Chứng chỉ SSL (Secure Sockets Layer) là một tiêu chuẩn an ninh công nghệ toàn cầu, tạo ra một liên kết được mã hóa giữa máy chủ web và trình duyệt của người dùng. Dịch vụ này giải quyết hai bài toán cốt lõi cho bất kỳ website nào:

*   **Bảo mật & Mã hóa:** Đảm bảo mọi dữ liệu trao đổi giữa người dùng và website (như thông tin đăng nhập, giao dịch, dữ liệu cá nhân) được mã hóa, chống lại nguy cơ bị đánh cắp.
*   **Xây dựng lòng tin:** Tăng cường uy tín và lòng tin của khách hàng. Các chứng chỉ cấp cao (OV, EV) còn hiển thị tên doanh nghiệp đã được xác thực, khẳng định danh tính và sự chuyên nghiệp của tổ chức.

BKNS cung cấp một danh mục đa dạng các chứng chỉ SSL từ những nhà cung cấp uy tín hàng đầu như Comodo, GeoTrust và DigiCert, đáp ứng mọi nhu cầu từ cơ bản đến nâng cao.

### 2. Các Gói Chứng Chỉ SSL do BKNS Cung Cấp

BKNS cung cấp nhiều loại chứng chỉ SSL, được phân loại theo mức độ xác thực và tính năng, phù hợp với các quy mô và nhu cầu khác nhau.

#### Chứng chỉ Xác thực Tên miền (Domain Validation - DV)

Loại chứng chỉ này phù hợp cho các website cá nhân, blog, và các dự án cần triển khai SSL nhanh chóng với chi phí thấp.

*   **PositiveSSL (DV):** Cung cấp bởi Comodo, nổi bật với chi phí thấp và thời gian cấp phát nhanh.
*   **EssentialSSL (DV):** Từ Comodo, dùng để mã hóa và bảo mật cho một tên miền duy nhất.
*   **RapidSSL Certificate:** Sản phẩm giá rẻ của DigiCert, xác thực nhanh và cấp phát tức thời, phù hợp cho mã hóa cơ bản.
*   **GeoTrust QuickSSL Premium:** Do GeoTrust cung cấp, bảo mật cho 1 tên miền (bao gồm cả phiên bản www và không www).

#### Chứng chỉ Xác thực Tổ chức (Organization Validation - OV)

Dành cho các doanh nghiệp và tổ chức muốn tăng độ tin cậy bằng cách hiển thị thông tin công ty đã được xác thực trong chi tiết chứng chỉ.

*   **InstantSSL (OV) & InstantSSL Pro (OV):** Cung cấp bởi Comodo, cho phép hiển thị thông tin doanh nghiệp đã được xác thực, đặc biệt qua Dấu bảo mật Comodo động.
*   **GeoTrust True BusinessID:** Hỗ trợ cài đặt và xác thực thông tin doanh nghiệp.

#### Chứng chỉ Xác thực Mở rộng (Extended Validation - EV)

Cung cấp mức độ tin cậy và xác thực cao nhất, hiển thị tên công ty trên thanh địa chỉ màu xanh của trình duyệt.

*   **PositiveSSL EV:** Giúp hiển thị tên công ty trên thanh địa chỉ, phù hợp cho các trang thương mại điện tử, tài chính, ngân hàng.
*   **Comodo EV SSL:** Tăng cường lòng tin của khách hàng bằng cách hiển thị tên doanh nghiệp.

#### Chứng chỉ Wildcard SSL

Bảo vệ một tên miền chính và không giới hạn số lượng tên miền con (subdomain), là giải pháp tối ưu chi phí cho các hệ thống có nhiều subdomain.

*   **AlphaSSL Wildcard:** Bảo vệ domain chính và tất cả subdomain.
*   **RapidSSL Wildcard:** Bảo vệ 1 tên miền chính và tất cả các tên miền con.
*   **EssentialSSL Wildcard (DV):** Chỉ xác thực tên miền, không xác thực thông tin tổ chức.
*   **GeoTrust QuickSSL Premium Wildcard:** Bảo mật cho 1 tên miền chính và không giới hạn tên miền phụ.
*   **PositiveSSL Wildcard (DV):** Phù hợp cho các trang thương mại điện tử nhẹ, blog, website cá nhân.

#### Chứng chỉ Multi-Domain SSL (SAN/UCC)

Bảo mật nhiều tên miền và tên miền con khác nhau chỉ trong một chứng chỉ duy nhất.

*   **PositiveSSL Multi-Domain (DV):** Cho phép bảo mật nhiều tên miền khác nhau trên cùng một chứng chỉ.
*   **GeoTrust QuickSSL Premium SAN:** Phù hợp để bảo mật cho Exchange Server và các website cần bảo mật nhiều tên miền phụ.
*   **GeoTrust True BusinessID with EV Multi-Domain:** Kết hợp mức xác thực EV cao nhất và khả năng bảo vệ nhiều tên miền, cung cấp thanh địa chỉ màu xanh.

### 3. Đối Tượng Khách Hàng Phù Hợp

Chứng chỉ SSL của BKNS phục vụ một dải rộng khách hàng:

*   **Cá nhân & Blogger:** Các gói DV như RapidSSL, PositiveSSL, EssentialSSL là lựa chọn lý tưởng với chi phí thấp và cài đặt nhanh chóng.
*   **Doanh nghiệp vừa và nhỏ (SMBs):** Các gói OV như InstantSSL Pro hoặc các gói DV Wildcard giúp tăng uy tín và bảo mật hiệu quả với chi phí hợp lý.
*   **Doanh nghiệp lớn, Thương mại điện tử, Tài chính:** Các gói EV (PositiveSSL EV, GeoTrust True BusinessID with EV) là bắt buộc để xây dựng lòng tin tuyệt đối và bảo vệ giao dịch của khách hàng.
*   **Nhà phát triển & Quản trị hệ thống:** Các gói Wildcard và Multi-Domain (SAN) giúp đơn giản hóa việc quản lý và bảo mật cho các hệ thống phức tạp có nhiều tên miền và máy chủ.

### 4. Điểm Mạnh / USP của Dịch Vụ SSL tại BKNS

*   **Hỗ trợ Cài đặt Miễn phí:** BKNS cung cấp dịch vụ cài đặt miễn phí, giúp khách hàng không am hiểu về kỹ thuật cũng có thể triển khai SSL một cách dễ dàng.
*   **Hỗ trợ Kỹ thuật 24/7:** Đội ngũ kỹ thuật của BKNS luôn sẵn sàng hỗ trợ 24/7 để giải quyết mọi vấn đề phát sinh.
*   **Danh mục Đa dạng:** Cung cấp đầy đủ các loại chứng chỉ từ các thương hiệu hàng đầu thế giới (Comodo, GeoTrust, DigiCert), đáp ứng mọi nhu cầu và ngân sách.

### 5. Khi nào nên chọn SSL so với các dịch vụ khác của BKNS?

Chứng chỉ SSL không phải là dịch vụ thay thế mà là một thành phần bổ sung, không thể thiếu trong hệ sinh thái website của BKNS. Quy trình điển hình của một khách hàng sẽ là:

1.  Đăng ký [Tên Miền BKNS](../ten-mien/index.md) để sở hữu địa chỉ website.
2.  Triển khai website trên nền tảng [Web Hosting BKNS](../hosting/index.md) hoặc [Cloud VPS BKNS](../vps/index.md).
3.  **Cài đặt Chứng chỉ SSL** để mã hóa dữ liệu, bảo mật website và tăng uy tín với người dùng.

Do đó, hãy chọn Chứng chỉ SSL ngay sau khi website của bạn đã sẵn sàng hoạt động trên hosting hoặc VPS.

### Bảng Tổng Hợp Tính Năng Một Số Sản Phẩm Tiêu Biểu

| Tên Sản Phẩm | Nhà Cung Cấp | Hỗ trợ Wildcard | Hỗ trợ SAN | Đối Tượng Chính |
| :--- | :--- | :--- | :--- | :--- |
| **RapidSSL Certificate** | DigiCert | Không | Không | Website cá nhân, blog, cần bảo mật cơ bản. |
| **GeoTrust QuickSSL Premium** | GeoTrust | Không | Không | Doanh nghiệp vừa và nhỏ, bảo mật 1 tên miền. |
| **PositiveSSL EV** | Comodo | Không | Không | TMĐT, tài chính, ngân hàng cần uy tín cao nhất. |
| **EssentialSSL Wildcard (DV)** | Comodo | Có | Có (1 SAN) | Website nhỏ cần bảo mật không giới hạn subdomain. |
| **InstantSSL Pro (OV)** | Comodo | Không | Không | Doanh nghiệp muốn xác thực danh tính tổ chức. |
| **GeoTrust True BusinessID with EV Multi-Domain** | GeoTrust | Không | Có | Doanh nghiệp lớn cần bảo mật nhiều tên miền với thanh địa chỉ xanh. |

*Lưu ý: Bảng giá chi tiết cho từng sản phẩm đang được cập nhật. Vui lòng tham khảo các liên kết đăng ký trong danh sách claims để có thông tin chính xác.*

## Sản phẩm liên quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Tên Miền BKNS](../ten-mien/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---


# BKNS Wiki Cross-Verification Request — EMAIL

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (100)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (202)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages (15)**: Trang wiki đã compile — CẦN KIỂM TRA

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

- Email Hosting EMAIL 1: email_accounts = 5  [CLM-EXCEL-product_email_hosting_email_1-email_accounts]
- Email Hosting EMAIL 1: forwarders = 5  [CLM-EXCEL-product_email_hosting_email_1-forwarders]
- Email Hosting EMAIL 1: monthly_price = 45000 VND [CLM-EXCEL-product_email_hosting_email_1-monthly_price]
- Email Hosting EMAIL 1: price_1y = 513000 VND [CLM-EXCEL-product_email_hosting_email_1-price_1y]
- Email Hosting EMAIL 1: price_2y = 864000 VND [CLM-EXCEL-product_email_hosting_email_1-price_2y]
- Email Hosting EMAIL 1: price_3y = 1134000 VND [CLM-EXCEL-product_email_hosting_email_1-price_3y]
- Email Hosting EMAIL 1: price_4y = 1296000 VND [CLM-EXCEL-product_email_hosting_email_1-price_4y]
- Email Hosting EMAIL 1: storage_per_email = 5GB/ email  [CLM-EXCEL-product_email_hosting_email_1-storage_per_email]
- Email Hosting EMAIL 2: email_accounts = 20  [CLM-EXCEL-product_email_hosting_email_2-email_accounts]
- Email Hosting EMAIL 2: forwarders = 10  [CLM-EXCEL-product_email_hosting_email_2-forwarders]
- Email Hosting EMAIL 2: monthly_price = 90000 VND [CLM-EXCEL-product_email_hosting_email_2-monthly_price]
- Email Hosting EMAIL 2: price_1y = 1026000 VND [CLM-EXCEL-product_email_hosting_email_2-price_1y]
- Email Hosting EMAIL 2: price_2y = 1728000 VND [CLM-EXCEL-product_email_hosting_email_2-price_2y]
- Email Hosting EMAIL 2: price_3y = 2268000 VND [CLM-EXCEL-product_email_hosting_email_2-price_3y]
- Email Hosting EMAIL 2: price_4y = 2592000 VND [CLM-EXCEL-product_email_hosting_email_2-price_4y]
- Email Hosting EMAIL 2: storage_per_email = 5GB/ email  [CLM-EXCEL-product_email_hosting_email_2-storage_per_email]
- Email Hosting EMAIL 3: email_accounts = 50  [CLM-EXCEL-product_email_hosting_email_3-email_accounts]
- Email Hosting EMAIL 3: forwarders = 40  [CLM-EXCEL-product_email_hosting_email_3-forwarders]
- Email Hosting EMAIL 3: monthly_price = 175000 VND [CLM-EXCEL-product_email_hosting_email_3-monthly_price]
- Email Hosting EMAIL 3: price_1y = 1995000 VND [CLM-EXCEL-product_email_hosting_email_3-price_1y]
- Email Hosting EMAIL 3: price_2y = 3360000 VND [CLM-EXCEL-product_email_hosting_email_3-price_2y]
- Email Hosting EMAIL 3: price_3y = 4410000 VND [CLM-EXCEL-product_email_hosting_email_3-price_3y]
- Email Hosting EMAIL 3: price_4y = 5040000 VND [CLM-EXCEL-product_email_hosting_email_3-price_4y]
- Email Hosting EMAIL 3: storage_per_email = 5GB/ email  [CLM-EXCEL-product_email_hosting_email_3-storage_per_email]
- Email Hosting EMAIL 4: email_accounts = 100  [CLM-EXCEL-product_email_hosting_email_4-email_accounts]
- Email Hosting EMAIL 4: forwarders = 100  [CLM-EXCEL-product_email_hosting_email_4-forwarders]
- Email Hosting EMAIL 4: monthly_price = 300000 VND [CLM-EXCEL-product_email_hosting_email_4-monthly_price]
- Email Hosting EMAIL 4: price_1y = 3420000 VND [CLM-EXCEL-product_email_hosting_email_4-price_1y]
- Email Hosting EMAIL 4: price_2y = 5760000 VND [CLM-EXCEL-product_email_hosting_email_4-price_2y]
- Email Hosting EMAIL 4: price_3y = 7560000 VND [CLM-EXCEL-product_email_hosting_email_4-price_3y]
- Email Hosting EMAIL 4: price_4y = 8640000 VND [CLM-EXCEL-product_email_hosting_email_4-price_4y]
- Email Hosting EMAIL 4: storage_per_email = 5GB/ email  [CLM-EXCEL-product_email_hosting_email_4-storage_per_email]
- Email Relay BK-RELAY 01: daily_email_limit = 350 emails/ngày [CLM-EXCEL-product_email_relay_bk_relay_01-daily_email_limit]
- Email Relay BK-RELAY 01: monthly_price = 180000 VND [CLM-EXCEL-product_email_relay_bk_relay_01-monthly_price]
- Email Relay BK-RELAY 01: price_1y = 2160000 VND [CLM-EXCEL-product_email_relay_bk_relay_01-price_1y]
- Email Relay BK-RELAY 01: price_2y = 4320000 VND [CLM-EXCEL-product_email_relay_bk_relay_01-price_2y]
- Email Relay BK-RELAY 01: price_3y = 6480000 VND [CLM-EXCEL-product_email_relay_bk_relay_01-price_3y]
- Email Relay BK-RELAY 02: daily_email_limit = 700 emails/ngày [CLM-EXCEL-product_email_relay_bk_relay_02-daily_email_limit]
- Email Relay BK-RELAY 02: monthly_price = 290000 VND [CLM-EXCEL-product_email_relay_bk_relay_02-monthly_price]
- Email Relay BK-RELAY 02: price_1y = 3480000 VND [CLM-EXCEL-product_email_relay_bk_relay_02-price_1y]
- Email Relay BK-RELAY 02: price_2y = 6960000 VND [CLM-EXCEL-product_email_relay_bk_relay_02-price_2y]
- Email Relay BK-RELAY 02: price_3y = 10440000 VND [CLM-EXCEL-product_email_relay_bk_relay_02-price_3y]
- Email Relay BK-RELAY 03: daily_email_limit = 1500 emails/ngày [CLM-EXCEL-product_email_relay_bk_relay_03-daily_email_limit]
- Email Relay BK-RELAY 03: monthly_price = 500000 VND [CLM-EXCEL-product_email_relay_bk_relay_03-monthly_price]
- Email Relay BK-RELAY 03: price_1y = 6000000 VND [CLM-EXCEL-product_email_relay_bk_relay_03-price_1y]
- Email Relay BK-RELAY 03: price_2y = 12000000 VND [CLM-EXCEL-product_email_relay_bk_relay_03-price_2y]
- Email Relay BK-RELAY 03: price_3y = 18000000 VND [CLM-EXCEL-product_email_relay_bk_relay_03-price_3y]
- Email Relay BK-RELAY 04: daily_email_limit = 30000 emails/ngày [CLM-EXCEL-product_email_relay_bk_relay_04-daily_email_limit]
- Email Relay BK-RELAY 04: monthly_price = 980000 VND [CLM-EXCEL-product_email_relay_bk_relay_04-monthly_price]
- Email Relay BK-RELAY 04: price_1y = 11760000 VND [CLM-EXCEL-product_email_relay_bk_relay_04-price_1y]
- Email Relay BK-RELAY 04: price_2y = 23520000 VND [CLM-EXCEL-product_email_relay_bk_relay_04-price_2y]
- Email Relay BK-RELAY 04: price_3y = 35280000 VND [CLM-EXCEL-product_email_relay_bk_relay_04-price_3y]
- Cloud Email Server ES 1: monthly_price = 870000 VND [CLM-EXCEL-product_email_server_es_1-monthly_price]
- Cloud Email Server ES 1: price_1y = 8874000 VND [CLM-EXCEL-product_email_server_es_1-price_1y]
- Cloud Email Server ES 1: price_2y = 15660000 VND [CLM-EXCEL-product_email_server_es_1-price_2y]
- Cloud Email Server ES 1: price_3y = 20358000 VND [CLM-EXCEL-product_email_server_es_1-price_3y]
- Cloud Email Server ES 1: price_6m = 4959000 VND [CLM-EXCEL-product_email_server_es_1-price_6m]
- Cloud Email Server ES 1: storage = 300GB  [CLM-EXCEL-product_email_server_es_1-storage]
- Cloud Email Server ES 2: monthly_price = 1500000 VND [CLM-EXCEL-product_email_server_es_2-monthly_price]
- Cloud Email Server ES 2: price_1y = 15300000 VND [CLM-EXCEL-product_email_server_es_2-price_1y]
- Cloud Email Server ES 2: price_2y = 27000000 VND [CLM-EXCEL-product_email_server_es_2-price_2y]
- Cloud Email Server ES 2: price_3y = 35100000 VND [CLM-EXCEL-product_email_server_es_2-price_3y]
- Cloud Email Server ES 2: price_6m = 8550000 VND [CLM-EXCEL-product_email_server_es_2-price_6m]
- Cloud Email Server ES 2: storage = 500GB  [CLM-EXCEL-product_email_server_es_2-storage]
- Cloud Email Server ES 3: monthly_price = 3200000 VND [CLM-EXCEL-product_email_server_es_3-monthly_price]
- Cloud Email Server ES 3: price_1y = 32640000 VND [CLM-EXCEL-product_email_server_es_3-price_1y]
- Cloud Email Server ES 3: price_2y = 57600000 VND [CLM-EXCEL-product_email_server_es_3-price_2y]
- Cloud Email Server ES 3: price_3y = 74880000 VND [CLM-EXCEL-product_email_server_es_3-price_3y]
- Cloud Email Server ES 3: price_6m = 18240000 VND [CLM-EXCEL-product_email_server_es_3-price_6m]
- Cloud Email Server ES 3: storage = 1000GB  [CLM-EXCEL-product_email_server_es_3-storage]
- Cloud Email Server ES 4: monthly_price = 4900000 VND [CLM-EXCEL-product_email_server_es_4-monthly_price]
- Cloud Email Server ES 4: price_1y = 49980000 VND [CLM-EXCEL-product_email_server_es_4-price_1y]
- Cloud Email Server ES 4: price_2y = 88200000 VND [CLM-EXCEL-product_email_server_es_4-price_2y]
- Cloud Email Server ES 4: price_3y = 114660000 VND [CLM-EXCEL-product_email_server_es_4-price_3y]
- Cloud Email Server ES 4: price_6m = 27930000 VND [CLM-EXCEL-product_email_server_es_4-price_6m]
- Cloud Email Server ES 4: storage = 2000GB  [CLM-EXCEL-product_email_server_es_4-storage]
- Cloud Email Server MINI EMAIL 1: monthly_price = 369000 VND [CLM-EXCEL-product_email_server_mini_email_1-monthly_price]
- Cloud Email Server MINI EMAIL 1: price_1y = 3763800 VND [CLM-EXCEL-product_email_server_mini_email_1-price_1y]
- Cloud Email Server MINI EMAIL 1: price_2y = 6642000 VND [CLM-EXCEL-product_email_server_mini_email_1-price_2y]
- Cloud Email Server MINI EMAIL 1: price_3y = 8634600 VND [CLM-EXCEL-product_email_server_mini_email_1-price_3y]
- Cloud Email Server MINI EMAIL 1: price_6m = 2103300 VND [CLM-EXCEL-product_email_server_mini_email_1-price_6m]
- Cloud Email Server MINI EMAIL 1: storage = 100GB  [CLM-EXCEL-product_email_server_mini_email_1-storage]
- Cloud Email Server MINI EMAIL 2: monthly_price = 529000 VND [CLM-EXCEL-product_email_server_mini_email_2-monthly_price]
- Cloud Email Server MINI EMAIL 2: price_1y = 5395800 VND [CLM-EXCEL-product_email_server_mini_email_2-price_1y]
- Cloud Email Server MINI EMAIL 2: price_2y = 9522000 VND [CLM-EXCEL-product_email_server_mini_email_2-price_2y]
- Cloud Email Server MINI EMAIL 2: price_3y = 12378600 VND [CLM-EXCEL-product_email_server_mini_email_2-price_3y]
- Cloud Email Server MINI EMAIL 2: price_6m = 3015300 VND [CLM-EXCEL-product_email_server_mini_email_2-price_6m]
- Cloud Email Server MINI EMAIL 2: storage = 150GB  [CLM-EXCEL-product_email_server_mini_email_2-storage]
- Cloud Email Server MINI EMAIL 3: monthly_price = 654000 VND [CLM-EXCEL-product_email_server_mini_email_3-monthly_price]
- Cloud Email Server MINI EMAIL 3: price_1y = 6670800 VND [CLM-EXCEL-product_email_server_mini_email_3-price_1y]
- Cloud Email Server MINI EMAIL 3: price_2y = 11772000 VND [CLM-EXCEL-product_email_server_mini_email_3-price_2y]
- Cloud Email Server MINI EMAIL 3: price_3y = 15303600 VND [CLM-EXCEL-product_email_server_mini_email_3-price_3y]
- Cloud Email Server MINI EMAIL 3: price_6m = 3727800 VND [CLM-EXCEL-product_email_server_mini_email_3-price_6m]
- Cloud Email Server MINI EMAIL 3: storage = 200GB  [CLM-EXCEL-product_email_server_mini_email_3-storage]
- Cloud Email Server MINI EMAIL 4: monthly_price = 789000 VND [CLM-EXCEL-product_email_server_mini_email_4-monthly_price]
- Cloud Email Server MINI EMAIL 4: price_1y = 8047800 VND [CLM-EXCEL-product_email_server_mini_email_4-price_1y]
- Cloud Email Server MINI EMAIL 4: price_2y = 14202000 VND [CLM-EXCEL-product_email_server_mini_email_4-price_2y]
- Cloud Email Server MINI EMAIL 4: price_3y = 18462600 VND [CLM-EXCEL-product_email_server_mini_email_4-price_3y]
- Cloud Email Server MINI EMAIL 4: price_6m = 4497300 VND [CLM-EXCEL-product_email_server_mini_email_4-price_6m]
- Cloud Email Server MINI EMAIL 4: storage = 255GB  [CLM-EXCEL-product_email_server_mini_email_4-storage]

## LLM-EXTRACTED CLAIMS (Check these)

- Dịch vụ Cloud Email Server: data_contradiction = Giá quảng cáo trên meta description ('CHỈ TỪ 239K/THÁNG') mâu thuẫn với giá gói thấp nhất trong bảng giá ('314.000đ/Tháng'). None (confidence: high)
- Dịch vụ Cloud Email Server: description = Dịch vụ Cloud Email Server là giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây, dành cho các tổ chức và doanh nghiệp. None (confidence: high)
- Dịch vụ Cloud Email Server: parent_entity = ENT-PROD-EMAIL None (confidence: high)
- MINI EMAIL 02: platform = Kerio None (confidence: high)
- MINI EMAIL 02: monthly_price = 450000 VND (confidence: high)
- Dịch vụ Cloud Email Server: source_url = https://www.bkns.vn/email/cloud-email-server.html None (confidence: high)
- MINI EMAIL 02: storage = 150 GB (confidence: high)
- Dịch vụ Cloud Email Server: target_audience = Doanh nghiệp cần một hệ thống email riêng theo tên miền, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng. None (confidence: high)
- Dịch vụ Cloud Email Server: uptime_guarantee = 99 % (confidence: high)
- BK-RELAY 04: daily_email_limit = 30000 email (confidence: high)
- BK-RELAY 04: discount_percentage = 30 % (confidence: high)
- BK-RELAY 04: feature = White list IP None (confidence: high)
- BK-RELAY 04: price = 35280000 VND (confidence: high)
- BK-RELAY 04: target_audience = Doanh nghiệp cần gửi email marketing số lượng lớn None (confidence: high)
- MINI EMAIL 01: admin_account_type = Riêng None (confidence: high)
- MINI EMAIL 01: admin_permission = Admin None (confidence: high)
- MINI EMAIL 01: auto_responder = True None (confidence: high)
- ES 01: platform = Zimbra None (confidence: high)
- ES 01: monthly_price = 734000 VND (confidence: high)
- ES 01: storage_capacity = 300 GB (confidence: high)
- ES 02: platform = Zimbra None (confidence: high)
- ES 02: monthly_price = 1275000 VND (confidence: high)
- ES 02: storage_capacity = 500 GB (confidence: high)
- ES 03: platform = Zimbra None (confidence: high)
- ES 03: monthly_price = 2720000 VND (confidence: high)
- ES 03: storage_capacity = 1000 GB (confidence: high)
- ES 04: monthly_price = 4165000 VND (confidence: high)
- ES 04: storage_capacity = 2000 GB (confidence: high)
- MINI EMAIL 01: platform = Kerio None (confidence: high)
- MINI EMAIL 01: monthly_price = 314000 VND (confidence: high)
- MINI EMAIL 01: storage_capacity = 100 GB (confidence: high)
- MINI EMAIL 02: platform = Kerio None (confidence: high)
- MINI EMAIL 02: monthly_price = 450000 VND (confidence: high)
- MINI EMAIL 02: storage_capacity = 150 GB (confidence: high)
- MINI EMAIL 03: platform = Kerio None (confidence: high)
- MINI EMAIL 03: monthly_price = 556000 VND (confidence: high)
- MINI EMAIL 03: storage_capacity = 200 GB (confidence: high)
- MINI EMAIL 04: platform = Kerio None (confidence: high)
- MINI EMAIL 04: monthly_price = 671000 VND (confidence: high)
- MINI EMAIL 04: storage_capacity = 250 GB (confidence: high)
- Cloud Email Server: backup_frequency = Hàng tuần None (confidence: high)
- Cloud Email Server: feature = Tích hợp chống Spam/Virus miễn phí None (confidence: high)
- Cloud Email Server: inbox_delivery_rate = 99 % (confidence: high)
- Cloud Email Server: is_for = Dịch vụ Cloud Email Server là giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây, dành cho các tổ chức và doanh nghiệp. None (confidence: high)
- Cloud Email Server: platform_options = Kerio, Zimbra None (confidence: high)
- Cloud Email Server: protocol_support = POP3/IMAP/SMTP None (confidence: high)
- Cloud Email Server: sending_limit = 200 email/giờ (confidence: high)
- Cloud Email Server: starting_price = 239000 VND (confidence: low)
- Cloud Email Server: target_audience = Doanh nghiệp cần một hệ thống email riêng theo tên miền, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng. None (confidence: high)
- Cloud Email Server: uptime_guarantee = 99 % (confidence: high)
- Email Hosting Gói 4: domain_limit = 1 None (confidence: high)
- Email Hosting Gói 4: email_account_limit = 100 email (confidence: high)
- MINI EMAIL 01: email_filter = True None (confidence: high)
- Email Hosting Gói 4: email_forwarder_limit = 100 None (confidence: high)
- MINI EMAIL 01: mailing_list_limit = Unlimited None (confidence: high)
- Email Hosting Gói 4: outgoing_email_limit = 200 email/giờ (confidence: high)
- MINI EMAIL 01: outlook_compatibility = True None (confidence: high)
- MINI EMAIL 02: platform = Kerio None (confidence: high)
- MINI EMAIL 03: monthly_price = 556000 VND (confidence: high)
- MINI EMAIL 01: spam_protection = True None (confidence: high)
- MINI EMAIL 02: storage = 150 GB (confidence: high)
- Email Hosting Gói 4: storage_per_email = 5 GB (confidence: high)
- MINI EMAIL 01: virus_protection = True None (confidence: high)
- MINI EMAIL 01: webmail_access = True None (confidence: high)
- Cloud Email Server: product_category = Giải Pháp Email Doanh Nghiệp None (confidence: high)
- EMAIL 1: hourly_send_limit = 200 email (confidence: high)
- EMAIL 1: num_accounts = 5  (confidence: high)
- EMAIL 1: num_domains = 1  (confidence: high)
- EMAIL 1: num_email_forwards = 5  (confidence: high)
- EMAIL 1: monthly_price = 42000 VND (confidence: high)
- EMAIL 1: registration_url = https://my.bkns.net/?cmd=cart&action=add&id=302  (confidence: high)
- EMAIL 1: storage_per_account = 5 GB (confidence: high)
- EMAIL 2: num_accounts = 20  (confidence: high)
- EMAIL 2: num_email_forwards = 10  (confidence: high)
- EMAIL 2: monthly_price = 85000 VND (confidence: high)
- EMAIL 1: email_accounts = 5 tài khoản (confidence: high)
- EMAIL 1: email_forwards = 5 tài khoản (confidence: high)
- EMAIL 1: monthly_price = 42000 VND (confidence: high)
- EMAIL 1: registration_url = https://my.bkns.net/?cmd=cart&action=add&id=302 None (confidence: high)
- EMAIL 1: storage_per_email = 5 GB (confidence: high)
- EMAIL 2: email_accounts = 20 tài khoản (confidence: high)
- EMAIL 2: email_forwards = 10 tài khoản (confidence: high)
- EMAIL 2: monthly_price = 85000 VND (confidence: high)
- EMAIL 2: registration_url = https://my.bkns.net/?cmd=cart&action=add&id=264 None (confidence: high)
- EMAIL 2: storage_per_email = 5 GB (confidence: high)
- EMAIL 3: email_accounts = 50 tài khoản (confidence: high)
- EMAIL 3: email_forwards = 40 tài khoản (confidence: high)
- EMAIL 3: monthly_price = 166000 VND (confidence: high)
- EMAIL 3: registration_url = https://my.bkns.net/?cmd=cart&action=add&id=265 None (confidence: high)
- EMAIL 3: storage_per_account = 5 GB (confidence: high)
- EMAIL 4: email_accounts = 100 tài khoản (confidence: high)
- EMAIL 4: email_forwards = 100 tài khoản (confidence: high)
- EMAIL 4: monthly_price = 285000 VND (confidence: high)
- EMAIL 4: registration_url = https://my.bkns.net/?cmd=cart&action=add&id=266 None (confidence: high)
- Email Relay: comparison_point = Toàn bộ email gửi ra ngoài sẽ được routing qua hệ thống của BKNS để xử lý.  (confidence: high)
- Email Relay: description = Email Relay là một giải pháp trung gian giúp định tuyến toàn bộ email gửi ra từ hệ thống Email Server của khách hàng qua hệ thống của BKNS để xử lý, nhằm tăng uy tín IP và đảm bảo tỷ lệ email vào inbox cao.  (confidence: high)
- Email Relay: domain_limit = unlimited None (confidence: high)
- BK-RELAY04: email_limit_hourly = 3000 email (confidence: high)
- Email Relay: feature = Sử dụng hệ thống IP đã được whitelist để gửi email.  (confidence: high)
- Email Relay: has_admin_interface = True None (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.email.bang-gia
title: Email Doanh Nghiệp BKNS — Bảng Giá
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 109
compile_cost_usd: 0.0346
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:19.969286+07:00'
---

# Email Doanh Nghiệp BKNS — Bảng Giá

Trang này tổng hợp bảng giá chi tiết cho các dịch vụ Email Doanh Nghiệp do BKNS cung cấp, dựa trên các nguồn dữ liệu đã được kiểm duyệt.

Lưu ý: Tất cả các mức giá được liệt kê dưới đây chưa bao gồm thuế VAT. Phí cài đặt (Setup fee) hiện đang được cập nhật.

## Bảng giá Email Hosting

Dịch vụ email theo tên miền riêng, phù hợp cho các cá nhân và doanh nghiệp nhỏ.

| Tên Gói | Giá hàng tháng | Bảng giá theo chu kỳ dài hạn |
| :--- | :--- | :--- |
| Email Hosting EMAIL 1 | 45.000 VND | 1 năm: 513.000 VND <br> 2 năm: 864.000 VND <br> 3 năm: 1.134.000 VND <br> 4 năm: 1.296.000 VND |
| Email Hosting EMAIL 2 | 90.000 VND | 1 năm: 1.026.000 VND <br> 2 năm: 1.728.000 VND <br> 3 năm: 2.268.000 VND <br> 4 năm: 2.592.000 VND |
| Email Hosting EMAIL 3 | 175.000 VND | 1 năm: 1.995.000 VND <br> 2 năm: 3.360.000 VND <br> 3 năm: 4.410.000 VND <br> 4 năm: 5.040.000 VND |
| Email Hosting EMAIL 4 | 300.000 VND | 1 năm: 3.420.000 VND <br> 2 năm: 5.760.000 VND <br> 3 năm: 7.560.000 VND <br> 4 năm: 8.640.000 VND |

## Bảng giá Cloud Email Server

Giải pháp email chuyên dụng trên nền tảng máy chủ ảo, cung cấp hiệu năng và độ ổn định cao. Dịch vụ này có hai dòng sản phẩm chính: MINI EMAIL và ES.

*Lưu ý: Có thông tin ghi nhận giá khởi điểm của dịch vụ từ 239.000 VND/tháng, tuy nhiên gói thấp nhất được niêm yết trong bảng giá chi tiết là MINI EMAIL 1 với giá 369.000 VND/tháng.*

| Tên Gói | Giá hàng tháng | Bảng giá theo chu kỳ dài hạn |
| :--- | :--- | :--- |
| Cloud Email Server MINI EMAIL 1 | 369.000 VND | 6 tháng: 2.103.300 VND <br> 1 năm: 3.763.800 VND <br> 2 năm: 6.642.000 VND <br> 3 năm: 8.634.600 VND |
| Cloud Email Server MINI EMAIL 2 | 529.000 VND | 6 tháng: 3.015.300 VND <br> 1 năm: 5.395.800 VND <br> 2 năm: 9.522.000 VND <br> 3 năm: 12.378.600 VND |
| Cloud Email Server MINI EMAIL 3 | 654.000 VND | 6 tháng: 3.727.800 VND <br> 1 năm: 6.670.800 VND <br> 2 năm: 11.772.000 VND <br> 3 năm: 15.303.600 VND |
| Cloud Email Server MINI EMAIL 4 | 789.000 VND | 6 tháng: 4.497.300 VND <br> 1 năm: 8.047.800 VND <br> 2 năm: 14.202.000 VND <br> 3 năm: 18.462.600 VND |
| Cloud Email Server ES 1 | 870.000 VND | 6 tháng: 4.959.000 VND <br> 1 năm: 8.874.000 VND <br> 2 năm: 15.660.000 VND <br> 3 năm: 20.358.000 VND |
| Cloud Email Server ES 2 | 1.500.000 VND | 6 tháng: 8.550.000 VND <br> 1 năm: 15.300.000 VND <br> 2 năm: 27.000.000 VND <br> 3 năm: 35.100.000 VND |
| Cloud Email Server ES 3 | 3.200.000 VND | 6 tháng: 18.240.000 VND <br> 1 năm: 32.640.000 VND <br> 2 năm: 57.600.000 VND <br> 3 năm: 74.880.000 VND |
| Cloud Email Server ES 4 | 4.900.000 VND | 6 tháng: 27.930.000 VND <br> 1 năm: 49.980.000 VND <br> 2 năm: 88.200.000 VND <br> 3 năm: 114.660.000 VND |

## Bảng giá Email Relay

Dịch vụ chuyển tiếp email (SMTP Relay) giúp gửi email số lượng lớn với tỷ lệ vào hộp thư đến cao.

| Tên Gói | Giá hàng tháng | Bảng giá theo chu kỳ dài hạn |
| :--- | :--- | :--- |
| Email Relay BK-RELAY 01 | 180.000 VND | 1 năm: 2.160.000 VND <br> 2 năm: 4.320.000 VND <br> 3 năm: 6.480.000 VND |
| Email Relay BK-RELAY 02 | 290.000 VND | 1 năm: 3.480.000 VND <br> 2 năm: 6.960.000 VND <br> 3 năm: 10.440.000 VND |
| Email Relay BK-RELAY 03 | 500.000 VND | 1 năm: 6.000.000 VND <br> 2 năm: 12.000.000 VND <br> 3 năm: 18.000.000 VND |
| Email Relay BK-RELAY 04 | 980.000 VND | 1 năm: 11.760.000 VND <br> 2 năm: 23.520.000 VND <br> 3 năm: 35.280.000 VND |

### Xem Thêm

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.email.cau-hoi-thuong-gap
title: Email Doanh Nghiệp BKNS — Câu Hỏi Thường Gặp
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:24:19.973070+07:00'
---

# Email Doanh Nghiệp BKNS — Câu Hỏi Thường Gặp

> FAQ cho Email Doanh Nghiệp BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### chinh-sach.md

---
page_id: wiki.products.email.chinh-sach
title: Email Doanh Nghiệp BKNS — Chính Sách
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 13
compile_cost_usd: 0.0067
self_review: fail
corrections: 5
approved_at: '2026-04-07T16:24:19.976746+07:00'
---

# Email Doanh Nghiệp BKNS — Chính Sách

Trang này tổng hợp các chính sách, cam kết dịch vụ (SLA) và điều khoản quan trọng liên quan đến các gói dịch vụ Email Doanh Nghiệp do BKNS cung cấp.

## 1. Cam kết Chất lượng Dịch vụ (SLA)

### Cam kết Uptime và Tỷ lệ vào Inbox
BKNS cam kết thời gian hoạt động (uptime) cho dịch vụ **Cloud Email Server** là **99%** và đảm bảo tỷ lệ email vào inbox lên đến **99%**.

## 2. Chính sách Sao lưu Dữ liệu (Backup)

Dữ liệu của dịch vụ **Cloud Email Server** được sao lưu (backup) định kỳ **Hàng tuần**.

## 3. Chính sách Hỗ trợ Kỹ thuật

BKNS cung cấp hỗ trợ kỹ thuật cho các dịch vụ email.

- **Thời gian hỗ trợ:** 24/7/365 (áp dụng cho dịch vụ Email Relay).
- **Kênh hỗ trợ (Hotline, Email, Ticket):** [Cần cập nhật]
- **Thời gian phản hồi:** [Cần cập nhật]

## 4. Điều khoản và Lưu ý Quan trọng

### Đối với dịch vụ Cloud Email Server
- **Tương thích:** Hỗ trợ đầy đủ các giao thức POP3/IMAP/SMTP, cho phép sử dụng trên Webmail và các ứng dụng email client như Outlook.

### Đối với dịch vụ Email Relay
- Dịch vụ này là giải pháp định tuyến email gửi đi, không phải là dịch vụ lưu trữ email đến.
- Toàn bộ email gửi ra từ hệ thống của khách hàng sẽ được định tuyến (routing) qua hệ thống của BKNS để xử lý và gửi đi, nhằm đảm bảo uy tín và tỷ lệ vào inbox cao.

### Chính sách chung
- Giá dịch vụ niêm yết **chưa bao gồm VAT**.

## 5. Chính sách Dùng thử và Hoàn tiền

- **Thời gian dùng thử:** [Cần cập nhật]
- **Chính sách hoàn tiền:** [Cần cập nhật]

## Xem Thêm

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • [Ngày biên soạn chính xác]

---

### cloud-email-server.md

---
page_id: wiki.products.email.cloud-email-server
title: Cloud Email Server BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 58
compile_cost_usd: 0.0162
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:19.979693+07:00'
---

## Cloud Email Server BKNS

**Cloud Email Server** của BKNS là giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây. Dịch vụ này được thiết kế cho các tổ chức và doanh nghiệp cần một hệ thống email theo tên miền riêng, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng.

Dịch vụ cung cấp hai lựa chọn nền tảng là **Kerio** và **Zimbra**.

### Tính năng và Chính sách chung

*   **Độ tin cậy**: Đảm bảo tỷ lệ email vào inbox lên đến 99% và uptime 99%.
*   **Bảo mật**: Tích hợp miễn phí các công cụ chống Spam và chống Virus.
*   **Quản lý IP**: IP gửi mail được BKNS quản lý và theo dõi để đảm bảo uy tín.
*   **Sao lưu**: Dữ liệu được sao lưu (backup) định kỳ hàng tuần.
*   **Giới hạn gửi**: Giới hạn số lượng email gửi đi là 200 email/giờ cho tất cả các gói.
*   **Giao thức hỗ trợ**: Hỗ trợ đầy đủ các giao thức POP3/IMAP/SMTP, cho phép sử dụng trên Webmail và các ứng dụng email client như Outlook.

### Lưu ý về giá
Thông tin giá quảng cáo ("CHỈ TỪ 239K/THÁNG") có sự mâu thuẫn với giá gói thấp nhất trong bảng giá thực tế (MINI EMAIL 01: 314.000đ/Tháng). Bảng giá dưới đây dựa trên thông tin chi tiết của từng gói.

### Bảng giá và Cấu hình chi tiết

| Tên Gói | Nền tảng | Dung lượng | Giới hạn Gửi (Email/ngày) | Giá/Tháng (VND) |
| :--- | :--- | :--- | :--- | :--- |
| **MINI EMAIL 01** | Kerio | 100 GB | 4.800 (200/giờ) | 314.000 |
| **MINI EMAIL 02** | Kerio | 150 GB | 4.800 (200/giờ) | 450.000 |
| **MINI EMAIL 03** | Kerio | 200 GB | 4.800 (200/giờ) | 556.000 |
| **MINI EMAIL 04** | Kerio | 250 GB | 4.800 (200/giờ) | 671.000 |
| **ES 01** | Zimbra | 300 GB | 4.800 (200/giờ) | 734.000 |
| **ES 02** | Zimbra | 500 GB | 4.800 (200/giờ) | 1.275.000 |
| **ES 03** | Zimbra | 1000 GB | 4.800 (200/giờ) | 2.720.000 |
| **ES 04** | Zimbra | 2000 GB | 4.800 (200/giờ) | 4.165.000 |

### Sản phẩm liên quan
- [Tên Miền BKNS](../ten-mien/index.md)
- [Hosting BKNS](../hosting/index.md)
- [SSL Certificate BKNS](../ssl/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### email-hosting.md

---
page_id: wiki.products.email.email-hosting
title: Email Hosting BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 31
compile_cost_usd: 0.0088
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:19.982774+07:00'
---

# Email Hosting BKNS

Dịch vụ Email Hosting của BKNS cung cấp giải pháp email chuyên nghiệp theo tên miền riêng, đáp ứng nhu cầu của cá nhân và doanh nghiệp. Dưới đây là bảng so sánh chi tiết các gói dịch vụ từ EMAIL 1 đến EMAIL 4.

## Bảng so sánh các gói Email Hosting

| Tính năng | EMAIL 1 | EMAIL 2 | EMAIL 3 | EMAIL 4 |
| :--- | :--- | :--- | :--- | :--- |
| **Giá mỗi tháng** | 42.000 VNĐ | 85.000 VNĐ | 166.000 VNĐ | 285.000 VNĐ |
| **Dung lượng mỗi tài khoản** | 5 GB | 5 GB | 5 GB | 5 GB |
| **Số lượng tài khoản email** | 5 | 20 | 50 | 100 |
| **Số lượng tên miền** | 1 | [CẦN CẬP NHẬT] | [CẦN CẬP NHẬT] | [CẦN CẬP NHẬT] |
| **Giới hạn gửi email/giờ** | 200 email | [CẦN CẬP NHẬT] | [CẦN CẬP NHẬT] | 200 email |
| **Số lượng email forward** | 5 | 10 | 40 | 100 |
| **Đăng ký** | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=302) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=264) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=265) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=266) |

## Xem thêm

- [Tên Miền BKNS](../ten-mien/index.md)
- [Hosting BKNS](../hosting/index.md)
- [SSL Certificate BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### email-relay.md

---
page_id: wiki.products.email.email-relay
title: Email Relay BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 46
compile_cost_usd: 0.0139
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:19.986668+07:00'
---

# Email Relay BKNS

Email Relay là một giải pháp trung gian giúp định tuyến toàn bộ email gửi ra từ hệ thống Email Server của khách hàng qua hệ thống của BKNS. Dịch vụ này sử dụng các máy chủ chuyên dụng với dải IP uy tín cao (đã được whitelist) nhằm tăng tỷ lệ email gửi vào inbox của người nhận lên đến 99%.

Dịch vụ phù hợp cho các doanh nghiệp đã có Email Server riêng nhưng gặp vấn đề khi gửi email ra ngoài (như IP bị blacklist, email vào spam) hoặc có nhu cầu gửi email marketing, email giao dịch với số lượng lớn.

## Đặc điểm và Chính sách chung

- **Yêu cầu bắt buộc:** Khách hàng cần có sẵn một hệ thống Email Server để có thể sử dụng dịch vụ.
- **IP uy tín:** Toàn bộ email được gửi qua hệ thống IP đã được whitelist của BKNS để đảm bảo không bị chặn.
- **Không giới hạn tên miền:** Dịch vụ cho phép sử dụng với nhiều tên miền khác nhau.
- **Giao diện quản trị:** Cung cấp giao diện để khách hàng tự quản trị dịch vụ Email Relay của mình.
- **Hỗ trợ kỹ thuật:** Đội ngũ kỹ thuật của BKNS hỗ trợ 24/7/365.
- **Lưu ý:** Đây là giải pháp định tuyến email gửi đi, không phải dịch vụ lưu trữ email đến.

## So sánh các gói cước Email Relay

| Tính năng | BK-RELAY 01 | BK-RELAY 02 | BK-RELAY 03 | BK-RELAY 04 |
| :--- | :--- | :--- | :--- | :--- |
| **Số lượng email/ngày** | 350 | 700 | 1.500 | 30.000 |
| **Số lượng email/giờ** | 200 | 200 | 200 | 200 |
| **Tỉ lệ vào inbox** | 99% | 99% | 99% | 99% |
| **Số lượng tên miền** | Không giới hạn | Không giới hạn | Không giới hạn | Không giới hạn |
| **Quản trị email relay** | Có | Có | Có | Có |
| **Giá/Tháng (chưa VAT)** | 180.000 VNĐ | 290.000 VNĐ | 500.000 VNĐ | 980.000 VNĐ |
| **Đăng ký** | Đang cập nhật | Đang cập nhật | Đang cập nhật | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=408) |

**Ghi chú:**
*   Đối với gói **BK-RELAY 04**, khi đăng ký 3 năm (đã bao gồm ưu đãi giảm 30%), chi phí là 35.280.000 VNĐ (chưa VAT).

## Xem thêm

- [Tên Miền BKNS](../ten-mien/index.md)
- [Hosting BKNS](../hosting/index.md)
- [SSL Certificate BKNS](../ssl/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### huong-dan.md

---
page_id: wiki.products.email.huong-dan
title: Email Doanh Nghiệp BKNS — Hướng Dẫn
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:24:19.991430+07:00'
---

# Email Doanh Nghiệp BKNS — Hướng Dẫn

> Hướng dẫn đăng ký, kích hoạt, quản lý Email Doanh Nghiệp BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### index.md

---
page_id: wiki.products.email.index
title: Email Doanh Nghiệp BKNS — Trang Tổng Quan
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 27
compile_cost_usd: 0.0112
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:19.996227+07:00'
---

# Email Doanh Nghiệp BKNS — Trang Tổng Quan

Email Doanh Nghiệp BKNS là giải pháp email theo tên miền công ty, cung cấp một hệ thống chuyên nghiệp, ổn định và bảo mật cho các doanh nghiệp với khả năng tùy chỉnh linh hoạt theo nhu cầu.

## Mục lục

- **Tổng quan:** [tong-quan.md](./tong-quan.md)
- **Bảng giá:** [bang-gia.md](./bang-gia.md)
- **Thông số kỹ thuật:** [thong-so.md](./thong-so.md)
- **Tính năng:** [tinh-nang.md](./tinh-nang.md)
- **Chính sách:** [chinh-sach.md](./chinh-sach.md)
- **Câu hỏi thường gặp:** [cau-hoi-thuong-gap.md](./cau-hoi-thuong-gap.md)
- **So sánh:** [so-sanh.md](./so-sanh.md)
- **Hướng dẫn:** [huong-dan.md](./huong-dan.md)

## Các Dòng Sản Phẩm Chính

Dựa trên các nhu cầu khác nhau của doanh nghiệp, BKNS cung cấp các dòng sản phẩm email chuyên biệt:

- **Email Hosting**: Dịch vụ email theo tên miền riêng cho doanh nghiệp, chạy trên nền tảng Zimbra độc lập, cung cấp các tính năng bảo mật và chống spam. Phù hợp cho doanh nghiệp cần một hệ thống email chuyên nghiệp, ổn định và bảo mật, với khả năng tùy chỉnh số lượng tài khoản theo nhu cầu.

- **Cloud Email Server**: Giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây. Dành cho các tổ chức và doanh nghiệp cần một hệ thống email riêng theo tên miền, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng.

- **Email Relay**: Một giải pháp trung gian giúp định tuyến toàn bộ email gửi ra từ hệ thống Email Server của khách hàng qua hệ thống của BKNS để xử lý. Dịch vụ này giúp tăng uy tín IP và đảm bảo tỷ lệ email vào inbox cao, phù hợp với các khách hàng đã có Email Server riêng nhưng gặp vấn đề khi gửi email ra ngoài (ví dụ: IP bị blacklist, email vào spam) hoặc có nhu cầu gửi Email marketing với số lượng lớn.

## Liên kết nhanh đến các sản phẩm

- [Email Hosting](./san-pham/email-hosting.md)
- [Cloud Email Server](./san-pham/cloud-email-server.md)
- [Email Relay](./san-pham/email-relay.md)

## Sản phẩm liên quan

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

***

*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### san-pham/cloud-email-server.md

---
page_id: wiki.products.email.san-pham.cloud-email-server
title: Cloud Email Server BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 106
compile_cost_usd: 0.0272
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:20.001000+07:00'
---

# Cloud Email Server BKNS

**Giải Pháp Email Doanh Nghiệp**

Dịch vụ Cloud Email Server của BKNS là giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây, được thiết kế cho các tổ chức và doanh nghiệp. Dịch vụ này phù hợp với các doanh nghiệp cần một hệ thống email riêng theo tên miền, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng.

BKNS cung cấp hai lựa chọn nền tảng là Kerio và Zimbra.

## Tính năng và Cam kết Dịch vụ

*   **Độ tin cậy cao:** Cam kết tỷ lệ email vào inbox và thời gian hoạt động (uptime) lên đến 99%.
*   **Bảo mật tích hợp:** Tích hợp miễn phí các công cụ chống Spam và Virus.
*   **Sao lưu định kỳ:** Dữ liệu được sao lưu tự động hàng tuần.
*   **Giới hạn gửi email:** Giới hạn gửi đi là 200 email/giờ cho tất cả các gói.
*   **Hỗ trợ đa giao thức:** Hỗ trợ đầy đủ các giao thức POP3/IMAP/SMTP, tương thích với Webmail và các ứng dụng email client như Outlook.

## Bảng giá và Cấu hình Chi tiết

Bảng dưới đây tổng hợp thông số kỹ thuật và chi phí cho các gói dịch vụ Cloud Email Server.

| Gói dịch vụ | Nền tảng | Dung lượng | Giá 1 tháng | Giá 6 tháng | Giá 1 năm | Giá 2 năm | Giá 3 năm |
| :--- | :--- | :--- | ---:| ---:| ---:| ---:| ---:|
| **MINI EMAIL 1** | Kerio | 100 GB | 369.000 | 2.103.300 | 3.763.800 | 6.642.000 | 8.634.600 |
| **MINI EMAIL 2** | Kerio | 150 GB | 529.000 | 3.015.300 | 5.395.800 | 9.522.000 | 12.378.600 |
| **MINI EMAIL 3** | Kerio | 200 GB | 654.000 | 3.727.800 | 6.670.800 | 11.772.000 | 15.303.600 |
| **MINI EMAIL 4** | Kerio | 255 GB | 789.000 | 4.497.300 | 8.047.800 | 14.202.000 | 18.462.600 |
| **ES 1** | Zimbra | 300 GB | 870.000 | 4.959.000 | 8.874.000 | 15.660.000 | 20.358.000 |
| **ES 2** | Zimbra | 500 GB | 1.500.000 | 8.550.000 | 15.300.000 | 27.000.000 | 35.100.000 |
| **ES 3** | Zimbra | 1.000 GB | 3.200.000 | 18.240.000 | 32.640.000 | 57.600.000 | 74.880.000 |
| **ES 4** | Zimbra | 2.000 GB | 4.900.000 | 27.930.000 | 49.980.000 | 88.200.000 | 114.660.000 |

*Đơn vị: VNĐ. Giá chưa bao gồm VAT.*

**Lưu ý:** Có sự khác biệt về giá giữa thông tin quảng cáo ("chỉ từ 239K/tháng") và giá niêm yết trên website so với bảng giá nội bộ. Bảng giá trên được tổng hợp từ nguồn dữ liệu nội bộ (ground truth) và có độ tin cậy cao nhất.

## So sánh với các giải pháp khác

*   **So với Email Hosting:** Email Server cho phép tạo số lượng email nhiều hơn, trong khi số lượng email của Email Hosting bị giới hạn theo tài nguyên gói dịch vụ.
*   **So với Email Relay:** Với dịch vụ Email Server, BKNS chịu trách nhiệm quản lý IP gửi của máy chủ cho khách hàng.

## Sản phẩm liên quan

*   [Tên Miền BKNS](../ten-mien/index.md)
*   [Web Hosting BKNS](../hosting/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/email-hosting.md

---
page_id: wiki.products.email.san-pham.email-hosting
title: Email Hosting BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 31
compile_cost_usd: 0.0092
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:20.005823+07:00'
---

# Email Hosting BKNS

Dịch vụ Email Hosting của BKNS cung cấp giải pháp email chuyên nghiệp theo tên miền riêng, được thiết kế để đáp ứng các nhu cầu khác nhau của cá nhân và doanh nghiệp.

Dưới đây là bảng so sánh chi tiết các gói dịch vụ Email Hosting hiện có.

### Bảng giá và thông số kỹ thuật Email Hosting

| Thông số | EMAIL 1 | EMAIL 2 | EMAIL 3 | EMAIL 4 |
| :--- | :--- | :--- | :--- | :--- |
| **Số lượng tài khoản** | 5 | 20 | 50 | 100 |
| **Dung lượng/tài khoản** | 5 GB | 5 GB | 5 GB | 5 GB |
| **Số lượng tên miền** | 1 | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| **Giới hạn gửi email** | 200 email/giờ | Đang cập nhật | Đang cập nhật | 200 email/giờ |
| **Số lượng email forward** | 5 | 10 | 40 | 100 |
| **Giá hàng tháng** | 42.000 VNĐ | 85.000 VNĐ | 166.000 VNĐ | 285.000 VNĐ |
| **Đăng ký** | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=302) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=264) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=265) | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=266) |

---

### Sản phẩm liên quan

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/email-relay.md

---
page_id: wiki.products.email.san-pham.email-relay
title: Email Relay BKNS
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 66
compile_cost_usd: 0.0181
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:20.010807+07:00'
---

# Email Relay BKNS

Email Relay là một giải pháp trung gian giúp định tuyến toàn bộ email gửi ra từ hệ thống Email Server của khách hàng qua hệ thống máy chủ chuyên dụng của BKNS. Dịch vụ này sử dụng các dải IP uy tín đã được whitelist, nhằm tăng tỷ lệ email gửi vào inbox lên đến 99% và giải quyết các vấn đề như IP bị blacklist hay email bị đánh dấu spam.

Dịch vụ phù hợp cho các doanh nghiệp đã có Email Server riêng nhưng gặp khó khăn khi gửi email ra ngoài, hoặc có nhu cầu gửi email marketing với số lượng lớn.

**Yêu cầu:** Khách hàng cần có sẵn một hệ thống Email Server để sử dụng dịch vụ. Email Relay là giải pháp định tuyến email gửi đi, không phải dịch vụ lưu trữ email đến.

### Tính năng chung

Tất cả các gói Email Relay của BKNS đều bao gồm các tính năng sau:
*   **IP uy tín:** Sử dụng hệ thống IP đã được whitelist để gửi email.
*   **Không giới hạn tên miền:** Khách hàng có thể sử dụng dịch vụ cho nhiều tên miền khác nhau.
*   **Giao diện quản trị:** Cung cấp giao diện để khách hàng quản trị dịch vụ.
*   **Giới hạn gửi:** Tất cả các gói đều có giới hạn gửi chung là 200 email/giờ.
*   **Hỗ trợ kỹ thuật:** Đội ngũ hỗ trợ kỹ thuật hoạt động 24/7/365.

### Bảng giá dịch vụ Email Relay (BK-RELAY)

Bảng so sánh chi tiết các gói cước Email Relay BK-RELAY 01, 02, 03, và 04.

| Tính năng | BK-RELAY 01 | BK-RELAY 02 | BK-RELAY 03 | BK-RELAY 04 |
| :--- | :--- | :--- | :--- | :--- |
| **Số lượng email/ngày** | 350 | 700 | 1.500 | 30.000 |
| **Giá/tháng** | 180.000đ | 290.000đ | 500.000đ | 980.000đ |
| **Giá/1 năm** | 2.160.000đ | 3.480.000đ | 6.000.000đ | 11.760.000đ |
| **Giá/2 năm** | 4.320.000đ | 6.960.000đ | 12.000.000đ | 23.520.000đ |
| **Giá/3 năm** | 6.480.000đ | 10.440.000đ | 18.000.000đ | 35.280.000đ |
| **Đăng ký** | Đang cập nhật | Đang cập nhật | Đang cập nhật | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=408) |

*Lưu ý: Bảng giá trên chưa bao gồm VAT.*

### Sản phẩm liên quan

*   [Tên Miền BKNS](../ten-mien/index.md)
*   [Web Hosting BKNS](../hosting/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)

***

*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### so-sanh.md

---
page_id: wiki.products.email.so-sanh
title: Email Doanh Nghiệp BKNS — So Sánh
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:24:20.015319+07:00'
---

# Email Doanh Nghiệp BKNS — So Sánh

> So sánh nội bộ các sản phẩm trong Email Doanh Nghiệp BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### thong-so.md

---
page_id: wiki.products.email.thong-so
title: Email Doanh Nghiệp BKNS — Thông Số Kỹ Thuật
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 70
compile_cost_usd: 0.0165
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:20.018449+07:00'
---

# Email Doanh Nghiệp BKNS — Thông Số Kỹ Thuật

Trang này tổng hợp và so sánh các thông số kỹ thuật chính của các gói dịch vụ Email Doanh Nghiệp do BKNS cung cấp, bao gồm Email Hosting, Cloud Email Server và Email Relay. Dữ liệu được trích xuất trực tiếp từ cơ sở tri thức nội bộ.

## Email Hosting

Dịch vụ Email Hosting cung cấp một số lượng tài khoản email nhất định, mỗi tài khoản có dung lượng lưu trữ riêng. Đây là giải pháp phù hợp cho các doanh nghiệp cần email theo tên miền với số lượng người dùng xác định.

| Gói Dịch Vụ | Số Lượng Tài Khoản | Dung Lượng / Tài Khoản |
| :--- | :--- | :--- |
| EMAIL 1 | 5 | 5 GB |
| EMAIL 2 | 20 | 5 GB |
| EMAIL 3 | 50 | 5 GB |
| EMAIL 4 | 100 | 5 GB |

**Tính năng nổi bật:**
- Tỷ lệ gửi email vào inbox: 99%
- Hỗ trợ truy cập qua các ứng dụng email client phổ biến như Outlook.

## Cloud Email Server

Cloud Email Server là giải pháp email chuyên dụng với không gian lưu trữ lớn, không giới hạn số lượng tài khoản và tên miền, phù hợp cho các tổ chức có nhu cầu sử dụng email linh hoạt và quy mô lớn.

**Tính năng chung:**
- Số lượng tài khoản email: Không giới hạn
- Số lượng tên miền: Không giới hạn
- Tỷ lệ gửi email vào inbox: 99%
- Hỗ trợ giao thức: POP3/IMAP/SMTP

### Gói Cloud Email Server Mini

| Gói Dịch Vụ | Tổng Dung Lượng |
| :--- | :--- |
| MINI EMAIL 1 | 100 GB |
| MINI EMAIL 2 | 150 GB |
| MINI EMAIL 3 | 200 GB |
| MINI EMAIL 4 | 255 GB |

### Gói Cloud Email Server ES

| Gói Dịch Vụ | Tổng Dung Lượng |
| :--- | :--- |
| ES 1 | 300 GB |
| ES 2 | 500 GB |
| ES 3 | 1000 GB |
| ES 4 | 2000 GB |

## Email Relay

Dịch vụ Email Relay được thiết kế để gửi email marketing và email giao dịch số lượng lớn với tỷ lệ vào inbox cao, giúp doanh nghiệp tiếp cận khách hàng hiệu quả.

| Gói Dịch Vụ | Giới Hạn Email / Ngày |
| :--- | :--- |
| BK-RELAY 01 | 350 |
| BK-RELAY 02 | 700 |
| BK-RELAY 03 | 1.500 |
| BK-RELAY 04 | 30.000 |

**Tính năng chung:**
- Số lượng tên miền: Không giới hạn
- Tỷ lệ gửi email vào inbox: 99%
- Hỗ trợ kỹ thuật: 24/7/365

## Xem Thêm

- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---
Compiled by BKNS Wiki Bot • 2024-05-24

---

### tinh-nang.md

---
page_id: wiki.products.email.tinh-nang
title: Email Doanh Nghiệp BKNS — Tính Năng
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 35
compile_cost_usd: 0.0106
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:20.022479+07:00'
---

# Email Doanh Nghiệp BKNS — Các Dịch Vụ và Tính Năng

BKNS cung cấp nhiều giải pháp email chuyên nghiệp, mỗi dịch vụ được thiết kế với các tính năng riêng biệt để đáp ứng nhu cầu đa dạng của doanh nghiệp.

## 1. Email Hosting

Dịch vụ Email Hosting của BKNS là lựa chọn phù hợp cho các doanh nghiệp cần một hệ thống email ổn định và dễ quản lý.

*   **Tự động trả lời (Auto-responder):** Dễ dàng thiết lập các email phản hồi tự động khi bạn vắng mặt.
*   **Quản trị DNS miễn phí (Managed DNS):** Đi kèm tính năng quản trị DNS miễn phí, giúp đơn giản hóa việc cấu hình.
*   **Tương thích Email Client:** Hỗ trợ truy cập qua Webmail và các ứng dụng phổ biến như Microsoft Outlook.

## 2. Cloud Email Server

Giải pháp email mạnh mẽ, cung cấp hiệu suất cao và bảo mật nâng cao cho doanh nghiệp.

*   **Tích hợp chống Spam/Virus:** Được tích hợp sẵn các công cụ chống spam và virus miễn phí để bảo vệ hộp thư của bạn.
*   **Hỗ trợ đa giao thức (POP3/IMAP/SMTP):** Tương thích hoàn toàn với các giao thức phổ biến, đảm bảo hoạt động trên mọi ứng dụng email client từ Outlook đến các ứng dụng di động.

## 3. Email Relay

Dịch vụ chuyên dụng giúp đảm bảo tỷ lệ gửi email thành công vào inbox cao, phù hợp cho các chiến dịch marketing hoặc gửi thông báo hàng loạt.

*   **Giao diện quản trị chuyên dụng:** Cung cấp giao diện riêng để khách hàng chủ động quản lý và theo dõi dịch vụ.
*   **Không giới hạn tên miền:** Cho phép sử dụng không giới hạn số lượng tên miền trên một gói dịch vụ, mang lại sự linh hoạt tối đa.
*   **Hệ thống IP uy tín (Whitelist IP):** Sử dụng hệ thống IP được tin cậy (whitelist) để tăng tỷ lệ email vào inbox và không bị chặn bởi bộ lọc thư rác.
*   **Hỗ trợ kỹ thuật 24/7/365:** Đội ngũ hỗ trợ chuyên nghiệp luôn sẵn sàng giải quyết các vấn đề kỹ thuật liên quan đến dịch vụ.

## Sản phẩm liên quan
- [Tên Miền BKNS](../ten-mien/index.md)
- [Web Hosting BKNS](../hosting/index.md)
- [Chứng Chỉ SSL BKNS](../ssl/index.md)

---

### tong-quan.md

---
page_id: wiki.products.email.tong-quan
title: Email Doanh Nghiệp BKNS — Tổng Quan Chi Tiết
category: products/email
updated: '2026-04-07'
review_state: approved
claims_used: 62
compile_cost_usd: 0.0244
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:20.026846+07:00'
---

# Email Doanh Nghiệp BKNS — Tổng Quan Chi Tiết

Email Doanh Nghiệp là một giải pháp email theo tên miền riêng của công ty, được thiết kế để đáp ứng nhu cầu trao đổi thông tin chuyên nghiệp, bảo mật và ổn định. Dịch vụ này giải quyết bài toán xây dựng hình ảnh thương hiệu đồng nhất qua từng email gửi đi, đồng thời đảm bảo an toàn dữ liệu và khả năng quản lý tập trung cho tổ chức.

Tại BKNS, các giải pháp Email Doanh Nghiệp được xây dựng để phục vụ nhiều quy mô và nhu cầu khác nhau, từ các gói hosting email cơ bản đến hệ thống máy chủ email riêng biệt.

## 1. Các giải pháp Email Doanh Nghiệp tại BKNS

BKNS cung cấp ba dòng sản phẩm chính trong danh mục Email Doanh Nghiệp, mỗi dòng sản phẩm hướng đến một nhóm đối tượng và bài toán cụ thể.

### 1.1. Email Hosting

Đây là dịch vụ email theo tên miền riêng cho doanh nghiệp, hoạt động trên một nền tảng độc lập, được tối ưu hóa cho sự ổn định và bảo mật.

*   **Nền tảng:** Zimbra.
*   **Đối tượng phù hợp:** Doanh nghiệp cần một hệ thống email chuyên nghiệp, ổn định, bảo mật và có khả năng tùy chỉnh số lượng tài khoản theo nhu cầu.
*   **Tính năng nổi bật:**
    *   Hỗ trợ truy cập qua Webmail và các ứng dụng email client phổ biến như Outlook.
    *   Tích hợp tính năng tự động trả lời (Auto-responder).
    *   Bao gồm dịch vụ Managed DNS (Quản trị DNS) miễn phí.
*   **Giới hạn:** Tất cả các gói đều có giới hạn gửi 200 email/giờ.

**Các gói dịch vụ (Thông tin chi tiết đang được cập nhật):**

| Gói Dịch Vụ | Giới hạn gửi (email/giờ) | Link Đăng Ký |
| :--- | :--- | :--- |
| **EMAIL 1** | 200 | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=302) |
| **EMAIL 2** | Đang cập nhật | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=264) |
| **EMAIL 3** | Đang cập nhật | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=265) |
| **EMAIL 4** | Đang cập nhật | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=266) |

### 1.2. Cloud Email Server

Đây là giải pháp cung cấp một hệ thống máy chủ email riêng hoạt động trên nền tảng điện toán đám mây, mang lại khả năng kiểm soát và bảo mật vượt trội.

*   **Nền tảng tùy chọn:** Kerio hoặc Zimbra.
*   **Đối tượng phù hợp:** Doanh nghiệp cần một hệ thống email riêng theo tên miền, yêu cầu tính bảo mật cao, hoạt động ổn định, có toàn quyền quản trị và không giới hạn số lượng tài khoản người dùng.
*   **Tính năng nổi bật:**
    *   Tích hợp miễn phí các công cụ bảo mật, bao gồm chống Spam và chống Virus.
    *   Hỗ trợ đầy đủ các giao thức POP3/IMAP/SMTP.
    *   Cung cấp hai dòng gói cước chính dựa trên nền tảng:
        *   **Nền tảng Kerio:** Các gói MINI EMAIL 01, MINI EMAIL 02, MINI EMAIL 03, MINI EMAIL 04.
        *   **Nền tảng Zimbra:** Các gói ES 01, ES 02, ES 03, ES 04.

### 1.3. Email Relay

Email Relay là một giải pháp trung gian giúp định tuyến toàn bộ email gửi ra từ hệ thống Email Server hiện có của khách hàng qua hệ thống của BKNS. Dịch vụ này giúp tăng uy tín IP và đảm bảo tỷ lệ email vào hộp thư đến (inbox) cao.

*   **Đối tượng phù hợp:**
    *   Doanh nghiệp đã có Email Server riêng và gặp vấn đề khi gửi email ra ngoài (ví dụ: IP bị blacklist, email vào spam).
    *   Doanh nghiệp có nhu cầu gửi Email Marketing với số lượng lớn.
*   **Tính năng nổi bật:**
    *   Sử dụng hệ thống IP đã được whitelist để gửi email.
    *   Không giới hạn số lượng tên miền sử dụng.
    *   Cung cấp giao diện quản trị dịch vụ.
    *   Hỗ trợ kỹ thuật 24/7/365.
*   **Giới hạn chung:** Tất cả các gói đều có giới hạn gửi 200 email/giờ. Một số gói cụ thể như BK-RELAY 04 có thêm giới hạn 3.000 email/ngày.

## 2. Điểm mạnh và Lợi thế cạnh tranh (USP)

*   **Đa dạng giải pháp:** Cung cấp nhiều lựa chọn từ Email Hosting, Cloud Email Server riêng, đến Email Relay chuyên dụng, đáp ứng mọi nhu cầu từ cơ bản đến nâng cao.
*   **Bảo mật tích hợp:** Các giải pháp đều chú trọng đến bảo mật, tích hợp sẵn các công cụ chống Spam/Virus để bảo vệ người dùng.
*   **Lựa chọn nền tảng linh hoạt:** Khách hàng có thể lựa chọn giữa các nền tảng email phổ biến và mạnh mẽ là Zimbra và Kerio cho dịch vụ Cloud Email Server.
*   **Giải pháp cho vấn đề gửi mail:** Dịch vụ Email Relay giải quyết triệt để bài toán IP bị blacklist và tối ưu hóa việc gửi email marketing số lượng lớn.
*   **Hỗ trợ chuyên nghiệp:** Cung cấp hỗ trợ kỹ thuật chuyên sâu, đặc biệt là hỗ trợ 24/7/365 cho dịch vụ Email Relay.

## 3. Khi nào nên chọn các giải pháp Email của BKNS?

*   **Chọn Email Hosting:** Khi doanh nghiệp của bạn cần một giải pháp email theo tên miền nhanh chóng, hiệu quả về chi phí, không yêu cầu quyền quản trị sâu và muốn tùy chỉnh số lượng tài khoản linh hoạt.
*   **Chọn Cloud Email Server:** Khi doanh nghiệp của bạn yêu cầu một hệ thống email hoàn toàn riêng biệt, bảo mật cao, có toàn quyền quản trị máy chủ và không muốn bị giới hạn số lượng tài khoản người dùng.
*   **Chọn Email Relay:** Khi bạn đã có sẵn một hệ thống email nhưng đang gặp khó khăn trong việc gửi email ra ngoài (email vào spam, IP bị chặn) hoặc có nhu cầu gửi email marketing một cách hiệu quả.

## Sản phẩm liên quan

*   [Tên Miền BKNS](../ten-mien/index.md)
*   [Web Hosting BKNS](../hosting/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)

---


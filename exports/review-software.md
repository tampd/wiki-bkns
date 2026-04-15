# BKNS Wiki Cross-Verification Request — SOFTWARE

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (0)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (151)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages (10)**: Trang wiki đã compile — CẦN KIỂM TRA

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

- Gói Nâng cao: billing_term = 1 năm None (confidence: high)
- Gói Nâng cao: price = 910000000 VND (confidence: high)
- Gói Nâng cao: support_hours = 24/7 None (confidence: high)
- Gói Nâng cao: user_accounts_limit = unlimited None (confidence: high)
- Gói Cơ bản: billing_term = 1 năm None (confidence: high)
- Gói Cơ bản: price = 650000000 VND (confidence: high)
- Gói Cơ bản: support_hours = 24/7 None (confidence: high)
- Gói Cơ bản: user_accounts_limit = 200 tài khoản (confidence: high)
- Gói Vĩnh viễn: billing_term = Vĩnh viễn None (confidence: high)
- Gói Vĩnh viễn: has_feature = Cấu hình và phát triển theo yêu cầu của Tỉnh None (confidence: high)
- Gói Vĩnh viễn: price = 1910000000 VND (confidence: high)
- Gói Vĩnh viễn: support_hours = 24/7 None (confidence: high)
- Gói Vĩnh viễn: user_accounts_limit = unlimited None (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: description = Là một công cụ phần mềm dùng để đánh giá mức độ chuyển đổi số theo phân cấp địa phương, dựa trên bộ chỉ số DTI (Digital Transformation Index) do Bộ Thông tin và Truyền thông ban hành. None (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: has_feature = Bản đồ số liệu trong tỉnh None (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: target_customer = Các cơ quan, đơn vị, tỉnh thành cần một công cụ để theo dõi, báo cáo, và so sánh tiến độ chuyển đổi số. None (confidence: high)
- DirectAdmin Lite: account_limit = 10 Account (confidence: high)
- LiteSpeed Web Server: architecture = hướng sự kiện None (confidence: high)
- LiteSpeed Enterprise: attribute = ổn định None (confidence: high)
- LiteSpeed Web Server: benefit = Giảm tải CPU server None (confidence: high)
- LiteSpeed Web Server: capability = xử lý hàng ngàn kết nối đồng thời None (confidence: high)
- Bản quyền Softaculous: category = Phần mềm None (confidence: high)
- Bản Quyền CloudLinux OS: compatibility = DirectAdmin None (confidence: high)
- DirectAdmin: crawl_date = 2026-04-05T14:25:00+07:00 None (confidence: high)
- Bản quyền cPanel/WHM: crawl_timestamp = 2026-04-05T14:25:00+07:00 None (confidence: high)
- Bản quyền vBulletin: description = vBulletin là một hệ quản trị nội dung mạnh mẽ và lâu đời, được thiết kế chuyên biệt để xây dựng và quản lý các diễn đàn trực tuyến và mạng xã hội. Dịch vụ này cung cấp các gói bản quyền chính hãng cho phần mềm vBulletin, cho phép người dùng triển khai một nền tảng cộng đồng cho website của mình. None (confidence: high)
- DirectAdmin Standard: domain_limit = unlimited None (confidence: high)
- Bản quyền Softaculous: feature = Cài đặt bằng một cú nhấp chuột None (confidence: high)
- Bản Quyền CloudLinux OS: installation_option = Có thể được cài đặt trên các máy chủ hiện tại. None (confidence: high)
- LiteSpeed Web Server: is_replacement_for = Apache None (confidence: high)
- Bản Quyền CloudLinux OS: max_price = 26 USD (confidence: high)
- Bản Quyền CloudLinux OS: migration_process = Quá trình chuyển đổi từ CentOS hoặc RHEL sang CloudLinux dễ dàng. None (confidence: high)
- DirectAdmin: min_cpu_cores = 1 core (confidence: high)
- Bản Quyền CloudLinux OS: min_price = 14 USD (confidence: high)
- DirectAdmin: min_ram = 1 GB (confidence: high)
- Bản quyền vBulletin: ordering_process = Có nút 'ĐẶT MUA' dẫn đến giỏ hàng. None (confidence: high)
- LiteSpeed Web Server: performance_claim = Nhanh hơn gấp nhiều lần None (confidence: high)
- Bản Quyền CloudLinux OS: platform = CentOS/RHEL None (confidence: high)
- Bản quyền phần mềm DirectAdmin: policy = Kể từ ngày 01/07/2020, DirectAdmin đã ngừng bán bản quyền lifetime và ngừng hỗ trợ đổi địa chỉ IP cho loại bản quyền này. None (confidence: high)
- DirectAdmin Standard: monthly_price = 790000 VND (confidence: high)
- Bản Quyền CloudLinux OS: price_note = Giá tùy thuộc vào loại giấy phép (cho VPS hoặc máy chủ riêng) và số lượng máy chủ. None (confidence: high)
- Bản quyền vBulletin: pricing_policy = Chi phí cho tất cả các gói dịch vụ không được niêm yết công khai và yêu cầu khách hàng phải liên hệ để nhận báo giá. None (confidence: high)
- LiteSpeed Web Server: product_type = web server hiệu suất cao None (confidence: high)
- LiteSpeed Web Server: protocol_support = QUIC None (confidence: high)
- Bản quyền vBulletin: registration_process = Trang có nút 'ĐẶT MUA' dẫn đến giỏ hàng. None (confidence: high)
- Bản quyền Softaculous: requirement = Cần có máy chủ hoặc VPS đã cài đặt một trong các control panel được hỗ trợ. None (confidence: high)
- LiteSpeed Web Server: resource_usage_comparison = sử dụng ít tài nguyên (CPU/RAM) hơn so với Apache None (confidence: high)
- Bản Quyền CloudLinux OS: sales_policy = Khách hàng cần liên hệ trực tiếp với BKNS để có giá chính xác và thông tin về các chương trình khuyến mại. None (confidence: high)
- Bản quyền vBulletin: short_description = Cung cấp bản quyền phần mềm vBulletin, một hệ quản trị nội dung (CMS) chuyên dụng để xây dựng diễn đàn (forum) và mạng xã hội. None (confidence: high)
- LiteSpeed Web Server: source_url = https://www.bkns.vn/phan-mem/litespeed.html None (confidence: high)
- DirectAdmin Standard: support = Hỗ trợ cài đặt và tối ưu miễn phí. None (confidence: high)
- DirectAdmin: supported_os_distro = Debian None (confidence: high)
- LiteSpeed Web Server: tagline = Web Server Hiệu Suất Cao None (confidence: high)
- Bản quyền vBulletin: target_audience = Các cá nhân, doanh nghiệp và tổ chức muốn tạo và quản lý một cộng đồng trực tuyến, diễn đàn thảo luận. None (confidence: high)
- OpenLiteSpeed: target_customer = phù hợp cho các trang web không yêu cầu các tính năng của phiên bản Enterprise None (confidence: high)
- Bản quyền vBulletin: tax_policy = Bản quyền phần mềm không chịu thuế. None (confidence: high)
- Bản quyền Softaculous: url = https://www.bkns.vn/phan-mem/softaculous.html None (confidence: high)
- DirectAdmin Standard: user_limit = unlimited None (confidence: high)
- LiteSpeed Web Server: version_count = 3 phiên bản chính (confidence: high)
- Softaculous Page Crawl: crawl_timestamp = 2026-04-05T14:25:00+07:00 None (confidence: high)
- Softaculous Page Crawl: source_url = https://www.bkns.vn/phan-mem/softaculous.html None (confidence: high)
- Imunify360: category = phan-mem None (confidence: high)
- Imunify360: data_completeness_note = Không có bảng giá nào được tìm thấy trong nội dung trích xuất. None (confidence: high)
- Imunify360: description = Imunify360 là một giải pháp bảo mật dành cho server, được xây dựng dựa trên công nghệ Trí tuệ nhân tạo (AI). None (confidence: high)
- Imunify360: feature = Ngăn chặn sự tiếp cận trái phép từ hacker None (confidence: high)
- Imunify360: name = Phần mềm bảo mật Imunify360 None (confidence: high)
- Imunify360: related_service = CloudLinux None (confidence: high)
- Imunify360: target_audience = Các cá nhân, doanh nghiệp quản trị server None (confidence: high)
- Imunify360: url = https://www.bkns.vn/phan-mem/imunify360.html None (confidence: high)
- Bản Quyền CloudLinux OS: category = phan-mem  (confidence: high)
- Bản Quyền CloudLinux OS: name = Bản Quyền CloudLinux OS  (confidence: high)
- Bản Quyền CloudLinux OS: source_url = https://www.bkns.vn/phan-mem/cloudlinux.html  (confidence: high)
- Bản quyền cPanel/WHM: category = Phần mềm None (confidence: high)
- Bản quyền cPanel/WHM: source_url = https://www.bkns.vn/phan-mem/cpanel-whm.html None (confidence: high)
- 5 Account: account_limit = 5 account (confidence: high)
- 5 Account: monthly_price = 697000 VND (confidence: high)
- 5 Account: target_product = VPS None (confidence: high)
- Bản quyền cPanel/WHM: category = Phần mềm None (confidence: high)
- Bản quyền cPanel/WHM: comparison = Giao diện được đánh giá là đẹp, hiện đại, dễ dùng so với DirectAdmin (đơn giản). None (confidence: high)
- Bản quyền cPanel/WHM: component = WHM (WebHost Manager) (giao diện quản trị viên) None (confidence: high)
- Bản quyền cPanel/WHM: description = Cung cấp bản quyền cPanel/WHM, một phần mềm quản lý hosting cho máy chủ chạy hệ điều hành Linux. None (confidence: high)
- Bản quyền cPanel/WHM: feature = Preferences: cho phép người dùng tùy chỉnh giao diện, ngôn ngữ, mật khẩu. None (confidence: high)
- Bản quyền cPanel/WHM: name = Bản quyền cPanel/WHM None (confidence: high)
- Bản quyền cPanel/WHM: source_url = https://www.bkns.vn/phan-mem/cpanel-whm.html None (confidence: high)
- Bản quyền cPanel/WHM: system_requirement = Hệ điều hành Linux None (confidence: high)
- Bản quyền cPanel/WHM: target_customer = Cá nhân và doanh nghiệp cần một công cụ quản lý máy chủ hosting với giao diện đồ họa trực quan, dễ sử dụng. None (confidence: high)
- DirectAdmin Lite: account_limit = 10 Account (confidence: high)
- Bản quyền phần mềm DirectAdmin: description = DirectAdmin là một phần mềm quản trị server (control panel) có giao diện đồ họa, được biết đến như một giải pháp thay thế cho cPanel. None (confidence: high)
- DirectAdmin Standard: domain_limit = unlimited None (confidence: high)
- DirectAdmin Standard: feature = Sử dụng cho IP theo yêu cầu của khách hàng. None (confidence: high)
- Bản quyền phần mềm DirectAdmin: policy = Khách hàng Thuê Server tại BKNS được hỗ trợ đổi IP miễn phí (áp dụng cho IP thuộc BKNS). None (confidence: high)
- DirectAdmin Standard: price = 790000 VND (confidence: high)
- Bản quyền phần mềm DirectAdmin: promotion = Khách hàng Thuê Server tại BKNS sẽ được miễn phí License DirectAdmin. None (confidence: high)
- DirectAdmin Standard: target_audience = Đơn vị cung cấp dịch vụ chuyên nghiệp, thiết kế web, kinh doanh Hosting. None (confidence: high)
- DirectAdmin Standard: user_limit = unlimited None (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: acronym = DTI  (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: acronym_expansion = Digital Transformation Index  (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: compliance = Theo tiêu chuẩn Bộ TT&TT  (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: data_crawl_timestamp = 2026-04-05T14:25:00+07:00  (confidence: high)
- Phần Mềm Đánh Giá Chuyển Đổi Số DTI: description = Là giải pháp đánh giá mức độ chuyển đổi số của doanh nghiệp.  (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.software.bang-gia
title: Phần Mềm & Bản Quyền BKNS — Bảng Giá
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 18
compile_cost_usd: 0.0094
self_review: pass
corrections: 0
approved_at: '2026-04-07T13:43:52.203258+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Bảng Giá

Trang này tổng hợp bảng giá chi tiết cho các sản phẩm phần mềm và bản quyền do BKNS cung cấp, dựa trên dữ liệu đã được xác thực.

### Phần mềm DTI

| Tên gói | Giá | Setup fee | VAT | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| Gói Cơ bản | 650.000.000 VNĐ / năm | Đang cập nhật | Đang cập nhật | Thanh toán theo chu kỳ 1 năm. |
| Gói Nâng cao | 910.000.000 VNĐ / năm | Đang cập nhật | Đang cập nhật | Thanh toán theo chu kỳ 1 năm. |
| Gói Vĩnh viễn | 1.910.000.000 VNĐ | Đang cập nhật | Đang cập nhật | Thanh toán một lần duy nhất. |

### Bản quyền Control Panel

| Tên gói | Giá tháng | Setup fee | VAT | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| cPanel - 5 Account | 697.000 VNĐ | Đang cập nhật | Đang cập nhật | Dành cho VPS. |
| DirectAdmin - Standard | 790.000 VNĐ | Đang cập nhật | Đang cập nhật | Áp dụng cho Cloud VPS / Server có IP ngoài BKNS (External license). |
| Plesk Obsidian - Developer Pack | 500.000 VNĐ | Đang cập nhật | Đang cập nhật | Dành cho máy chủ riêng (Dedicated License). |

### Bản quyền Hệ điều hành

**Bản Quyền CloudLinux OS**
*   **Giá tham khảo:** $14 - $26 / tháng
*   **Ghi chú:** Giá tùy thuộc vào loại giấy phép (cho VPS hoặc máy chủ riêng) và số lượng máy chủ.

### Bản quyền Diễn đàn vBulletin

| Tên gói | Giá | Setup fee | VAT | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| vBulletin Cloud (Theo tháng) | Giá liên hệ | Đang cập nhật | Đang cập nhật | Chi phí theo tháng. |
| vBulletin Cloud (Theo năm) | Giá liên hệ | Đang cập nhật | Đang cập nhật | Chi phí theo năm. |
| vBulletin 5 Connect + Mobile Suite Bundle (Upgrade) | Giá liên hệ | Đang cập nhật | Đang cập nhật | Gói nâng cấp. |

***

### Sản phẩm liên quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Máy Chủ BKNS](../server/index.md)

***
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.software.cau-hoi-thuong-gap
title: Phần Mềm & Bản Quyền BKNS — Câu Hỏi Thường Gặp
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T13:43:52.205819+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Câu Hỏi Thường Gặp

> FAQ cho Phần Mềm & Bản Quyền BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### chi-tiet.md

---
page_id: wiki.products.software.chi-tiet
title: Phần Mềm — Chi Tiết Từng Sản Phẩm
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 39
compile_cost_usd: 0.0184
self_review: fail
corrections: 4
approved_at: '2026-04-07T13:43:52.208326+07:00'
---

# Phần Mềm — Chi Tiết Từng Sản Phẩm

Trang này tổng hợp thông tin chi tiết về các sản phẩm phần mềm do BKNS cung cấp hoặc hỗ trợ, dựa trên các dữ liệu đã được xác thực. Thông tin bao gồm tính năng, yêu cầu kỹ thuật, và so sánh giữa các gói sản phẩm.

## Phần Mềm Quản Trị Hosting (Control Panel)

Đây là các công cụ không thể thiếu để quản lý máy chủ, website, email và các tài nguyên hosting khác một cách trực quan và hiệu quả.

### DirectAdmin

DirectAdmin là một control panel quản trị hosting mạnh mẽ và nhẹ, được biết đến với hiệu suất cao và giao diện đơn giản.

**Yêu cầu hệ thống tối thiểu:**
*   **CPU:** 1 Core
*   **RAM:** 1 GB
*   **Hệ điều hành hỗ trợ:** Linux (bao gồm CentOS, Rocky Linux, AlmaLinux, Ubuntu, Debian)

**Gói bản quyền (DirectAdmin Standard):**
*   **Loại License:** Sử dụng cho IP theo yêu cầu của khách hàng.
*   **Giới hạn:** Không giới hạn số User và domain.
*   **Hỗ trợ:** Hỗ trợ cài đặt và tối ưu miễn phí.

### cPanel/WHM

cPanel/WHM là một trong những control panel phổ biến nhất thế giới, cung cấp một hệ sinh thái tính năng toàn diện cho cả người dùng cuối và nhà quản trị máy chủ.

*   **Tính năng nổi bật:**
    *   **Preferences:** Cho phép người dùng tùy chỉnh giao diện, ngôn ngữ, mật khẩu, và các thiết lập khác của cPanel.

### Plesk Obsidian

Plesk là một control panel đa nền tảng, hỗ trợ cả Linux và Windows, nổi bật với giao diện hiện đại và các tiện ích mở rộng mạnh mẽ cho WordPress, bảo mật và lập trình.

*   **Hệ điều hành hỗ trợ:** Linux và Windows.
*   **Tính năng chung:** Security Advisor.

**So sánh các phiên bản:**

| Tính năng | Web Host Edition | Web Pro Edition |
| :--- | :--- | :--- |
| Giới hạn Domain | Không giới hạn | [Cần bổ sung] |
| Quản lý Reseller | [Cần bổ sung] | Có |

## Phần Mềm Bảo Mật & Tối Ưu Hóa Server

Các giải pháp giúp tăng cường bảo mật, cải thiện hiệu suất và tự động hóa việc quản lý ứng dụng trên máy chủ của bạn.

### LiteSpeed Web Server

LiteSpeed Web Server là một giải pháp thay thế hiệu suất cao cho Apache, được xây dựng trên kiến trúc hướng sự kiện.

*   **Kiến trúc:** Hướng sự kiện.
*   **Khả năng:** Xử lý hàng ngàn kết nối đồng thời với việc sử dụng ít tài nguyên.
*   **Lợi ích:** Giảm tải CPU server.
*   **Giao thức hỗ trợ:** Hỗ trợ các giao thức mới nhất như HTTP/3 và QUIC.

### Imunify360

Imunify360 là một giải pháp bảo mật toàn diện cho máy chủ web, sử dụng công nghệ Trí tuệ nhân tạo (AI) để chủ động bảo vệ hệ thống.

*   **Công nghệ cốt lõi:** Trí tuệ nhân tạo (AI).
*   **Tính năng chính:** Giúp bảo vệ server khỏi việc bị nhiễm mã độc và ngăn chặn sự tiếp cận trái phép từ hacker.
*   **Hệ điều hành hỗ trợ:** Ubuntu 16.04 và các phiên bản khác [Cần bổ sung danh sách chi tiết].

### CloudLinux OS

CloudLinux OS là hệ điều hành được thiết kế đặc biệt cho môi trường shared hosting, giúp tăng cường sự ổn định, bảo mật và cô lập tài nguyên giữa các tài khoản.

*   **Nền tảng:** Dựa trên hệ điều hành CentOS/RHEL.

### Softaculous

Softaculous là một trình cài đặt tự động, giúp người dùng triển khai hàng trăm ứng dụng web chỉ với vài cú nhấp chuột.

*   **Tính năng nổi bật:**
    *   Cài đặt bằng một cú nhấp chuột cho hơn 400 ứng dụng.
    *   Cung cấp môi trường Staging để thử nghiệm thay đổi trước khi áp dụng lên website chính.
*   **Ví dụ script hỗ trợ:** WordPress, Joomla, Drupal, Magento.

## Phần Mềm Chuyên Dụng

Các phần mềm được phát triển cho những mục đích và nghiệp vụ đặc thù.

### Phần Mềm Đánh Giá Chuyển Đổi Số DTI

Đây là một bộ công cụ phần mềm được thiết kế để giúp các tổ chức, địa phương đánh giá và xây dựng lộ trình chuyển đổi số.

*   **Tính năng chung:**
    *   Bản đồ số liệu trong tỉnh.
    *   Đề xuất lộ trình chuyển đổi số.

**So sánh các gói dịch vụ:**

| Tính năng | Gói Cơ bản | Gói Nâng cao | Gói Vĩnh viễn |
| :--- | :--- | :--- | :--- |
| **Số lượng tài khoản** | 200 tài khoản | Không giới hạn | Không giới hạn |
| **Hỗ trợ kỹ thuật** | 24/7 | 24/7 | 24/7 trong vòng 3 năm |
| **Chức năng đặc thù** | [Cần bổ sung] | [Cần bổ sung] | Cấu hình và phát triển theo yêu cầu của Tỉnh |

### vBulletin

vBulletin là một nền tảng mạnh mẽ để xây dựng và quản lý các cộng đồng trực tuyến, diễn đàn.

**Gói vBulletin 5 Connect + Mobile Suite Bundle:**
*   **Tính năng đi kèm:** Bao gồm Mobile Suite Bundle.
*   **Mô tả:** Cung cấp ứng dụng trên Face Book, IOS…

## Sản Phẩm Liên Quan

*   [Hosting BKNS](../hosting/index.md)
*   [VPS Cloud BKNS](../vps/index.md)
*   [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • [Cần cập nhật ngày thực tế]

---

### chinh-sach.md

---
page_id: wiki.products.software.chinh-sach
title: Phần Mềm & Bản Quyền BKNS — Chính Sách
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 20
compile_cost_usd: 0.0122
self_review: fail
corrections: 3
approved_at: '2026-04-07T13:43:52.210837+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Chính Sách

Trang này tổng hợp các thông tin về chính sách dịch vụ, điều khoản sử dụng, và quy trình hỗ trợ cho các sản phẩm Phần mềm & Bản quyền do BKNS cung cấp. Toàn bộ thông tin được trích xuất và tổng hợp tự động từ cơ sở dữ liệu của BKNS.

## Chính sách Hỗ trợ (Support Policy)

BKNS cung cấp hỗ trợ cho các sản phẩm phần mềm với các điều kiện cụ thể như sau:

| Sản phẩm/Gói dịch vụ | Thời gian hỗ trợ | Chi tiết hỗ trợ |
| --- | --- | --- |
| DTI Software (Gói Cơ bản, Nâng cao) | 24/7 | Đang cập nhật |
| DTI Software (Gói Vĩnh viễn) | 24/7 trong vòng 3 năm | Đang cập nhật |
| DirectAdmin Standard | Đang cập nhật | Hỗ trợ cài đặt và tối ưu miễn phí. |

## Chính sách Bản quyền & Giấy phép (Licensing Policy)

### Thay đổi IP và Loại bản quyền
*   **DirectAdmin:**
    *   Kể từ ngày 01/07/2020, DirectAdmin đã ngừng bán bản quyền lifetime và ngừng hỗ trợ đổi địa chỉ IP cho loại bản quyền này.
    *   Khách hàng Thuê Server tại BKNS được hỗ trợ đổi IP miễn phí (áp dụng cho IP thuộc BKNS).
*   **Imunify360:** Bản quyền được tính theo IP và có thể thay đổi IP.

### Nâng cấp & Add-on
*   **vBulletin:** Cung cấp gói nâng cấp từ phiên bản vBulletin 4 lên vBulletin 5 Connect.
*   **Plesk Obsidian:** Các tính năng có ghi chú là 'Available as Add-on' (biểu tượng ➕) là các tùy chọn cần mua thêm và không bao gồm trong giá gói cơ bản.

## Chính sách Bán hàng, Giá & Thuế

*   **CloudLinux OS:** Để có giá chính xác và thông tin về các chương trình khuyến mại, khách hàng cần liên hệ trực tiếp với BKNS.
*   **Bản quyền vBulletin:** Chi phí cho tất cả các gói dịch vụ không được niêm yết công khai và yêu cầu khách hàng phải liên hệ để nhận báo giá.
*   **Chính sách thuế:** Bản quyền phần mềm không chịu thuế.

## Quy trình Đăng ký & Kích hoạt

*   **Bản quyền vBulletin:** Trang dịch vụ có nút 'ĐẶT MUA' dẫn đến giỏ hàng để khách hàng tiến hành đăng ký.
*   **Plesk Obsidian License:** Khách hàng có thể đặt mua license trực tiếp trên trang dịch vụ bằng cách nhấn vào nút 'ĐẶT MUA'. Hệ thống sẽ chuyển hướng đến giỏ hàng trên trang my.bkns.net để hoàn tất thanh toán.

## Tương thích & Tính năng

*   **Hệ điều hành hỗ trợ:**
    *   **DirectAdmin:** Hỗ trợ các hệ điều hành Linux phổ biến như CentOS, Rocky Linux, AlmaLinux, Ubuntu, Debian.
    *   **Imunify360:** Hỗ trợ Ubuntu 16.04.
    *   **Plesk Obsidian:** Hỗ trợ cả Linux và Windows.
*   **Giao thức hỗ trợ:**
    *   **LiteSpeed Web Server:** Hỗ trợ giao thức HTTP/3 và QUIC.
*   **Script hỗ trợ:**
    *   **Softaculous:** Hỗ trợ hơn 400 script, ví dụ như Magento.

## Cam kết dịch vụ (SLA)

Đang cập nhật.

## Chính sách Dùng thử (Trial)

Đang cập nhật.

## Chính sách Hoàn tiền (Refund Policy)

Đang cập nhật.

## Chính sách Sao lưu (Backup Policy)

Đang cập nhật.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### huong-dan.md

---
page_id: wiki.products.software.huong-dan
title: Phần Mềm & Bản Quyền BKNS — Hướng Dẫn
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 4
compile_cost_usd: 0.005
self_review: skipped
corrections: 0
approved_at: '2026-04-07T13:43:52.213468+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Hướng Dẫn

Trang này cung cấp hướng dẫn về quy trình đăng ký, kích hoạt và quản lý các sản phẩm phần mềm và bản quyền do BKNS cung cấp, dựa trên các thông tin đã được xác thực.

### 1. Hướng dẫn Đăng ký & Mua bản quyền

Quy trình đặt mua bản quyền phần mềm tại BKNS nhìn chung rất đơn giản và trực tiếp.

**Quy trình chung:**

1.  **Chọn sản phẩm:** Truy cập trang chi tiết của sản phẩm phần mềm bạn quan tâm (ví dụ: Bản quyền vBulletin, Plesk Obsidian License).
2.  **Đặt mua:** Nhấn vào nút **"ĐẶT MUA"** trên trang dịch vụ.
3.  **Thanh toán:** Hệ thống sẽ chuyển hướng bạn đến giỏ hàng trên trang `my.bkns.net` để hoàn tất quá trình thanh toán.

### 2. Hướng dẫn Kích hoạt & Triển khai

**Bản Quyền CloudLinux OS**

*   Quá trình chuyển đổi từ hệ điều hành CentOS hoặc RHEL sang CloudLinux được thực hiện dễ dàng.

*(Các hướng dẫn kích hoạt cho sản phẩm khác đang được cập nhật.)*

### 3. Hướng dẫn Quản lý & Sử dụng

Đang cập nhật.

### 4. Xử lý sự cố (Troubleshooting)

Đang cập nhật.

---

**Sản phẩm liên quan:**
- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### index.md

---
page_id: wiki.products.software.index
title: Phần Mềm & Bản Quyền BKNS — Trang Tổng Quan
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 46
compile_cost_usd: 0.0174
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:43:52.216649+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Trang Tổng Quan

Danh mục Phần mềm & Bản quyền tại BKNS cung cấp các giải pháp phần mềm và bản quyền chính hãng, phục vụ cho việc quản trị máy chủ, bảo mật, xây dựng cộng đồng trực tuyến và đánh giá hiệu quả hoạt động. Các sản phẩm này bao gồm từ các control panel phổ biến, giải pháp bảo mật AI, cho đến các công cụ chuyên dụng cho doanh nghiệp và cơ quan nhà nước.

## Mục lục

*   **[Tổng Quan](tong-quan.md)**
*   [Bảng Giá](bang-gia.md)
*   [Thông số kỹ thuật](thong-so.md)
*   [Tính năng](tinh-nang.md)
*   [Chính sách](chinh-sach.md)
*   [Câu hỏi thường gặp](cau-hoi-thuong-gap.md)
*   [So sánh](so-sanh.md)
*   [Hướng dẫn](huong-dan.md)

## Sản phẩm trong danh mục

### [Bản quyền cPanel/WHM](san-pham/cpanel-whm.md)
Cung cấp bản quyền cPanel/WHM, một phần mềm quản lý hosting cho máy chủ chạy hệ điều hành Linux. Sản phẩm phù hợp cho cá nhân và doanh nghiệp cần một công cụ quản lý máy chủ hosting với giao diện đồ họa trực quan, dễ sử dụng.

### [Bản quyền phần mềm DirectAdmin](san-pham/directadmin.md)
DirectAdmin là một phần mềm quản trị server (control panel) có giao diện đồ họa, được biết đến như một giải pháp thay thế cho cPanel. Sản phẩm hướng đến các đơn vị cung cấp dịch vụ chuyên nghiệp, thiết kế web, và kinh doanh Hosting.

### [Bản quyền Plesk Obsidian](san-pham/plesk-obsidian.md)
Cung cấp bản quyền phần mềm quản trị hosting Plesk Obsidian cho VPS và máy chủ riêng (Dedicated Server). Dịch vụ phù hợp với quản trị viên máy chủ, nhà cung cấp dịch vụ hosting, và các nhà phát triển web.

### [Phần mềm bảo mật Imunify360](san-pham/imunify360.md)
Imunify360 là một giải pháp bảo mật toàn diện dành cho server, được xây dựng dựa trên công nghệ Trí tuệ nhân tạo (AI) để phát hiện và ngăn chặn các mối đe dọa. Sản phẩm phù hợp với các cá nhân và doanh nghiệp quản trị server.

### [Bản Quyền CloudLinux OS](san-pham/cloudlinux-os.md)
Cung cấp bản quyền hệ điều hành CloudLinux OS.

### [LiteSpeed Web Server](san-pham/litespeed.md)
Cung cấp bản quyền LiteSpeed Web Server, bao gồm phiên bản thương mại Enterprise và phiên bản miễn phí OpenLiteSpeed phù hợp cho các trang web không yêu cầu các tính năng của phiên bản Enterprise.

### [Bản quyền Softaculous](san-pham/softaculous.md)
Softaculous là một trình cài đặt ứng dụng tự động (auto-installer), cho phép cài đặt hơn 400+ script và ứng dụng web phổ biến chỉ với vài cú nhấp chuột.

### [Bản quyền vBulletin](san-pham/vbulletin.md)
Cung cấp các gói bản quyền chính hãng cho phần mềm vBulletin, một hệ quản trị nội dung (CMS) chuyên dụng để xây dựng diễn đàn (forum) và mạng xã hội. Dịch vụ phù hợp cho các cá nhân, doanh nghiệp và tổ chức muốn tạo và quản lý một cộng đồng trực tuyến.

### [Phần Mềm Đánh Giá Chuyển Đổi Số DTI](san-pham/phan-mem-danh-gia-chuyen-doi-so-dti.md)
Là một công cụ phần mềm dùng để đánh giá mức độ chuyển đổi số theo phân cấp địa phương, dựa trên bộ chỉ số DTI (Digital Transformation Index) do Bộ Thông tin và Truyền thông ban hành. Giải pháp phù hợp cho các cơ quan, đơn vị, tỉnh thành cần một công cụ để theo dõi, báo cáo, và so sánh tiến độ chuyển đổi số.

## Sản phẩm liên quan
- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### so-sanh.md

---
page_id: wiki.products.software.so-sanh
title: Phần Mềm & Bản Quyền BKNS — So Sánh
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T13:43:52.219399+07:00'
---

# Phần Mềm & Bản Quyền BKNS — So Sánh

> So sánh nội bộ các sản phẩm trong Phần Mềm & Bản Quyền BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### thong-so.md

---
page_id: wiki.products.software.thong-so
title: Phần Mềm & Bản Quyền BKNS — Thông Số Kỹ Thuật
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 19
compile_cost_usd: 0.0079
self_review: fail
corrections: 3
approved_at: '2026-04-07T13:43:52.221871+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Thông Số Kỹ Thuật

Trang này tổng hợp và so sánh các thông số kỹ thuật của các sản phẩm phần mềm và bản quyền do BKNS cung cấp, dựa trên dữ liệu đã được xác thực.

### Phần mềm DTI

Bảng so sánh các gói phần mềm DTI.

| Gói Dịch Vụ | Số Lượng Tài Khoản | Hỗ Trợ Kỹ Thuật |
| :--- | :--- | :--- |
| Gói Cơ bản | 200 tài khoản | 24/7 |
| Gói Nâng cao | Không giới hạn | 24/7 |
| Gói Vĩnh viễn | Không giới hạn | 24/7 trong vòng 3 năm |

### Control Panel

Thông số kỹ thuật chi tiết cho các phần mềm quản lý máy chủ (control panel).

#### DirectAdmin

*   **Giới hạn (Bản Standard)**: Không giới hạn số User, domain.
*   **Hỗ trợ (Bản Standard)**: Hỗ trợ cài đặt và tối ưu miễn phí.
*   **Cấu hình tối thiểu**:
    *   CPU: 1 Core
    *   RAM: 1 GB
*   **Hệ điều hành hỗ trợ**: Linux (CentOS, Rocky Linux, AlmaLinux, Ubuntu, Debian).

#### Plesk Obsidian

*   **Giới hạn Domain (Bản Web Host)**: Không giới hạn.
*   **Hệ điều hành hỗ trợ**: Linux, Windows.
*   **Cấu hình tối thiểu**: Đang cập nhật.

### Phần Mềm & Tiện Ích Khác

Thông tin về các phần mềm và tiện ích mở rộng khác.

#### LiteSpeed Web Server

*   **Hỗ trợ giao thức**: QUIC (HTTP/3).

#### Imunify360

*   **Hệ điều hành hỗ trợ**: Ubuntu 16.04.

#### Softaculous

*   **Script hỗ trợ**: Hỗ trợ hơn 400 script, bao gồm WordPress, Joomla, Drupal, Magento.

### Sản phẩm liên quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • [ngày hiện tại]

---

### tinh-nang.md

---
page_id: wiki.products.software.tinh-nang
title: Phần Mềm & Bản Quyền BKNS — Tính Năng
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 30
compile_cost_usd: 0.013
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:43:52.224350+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Tính Năng

Features nổi bật của các sản phẩm phần mềm và bản quyền do BKNS cung cấp, giúp người dùng quản trị, bảo mật và tối ưu hóa hệ thống hiệu quả.

## Các Tính Năng Nổi Bật

Các phần mềm được phân phối bởi BKNS đi kèm với nhiều tính năng mạnh mẽ, được nhóm thành các danh mục chính sau:

### Quản trị & Vận hành

*   **Triển khai Nhanh chóng:** Hỗ trợ cài đặt nhanh chóng hơn 400 ứng dụng và tập lệnh chỉ bằng một cú nhấp chuột. Cung cấp môi trường Staging để thử nghiệm tính năng mới một cách an toàn trước khi triển khai chính thức (Softaculous).
*   **Tùy chỉnh Linh hoạt:** Cho phép người dùng tùy chỉnh các thiết lập cá nhân như giao diện, ngôn ngữ, mật khẩu (cPanel/WHM). Một số license cho phép sử dụng cho IP theo yêu cầu của khách hàng (DirectAdmin Standard).
*   **Phát triển theo Yêu cầu:** Cung cấp khả năng cấu hình và phát triển phần mềm theo yêu cầu đặc thù của từng Tỉnh (Phần Mềm Đánh Giá Chuyển Đổi Số DTI - Gói Vĩnh viễn).
*   **Công cụ Phân tích & Hoạch định:** Tích hợp các công cụ chuyên sâu như bản đồ số liệu trong tỉnh và đề xuất lộ trình chuyển đổi số (Phần Mềm Đánh Giá Chuyển Đổi Số DTI).
*   **Tích hợp Mở rộng:** Hỗ trợ các tính năng đi kèm như ứng dụng trên Facebook, iOS (vBulletin 5 Connect + Mobile Suite Bundle) và quản lý tài khoản đại lý (Plesk Obsidian - Web Pro Edition).

### Bảo mật

*   **Bảo vệ Chủ động bằng AI:** Sử dụng công nghệ Trí tuệ nhân tạo (AI) để bảo vệ máy chủ khỏi mã độc và ngăn chặn sự tiếp cận trái phép từ hacker (Imunify360).
*   **Tư vấn Tăng cường Bảo mật:** Tích hợp công cụ Security Advisor giúp rà soát và đưa ra các khuyến nghị để nâng cao an toàn cho hệ thống (Plesk Obsidian).

### Hiệu suất

*   **Tối ưu hóa Tốc độ và Tài nguyên:** Sử dụng kiến trúc hướng sự kiện (event-driven) giúp xử lý hàng ngàn kết nối đồng thời, giảm tải CPU cho máy chủ. Hỗ trợ các giao thức web hiện đại như HTTP/3 và QUIC để tăng tốc độ tải trang (LiteSpeed Web Server).

### Hỗ trợ Kỹ thuật

*   **Hỗ trợ 24/7:** Nhiều gói sản phẩm phần mềm cung cấp dịch vụ hỗ trợ kỹ thuật liên tục 24/7.
*   **Hỗ trợ Cài đặt & Tối ưu:** Cung cấp dịch vụ hỗ trợ cài đặt và tối ưu miễn phí cho một số sản phẩm (DirectAdmin Standard).
*   **Hỗ trợ Dài hạn:** Một số gói sản phẩm đặc thù như Gói Vĩnh viễn của Phần mềm DTI được hỗ trợ kỹ thuật trong vòng 3 năm.

## Nền Tảng Hỗ Trợ

Các phần mềm do BKNS cung cấp tương thích với nhiều hệ điều hành và nền tảng phổ biến, đảm bảo tính linh hoạt trong triển khai.

*   **Linux:** Hỗ trợ các phiên bản phổ biến như CentOS, RHEL (CloudLinux OS), Rocky Linux, AlmaLinux, Ubuntu, Debian (DirectAdmin, Imunify360).
*   **Windows:** Hỗ trợ hệ điều hành Windows (Plesk Obsidian).
*   **Script & Ứng dụng:** Hỗ trợ hàng trăm script phổ biến như WordPress, Joomla, Drupal, Magento (Softaculous).

## Sản phẩm liên quan

- [Web Hosting BKNS](../hosting/index.md)
- [Cloud VPS BKNS](../vps/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### tong-quan.md

---
page_id: wiki.products.software.tong-quan
title: Phần Mềm & Bản Quyền BKNS — Tổng Quan Chi Tiết
category: products/software
updated: '2026-04-07'
review_state: approved
claims_used: 75
compile_cost_usd: 0.0361
self_review: fail
corrections: 1
approved_at: '2026-04-07T13:43:52.227038+07:00'
---

# Phần Mềm & Bản Quyền BKNS — Tổng Quan Chi Tiết

## Tổng Quan

Dịch vụ Phần Mềm & Bản Quyền của BKNS cung cấp các công cụ, giấy phép và giải pháp phần mềm thiết yếu, giúp khách hàng tối ưu hóa việc quản trị, bảo mật và vận hành hạ tầng máy chủ, website. Các sản phẩm này giải quyết các bài toán chuyên biệt từ quản trị hosting, tăng cường an ninh mạng, tối ưu hiệu suất web server cho đến các công cụ đánh giá chuyên ngành theo tiêu chuẩn của cơ quan nhà nước.

Mục tiêu của danh mục này là trang bị cho các quản trị viên, nhà phát triển và doanh nghiệp những công cụ mạnh mẽ, chính hãng để xây dựng, quản lý và bảo vệ các tài sản số một cách hiệu quả và chuyên nghiệp.

## Các Sản Phẩm & Dịch Vụ Phần Mềm Nổi Bật

BKNS cung cấp một danh mục đa dạng các phần mềm và bản quyền, đáp ứng nhiều nhu cầu khác nhau.

### 1. Phần Mềm Quản Trị Hosting (Control Panel)

Đây là nhóm công cụ có giao diện đồ họa giúp quản lý máy chủ và hosting một cách trực quan.

*   **Bản quyền cPanel/WHM:**
    *   **Mô tả:** Là phần mềm quản lý hosting phổ biến cho máy chủ chạy hệ điều hành Linux.
    *   **Tính năng nổi bật:** Cho phép người dùng tùy chỉnh giao diện, ngôn ngữ, mật khẩu và các thiết lập khác thông qua mục "Preferences".
    *   **Đối tượng:** Cá nhân và doanh nghiệp cần một công cụ quản lý máy chủ hosting với giao diện đồ họa trực quan, dễ sử dụng.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/cpanel-whm.html](https://www.bkns.vn/phan-mem/cpanel-whm.html)

*   **Bản quyền DirectAdmin:**
    *   **Mô tả:** Một giải pháp control panel nhẹ, hiệu quả, thường được xem là sự thay thế cho cPanel.
    *   **Hệ điều hành hỗ trợ:** Linux (CentOS, Rocky Linux, AlmaLinux, Ubuntu, Debian).
    *   **Gói "Standard":** Dành cho đơn vị cung cấp dịch vụ chuyên nghiệp, thiết kế web, kinh doanh Hosting. License được sử dụng cho IP theo yêu cầu của khách hàng và được hỗ trợ cài đặt, tối ưu miễn phí.

*   **Bản quyền Plesk Obsidian:**
    *   **Mô tả:** Cung cấp bản quyền phần mềm quản trị hosting cho VPS và máy chủ riêng, hỗ trợ cả Linux và Windows.
    *   **Tính năng nổi bật:** Tích hợp Security Advisor. Phiên bản "Web Pro Edition" có tính năng quản lý đại lý (Reseller Management).
    *   **Đối tượng:** Quản trị viên máy chủ, nhà cung cấp dịch vụ hosting, và các nhà phát triển web.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/plesk-obsidian.html](https://www.bkns.vn/phan-mem/plesk-obsidian.html)

### 2. Phần Mềm Bảo Mật

*   **Imunify360:**
    *   **Mô tả:** Một giải pháp bảo mật toàn diện cho server, được xây dựng dựa trên công nghệ Trí tuệ nhân tạo (AI) để phát hiện và ngăn chặn các mối đe dọa.
    *   **Tính năng chính:** Ngăn chặn sự tiếp cận trái phép từ hacker và bảo vệ server khỏi mã độc.
    *   **Đối tượng:** Các cá nhân, doanh nghiệp quản trị server.
    *   **Hệ điều hành hỗ trợ:** Ubuntu 16.04.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/imunify360.html](https://www.bkns.vn/phan-mem/imunify360.html)

### 3. Phần Mềm Tối Ưu Hóa & Tiện Ích

*   **LiteSpeed Web Server:**
    *   **Mô tả:** Web server hiệu suất cao với kiến trúc hướng sự kiện, giúp xử lý hàng ngàn kết nối đồng thời và giảm tải CPU cho server.
    *   **Phiên bản:** Bao gồm phiên bản thương mại (LiteSpeed Enterprise) và phiên bản miễn phí (OpenLiteSpeed) cho các trang web không yêu cầu tính năng cao cấp.
    *   **Công nghệ hỗ trợ:** HTTP/3 và QUIC.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/litespeed.html](https://www.bkns.vn/phan-mem/litespeed.html)

*   **Bản Quyền CloudLinux OS:**
    *   **Mô tả:** Hệ điều hành được thiết kế để tăng cường sự ổn định, bảo mật và mật độ cho các môi trường hosting chia sẻ.
    *   **Nền tảng:** Dựa trên hệ điều hành CentOS/RHEL.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/cloudlinux.html](https://www.bkns.vn/phan-mem/cloudlinux.html)

*   **Bản quyền Softaculous:**
    *   **Mô tả:** Là một trình cài đặt ứng dụng tự động (auto-installer), cho phép cài đặt nhanh chóng hơn 400 ứng dụng web phổ biến như WordPress, Joomla, Magento chỉ bằng một cú nhấp chuột.
    *   **Tính năng nổi bật:** Hỗ trợ tạo môi trường Staging.
    *   **Nguồn:** [https://www.bkns.vn/phan-mem/softaculous.html](https://www.bkns.vn/phan-mem/softaculous.html)

### 4. Phần Mềm Nền Tảng & Chuyên Dụng

*   **Bản quyền vBulletin:**
    *   **Mô tả:** Một hệ quản trị nội dung (CMS) mạnh mẽ và lâu đời, chuyên dụng để xây dựng và quản lý các diễn đàn trực tuyến (forum) và mạng xã hội.
    *   **Đối tượng:** Các cá nhân, doanh nghiệp và tổ chức muốn tạo và quản lý một cộng đồng trực tuyến.
    *   **Các gói cung cấp:**
        *   **vBulletin Cloud:** Chi phí theo năm cho vBulletin 5 Connect.
        *   **vBulletin 5 Connect + Mobile Suite Bundle:** Bao gồm ứng dụng trên Facebook, iOS,... và là phiên bản Lifetime.

*   **Phần Mềm Đánh Giá Chuyển Đổi Số DTI:**
    *   **Mô tả:** Là một công cụ phần mềm dùng để đánh giá mức độ chuyển đổi số theo phân cấp địa phương, dựa trên bộ chỉ số DTI (Digital Transformation Index) do Bộ Thông tin và Truyền thông ban hành.
    *   **Tính năng chung:** Bản đồ số liệu trong tỉnh, đề xuất lộ trình chuyển đổi số.
    *   **Đối tượng:** Các cơ quan, đơn vị, tỉnh thành cần một công cụ để theo dõi, báo cáo, và so sánh tiến độ chuyển đổi số.
    *   **Các gói dịch vụ:**

| Tính năng / Gói | Gói Cơ bản | Gói Nâng cao | Gói Vĩnh viễn |
| :--------------- | :--------- | :----------- | :------------------------------------------------ |
| **Chức năng** | Đang cập nhật | Đang cập nhật | Cấu hình và phát triển theo yêu cầu của Tỉnh |
| **Hỗ trợ** | 24/7 | 24/7 | 24/7 trong vòng 3 năm |

    *   **Nguồn:** [https://www.bkns.vn/phan-mem-danh-gia-chuyen-doi-so-dti.html](https://www.bkns.vn/phan-mem-danh-gia-chuyen-doi-so-dti.html)

## Đối Tượng Phù Hợp

Dịch vụ phần mềm và bản quyền của BKNS hướng đến nhiều nhóm đối tượng:

*   **Quản trị viên hệ thống và nhà phát triển:** Cần các công cụ control panel (cPanel, Plesk, DirectAdmin), web server hiệu năng cao (LiteSpeed) và hệ điều hành chuyên dụng (CloudLinux) để tối ưu hóa môi trường làm việc.
*   **Doanh nghiệp và nhà cung cấp dịch vụ Hosting:** Tận dụng các bản quyền phần mềm để cung cấp dịch vụ cho khách hàng cuối, đồng thời đảm bảo sự ổn định và bảo mật cho toàn bộ hệ thống.
*   **Chủ sở hữu website và cộng đồng trực tuyến:** Sử dụng Softaculous để dễ dàng cài đặt ứng dụng và vBulletin để xây dựng các diễn đàn, mạng xã hội chuyên nghiệp.
*   **Cơ quan nhà nước, đơn vị sự nghiệp và tổ chức:** Sử dụng các phần mềm chuyên ngành như "Phần Mềm Đánh Giá Chuyển Đổi Số DTI" để phục vụ công tác quản lý và báo cáo.

## Điểm Mạnh & Lợi Thế Cạnh Tranh (USP)

*   **Danh mục đa dạng:** Cung cấp một loạt các phần mềm thiết yếu từ quản trị, bảo mật, tối ưu hóa đến các ứng dụng chuyên ngành, giúp khách hàng tìm thấy mọi thứ ở một nơi.
*   **Tập trung vào hiệu suất và bảo mật:** Các sản phẩm như LiteSpeed giúp giảm tải CPU, trong khi Imunify360 sử dụng AI để chủ động ngăn chặn các cuộc tấn công, mang lại sự an tâm cho người quản trị.
*   **Hỗ trợ chuyên nghiệp:** BKNS cung cấp "Hỗ trợ cài đặt và tối ưu miễn phí" cho một số sản phẩm như DirectAdmin, đây là một giá trị gia tăng quan trọng so với việc chỉ bán license đơn thuần.
*   **Giải pháp chuyên ngành độc đáo:** Phần mềm Đánh giá DTI là một sản phẩm đặc thù, thể hiện năng lực phát triển và đáp ứng các nhu cầu của thị trường ngách.

## Khi Nào Nên Chọn Dịch Vụ Phần Mềm?

Bạn nên cân nhắc sử dụng các dịch vụ trong danh mục này khi:

*   Bạn đã có hoặc đang thuê [Cloud VPS BKNS](../vps/index.md) hoặc [Máy Chủ BKNS](../server/index.md) và cần các công cụ mạnh mẽ để quản trị, bảo mật và tối ưu hóa hạ tầng đó.
*   Bạn là một nhà cung cấp dịch vụ hosting và cần các bản quyền phần mềm (cPanel, CloudLinux, Imunify360) để xây dựng gói dịch vụ cho khách hàng của mình.
*   Bạn muốn xây dựng một website chuyên biệt như diễn đàn, cộng đồng và cần một nền tảng mạnh mẽ như vBulletin.
*   Bạn muốn đơn giản hóa việc cài đặt và quản lý các ứng dụng web trên hosting/server của mình với công cụ như Softaculous.
*   Bạn là một cơ quan, tổ chức cần một công cụ phần mềm chuyên dụng để đánh giá và báo cáo theo các tiêu chuẩn cụ thể.

## Sản Phẩm Liên Quan

*   [Web Hosting BKNS](../hosting/index.md)
*   [Cloud VPS BKNS](../vps/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2024-04-07

---


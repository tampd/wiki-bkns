# BKNS Wiki Cross-Verification Request — HOSTING

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (176)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (255)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
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

- Platium Web Hosting BKCP01: cpu_cores = 1 Core  [CLM-EXCEL-product_hosting_bkcp01-cpu_cores]
- Platium Web Hosting BKCP01: domain_count = 1  [CLM-EXCEL-product_hosting_bkcp01-domain_count]
- Platium Web Hosting BKCP01: monthly_price = 29000 VND [CLM-EXCEL-product_hosting_bkcp01-monthly_price]
- Platium Web Hosting BKCP01: price_1y = 330600 VND [CLM-EXCEL-product_hosting_bkcp01-price_1y]
- Platium Web Hosting BKCP01: price_2y = 556800 VND [CLM-EXCEL-product_hosting_bkcp01-price_2y]
- Platium Web Hosting BKCP01: price_3y = 730800 VND [CLM-EXCEL-product_hosting_bkcp01-price_3y]
- Platium Web Hosting BKCP01: price_4y = 835200 VND [CLM-EXCEL-product_hosting_bkcp01-price_4y]
- Platium Web Hosting BKCP01: ram = 1 GB  [CLM-EXCEL-product_hosting_bkcp01-ram]
- Platium Web Hosting BKCP01: storage = 2 GB  [CLM-EXCEL-product_hosting_bkcp01-storage]
- Platium Web Hosting BKCP02: cpu_cores = 1 Core  [CLM-EXCEL-product_hosting_bkcp02-cpu_cores]
- Platium Web Hosting BKCP02: domain_count = 2  [CLM-EXCEL-product_hosting_bkcp02-domain_count]
- Platium Web Hosting BKCP02: monthly_price = 50000 VND [CLM-EXCEL-product_hosting_bkcp02-monthly_price]
- Platium Web Hosting BKCP02: price_1y = 570000 VND [CLM-EXCEL-product_hosting_bkcp02-price_1y]
- Platium Web Hosting BKCP02: price_2y = 960000 VND [CLM-EXCEL-product_hosting_bkcp02-price_2y]
- Platium Web Hosting BKCP02: price_3y = 1260000 VND [CLM-EXCEL-product_hosting_bkcp02-price_3y]
- Platium Web Hosting BKCP02: price_4y = 1440000 VND [CLM-EXCEL-product_hosting_bkcp02-price_4y]
- Platium Web Hosting BKCP02: ram = 2 GB  [CLM-EXCEL-product_hosting_bkcp02-ram]
- Platium Web Hosting BKCP02: storage = 5 GB  [CLM-EXCEL-product_hosting_bkcp02-storage]
- Platium Web Hosting BKCP03: cpu_cores = 2 Cores  [CLM-EXCEL-product_hosting_bkcp03-cpu_cores]
- Platium Web Hosting BKCP03: domain_count = 3  [CLM-EXCEL-product_hosting_bkcp03-domain_count]
- Platium Web Hosting BKCP03: monthly_price = 78000 VND [CLM-EXCEL-product_hosting_bkcp03-monthly_price]
- Platium Web Hosting BKCP03+: cpu_cores = 2 Cores  [CLM-EXCEL-product_hosting_bkcp03_plus-cpu_cores]
- Platium Web Hosting BKCP03+: domain_count = 4  [CLM-EXCEL-product_hosting_bkcp03_plus-domain_count]
- Platium Web Hosting BKCP03+: monthly_price = 110000 VND [CLM-EXCEL-product_hosting_bkcp03_plus-monthly_price]
- Platium Web Hosting BKCP03+: price_1y = 1254000 VND [CLM-EXCEL-product_hosting_bkcp03_plus-price_1y]
- Platium Web Hosting BKCP03+: price_2y = 2112000 VND [CLM-EXCEL-product_hosting_bkcp03_plus-price_2y]
- Platium Web Hosting BKCP03+: price_3y = 2772000 VND [CLM-EXCEL-product_hosting_bkcp03_plus-price_3y]
- Platium Web Hosting BKCP03+: price_4y = 3168000 VND [CLM-EXCEL-product_hosting_bkcp03_plus-price_4y]
- Platium Web Hosting BKCP03+: ram = 4 GB  [CLM-EXCEL-product_hosting_bkcp03_plus-ram]
- Platium Web Hosting BKCP03+: storage = 10 GB  [CLM-EXCEL-product_hosting_bkcp03_plus-storage]
- Platium Web Hosting BKCP03: price_1y = 889200 VND [CLM-EXCEL-product_hosting_bkcp03-price_1y]
- Platium Web Hosting BKCP03: price_2y = 1497600 VND [CLM-EXCEL-product_hosting_bkcp03-price_2y]
- Platium Web Hosting BKCP03: price_3y = 1965600 VND [CLM-EXCEL-product_hosting_bkcp03-price_3y]
- Platium Web Hosting BKCP03: price_4y = 2246400 VND [CLM-EXCEL-product_hosting_bkcp03-price_4y]
- Platium Web Hosting BKCP03: ram = 2 GB  [CLM-EXCEL-product_hosting_bkcp03-ram]
- Platium Web Hosting BKCP03: storage = 7 GB  [CLM-EXCEL-product_hosting_bkcp03-storage]
- Platium Web Hosting BKCP04: cpu_cores = 2 Cores  [CLM-EXCEL-product_hosting_bkcp04-cpu_cores]
- Platium Web Hosting BKCP04: domain_count = 6  [CLM-EXCEL-product_hosting_bkcp04-domain_count]
- Platium Web Hosting BKCP04: monthly_price = 145000 VND [CLM-EXCEL-product_hosting_bkcp04-monthly_price]
- Platium Web Hosting BKCP04+: cpu_cores = 2 Cores  [CLM-EXCEL-product_hosting_bkcp04_plus-cpu_cores]
- Platium Web Hosting BKCP04+: domain_count = 8  [CLM-EXCEL-product_hosting_bkcp04_plus-domain_count]
- Platium Web Hosting BKCP04+: monthly_price = 200000 VND [CLM-EXCEL-product_hosting_bkcp04_plus-monthly_price]
- Platium Web Hosting BKCP04+: price_1y = 2280000 VND [CLM-EXCEL-product_hosting_bkcp04_plus-price_1y]
- Platium Web Hosting BKCP04+: price_2y = 3840000 VND [CLM-EXCEL-product_hosting_bkcp04_plus-price_2y]
- Platium Web Hosting BKCP04+: price_3y = 5040000 VND [CLM-EXCEL-product_hosting_bkcp04_plus-price_3y]
- Platium Web Hosting BKCP04+: price_4y = 5760000 VND [CLM-EXCEL-product_hosting_bkcp04_plus-price_4y]
- Platium Web Hosting BKCP04+: ram = 6 GB  [CLM-EXCEL-product_hosting_bkcp04_plus-ram]
- Platium Web Hosting BKCP04+: storage = 20 GB  [CLM-EXCEL-product_hosting_bkcp04_plus-storage]
- Platium Web Hosting BKCP04: price_1y = 1653000 VND [CLM-EXCEL-product_hosting_bkcp04-price_1y]
- Platium Web Hosting BKCP04: price_2y = 2784000 VND [CLM-EXCEL-product_hosting_bkcp04-price_2y]
- Platium Web Hosting BKCP04: price_3y = 3654000 VND [CLM-EXCEL-product_hosting_bkcp04-price_3y]
- Platium Web Hosting BKCP04: price_4y = 4176000 VND [CLM-EXCEL-product_hosting_bkcp04-price_4y]
- Platium Web Hosting BKCP04: ram = 5 GB  [CLM-EXCEL-product_hosting_bkcp04-ram]
- Platium Web Hosting BKCP04: storage = 15 GB  [CLM-EXCEL-product_hosting_bkcp04-storage]
- Platium Web Hosting BKCP05: cpu_cores = 3 Cores  [CLM-EXCEL-product_hosting_bkcp05-cpu_cores]
- Platium Web Hosting BKCP05: domain_count = 9  [CLM-EXCEL-product_hosting_bkcp05-domain_count]
- Platium Web Hosting BKCP05: monthly_price = 250000 VND [CLM-EXCEL-product_hosting_bkcp05-monthly_price]
- Platium Web Hosting BKCP05+: cpu_cores = 3 Cores  [CLM-EXCEL-product_hosting_bkcp05_plus-cpu_cores]
- Platium Web Hosting BKCP05+: domain_count = 10  [CLM-EXCEL-product_hosting_bkcp05_plus-domain_count]
- Platium Web Hosting BKCP05+: monthly_price = 290000 VND [CLM-EXCEL-product_hosting_bkcp05_plus-monthly_price]
- Platium Web Hosting BKCP05+: price_1y = 3306000 VND [CLM-EXCEL-product_hosting_bkcp05_plus-price_1y]
- Platium Web Hosting BKCP05+: price_2y = 5568000 VND [CLM-EXCEL-product_hosting_bkcp05_plus-price_2y]
- Platium Web Hosting BKCP05+: price_3y = 7308000 VND [CLM-EXCEL-product_hosting_bkcp05_plus-price_3y]
- Platium Web Hosting BKCP05+: price_4y = 8352000 VND [CLM-EXCEL-product_hosting_bkcp05_plus-price_4y]
- Platium Web Hosting BKCP05+: ram = 8 GB  [CLM-EXCEL-product_hosting_bkcp05_plus-ram]
- Platium Web Hosting BKCP05+: storage = 30 GB  [CLM-EXCEL-product_hosting_bkcp05_plus-storage]
- Platium Web Hosting BKCP05: price_1y = 2850000 VND [CLM-EXCEL-product_hosting_bkcp05-price_1y]
- Platium Web Hosting BKCP05: price_2y = 4800000 VND [CLM-EXCEL-product_hosting_bkcp05-price_2y]
- Platium Web Hosting BKCP05: price_3y = 6300000 VND [CLM-EXCEL-product_hosting_bkcp05-price_3y]
- Platium Web Hosting BKCP05: price_4y = 7200000 VND [CLM-EXCEL-product_hosting_bkcp05-price_4y]
- Platium Web Hosting BKCP05: ram = 7 GB  [CLM-EXCEL-product_hosting_bkcp05-ram]
- Platium Web Hosting BKCP05: storage = 25 GB  [CLM-EXCEL-product_hosting_bkcp05-storage]
- Hosting Windows BKSW01: domain_count = 1  [CLM-EXCEL-product_hosting_bksw01-domain_count]
- Hosting Windows BKSW01: monthly_price = 33000 VND [CLM-EXCEL-product_hosting_bksw01-monthly_price]
- Hosting Windows BKSW01: price_1y = 396000 VND [CLM-EXCEL-product_hosting_bksw01-price_1y]
- Hosting Windows BKSW01: price_2y = 665280 VND [CLM-EXCEL-product_hosting_bksw01-price_2y]
- Hosting Windows BKSW01: price_3y = 879120 VND [CLM-EXCEL-product_hosting_bksw01-price_3y]
- Hosting Windows BKSW01: storage = 1 GB  [CLM-EXCEL-product_hosting_bksw01-storage]
- Hosting Windows BKSW02: domain_count = 2  [CLM-EXCEL-product_hosting_bksw02-domain_count]
- Hosting Windows BKSW02: monthly_price = 60000 VND [CLM-EXCEL-product_hosting_bksw02-monthly_price]
- Hosting Windows BKSW02: price_1y = 720000 VND [CLM-EXCEL-product_hosting_bksw02-price_1y]
- Hosting Windows BKSW02: price_2y = 1209600 VND [CLM-EXCEL-product_hosting_bksw02-price_2y]
- Hosting Windows BKSW02: price_3y = 1598400 VND [CLM-EXCEL-product_hosting_bksw02-price_3y]
- Hosting Windows BKSW02: storage = 1.5 GB  [CLM-EXCEL-product_hosting_bksw02-storage]
- Hosting Windows BKSW03: domain_count = 3  [CLM-EXCEL-product_hosting_bksw03-domain_count]
- Hosting Windows BKSW03: monthly_price = 85000 VND [CLM-EXCEL-product_hosting_bksw03-monthly_price]
- Hosting Windows BKSW03+: domain_count = 5  [CLM-EXCEL-product_hosting_bksw03_plus-domain_count]
- Hosting Windows BKSW03+: monthly_price = 135000 VND [CLM-EXCEL-product_hosting_bksw03_plus-monthly_price]
- Hosting Windows BKSW03+: price_1y = 1620000 VND [CLM-EXCEL-product_hosting_bksw03_plus-price_1y]
- Hosting Windows BKSW03+: price_2y = 2721600 VND [CLM-EXCEL-product_hosting_bksw03_plus-price_2y]
- Hosting Windows BKSW03+: price_3y = 3596400 VND [CLM-EXCEL-product_hosting_bksw03_plus-price_3y]
- Hosting Windows BKSW03+: storage = 3.5 GB  [CLM-EXCEL-product_hosting_bksw03_plus-storage]
- Hosting Windows BKSW03: price_1y = 1020000 VND [CLM-EXCEL-product_hosting_bksw03-price_1y]
- Hosting Windows BKSW03: price_2y = 1713600 VND [CLM-EXCEL-product_hosting_bksw03-price_2y]
- Hosting Windows BKSW03: price_3y = 2264400 VND [CLM-EXCEL-product_hosting_bksw03-price_3y]
- Hosting Windows BKSW03: storage = 2.5 GB  [CLM-EXCEL-product_hosting_bksw03-storage]
- Hosting Windows BKSW04: domain_count = 7  [CLM-EXCEL-product_hosting_bksw04-domain_count]
- Hosting Windows BKSW04: monthly_price = 165000 VND [CLM-EXCEL-product_hosting_bksw04-monthly_price]
- Hosting Windows BKSW04+: domain_count = 9  [CLM-EXCEL-product_hosting_bksw04_plus-domain_count]
- Hosting Windows BKSW04+: monthly_price = 210000 VND [CLM-EXCEL-product_hosting_bksw04_plus-monthly_price]
- Hosting Windows BKSW04+: price_1y = 2520000 VND [CLM-EXCEL-product_hosting_bksw04_plus-price_1y]
- Hosting Windows BKSW04+: price_2y = 4233600 VND [CLM-EXCEL-product_hosting_bksw04_plus-price_2y]
- Hosting Windows BKSW04+: price_3y = 5594400 VND [CLM-EXCEL-product_hosting_bksw04_plus-price_3y]
- Hosting Windows BKSW04+: storage = 7 GB  [CLM-EXCEL-product_hosting_bksw04_plus-storage]
- Hosting Windows BKSW04: price_1y = 1980000 VND [CLM-EXCEL-product_hosting_bksw04-price_1y]
- Hosting Windows BKSW04: price_2y = 3326400 VND [CLM-EXCEL-product_hosting_bksw04-price_2y]
- Hosting Windows BKSW04: price_3y = 4395600 VND [CLM-EXCEL-product_hosting_bksw04-price_3y]
- Hosting Windows BKSW04: storage = 5 GB  [CLM-EXCEL-product_hosting_bksw04-storage]
- Hosting Windows BKSW05: domain_count = 12  [CLM-EXCEL-product_hosting_bksw05-domain_count]
- Hosting Windows BKSW05: monthly_price = 250000 VND [CLM-EXCEL-product_hosting_bksw05-monthly_price]
- Hosting Windows BKSW05+: domain_count = 15  [CLM-EXCEL-product_hosting_bksw05_plus-domain_count]
- Hosting Windows BKSW05+: monthly_price = 390000 VND [CLM-EXCEL-product_hosting_bksw05_plus-monthly_price]
- Hosting Windows BKSW05+: price_1y = 4680000 VND [CLM-EXCEL-product_hosting_bksw05_plus-price_1y]
- Hosting Windows BKSW05+: price_2y = 7862400 VND [CLM-EXCEL-product_hosting_bksw05_plus-price_2y]
- Hosting Windows BKSW05+: price_3y = 10389600 VND [CLM-EXCEL-product_hosting_bksw05_plus-price_3y]
- Hosting Windows BKSW05+: storage = 15 GB  [CLM-EXCEL-product_hosting_bksw05_plus-storage]
- Hosting Windows BKSW05: price_1y = 3000000 VND [CLM-EXCEL-product_hosting_bksw05-price_1y]
- Hosting Windows BKSW05: price_2y = 5040000 VND [CLM-EXCEL-product_hosting_bksw05-price_2y]
- Hosting Windows BKSW05: price_3y = 6660000 VND [CLM-EXCEL-product_hosting_bksw05-price_3y]
- Hosting Windows BKSW05: storage = 10 GB  [CLM-EXCEL-product_hosting_bksw05-storage]
- Hosting WordPress WPCP01: domain_count = 2  [CLM-EXCEL-product_hosting_wpcp01-domain_count]
- Hosting WordPress WPCP01: monthly_price = 50000 VND [CLM-EXCEL-product_hosting_wpcp01-monthly_price]
- Hosting WordPress WPCP01: price_1y = 570000 VND [CLM-EXCEL-product_hosting_wpcp01-price_1y]
- Hosting WordPress WPCP01: price_2y = 960000 VND [CLM-EXCEL-product_hosting_wpcp01-price_2y]
- Hosting WordPress WPCP01: price_3y = 1260000 VND [CLM-EXCEL-product_hosting_wpcp01-price_3y]
- Hosting WordPress WPCP01: price_4y = 1440000 VND [CLM-EXCEL-product_hosting_wpcp01-price_4y]
- Hosting WordPress WPCP01: storage = 1 GB  [CLM-EXCEL-product_hosting_wpcp01-storage]
- Hosting WordPress WPCP02: domain_count = 3  [CLM-EXCEL-product_hosting_wpcp02-domain_count]
- Hosting WordPress WPCP02: monthly_price = 78000 VND [CLM-EXCEL-product_hosting_wpcp02-monthly_price]
- Hosting WordPress WPCP02: price_1y = 889200 VND [CLM-EXCEL-product_hosting_wpcp02-price_1y]
- Hosting WordPress WPCP02: price_2y = 1497600 VND [CLM-EXCEL-product_hosting_wpcp02-price_2y]
- Hosting WordPress WPCP02: price_3y = 1965600 VND [CLM-EXCEL-product_hosting_wpcp02-price_3y]
- Hosting WordPress WPCP02: price_4y = 2246400 VND [CLM-EXCEL-product_hosting_wpcp02-price_4y]
- Hosting WordPress WPCP02: storage = 1.5 GB  [CLM-EXCEL-product_hosting_wpcp02-storage]
- Hosting WordPress WPCP03: domain_count = 4  [CLM-EXCEL-product_hosting_wpcp03-domain_count]
- Hosting WordPress WPCP03: monthly_price = 110000 VND [CLM-EXCEL-product_hosting_wpcp03-monthly_price]
- Hosting WordPress WPCP03: price_1y = 1254000 VND [CLM-EXCEL-product_hosting_wpcp03-price_1y]
- Hosting WordPress WPCP03: price_2y = 2112000 VND [CLM-EXCEL-product_hosting_wpcp03-price_2y]
- Hosting WordPress WPCP03: price_3y = 2772000 VND [CLM-EXCEL-product_hosting_wpcp03-price_3y]
- Hosting WordPress WPCP03: price_4y = 3168000 VND [CLM-EXCEL-product_hosting_wpcp03-price_4y]
- Hosting WordPress WPCP03: storage = 2 GB  [CLM-EXCEL-product_hosting_wpcp03-storage]
- Hosting WordPress WPCP04: domain_count = 5  [CLM-EXCEL-product_hosting_wpcp04-domain_count]
- Hosting WordPress WPCP04: monthly_price = 145000 VND [CLM-EXCEL-product_hosting_wpcp04-monthly_price]
- Hosting WordPress WPCP04: price_1y = 1653000 VND [CLM-EXCEL-product_hosting_wpcp04-price_1y]
- Hosting WordPress WPCP04: price_2y = 2784000 VND [CLM-EXCEL-product_hosting_wpcp04-price_2y]
- Hosting WordPress WPCP04: price_3y = 3654000 VND [CLM-EXCEL-product_hosting_wpcp04-price_3y]
- Hosting WordPress WPCP04: price_4y = 4176000 VND [CLM-EXCEL-product_hosting_wpcp04-price_4y]
- Hosting WordPress WPCP04: storage = 3 GB  [CLM-EXCEL-product_hosting_wpcp04-storage]
- Hosting WordPress WPCP05: domain_count = 6  [CLM-EXCEL-product_hosting_wpcp05-domain_count]
- Hosting WordPress WPCP05: monthly_price = 200000 VND [CLM-EXCEL-product_hosting_wpcp05-monthly_price]
- Hosting WordPress WPCP05: price_1y = 2280000 VND [CLM-EXCEL-product_hosting_wpcp05-price_1y]
- Hosting WordPress WPCP05: price_2y = 3840000 VND [CLM-EXCEL-product_hosting_wpcp05-price_2y]
- Hosting WordPress WPCP05: price_3y = 5040000 VND [CLM-EXCEL-product_hosting_wpcp05-price_3y]
- Hosting WordPress WPCP05: price_4y = 5760000 VND [CLM-EXCEL-product_hosting_wpcp05-price_4y]
- Hosting WordPress WPCP05: storage = 5 GB  [CLM-EXCEL-product_hosting_wpcp05-storage]
- Hosting WordPress WPCP06: domain_count = 8  [CLM-EXCEL-product_hosting_wpcp06-domain_count]
- Hosting WordPress WPCP06: monthly_price = 250000 VND [CLM-EXCEL-product_hosting_wpcp06-monthly_price]
- Hosting WordPress WPCP06: price_1y = 2850000 VND [CLM-EXCEL-product_hosting_wpcp06-price_1y]
- Hosting WordPress WPCP06: price_2y = 4800000 VND [CLM-EXCEL-product_hosting_wpcp06-price_2y]
- Hosting WordPress WPCP06: price_3y = 6300000 VND [CLM-EXCEL-product_hosting_wpcp06-price_3y]
- Hosting WordPress WPCP06: price_4y = 7200000 VND [CLM-EXCEL-product_hosting_wpcp06-price_4y]
- Hosting WordPress WPCP06: storage = 8 GB  [CLM-EXCEL-product_hosting_wpcp06-storage]
- Hosting WordPress WPCP07: domain_count = 10  [CLM-EXCEL-product_hosting_wpcp07-domain_count]
- Hosting WordPress WPCP07: monthly_price = 390000 VND [CLM-EXCEL-product_hosting_wpcp07-monthly_price]
- Hosting WordPress WPCP07: price_1y = 4446000 VND [CLM-EXCEL-product_hosting_wpcp07-price_1y]
- Hosting WordPress WPCP07: price_2y = 7488000 VND [CLM-EXCEL-product_hosting_wpcp07-price_2y]
- Hosting WordPress WPCP07: price_3y = 9828000 VND [CLM-EXCEL-product_hosting_wpcp07-price_3y]
- Hosting WordPress WPCP07: price_4y = 11232000 VND [CLM-EXCEL-product_hosting_wpcp07-price_4y]
- Hosting WordPress WPCP07: storage = 15 GB  [CLM-EXCEL-product_hosting_wpcp07-storage]
- Hosting WordPress WPCP08: domain_count = 15  [CLM-EXCEL-product_hosting_wpcp08-domain_count]
- Hosting WordPress WPCP08: monthly_price = 500000 VND [CLM-EXCEL-product_hosting_wpcp08-monthly_price]
- Hosting WordPress WPCP08: price_1y = 5700000 VND [CLM-EXCEL-product_hosting_wpcp08-price_1y]
- Hosting WordPress WPCP08: price_2y = 9600000 VND [CLM-EXCEL-product_hosting_wpcp08-price_2y]
- Hosting WordPress WPCP08: price_3y = 12600000 VND [CLM-EXCEL-product_hosting_wpcp08-price_3y]
- Hosting WordPress WPCP08: price_4y = 14400000 VND [CLM-EXCEL-product_hosting_wpcp08-price_4y]
- Hosting WordPress WPCP08: storage = 30 GB  [CLM-EXCEL-product_hosting_wpcp08-storage]

## LLM-EXTRACTED CLAIMS (Check these)

- Hosting: access.admin = Chỉ có quyền cơ bản, không cài được các phần mềm tuỳ biến  (confidence: high)
- Hosting: admin_access = Chỉ có quyền cơ bản, không cài được các phần mềm tuỳ biến None (confidence: high)
- Hosting Giá Rẻ: backup_frequency = daily  (confidence: high)
- Shared Hosting: backup_solution = Jetbackup  (confidence: high)
- Shared Hosting: benefit = Tăng bảo mật None (confidence: high)
- Hosting Giá Rẻ: bandwidth = unlimited None (confidence: high)
- Hosting Giá Rẻ: control_panel_language = Vietnamese None (confidence: high)
- Hosting Giá Rẻ: description = Dịch vụ lưu trữ web (hosting) giá rẻ, sử dụng ổ cứng SSD Enterprise, dành cho các website có ngân sách hạn chế nhưng vẫn yêu cầu chất lượng và tốc độ.  (confidence: high)
- Hosting WordPress: feature = Bảo mật None (confidence: high)
- Hosting: hardware.storage_capacity = vài chục GB  (confidence: high)
- Hosting Giá Rẻ: has_feature = Redis  (confidence: high)
- Hosting Giá Rẻ: has_free_ssl = True  (confidence: high)
- Hosting Giá Rẻ: has_offer = Tặng theme và plugin bản quyền  (confidence: high)
- Hosting Giá Rẻ: has_policy = Giá chưa bao gồm VAT  (confidence: high)
- Shared Hosting: included_feature = OneClick installer  (confidence: high)
- Hosting Giá Rẻ: name = Hosting Giá Rẻ  (confidence: high)
- Shared Hosting: performance_feature = Redis  (confidence: high)
- Shared Hosting: platform_os = Windows Server  (confidence: high)
- Hosting: price_level = Thấp None (confidence: high)
- Hosting: price_vat_policy = not_included None (confidence: high)
- Hosting: pricing.level = Thấp  (confidence: high)
- BẢNG GIÁ HOSTING: pricing_policy = Chưa bao gồm VAT None (confidence: high)
- Hosting WordPress: product_name = Hosting WordPress None (confidence: high)
- Hosting WordPress: promotion = Giảm 20% khi chuyển dịch vụ về BKNS None (confidence: high)
- Hosting: resource_allocation = Được chia sẻ từ 1 máy chủ None (confidence: high)
- Hosting WordPress: starting_price = 24000 VND (confidence: high)
- Hosting (Web Hosting): storage_type = NVME None (confidence: high)
- Hosting (Web Hosting): support_availability = 24/7 None (confidence: high)
- Shared Hosting: supported_database = MSSQL  (confidence: high)
- Hosting Giá Rẻ: target_audience = Các website cá nhân, blog, trang giới thiệu công ty, doanh nghiệp nhỏ và các dự án mới. None (confidence: high)
- Hosting Giá Rẻ: technical_support_hours = 24/7  (confidence: high)
- Hosting Giá Rẻ: upgrade_policy = dễ dàng nâng cấp lên gói cao hơn None (confidence: high)
- Hosting (Web Hosting): uptime_commitment = >99.9 % (confidence: high)
- BKCP01: cpu_cores = 1 core (confidence: high)
- BKH01: allowed_domains = 1 domain (confidence: high)
- BKH01: bandwidth = unlimited  (confidence: high)
- BKH01: cpu_cores = 1 core (confidence: high)
- BKH01: price = 5700 VND (confidence: high)
- BKH01: ram = 1 GB (confidence: high)
- BKH01: storage_capacity = 1 GB (confidence: high)
- BKH02: allowed_domains = 3 domain (confidence: high)
- BKH02: bandwidth = unlimited  (confidence: high)
- BKH02: cpu_cores = 3 core (confidence: high)
- BKH02: price = 11100 VND (confidence: high)
- BKH02: ram = 2 GB (confidence: high)
- BKH02: storage_capacity = 3 GB (confidence: high)
- BKH03: allowed_domains = 5 domain (confidence: high)
- BKH03: bandwidth = unlimited  (confidence: high)
- BKH03: cpu_cores = 5 core (confidence: high)
- BKH03: price = 23700 VND (confidence: high)
- BKH03: ram = 4 GB (confidence: high)
- BKH03: storage_capacity = 6 GB (confidence: high)
- BKH04: allowed_domains = 6 domain (confidence: high)
- BKH04: bandwidth = unlimited  (confidence: high)
- BKH04: cpu_cores = 6 core (confidence: high)
- BKH04: price = 31500 VND (confidence: high)
- BKH04: ram = 6 GB (confidence: high)
- BKH04: storage_capacity = 8 GB (confidence: high)
- Platinum 3: bandwidth = Không giới hạn  (confidence: high)
- Platinum 4: cpu_cores = 2 Core (confidence: high)
- Platinum Web Hosting: description = Dịch vụ hosting mạnh mẽ nhất của BKNS, sử dụng phần cứng Enterprise chuyên dụng.  (confidence: high)
- Hosting Miễn phí: description = Cung cấp dịch vụ lưu trữ web (hosting) với chi phí 0 đồng. None (confidence: high)
- Hosting Miễn Phí: parent_entity = ENT-PROD-HOSTING None (confidence: high)
- Hosting Miễn Phí: price = 0 VND (confidence: high)
- Hosting Miễn phí: product_category = hosting None (confidence: high)
- Hosting Miễn Phí: provider = BKNS None (confidence: high)
- Hosting Miễn Phí: purpose = khởi tạo website None (confidence: high)
- Hosting Miễn Phí: suitability = phù hợp cho người mới học làm website None (confidence: high)
- Hosting Miễn Phí: support_level = cơ bản None (confidence: high)
- Hosting Miễn Phí: target_audience = người mới bắt đầu None (confidence: high)
- Hosting Miễn phí: target_customer = Các cá nhân muốn bắt đầu một website với chi phí thấp None (confidence: high)
- Hosting Miễn Phí: upgrade_policy = có thể nâng cấp lên gói trả phí bất cứ lúc nào None (confidence: high)
- Hosting Miễn phí: url = https://www.bkns.vn/hosting/hosting-mien-phi.html None (confidence: high)
- Platinum 3: ram = 2 GB (confidence: high)
- Reseller Hosting cPanel: crawl_date = 2026-04-05T14:25:00+07:00 None (confidence: high)
- Reseller Hosting cPanel: feature = Cài WordPress 1 click qua Softaculous None (confidence: high)
- Reseller Hosting cPanel: price_max = 12 USD (confidence: high)
- Reseller Hosting cPanel: price_min = 2 USD (confidence: high)
- Reseller Hosting cPanel: product_name = Reseller Hosting cPanel None (confidence: high)
- Reseller Hosting cPanel: refund_policy = Hoàn tiền 100% nếu không hài lòng None (confidence: high)
- Reseller Hosting cPanel: source_url = https://www.bkns.vn/hosting/reseller-hosting-cpanel.html None (confidence: high)
- Reseller Hosting cPanel: support_availability = 24/5 None (confidence: high)
- Reseller Hosting cPanel: target_audience = Freelancer quản lý nhiều website khách hàng None (confidence: high)
- Platinum 3: storage_capacity = 7 GB (confidence: high)
- Platinum Web Hosting: technology = Ổ cứng NVMe U.2  (confidence: high)
- Platinum 3: website_limit = 3  (confidence: high)
- BKSW01: bandwidth = 20 GB (confidence: high)
- BKSW01: disk_space = 1 GB (confidence: high)
- BKSW01: domain_limit = 1 domain (confidence: high)
- BKSW01: email_account_limit = 5 account (confidence: high)
- BKSW01: ftp_account_limit = 2 account (confidence: high)
- BKSW01: minimum_billing_cycle = 12 month (confidence: high)
- BKSW01: mssql_account_limit = 2 account (confidence: high)
- BKSW01: parked_subdomain_limit = 2 domain (confidence: high)
- BKSW01: monthly_price = 31350 VND (confidence: high)
- BKSW05+: disk_space = 15 GB (confidence: high)
- BKSW05+: domain_limit = 15 domain (confidence: high)
- BKSW05+: price = 10389600 VND (confidence: high)
- Hosting Miễn phí: feature = Allows website creation with no initial cost  (confidence: high)
- Hosting Miễn phí: included_feature = cPanel  (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.hosting.bang-gia
title: Web Hosting BKNS — Bảng Giá
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 134
compile_cost_usd: 0.0492
self_review: error
corrections: 0
approved_at: '2026-04-07T16:01:36.061733+07:00'
---

# Web Hosting BKNS — Bảng Giá

Trang này tổng hợp bảng giá chi tiết cho các dịch vụ Web Hosting do BKNS cung cấp, được biên soạn từ các nguồn dữ liệu nội bộ đã xác thực. Các mức giá này chưa bao gồm thuế Giá trị gia tăng (VAT).

## Bảng giá Platium Web Hosting

Dòng sản phẩm Platium Web Hosting cung cấp nhiều gói với các mức chiết khấu hấp dẫn khi đăng ký dài hạn.

| Tên Gói | Giá / tháng | Giá / 1 năm | Giá / 2 năm | Giá / 3 năm | Giá / 4 năm |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BKCP01** | 29,000 VND | 330,600 VND (Giảm 5%) | 556,800 VND (Giảm 20%) | 730,800 VND (Giảm 30%) | 835,200 VND (Giảm 40%) |
| **BKCP02** | 50,000 VND | 570,000 VND (Giảm 5%) | 960,000 VND (Giảm 20%) | 1,260,000 VND (Giảm 30%) | 1,440,000 VND (Giảm 40%) |
| **BKCP03** | 78,000 VND | 889,200 VND (Giảm 5%) | 1,497,600 VND (Giảm 20%) | 1,965,600 VND (Giảm 30%) | 2,246,400 VND (Giảm 40%) |
| **BKCP03+** | 110,000 VND | 1,254,000 VND (Giảm 5%) | 2,112,000 VND (Giảm 20%) | 2,772,000 VND (Giảm 30%) | 3,168,000 VND (Giảm 40%) |
| **BKCP04** | 145,000 VND | 1,653,000 VND (Giảm 5%) | 2,784,000 VND (Giảm 20%) | 3,654,000 VND (Giảm 30%) | 4,176,000 VND (Giảm 40%) |
| **BKCP04+** | 200,000 VND | 2,280,000 VND (Giảm 5%) | 3,840,000 VND (Giảm 20%) | 5,040,000 VND (Giảm 30%) | 5,760,000 VND (Giảm 40%) |
| **BKCP05** | 250,000 VND | 2,850,000 VND (Giảm 5%) | 4,800,000 VND (Giảm 20%) | 6,300,000 VND (Giảm 30%) | 7,200,000 VND (Giảm 40%) |
| **BKCP05+** | 290,000 VND | 3,306,000 VND (Giảm 5%) | 5,568,000 VND (Giảm 20%) | 7,308,000 VND (Giảm 30%) | 8,352,000 VND (Giảm 40%) |

## Bảng giá Hosting WordPress

Dịch vụ hosting chuyên biệt cho nền tảng WordPress, tối ưu hiệu suất và bảo mật.

| Tên Gói | Giá / tháng | Giá / 1 năm | Giá / 2 năm | Giá / 3 năm | Giá / 4 năm |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WPCP01** | 50,000 VND | 570,000 VND (Giảm 5%) | 960,000 VND (Giảm 20%) | 1,260,000 VND (Giảm 30%) | 1,440,000 VND (Giảm 40%) |
| **WPCP02** | 78,000 VND | 889,200 VND (Giảm 5%) | 1,497,600 VND (Giảm 20%) | 1,965,600 VND (Giảm 30%) | 2,246,400 VND (Giảm 40%) |
| **WPCP03** | 110,000 VND | 1,254,000 VND (Giảm 5%) | 2,112,000 VND (Giảm 20%) | 2,772,000 VND (Giảm 30%) | 3,168,000 VND (Giảm 40%) |
| **WPCP04** | 145,000 VND | 1,653,000 VND (Giảm 5%) | 2,784,000 VND (Giảm 20%) | 3,654,000 VND (Giảm 30%) | 4,176,000 VND (Giảm 40%) |
| **WPCP05** | 200,000 VND | 2,280,000 VND (Giảm 5%) | 3,840,000 VND (Giảm 20%) | 5,040,000 VND (Giảm 30%) | 5,760,000 VND (Giảm 40%) |
| **WPCP06** | 250,000 VND | 2,850,000 VND (Giảm 5%) | 4,800,000 VND (Giảm 20%) | 6,300,000 VND (Giảm 30%) | 7,200,000 VND (Giảm 40%) |
| **WPCP07** | 390,000 VND | 4,446,000 VND (Giảm 5%) | 7,488,000 VND (Giảm 20%) | 9,828,000 VND (Giảm 30%) | 11,232,000 VND (Giảm 40%) |
| **WPCP08** | 500,000 VND | 5,700,000 VND (Giảm 5%) | 9,600,000 VND (Giảm 20%) | 12,600,000 VND (Giảm 30%) | 14,400,000 VND (Giảm 40%) |

## Bảng giá Hosting Windows

Hosting trên nền tảng hệ điều hành Windows, phù hợp cho các website sử dụng ngôn ngữ lập trình ASP.NET và cơ sở dữ liệu MSSQL.

| Tên Gói | Giá / tháng | Giá / 1 năm | Giá / 2 năm | Giá / 3 năm |
| :--- | :--- | :--- | :--- | :--- |
| **BKSW01** | 33,000 VND | 396,000 VND | 665,280 VND (Giảm 16%) | 879,120 VND (Giảm 26%) |
| **BKSW02** | 60,000 VND | 720,000 VND | 1,209,600 VND (Giảm 16%) | 1,598,400 VND (Giảm 26%) |
| **BKSW03** | 85,000 VND | 1,020,000 VND | 1,713,600 VND (Giảm 16%) | 2,264,400 VND (Giảm 26%) |
| **BKSW03+** | 135,000 VND | 1,620,000 VND | 2,721,600 VND (Giảm 16%) | 3,596,400 VND (Giảm 26%) |
| **BKSW04** | 165,000 VND | 1,980,000 VND | 3,326,400 VND (Giảm 16%) | 4,395,600 VND (Giảm 26%) |
| **BKSW04+** | 210,000 VND | 2,520,000 VND | 4,233,600 VND (Giảm 16%) | 5,594,400 VND (Giảm 26%) |
| **BKSW05** | 250,000 VND | 3,000,000 VND | 5,040,000 VND (Giảm 16%) | 6,660,000 VND (Giảm 26%) |
| **BKSW05+** | 390,000 VND | 4,680,000 VND | 7,862,400 VND (Giảm 16%) | 10,389,600 VND (Giảm 26%) |

*Lưu ý: Dịch vụ Hosting Windows có chu kỳ thanh toán tối thiểu là 12 tháng.*

## Các Dịch vụ Hosting Khác

### Hosting Giá Rẻ
Dòng sản phẩm với chi phí tối ưu, phù hợp cho các website cá nhân, blog hoặc các dự án nhỏ.

| Tên Gói | Giá | Chu kỳ thanh toán |
| :--- | :--- | :--- |
| **BKH01** | 5,700 VND | Tháng |
| **BKH02** | 11,100 VND | Tháng |
| **BKH03** | 23,700 VND | Tháng |
| **BKH04** | 31,500 VND | Năm |

### Các gói dịch vụ khác
- **Hosting Miễn Phí**: Cung cấp dịch vụ hosting với chi phí 0 VND, phù hợp để khởi tạo và trải nghiệm website.
- **Reseller Hosting cPanel**: Dịch vụ đại lý hosting, giá từ 2 USD đến 12 USD mỗi tháng.
- **SEO Hosting**: Dịch vụ hosting chuyên dụng cho SEO, giá khởi điểm từ 189,000 VND mỗi tháng.

### Lưu ý chung
- Tất cả các mức giá được niêm yết trong tài liệu này **chưa bao gồm** thuế Giá trị gia tăng (VAT).
- Phí cài đặt (Setup fee): Đang cập nhật.

## Sản phẩm liên quan
- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.hosting.cau-hoi-thuong-gap
title: Web Hosting BKNS — Câu Hỏi Thường Gặp
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:01:36.064512+07:00'
---

# Web Hosting BKNS — Câu Hỏi Thường Gặp

> FAQ cho Web Hosting BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### chinh-sach.md

---
page_id: wiki.products.hosting.chinh-sach
title: Web Hosting BKNS — Chính Sách
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 37
compile_cost_usd: 0.0144
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:01:36.067310+07:00'
---

# Web Hosting BKNS — Chính Sách

Trang này tổng hợp các chính sách chung và cam kết chất lượng dịch vụ (SLA) liên quan đến các gói Web Hosting do BKNS cung cấp. Thông tin được biên soạn dựa trên các nguồn dữ liệu đã được xác thực, giúp người dùng dễ dàng tra cứu và so sánh.

### 1. Cam Kết Chất Lượng Dịch Vụ (SLA)

-   **Thời gian hoạt động (Uptime):** BKNS cam kết uptime cho các dịch vụ Web Hosting là **99.9%** và **>99.9%**.

### 2. Chính Sách Dùng Thử

BKNS cung cấp chính sách dùng thử dịch vụ trong **7 ngày** cho nhiều gói hosting, cho phép khách hàng trải nghiệm trước khi quyết định đăng ký chính thức. Các dịch vụ áp dụng bao gồm:
-   Hosting Giá Rẻ
-   Reseller Hosting cPanel
-   Hosting SEO
-   Hosting Windows (áp dụng cho tất cả các gói)
-   Hosting WordPress (áp dụng cho tất cả các gói)

### 3. Chính Sách Hoàn Tiền

Chính sách hoàn tiền được áp dụng tùy theo từng sản phẩm cụ thể:
-   **Platinum Web Hosting:** Cam kết hoàn tiền trong **30 ngày** nếu khách hàng không hài lòng.
-   **Reseller Hosting cPanel:** Hoàn tiền **100%** nếu khách hàng không hài lòng.
-   Chính sách cho các dịch vụ khác: Đang cập nhật.

### 4. Chính Sách Hỗ Trợ Kỹ Thuật

**Thời gian hỗ trợ**

| Dịch Vụ | Thời Gian Hỗ Trợ | Ghi Chú |
| :--- | :--- | :--- |
| Hosting (Nói chung) | 24/7 | Hỗ trợ kỹ thuật |
| Hosting Giá Rẻ | 24/7 | |
| Platinum Web Hosting | 24/7/365 | |
| Hosting SEO | 24/7 | |
| Hosting Windows | 24/7 | |
| Hosting WordPress | 24/7 | Đội ngũ chuyên môn về WordPress |
| Reseller Hosting cPanel | 24/5 | |
| Hosting Miễn Phí | Đang cập nhật | Hỗ trợ kỹ thuật ở mức cơ bản |

-   **Kênh hỗ trợ (Hotline, Email, Ticket):** Đang cập nhật
-   **Thời gian phản hồi:** Đang cập nhật

### 5. Chính Sách Sao Lưu Dữ Liệu (Backup)

| Dịch Vụ | Tần Suất Sao Lưu | Chi Tiết |
| :--- | :--- | :--- |
| Hosting Giá Rẻ | Hàng ngày | Dữ liệu được tự động sao lưu mỗi ngày. |
| Platinum Web Hosting | 3 lần/ngày | Sao lưu tự động bằng Jetbackup. |
| Reseller Hosting cPanel | Hàng ngày | Sử dụng Jetbackup, lưu trữ 30 bản gần nhất. |
| Hosting WordPress | Hàng ngày | Tự động sao lưu với JetBackup. |

### 6. Chính Sách Thanh Toán

-   **Thuế GTGT (VAT):** Tất cả bảng giá dịch vụ Hosting được công bố đều **chưa bao gồm VAT**.
-   **Chu kỳ thanh toán:**
    -   **Hosting Windows:** Yêu cầu thanh toán theo năm.
    -   Các dịch vụ khác: Đang cập nhật.

### 7. Chính Sách Nâng Cấp

-   **Hosting Miễn Phí:** Người dùng có thể nâng cấp lên gói trả phí bất cứ lúc nào.
-   **Hosting Giá Rẻ:** Hỗ trợ nâng cấp dễ dàng lên các gói dịch vụ cao hơn.

### 8. Điều Khoản Sử Dụng

Đang cập nhật.

### Xem Thêm

-   [Chứng Chỉ SSL BKNS](../ssl/index.md)
-   [Tên Miền BKNS](../ten-mien/index.md)
-   [Email Doanh Nghiệp BKNS](../email/index.md)
-   [Phần Mềm & Bản Quyền BKNS](../software/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### huong-dan.md

---
page_id: wiki.products.hosting.huong-dan
title: Web Hosting BKNS — Hướng Dẫn
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:01:36.069747+07:00'
---

# Web Hosting BKNS — Hướng Dẫn

> Hướng dẫn đăng ký, kích hoạt, quản lý Web Hosting BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### index.md

---
page_id: wiki.products.hosting.index
title: Web Hosting BKNS — Trang Tổng Quan
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 40
compile_cost_usd: 0.0159
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:01:36.072520+07:00'
---

# Web Hosting BKNS — Trang Tổng Quan

BKNS cung cấp nhiều giải pháp lưu trữ web (web hosting) đa dạng, được thiết kế để đáp ứng các nhu cầu khác nhau từ cá nhân, doanh nghiệp nhỏ đến các hệ thống website lớn yêu cầu hiệu suất cao.

## Mục lục
- [Tổng quan](tong-quan.md)
- [Bảng giá](bang-gia.md)
- [Thông số kỹ thuật](thong-so.md)
- [Tính năng chi tiết](tinh-nang.md)
- [Chính sách & Cam kết](chinh-sach.md)
- [Câu hỏi thường gặp (FAQ)](cau-hoi-thuong-gap.md)
- [So sánh các gói dịch vụ](so-sanh.md)
- [Hướng dẫn sử dụng](huong-dan.md)

## Các Dòng Sản Phẩm Hosting

Dưới đây là tổng quan về các dịch vụ web hosting do BKNS cung cấp.

### [Hosting Giá Rẻ](san-pham/hosting-gia-re.md)
- **Mô tả:** Dịch vụ lưu trữ web (hosting) giá rẻ, sử dụng ổ cứng SSD Enterprise, dành cho các website có ngân sách hạn chế nhưng vẫn yêu cầu chất lượng và tốc độ.
- **Phù hợp với:** Các website cá nhân, blog, trang giới thiệu công ty, doanh nghiệp nhỏ và các dự án mới.

### [Hosting WordPress](san-pham/hosting-wordpress.md)
- **Mô tả:** Dịch vụ lưu trữ web được thiết kế và tối ưu hóa đặc biệt cho các website sử dụng mã nguồn WordPress.
- **Phù hợp với:** Các cá nhân, doanh nghiệp sử dụng website WordPress, từ blog cá nhân, trang giới thiệu công ty đến các trang thương mại điện tử.

### [Platinum Web Hosting](san-pham/platinum-web-hosting.md)
- **Mô tả:** Dịch vụ lưu trữ website cao cấp, sử dụng phần cứng hiện đại như 100% ổ cứng NVMe U.2 và CPU Intel Platinum để đạt hiệu suất cao. Đây là dịch vụ hosting mạnh mẽ nhất của BKNS.
- **Phù hợp với:** Các website có lượng truy cập lớn, website thương mại điện tử, báo chí, tin tức yêu cầu tốc độ và sự ổn định.

### [Hosting Windows](san-pham/hosting-windows.md)
- **Mô tả:** Dịch vụ lưu trữ web chạy trên nền tảng hệ điều hành Windows, được tối ưu cho các website sử dụng ngôn ngữ lập trình ASP, ASP.NET và cơ sở dữ liệu MSSQL.
- **Phù hợp với:** Các doanh nghiệp và cá nhân có website hoặc ứng dụng được phát triển bằng công nghệ của Microsoft.

### [Hosting SEO](san-pham/hosting-seo.md)
- **Mô tả:** Dịch vụ hosting chuyên biệt cho SEO.
- **Phù hợp với:** Các chiến dịch link building đa IP.

### [Reseller Hosting cPanel](san-pham/reseller-hosting-cpanel.md)
- **Mô tả:** Dịch vụ cho phép người dùng mua một gói tài nguyên hosting lớn, sau đó chia nhỏ thành các gói hosting con để cung cấp cho khách hàng của mình thông qua control panel cPanel.
- **Phù hợp với:** Các cá nhân, đơn vị thiết kế website, lập trình viên muốn kinh doanh dịch vụ hosting dưới thương hiệu riêng mà không cần đầu tư và quản lý máy chủ vật lý.

### [Hosting Miễn Phí](san-pham/hosting-mien-phi.md)
- **Mô tả:** Cung cấp dịch vụ lưu trữ web (hosting) với chi phí 0 đồng.
- **Phù hợp với:** Sinh viên, lập trình viên có nhu cầu học tập, thử nghiệm code, người mới bắt đầu hoặc các cá nhân muốn bắt đầu một website với chi phí thấp.

## Bảng giá
Thông tin chi tiết về bảng giá đang được cập nhật. Vui lòng tham khảo trang chi tiết của từng sản phẩm.

## Sản phẩm liên quan
- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### so-sanh.md

---
page_id: wiki.products.hosting.so-sanh
title: Web Hosting BKNS — So Sánh
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 0
compile_cost_usd: 0
self_review: skeleton
corrections: 0
approved_at: '2026-04-07T16:01:36.075292+07:00'
---

# Web Hosting BKNS — So Sánh

> So sánh nội bộ các sản phẩm trong Web Hosting BKNS

## Nội dung

⏳ Đang cập nhật — Chưa có claims đủ cho trang này.

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

---

### thong-so.md

---
page_id: wiki.products.hosting.thong-so
title: Web Hosting BKNS — Thông Số Kỹ Thuật
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 116
compile_cost_usd: 0.0302
self_review: error
corrections: 0
approved_at: '2026-04-07T16:01:36.078254+07:00'
---

# Web Hosting BKNS — Thông Số Kỹ Thuật

Trang này tổng hợp và so sánh chi tiết thông số kỹ thuật của các gói dịch vụ Web Hosting do BKNS cung cấp. Dữ liệu được trích xuất từ các nguồn thông tin đã được kiểm duyệt, đảm bảo tính chính xác và khách quan.

## Platinum Web Hosting

Dòng hosting hiệu suất cao, sử dụng phần cứng hiện đại với CPU Intel Xeon Platinum Gen 2 và 100% ổ cứng NVMe U.2, cho tốc độ xử lý nhanh hơn tới 25 lần so với ổ cứng HDD thông thường. Dịch vụ được hỗ trợ kỹ thuật 24/7/365.

| Gói Dịch Vụ | CPU | RAM | Dung lượng (NVMe U.2) |
| :--- | :--- | :--- | :--- |
| Platinum Web Hosting BKCP01 | 1 Core | 1 GB | 2 GB |
| Platinum Web Hosting BKCP02 | 1 Core | 2 GB | 5 GB |
| Platinum Web Hosting BKCP03 | 2 Cores | 2 GB | 7 GB |
| Platinum Web Hosting BKCP03+ | 2 Cores | 4 GB | 10 GB |
| Platinum Web Hosting BKCP04 | 2 Cores | 5 GB | 15 GB |
| Platinum Web Hosting BKCP04+ | 2 Cores | 6 GB | 20 GB |
| Platinum Web Hosting BKCP05 | 3 Cores | 7 GB | 25 GB |
| Platinum Web Hosting BKCP05+ | 3 Cores | 8 GB | 30 GB |

## Hosting WordPress

Dịch vụ hosting chuyên dụng cho website WordPress, được tối ưu hóa với LiteSpeed Web Server và ổ cứng 100% SSD để tăng tốc độ tải trang. Đội ngũ kỹ thuật chuyên môn về WordPress hỗ trợ 24/7.

| Gói Dịch Vụ | CPU | RAM | Dung lượng (SSD) | Băng thông | Tài khoản Email |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Hosting WordPress WPCP01 | 1 Core | 1 GB | 1 GB | Đang cập nhật | 10 |
| Hosting WordPress WPCP02 | Đang cập nhật | Đang cập nhật | 1.5 GB | Unlimited | Đang cập nhật |
| Hosting WordPress WPCP03 | Đang cập nhật | Đang cập nhật | 2 GB | Đang cập nhật | Đang cập nhật |
| Hosting WordPress WPCP04 | Đang cập nhật | Đang cập nhật | 3 GB | Đang cập nhật | Đang cập nhật |
| Hosting WordPress WPCP05 | Đang cập nhật | Đang cập nhật | 5 GB | Đang cập nhật | Đang cập nhật |
| Hosting WordPress WPCP06 | Đang cập nhật | Đang cập nhật | 8 GB | Đang cập nhật | Đang cập nhật |
| Hosting WordPress WPCP07 | Đang cập nhật | Đang cập nhật | 15 GB | Đang cập nhật | Đang cập nhật |
| Hosting WordPress WPCP08 | Đang cập nhật | Đang cập nhật | 30 GB | Đang cập nhật | Đang cập nhật |

## Hosting Windows

Hosting Windows sử dụng ổ cứng SSD Enterprise, hỗ trợ các nền tảng và cơ sở dữ liệu của Microsoft như MSSQL, bên cạnh đó vẫn hỗ trợ MySQL. Dịch vụ được hỗ trợ kỹ thuật 24/7.

| Gói Dịch Vụ | Dung lượng (SSD) | Băng thông | Domain | Tài khoản Email | Parked/Sub Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Hosting Windows BKSW01 | 1 GB | 20 GB | 1 | 5 | 2 |
| Hosting Windows BKSW02 | 1.5 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW03 | 2.5 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW03+ | 3.5 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW04 | 5 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW04+ | 7 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW05 | 10 GB | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| Hosting Windows BKSW05+ | 15 GB | Đang cập nhật | 15 | Đang cập nhật | Đang cập nhật |

## Hosting Giá Rẻ

Giải pháp hosting tiết kiệm chi phí, sử dụng ổ cứng SSD Enterprise để tăng tốc độ đọc/ghi dữ liệu và cung cấp băng thông không giới hạn. Đội ngũ kỹ thuật hỗ trợ 24/7.

| Gói Dịch Vụ | CPU | RAM | Dung lượng (SSD Enterprise) | Băng thông |
| :--- | :--- | :--- | :--- | :--- |
| BKH01 | 1 Core | 1 GB | 1 GB | Unlimited |
| BKH02 | 3 Cores | 2 GB | 3 GB | Unlimited |
| BKH03 | 5 Cores | 4 GB | 6 GB | Unlimited |
| BKH04 | 6 Cores | 6 GB | 8 GB | Unlimited |

## Hosting SEO

Dịch vụ hosting được thiết kế để hỗ trợ các chiến dịch SEO. Hỗ trợ kỹ thuật 24/7.

| Gói Dịch Vụ | CPU | RAM | Dung lượng | Băng thông |
| :--- | :--- | :--- | :--- | :--- |
| BKSEO-01 | Đang cập nhật | 1 GB | Đang cập nhật | Đang cập nhật |
| BKSEO-02 | 2 Core | Đang cập nhật | 8 GB | Unlimited |

## Reseller Hosting cPanel

Dịch vụ dành cho các đại lý, cho phép quản lý nhiều tài khoản hosting con. Sử dụng ổ cứng SSD, băng thông không giới hạn và hỗ trợ caching với Redis. Hỗ trợ kỹ thuật 24/5.

| Gói Dịch Vụ | CPU | RAM | Dung lượng (SSD) | Băng thông | Số lượng Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| RL03 | 2 Core | 2 GB | 20 GB | Unlimited | 12 |

## Xem Thêm

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### tinh-nang.md

---
page_id: wiki.products.hosting.tinh-nang
title: Web Hosting BKNS — Tính Năng
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 38
compile_cost_usd: 0.0118
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:01:36.080894+07:00'
---

# Web Hosting BKNS — Tính Năng

Trang này tổng hợp các tính năng kỹ thuật và tiện ích nổi bật được tích hợp trong các dịch vụ Web Hosting do BKNS cung cấp, dựa trên các thông tin đã được kiểm duyệt.

## Quản trị

*   **cPanel:** Hầu hết các gói hosting được trang bị cPanel, giúp người dùng dễ dàng quản lý website, database, và các tài nguyên khác thông qua một giao diện đồ họa trực quan.
*   **One-Click Installer:** Tích hợp công cụ cài đặt tự động (OneClick Installer/Softaculous) giúp triển khai nhanh chóng các mã nguồn mở phổ biến như WordPress chỉ với một cú nhấp chuột.
*   **Tự động sao lưu (Backup):** Dịch vụ sử dụng công nghệ JetBackup để tự động sao lưu dữ liệu hàng ngày, đảm bảo an toàn và khả năng khôi phục cho website của bạn.
*   **Nhiều IP độc lập:** Một số gói hosting chuyên dụng như Hosting SEO cung cấp nhiều địa chỉ IP độc lập, hỗ trợ tối ưu cho các chiến dịch SEO.

## Bảo mật

*   **Miễn phí SSL:** Tất cả các gói hosting đều được cung cấp chứng chỉ SSL miễn phí, giúp mã hóa kết nối, tăng cường bảo mật và độ tin cậy cho website.
*   **CloudLinux OS:** Sử dụng hệ điều hành CloudLinux để tăng cường sự ổn định và bảo mật, giúp cô lập tài nguyên giữa các tài khoản và ngăn chặn tấn công cục bộ (local-attack).
*   **Imunify360:** Tích hợp giải pháp bảo mật đa tầng Imunify360 trên một số gói hosting chuyên dụng (như Hosting WordPress) để chủ động phòng chống mã độc và các cuộc tấn công.

## Hiệu suất

*   **Ổ cứng NVMe U.2 & CPU Intel Xeon Platinum:** Các gói hosting cao cấp sử dụng phần cứng mạnh mẽ với ổ cứng NVMe U.2 và CPU Intel Xeon Platinum Gen 2, mang lại tốc độ xử lý và truy xuất dữ liệu vượt trội.
*   **Redis & LiteSpeed Cache:** Hỗ trợ các công nghệ caching tiên tiến như Redis và LiteSpeed Cache, giúp tăng tốc độ tải trang và giảm tải cho máy chủ, đặc biệt hiệu quả với các website WordPress.

## Ưu đãi & Dùng thử

*   **Dùng thử 7 ngày:** Các gói như Hosting WordPress và Reseller Hosting cho phép khách hàng dùng thử dịch vụ miễn phí trong 7 ngày.
*   **Tặng theme/plugin:** Một số gói (ví dụ: Hosting Giá Rẻ) có ưu đãi tặng kèm theme và plugin bản quyền, giúp tiết kiệm chi phí cho người dùng.

## Hỗ trợ kỹ thuật

*   **Hỗ trợ 24/7:** BKNS cung cấp dịch vụ hỗ trợ kỹ thuật 24/7 qua nhiều kênh. Một số dịch vụ còn có đội ngũ hỗ trợ chuyên sâu (ví dụ: chuyên về WordPress). Lưu ý: một số gói đặc thù như Reseller Hosting có thời gian hỗ trợ 24/5, và các gói miễn phí có mức hỗ trợ kỹ thuật cơ bản.

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

---
Compiled by BKNS Wiki Bot • 2024-05-21

---

### tong-quan.md

---
page_id: wiki.products.hosting.tong-quan
title: Web Hosting BKNS — Tổng Quan Chi Tiết
category: products/hosting
updated: '2026-04-07'
review_state: approved
claims_used: 78
compile_cost_usd: 0.0334
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:01:36.083421+07:00'
---

# Web Hosting BKNS — Tổng Quan Chi Tiết

Web Hosting là dịch vụ lưu trữ dữ liệu (bao gồm mã nguồn, hình ảnh, cơ sở dữ liệu) và chia sẻ không gian trên máy chủ để website có thể hoạt động và được truy cập trên Internet. Dịch vụ này giải quyết bài toán cơ bản nhất cho bất kỳ cá nhân hay tổ chức nào muốn hiện diện trực tuyến: một nền tảng ổn định, an toàn và tốc độ để vận hành website mà không cần đầu tư hay quản lý hạ tầng máy chủ phức tạp.

BKNS cung cấp một hệ sinh thái dịch vụ Web Hosting đa dạng, được thiết kế chuyên biệt để đáp ứng từng nhu cầu cụ thể của khách hàng, từ các dự án cá nhân nhỏ đến các hệ thống thương mại điện tử yêu cầu hiệu suất cao.

### Các Gói Dịch Vụ Web Hosting tại BKNS

BKNS cung cấp nhiều dòng sản phẩm hosting, mỗi dòng được tối ưu cho một mục đích sử dụng riêng biệt.

#### 1. Hosting Giá Rẻ
Dịch vụ lưu trữ web dành cho các website có ngân sách hạn chế nhưng vẫn yêu cầu chất lượng và tốc độ.
- **Đối tượng:** Các website cá nhân, blog, trang giới thiệu công ty, doanh nghiệp nhỏ và các dự án mới.
- **Công nghệ & Tính năng:**
    - Ổ cứng: SSD Enterprise.
    - Tiện ích: Hỗ trợ Jetbackup, OneClick installer, Redis.
    - Bảo mật: Cung cấp chứng chỉ SSL miễn phí.
- **Ưu đãi:** Tặng theme và plugin bản quyền.
- **Hỗ trợ:** Kỹ thuật 24/7.
- **Lưu ý:** Giá dịch vụ chưa bao gồm VAT.

#### 2. Hosting WordPress
Dịch vụ lưu trữ web được thiết kế và tối ưu hóa đặc biệt cho các website sử dụng mã nguồn WordPress.
- **Đối tượng:** Các cá nhân, doanh nghiệp sử dụng website WordPress, từ blog cá nhân, trang giới thiệu công ty đến các trang thương mại điện tử.
- **Công nghệ & Tính năng:**
    - Tối ưu hiệu suất: Tích hợp sẵn Redis Cache và LiteSpeed Cache.
    - Bảo mật đa tầng: Sử dụng CloudLinux để ngăn chặn tấn công cục bộ và tích hợp Imunify360.
    - Tiện ích: Sao lưu tự động hàng ngày với JetBackup, cài đặt bằng OneClick Install.
- **Hỗ trợ:** Đội ngũ kỹ thuật chuyên môn về WordPress, hỗ trợ 24/7.
- **Dùng thử:** Cung cấp 7 ngày dùng thử miễn phí cho tất cả các gói.

#### 3. Platinum Web Hosting (Cao cấp)
Dịch vụ hosting mạnh mẽ nhất của BKNS, sử dụng phần cứng Enterprise chuyên dụng cho các website yêu cầu hiệu suất cao.
- **Đối tượng:** Các website có lượng truy cập lớn, website thương mại điện tử, báo chí, tin tức yêu cầu tốc độ và sự ổn định.
- **Công nghệ & Tính năng:**
    - CPU: Intel Xeon Platinum Gen 2.
    - Ổ cứng: 100% NVMe U.2.
- **Hỗ trợ:** Đội ngũ kỹ thuật hỗ trợ 24/7/365 qua nhiều kênh liên lạc.
- **URL:** [https://www.bkns.vn/hosting/platinum-web-hosting.html](https://www.bkns.vn/hosting/platinum-web-hosting.html)

#### 4. Hosting Windows
Dịch vụ lưu trữ web chạy trên nền tảng hệ điều hành Windows Server, tối ưu cho các công nghệ của Microsoft.
- **Đối tượng:** Các doanh nghiệp và cá nhân có website hoặc ứng dụng được phát triển bằng ngôn ngữ lập trình ASP, ASP.NET.
- **Công nghệ & Tính năng:**
    - Nền tảng: Windows Server.
    - Cơ sở dữ liệu: Hỗ trợ Microsoft SQL Server (MSSQL) và MySQL.
    - Tiện ích: OneClick installer, hỗ trợ Redis.
    - Bảo mật: Cung cấp chứng chỉ SSL miễn phí.
- **Hỗ trợ:** Đội ngũ kỹ thuật hỗ trợ 24/7.

#### 5. Hosting SEO
Dịch vụ hosting chuyên biệt cho các chiến dịch SEO, đặc biệt là xây dựng hệ thống website vệ tinh (link building).
- **Đối tượng:** Các chiến dịch link building đa IP.
- **Công nghệ & Tính năng:**
    - Tính năng chính: Cung cấp nhiều địa chỉ IP độc lập.
    - Tiện ích: Sao lưu dữ liệu tự động, tích hợp Redis và CloudLinux.
- **Hỗ trợ:** Kỹ thuật 24/7.
- **URL:** [https://www.bkns.vn/hosting/seo-hosting.html](https://www.bkns.vn/hosting/seo-hosting.html)

#### 6. Reseller Hosting cPanel
Dịch vụ cho phép người dùng mua một gói tài nguyên lớn, sau đó chia nhỏ thành các gói hosting con để cung cấp cho khách hàng của mình dưới thương hiệu riêng.
- **Đối tượng:** Các cá nhân, đơn vị thiết kế website, lập trình viên, freelancer muốn kinh doanh dịch vụ hosting.
- **Công nghệ & Tính năng:**
    - Quản lý: Control panel cPanel.
    - Tiện ích: Cài WordPress 1 click qua Softaculous, hỗ trợ Redis.
    - Bảo mật: Sử dụng CloudLinux để cô lập tài nguyên, cung cấp SSL miễn phí.
- **Hỗ trợ:** Kỹ thuật 24/5.
- **Dùng thử:** Cho phép dùng thử trong 7 ngày.
- **URL:** [https://www.bkns.vn/hosting/reseller-hosting-cpanel.html](https://www.bkns.vn/hosting/reseller-hosting-cpanel.html)

#### 7. Hosting Miễn Phí
Dịch vụ lưu trữ web với chi phí 0 đồng, phù hợp cho mục đích học tập, thử nghiệm hoặc các dự án khởi đầu.
- **Đối tượng:** Sinh viên, lập trình viên, người mới bắt đầu, các cá nhân muốn khởi tạo website mà không tốn chi phí ban đầu.
- **Công nghệ & Tính năng:**
    - Quản lý: cPanel.
- **Hỗ trợ:** Hỗ trợ kỹ thuật ở mức cơ bản.
- **URL:** [https://www.bkns.vn/hosting/hosting-mien-phi.html](https://www.bkns.vn/hosting/hosting-mien-phi.html)

### Đối Tượng Phù Hợp
Dịch vụ Web Hosting của BKNS hướng đến một dải khách hàng rộng lớn:
- **Cá nhân và Người mới bắt đầu:** Phù hợp với các gói **Hosting Miễn Phí** và **Hosting Giá Rẻ** để khởi tạo blog, website cá nhân hoặc học tập, thử nghiệm.
- **Doanh nghiệp nhỏ và vừa (SMBs):** Các gói **Hosting Giá Rẻ** và **Hosting WordPress** là lựa chọn tối ưu cho website giới thiệu công ty, trang bán hàng quy mô vừa và nhỏ.
- **Website yêu cầu hiệu suất cao:** **Platinum Web Hosting** đáp ứng nhu cầu của các trang thương mại điện tử, báo chí, tin tức có lượng truy cập lớn, yêu cầu tốc độ xử lý và sự ổn định tuyệt đối.
- **Developers, Freelancers và Agency:**
    - **Hosting Windows:** Dành cho các dự án phát triển trên nền tảng ASP.NET.
    - **Hosting SEO:** Công cụ đắc lực cho các chuyên gia SEO triển khai hệ thống PBN.
    - **Reseller Hosting:** Giải pháp cho các đơn vị thiết kế web và freelancer muốn kinh doanh hosting.

### Điểm Mạnh Cạnh Tranh (USP)
- **Hiệu suất Cao và Ổn định:** Sử dụng các công nghệ phần cứng hiện đại như ổ cứng SSD Enterprise, NVMe U.2 và CPU Intel Xeon Platinum. Tích hợp các công nghệ tăng tốc như Redis và LiteSpeed Cache.
- **Bảo mật Toàn diện:** Nền tảng được gia cố bằng CloudLinux OS giúp tăng cường bảo mật và cô lập tài nguyên giữa các tài khoản hosting. Hầu hết các gói dịch vụ đều được cung cấp chứng chỉ SSL miễn phí.
- **Hỗ trợ Kỹ thuật Chuyên nghiệp:** Đội ngũ hỗ trợ hoạt động 24/7 (một số gói đặc thù là 24/5 hoặc 24/7/365), sẵn sàng giải quyết các vấn đề của khách hàng. Đặc biệt có đội ngũ chuyên sâu về WordPress.
- **Hệ sinh thái Đa dạng:** Cung cấp đầy đủ các gói hosting chuyên biệt, từ miễn phí, giá rẻ đến cao cấp và reseller, đáp ứng chính xác mọi nhu cầu của người dùng.
- **Nhiều Tiện ích Đi kèm:** Tích hợp sẵn các công cụ quản lý phổ biến như cPanel, trình cài đặt tự động OneClick, và công cụ sao lưu JetBackup.

### Khi nào nên chọn Web Hosting BKNS?
Web Hosting là lựa chọn lý tưởng khi bạn cần một giải pháp lưu trữ website nhanh chóng, dễ quản lý và không yêu cầu kiến thức sâu về quản trị máy chủ. Đây là điểm khởi đầu phù hợp cho hầu hết các loại website.

- Chọn **Hosting Giá Rẻ** hoặc **Hosting Miễn Phí** cho các dự án mới, ngân sách hạn chế.
- Chọn **Hosting WordPress** nếu website của bạn được xây dựng trên nền tảng WordPress.
- Chọn **Hosting Windows** nếu ứng dụng của bạn yêu cầu công nghệ của Microsoft (ASP.NET, MSSQL).
- Chọn **Platinum Web Hosting** cho các website quan trọng, có lượng truy cập lớn, yêu cầu tốc độ và sự ổn định cao nhất.
- Chọn **Hosting SEO** khi bạn cần triển khai các chiến dịch SEO với nhiều địa chỉ IP.
- Chọn **Reseller Hosting** nếu bạn muốn kinh doanh dịch vụ hosting dưới thương hiệu riêng.

### Sản Phẩm Liên Quan
- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Tên Miền BKNS](../ten-mien/index.md)
- [Email Doanh Nghiệp BKNS](../email/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---


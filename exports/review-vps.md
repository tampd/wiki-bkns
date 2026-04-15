# BKNS Wiki Cross-Verification Request — VPS

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims (216)**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims (355)**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages (25)**: Trang wiki đã compile — CẦN KIỂM TRA

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

- Cloud VPS AMD EPYC 1: cpu_cores = 1 Core  [CLM-EXCEL-product_vps_epyc_1-cpu_cores]
- Cloud VPS AMD EPYC 1: monthly_price = 165000 VND [CLM-EXCEL-product_vps_epyc_1-monthly_price]
- Cloud VPS AMD EPYC 1: network_speed = 100 Mbps  [CLM-EXCEL-product_vps_epyc_1-network_speed]
- Cloud VPS AMD EPYC 1: price_12m = 1683000 VND [CLM-EXCEL-product_vps_epyc_1-price_12m]
- Cloud VPS AMD EPYC 1: price_24m = 2970000 VND [CLM-EXCEL-product_vps_epyc_1-price_24m]
- Cloud VPS AMD EPYC 1: price_3m = 495000 VND [CLM-EXCEL-product_vps_epyc_1-price_3m]
- Cloud VPS AMD EPYC 1: price_6m = 5445000 VND [CLM-EXCEL-product_vps_epyc_1-price_6m]
- Cloud VPS AMD EPYC 1: ram = 1 GB  [CLM-EXCEL-product_vps_epyc_1-ram]
- Cloud VPS AMD EPYC 1: storage = 20GB  [CLM-EXCEL-product_vps_epyc_1-storage]
- Cloud VPS AMD EPYC 2: cpu_cores = 2 Cores  [CLM-EXCEL-product_vps_epyc_2-cpu_cores]
- Cloud VPS AMD EPYC 2: monthly_price = 210000 VND [CLM-EXCEL-product_vps_epyc_2-monthly_price]
- Cloud VPS AMD EPYC 2: network_speed = 100 Mbps  [CLM-EXCEL-product_vps_epyc_2-network_speed]
- Cloud VPS AMD EPYC 2: price_12m = 2142000 VND [CLM-EXCEL-product_vps_epyc_2-price_12m]
- Cloud VPS AMD EPYC 2: price_24m = 3780000 VND [CLM-EXCEL-product_vps_epyc_2-price_24m]
- Cloud VPS AMD EPYC 2: price_3m = 630000 VND [CLM-EXCEL-product_vps_epyc_2-price_3m]
- Cloud VPS AMD EPYC 2: price_6m = 6930000 VND [CLM-EXCEL-product_vps_epyc_2-price_6m]
- Cloud VPS AMD EPYC 2: ram = 2 GB  [CLM-EXCEL-product_vps_epyc_2-ram]
- Cloud VPS AMD EPYC 2: storage = 30GB  [CLM-EXCEL-product_vps_epyc_2-storage]
- Cloud VPS AMD EPYC 3: cpu_cores = 3 Cores  [CLM-EXCEL-product_vps_epyc_3-cpu_cores]
- Cloud VPS AMD EPYC 3: monthly_price = 320000 VND [CLM-EXCEL-product_vps_epyc_3-monthly_price]
- Cloud VPS AMD EPYC 3: network_speed = 150 Mbps  [CLM-EXCEL-product_vps_epyc_3-network_speed]
- Cloud VPS AMD EPYC 3: price_12m = 3264000 VND [CLM-EXCEL-product_vps_epyc_3-price_12m]
- Cloud VPS AMD EPYC 3: price_24m = 5760000 VND [CLM-EXCEL-product_vps_epyc_3-price_24m]
- Cloud VPS AMD EPYC 3: price_3m = 960000 VND [CLM-EXCEL-product_vps_epyc_3-price_3m]
- Cloud VPS AMD EPYC 3: price_6m = 10560000 VND [CLM-EXCEL-product_vps_epyc_3-price_6m]
- Cloud VPS AMD EPYC 3: ram = 3 GB  [CLM-EXCEL-product_vps_epyc_3-ram]
- Cloud VPS AMD EPYC 3: storage = 40GB  [CLM-EXCEL-product_vps_epyc_3-storage]
- Cloud VPS AMD EPYC 4: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_epyc_4-cpu_cores]
- Cloud VPS AMD EPYC 4: monthly_price = 480000 VND [CLM-EXCEL-product_vps_epyc_4-monthly_price]
- Cloud VPS AMD EPYC 4: network_speed = 150 Mbps  [CLM-EXCEL-product_vps_epyc_4-network_speed]
- Cloud VPS AMD EPYC 4: price_12m = 4896000 VND [CLM-EXCEL-product_vps_epyc_4-price_12m]
- Cloud VPS AMD EPYC 4: price_24m = 8640000 VND [CLM-EXCEL-product_vps_epyc_4-price_24m]
- Cloud VPS AMD EPYC 4: price_3m = 1440000 VND [CLM-EXCEL-product_vps_epyc_4-price_3m]
- Cloud VPS AMD EPYC 4: price_6m = 15840000 VND [CLM-EXCEL-product_vps_epyc_4-price_6m]
- Cloud VPS AMD EPYC 4: ram = 4 GB  [CLM-EXCEL-product_vps_epyc_4-ram]
- Cloud VPS AMD EPYC 4: storage = 50GB  [CLM-EXCEL-product_vps_epyc_4-storage]
- Cloud VPS AMD EPYC 5: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_epyc_5-cpu_cores]
- Cloud VPS AMD EPYC 5: monthly_price = 710000 VND [CLM-EXCEL-product_vps_epyc_5-monthly_price]
- Cloud VPS AMD EPYC 5: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_epyc_5-network_speed]
- Cloud VPS AMD EPYC 5: price_12m = 7242000 VND [CLM-EXCEL-product_vps_epyc_5-price_12m]
- Cloud VPS AMD EPYC 5: price_24m = 12780000 VND [CLM-EXCEL-product_vps_epyc_5-price_24m]
- Cloud VPS AMD EPYC 5: price_3m = 2130000 VND [CLM-EXCEL-product_vps_epyc_5-price_3m]
- Cloud VPS AMD EPYC 5: price_6m = 23430000 VND [CLM-EXCEL-product_vps_epyc_5-price_6m]
- Cloud VPS AMD EPYC 5: ram = 6 GB  [CLM-EXCEL-product_vps_epyc_5-ram]
- Cloud VPS AMD EPYC 5: storage = 60GB  [CLM-EXCEL-product_vps_epyc_5-storage]
- Cloud VPS AMD EPYC 6: cpu_cores = 5 Cores  [CLM-EXCEL-product_vps_epyc_6-cpu_cores]
- Cloud VPS AMD EPYC 6: monthly_price = 870000 VND [CLM-EXCEL-product_vps_epyc_6-monthly_price]
- Cloud VPS AMD EPYC 6: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_epyc_6-network_speed]
- Cloud VPS AMD EPYC 6: price_12m = 8874000 VND [CLM-EXCEL-product_vps_epyc_6-price_12m]
- Cloud VPS AMD EPYC 6: price_24m = 15660000 VND [CLM-EXCEL-product_vps_epyc_6-price_24m]
- Cloud VPS AMD EPYC 6: price_3m = 2610000 VND [CLM-EXCEL-product_vps_epyc_6-price_3m]
- Cloud VPS AMD EPYC 6: price_6m = 28710000 VND [CLM-EXCEL-product_vps_epyc_6-price_6m]
- Cloud VPS AMD EPYC 6: ram = 8 GB  [CLM-EXCEL-product_vps_epyc_6-ram]
- Cloud VPS AMD EPYC 6: storage = 70GB  [CLM-EXCEL-product_vps_epyc_6-storage]
- Cloud VPS AMD EPYC 7: cpu_cores = 7 Cores  [CLM-EXCEL-product_vps_epyc_7-cpu_cores]
- Cloud VPS AMD EPYC 7: monthly_price = 1200000 VND [CLM-EXCEL-product_vps_epyc_7-monthly_price]
- Cloud VPS AMD EPYC 7: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_epyc_7-network_speed]
- Cloud VPS AMD EPYC 7: price_12m = 12240000 VND [CLM-EXCEL-product_vps_epyc_7-price_12m]
- Cloud VPS AMD EPYC 7: price_24m = 21600000 VND [CLM-EXCEL-product_vps_epyc_7-price_24m]
- Cloud VPS AMD EPYC 7: price_3m = 3600000 VND [CLM-EXCEL-product_vps_epyc_7-price_3m]
- Cloud VPS AMD EPYC 7: price_6m = 39600000 VND [CLM-EXCEL-product_vps_epyc_7-price_6m]
- Cloud VPS AMD EPYC 7: ram = 12 GB  [CLM-EXCEL-product_vps_epyc_7-ram]
- Cloud VPS AMD EPYC 7: storage = 80GB  [CLM-EXCEL-product_vps_epyc_7-storage]
- Cloud VPS AMD EPYC 8: cpu_cores = 8 Cores  [CLM-EXCEL-product_vps_epyc_8-cpu_cores]
- Cloud VPS AMD EPYC 8: monthly_price = 1800000 VND [CLM-EXCEL-product_vps_epyc_8-monthly_price]
- Cloud VPS AMD EPYC 8: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_epyc_8-network_speed]
- Cloud VPS AMD EPYC 8: price_12m = 18360000 VND [CLM-EXCEL-product_vps_epyc_8-price_12m]
- Cloud VPS AMD EPYC 8: price_24m = 32400000 VND [CLM-EXCEL-product_vps_epyc_8-price_24m]
- Cloud VPS AMD EPYC 8: price_3m = 5400000 VND [CLM-EXCEL-product_vps_epyc_8-price_3m]
- Cloud VPS AMD EPYC 8: price_6m = 59400000 VND [CLM-EXCEL-product_vps_epyc_8-price_6m]
- Cloud VPS AMD EPYC 8: ram = 16 GB  [CLM-EXCEL-product_vps_epyc_8-ram]
- Cloud VPS AMD EPYC 8: storage = 100GB  [CLM-EXCEL-product_vps_epyc_8-storage]
- VPS MMO (Bảng mới) MMO1: cpu_cores = 1 Core  [CLM-EXCEL-product_vps_mmo1-cpu_cores]
- VPS MMO (Bảng mới) MMO1: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo1-ipv4]
- VPS MMO (Bảng mới) MMO1: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo1-ipv6]
- VPS MMO/Giá rẻ MMO1: monthly_price = 90000 VND [CLM-EXCEL-product_vps_mmo1-monthly_price]
- VPS MMO (Bảng mới) MMO1: price_12m = 660000 VND [CLM-EXCEL-product_vps_mmo1-price_12m]
- VPS MMO (Bảng mới) MMO1: price_3m = 210000 VND [CLM-EXCEL-product_vps_mmo1-price_3m]
- VPS MMO (Bảng mới) MMO1: price_6m = 360000 VND [CLM-EXCEL-product_vps_mmo1-price_6m]
- VPS MMO (Bảng mới) MMO1: ram = 1 GB  [CLM-EXCEL-product_vps_mmo1-ram]
- VPS MMO (Bảng mới) MMO1: storage = 20GB  [CLM-EXCEL-product_vps_mmo1-storage]
- VPS MMO (Bảng mới) MMO2: cpu_cores = 1 Cores  [CLM-EXCEL-product_vps_mmo2-cpu_cores]
- VPS MMO (Bảng mới) MMO2: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo2-ipv4]
- VPS MMO (Bảng mới) MMO2: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo2-ipv6]
- VPS MMO/Giá rẻ MMO2: monthly_price = 120000 VND [CLM-EXCEL-product_vps_mmo2-monthly_price]
- VPS MMO (Bảng mới) MMO2: price_12m = 900000 VND [CLM-EXCEL-product_vps_mmo2-price_12m]
- VPS MMO (Bảng mới) MMO2: price_3m = 285000 VND [CLM-EXCEL-product_vps_mmo2-price_3m]
- VPS MMO (Bảng mới) MMO2: price_6m = 510000 VND [CLM-EXCEL-product_vps_mmo2-price_6m]
- VPS MMO (Bảng mới) MMO2: ram = 2 GB  [CLM-EXCEL-product_vps_mmo2-ram]
- VPS MMO (Bảng mới) MMO2: storage = 25GB  [CLM-EXCEL-product_vps_mmo2-storage]
- VPS MMO (Bảng mới) MMO3: cpu_cores = 2 Cores  [CLM-EXCEL-product_vps_mmo3-cpu_cores]
- VPS MMO (Bảng mới) MMO3: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo3-ipv4]
- VPS MMO (Bảng mới) MMO3: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo3-ipv6]
- VPS MMO (Bảng mới) MMO3: monthly_price = 110000 VND [CLM-EXCEL-product_vps_mmo3-monthly_price]
- VPS MMO (Bảng mới) MMO3: price_12m = 960000 VND [CLM-EXCEL-product_vps_mmo3-price_12m]
- VPS MMO (Bảng mới) MMO3: price_3m = 300000 VND [CLM-EXCEL-product_vps_mmo3-price_3m]
- VPS MMO (Bảng mới) MMO3: price_6m = 540000 VND [CLM-EXCEL-product_vps_mmo3-price_6m]
- VPS MMO (Bảng mới) MMO3: ram = 2 GB  [CLM-EXCEL-product_vps_mmo3-ram]
- VPS MMO (Bảng mới) MMO3: storage = 30GB  [CLM-EXCEL-product_vps_mmo3-storage]
- VPS MMO (Bảng mới) MMO4: cpu_cores = 2 Cores  [CLM-EXCEL-product_vps_mmo4-cpu_cores]
- VPS MMO (Bảng mới) MMO4: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo4-ipv4]
- VPS MMO (Bảng mới) MMO4: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo4-ipv6]
- VPS MMO (Bảng mới) MMO4: monthly_price = 150000 VND [CLM-EXCEL-product_vps_mmo4-monthly_price]
- VPS MMO (Bảng mới) MMO4: price_12m = 1320000 VND [CLM-EXCEL-product_vps_mmo4-price_12m]
- VPS MMO (Bảng mới) MMO4: price_3m = 420000 VND [CLM-EXCEL-product_vps_mmo4-price_3m]
- VPS MMO (Bảng mới) MMO4: price_6m = 750000 VND [CLM-EXCEL-product_vps_mmo4-price_6m]
- VPS MMO (Bảng mới) MMO4: ram = 4 GB  [CLM-EXCEL-product_vps_mmo4-ram]
- VPS MMO (Bảng mới) MMO4: storage = 40GB  [CLM-EXCEL-product_vps_mmo4-storage]
- VPS MMO (Bảng mới) MMO5: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_mmo5-cpu_cores]
- VPS MMO (Bảng mới) MMO5: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo5-ipv4]
- VPS MMO (Bảng mới) MMO5: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo5-ipv6]
- VPS MMO (Bảng mới) MMO5: monthly_price = 190000 VND [CLM-EXCEL-product_vps_mmo5-monthly_price]
- VPS MMO (Bảng mới) MMO5: price_12m = 1800000 VND [CLM-EXCEL-product_vps_mmo5-price_12m]
- VPS MMO (Bảng mới) MMO5: price_3m = 525000 VND [CLM-EXCEL-product_vps_mmo5-price_3m]
- VPS MMO (Bảng mới) MMO5: price_6m = 960000 VND [CLM-EXCEL-product_vps_mmo5-price_6m]
- VPS MMO (Bảng mới) MMO5: ram = 4 GB  [CLM-EXCEL-product_vps_mmo5-ram]
- VPS MMO (Bảng mới) MMO5: storage = 50GB  [CLM-EXCEL-product_vps_mmo5-storage]
- VPS MMO (Bảng mới) MMO6: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_mmo6-cpu_cores]
- VPS MMO (Bảng mới) MMO6: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo6-ipv4]
- VPS MMO (Bảng mới) MMO6: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo6-ipv6]
- VPS MMO (Bảng mới) MMO6: monthly_price = 250000 VND [CLM-EXCEL-product_vps_mmo6-monthly_price]
- VPS MMO (Bảng mới) MMO6: price_12m = 2520000 VND [CLM-EXCEL-product_vps_mmo6-price_12m]
- VPS MMO (Bảng mới) MMO6: price_3m = 705000 VND [CLM-EXCEL-product_vps_mmo6-price_3m]
- VPS MMO (Bảng mới) MMO6: price_6m = 1320000 VND [CLM-EXCEL-product_vps_mmo6-price_6m]
- VPS MMO (Bảng mới) MMO6: ram = 8 GB  [CLM-EXCEL-product_vps_mmo6-ram]
- VPS MMO (Bảng mới) MMO6: storage = 60GB  [CLM-EXCEL-product_vps_mmo6-storage]
- VPS MMO (Bảng mới) MMO7: cpu_cores = 8 Cores  [CLM-EXCEL-product_vps_mmo7-cpu_cores]
- VPS MMO (Bảng mới) MMO7: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo7-ipv4]
- VPS MMO (Bảng mới) MMO7: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo7-ipv6]
- VPS MMO (Bảng mới) MMO7: monthly_price = 450000 VND [CLM-EXCEL-product_vps_mmo7-monthly_price]
- VPS MMO (Bảng mới) MMO7: price_12m = 4800000 VND [CLM-EXCEL-product_vps_mmo7-price_12m]
- VPS MMO (Bảng mới) MMO7: price_3m = 1290000 VND [CLM-EXCEL-product_vps_mmo7-price_3m]
- VPS MMO (Bảng mới) MMO7: price_6m = 2460000 VND [CLM-EXCEL-product_vps_mmo7-price_6m]
- VPS MMO (Bảng mới) MMO7: ram = 8 GB  [CLM-EXCEL-product_vps_mmo7-ram]
- VPS MMO (Bảng mới) MMO7: storage = 80GB  [CLM-EXCEL-product_vps_mmo7-storage]
- VPS MMO (Bảng mới) MMO8: cpu_cores = 8 Cores  [CLM-EXCEL-product_vps_mmo8-cpu_cores]
- VPS MMO (Bảng mới) MMO8: ipv4 = 1 IPv4 VN  [CLM-EXCEL-product_vps_mmo8-ipv4]
- VPS MMO (Bảng mới) MMO8: ipv6 = IPv6/56  [CLM-EXCEL-product_vps_mmo8-ipv6]
- VPS MMO (Bảng mới) MMO8: monthly_price = 550000 VND [CLM-EXCEL-product_vps_mmo8-monthly_price]
- VPS MMO (Bảng mới) MMO8: price_12m = 6000000 VND [CLM-EXCEL-product_vps_mmo8-price_12m]
- VPS MMO (Bảng mới) MMO8: price_3m = 1590000 VND [CLM-EXCEL-product_vps_mmo8-price_3m]
- VPS MMO (Bảng mới) MMO8: price_6m = 3060000 VND [CLM-EXCEL-product_vps_mmo8-price_6m]
- VPS MMO (Bảng mới) MMO8: ram = 16 GB  [CLM-EXCEL-product_vps_mmo8-ram]
- VPS MMO (Bảng mới) MMO8: storage = 100GB  [CLM-EXCEL-product_vps_mmo8-storage]
- Cloud VPS VM VM01: cpu_cores = 1 Core  [CLM-EXCEL-product_vps_vm01-cpu_cores]
- Cloud VPS VM VM01: monthly_price = 140000 VND [CLM-EXCEL-product_vps_vm01-monthly_price]
- Cloud VPS VM VM01: network_speed = 100 Mbps  [CLM-EXCEL-product_vps_vm01-network_speed]
- Cloud VPS VM VM01: price_12m = 1428000 VND [CLM-EXCEL-product_vps_vm01-price_12m]
- Cloud VPS VM VM01: price_24m = 2520000 VND [CLM-EXCEL-product_vps_vm01-price_24m]
- Cloud VPS VM VM01: price_3m = 420000 VND [CLM-EXCEL-product_vps_vm01-price_3m]
- Cloud VPS VM VM01: price_6m = 4620000 VND [CLM-EXCEL-product_vps_vm01-price_6m]
- Cloud VPS VM VM01: ram = 1 GB  [CLM-EXCEL-product_vps_vm01-ram]
- Cloud VPS VM VM01: storage = 20GB  [CLM-EXCEL-product_vps_vm01-storage]
- Cloud VPS VM VM02: cpu_cores = 2 Cores  [CLM-EXCEL-product_vps_vm02-cpu_cores]
- Cloud VPS VM VM02: monthly_price = 180000 VND [CLM-EXCEL-product_vps_vm02-monthly_price]
- Cloud VPS VM VM02: network_speed = 100 Mbps  [CLM-EXCEL-product_vps_vm02-network_speed]
- Cloud VPS VM VM02: price_12m = 1836000 VND [CLM-EXCEL-product_vps_vm02-price_12m]
- Cloud VPS VM VM02: price_24m = 3240000 VND [CLM-EXCEL-product_vps_vm02-price_24m]
- Cloud VPS VM VM02: price_3m = 540000 VND [CLM-EXCEL-product_vps_vm02-price_3m]
- Cloud VPS VM VM02: price_6m = 5940000 VND [CLM-EXCEL-product_vps_vm02-price_6m]
- Cloud VPS VM VM02: ram = 2 GB  [CLM-EXCEL-product_vps_vm02-ram]
- Cloud VPS VM VM02: storage = 30GB  [CLM-EXCEL-product_vps_vm02-storage]
- Cloud VPS VM VM03: cpu_cores = 3 Cores  [CLM-EXCEL-product_vps_vm03-cpu_cores]
- Cloud VPS VM VM03: monthly_price = 220000 VND [CLM-EXCEL-product_vps_vm03-monthly_price]
- Cloud VPS VM VM03: network_speed = 150 Mbps  [CLM-EXCEL-product_vps_vm03-network_speed]
- Cloud VPS VM VM03: price_12m = 2244000 VND [CLM-EXCEL-product_vps_vm03-price_12m]
- Cloud VPS VM VM03: price_24m = 3960000 VND [CLM-EXCEL-product_vps_vm03-price_24m]
- Cloud VPS VM VM03: price_3m = 660000 VND [CLM-EXCEL-product_vps_vm03-price_3m]
- Cloud VPS VM VM03: price_6m = 7260000 VND [CLM-EXCEL-product_vps_vm03-price_6m]
- Cloud VPS VM VM03: ram = 3 GB  [CLM-EXCEL-product_vps_vm03-ram]
- Cloud VPS VM VM03: storage = 40GB  [CLM-EXCEL-product_vps_vm03-storage]
- Cloud VPS VM VM04: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_vm04-cpu_cores]
- Cloud VPS VM VM04: monthly_price = 340000 VND [CLM-EXCEL-product_vps_vm04-monthly_price]
- Cloud VPS VM VM04: network_speed = 150 Mbps  [CLM-EXCEL-product_vps_vm04-network_speed]
- Cloud VPS VM VM04: price_12m = 3468000 VND [CLM-EXCEL-product_vps_vm04-price_12m]
- Cloud VPS VM VM04: price_24m = 6120000 VND [CLM-EXCEL-product_vps_vm04-price_24m]
- Cloud VPS VM VM04: price_3m = 1020000 VND [CLM-EXCEL-product_vps_vm04-price_3m]
- Cloud VPS VM VM04: price_6m = 11220000 VND [CLM-EXCEL-product_vps_vm04-price_6m]
- Cloud VPS VM VM04: ram = 4 GB  [CLM-EXCEL-product_vps_vm04-ram]
- Cloud VPS VM VM04: storage = 50GB  [CLM-EXCEL-product_vps_vm04-storage]
- Cloud VPS VM VM05: cpu_cores = 4 Cores  [CLM-EXCEL-product_vps_vm05-cpu_cores]
- Cloud VPS VM VM05: monthly_price = 500000 VND [CLM-EXCEL-product_vps_vm05-monthly_price]
- Cloud VPS VM VM05: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_vm05-network_speed]
- Cloud VPS VM VM05: price_12m = 5100000 VND [CLM-EXCEL-product_vps_vm05-price_12m]
- Cloud VPS VM VM05: price_24m = 9000000 VND [CLM-EXCEL-product_vps_vm05-price_24m]
- Cloud VPS VM VM05: price_3m = 1500000 VND [CLM-EXCEL-product_vps_vm05-price_3m]
- Cloud VPS VM VM05: price_6m = 16500000 VND [CLM-EXCEL-product_vps_vm05-price_6m]
- Cloud VPS VM VM05: ram = 6 GB  [CLM-EXCEL-product_vps_vm05-ram]
- Cloud VPS VM VM05: storage = 60GB  [CLM-EXCEL-product_vps_vm05-storage]
- Cloud VPS VM VM06: cpu_cores = 5 Cores  [CLM-EXCEL-product_vps_vm06-cpu_cores]
- Cloud VPS VM VM06: monthly_price = 610000 VND [CLM-EXCEL-product_vps_vm06-monthly_price]
- Cloud VPS VM VM06: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_vm06-network_speed]
- Cloud VPS VM VM06: price_12m = 6222000 VND [CLM-EXCEL-product_vps_vm06-price_12m]
- Cloud VPS VM VM06: price_24m = 10980000 VND [CLM-EXCEL-product_vps_vm06-price_24m]
- Cloud VPS VM VM06: price_3m = 1830000 VND [CLM-EXCEL-product_vps_vm06-price_3m]
- Cloud VPS VM VM06: price_6m = 20130000 VND [CLM-EXCEL-product_vps_vm06-price_6m]
- Cloud VPS VM VM06: ram = 8 GB  [CLM-EXCEL-product_vps_vm06-ram]
- Cloud VPS VM VM06: storage = 70GB  [CLM-EXCEL-product_vps_vm06-storage]
- Cloud VPS VM VM07: cpu_cores = 7 Cores  [CLM-EXCEL-product_vps_vm07-cpu_cores]
- Cloud VPS VM VM07: monthly_price = 840000 VND [CLM-EXCEL-product_vps_vm07-monthly_price]
- Cloud VPS VM VM07: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_vm07-network_speed]
- Cloud VPS VM VM07: price_12m = 8568000 VND [CLM-EXCEL-product_vps_vm07-price_12m]
- Cloud VPS VM VM07: price_24m = 15120000 VND [CLM-EXCEL-product_vps_vm07-price_24m]
- Cloud VPS VM VM07: price_3m = 2520000 VND [CLM-EXCEL-product_vps_vm07-price_3m]
- Cloud VPS VM VM07: price_6m = 27720000 VND [CLM-EXCEL-product_vps_vm07-price_6m]
- Cloud VPS VM VM07: ram = 12 GB  [CLM-EXCEL-product_vps_vm07-ram]
- Cloud VPS VM VM07: storage = 80GB  [CLM-EXCEL-product_vps_vm07-storage]
- Cloud VPS VM VM08: cpu_cores = 8 Cores  [CLM-EXCEL-product_vps_vm08-cpu_cores]
- Cloud VPS VM VM08: monthly_price = 1260000 VND [CLM-EXCEL-product_vps_vm08-monthly_price]
- Cloud VPS VM VM08: network_speed = 200 Mbps  [CLM-EXCEL-product_vps_vm08-network_speed]
- Cloud VPS VM VM08: price_12m = 12852000 VND [CLM-EXCEL-product_vps_vm08-price_12m]
- Cloud VPS VM VM08: price_24m = 22680000 VND [CLM-EXCEL-product_vps_vm08-price_24m]
- Cloud VPS VM VM08: price_3m = 3780000 VND [CLM-EXCEL-product_vps_vm08-price_3m]
- Cloud VPS VM VM08: price_6m = 41580000 VND [CLM-EXCEL-product_vps_vm08-price_6m]
- Cloud VPS VM VM08: ram = 16 GB  [CLM-EXCEL-product_vps_vm08-ram]
- Cloud VPS VM VM08: storage = 100GB  [CLM-EXCEL-product_vps_vm08-storage]

## LLM-EXTRACTED CLAIMS (Check these)

- BK MISA: backup_frequency = daily None (confidence: high)
- BK MISA: benefit = Tiết kiệm chi phí đầu tư phần cứng None (confidence: high)
- BK MISA: category = server None (confidence: high)
- BK MISA: data_center_location = Việt Nam None (confidence: high)
- BK MISA: description = Dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên biệt để lưu trữ và vận hành phần mềm kế toán MISA SME trên nền tảng điện toán đám mây. None (confidence: high)
- BK MISA: feature = Khả năng khôi phục dữ liệu ngay cả khi bị xóa None (confidence: high)
- BK MISA: hardware_cpu_type = SSD & NVME None (confidence: high)
- BK MISA: io_speed = 10000 IOPS (confidence: high)
- BK MISA: promotion = Tặng thêm dung lượng lưu trữ HDD None (confidence: high)
- BK MISA: scalability = Có thể mở rộng theo khối lượng công việc và nhu cầu sử dụng None (confidence: high)
- BK MISA: source_url = https://www.bkns.vn/server/cloud-vps-bk-misa.html None (confidence: high)
- BK MISA: target_audience = Các doanh nghiệp đang sử dụng MISA SME, đặc biệt là các doanh nghiệp có nhiều chi nhánh cần làm việc chung trên cùng một cơ sở dữ liệu kế toán. None (confidence: high)
- BK MISA: uptime_commitment = 99.99 % (confidence: high)
- BK MISA: user_limit = unlimited None (confidence: high)
- VPS N8N – AI: activation_process = Dịch vụ được khởi tạo nhanh chóng sau khi đăng ký. None (confidence: high)
- VPS N8N – AI: backup_policy = Dữ liệu được sao lưu hàng tuần. None (confidence: high)
- VPS N8N – AI: category = server None (confidence: high)
- VPS N8N – AI: data_transfer = Không giới hạn (Unlimited) None (confidence: high)
- VPS N8N – AI: description = VPS N8N tại BKNS là một giải pháp máy chủ ảo được tối ưu hóa cho việc triển khai N8N, một công cụ tự động hóa quy trình. Dịch vụ này cung cấp một môi trường máy chủ độc lập, hiệu năng cao và ổn định, cho phép người dùng xây dựng, quản lý và thực thi các luồng công việc tự động kết nối nhiều ứng dụng khác nhau. None (confidence: high)
- VPS N8N – AI: feature = Cung cấp bảng điều khiển VPS để quản lý. None (confidence: high)
- VPS N8N – AI: ipv6_support = True None (confidence: high)
- VPS N8N – AI: name = VPS N8N – AI None (confidence: high)
- VPS N8N – AI: target_audience = Người dùng cần triển khai các quy trình tự động hóa (workflow automation) một cách nhanh chóng, an toàn và ổn định trên một môi trường riêng biệt. None (confidence: high)
- VPS N8N – AI: url = https://www.bkns.vn/server/vps-n8n.html None (confidence: high)
- VPS N8N – AI: vat_policy = Giá trên chưa bao gồm VAT. None (confidence: high)
- VPS N8N – AI: virtualization_technology = KVM None (confidence: high)
- SEO 01: backup_frequency = weekly None (confidence: high)
- SEO 01: bandwidth = unlimited None (confidence: high)
- SEO 01: control_panel_support = DirectAdmin None (confidence: high)
- SEO 01: free_ssl_included = False None (confidence: high)
- SEO 01: ipv6_support = True None (confidence: high)
- SEO 01: minimum_billing_cycle = 3 month (confidence: high)
- SEO 01: parent_product = ENT-PROD-VPS.seo None (confidence: high)
- SEO 01: monthly_price = 425000 VND (confidence: high)
- SEO 01: ram = 3 GB (confidence: high)
- SEO 01: registration_link = https://my.bkns.net/?cmd=cart&action=add&id=450 None (confidence: high)
- SEO 01: storage = 50 GB (confidence: high)
- SEO 01: vcpu = 3 core (confidence: high)
- SEO 02: parent_product = ENT-PROD-VPS.seo None (confidence: high)
- VPS SEO: activation_type = automatic None (confidence: high)
- VPS SEO: auto_activation = True  (confidence: high)
- VPS SEO: backup_frequency = weekly  (confidence: high)
- VPS SEO: bandwidth = unlimited  (confidence: high)
- VPS SEO: control_panel_support = False  (confidence: high)
- VPS SEO: description = Một dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên dụng cho các website cần tối ưu hóa cho công cụ tìm kiếm (SEO). None (confidence: high)
- VPS SEO: faq_section_availability = False  (confidence: high)
- VPS SEO: free_ssl_support = False  (confidence: high)
- VPS SEO: ipv6_support = True  (confidence: high)
- VPS SEO: minimum_billing_cycle = 3 month (confidence: high)
- VPS SEO: root_access = True  (confidence: high)
- VPS SEO: service_description = Một dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên dụng cho các website cần tối ưu hóa cho công cụ tìm kiếm (SEO).  (confidence: high)
- VPS SEO: target_audience = Các cá nhân, doanh nghiệp vận hành website muốn cải thiện thứ hạng SEO.  (confidence: high)
- VPS SEO: target_customer = Các cá nhân, doanh nghiệp vận hành website muốn cải thiện thứ hạng SEO. None (confidence: high)
- VPS SEO: user_privilege = full_administrative_rights None (confidence: high)
- VPS SEO: vps_control_panel = True  (confidence: high)
- Storage VPS: marketing_claim = giá rẻ None (confidence: high)
- Storage VPS: product_description = giải pháp máy chủ ảo lưu trữ dung lượng cao None (confidence: high)
- Storage VPS: use_case = File server None (confidence: high)
- VPS: access.admin = Có quyền Root/Administor có thể cài đặt tuỳ biến theo nhu cầu  (confidence: high)
- VPS: access.root = True  (confidence: high)
- VPS N8N – AI: activation_process = Dịch vụ VPS N8N được kích hoạt tự động sau khi khách hàng hoàn tất đăng ký và thanh toán. None (confidence: high)
- VPS Siêu Tiết Kiệm: addon_price = 30000 VND (confidence: high)
- Storage VPS: admin_access = Full root/admin None (confidence: high)
- VPS Siêu Rẻ: auto_activation = True None (confidence: high)
- Cloud VPS: backup.frequency = 1 lần / tuần  (confidence: high)
- VPS Siêu Rẻ: backup_frequency = weekly None (confidence: high)
- Storage VPS: bandwidth_limit = Unlimited None (confidence: high)
- VPS Giá Rẻ: bandwidth = Không giới hạn None (confidence: high)
- VPS Giá Rẻ: category = server None (confidence: high)
- VPS Siêu Rẻ: control_panel_availability = True None (confidence: high)
- Cloud VPS AMD: cpu_clock_speed = 2.6GHz – 3.9GHz None (confidence: high)
- AMD 5: cpu_cores = 4 core (confidence: high)
- Cloud VPS AMD: cpu_type = AMD EPYC™ Gen 2 None (confidence: high)
- VPS Giá Rẻ: data_gap = Loại ổ cứng sử dụng (ví dụ: SSD, NVMe, HDD) không được nêu rõ None (confidence: high)
- VPS: definition = Máy chủ riêng ảo (Virtual Private Server), là một máy chủ ảo được tạo ra bằng công nghệ ảo hóa từ một máy chủ vật lý. None (confidence: high)
- VPS Giá Rẻ: description = Dịch vụ cho thuê máy chủ ảo (VPS) với chi phí thấp, cung cấp tài nguyên độc lập và quyền quản trị toàn phần cho người dùng. None (confidence: high)
- Cloud VPS VM Discount: discount_percentage = 45 % (confidence: high)
- AMD 5: download_speed = 500 Mbps (confidence: high)
- VPS Giá Rẻ: feature.auto_activation = Môi trường hoạt động riêng biệt giúp tăng cường bảo mật so với shared hosting. None (confidence: high)
- VPS Giá Rẻ: feature = cấu hình ổn định None (confidence: high)
- Cloud VPS: hardware.storage_capacity = SSD Enterprise  (confidence: high)
- VPS Giá Rẻ: has_auto_activation = True None (confidence: high)
- VPS Giá Rẻ: has_control_panel = True None (confidence: high)
- VPS Giá Rẻ: has_directadmin = False None (confidence: high)
- VPS Giá Rẻ: has_free_ssl = False None (confidence: high)
- VPS Giá Rẻ: has_root_access = True None (confidence: high)
- VPS Giá Rẻ: has_weekly_backup = False None (confidence: high)
- Cloud VPS: infrastructure = Tier III None (confidence: high)
- VPS Siêu Rẻ: ipv6_support = True None (confidence: high)
- VPS Giá Rẻ: is_upgradeable = True None (confidence: high)
- VPS/Cloud Server: management_option = tự quản lý hoặc quản trị thuê ngoài None (confidence: high)
- VPS Siêu Rẻ: minimum_billing_cycle = 1 month (confidence: high)
- Cloud VPS: monitoring.system = BKNS Cloud Monitoring  (confidence: high)
- Cloud VPS: network.connection = Dual Uplink – Multihome Network  (confidence: high)
- Cloud VPS AMD: network_port_speed = 10 Gbps (confidence: high)
- VPS Giá Rẻ: policy.backup.weekly = False None (confidence: high)
- VPS Giá Rẻ: policy.upgrade = True None (confidence: high)
- Dịch vụ Backup: monthly_price = 100000 VND (confidence: high)
- Cloud VPS AMD: price_starts_at = 165000 VND (confidence: high)
- Cloud VPS SSD: price_vat_exclusion = True None (confidence: high)

## WIKI PAGES TO VERIFY

### bang-gia.md

---
page_id: wiki.products.vps.bang-gia
title: Cloud VPS BKNS — Bảng Giá
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 171
compile_cost_usd: 0.054
self_review: error
corrections: 0
approved_at: '2026-04-07T16:24:08.823984+07:00'
---

# Cloud VPS BKNS — Bảng Giá

Trang này tổng hợp bảng giá chi tiết cho các dịch vụ Cloud VPS do BKNS cung cấp, được biên soạn dựa trên các nguồn dữ liệu đã được xác thực.

**Lưu ý quan trọng:**
*   Tất cả các mức giá được niêm yết trong tài liệu này là giá **chưa bao gồm thuế VAT**.
*   Giá có thể thay đổi, vui lòng tham khảo thông tin mới nhất từ bộ phận kinh doanh.

---

### 1. Cloud VPS AMD EPYC

Dòng VPS hiệu năng cao sử dụng CPU AMD EPYC, phù hợp cho các ứng dụng đòi hỏi sức mạnh xử lý.

| Tên Gói | Giá 1 tháng (VND) | Giá 3 tháng (VND) | Giá 12 tháng (VND) | Giá 24 tháng (VND) | Giá 60 tháng (VND) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EPYC 1** | 165.000 | 495.000 | 1.683.000 | 2.970.000 | 5.445.000 |
| **EPYC 2** | 210.000 | 630.000 | 2.142.000 | 3.780.000 | 6.930.000 |
| **EPYC 3** | 320.000 | 960.000 | 3.264.000 | 5.760.000 | 10.560.000 |
| **EPYC 4** | 480.000 | 1.440.000 | 4.896.000 | 8.640.000 | 15.840.000 |
| **EPYC 5** | 710.000 | 2.130.000 | 7.242.000 | 12.780.000 | 23.430.000 |
| **EPYC 6** | 870.000 | 2.610.000 | 8.874.000 | 15.660.000 | 28.710.000 |
| **EPYC 7** | 1.200.000 | 3.600.000 | 12.240.000 | 21.600.000 | 39.600.000 |
| **EPYC 8** | 1.800.000 | 5.400.000 | 18.360.000 | 32.400.000 | 59.400.000 |

*Ghi chú: Giá khởi điểm từ 165.000đ/tháng.*

### 2. Cloud VPS VM

Dòng VPS phổ thông, cân bằng giữa chi phí và hiệu năng, có chính sách giảm giá hấp dẫn khi thanh toán dài hạn.

| Tên Gói | Giá 1 tháng (VND) | Giá 3 tháng (VND) | Giá 12 tháng (VND) | Giá 24 tháng (VND) | Giá 60 tháng (VND) | Ghi chú |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VM01** | 140.000 | 420.000 | 1.428.000 | 2.520.000 | 4.620.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM02** | 180.000 | 540.000 | 1.836.000 | 3.240.000 | 5.940.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM03** | 220.000 | 660.000 | 2.244.000 | 3.960.000 | 7.260.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM04** | 340.000 | 1.020.000 | 3.468.000 | 6.120.000 | 11.220.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM05** | 500.000 | 1.500.000 | 5.100.000 | 9.000.000 | 16.500.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM06** | 610.000 | 1.830.000 | 6.222.000 | 10.980.000 | 20.130.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM07** | 840.000 | 2.520.000 | 8.568.000 | 15.120.000 | 27.720.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |
| **VM08** | 1.260.000 | 3.780.000 | 12.852.000 | 22.680.000 | 41.580.000 | Giảm 15% (12T), 25% (24T), 45% (60T) |

### 3. VPS MMO / Giá Rẻ

Dòng VPS tối ưu chi phí, phù hợp cho các tác vụ MMO, nuôi tài khoản, hoặc các dự án không yêu cầu cấu hình cao. Giá khởi điểm từ 90.000đ/tháng.

| Tên Gói | Giá 1 tháng (VND) | Giá 3 tháng (VND) | Giá 6 tháng (VND) | Giá 12 tháng (VND) |
| :--- | :--- | :--- | :--- | :--- |
| **MMO1** | 90.000 | 210.000 | 360.000 | 660.000 |
| **MMO2** | 120.000 | 285.000 | 510.000 | 900.000 |
| **MMO3** | 110.000 | 300.000 | 540.000 | 960.000 |
| **MMO4** | 150.000 | 420.000 | 750.000 | 1.320.000 |
| **MMO5** | 190.000 | 525.000 | 960.000 | 1.800.000 |
| **MMO6** | 250.000 | 705.000 | 1.320.000 | 2.520.000 |
| **MMO7** | 450.000 | 1.290.000 | 2.460.000 | 4.800.000 |
| **MMO8** | 550.000 | 1.590.000 | 3.060.000 | 6.000.000 |

### 4. VPS Siêu Rẻ / Siêu Tiết Kiệm (VPSTK)

Dòng VPS có mức giá cạnh tranh nhất, chu kỳ thanh toán tối thiểu 1 tháng.

| Tên Gói | Giá/tháng (VND) | Thanh toán tối thiểu |
| :--- | :--- | :--- |
| **VPSTK1** | 69.000 | 1 tháng |
| **VPSTK2** | 99.000 | 1 tháng |
| **VPSTK3** | 129.000 | 1 tháng |
| **VPSTK4** | 159.000 | 1 tháng |
| **VPSTK5** | 189.000 | 1 tháng |
| **VPSTK6** | 239.000 | 1 tháng |
| **VPSTK7** | 299.000 | 1 tháng |

*Ghi chú: Có thể nâng cấp RAM với chi phí 30.000đ/tháng (chưa bao gồm VAT, dung lượng RAM thêm đang cập nhật).*

### 5. Các Dòng VPS Chuyên Dụng

| Dòng sản phẩm | Tên Gói | Giá/tháng (VND) | Thanh toán tối thiểu | Ghi chú |
| :--- | :--- | :--- | :--- | :--- |
| **VPS SEO** | SEO 01 | 425.000 | 3 tháng | |
| | SEO 02 | 700.000 | Đang cập nhật | |
| **VPS N8N AI** | N8N-AI01 | 140.000 | 3 tháng | Giá khởi điểm từ 140.000đ/tháng |
| | N8N-AI02 | 180.000 | Đang cập nhật | |
| **Storage VPS** | STORAGE VPS 2 | 360.000 | Đang cập nhật | Có thể nâng cấp gói khi có nhu cầu |
| **VPS MISA** | BKMS - 04 | 1.020.000 | Đang cập nhật | |
| **Cloud VPS SSD** | CLOUD-VM01 | 42.000 | 3 tháng | |
| | CLOUD-VM02 | 54.000 | 1 tháng | |
| | CLOUD-VM03 | 66.000 | Đang cập nhật | |

### 6. Dịch vụ & Addon

*   **Dịch vụ Backup:**
    *   **Backup hàng ngày:** 100.000 VND/tháng.
    *   **Backup hàng giờ:** Đang cập nhật.

---

### Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### cau-hoi-thuong-gap.md

---
page_id: wiki.products.vps.cau-hoi-thuong-gap
title: Cloud VPS BKNS — Câu Hỏi Thường Gặp
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 1
compile_cost_usd: 0.0021
self_review: skipped
corrections: 0
approved_at: '2026-04-07T16:24:08.827091+07:00'
---

# Cloud VPS BKNS — Câu Hỏi Thường Gặp

Tổng hợp các câu hỏi thường gặp về dịch vụ Cloud VPS tại BKNS.

## Trước khi mua

Đang cập nhật.

## Trong quá trình sử dụng

Đang cập nhật.

## Hỗ trợ & khắc phục sự cố

Đang cập nhật.

## Xem thêm

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### chinh-sach.md

---
page_id: wiki.products.vps.chinh-sach
title: Cloud VPS BKNS — Chính Sách
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 37
compile_cost_usd: 0.0139
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:24:08.829505+07:00'
---

# Cloud VPS BKNS — Chính Sách

Trang này tổng hợp các chính sách quan trọng liên quan đến dịch vụ Cloud VPS tại BKNS, bao gồm cam kết chất lượng dịch vụ (SLA), chính sách hỗ trợ, và các điều khoản khác.

## 1. Cam kết Chất lượng Dịch vụ (SLA)

- **Cam kết Uptime (Uptime Commitment):** BKNS cam kết thời gian hoạt động của dịch vụ là **99.99%**.
  - *Thông tin được xác nhận cho các dịch vụ: BK MISA, Storage VPS.*

## 2. Chính sách Dùng thử và Hoàn tiền

- **Dùng thử miễn phí (Free Trial):** Dịch vụ **BK MISA** cung cấp **7 ngày** dùng thử miễn phí.
- **Chính sách hoàn tiền:** Đang cập nhật.

## 3. Chính sách Hỗ trợ Kỹ thuật

- **Thời gian hỗ trợ:** Đội ngũ kỹ thuật của BKNS hỗ trợ khách hàng liên tục.
  - Hỗ trợ **24/7/365** cho các dịch vụ: **BK MISA, Storage VPS**.
  - Hỗ trợ **24/7** cho dịch vụ: **VPS Giá Rẻ**.
- **Kênh hỗ trợ (Hotline, Email, Ticket):** Đang cập nhật.
- **Thời gian phản hồi yêu cầu:** Đang cập nhật.
- **Hỗ trợ khác:**
  - Khách hàng được hỗ trợ đổi địa chỉ IP miễn phí (áp dụng cho các địa chỉ IP thuộc sở hữu của BKNS).

## 4. Chính sách Sao lưu Dữ liệu (Backup Policy)

Chính sách sao lưu có thể khác nhau tùy thuộc vào từng dòng sản phẩm VPS cụ thể.

| Dịch vụ (Service) | Tần suất Sao lưu (Backup Frequency) | Ghi chú |
| :--- | :--- | :--- |
| **BK MISA** | Hàng ngày (Daily) | Sao lưu được thực hiện tự động. |
| **VPS N8N – AI** | Hàng tuần (Weekly) | |
| **Cloud VPS SEO** (bao gồm SEO 01, SEO 02) | Hàng tuần (Weekly) | |
| **VPS Siêu Rẻ** | Hàng tuần (Weekly) | |
| **Thuê Cloud VPS SSD** | Hàng tuần (Weekly) | |
| **VPS Giá Rẻ** (bao gồm VPS-MM01) | Không hỗ trợ | Các gói dịch vụ không đi kèm sao lưu dữ liệu hàng tuần. |

## 5. Các Chính sách và Điều khoản Khác

- **Nâng cấp (Upgrade):**
  - Hầu hết các dịch vụ đều hỗ trợ nâng cấp tài nguyên khi người dùng có nhu cầu (ví dụ: VPS Giá Rẻ).
  - Đối với dịch vụ **BK MISA**, việc nâng cấp có thể được thực hiện bất kỳ lúc nào mà không làm gián đoạn dịch vụ hay mất mát dữ liệu.

- **Hỗ trợ IPv6 (IPv6 Support):**
  - Hầu hết các dịch vụ Cloud VPS đều hỗ trợ địa chỉ IPv6.
  - *Thông tin được xác nhận cho: VPS N8N – AI, VPS SEO, VPS Siêu Rẻ, Thuê Cloud VPS SSD, VPS-MM01.*

- **Control Panel:**
  - Dịch vụ **VPS SEO** và **SEO 01** không hỗ trợ control panel **DirectAdmin**.

- **Chứng chỉ SSL (SSL Certificate):**
  - Gói dịch vụ **VPS SEO** không đi kèm chứng chỉ SSL miễn phí.

- **Hệ điều hành được hỗ trợ (Supported OS):**
  - Dịch vụ **Storage VPS** tương thích với các hệ điều hành phổ biến như CentOS, Ubuntu, Debian, và Windows.

- **Thuế VAT (VAT Policy):**
  - Giá dịch vụ **VPS N8N – AI** được niêm yết chưa bao gồm thuế VAT.

---

### Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### cloud-vps-amd.md

---
page_id: wiki.products.vps.cloud-vps-amd
title: Cloud VPS AMD EPYC — Hiệu Năng Cao
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 43
compile_cost_usd: 0.0136
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.832338+07:00'
---

# Cloud VPS AMD EPYC — Hiệu Năng Cao

**Cloud VPS AMD** là dòng máy chủ ảo (VPS) cao cấp nhất (Flagship) của BKNS, được thiết kế để mang lại hiệu suất vượt trội với giá thành hợp lý. Dịch vụ này sử dụng sức mạnh từ bộ xử lý CPU AMD EPYC™ thế hệ mới, phù hợp cho mọi doanh nghiệp có nhu cầu về một giải pháp VPS mạnh mẽ và ổn định.

## Ưu Điểm Nổi Bật

*   **Hiệu Suất Vượt Trội**: Tốc độ xử lý PHP nhanh hơn 30% so với các dòng chip thông thường, mang lại sức mạnh xử lý ấn tượng.
*   **Ổ Cứng Tốc Độ Cao**: Sử dụng ổ cứng NVMe Enterprise, đảm bảo tốc độ truy xuất cơ sở dữ liệu cực nhanh, loại bỏ hoàn toàn tình trạng nghẽn cổ chai.
*   **Băng Thông Không Giới Hạn**: Cung cấp băng thông không giới hạn, đáp ứng mọi nhu cầu sử dụng.
*   **Bảo Mật Tối Ưu**: Tích hợp công nghệ bảo mật AMD Infinity Guard.
*   **Khởi Tạo Nhanh Chóng**: Hệ thống tự động khởi tạo dịch vụ chỉ trong vòng 5-10 phút sau khi hoàn tất thanh toán.
*   **Sao Lưu Định Kỳ**: Dữ liệu được tự động sao lưu hàng tuần để đảm bảo an toàn.

## Thông Số Kỹ Thuật Chung

*   **CPU**: AMD EPYC™ Gen 2
*   **Xung nhịp CPU**: 2.6GHz – 3.9GHz
*   **Cổng mạng (Network Port)**: 10Gbps

## Bảng Giá & Cấu Hình Chi Tiết

*Lưu ý: Giá khởi điểm từ 165.000 VND/tháng.*

| Gói | vCPU | RAM | Ổ cứng NVMe | Tốc độ mạng | IP | Giá |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AMD 1** | 1 Core | 1 GB | 20 GB | 100 Mbps | Đang cập nhật | 940.500 VND / 6 tháng |
| **AMD 2** | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | 1 | Đang cập nhật |
| **AMD 3** | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| **AMD 4** | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |
| **AMD 5** | 4 Core | 6 GB | 60 GB | Download 500Mbps / Upload 200Mbps | Đang cập nhật | Đang cập nhật |

## Thông Tin Thêm

*   **Trang sản phẩm**: [https://www.bkns.vn/server/cloud-vps-amd.html](https://www.bkns.vn/server/cloud-vps-amd.html)

## Xem Thêm

*   [SSL Certificate BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2024-04-07*

---

### cloud-vps-ssd.md

---
page_id: wiki.products.vps.cloud-vps-ssd
title: Cloud VPS SSD — VM Series
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 43
compile_cost_usd: 0.0113
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:08.834988+07:00'
---

# Cloud VPS SSD — VM Series

Dịch vụ cho thuê máy chủ ảo (Cloud VPS) của BKNS được xây dựng trên nền tảng ảo hóa KVM và sử dụng ổ cứng SSD cho hiệu suất cao. Dịch vụ này phù hợp cho cá nhân và doanh nghiệp cần một môi trường máy chủ ảo độc lập, tốc độ cao để chạy website, ứng dụng, lưu trữ dữ liệu hoặc các tác vụ khác.

## Bảng giá và so sánh cấu hình

| Gói | vCPU | RAM | SSD | Giá/tháng (VND) | Chu kỳ TT tối thiểu | SSL Miễn phí |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLOUD-VM01** | 1 Core | 1 GB | 20 GB | 42.000đ | 3 tháng | Không |
| **CLOUD-VM02** | 2 Core | 2 GB | 30 GB | 54.000đ | 1 tháng | Có |
| **CLOUD-VM03** | 3 Core | 3 GB | Đang cập nhật | 66.000đ | Đang cập nhật | Có |

## Đặc điểm chung của dịch vụ

*   **Nền tảng ảo hóa**: KVM
*   **Loại ổ cứng**: SSD
*   **Nền tảng lưu trữ**: Ceph Distributed Storage
*   **Băng thông**: Không giới hạn
*   **Tần suất Backup**: 1 lần / tuần
*   **Kích hoạt**: Tự động
*   **Quản lý**: Cung cấp Bảng điều khiển VPS
*   **Hệ thống giám sát**: BKNS Cloud Monitoring
*   **Mạng kết nối**: Dual Uplink – Multihome Network
*   **Hỗ trợ IP**: Hỗ trợ IPv6

## Lưu ý quan trọng

*   Giá trên bảng là giá hàng tháng và chưa bao gồm VAT.
*   SSL Miễn phí chỉ áp dụng cho các gói từ CLOUD-VM02 trở lên.

## Sản phẩm liên quan

*   [SSL Certificate BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### huong-dan.md

---
page_id: wiki.products.vps.huong-dan
title: Cloud VPS BKNS — Hướng Dẫn
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 3
compile_cost_usd: 0.0039
self_review: skipped
corrections: 0
approved_at: '2026-04-07T16:24:08.837216+07:00'
---

# Cloud VPS BKNS — Hướng Dẫn

Hướng dẫn đăng ký, kích hoạt và quản lý dịch vụ Cloud VPS tại BKNS.

## 1. Hướng dẫn Đăng ký & Mua dịch vụ

Đang cập nhật.

## 2. Hướng dẫn Kích hoạt & Triển khai

Hầu hết các dịch vụ Cloud VPS tại BKNS đều được kích hoạt tự động để đảm bảo khách hàng có thể sử dụng dịch vụ một cách nhanh chóng.

-   **Đối với VPS N8N – AI:** Dịch vụ được khởi tạo nhanh chóng và kích hoạt tự động ngay sau khi khách hàng hoàn tất đăng ký và thanh toán.
-   **Đối với VPS Siêu Rẻ:** Dịch vụ được khởi tạo và kích hoạt một cách tự động sau khi đăng ký.

## 3. Hướng dẫn Quản lý & Sử dụng cơ bản

Đang cập nhật.

## 4. Xử lý sự cố (Troubleshooting) cơ bản

Đang cập nhật.

## Sản phẩm liên quan

-   [Chứng Chỉ SSL BKNS](../ssl/index.md)
-   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
-   [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### index.md

---
page_id: wiki.products.vps.index
title: Cloud VPS BKNS — Trang Tổng Quan
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 48
compile_cost_usd: 0.0171
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.839501+07:00'
---

# Cloud VPS BKNS — Trang Tổng Quan

Cloud VPS BKNS là dịch vụ máy chủ ảo được cung cấp bởi BKNS, mang đến các giải pháp đa dạng từ chi phí thấp cho các dự án nhỏ, cá nhân đến các gói hiệu năng vượt trội cho doanh nghiệp. Dịch vụ cung cấp một môi trường máy chủ độc lập, hiệu năng cao và ổn định, cho phép người dùng có toàn quyền quản trị để chạy website, ứng dụng, lưu trữ dữ liệu hoặc các tác vụ chuyên biệt khác trên nền tảng điện toán đám mây.

## Mục Lục

*   [Tổng quan](./tong-quan.md)
*   [Bảng giá](./bang-gia.md)
*   [Thông số kỹ thuật](./thong-so.md)
*   [Tính năng](./tinh-nang.md)
*   [Chính sách](./chinh-sach.md)
*   [Câu hỏi thường gặp](./cau-hoi-thuong-gap.md)
*   [So sánh](./so-sanh.md)
*   [Hướng dẫn](./huong-dan.md)

## Các Dòng Sản Phẩm Cloud VPS

BKNS cung cấp nhiều dòng sản phẩm VPS chuyên biệt để đáp ứng các nhu cầu khác nhau của khách hàng.

### [Cloud VPS AMD](san-pham/cloud-vps-amd.md)
Dòng VPS cao cấp nhất (Flagship) của BKNS, sử dụng bộ xử lý CPU AMD EPYC™ cho hiệu suất vượt trội.
*   **Đối tượng:** Mọi doanh nghiệp có nhu cầu về một VPS hiệu suất cao với giá thành hợp lý.

### [Cloud VPS SSD](san-pham/cloud-vps-ssd.md)
Dịch vụ máy chủ ảo được xây dựng trên nền tảng ảo hóa KVM và sử dụng ổ cứng SSD cho hiệu suất cao.
*   **Đối tượng:** Cá nhân và doanh nghiệp cần một môi trường máy chủ ảo độc lập, tốc độ cao để chạy website, ứng dụng, và lưu trữ dữ liệu.

### [Storage VPS](san-pham/storage-vps.md)
Giải pháp máy chủ ảo được tối ưu hóa cho nhu cầu lưu trữ dung lượng lớn, sử dụng ổ cứng HDD.
*   **Đối tượng:** Cá nhân và doanh nghiệp cần không gian lớn để lưu trữ dữ liệu như thư viện ảnh, tài liệu, file server.

### [VPS Giá Rẻ](san-pham/vps-gia-re.md)
Dịch vụ cho thuê máy chủ ảo với chi phí thấp, cung cấp tài nguyên độc lập và quyền quản trị toàn phần.
*   **Đối tượng:** Phù hợp cho các dự án nhỏ, test, development.

### [VPS Siêu Rẻ (VPS Siêu Tiết Kiệm)](san-pham/vps-sieu-re.md)
Dịch vụ máy chủ ảo được thiết kế để tối ưu hiệu năng với chi phí thấp, phù hợp cho các tác vụ như tool automation.
*   **Đối tượng:** Người dùng cần một VPS với chi phí tối ưu, hiệu năng cơ bản cho các dự án nhỏ hoặc cá nhân.

### [BK MISA](san-pham/bk-misa.md)
Dịch vụ máy chủ ảo được cấu hình chuyên biệt để lưu trữ và vận hành phần mềm kế toán MISA SME.
*   **Đối tượng:** Các doanh nghiệp đang sử dụng MISA SME, đặc biệt là các doanh nghiệp có nhiều chi nhánh.

### [VPS SEO](san-pham/vps-seo.md)
Dịch vụ máy chủ ảo được cấu hình chuyên dụng cho các website cần tối ưu hóa cho công cụ tìm kiếm (SEO).
*   **Đối tượng:** Các cá nhân, doanh nghiệp vận hành website muốn cải thiện thứ hạng SEO.

### [VPS N8N – AI](san-pham/vps-n8n-ai.md)
Giải pháp máy chủ ảo tích hợp sẵn N8N AI, giúp tăng tốc và tối ưu hóa các quy trình tự động hóa (workflow automation).
*   **Đối tượng:** Người dùng cần triển khai các quy trình tự động hóa một cách nhanh chóng, an toàn và ổn định.

## Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---

### san-pham/cloud-vps-amd.md

---
page_id: wiki.products.vps.san-pham.cloud-vps-amd
title: Cloud VPS AMD EPYC — Hiệu Năng Cao
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 115
compile_cost_usd: 0.0258
self_review: error
corrections: 0
approved_at: '2026-04-07T16:24:08.841788+07:00'
---

# Cloud VPS AMD EPYC — Hiệu Năng Cao

Cloud VPS AMD là dòng máy chủ ảo (VPS) cao cấp nhất (Flagship) của BKNS, được thiết kế để mang lại hiệu suất vượt trội với giá thành hợp lý. Dịch vụ sử dụng bộ xử lý CPU AMD EPYC™ Gen 2 mạnh mẽ, phù hợp cho mọi doanh nghiệp đang tìm kiếm một giải pháp máy chủ ảo hiệu năng cao để tăng tốc website và ứng dụng.

## Ưu điểm nổi bật của Cloud VPS AMD EPYC

*   **Hiệu năng CPU đỉnh cao:** Trang bị chip AMD EPYC™ Gen 2 với xung nhịp từ 2.6GHz – 3.9GHz, cho tốc độ xử lý PHP nhanh hơn 30% so với các dòng chip thông thường.
*   **Ổ cứng NVMe Enterprise:** Đảm bảo tốc độ truy xuất cơ sở dữ liệu cực nhanh, loại bỏ hoàn toàn tình trạng nghẽn cổ chai.
*   **Hạ tầng mạng mạnh mẽ:** Cung cấp băng thông không giới hạn và cổng mạng vật lý tốc độ 10Gbps.
*   **Bảo mật tích hợp:** Tận dụng lớp bảo mật phần cứng AMD Infinity Guard.
*   **Khởi tạo nhanh chóng:** Hệ thống tự động khởi tạo dịch vụ chỉ trong 5-10 phút sau khi thanh toán.
*   **An toàn dữ liệu:** Dữ liệu được tự động sao lưu định kỳ hàng tuần.

## Bảng so sánh cấu hình các gói Cloud VPS AMD EPYC (1-5)

| Gói cước | vCPU | RAM | SSD NVMe | Tốc độ mạng |
| :--- | :--- | :--- | :--- | :--- |
| **EPYC 1** | 1 Core | 1 GB | 20 GB | 100 Mbps |
| **EPYC 2** | 2 Cores | 2 GB | 30 GB | 100 Mbps |
| **EPYC 3** | 3 Cores | 3 GB | 40 GB | 150 Mbps |
| **EPYC 4** | 4 Cores | 4 GB | 50 GB | 150 Mbps |
| **EPYC 5** | 4 Cores | 6 GB | 60 GB | 200 Mbps |

## Bảng giá chi tiết theo chu kỳ thanh toán

*Giá trên chưa bao gồm VAT.*

| Gói cước | 1 Tháng (VND) | 3 Tháng (VND) | 6 Tháng (VND) | 12 Tháng (VND) | 24 Tháng (VND) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EPYC 1** | 165.000 | 495.000 | 940.500 | 1.683.000 | 2.970.000 |
| **EPYC 2** | 210.000 | 630.000 | Đang cập nhật | 2.142.000 | 3.780.000 |
| **EPYC 3** | 320.000 | 960.000 | Đang cập nhật | 3.264.000 | 5.760.000 |
| **EPYC 4** | 480.000 | 1.440.000 | Đang cập nhật | 4.896.000 | 8.640.000 |
| **EPYC 5** | 710.000 | 2.130.000 | Đang cập nhật | 7.242.000 | 12.780.000 |

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/cloud-vps-vm.md

---
page_id: wiki.products.vps.san-pham.cloud-vps-vm
title: Cloud VPS SSD — VM Series
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 115
compile_cost_usd: 0.0248
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:08.844428+07:00'
---

# Cloud VPS SSD — VM Series

Dịch vụ cho thuê máy chủ ảo (Cloud VPS) dòng VM của BKNS được xây dựng trên nền tảng ảo hóa KVM và sử dụng ổ cứng SSD cho hiệu suất cao. Dịch vụ này phù hợp cho cá nhân và doanh nghiệp cần một môi trường máy chủ ảo độc lập, tốc độ cao để chạy website, ứng dụng, lưu trữ dữ liệu hoặc các tác vụ khác.

### Đặc điểm nổi bật

*   **Nền tảng:** Ảo hóa KVM, với nền tảng lưu trữ phân tán Ceph Distributed Storage.
*   **Phần cứng:** 100% sử dụng ổ cứng SSD hiệu suất cao.
*   **Mạng:** Kết nối Dual Uplink – Multihome Network, băng thông không giới hạn (Unlimited) và hỗ trợ địa chỉ IPv6.
*   **Quản lý & Vận hành:** Dịch vụ được kích hoạt tự động, cung cấp Bảng điều khiển VPS để quản lý và được giám sát bởi hệ thống BKNS Cloud Monitoring.
*   **Sao lưu:** Dữ liệu được sao lưu tự động định kỳ 1 lần/tuần.

### Bảng giá và Cấu hình chi tiết

Bảng giá dưới đây là giá niêm yết theo tháng và chưa bao gồm VAT.

| Gói | CPU | RAM | SSD | Tốc độ mạng | Giá / tháng (chưa VAT) |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **VM01** | 1 Core | 1 GB | 20 GB | 100 Mbps | 140.000 VNĐ |
| **VM02** | 2 Cores | 2 GB | 30 GB | 100 Mbps | 180.000 VNĐ |
| **VM03** | 3 Cores | 3 GB | 40 GB | 150 Mbps | 220.000 VNĐ |
| **VM04** | 4 Cores | 4 GB | 50 GB | 150 Mbps | 340.000 VNĐ |
| **VM05** | 4 Cores | 6 GB | 60 GB | 200 Mbps | 500.000 VNĐ |
| **VM06** | 5 Cores | 8 GB | 70 GB | 200 Mbps | 610.000 VNĐ |
| **VM07** | 7 Cores | 12 GB | 80 GB | 200 Mbps | 840.000 VNĐ |
| **VM08** | 8 Cores | 16 GB | 100 GB | 200 Mbps | 1.260.000 VNĐ |

### Chính sách giá và Thanh toán

*   Giá trên bảng là giá gốc cho chu kỳ thanh toán 1 tháng và 3 tháng.
*   BKNS cung cấp các gói thanh toán dài hạn với mức chiết khấu hấp dẫn:
    *   **Thanh toán 12 tháng:** Chiết khấu **15%**.
    *   **Thanh toán 24 tháng:** Chiết khấu **25%**.
    *   **Thanh toán 60 tháng:** Chiết khấu **45%**.
*   Tất cả giá trên chưa bao gồm thuế VAT.

### Lưu ý khác

*   **SSL Miễn Phí:** Không áp dụng cho gói VM01. Chỉ áp dụng cho các gói từ VM02 trở lên.

### Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/storage-vps.md

---
page_id: wiki.products.vps.san-pham.storage-vps
title: VPS Storage BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 8
compile_cost_usd: 0.0043
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:24:08.846804+07:00'
---

# VPS Storage BKNS

VPS Storage BKNS là giải pháp máy chủ ảo lưu trữ dung lượng cao, giá rẻ, được thiết kế cho các nhu cầu lưu trữ chuyên biệt.

### Ứng dụng chính

Dịch vụ này đặc biệt phù hợp để triển khai:
- File server

### Bảng giá và Cấu hình chi tiết

Dưới đây là thông tin chi tiết về cấu hình và giá của các gói dịch vụ VPS Storage.

| Tên gói | CPU | RAM | Dung lượng | Địa chỉ IPv4 | Giá (chưa VAT) |
|---|---|---|---|---|---|
| STORAGE VPS 2 | 2 Core | 2 GB | 200 GB HDD | 1 | 360.000 đ/tháng |
| STORAGE VPS 3 | 3 Core | 3 GB | 300 GB HDD | 1 | [Chưa có thông tin] |

### Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

***

*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### san-pham/vps-bk-misa.md

---
page_id: wiki.products.vps.san-pham.vps-bk-misa
title: VPS MISA BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 34
compile_cost_usd: 0.0123
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:24:08.849145+07:00'
---

# Cloud VPS BK MISA – Giải Pháp Lưu Trữ Kế Toán Số

**Cloud VPS BK MISA** là dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên biệt để lưu trữ và vận hành phần mềm kế toán MISA SME trên nền tảng điện toán đám mây.

Dịch vụ này phù hợp với các doanh nghiệp đang sử dụng MISA SME, đặc biệt là các doanh nghiệp có nhiều chi nhánh cần làm việc chung trên cùng một cơ sở dữ liệu kế toán.

## Tính năng và Lợi ích chính

*   **Tiết kiệm chi phí:** Giúp doanh nghiệp tiết kiệm chi phí đầu tư và bảo trì phần cứng máy chủ vật lý.
*   **Linh hoạt & Mở rộng:** Có thể mở rộng theo khối lượng công việc và nhu cầu sử dụng.
*   **Không giới hạn người dùng:** Cho phép nhiều người dùng truy cập và làm việc đồng thời.
*   **Hoạt động ổn định:** Cam kết thời gian hoạt động (uptime) lên đến 99.99%.
*   **An toàn dữ liệu:** Dữ liệu được sao lưu tự động hàng ngày và có khả năng khôi phục ngay cả khi bị xóa.
*   **Hỗ trợ chuyên nghiệp:** Đội ngũ kỹ thuật viên hỗ trợ 24/7/365.

## Thông số kỹ thuật

*   **Nền tảng phần cứng:** Sử dụng Chipset Intel Xeon, RAM DDR4 và ổ cứng SSD & NVME.
*   **Tốc độ truy xuất (IOPS):** Lên đến 10.000 IOPS, giúp tăng tốc độ xử lý dữ liệu.
*   **Data Center:** Máy chủ được đặt tại các Data Center lớn tại Việt Nam.

## Bảng giá

Dưới đây là thông tin chi tiết về một trong các gói dịch vụ tiêu biểu. Các gói khác đang được cập nhật.

| Tên Gói | CPU | RAM | SSD | Băng thông | Giá/tháng |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BKMS - 04** | 7 Core | 12 GB | 100 GB | 200 Mbps | 1.020.000 VNĐ |

## Chính sách dịch vụ

*   **Dùng thử miễn phí:** Cung cấp 7 ngày dùng thử dịch vụ miễn phí để khách hàng trải nghiệm.
*   **Chính sách nâng cấp:** Hỗ trợ nâng cấp gói dịch vụ bất kỳ lúc nào mà không làm gián đoạn hoạt động hay mất mát dữ liệu.
*   **Chính sách sao lưu:** Dữ liệu được sao lưu tự động hàng ngày.
*   **Khuyến mãi:** Khách hàng được tặng thêm dung lượng lưu trữ HDD khi thanh toán dịch vụ từ 12 tháng trở lên. Đối với gói **BKMS - 04**, ưu đãi là tặng miễn phí 100GB HDD khi thanh toán từ 12 tháng.

## Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-05*

---

### san-pham/vps-gia-re.md

---
page_id: wiki.products.vps.san-pham.vps-gia-re
title: VPS Giá Rẻ BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 30
compile_cost_usd: 0.009
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:24:08.851674+07:00'
---

# VPS Giá Rẻ BKNS

Dòng sản phẩm VPS Giá Rẻ của BKNS được thiết kế để đáp ứng nhu cầu của cá nhân, lập trình viên và các startup cần một môi trường máy chủ ảo ổn định với chi phí tối ưu.

## Bảng giá và Cấu hình chi tiết

Bảng dưới đây so sánh cấu hình và giá của các gói trong dòng sản phẩm VPS Giá Rẻ.

| Gói | vCPU | RAM | Dung lượng | Băng thông | Giá/Tháng |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VPS-MM01** | 1 Core | 1 GB | 20 GB | Không giới hạn | 90.000đ |
| **VPS-MM02** | 1 Core | 2 GB | 25 GB | Không giới hạn | 120.000đ |
| **VPS-MM03** | 2 Core | 2 GB | 30 GB | Không giới hạn | 140.000đ |
| **VPS-MM04** | 2 Core | 4 GB | 40 GB | Không giới hạn | 210.000đ |
| **VPS-MM05** | Đang cập nhật | 4 GB | Đang cập nhật | Không giới hạn | 310.000đ |

*Lưu ý: Cấu hình chi tiết của gói VPS-MM05 đang được cập nhật.*

## Thông tin chung & Chính sách

Các thông tin và chính sách sau áp dụng cho toàn bộ dòng sản phẩm VPS Giá Rẻ:

*   **Bảng điều khiển VPS:** Có
*   **Kích hoạt tự động:** Có
*   **Hỗ trợ IPv6:** Có
*   **Sao lưu dữ liệu hàng tuần:** Không
*   **DirectAdmin:** Không
*   **SSL Miễn Phí:** Không
*   **Thanh toán tối thiểu:** 1 tháng

## Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### san-pham/vps-mmo.md

---
page_id: wiki.products.vps.san-pham.vps-mmo
title: VPS MMO BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 72
compile_cost_usd: 0.0204
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.854406+07:00'
---

# VPS MMO BKNS

VPS MMO là dòng máy chủ ảo (VPS) được BKNS tối ưu hóa cấu hình và chi phí dành riêng cho các khách hàng có nhu cầu Kiếm tiền Online (Make Money Online - MMO). Dịch vụ cung cấp tài nguyên phần cứng đa dạng, đi kèm địa chỉ IP riêng, phù hợp cho các tác vụ yêu cầu hiệu suất và định danh mạng ổn định.

## Bảng giá và Cấu hình chi tiết

Dưới đây là bảng thông số kỹ thuật và chi phí của các gói cước VPS MMO.

| Tên gói | CPU | RAM | SSD | IPv4 | IPv6 | Giá/tháng | Giá/3 tháng | Giá/6 tháng | Giá/12 tháng |
|---|---|---|---|---|---|---|---|---|---|
| **MMO1** | 1 Core | 1 GB | 20GB | 1 IPv4 VN | IPv6/56 | 90.000 VNĐ | 210.000 VNĐ | 360.000 VNĐ | 660.000 VNĐ |
| **MMO2** | 1 Cores | 2 GB | 25GB | 1 IPv4 VN | IPv6/56 | 120.000 VNĐ | 285.000 VNĐ | 510.000 VNĐ | 900.000 VNĐ |
| **MMO3** | 2 Cores | 2 GB | 30GB | 1 IPv4 VN | IPv6/56 | 110.000 VNĐ | 300.000 VNĐ | 540.000 VNĐ | 960.000 VNĐ |
| **MMO4** | 2 Cores | 4 GB | 40GB | 1 IPv4 VN | IPv6/56 | 150.000 VNĐ | 420.000 VNĐ | 750.000 VNĐ | 1.320.000 VNĐ |
| **MMO5** | 4 Cores | 4 GB | 50GB | 1 IPv4 VN | IPv6/56 | 190.000 VNĐ | 525.000 VNĐ | 960.000 VNĐ | 1.800.000 VNĐ |
| **MMO6** | 4 Cores | 8 GB | 60GB | 1 IPv4 VN | IPv6/56 | 250.000 VNĐ | 705.000 VNĐ | 1.320.000 VNĐ | 2.520.000 VNĐ |
| **MMO7** | 8 Cores | 8 GB | 80GB | 1 IPv4 VN | IPv6/56 | 450.000 VNĐ | 1.290.000 VNĐ | 2.460.000 VNĐ | 4.800.000 VNĐ |
| **MMO8** | 8 Cores | 16 GB | 100GB | 1 IPv4 VN | IPv6/56 | 550.000 VNĐ | 1.590.000 VNĐ | 3.060.000 VNĐ | 6.000.000 VNĐ |

*Lưu ý: Bảng giá trên chưa bao gồm thuế VAT.*

## Đặc điểm Dịch vụ

*   **Cấu hình đa dạng:** Các gói VPS MMO cung cấp nhiều lựa chọn về tài nguyên, từ 1 đến 8 Cores CPU, 1GB đến 16GB RAM và dung lượng ổ cứng SSD từ 20GB đến 100GB, đáp ứng linh hoạt các quy mô công việc khác nhau.
*   **Lưu trữ SSD:** Tất cả các gói đều sử dụng ổ cứng SSD, đảm bảo tốc độ đọc/ghi và truy xuất dữ liệu nhanh chóng.
*   **Địa chỉ IP:** Mỗi gói dịch vụ được cấp 1 địa chỉ IPv4 Việt Nam và một dải địa chỉ IPv6/56, thuận lợi cho các tác vụ yêu cầu nhiều định danh mạng.

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot

---

### san-pham/vps-n8n.md

---
page_id: wiki.products.vps.san-pham.vps-n8n
title: VPS N8N-AI BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 25
compile_cost_usd: 0.0093
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.857157+07:00'
---

# VPS N8N – AI

*Dịch vụ tự động hóa quy trình tại BKNS*

## Tổng quan

VPS N8N tại BKNS là một giải pháp máy chủ ảo được tối ưu hóa cho việc triển khai N8N, một công cụ tự động hóa quy trình. Dịch vụ này cung cấp một môi trường máy chủ độc lập, hiệu năng cao và ổn định, cho phép người dùng xây dựng, quản lý và thực thi các luồng công việc tự động kết nối nhiều ứng dụng khác nhau. Tích hợp sẵn N8N AI, dịch vụ giúp tăng tốc quy trình tự động hóa của bạn.

Dịch vụ này phù hợp với người dùng cần triển khai các quy trình tự động hóa (workflow automation) một cách nhanh chóng, an toàn và ổn định trên một môi trường riêng biệt.

## Tính năng chính

- **Nền tảng ảo hóa KVM:** Đảm bảo hiệu suất và sự ổn định cho máy chủ ảo của bạn.
- **Kích hoạt tự động:** Dịch vụ được khởi tạo nhanh chóng ngay sau khi hoàn tất đăng ký.
- **Lưu lượng truyền tải:** Không giới hạn (Unlimited).
- **Sao lưu dữ liệu:** Dữ liệu được tự động sao lưu hàng tuần.
- **Hỗ trợ IPv6:** Có sẵn trên tất cả các gói dịch vụ.
- **Bảng điều khiển:** Cung cấp bảng điều khiển VPS để quản lý dễ dàng.

## Bảng giá và Cấu hình

Giá khởi điểm từ **140.000 VNĐ/tháng**.

| Gói cước | vCPU | RAM | Dung lượng | Giá/tháng | Thanh toán tối thiểu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **N8N-AI01** | 1 Core | 1 GB | 20 GB | 140.000 VNĐ | 3 tháng |

*Lưu ý: Giá trên chưa bao gồm VAT.*

## Sản phẩm liên quan

- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

---

### san-pham/vps-seo.md

---
page_id: wiki.products.vps.san-pham.vps-seo
title: VPS SEO BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 53
compile_cost_usd: 0.0146
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.860139+07:00'
---

# VPS SEO BKNS

VPS SEO là dịch vụ máy chủ ảo (Cloud VPS) được BKNS cấu hình chuyên dụng cho các website cần tối ưu hóa cho công cụ tìm kiếm (SEO). Dịch vụ này phù hợp với các cá nhân và doanh nghiệp đang vận hành website muốn cải thiện thứ hạng, đặc biệt là các hệ thống PBN (Private Blog Network).

## Tính năng chính

Dịch vụ Cloud VPS SEO của BKNS được xây dựng với các tính năng hỗ trợ tối đa cho các hoạt động SEO:

*   **Toàn quyền quản trị:** Khách hàng được cấp quyền truy cập root cao nhất, cho phép toàn quyền quản trị và sử dụng tài nguyên được cấp phát.
*   **Kích hoạt tự động:** Dịch vụ được khởi tạo và kích hoạt tự động ngay sau khi hoàn tất đăng ký.
*   **Băng thông không giới hạn:** Không giới hạn lưu lượng truy cập và truyền tải dữ liệu.
*   **Sao lưu định kỳ:** Dữ liệu trên VPS được tự động sao lưu hàng tuần để đảm bảo an toàn.
*   **Hỗ trợ IPv6:** Cung cấp địa chỉ IPv6 cho VPS.
*   **Bảng điều khiển VPS:** Cung cấp bảng điều khiển để người dùng có thể quản lý VPS của mình (khởi động, tắt, cài lại hệ điều hành...).
*   **Tối ưu cho PBN:** Cung cấp tùy chọn nhiều địa chỉ IP khác lớp C, một yếu tố quan trọng khi xây dựng hệ thống Private Blog Network.

## Bảng giá và Cấu hình chi tiết

| Thông số                | Gói SEO 01                                                  | Gói SEO 02                                                  |
| ----------------------- | ----------------------------------------------------------- | ----------------------------------------------------------- |
| **vCPU**                | 3 Core                                                      | 5 Core                                                      |
| **RAM**                 | 3 GB                                                        | 5 GB                                                        |
| **Dung lượng SSD**       | 50 GB                                                       | 70 GB                                                       |
| **Số IP**               | 5 IP                                                        | 5 IP                                                        |
| **Băng thông**          | Không giới hạn                                             | Không giới hạn                                             |
| **Sao lưu**             | Hàng tuần                                                   | Hàng tuần                                                   |
| **Giá/tháng**           | 425.000 VNĐ                                                 | 700.000 VNĐ                                                 |
| **Đăng ký**             | [Đăng ký ngay](https://my.bkns.net/?cmd=cart&action=add&id=450) | Đang cập nhật                                               |

## Chính sách và Lưu ý

*   **Chu kỳ thanh toán:** Yêu cầu thanh toán tối thiểu là **3 tháng**.
*   **IP khác lớp C:** Dịch vụ có cung cấp IP khác lớp C với phụ phí **150.000đ**.
*   **Control Panel:** Dịch vụ không hỗ trợ control panel DirectAdmin.
*   **SSL:** Gói dịch vụ không đi kèm chứng chỉ SSL miễn phí. Khách hàng có thể tham khảo dịch vụ [Chứng Chỉ SSL BKNS](../ssl/index.md).
*   **Câu hỏi thường gặp (FAQ):** Đang cập nhật.

## Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • [CURRENT_DATE]

---

### so-sanh.md

---
page_id: wiki.products.vps.so-sanh
title: Cloud VPS BKNS — So Sánh
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 1
compile_cost_usd: 0.0037
self_review: skipped
corrections: 0
approved_at: '2026-04-07T16:24:08.864587+07:00'
---

# Cloud VPS BKNS — So Sánh

Trang này cung cấp thông tin so sánh chi tiết về các gói dịch vụ Cloud VPS do BKNS cung cấp, giúp khách hàng lựa chọn giải pháp phù hợp nhất với nhu cầu và ngân sách.

Do dữ liệu về các gói dịch vụ đang trong quá trình tổng hợp, bảng so sánh dưới đây sẽ được cập nhật sớm nhất có thể.

## Bảng So Sánh Tính Năng Các Gói Cloud VPS

| Tên Gói Dịch Vụ | CPU | RAM | Ổ cứng | Băng thông | Giá |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VPS Siêu Rẻ (VPS Siêu Tiết Kiệm)** | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật | Đang cập nhật |

## Mô Tả Chi Tiết

*   **VPS Siêu Rẻ (VPS Siêu Tiết Kiệm):** Dịch vụ máy chủ ảo được thiết kế để tối ưu hiệu năng với chi phí thấp.

## Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### thong-so.md

---
page_id: wiki.products.vps.thong-so
title: Cloud VPS BKNS — Thông Số Kỹ Thuật
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 225
compile_cost_usd: 0.0429
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:08.868950+07:00'
---

# Cloud VPS BKNS — Thông Số Kỹ Thuật

Trang này so sánh chi tiết thông số kỹ thuật của các gói dịch vụ Cloud VPS do BKNS cung cấp, giúp bạn lựa chọn giải pháp phù hợp nhất với nhu cầu. Tất cả thông tin được tổng hợp từ nguồn dữ liệu đã được xác thực.

## 1. Cloud VPS AMD EPYC (Hiệu Năng Cao)

Dòng VPS sử dụng CPU AMD EPYC™ thế hệ mới, mang lại hiệu năng vượt trội, đặc biệt phù hợp cho các tác vụ đòi hỏi sức mạnh xử lý cao.

*   **CPU**: AMD EPYC™ Gen 2, xung nhịp 2.6GHz – 3.9GHz.
*   **Lưu trữ**: Ổ cứng NVMe Enterprise, đảm bảo tốc độ truy xuất dữ liệu cực nhanh.
*   **Băng thông**: Không giới hạn.
*   **Tốc độ cổng mạng**: 10Gbps.

| Gói Dịch Vụ | CPU | RAM | Dung lượng NVMe |
| :--- | :--- | :--- | :--- |
| Cloud VPS AMD EPYC 1 | 1 Core | 1 GB | 20GB |
| Cloud VPS AMD EPYC 2 | 2 Cores | 2 GB | 30GB |
| Cloud VPS AMD EPYC 3 | 3 Cores | 3 GB | 40GB |
| Cloud VPS AMD EPYC 4 | 4 Cores | 4 GB | 50GB |
| Cloud VPS AMD EPYC 5 | 4 Cores | 6 GB | 60GB |
| Cloud VPS AMD EPYC 6 | 5 Cores | 8 GB | 70GB |
| Cloud VPS AMD EPYC 7 | 7 Cores | 12 GB | 80GB |
| Cloud VPS AMD EPYC 8 | 8 Cores | 16 GB | 100GB |

## 2. Cloud VPS VM (Phổ Thông)

Dòng VPS phổ thông, cân bằng giữa chi phí và hiệu năng, sử dụng ổ cứng SSD Enterprise và nền tảng lưu trữ phân tán Ceph.

*   **Lưu trữ**: Ổ cứng SSD Enterprise.
*   **Nền tảng lưu trữ**: Ceph Distributed Storage.
*   **Mạng**: Dual Uplink – Multihome Network.
*   **Băng thông**: Không giới hạn.
*   **Hỗ trợ IP**: Có hỗ trợ IPv6.

| Gói Dịch Vụ | CPU | RAM | Dung lượng SSD |
| :--- | :--- | :--- | :--- |
| Cloud VPS VM VM01 | 1 Core | 1 GB | 20GB |
| Cloud VPS VM VM02 | 2 Cores | 2 GB | 30GB |
| Cloud VPS VM VM03 | 3 Cores | 3 GB | 40GB |
| Cloud VPS VM VM04 | 4 Cores | 4 GB | 50GB |
| Cloud VPS VM VM05 | 4 Cores | 6 GB | 60GB |
| Cloud VPS VM VM06 | 5 Cores | 8 GB | 70GB |
| Cloud VPS VM VM07 | 7 Cores | 12 GB | 80GB |
| Cloud VPS VM VM08 | 8 Cores | 16 GB | 100GB |

## 3. VPS MMO

Dòng VPS được tối ưu cho các hoạt động MMO (Make Money Online), đi kèm sẵn địa chỉ IPv4 và dải IPv6.

*   **Băng thông**: Không giới hạn.
*   **Hỗ trợ IP**: Mỗi gói đi kèm 1 địa chỉ IPv4 Việt Nam và dải IPv6/56.

| Gói Dịch Vụ | CPU | RAM | Dung lượng SSD | IPv4 | IPv6 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| VPS MMO MMO1 | 1 Core | 1 GB | 20GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO2 | 1 Cores | 2 GB | 25GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO3 | 2 Cores | 2 GB | 30GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO4 | 2 Cores | 4 GB | 40GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO5 | 4 Cores | 4 GB | 50GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO6 | 4 Cores | 8 GB | 60GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO7 | 8 Cores | 8 GB | 80GB | 1 IPv4 VN | IPv6/56 |
| VPS MMO MMO8 | 8 Cores | 16 GB | 100GB | 1 IPv4 VN | IPv6/56 |

## 4. Các Gói VPS Chuyên Dụng Khác

### VPS SEO
Tối ưu cho các dự án SEO cần nhiều địa chỉ IP.
*   **Băng thông**: Không giới hạn.
*   **Hỗ trợ IP**: Hỗ trợ IPv6.
*   **Control Panel**: Không hỗ trợ DirectAdmin.

| Gói Dịch Vụ | CPU | RAM | Dung lượng SSD | Địa chỉ IP |
| :--- | :--- | :--- | :--- | :--- |
| SEO 01 | 3 Core | 3 GB | 50 GB | 5 IP |
| SEO 02 | 5 Core | 5 GB | 70 GB | 5 IP |

### Storage VPS
Tối ưu cho nhu cầu lưu trữ dung lượng lớn với chi phí hợp lý.
*   **Lưu trữ**: Ổ cứng HDD.
*   **Băng thông**: Không giới hạn.
*   **Hệ điều hành**: Hỗ trợ CentOS, Ubuntu, Debian, Windows.

| Gói Dịch Vụ | CPU | RAM | Dung lượng HDD | IPv4 |
| :--- | :--- | :--- | :--- | :--- |
| STORAGE VPS 2 | 2 Core | 2 GB | 200 GB | 1 |
| STORAGE VPS 3 | 3 Core | 3 GB | 300 GB | 1 |

### Chính Sách Chung
*   **Hỗ trợ kỹ thuật**: 24/7/365.
*   **Đổi IP**: Hỗ trợ đổi IP miễn phí (áp dụng cho IP thuộc BKNS).

***

### Xem Thêm

*   [Máy Chủ BKNS](../server/index.md)
*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)

***

*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### tinh-nang.md

---
page_id: wiki.products.vps.tinh-nang
title: Cloud VPS BKNS — Tính Năng
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 45
compile_cost_usd: 0.0145
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:08.873488+07:00'
---

# Cloud VPS BKNS — Tính Năng

Cloud VPS tại BKNS được xây dựng trên nền tảng phần cứng mạnh mẽ với cấu hình ổn định, đi kèm nhiều tính năng nổi bật giúp khách hàng dễ dàng quản trị, đảm bảo hiệu suất và an toàn dữ liệu.

### Quản trị & Vận hành

*   **Toàn quyền quản trị (Root Access):** Cung cấp quyền truy cập root, cho phép người dùng toàn quyền cài đặt và cấu hình máy chủ ảo theo nhu cầu sử dụng riêng.
*   **Bảng điều khiển chuyên dụng:** Người dùng được cung cấp một bảng điều khiển VPS chuyên dụng để quản lý dịch vụ một cách trực quan và thuận tiện.
*   **Kích hoạt tự động:** Dịch vụ được khởi tạo và kích hoạt hoàn toàn tự động ngay sau khi đăng ký, giúp tiết kiệm thời gian triển khai.
*   **Hỗ trợ đa dạng hệ điều hành:** Tương thích với các hệ điều hành phổ biến nhất hiện nay như Windows, CentOS, Ubuntu và Debian.

### Bảo mật & Dữ liệu

*   **Môi trường hoạt động riêng biệt:** Mỗi VPS hoạt động trong một môi trường tài nguyên độc lập, giúp tăng cường bảo mật và tránh bị ảnh hưởng bởi người dùng khác so với shared hosting.
*   **Khả năng khôi phục dữ liệu:** Hệ thống được thiết kế với khả năng khôi phục dữ liệu, giúp bảo vệ thông tin ngay cả trong trường hợp bị xóa do sự cố (áp dụng trên một số dòng sản phẩm).
*   **Bảo mật phần cứng nâng cao:** Các dòng VPS hiệu năng cao sử dụng CPU AMD được trang bị công nghệ bảo mật AMD Infinity Guard, giúp bảo vệ dữ liệu ở cấp độ phần cứng.

### Hiệu suất & Hạ tầng

*   **Hạ tầng Data Center Tier III:** Dịch vụ được vận hành tại các trung tâm dữ liệu đạt chuẩn quốc tế Tier III tại Việt Nam, đảm bảo độ ổn định và tính sẵn sàng cao.
*   **Công nghệ ảo hóa KVM:** Sử dụng nền tảng ảo hóa KVM (Kernel-based Virtual Machine) tiên tiến, đảm bảo hiệu suất và sự ổn định cho từng máy chủ ảo.
*   **Nền tảng lưu trữ phân tán:** Hệ thống lưu trữ được xây dựng trên nền tảng Ceph Distributed Storage, tăng cường khả năng chịu lỗi và tốc độ truy xuất dữ liệu.
*   **Phần cứng thế hệ mới:** Cloud VPS sử dụng các nền tảng phần cứng mạnh mẽ, bao gồm Chipset Intel Xeon và CPU AMD EPYC™ thế hệ mới, kết hợp với RAM DDR4 và ổ cứng SSD/NVMe tốc độ cao.
*   **Hỗ trợ IPv6:** Tất cả các gói dịch vụ đều được hỗ trợ và cung cấp sẵn địa chỉ IPv6.

### Hỗ trợ kỹ thuật

*   **Hỗ trợ 24/7/365:** Đội ngũ kỹ thuật chuyên nghiệp của BKNS luôn sẵn sàng hỗ trợ khách hàng liên tục 24/7/365.
*   **Hỗ trợ đổi IP miễn phí:** BKNS hỗ trợ đổi địa chỉ IP miễn phí cho khách hàng (chính sách áp dụng cho các dải IP thuộc sở hữu của BKNS).

### Giới hạn & Lưu ý

*   **Sao lưu hàng tuần:** Các gói dịch vụ cơ bản không đi kèm tính năng sao lưu dữ liệu hàng tuần.
*   **Control Panel DirectAdmin:** Dịch vụ không hỗ trợ sẵn control panel DirectAdmin.
*   **Chứng chỉ SSL miễn phí:** Các gói dịch vụ không đi kèm chứng chỉ SSL miễn phí. Khách hàng có thể tham khảo các gói [Chứng Chỉ SSL BKNS](../ssl/index.md).

### Sản phẩm liên quan

*   [Chứng Chỉ SSL BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---

### tong-quan.md

---
page_id: wiki.products.vps.tong-quan
title: Cloud VPS BKNS — Tổng Quan Chi Tiết
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 93
compile_cost_usd: 0.0309
self_review: fail
corrections: 3
approved_at: '2026-04-07T16:24:08.878106+07:00'
---

# Cloud VPS BKNS — Tổng Quan Chi Tiết

Cloud VPS của BKNS là dịch vụ cho thuê máy chủ ảo (Cloud VPS), cung cấp cho người dùng một môi trường tài nguyên độc lập với quyền quản trị toàn phần. Dịch vụ này được thiết kế để giải quyết nhu cầu về một không gian máy chủ riêng biệt, bảo mật và linh hoạt hơn so với shared hosting, cho phép chạy website, ứng dụng, lưu trữ dữ liệu hoặc triển khai các tác vụ chuyên biệt.

## Các Dòng Sản Phẩm Cloud VPS tại BKNS

BKNS cung cấp một danh mục đa dạng các sản phẩm Cloud VPS, mỗi loại được tối ưu hóa cho một nhu cầu cụ thể:

*   **Cloud VPS AMD (Hiệu năng cao):** Dòng VPS cao cấp nhất (Flagship) của BKNS, sử dụng bộ xử lý CPU AMD EPYC™ thế hệ mới, mang lại hiệu suất vượt trội cho các tác vụ nặng.
*   **Storage VPS:** Giải pháp máy chủ ảo được tối ưu hóa cho nhu cầu lưu trữ dung lượng lớn với chi phí hợp lý, sử dụng ổ cứng HDD. Rất phù hợp để làm máy chủ lưu trữ tập tin (File server).
*   **VPS SEO:** Dịch vụ máy chủ ảo được cấu hình chuyên dụng cho các website cần tối ưu hóa cho công cụ tìm kiếm (SEO), với tính năng nổi bật là cung cấp nhiều địa chỉ IP khác lớp C.
*   **Cloud VPS BK MISA:** Dịch vụ máy chủ ảo được cấu hình chuyên biệt để lưu trữ và vận hành phần mềm kế toán MISA SME trên nền tảng điện toán đám mây. Giải pháp này giúp doanh nghiệp **tiết kiệm chi phí đầu tư phần cứng**, cho phép các đơn vị có nhiều chi nhánh làm việc chung trên một cơ sở dữ liệu, và đặc biệt **có khả năng khôi phục dữ liệu ngay cả khi bị xóa**.
*   **VPS N8N – AI:** Một giải pháp máy chủ ảo được tối ưu hóa cho việc triển khai N8N, một công cụ tự động hóa quy trình (workflow automation), **tích hợp sẵn các tính năng AI** giúp người dùng xây dựng và quản lý các luồng công việc một cách hiệu quả.
*   **VPS Giá Rẻ / Siêu Rẻ:** Dịch vụ cho thuê VPS với chi phí thấp, cung cấp cấu hình ổn định, phù hợp cho các dự án nhỏ, mục đích test, development, hoặc các tác vụ tự động hóa (tool automation) không đòi hỏi tài nguyên cao.
*   **Cloud VPS SSD:** Dịch vụ máy chủ ảo xây dựng trên nền tảng ảo hóa KVM và sử dụng ổ cứng SSD, mang lại hiệu suất cao cho các website, ứng dụng cần tốc độ truy xuất dữ liệu nhanh.

## Đối Tượng Phù Hợp

Dịch vụ Cloud VPS của BKNS hướng đến một dải rộng khách hàng:

*   **Doanh nghiệp:** Các doanh nghiệp cần một VPS hiệu suất vượt trội (Cloud VPS AMD), hoặc các giải pháp chuyên biệt như vận hành phần mềm kế toán (Cloud VPS BK MISA) và cải thiện thứ hạng website (VPS SEO).
*   **Cá nhân và Lập trình viên:** Những người cần một môi trường máy chủ ảo độc lập, tốc độ cao để phát triển dự án, chạy ứng dụng, hoặc lưu trữ dữ liệu cá nhân (Cloud VPS SSD, VPS Giá Rẻ).
*   **Người dùng có nhu cầu lưu trữ lớn:** Các cá nhân và tổ chức cần không gian lưu trữ lớn cho tài liệu, thư viện ảnh, video với chi phí tối ưu (Storage VPS).
*   **Chuyên gia Tự động hóa & MMO:** Người dùng cần triển khai các quy trình tự động hóa nhanh chóng, an toàn (VPS N8N – AI) hoặc các công cụ cho mục đích MMO (VPS Siêu Rẻ).

## Điểm Nổi Bật & Lợi Thế Cạnh Tranh (USP)

*   **Nền tảng phần cứng mạnh mẽ:** Sử dụng các dòng CPU hiệu năng cao như AMD EPYC™ (lên tới 64 nhân/128 luồng với công nghệ bảo mật AMD Infinity Guard) và Intel Xeon, kết hợp RAM DDR4 và ổ cứng SSD/NVME.
*   **Công nghệ ảo hóa KVM:** Đảm bảo hiệu suất, sự ổn định và tài nguyên được cấp phát độc lập, riêng biệt cho mỗi VPS.
*   **Hạ tầng Data Center chuẩn Tier III:** Dịch vụ được vận hành tại các trung tâm dữ liệu đạt chuẩn Tier III tại Việt Nam, đảm bảo tính sẵn sàng và ổn định cao.
*   **Toàn quyền quản trị (Root Access):** Người dùng được cấp quyền truy cập root cao nhất, cho phép toàn quyền cài đặt và cấu hình máy chủ theo nhu-cầu.
*   **Giải pháp chuyên dụng:** Cung cấp các gói VPS được tối ưu hóa cho các nhu cầu đặc thù như SEO, lưu trữ, phần mềm kế toán MISA, và tự động hóa N8N.
*   **Hỗ trợ kỹ thuật 24/7/365:** Đội ngũ kỹ thuật chuyên nghiệp của BKNS luôn sẵn sàng hỗ trợ liên tục.
*   **Hỗ trợ IPv6:** Hầu hết các dịch vụ VPS đều có sẵn và hỗ trợ địa chỉ IPv6.

## Thông số Kỹ thuật Chung

| Thuộc tính | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Nhà cung cấp** | BKNS | |
| **Công nghệ ảo hóa** | KVM (Kernel-based Virtual Machine) | Đảm bảo hiệu suất và sự ổn định. |
| **Nền tảng lưu trữ** | Ceph Distributed Storage | Áp dụng cho dòng Cloud VPS. |
| **Hạ tầng Data Center**| Tier III | Tại Việt Nam. |
| **Quyền quản trị** | Có (Root Access) | Toàn quyền cài đặt và cấu hình. |
| **Bảng điều khiển** | Có | Cung cấp bảng điều khiển VPS chuyên dụng. |
| **Kích hoạt dịch vụ** | Tự động | |
| **Hỗ trợ IPv6** | Có | Có sẵn trên hầu hết các gói. |
| **Hỗ trợ kỹ thuật** | 24/7/365 | |

## Khi Nào Nên Lựa Chọn Cloud VPS?

Bạn nên lựa chọn Cloud VPS khi:

*   **Cần nhiều quyền kiểm soát hơn Shared Hosting:** VPS cung cấp môi trường hoạt động riêng biệt, bảo mật hơn và cho phép bạn toàn quyền cài đặt phần mềm, cấu hình máy chủ, điều mà Shared Hosting không thể đáp ứng.
*   **Yêu cầu tài nguyên độc lập:** Không giống như Shared Hosting, tài nguyên CPU, RAM của VPS là của riêng bạn, không bị ảnh hưởng bởi người dùng khác trên cùng một máy chủ vật lý.
*   **Chi phí thấp hơn Máy chủ riêng (Dedicated Server):** VPS là một giải pháp cân bằng giữa chi phí và hiệu năng, phù hợp khi nhu cầu của bạn chưa cần đến toàn bộ tài nguyên của một máy chủ vật lý.

Để chọn đúng dòng sản phẩm VPS tại BKNS, hãy cân nhắc:
*   Nếu cần **hiệu năng cao nhất** cho ứng dụng lớn, hãy chọn **Cloud VPS AMD**.
*   Nếu cần **lưu trữ nhiều dữ liệu** với chi phí thấp, hãy chọn **Storage VPS**.
*   Nếu mục tiêu chính là **cải thiện thứ hạng website**, hãy chọn **VPS SEO**.
*   Nếu bạn đang sử dụng **phần mềm MISA**, **Cloud VPS BK MISA** là lựa chọn được tối ưu sẵn.
*   Nếu bạn muốn **tự động hóa quy trình**, hãy chọn **VPS N8N – AI**.
*   Nếu ngân sách có hạn hoặc chỉ cần cho **dự án nhỏ, test**, **VPS Giá Rẻ** là phù hợp.

### Ghi Chú

*   Một số gói dịch vụ (như VPS Giá Rẻ, VPS SEO) không hỗ trợ sẵn control panel **DirectAdmin** và không đi kèm **chứng chỉ SSL miễn phí**.
*   Chính sách sao lưu dữ liệu hàng tuần không được bao gồm trong các gói VPS Giá Rẻ.
*   BKNS hỗ trợ đổi IP miễn phí cho các địa chỉ IP thuộc quản lý của BKNS.

### Sản phẩm liên quan
- [Chứng Chỉ SSL BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### vps-gia-re.md

---
page_id: wiki.products.vps.vps-gia-re
title: VPS Giá Rẻ BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 30
compile_cost_usd: 0.0091
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.882745+07:00'
---

# VPS Giá Rẻ BKNS

VPS Giá Rẻ là dòng sản phẩm máy chủ ảo được thiết kế đặc biệt cho các cá nhân, lập trình viên và các startup có nhu cầu sử dụng VPS với chi phí tối ưu, phù hợp cho các dự án nhỏ và giai đoạn khởi đầu.

## Bảng giá và Cấu hình chi tiết

Dưới đây là bảng so sánh chi tiết về cấu hình và giá của các gói trong dòng sản phẩm VPS Giá Rẻ.

| Thông số | VPS-MM01 | VPS-MM02 | VPS-MM03 | VPS-MM04 | VPS-MM05 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **vCPU** | 1 Core | 1 Core | 2 Core | 2 Core | [CẦN BỔ SUNG] |
| **RAM** | 1 GB | 2 GB | 2 GB | 4 GB | 4 GB |
| **Dung lượng** | 20 GB | 25 GB | 30 GB | 40 GB | [CẦN BỔ SUNG] |
| **Giá/Tháng** | 90.000 VNĐ | 120.000 VNĐ | 140.000 VNĐ | 210.000 VNĐ | 310.000 VNĐ |

## Tính năng và Chính sách chung

Các thông tin dưới đây được tổng hợp từ các gói dịch vụ đã được xác thực.

*   **Lưu Lượng Truyền Tải:** Không giới hạn
*   **Bảng điều khiển VPS:** Có
*   **Kích Hoạt Tự Động:** Có
*   **Hỗ trợ IPv6:** Có
*   **Thanh Toán Tối Thiểu:** 1 tháng (xác thực trên gói VPS-MM01)
*   **Sao Lưu Dữ Liệu Hàng Tuần:** Không
*   **DirectAdmin:** Không
*   **SSL Miễn Phí:** Không

## Sản phẩm liên quan

*   [SSL Certificate BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### vps-misa.md

---
page_id: wiki.products.vps.vps-misa
title: VPS MISA BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 34
compile_cost_usd: 0.0125
self_review: fail
corrections: 1
approved_at: '2026-04-07T16:24:08.887182+07:00'
---

# Cloud VPS BK MISA – Giải Pháp Lưu Trữ Kế Toán Số

**Cloud VPS BK MISA** là dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên biệt để lưu trữ và vận hành phần mềm kế toán MISA SME trên nền tảng điện toán đám mây. Dịch vụ này đặc biệt phù hợp với các doanh nghiệp đang sử dụng MISA SME, nhất là các doanh nghiệp có nhiều chi nhánh cần làm việc chung trên cùng một cơ sở dữ liệu kế toán.

## Tính năng & Lợi ích chính

-   **Tối ưu cho MISA:** Dịch vụ được thiết kế chuyên biệt để vận hành phần mềm kế toán MISA, đảm bảo hiệu suất và tính tương thích.
-   **Tiết kiệm chi phí:** Giúp doanh nghiệp tiết kiệm chi phí đầu tư và bảo trì hệ thống phần cứng máy chủ vật lý.
-   **Hiệu suất vượt trội:** Sử dụng nền tảng phần cứng mạnh mẽ gồm Chipset Intel Xeon, RAM DDR4 và ổ cứng SSD & NVME, cho tốc độ truy xuất dữ liệu lên đến 10.000 IOPS.
-   **Hoạt động ổn định:** Cam kết thời gian hoạt động (Uptime) đạt 99.99%.
-   **An toàn dữ liệu:** Dữ liệu được sao lưu tự động hàng ngày và có khả năng khôi phục ngay cả khi bị xóa.
-   **Linh hoạt & Không giới hạn:** Cung cấp tài nguyên không giới hạn, có thể mở rộng theo khối lượng công việc và không giới hạn số lượng người dùng.
-   **Hạ tầng tại Việt Nam:** Máy chủ được đặt tại các trung tâm dữ liệu lớn tại Việt Nam, đảm bảo tốc độ truy cập nhanh và ổn định.

## Bảng giá & Cấu hình chi tiết

Dưới đây là thông tin chi tiết về gói cước BKMS - 04.

| Tên gói | CPU | RAM | SSD | Băng thông | Giá/tháng | Khuyến mãi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BKMS - 04** | 7 Core | 12 GB | 100 GB | 200 Mbps | 1.020.000 VNĐ | Tặng miễn phí 100GB HDD |

## Chính sách & Hỗ trợ

-   **Dùng thử miễn phí:** Cung cấp 7 ngày dùng thử dịch vụ miễn phí để khách hàng trải nghiệm trước khi quyết định.
-   **Hỗ trợ nâng cấp:** Hỗ trợ nâng cấp gói dịch vụ bất kỳ lúc nào mà không làm gián đoạn dịch vụ hay mất mát dữ liệu.
-   **Chính sách sao lưu:** Dữ liệu được sao lưu tự động hàng ngày.
-   **Khuyến mãi thanh toán:** Khách hàng được tặng thêm dung lượng lưu trữ HDD khi thanh toán dịch vụ từ 12 tháng trở lên.
-   **Hỗ trợ kỹ thuật:** Đội ngũ kỹ thuật chuyên nghiệp sẵn sàng hỗ trợ 24/7/365.

## Sản phẩm liên quan

-   [SSL Certificate BKNS](../ssl/index.md)
-   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
-   [Máy Chủ BKNS](../server/index.md)

---
Compiled by BKNS Wiki Bot • 2026-04-05

---

### vps-n8n-ai.md

---
page_id: wiki.products.vps.vps-n8n-ai
title: VPS N8N-AI BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 25
compile_cost_usd: 0.0093
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.891648+07:00'
---

# VPS N8N – AI

**VPS N8N – AI** tại BKNS là một giải pháp máy chủ ảo được tối ưu hóa cho việc triển khai N8N, một công cụ tự động hóa quy trình. Đây là dịch vụ tự động hóa quy trình, cung cấp một môi trường máy chủ độc lập, hiệu năng cao và ổn định, cho phép người dùng xây dựng, quản lý và thực thi các luồng công việc tự động kết nối nhiều ứng dụng khác nhau.

Dịch vụ này phù hợp với những người dùng cần triển khai các quy trình tự động hóa (workflow automation) một cách nhanh chóng, an toàn và ổn định trên một môi trường riêng biệt.

## Tính năng nổi bật

*   **Nền tảng ảo hóa KVM**: Đảm bảo hiệu suất và sự ổn định cho máy chủ ảo.
*   **Kích hoạt tự động**: Dịch vụ được khởi tạo nhanh chóng ngay sau khi hoàn tất đăng ký.
*   **Lưu lượng không giới hạn**: Cung cấp lưu lượng truyền tải dữ liệu không giới hạn (Unlimited).
*   **Sao lưu hàng tuần**: Dữ liệu trên VPS được tự động sao lưu định kỳ mỗi tuần.
*   **Hỗ trợ IPv6**: Có sẵn trên tất cả các gói dịch vụ.
*   **Bảng điều khiển**: Cung cấp bảng điều khiển VPS để người dùng dễ dàng quản lý.

## Bảng giá và Cấu hình

Giá khởi điểm cho dịch vụ từ **140.000 VNĐ/tháng**.

| Tên Gói | vCPU | RAM | Dung Lượng | Giá/Tháng (VNĐ) | Thanh Toán Tối Thiểu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **N8N-AI01** | 1 Core | 1 GB | 20 GB | 140.000 | 3 tháng |
| **N8N-AI02** | Đang cập nhật | Đang cập nhật | Đang cập nhật | 180.000 | Đang cập nhật |

## Lưu ý

*   Giá trên chưa bao gồm thuế VAT.

---

### vps-seo.md

---
page_id: wiki.products.vps.vps-seo
title: VPS SEO BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 53
compile_cost_usd: 0.0129
self_review: pass
corrections: 0
approved_at: '2026-04-07T16:24:08.895952+07:00'
---

# VPS SEO BKNS

**VPS SEO** là dịch vụ máy chủ ảo (Cloud VPS) được cấu hình chuyên dụng cho các cá nhân và doanh nghiệp vận hành website muốn cải thiện thứ hạng trên các công cụ tìm kiếm (SEO). Dịch vụ cung cấp môi trường tối ưu cho các hoạt động SEO, đặc biệt là xây dựng hệ thống PBN (Private Blog Network).

## Đặc điểm và Tính năng nổi bật

- **Toàn quyền quản trị:** Khách hàng được cấp quyền root, có toàn quyền quản trị và sử dụng tài nguyên được cấp phát trên VPS.
- **Tối ưu cho SEO:** Cung cấp nhiều địa chỉ IP khác lớp C, một yếu tố quan trọng cho việc xây dựng hệ thống website vệ tinh.
- **Kích hoạt tự động:** Dịch vụ được khởi tạo và kích hoạt một cách tự động ngay sau khi hoàn tất đăng ký.
- **Băng thông không giới hạn:** Không giới hạn lưu lượng truy cập và truyền tải dữ liệu.
- **Sao lưu định kỳ:** Dữ liệu trên VPS được tự động sao lưu định kỳ mỗi tuần.
- **Hỗ trợ IPv6:** Dịch vụ có hỗ trợ và cung cấp địa chỉ IPv6 cho VPS.
- **Bảng điều khiển VPS:** Cung cấp bảng điều khiển để người dùng có thể quản lý VPS của mình (khởi động, tắt, cài lại hệ điều hành...).

## Bảng giá và Cấu hình

| Gói dịch vụ | vCPU | RAM | Dung lượng SSD | IP | Băng thông | Giá hàng tháng | Đăng ký |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SEO 01** | 3 Core | 3 GB | 50 GB | 5 | Không giới hạn | 425.000 VND | [Đăng ký](https://my.bkns.net/?cmd=cart&action=add&id=450) |
| **SEO 02** | 5 Core | 5 GB | 70 GB | 5 | Không giới hạn | 700.000 VND | Đang cập nhật |

**Chính sách và Lưu ý:**

*   **Chu kỳ thanh toán:** Yêu cầu thanh toán tối thiểu cho dịch vụ là **3 tháng**.
*   **Phụ phí:** Tùy chọn sử dụng IP khác lớp C có phụ phí **150.000 VND**.
*   **Giới hạn:** Dịch vụ không hỗ trợ control panel DirectAdmin và không đi kèm chứng chỉ SSL miễn phí.

## Sản phẩm liên quan

- [SSL Certificate BKNS](../ssl/index.md)
- [Phần Mềm & Bản Quyền BKNS](../software/index.md)
- [Máy Chủ BKNS](../server/index.md)

Compiled by BKNS Wiki Bot • 2026-04-07

---

### vps-sieu-re.md

---
page_id: wiki.products.vps.vps-sieu-re
title: VPS Siêu Rẻ BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 67
compile_cost_usd: 0.015
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.900149+07:00'
---

# VPS Siêu Rẻ BKNS (VPSTK Series)

**VPS Siêu Rẻ** (còn được biết đến với tên gọi **VPS Siêu Tiết Kiệm**) là dịch vụ cho thuê máy chủ ảo (VPS) của BKNS với chi phí thấp, cung cấp tài nguyên độc lập và quyền quản trị toàn phần cho người dùng.

Dịch vụ này phù hợp cho người dùng cần một VPS với chi phí tối ưu, hiệu năng cơ bản cho các dự án nhỏ, cá nhân, hoặc các tác vụ như tool automation.

### Đặc điểm chung

*   **Khởi tạo tự động**: Dịch vụ được kích hoạt một cách tự động ngay sau khi đăng ký thành công.
*   **Sao lưu dữ liệu**: Cung cấp tính năng sao lưu dữ liệu định kỳ hàng tuần.
*   **Bảng điều khiển**: Người dùng được cung cấp bảng điều khiển để quản lý VPS của mình.
*   **Chu kỳ thanh toán**: Các gói dịch vụ có chu kỳ thanh toán tối thiểu là 1 tháng.

### Bảng giá và Cấu hình chi tiết (VPSTK Series)

Dưới đây là bảng so sánh chi tiết các gói cước thuộc dòng VPS Siêu Rẻ.

| Tên Gói | vCPU | RAM | Dung lượng | Giá/Tháng (VNĐ) | Thanh toán tối thiểu |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **VPSTK1** | 1 Core | 1 GB | 20 GB | 69.000 | 1 tháng |
| **VPSTK2** | 1 Core | 2 GB | 25 GB | 99.000 | 1 tháng |
| **VPSTK3** | 2 Core | 2 GB | 30 GB | 129.000 | 1 tháng |
| **VPSTK4** | 2 Core | 3 GB | 40 GB | 159.000 | 1 tháng |
| **VPSTK5** | 2 Core | 4 GB | 50 GB | 189.000 | 1 tháng |
| **VPSTK6** | 3 Core | 6 GB | 60 GB | 239.000 | 1 tháng |
| **VPSTK7** | Đang cập nhật | 8 GB | 80 GB | 299.000 | Đang cập nhật |

*Lưu ý: Giá trên chưa bao gồm VAT.*

### Tùy chọn nâng cấp

*   **Thêm RAM**: 30.000 VNĐ/tháng. (Lưu ý: Cần xác định dung lượng RAM được thêm).

### Xem thêm

*   [SSL Certificate BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • [ngày biên soạn thực tế]*

---

### vps-storage.md

---
page_id: wiki.products.vps.vps-storage
title: VPS Storage BKNS
category: products/vps
updated: '2026-04-07'
review_state: approved
claims_used: 8
compile_cost_usd: 0.0049
self_review: fail
corrections: 2
approved_at: '2026-04-07T16:24:08.904417+07:00'
---

# VPS Storage BKNS

Storage VPS là giải pháp máy chủ ảo (VPS) chuyên dụng cho nhu cầu lưu trữ dung lượng cao. Đây là một lựa chọn có mức giá rẻ, được thiết kế để tối ưu cho việc lưu trữ dữ liệu.

## Trường hợp sử dụng

Với đặc tính dung lượng lớn, VPS Storage đặc biệt phù hợp để triển khai làm:

*   File server

## Bảng giá và Cấu hình chi tiết

*Lưu ý: Bảng giá và cấu hình dưới đây được tổng hợp từ các thông tin đã được xác thực. Các mục ghi "Đang cập nhật" sẽ được bổ sung khi có dữ liệu.*

| Tên gói | CPU | RAM | Dung lượng | Địa chỉ IPv4 | Băng thông | Giá/tháng |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| STORAGE VPS 2 | 2 Core | 2 GB | 200 GB | 1 | Không giới hạn | 360.000 VNĐ |
| STORAGE VPS 3 | 3 Core | 3 GB | 300 GB | 1 | Không giới hạn | 540.000 VNĐ |

## Sản phẩm liên quan

*   [SSL Certificate BKNS](../ssl/index.md)
*   [Phần Mềm & Bản Quyền BKNS](../software/index.md)
*   [Máy Chủ BKNS](../server/index.md)

---
*Compiled by BKNS Wiki Bot • 2026-04-07*

---


---
page_id: wiki.products.vps.thong-so
title: "Cloud VPS BKNS — Thông số kỹ thuật"
category: products/vps
updated: '2026-04-07'
review_state: drafted
claims_used: 18
---


# Cloud VPS BKNS — Thông số kỹ thuật

## Bảng specs chuẩn cho Cloud VPS VM
| Gói | Giá | CPU | RAM | SSD/NVMe | Network | Download | Upload |
|---|---|---|---|---|---|---|---|
| Cloud Server-VM01 | 119.000đ/tháng | 1 Core | 1 GB | 20 GB | 10Gbps | 500Mbps | 100Mbps |
| Cloud Server-VM02 | 153.000đ/tháng | 2 Core | 2 GB | 30 GB | 10Gbps | 500Mbps | 100Mbps |
| Cloud Server-VM03 | 187.000đ/tháng | 3 Core | 3 GB | 40 GB | 10Gbps | 500Mbps | 150Mbps |
| Cloud Server-VM04 | 289.000đ/tháng | 4 Core | 4 GB | 50 GB | 10Gbps | 500Mbps | 150Mbps |
| Cloud Server-VM05 | 425.000đ/tháng | 4 Core | 6 GB | 60 GB | 10Gbps | 500Mbps | 200Mbps |
| Cloud Server-VM06 | 519.000đ/tháng | 5 Core | 8 GB | 70 GB | 10Gbps | 500Mbps | 200Mbps |
| Cloud Server-VM07 | 714.000đ/tháng | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ | ⏳ |

## Bảng specs chuẩn cho Cloud VPS AMD
| Gói | Giá | CPU | RAM | NVMe | Network | Download | Upload | Backup |
|---|---|---|---|---|---|---|---|---|
| AMD 1 | 140.000đ/tháng | 1 Core | 1 GB | 20 GB | 10Gbps | 500Mbps | 100Mbps | Tuần/lần |
| AMD 2 | 179.000đ/tháng | 2 Core | 2 GB | 30 GB | 10Gbps | 500Mbps | 100Mbps | Tuần/lần |
| AMD 3 | 272.000đ/tháng | 3 Core | 3 GB | 40 GB | 10Gbps | 500Mbps | 150Mbps | Tuần/lần |
| AMD 4 | 408.000đ/tháng | 4 Core | 4 GB | 50 GB | 10Gbps | 500Mbps | 150Mbps | Tuần/lần |
| AMD 5 | 604.000đ/tháng | 4 Core | 6 GB | 60 GB | 10Gbps | 500Mbps | 200Mbps | Tuần/lần |
| AMD 6 | 740.000đ/tháng | 5 Core | 8 GB | 70 GB | 10Gbps | 500Mbps | 200Mbps | Tuần/lần |
| AMD 7 | 1.020.000đ/tháng | 7 Core | 12 GB | 80 GB | 10Gbps | 500Mbps | 200Mbps | Tuần/lần |
| AMD 8 | 1.530.000đ/tháng | 8 Core | 16 GB | 100 GB | 10Gbps | 500Mbps | 200Mbps | Tuần/lần |

## Thuộc tính hạ tầng dùng lại cho nhiều trang VPS
| Thuộc tính | Giá trị draft |
|---|---|
| Loại lưu trữ | 100% NVMe / Enterprise NVMe |
| Cơ chế sẵn sàng cao | High Availability (HA) |
| CPU platform | Intel Xeon / AMD EPYC tùy dòng |
| Control panel | Reboot, Reinstall OS, Firewall, Console, Snapshot |
| Hệ điều hành hỗ trợ | Linux / Windows / distro linh hoạt (chi tiết cần verify theo từng dòng) |
| Băng thông | Không giới hạn / tốc độ phụ thuộc từng gói |
| Backup | Miễn phí / định kỳ / tuần-lần (tùy dòng) |

## Trường dữ liệu nên có trong schema
- `cpu_cores`
- `ram_gb`
- `storage_gb`
- `storage_type`
- `network_port`
- `download_speed`
- `upload_speed`
- `backup_frequency`
- `ha_enabled`
- `os_supported`
- `control_panel_features`

## Sản phẩm liên quan

- [Bảng giá Cloud VPS](./bang-gia.md)
- [So sánh Cloud VPS](./so-sanh.md)
- [Máy Chủ](../server/index.md)

## Liên hệ / đăng ký

- [Liên hệ BKNS](../../support/lien-he.md)
- [Hướng dẫn chung](../../support/huong-dan-chung.md)

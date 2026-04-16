#!/usr/bin/env python3
"""
Generate raw markdown files from web-crawled data for the BKNS wiki pipeline.
Each file has proper YAML frontmatter with status=pending_extract.
Pricing data is sourced from the Excel file (source of truth).

Output: raw/website-crawl/*.md (pipeline scans this directory)
"""
import hashlib
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/wiki/raw/website-crawl")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CRAWL_DATE = "2026-04-05T14:25:00+07:00"
TODAY = "2026-04-05"


def content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def write_raw_file(filename: str, title: str, source_url: str, category: str, body: str):
    """Write a raw markdown file with proper frontmatter."""
    fm = f"""---
source_url: "{source_url}"
crawled_at: '{CRAWL_DATE}'
content_type: web_crawl
original_file: "{filename}"
original_format: web
page_title: "{title}"
content_hash: {content_hash(body)}
word_count: {len(body.split())}
status: pending_extract
suggested_category: {category}
crawl_method: web_crawl_tavily
source_date: '{TODAY}'
---

"""
    filepath = OUTPUT_DIR / filename
    filepath.write_text(fm + body, encoding="utf-8")
    print(f"  ✅ {filename} ({len(body.split())} words)")


# ═══════════════════════════════════════════════════════════════
# 1. TÊN MIỀN (DOMAIN)
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "dang-ky-ten-mien-2026-04-05.md",
    "Đăng Ký Tên Miền Website Giá Rẻ tại BKNS",
    "https://www.bkns.vn/ten-mien/dang-ky-ten-mien.html",
    "products/ten-mien",
    """# Đăng Ký Tên Miền Website Giá Rẻ – Kích Hoạt Tự Động Trong 30s

## Giới thiệu
BKNS là nhà đăng ký tên miền chính thức được cấp phép bởi VNNIC (Việt Nam) và ICANN (Quốc tế). Hơn 500.000+ cá nhân và doanh nghiệp tin dùng dịch vụ đăng ký tên miền tại BKNS.

## Tại sao chọn BKNS?
- Nhà đăng ký tên miền chính thức VNNIC & ICANN
- eKYC 100% online, quyền sở hữu hợp pháp tuyệt đối
- Kích hoạt tự động trong 30 giây
- Miễn phí Privacy Protection, miễn phí transfer khi chuyển về BKNS
- Tên miền .VN được pháp luật Việt Nam bảo hộ tuyệt đối
- Lợi thế SEO Local vượt trội (Google ưu tiên .VN cho IP Việt Nam)

## Quy trình đăng ký
1. Kiểm tra tên miền còn trống
2. Đăng ký và thanh toán
3. Kích hoạt tự động trong 30s
4. eKYC xác minh quyền sở hữu

## Hỗ trợ
- Hotline kỹ thuật: 1900 63 68 09 (có phí)
- Hotline kinh doanh: 1800 646 884 (miễn phí)
- Website: https://bkns.vn
"""
)

write_raw_file(
    "bang-gia-ten-mien-vn-web-2026-04-05.md",
    "Bảng Giá Tên Miền Việt Nam 2026",
    "https://www.bkns.vn/ten-mien/bang-gia-ten-mien.html",
    "products/ten-mien",
    """# Bảng Giá Tên Miền Việt Nam (Hiệu lực từ 01/09/2025)

## Bảng giá tên miền .VN

| Tên miền | Đăng ký mới (VND) | Phí gia hạn (VND) | Transfer về BKNS |
|---|---|---|---|
| .vn | 450.000 | 450.000 | Miễn phí |
| .com.vn | 350.000 | 350.000 | Miễn phí |
| .net.vn | 350.000 | 350.000 | Miễn phí |
| .biz.vn | 350.000 | 350.000 | Miễn phí |
| .ai.vn | 350.000 | 350.000 | Miễn phí |
| .org.vn | 150.000 | 150.000 | Miễn phí |
| .gov.vn | 150.000 | 150.000 | Miễn phí |
| .edu.vn | 150.000 | 150.000 | Miễn phí |
| .health.vn | 150.000 | 150.000 | Miễn phí |
| .ac.vn | 150.000 | 150.000 | Miễn phí |
| .int.vn | 150.000 | 150.000 | Miễn phí |
| .info.vn | 60.000 | 60.000 | Miễn phí |
| .pro.vn | 60.000 | 60.000 | Miễn phí |
| .id.vn | 60.000 | 60.000 | Miễn phí |
| .name.vn | 30.000 | 30.000 | Miễn phí |
| .io.vn | 30.000 | 30.000 | Miễn phí |
| Tên miền Tiếng Việt | 30.000 | 30.000 | Miễn phí |

## Ghi chú
- Giá chưa bao gồm VAT
- Transfer tên miền về BKNS: Miễn phí
- Tất cả tên miền .VN được pháp luật Việt Nam bảo hộ
- eKYC 100% online

## Bảng Giá Tên Miền Quốc Tế

| Đuôi | Phí cài đặt | Đăng ký mới (VND) | Duy trì hàng năm (VND) | Transfer (VND) |
|---|---|---|---|---|
| .com | Miễn phí | 25.000 (mua từ 5 năm, kèm .cloud miễn phí, giảm 50% Hosting/Email/VPS) | 379.000 | 379.000 |
| .net | Miễn phí | 159.000 (mua từ 5 năm, kèm .cloud miễn phí) | 439.000 | 439.000 |
| .org | Miễn phí | 365.000 | 535.000 | 535.000 |
| .info | Miễn phí | 170.000 | 980.000 | 980.000 |
| .id | Miễn phí | 575.000 | 575.000 | 575.000 |
| .biz | Miễn phí | 590.000 | 740.000 | 740.000 |

## Lưu ý khuyến mãi
- .com chỉ 25.000đ khi mua từ 5 năm
- Kèm tên miền .cloud miễn phí
- Giảm 50% dịch vụ Hosting/Email/VPS khi mua combo
- .net chỉ 159.000đ khi mua từ 5 năm
"""
)

# ═══════════════════════════════════════════════════════════════
# 2. HOSTING
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "platinum-web-hosting-web-2026-04-05.md",
    "Platinum Web Hosting - Hosting NVMe Tốc Độ Cao",
    "https://www.bkns.vn/hosting/platinum-web-hosting.html",
    "products/hosting",
    """# Platinum Web Hosting - Hosting NVMe Tốc Độ Cao, Backup 3 Lần/Ngày

## Giới thiệu
Platinum Web Hosting là dòng hosting cao cấp nhất của BKNS, sử dụng ổ cứng NVMe U.2 và CPU Intel Xeon Platinum.

## Đặc điểm nổi bật
- Ổ cứng NVMe U.2 tốc độ cao (nhanh gấp 25 lần HDD thông thường)
- CPU Intel Xeon Platinum
- Backup tự động 3 lần/ngày
- cPanel/DirectAdmin tiếng Việt
- Softaculous cài 1-click WordPress và 400+ ứng dụng
- Zero downtime khi nâng cấp gói
- Uptime cam kết lên đến 100%
- Băng thông không giới hạn

## Bảng giá gói BKCP05+ (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Thông số | Giá trị |
|---|---|
| CPU | 3 Cores |
| RAM | 8 GB |
| NVMe U.2 Storage | 30 GB |
| Domain | 10 |
| Giá tháng | 290.000đ |
| Giá 1 năm (giảm 5%) | 3.306.000đ |
| Giá 2 năm (giảm 20%) | 5.568.000đ |
| Giá 3 năm (giảm 30%) | 7.308.000đ |
| Giá 4 năm (giảm 40%) | 8.352.000đ |

## Giá khởi điểm
Giá từ 27.550đ/tháng (gói cơ bản nhất)
"""
)

write_raw_file(
    "hosting-gia-re-web-2026-04-05.md",
    "Hosting Giá Rẻ tại BKNS",
    "https://www.bkns.vn/hosting/hosting-gia-re.html",
    "products/hosting",
    """# Hosting Giá Rẻ - Bảng Giá và Thông Số Kỹ Thuật tại BKNS

## Giới thiệu
Hosting giá rẻ tại BKNS với giá chỉ từ 19.000đ/tháng, phù hợp cho website cá nhân, blog, landing page.

## Đặc điểm
- Giá chỉ từ 19.000đ/tháng
- Đội ngũ kỹ thuật chứng nhận cPanel 100%
- Băng thông không giới hạn
- Nâng cấp dễ dàng lên gói cao hơn
- cPanel Control Panel tiếng Việt
- Softaculous 1-click install WordPress
- Ưu đãi: Off 15% Hosting + Domain khi mua combo

## Phù hợp cho
- Website cá nhân, blog
- Landing page quảng cáo
- Website giới thiệu doanh nghiệp nhỏ
- Website mới bắt đầu
"""
)

write_raw_file(
    "hosting-mien-phi-web-2026-04-05.md",
    "Hosting Miễn Phí tại BKNS",
    "https://www.bkns.vn/hosting/hosting-mien-phi.html",
    "products/hosting",
    """# Hosting Miễn Phí - Khởi Tạo Website Chỉ Với 0đ

## Giới thiệu
BKNS cung cấp gói hosting miễn phí cho người mới bắt đầu, giúp khởi tạo website với chi phí 0đ.

## Đặc điểm
- Miễn phí hoàn toàn
- Phù hợp cho người mới học làm website
- Có thể nâng cấp lên gói trả phí bất cứ lúc nào
- Hỗ trợ kỹ thuật cơ bản
"""
)

write_raw_file(
    "seo-hosting-web-2026-04-05.md",
    "SEO Hosting tại BKNS",
    "https://www.bkns.vn/hosting/seo-hosting.html",
    "products/hosting",
    """# Hosting SEO - Tối Ưu Website Cho Công Cụ Tìm Kiếm

## Giới thiệu
SEO Hosting là dịch vụ hosting chuyên biệt cho SEO, cho phép quản lý nhiều website cùng 1 tài khoản hosting, mỗi website sử dụng 1 IP riêng biệt.

## Đặc điểm nổi bật
- Nhiều website cùng 1 tài khoản hosting
- Mỗi site được gán 1 IP riêng biệt (khác Class C)
- Hệ thống IP đa dạng hỗ trợ chiến dịch SEO Private Blog Network
- Sao lưu dữ liệu tự động
- Hỗ trợ kỹ thuật 24/7

## Bảng giá
| Gói | Giá/tháng |
|---|---|
| Giá khởi điểm | 189.000đ/tháng |

## Phù hợp cho
- Chủ PBN (Private Blog Network)
- Agency SEO quản lý nhiều website
- Chiến dịch link building đa IP
"""
)

write_raw_file(
    "hosting-wordpress-web-2026-04-05.md",
    "Hosting WordPress Tốc Độ Cao tại BKNS",
    "https://www.bkns.vn/hosting/hosting-wordpress.html",
    "products/hosting",
    """# Hosting WordPress Tốc Độ Cao – Bảng Giá & Giải Pháp Tối Ưu SEO

## Giới thiệu
Hosting WordPress tại BKNS được tối ưu riêng cho WordPress, đảm bảo tốc độ cao và bảo mật.

## Đặc điểm
- Tối ưu riêng cho WordPress
- Off 20% khi chuyển dịch vụ về BKNS
- Giá từ 24.000đ/tháng

## Bảng giá gói WPCP08 (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Thông số | Giá trị |
|---|---|
| SSD Disk space | 30 GB |
| Domain | 15 |
| Giá tháng | 500.000đ |
| Giá 1 năm (giảm 5%) | 5.700.000đ |
| Giá 2 năm (giảm 20%) | 9.600.000đ |
| Giá 3 năm (giảm 30%) | 12.600.000đ |
| Giá 4 năm (giảm 40%) | 14.400.000đ |
"""
)

write_raw_file(
    "windows-hosting-web-2026-04-05.md",
    "Dịch Vụ Hosting Windows tại BKNS",
    "https://www.bkns.vn/hosting/windows-hosting.html",
    "products/hosting",
    """# Dịch Vụ Hosting Windows tại BKNS

## Giới thiệu
Windows Hosting hỗ trợ ASP.NET & MSSQL, IIS Web Server - phù hợp cho ứng dụng .NET Framework.

## Đặc điểm
- Hỗ trợ ASP.NET và MSSQL
- IIS Web Server
- Giá từ 31.350đ/tháng

## Bảng giá gói BKSW01 (website)
| Thông số | Giá trị |
|---|---|
| Giá | 31.350đ/tháng |
| Thanh toán tối thiểu | 12 tháng |
| Disk space | 1 GB (nâng từ 250MB) |
| Bandwidth | 20 GB (nâng từ 5 GB) |
| Domain | 01 |
| Parked/Sub Domain | 02 |
| FTP Accounts | 02 |
| Email Accounts | 05 |
| MSSQL Accounts | 02 |

## Bảng giá gói BKSW05+ (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Thông số | Giá trị |
|---|---|
| SSD Disk Space | 15 GB |
| Domain | 15 |
| Giá tháng | 390.000đ |
| Giá 1 năm | 4.680.000đ |
| Giá 2 năm (giảm 16%) | 7.862.400đ |
| Giá 3 năm (giảm 26%) | 10.389.600đ |
"""
)

write_raw_file(
    "reseller-hosting-web-2026-04-05.md",
    "Reseller Hosting cPanel tại BKNS",
    "https://www.bkns.vn/hosting/reseller-hosting-cpanel.html",
    "products/hosting",
    """# Reseller Hosting cPanel - Quản Lý Nhiều Hosting Chỉ Với Một Tài Khoản

## Giới thiệu
Reseller Hosting cPanel cho phép quản lý nhiều hosting chỉ với 1 tài khoản, giá từ $2-$12/tháng. Phù hợp cho đại lý hosting.

## Đặc điểm
- Control Panel riêng cho mỗi khách hàng
- Quản lý nhiều hosting từ 1 tài khoản WHM
- Hỗ trợ kỹ thuật 24/5
- Hoàn tiền 100% nếu không hài lòng
- Cài WordPress 1 click qua Softaculous
- Giá từ $2/tháng đến $12/tháng

## Phù hợp cho
- Đại lý hosting
- Web agency
- Freelancer quản lý nhiều website khách hàng
"""
)

# ═══════════════════════════════════════════════════════════════
# 3. EMAIL
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "email-hosting-web-2026-04-05.md",
    "Dịch Vụ Email Hosting Chuyên Nghiệp tại BKNS",
    "https://www.bkns.vn/email/email-hosting.html",
    "products/email",
    """# Dịch Vụ Email Hosting Chuyên Nghiệp, An Toàn, Bảo Mật Cao

## Giới thiệu
Email Hosting theo tên miền riêng, nền tảng Zimbra, tỉ lệ inbox 99%.

## Bảng giá các gói Email Hosting (website)
| Gói | Giá/tháng | Số email | Email Forwarders | Dung lượng/email |
|---|---|---|---|---|
| EMAIL 1 | 42.750đ | 05 | 05 | 5 GB |
| EMAIL 2 | 85.500đ | 20 | 10 | 5 GB |
| EMAIL 3 | 166.250đ | 50 | 40 | 5 GB |
| EMAIL 4 | 285.000đ | 100 | 100 | 5 GB |

## Bảng giá gói EMAIL 1 (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Kỳ thanh toán | Giá (VND) |
|---|---|
| Giá tháng | 45.000 |
| 1 năm (giảm 5%) | 513.000 |
| 2 năm (giảm 20%) | 864.000 |
| 3 năm (giảm 30%) | 1.134.000 |
| 4 năm (giảm 40%) | 1.296.000 |

## Tính năng chung
- Tỉ lệ inbox 99%
- Chống Spam/Virus tích hợp
- Tự động trả lời
- Webmail, hỗ trợ Outlook
- Gửi tối đa 200 email/giờ
- 1 tên miền/gói
- Nền tảng Zimbra
"""
)

write_raw_file(
    "email-relay-web-2026-04-05.md",
    "Email Relay - Giải Pháp Gửi Email An Toàn tại BKNS",
    "https://www.bkns.vn/email/email-relay.html",
    "products/email",
    """# Email Relay - Giải Pháp Gửi Email An Toàn và Tin Cậy

## Giới thiệu
Email Relay là giải pháp gửi email an toàn, tin cậy với White list IP. Phù hợp cho doanh nghiệp cần gửi email marketing số lượng lớn.

## Bảng giá gói BK-RELAY 04 (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Thông số | Giá trị |
|---|---|
| Số lượng mail/ngày | 30.000 |
| Giá 1 tháng | 980.000đ |
| 1 năm (giảm 5%) | 11.760.000đ |
| 2 năm (giảm 20%) | 23.520.000đ |
| 3 năm (giảm 30%) | 35.280.000đ |

## Đặc điểm
- White list IP để đảm bảo email không bị chặn
- Gửi email số lượng lớn an toàn
- Tỉ lệ inbox cao
- Hỗ trợ SPF, DKIM, DMARC
"""
)

write_raw_file(
    "cloud-email-server-web-2026-04-05.md",
    "Dịch Vụ Cloud Email Server tại BKNS",
    "https://www.bkns.vn/email/cloud-email-server.html",
    "products/email",
    """# Cloud Email Server - Giải Pháp Email Doanh Nghiệp

## Giới thiệu
Cloud Email Server là giải pháp mail server doanh nghiệp, uptime 99%, không giới hạn số user. Giá từ 313.650đ/tháng.

## Bảng giá (Giá chính xác từ bảng giá nội bộ, chưa VAT)

### Gói MINI EMAIL 1
| Kỳ thanh toán | Giá (VND) |
|---|---|
| Dung lượng | 100 GB |
| Giá tháng | 369.000 |
| 6 tháng (giảm 5%) | 2.103.300 |
| 1 năm (giảm 15%) | 3.763.800 |
| 2 năm (giảm 25%) | 6.642.000 |
| 3 năm (giảm 35%) | 8.634.600 |

### Gói ES 1
| Kỳ thanh toán | Giá (VND) |
|---|---|
| Dung lượng | 300 GB |
| Giá tháng | 870.000 |
| 6 tháng (giảm 5%) | 4.959.000 |
| 1 năm (giảm 15%) | 8.874.000 |
| 2 năm (giảm 25%) | 15.660.000 |
| 3 năm (giảm 35%) | 20.358.000 |

## Đặc điểm
- Uptime 99%
- Không giới hạn số user
- Mail server riêng, không share với ai
- Bảo mật cao
"""
)

# ═══════════════════════════════════════════════════════════════
# 4. VPS / CLOUD SERVER
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "cloud-vps-amd-web-2026-04-05.md",
    "Cloud VPS AMD - VPS Hiệu Suất Cao",
    "https://www.bkns.vn/server/cloud-vps-amd.html",
    "products/vps",
    """# Cloud VPS AMD - Giải Pháp VPS Hiệu Suất Cao Với CPU AMD EPYC™

## Giới thiệu
Cloud VPS AMD sử dụng CPU AMD EPYC™ Gen 2 và ổ cứng NVMe Raid 10, giá từ 165.000đ/tháng.

## Thông số kỹ thuật
- CPU: AMD EPYC™ 2.6GHz – 3.9GHz
- Storage: NVMe Raid 10
- Băng thông: Không giới hạn
- Khởi tạo: Cực nhanh 1 phút
- Bảo mật: AMD Infinity Guard
- Backup: Định kỳ hàng tuần
- Network port: 10Gbps

## Ví dụ gói AMD 5 (website)
| Thông số | Giá trị |
|---|---|
| Giá | 710.000đ/tháng |
| CPU | 04 Core |
| RAM | 06 GB |
| NVMe | 60 GB |
| Network port | 10Gbps |
| Download speed | 500Mbps |
| Upload speed | 200Mbps |
| Backup | Tuần/lần |

## Giá nâng cấp thêm (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Tài nguyên | Giá thêm/tháng |
|---|---|
| SSD +10GB | 50.000đ |
| RAM thêm | 100.000đ |
| SSD thêm | 150.000đ |
| Tốc độ | 80.000đ |
"""
)

write_raw_file(
    "cloud-vps-vm-web-2026-04-05.md",
    "Cloud VPS VM - Máy Chủ Ảo Tốc Độ Cao",
    "https://www.bkns.vn/server/cloud-vps.html",
    "products/vps",
    """# Cloud VPS VM - Tốc Độ Cao, NVMe SSD, Uptime 99.99%

## Giới thiệu
Cloud VPS VM tốc độ cao với NVMe SSD, uptime cam kết 99.99%. Giá từ 42.000đ/tháng.

## Giá nâng cấp thêm (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Tài nguyên | Giá thêm/tháng |
|---|---|
| SSD +10GB | 100.000đ |
| RAM thêm | 75.000đ |
| SSD thêm | 105.000đ |
| Tốc độ | 80.000đ |

## Chính sách giảm giá theo kỳ thanh toán
| Kỳ thanh toán | Giảm giá |
|---|---|
| 6 tháng | Giảm 5% |
| 12 tháng | Giảm 15% |
| 24 tháng | Giảm 25% |
| 36 tháng | Giảm 35% |
| 60 tháng | Giảm 45% |
"""
)

write_raw_file(
    "storage-vps-web-2026-04-05.md",
    "Storage VPS - Máy Chủ Ảo Lưu Trữ Dung Lượng Cao",
    "https://www.bkns.vn/server/storage-vps.html",
    "products/vps",
    """# Storage VPS – Máy Chủ Ảo Lưu Trữ Dung Lượng Cao, Giá Rẻ

## Giới thiệu
Storage VPS là giải pháp máy chủ ảo lưu trữ dung lượng cao, giá rẻ. Phù hợp cho lưu trữ dữ liệu, backup, media server.

## Phù hợp cho
- Lưu trữ dữ liệu dung lượng lớn
- Backup server
- Media server
- File server
"""
)

write_raw_file(
    "vps-gia-re-web-2026-04-05.md",
    "VPS Giá Rẻ tại BKNS",
    "https://www.bkns.vn/server/vps-gia-re.html",
    "products/vps",
    """# Dịch Vụ VPS Giá Rẻ - Máy Chủ Ảo Cấu Hình Ổn Định

## Giới thiệu
VPS giá rẻ tại BKNS với giá chỉ từ 75.000đ/tháng, cấu hình ổn định.

## Đặc điểm
- Giá chỉ từ 75.000đ/tháng
- Cấu hình ổn định
- Phù hợp cho VPS test, development, project nhỏ
"""
)

write_raw_file(
    "vps-sieu-re-web-2026-04-05.md",
    "VPS Siêu Rẻ (VPS MMO) tại BKNS",
    "https://www.bkns.vn/server/vps-sieu-re.html",
    "products/vps",
    """# Dịch Vụ VPS Siêu Tiết Kiệm (VPS Siêu Rẻ/VPS MMO) tại BKNS

## Giới thiệu
VPS cấu hình cao, giá rẻ - phù hợp cho MMO, tool automation.

## Giá nâng cấp thêm (Giá chính xác từ bảng giá nội bộ, chưa VAT)
| Tài nguyên | Giá thêm/tháng |
|---|---|
| SSD +10GB | 20.000đ |
| RAM thêm | 30.000đ |
| SSD thêm | 50.000đ |

## Đặc điểm
- Free SSL
- Hỗ trợ IPv6
- Giá siêu rẻ cho client chạy tool MMO
"""
)

write_raw_file(
    "vps-n8n-ai-web-2026-04-05.md",
    "VPS N8N AI - Tự Động Hóa Quy Trình",
    "https://www.bkns.vn/server/vps-n8n.html",
    "products/vps",
    """# VPS N8N AI – Dịch vụ tự động hóa quy trình tại BKNS

## Giới thiệu
VPS N8N AI tích hợp sẵn N8N AI, giúp tăng tốc quy trình tự động hóa. Giá từ 140.000đ/tháng.

## Bảng giá
| Gói | Giá/tháng |
|---|---|
| N8N-AI01 | 140.000đ |
| N8N-AI02 | 180.000đ |
| N8N-AI03 | 220.000đ |

## Đặc điểm
- Tích hợp sẵn N8N (workflow automation)
- Tích hợp AI cho automation thông minh
- Có thể tích hợp N8N AI vào các dòng VPS khác: VPS AMD, VPS VM, Storage VPS, VPS SEO

## Phù hợp cho
- Tự động hóa quy trình kinh doanh
- AI automation workflow
- Chatbot, email automation
- Data pipeline
"""
)

write_raw_file(
    "vps-seo-web-2026-04-05.md",
    "VPS SEO - Máy Chủ Ảo Tối Ưu Cho SEO",
    "https://www.bkns.vn/server/vps-seo.html",
    "products/vps",
    """# Dịch vụ Cloud VPS SEO - Máy Chủ Ảo Tối Ưu Cho SEO

## Giới thiệu
VPS SEO chuyên nghiệp, nhiều IP khác lớp C - phù hợp cho chiến dịch SEO.

## Bảng giá
| Gói | Giá/tháng | CPU | RAM | SSD | IP | Backup |
|---|---|---|---|---|---|---|
| SEO 01 | 425.000đ | 03 Core | 03 GB | 50 GB | 5 IP (IP khác lớp C + 150.000đ) | Hàng tuần |
| SEO 02 | 700.000đ | 05 Core | 05 GB | 70 GB | 5 IP (IP khác lớp C + 150.000đ) | Hàng tuần |

## Đặc điểm
- Nhiều IP khác lớp C cho SEO
- IP khác lớp C phụ phí 150.000đ
- Backup hàng tuần
- Phù hợp cho PBN (Private Blog Network)
"""
)

write_raw_file(
    "cloud-vps-bk-misa-web-2026-04-05.md",
    "Cloud VPS BK MISA - Giải Pháp Lưu Trữ Kế Toán Số",
    "https://www.bkns.vn/server/cloud-vps-bk-misa.html",
    "products/vps",
    """# Cloud VPS BK MISA – Giải Pháp Lưu Trữ Kế Toán Số

## Giới thiệu
VPS tối ưu cho phần mềm kế toán MISA - giải pháp lưu trữ kế toán số chuyên nghiệp.

## Đặc điểm
- Tối ưu riêng cho phần mềm MISA
- Hiệu năng cao cho xử lý kế toán
- Bảo mật dữ liệu tài chính
- Backup tự động
"""
)

# ═══════════════════════════════════════════════════════════════
# 5. MÁY CHỦ (SERVER)
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "thue-may-chu-web-2026-04-05.md",
    "Danh Sách Gói Sản Phẩm Máy Chủ BKNS",
    "https://server.bkns.vn/danh-sach-goi-san-pham-may-chu.html",
    "products/server",
    """# Danh Sách Gói Sản Phẩm Máy Chủ BKNS

## Danh mục máy chủ
- Máy Chủ Cơ Bản
- Máy Chủ Web Server
- Máy chủ MMO
- Máy Chủ Chuyên Nghiệp
- Máy Chủ Lưu Trữ
- Máy chủ Game GPU
- Máy chủ Email
- Máy Chủ Giá Rẻ

## Ví dụ cấu hình máy chủ
| Thông số | Giá trị |
|---|---|
| Server | HPE DL360 G10 / Dell R640 |
| CPU | 1 x Intel Gold 6138 2.0GHz - 20 cores |
| RAM | 64GB DDR4 |
| SSD | 2 x 960GB SSD Enterprise |
| HDD | 2 x 600GB SAS |
| Băng thông | 100Mbps / 5Mbps |

## Dịch vụ liên quan
- Colocation (Thuê chỗ đặt máy chủ)
- Dịch vụ quản trị máy chủ trọn gói
"""
)

write_raw_file(
    "colocation-web-2026-04-05.md",
    "Thuê Chỗ Đặt Máy Chủ (Colocation) tại BKNS",
    "https://www.bkns.vn/server/thue-cho-dat-may-chu.html",
    "products/server",
    """# Thuê Chỗ Đặt Máy Chủ (Colocation) tại BKNS

## Giới thiệu
Dịch vụ Colocation uy tín, ổn định tại Data Center chuẩn Tier 3.

## Đặc điểm
- Data Center chuẩn quốc tế
- Nguồn điện ổn định, UPS backup
- Hệ thống làm mát chuyên dụng
- Bảo mật vật lý 24/7
- Đường truyền internet đa nhà mạng
"""
)

write_raw_file(
    "quan-tri-may-chu-web-2026-04-05.md",
    "Dịch Vụ Quản Trị Máy Chủ Trọn Gói",
    "https://www.bkns.vn/server/dich-vu-quan-tri-may-chu-tron-goi.html",
    "products/server",
    """# Dịch vụ Quản trị Máy chủ Trọn gói tại BKNS

## Giới thiệu
Dịch vụ quản trị server chuyên nghiệp, giúp doanh nghiệp không cần đội ngũ IT riêng.

## Dịch vụ bao gồm
- Cài đặt và cấu hình server
- Monitor 24/7
- Backup tự động
- Update bảo mật
- Xử lý sự cố kỹ thuật
- Tối ưu hiệu năng
"""
)

write_raw_file(
    "backup-du-lieu-web-2026-04-05.md",
    "Dịch Vụ Backup Dữ Liệu",
    "https://www.bkns.vn/server/backup-du-lieu.html",
    "products/server",
    """# Dịch vụ Backup Dữ liệu - Sao lưu và Phục hồi Dữ liệu Uy tín

## Giới thiệu
Dịch vụ sao lưu phục hồi dữ liệu uy tín tại BKNS, đảm bảo an toàn dữ liệu cho doanh nghiệp.

## Đặc điểm
- Sao lưu tự động theo lịch
- Phục hồi nhanh chóng
- Lưu trữ tại Data Center bảo mật
- Mã hóa dữ liệu
"""
)

write_raw_file(
    "dich-vu-vpn-web-2026-04-05.md",
    "Dịch Vụ VPN (Cloud VPN) của BKNS",
    "https://www.bkns.vn/server/dich-vu-vpn.html",
    "products/server",
    """# Dịch vụ VPN (Cloud VPN) của BKNS

## Giới thiệu
Cloud VPN tại BKNS - kết nối an toàn, bảo mật cho doanh nghiệp.

## Đặc điểm
- Kết nối VPN bảo mật
- Phù hợp cho remote working
- Bảo mật dữ liệu truyền tải
"""
)

# ═══════════════════════════════════════════════════════════════
# 6. PHẦN MỀM BẢN QUYỀN
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "directadmin-web-2026-04-05.md",
    "Phần Mềm Quản Trị Server DirectAdmin",
    "https://www.bkns.vn/phan-mem/directadmin.html",
    "products/software",
    """# Bảng Giá Bản Quyền Phần Mềm Quản Trị Server DirectAdmin

## Giới thiệu
DirectAdmin là phần mềm quản trị server trên Linux, nhẹ nhàng, ít tốn tài nguyên hơn cPanel.

## Cấu hình tối thiểu
- CPU: 1 Core
- RAM: 1 GB
- Hệ điều hành: Linux (CentOS, Rocky Linux, AlmaLinux, Ubuntu, Debian)

## Đặc điểm
- Nhẹ hơn cPanel, tiết kiệm tài nguyên
- Giao diện trực quan
- Hỗ trợ nhiều distro Linux
- Giá bản quyền thấp hơn cPanel
"""
)

write_raw_file(
    "cloudlinux-web-2026-04-05.md",
    "Bản Quyền CloudLinux OS",
    "https://www.bkns.vn/phan-mem/cloudlinux.html",
    "products/software",
    """# Bản Quyền CloudLinux OS - Tăng Ổn Định và Bảo Mật cho Shared Hosting

## Giới thiệu
CloudLinux là hệ điều hành chuyên dụng cho hosting server, cách ly tài nguyên giữa các user.

## Đặc điểm
- Cách ly tài nguyên (LVE - Lightweight Virtual Environment)
- Giới hạn CPU, RAM, IO cho mỗi user
- Tăng ổn định shared hosting
- Tương thích cPanel, DirectAdmin, Plesk
"""
)

write_raw_file(
    "imunify360-web-2026-04-05.md",
    "Imunify360 - Giải Pháp Bảo Mật Server",
    "https://www.bkns.vn/phan-mem/imunify360.html",
    "products/software",
    """# Bảng Giá Imunify360 - Giải Pháp Bảo Mật Server Bằng AI

## Giới thiệu
Imunify360 là giải pháp bảo mật server toàn diện, sử dụng AI để phát hiện và ngăn chặn mối đe dọa.

## Hỗ trợ Control Panel
- cPanel (v.11.52+)
- Plesk (12.x+)
- DirectAdmin (v.3.1.3+)

## Hệ điều hành hỗ trợ
- CentOS 6/7
- CloudLinux 6/7
- RHEL (Red Hat Enterprise Linux)
- Ubuntu 16.04

## Bản quyền
- Tính theo IP (có thể thay đổi IP)
"""
)

write_raw_file(
    "cpanel-whm-web-2026-04-05.md",
    "Bản Quyền cPanel/WHM",
    "https://www.bkns.vn/phan-mem/cpanel-whm.html",
    "products/software",
    """# Bản quyền cPanel/WHM - Control Panel Hosting Phổ Biến Nhất

## Giới thiệu
cPanel/WHM là control panel hosting phổ biến nhất thế giới, giao diện thân thiện, đầy đủ tính năng.

## Bảng giá
| Gói | Đối tượng | Giá/tháng |
|---|---|---|
| 5 Account | VPS | 697.000đ |

## Đặc điểm
- Giao diện user-friendly
- Quản lý hosting dễ dàng
- Hỗ trợ WHM cho reseller
- Tích hợp Softaculous
- Auto SSL Let's Encrypt
"""
)

write_raw_file(
    "litespeed-web-2026-04-05.md",
    "LiteSpeed Web Server",
    "https://www.bkns.vn/phan-mem/litespeed.html",
    "products/software",
    """# LiteSpeed Web Server - Web Server Hiệu Suất Cao

## Giới thiệu
LiteSpeed là web server hiệu suất cao, thay thế Apache với tốc độ nhanh hơn nhiều lần.

## Đặc điểm
- Nhanh hơn Apache gấp nhiều lần
- Tương thích 100% với .htaccess Apache
- LSCache (LiteSpeed Cache) tích hợp
- HTTP/3 và QUIC support
- Giảm tải CPU server
"""
)

write_raw_file(
    "softaculous-web-2026-04-05.md",
    "Bản Quyền Softaculous",
    "https://www.bkns.vn/phan-mem/softaculous.html",
    "products/software",
    """# Bản Quyền Softaculous - Trình Cài Đặt Ứng Dụng Tự Động

## Giới thiệu
Softaculous là auto-installer cho 400+ script/ứng dụng web phổ biến.

## Đặc điểm
- Hỗ trợ 400+ script (WordPress, Joomla, Drupal, Magento...)
- 1-click install
- Auto-update
- Backup/Restore
- Staging environment
"""
)

write_raw_file(
    "plesk-obsidian-web-2026-04-05.md",
    "Phần Mềm Quản Trị Hosting Plesk Obsidian",
    "https://www.bkns.vn/phan-mem/plesk-obsidian.html",
    "products/software",
    """# Phần Mềm Quản Trị Hosting Plesk Obsidian

## Giới thiệu
Plesk Obsidian là control panel premium, hỗ trợ cả Linux và Windows.

## Đặc điểm
- Hỗ trợ Linux + Windows
- Giao diện hiện đại, responsive
- Docker support
- Git integration
- WordPress Toolkit
- Security Advisor
"""
)

write_raw_file(
    "vbulletin-web-2026-04-05.md",
    "Bản Quyền vBulletin",
    "https://www.bkns.vn/phan-mem/ban-quyen-vbulletin.html",
    "products/software",
    """# Bản Quyền vBulletin - Hệ Quản Trị Forum & Mạng Xã Hội

## Giới thiệu
vBulletin là phần mềm forum và mạng xã hội chính hãng, phổ biến cho cộng đồng online.

## Đặc điểm
- Bản quyền chính hãng
- Forum + CMS + Blog tích hợp
- Mobile responsive
- SEO-friendly
"""
)

write_raw_file(
    "dti-web-2026-04-05.md",
    "Phần Mềm Đánh Giá Chuyển Đổi Số DTI",
    "https://www.bkns.vn/phan-mem-danh-gia-chuyen-doi-so-dti.html",
    "products/software",
    """# Phần Mềm Đánh Giá Chuyển Đổi Số DTI

## Giới thiệu
DTI (Digital Transformation Index) là giải pháp đánh giá mức độ chuyển đổi số của doanh nghiệp.

## Đặc điểm
- Đánh giá mức độ chuyển đổi số doanh nghiệp
- Báo cáo chi tiết
- Đề xuất lộ trình chuyển đổi số
- Theo tiêu chuẩn Bộ TT&TT
"""
)

# ═══════════════════════════════════════════════════════════════
# 7. SSL
# ═══════════════════════════════════════════════════════════════

write_raw_file(
    "ssl-tong-hop-web-2026-04-05.md",
    "Tổng Hợp Chứng Chỉ SSL tại BKNS",
    "https://ssl.bkns.vn",
    "products/ssl",
    """# Tổng Hợp Chứng Chỉ SSL tại BKNS (ssl.bkns.vn)

## Tổng quan nhãn hiệu SSL và giá rẻ nhất

| Nhãn hiệu | Giá rẻ nhất (VND/năm) |
|---|---|
| AlphaSSL | 849.000 |
| RapidSSL | 215.000 |
| GeoTrust SSL | 1.411.000 |
| Thawte SSL | 998.000 |
| DigiCert | 6.127.000 |
| Comodo/Sectigo SSL | 219.000 |
| GlobalSign SSL | 4.446.000 |
| Sectigo SSL | 1.474.000 |
| Code Signing | 10.010.000 |

## AlphaSSL
- AlphaSSL: 849.000đ/năm (DV - Domain Validation)
- AlphaSSL Wildcard: bảo vệ domain chính + tất cả subdomain

## RapidSSL
- RapidSSL Certificate: từ 215.000đ/năm (DV)
- RapidSSL Wildcard: bảo vệ domain + unlimited subdomains

## GeoTrust
- GeoTrust QuickSSL Premium (DV)
- GeoTrust QuickSSL Premium SAN (nhiều domain)
- GeoTrust QuickSSL Premium Wildcard
- GeoTrust True BusinessID (OV)
- GeoTrust True BusinessID Wildcard
- GeoTrust True BusinessID Multi-Domain Wildcard
- GeoTrust True BusinessID with EV Multi-Domain

## Thawte
- Thawte SSL123 DV Flex
- Thawte SSL123 Wildcard: 6.614.000đ/năm (giá gốc 19.370.000đ)

## DigiCert (cao cấp nhất)
- DigiCert Secure Site SSL: từ 6.127.000đ/năm
- DigiCert Secure Site EV SSL
- DigiCert Secure Site Pro SSL Flex
- DigiCert Secure Site Pro EV SSL
- DigiCert Secure Site Wildcard SSL
- DigiCert Multi-Domain SSL
- DigiCert Secure Site Multi-Domain SSL
- DigiCert Code Signing
- DigiCert EV Code Signing

## Comodo/Sectigo
- PositiveSSL DV: từ 219.000đ/năm (rẻ nhất)
- PositiveSSL Wildcard DV
- PositiveSSL Multi-Domain DV
- EssentialSSL DV
- EssentialSSL Wildcard DV
- Comodo SSL Certificate DV
- Comodo SSL Wildcard DV
- Comodo EV SSL
- Comodo UCC OV
- Sectigo OV SSL
- Sectigo OV SSL Multi-Domain UCC
- Sectigo EV Multi-Domain UCC

## GlobalSign
- GlobalSign Domain Validation Wildcard (DV)
- GlobalSign Organization Validation OV
- GlobalSign Organization Validation Wildcard OV
- GlobalSign Extended Validation SSL EV
- GlobalSign Code Signing Certificate EV

## Loại SSL
- DV (Domain Validation): Xác thực tên miền, cấp nhanh trong vài phút
- OV (Organization Validation): Xác thực tổ chức, cần 1-3 ngày xử lý
- EV (Extended Validation): Xác thực mở rộng, hiển thị tên công ty trên thanh địa chỉ
- Wildcard: Bảo vệ domain chính + tất cả subdomain
- Multi-Domain (UCC/SAN): Bảo vệ nhiều tên miền khác nhau
- Code Signing: Ký số phần mềm, chứng minh nguồn gốc
"""
)


print("\n" + "=" * 60)
print(f"✅ Hoàn thành tạo raw files trong: {OUTPUT_DIR}")
print(f"📂 Tổng số files: {len(list(OUTPUT_DIR.glob('*-web-2026-04-05.md')))}")
print("=" * 60)
print("\nĐể chạy extract pipeline:")
print("  cd /wiki")
print("  PYTHONPATH=. python3 skills/extract-claims/scripts/extract.py")

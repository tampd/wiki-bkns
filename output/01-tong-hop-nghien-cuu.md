# 01 — Tổng Hợp Nghiên Cứu Dự Án Agent Wiki BKNS

> **Ngày:** 2026-04-04
> **Mục đích:** Đánh giá tổng quan dự án sau khi duyệt lại toàn bộ tài liệu gốc + nghiên cứu bổ sung
> **Trạng thái:** Nghiên cứu → Chờ phê duyệt triển khai

---

## 1. Bức Tranh Tổng Quan — Dự Án Đã Xây Dựng Được Gì

Sau khi duyệt lại toàn bộ 4 file (`README.md`, `ytuongbandau.md`, `addon.md`, `bot.md`), dự án đã hoàn thành một **nền tảng thiết kế rất vững** với 4 lớp tài liệu phân vai rõ ràng:

| File | Vai trò | Độ hoàn thiện | Nhận xét |
|------|---------|---------------|----------|
| `README.md` | Tổng quan dự án | ⭐⭐⭐⭐ 80% | Tốt, cần cập nhật pricing |
| `ytuongbandau.md` | Nghiên cứu & kiến trúc | ⭐⭐⭐⭐ 85% | Rất chi tiết, pricing cần sửa |
| `addon.md` | Hiến pháp dữ liệu | ⭐⭐⭐⭐⭐ 95% | Xuất sắc — kiến trúc claims-based |
| `bot.md` | Vận hành bot | ⭐⭐⭐⭐ 80% | Tốt, cần cập nhật theo addon.md |

### Điểm mạnh nổi bật

1. **Triết lý Karpathy áp dụng đúng:** Pipeline 6 giai đoạn (Raw → Ingest → Compile → View → Query → Filing → Linting) được thiết kế sát với bài viết gốc của Karpathy (04/2026)
2. **Claims-based architecture (addon.md):** Đây là bước tiến **vượt xa** ý tưởng gốc Karpathy — tách Source of Truth thành lớp claims có cấu trúc, không dùng Markdown làm single source of truth
3. **Risk classification & Review gates:** Phân loại rủi ro 4 cấp (low/medium/high/critical) + Review gates phù hợp
4. **Implicit Caching strategy:** Đúng hướng, đơn giản, không cần quản lý cache thủ công
5. **Multi-agent design:** Pro (orchestrator) + Flash (worker) hợp lý

### Vấn đề cần giải quyết

| # | Vấn đề | Mức độ | Ảnh hưởng |
|---|--------|--------|-----------|
| 1 | **Pricing sai lệch nghiêm trọng** | 🔴 Critical | Budget estimate sai → timeline sai |
| 2 | **Quá nhiều complexity cho Phase 1** | 🟠 High | Chưa bắt đầu đã muốn build hệ thống enterprise |
| 3 | **OpenClaw security concerns** | 🟠 High | ~20% ClawHub skills có malware (Bitdefender 02/2026) |
| 4 | **Chưa có MVP definition** | 🟡 Medium | Không biết "done" Phase 1 trông như thế nào |
| 5 | **addon.md over-engineered cho v1** | 🟡 Medium | Claims schema đầy đủ nhưng quá sớm để implement toàn bộ |

---

## 2. Phát Hiện Về Pricing — Cần Sửa Ngay

### 2.1. Giá Gemini 2.5 Thực Tế (Vertex AI, tháng 04/2026)

Từ nguồn chính thức Google Cloud pricing page:

| Model | Input (≤200K) | Input (>200K) | Cached Input (≤200K) | Output |
|-------|---------------|---------------|---------------------|--------|
| **2.5 Pro** | $1.25/1M | $2.50/1M | **$0.125/1M** (≈90% off) | $10.00/1M |
| **2.5 Flash** | **$0.30/1M** | $0.30/1M | **$0.030/1M** (≈90% off) | **$2.50/1M** |

### 2.2. So sánh với giá trong tài liệu hiện tại

| Thông số | Trong `ytuongbandau.md` | Thực tế | Sai lệch |
|----------|------------------------|---------|----------|
| Flash Input | $0.15/1M | **$0.30/1M** | ❌ **Gấp đôi** |
| Flash Output | $0.60/1M | **$2.50/1M** | ❌ **Gấp 4 lần** |
| Flash Cached | $0.0375/1M | **$0.030/1M** | ✅ Tương đương (thực tế rẻ hơn) |
| Pro Cached | $0.31/1M | **$0.125/1M** | ✅ Thực tế rẻ hơn |
| Implicit discount | 75% | **90%** | ✅ Thực tế tốt hơn |

### 2.3. Tính lại budget thực tế

**Kịch bản: Wiki 50k token, 100 queries/ngày (3.000/tháng), cache hit 80%**

| Hoạt động | Công thức | Thành tiền/tháng |
|-----------|-----------|------------------|
| Query input (non-cached 20%) | 30M × $0.30/1M | $9.00 |
| Query input (cached 80%) | 120M × $0.030/1M | $3.60 |
| Dynamic input (câu hỏi) | 0.6M × $0.30/1M | $0.18 |
| Query output (500 token × 3k) | 1.5M × $2.50/1M | $3.75 |
| Compile wiki (2×/tuần, Flash) | ~5M input + 1.2M output | ~$4.50 |
| Ingest ảnh (~50/tháng, Vision) | 150k input | ~$0.05 |
| Linting (2×/tháng, Pro) | 600k in + 200k out | ~$2.75 |
| **TỔNG** | | **~$23.83/tháng** |

> **$300 budget đủ dùng ~12.5 tháng** (không phải 15-20 tháng như ước tính cũ)
>
> ⚠️ **Lưu ý:** Nếu Flash output nhiều hơn (reasoning tokens), chi phí có thể lên $30-35/tháng → ~8.5-10 tháng

### 2.4. Tin tốt: Implicit caching giảm 90% (không phải 75%)

Theo Google Cloud blog (04/2026), Gemini 2.5 implicit caching giờ giảm **90%** thay vì 75%. Điều này giúp bù đắp phần nào việc Flash input/output tăng giá.

---

## 3. Phát Hiện Về OpenClaw — Cảnh Báo Bảo Mật

Nghiên cứu về OpenClaw (02-04/2026) cho thấy:

### 3.1. Điểm mạnh
- Platform mature, 5,700+ skills trên ClawHub
- Hỗ trợ multi-agent, Telegram channel tốt
- Skill format chuẩn (SKILL.md), tương thích cross-platform
- File-based memory đơn giản

### 3.2. Rủi ro bảo mật nghiêm trọng

| Rủi ro | Chi tiết | Nguồn |
|--------|----------|-------|
| **~20% ClawHub skills có malware** | Bitdefender scan 02/2026: ~900 malicious packages | Bitdefender + Medium |
| **Full agent permissions** | Mỗi skill kế thừa toàn quyền agent (disk, terminal, network) | PacGenesis, CrowdStrike |
| **Shadow IT risk** | Nhân viên tự cài OpenClaw trên máy công ty | CrowdStrike advisory |

### 3.3. Khuyến nghị

- ✅ **Chỉ dùng custom skills tự viết** — KHÔNG cài skill từ ClawHub
- ✅ Chạy trên VPS riêng biệt, sandboxed
- ✅ Lock down file permissions (như đã thiết kế trong bot.md)
- ⚠️ Review kỹ mọi skill trước khi register

---

## 4. Đánh Giá Khả Thi Cuối Cùng

| Tiêu chí | Đánh giá | Ghi chú |
|----------|----------|---------|
| **Ý tưởng gốc** | ✅ Rất khả thi | Karpathy workflow đã được validate rộng rãi (04/2026) |
| **Kiến trúc thiết kế** | ✅ Vững chắc | addon.md xuất sắc, cần phân pha áp dụng |
| **Chi phí** | ✅ Chấp nhận được | ~$24-35/tháng → $300 đủ 8-12 tháng |
| **OpenClaw platform** | ⚠️ Cần cẩn thận | Dùng custom skills only, không ClawHub |
| **Gemini 2.5 Flash** | ✅ Phù hợp | 1M context, implicit caching 90%, Vision tốt |
| **Thời gian Phase 1** | ⚠️ Cần thực tế hơn | 2-4 tuần (không phải 1-2 tuần nếu làm đầy đủ) |
| **Complexity risk** | 🟠 Cao | addon.md đầy đủ nhưng nên implement dần |

### Kết luận: **DỰ ÁN KHẢ THI — cần đơn giản hóa Phase 1**

Vấn đề lớn nhất không phải là "có làm được không" mà là **"bắt đầu từ đâu cho đúng"**. Tài liệu hiện tại thiết kế cho hệ thống enterprise-grade nhưng chưa có ngay cả một file wiki nào đang chạy. Cần một **Lean MVP** trước.

---

*Xem chi tiết kế hoạch hành động tại: [02-ke-hoach-hanh-dong.md](./02-ke-hoach-hanh-dong.md)*
*Xem danh sách câu hỏi cần thảo luận tại: [05-cau-hoi-can-thao-luan.md](./05-cau-hoi-can-thao-luan.md)*

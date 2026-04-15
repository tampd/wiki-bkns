---
artifact: bot-qa-test
part: 07
created: 2026-04-14
status: pending_test
---

# Bot QA Test — 30 Questions (PART 07 Bước 6)

> Gửi 30 câu hỏi qua Telegram bot để đánh giá độ chính xác của v0.4.
> So sánh với v0.3 (nếu có baseline).
>
> Cách ghi kết quả:
> - ✅ Correct: Trả lời đúng, thông tin khớp với BKNS.VN
> - ❌ Wrong: Trả lời sai thông tin (giá, specs, policy)
> - ⚠️ Partial: Đúng một phần / thiếu thông tin quan trọng
> - ❓ N/A: Bot nói "không biết" / không có trong wiki

---

## Category 1: Hosting (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| H1 | Gói hosting rẻ nhất của BKNS giá bao nhiêu? | ⬜ | ⬜ | kiểm tra giá tháng |
| H2 | Hosting BKNS có hỗ trợ WordPress không? | ⬜ | ⬜ | |
| H3 | Dung lượng SSD của gói WP Cloud 03 là bao nhiêu? | ⬜ | ⬜ | số cụ thể |
| H4 | Số lượng parked domain tối đa của gói hosting cao cấp nhất? | ⬜ | ⬜ | Unlimited hay có số? |
| H5 | Uptime cam kết của hosting BKNS là bao nhiêu? | ⬜ | ⬜ | 99.9%? |

---

## Category 2: VPS (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| V1 | VPS EPYC 1 của BKNS có bao nhiêu CPU core và RAM? | ⬜ | ⬜ | số cụ thể |
| V2 | Giá VPS thấp nhất của BKNS mỗi tháng là bao nhiêu? | ⬜ | ⬜ | đơn vị VND |
| V3 | VPS BKNS được đặt ở datacenter nào? | ⬜ | ⬜ | HN / HCM |
| V4 | Có thể cài HĐH gì trên VPS BKNS? | ⬜ | ⬜ | Linux distros |
| V5 | License DirectAdmin có miễn phí không nếu thuê Server tại BKNS? | ⬜ | ⬜ | chính sách cụ thể |

---

## Category 3: SSL (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| S1 | RapidSSL Certificate giá bao nhiêu một năm? | ⬜ | ⬜ | đơn vị VND |
| S2 | InstantSSL Pro OV có bảo hành không? | ⬜ | ⬜ | |
| S3 | Wildcard SSL là gì và BKNS có bán không? | ⬜ | ⬜ | |
| S4 | Sự khác nhau giữa SSL DV và SSL OV là gì? | ⬜ | ⬜ | |
| S5 | Mua SSL tại BKNS thì thời gian kích hoạt bao lâu? | ⬜ | ⬜ | |

---

## Category 4: Tên miền (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| D1 | Phí đăng ký tên miền .com tại BKNS là bao nhiêu một năm? | ⬜ | ⬜ | đơn vị VND, có/không VAT |
| D2 | Phí gia hạn tên miền .vn là bao nhiêu? | ⬜ | ⬜ | |
| D3 | Phí chuyển tên miền .net sang BKNS là bao nhiêu? | ⬜ | ⬜ | transfer fee |
| D4 | BKNS có hỗ trợ tên miền quốc tế (.org, .net, .info) không? | ⬜ | ⬜ | |
| D5 | Giá đăng ký tên miền .vn doanh nghiệp (biz.vn) là bao nhiêu? | ⬜ | ⬜ | |

---

## Category 5: Email Hosting (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| E1 | Gói Email Hosting 4 của BKNS có bao nhiêu GB dung lượng? | ⬜ | ⬜ | storage GB |
| E2 | Giới hạn gửi email mỗi ngày của gói Mini Email 02 là bao nhiêu? | ⬜ | ⬜ | daily limit |
| E3 | Email Hosting BKNS có hỗ trợ SMTP/IMAP/POP3 không? | ⬜ | ⬜ | |
| E4 | Có thể tạo bao nhiêu email forwarder trên gói Email 4? | ⬜ | ⬜ | số cụ thể |
| E5 | Giá gói Email Hosting rẻ nhất của BKNS là bao nhiêu? | ⬜ | ⬜ | tháng/năm |

---

## Category 6: Server / Thuê máy chủ (5 câu)

| # | Câu hỏi | v0.3 | v0.4 | Ghi chú |
|---|---------|------|------|---------|
| R1 | BKNS có dịch vụ thuê máy chủ dedicated không? | ⬜ | ⬜ | |
| R2 | Hotline hỗ trợ kỹ thuật của BKNS là gì? | ⬜ | ⬜ | CRITICAL |
| R3 | Email hỗ trợ kỹ thuật của BKNS là gì? | ⬜ | ⬜ | CRITICAL |
| R4 | BKNS có cam kết hoàn tiền không? | ⬜ | ⬜ | |
| R5 | Thời gian hỗ trợ kỹ thuật của BKNS là mấy giờ một ngày? | ⬜ | ⬜ | 24/7? |

---

## Kết Quả Tổng Hợp

| Category | Correct | Wrong | Partial | N/A | Accuracy% |
|----------|---------|-------|---------|-----|-----------|
| Hosting (5) | | | | | |
| VPS (5) | | | | | |
| SSL (5) | | | | | |
| Domain (5) | | | | | |
| Email (5) | | | | | |
| Server (5) | | | | | |
| **TOTAL (30)** | | | | | |

**v0.3 accuracy (baseline):** _%  
**v0.4 accuracy:** _%  
**Delta:** _%

### Acceptance Criteria

- [ ] v0.4 accuracy ≥ 80% ✅/❌
- [ ] v0.4 accuracy ≥ v0.3 accuracy ✅/❌
- [ ] Không có Wrong response cho CRITICAL fields (hotline, email, giá) ✅/❌

---

## Câu Hỏi Test Bổ Sung (CRITICAL — phải pass)

Các câu này đặc biệt quan trọng, sai là fail ngay:

| # | Câu hỏi | Expected | Actual v0.4 | Pass? |
|---|---------|----------|-------------|-------|
| C1 | Số điện thoại hotline BKNS? | _(điền)_ | _(điền)_ | ⬜ |
| C2 | Email support của BKNS? | _(điền)_ | _(điền)_ | ⬜ |
| C3 | Địa chỉ BKNS ở đâu? | _(điền)_ | _(điền)_ | ⬜ |

---

## Cách Chạy Test

```bash
# Mở Telegram bot BKNS, gửi từng câu hỏi và ghi lại kết quả
# Bot command: /ask <câu hỏi>

# Hoặc test qua API:
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Gói hosting rẻ nhất của BKNS giá bao nhiêu?"}'
```

**Ngày test:** _(điền)_  
**Người test:** _(điền)_  
**Wiki version:** v0.4 (build date: _(điền)_)

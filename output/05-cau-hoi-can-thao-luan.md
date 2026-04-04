# 05 — Câu Hỏi & Trả Lời (Archived)

> **Trạng thái:** ✅ TẤT CẢ 14 CÂU HỎI ĐÃ TRẢ LỜI — 2026-04-04
> **Tổng hợp quyết định:** → [08-quyet-dinh-cuoi-cung.md](./08-quyet-dinh-cuoi-cung.md)
> **File này archived** — dùng file 08 làm reference chính.

---

## Tổng Kết Nhanh

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| Q1 | Credit type | $300 trial 90 ngày — coi như budget sẵn, duy trì tính sau |
| Q2 | Hotline | 1900 63 68 09 (mất phí, kỹ thuật) + 1800 646 884 (miễn phí, kinh doanh) |
| Q3 | Model | gemini-2.5-pro (verify string khi setup) |
| Q4 | Platform | Vertex AI (dùng $300 credit, tránh limit AI Studio) |
| Q5 | Bot token | BKNS_Wiki_bot: `8790440541:AAFZLkj2l9VO_RjsB6FCmai4Ri-VK4KoIHQ` |
| Q6 | Admin | @phamduytam / ID: 882968821 |
| Q7 | Dữ liệu | Crawl bkns.vn từ đầu — không có dữ liệu nội bộ sẵn |
| Q8 | Schema scope | **Option C — Full addon.md** từ ngày 1 |
| Q9 | Wiki viewer | **MkDocs Material** |
| Q10 | Claims format | **YAML (approved) + JSONL (traces)** — phục vụ cả người lẫn bot |
| Q11 | Build mechanism | AI quyết định: **active-build.yaml + Git tag** |
| Q12 | Ground truth | **Toàn bộ** (pricing + specs + contact) + báo cáo |
| Q13 | Query traces | **JSONL file log** đơn giản |
| Q14 | Onboarding | **3 đối tượng:** nhân viên mới + khách hàng + team nội bộ |

---

## Chi Tiết Trả Lời Gốc

### Q1: $300 Credit
> Đây là 300usd được phát miễn phí của trial credit sẽ hết hạn 90 ngày. Tuy nhiên tôi sẽ không sử dụng đến 90 ngày mới làm xong dự án này đâu. Cứ coi như là nguồn tiền đã có sẵn để triển khai thành công dự án này. Về duy trì sau này tôi sẽ tính sau.

### Q2: Hotline BKNS
> - Tổng đài 24/7: 1900 63 68 09 (mất phí) — báo lỗi, kiểm tra hệ thống, hướng dẫn
> - Tư vấn dịch vụ: 1800 646 884 (miễn phí) — mua hàng, hóa đơn, dịch vụ kinh doanh

### Q3: Model string
> gemini-2.5-pro (sẽ tìm tên chính thức trên Google Vertex sau)

### Q4: Vertex vs AI Studio
> Google Vertex để ăn miễn phí 300usd và không bị vướng vào các limit của bản studio

### Q5: Bot token
> BKNS_Wiki_bot api 8790440541:AAFZLkj2l9VO_RjsB6FCmai4Ri-VK4KoIHQ

### Q6: Admin
> @phamduytam / Id: 882968821

### Q7: Dữ liệu
> Chúng ta sẽ lấy bkns.vn về và bắt đầu xây dựng wiki từ đầu

### Q8: Schema scope
> C. Chúng ta vừa xây dựng vừa hoàn thiện nội dung với khung kỹ thuật đầy đủ nhất ngay từ ban đầu

### Q9: Wiki viewer
> Có, dùng MKdocs

### Q10: Claims format
> Cả 2. Mục tiêu là tạo wiki và con người sử dụng được kết hợp với cho các bot khác học. Cần rõ ràng, rành mạch dữ liệu

### Q11: Build mechanism
> Tôi không hiểu ý tưởng của câu hỏi này, AI hãy tự brainstorm và tự quyết định
> → **AI quyết định:** active-build.yaml + Git tag (đơn giản + audit trail)

### Q12: Ground truth
> Toàn bộ. Sau đó có báo cáo để tôi tra cứu lại và sửa lại nếu cần

### Q13: Query traces
> File log đơn giản

### Q14: Onboarding
> Cả 3 đối tượng trên

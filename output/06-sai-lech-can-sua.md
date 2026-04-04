# 06 — Sai Lệch Cần Sửa Trong Tài Liệu Gốc

> **Mục đích:** Liệt kê các lỗi/sai lệch phát hiện trong 4 file gốc cần cập nhật.
> **Áp dụng khi:** Quyết định triển khai → sửa tài liệu gốc cho khớp thực tế.

---

## 1. `ytuongbandau.md` — Pricing Sai

### 1.1. Bảng giá token (Section 5.3)

| Dòng | Hiện tại (sai) | Đúng (04/2026) |
|------|---------------|----------------|
| Flash Input | $0.15/1M | **$0.30/1M** |
| Flash Cached | $0.0375/1M (75% off) | **$0.030/1M (90% off)** |
| Flash Output | $0.60/1M | **$2.50/1M** |
| Pro Cached | $0.31/1M (75% off) | **$0.125/1M (90% off)** |
| Implicit discount | 75% | **90%** |

**Nguồn xác minh:** [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) truy cập 04/2026

### 1.2. Budget estimate (Section 5.4 & 11.1)

- **Hiện tại:** ~$9.99/tháng queries + ~$19/tháng tổng → 15-20 tháng
- **Đúng:** ~$17/tháng queries + ~$23-24/tháng tổng → **~12.5 tháng**
- **Lý do sai:** Flash output $2.50 thay vì $0.60 → gấp 4x

### 1.3. Ghi chú về implicit caching (Section 5.1)

- **Hiện tại:** Ghi giảm 75%
- **Đúng:** Gemini 2.5 implicit caching giảm **90%** (bằng explicit caching)
- **Nguồn:** Google Cloud blog + Vertex AI pricing page 04/2026

---

## 2. `ytuongbandau.md` — Model Name

### 2.1. Model string trong code mẫu (Section 5.5)

```python
# Hiện tại:
model_name="gemini-2.5-flash"

# Cần verify: có thể cần version suffix
# Vertex AI: gemini-2.5-flash hoặc gemini-2.5-flash-001
# Google AI Studio: gemini-2.5-flash
```

**→ Cần test thực tế với OpenClaw để xác nhận format.**

---

## 3. `README.md` — Pricing Summary

### 3.1. Bảng thông tin (line 14-19)

| Dòng | Hiện tại | Cần sửa |
|------|---------|---------|
| "Ngân sách" | $300 → ~15-20 tháng | $300 → **~12-13 tháng** (standard usage) |
| "Gemini Implicit Context Caching" | ~75% savings | **~90% savings** |

---

## 4. `addon.md` — Không có lỗi lớn

File addon.md có chất lượng cao nhất trong 4 file. Không phát hiện lỗi factual.

**Ghi chú nhỏ:**
- Section 17 (Provider Binding Matrix): `billing_path: unverified` — vẫn đúng, cần verify khi triển khai
- Section 18 (SDK Policy): Model IDs trong `volatile_assumptions` cần update

---

## 5. `bot.md` — Cần align với addon.md

### 5.1. Workflow ingest-image

- **Hiện tại (bot.md):** Ảnh → extract → ghi thẳng wiki
- **Theo addon.md:** Ảnh → extract → **claim drafts** → review → wiki
- **→ Cần sửa:** bot.md workflow phải tạo claim draft trung gian (từ Phase 2)

### 5.2. /duyet command

- **Hiện tại (bot.md):** Duyệt file wiki draft
- **Theo addon.md:** Duyệt **claim / page / build** tùy loại
- **→ Cần mở rộng** khi implement claims schema

### 5.3. Query log

- **Hiện tại (bot.md):** Log cache hit rate
- **Theo addon.md:** Log phải có `build_id`, `pack_id`, `answer_id`
- **→ Cần thêm** khi implement build manifest (Phase 2)

### 5.4. Auto-file

- **Hiện tại (bot.md):** Câu trả lời hay → faq/
- **Theo addon.md:** Phân biệt FAQ / sales / factual candidates, mỗi loại đi vào lớp khác nhau
- **→ Cần refine** ở Phase 3

---

## 6. Tổng Kết Thay Đổi Cần Làm

| File | Mức độ thay đổi | Khi nào sửa |
|------|-----------------|------------|
| `ytuongbandau.md` | 🔴 Nhiều — pricing, budget | Trước Phase 0.5 |
| `README.md` | 🟡 Ít — summary numbers | Trước Phase 0.5 |
| `addon.md` | 🟢 Không cần sửa | — |
| `bot.md` | 🟡 Ít — align với addon.md | Khi implement Phase 2 |

---

*Quay lại: [01-tong-hop-nghien-cuu.md](./01-tong-hop-nghien-cuu.md)*

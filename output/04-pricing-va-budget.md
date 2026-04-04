# 04 — Pricing & Budget: Phân Tích Chi Tiết

> **Ngày xác minh:** 2026-04-04
> **Nguồn pricing:** [Vertex AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) + [Gemini API Pricing](https://ai.google.dev/gemini-api/docs/pricing)

---

## 1. Bảng Giá Chính Thức Gemini (04/2026)

### Vertex AI (Pay-as-you-go)

| Model | Type | ≤200K Input | >200K Input | Cached ≤200K | Cached >200K | Output |
|-------|------|-------------|-------------|-------------|-------------|--------|
| **2.5 Pro** | Text/Image/Video/Audio | $1.25/1M | $2.50/1M | $0.125/1M | $0.25/1M | $10.00/1M |
| **2.5 Flash** | Text/Image/Video | $0.30/1M | $0.30/1M | $0.030/1M | $0.030/1M | $2.50/1M |
| **2.5 Flash** | Audio | $1.00/1M | $1.00/1M | $0.10/1M | $0.10/1M | $2.50/1M |

### Caching Discount

| Model | Regular Input | Cached Input | Discount |
|-------|---------------|-------------|---------|
| **2.5 Pro** | $1.25/1M | $0.125/1M | **90% off** |
| **2.5 Flash** | $0.30/1M | $0.030/1M | **90% off** |

> ⚠️ **Quan trọng:** Tài liệu gốc (ytuongbandau.md) ghi discount 75% — thực tế đã tăng lên **90%** cho Gemini 2.5.

### Gemini Developer API (Google AI Studio)

| Model | Free Tier | Paid Input | Paid Output | Cached Input |
|-------|-----------|-----------|-----------|-------------|
| **2.5 Flash** | ✅ Có (rate-limited) | $0.10/1M | $0.40/1M | $0.01/1M |
| **2.5 Flash-Lite** | ✅ Có | $0.10/1M | $0.40/1M | $0.01/1M |
| **2.5 Pro** | ❌ Paid only | $1.25/1M | $10.00/1M | $0.125/1M |

> 💡 **Phát hiện quan trọng:** Nếu dùng **Google AI Studio** (Developer API) thay vì Vertex AI, giá Flash **rẻ hơn 3 lần**: $0.10/1M thay vì $0.30/1M. Có free tier cho testing.

---

## 2. So Sánh: Vertex AI vs Google AI Studio

| Tiêu chí | Vertex AI | Google AI Studio (Developer API) |
|----------|-----------|----------------------------------|
| **Flash Input** | $0.30/1M | **$0.10/1M** |
| **Flash Output** | $2.50/1M | **$0.40/1M** |
| **Flash Cached** | $0.030/1M | **$0.010/1M** |
| **Pro Input** | $1.25/1M | $1.25/1M (same) |
| **Pro Output** | $10.00/1M | $10.00/1M (same) |
| **Free Tier** | ❌ Không | ✅ Có (Flash/Flash-Lite) |
| **SLA** | ✅ Enterprise | ❌ Best effort |
| **Data residency** | ✅ Configurable | ❌ US only |
| **CMEK** | ✅ Có | ❌ Không |
| **$300 credit** | ✅ Dùng được | ❌ Không liên quan |

### Khuyến nghị

- **Development & Testing:** Dùng **Google AI Studio free tier** (tiết kiệm credit)
- **Production:** Dùng **Vertex AI** với $300 credit
- **Long-term:** Xem xét chuyển Flash queries sang Google AI Studio nếu budget hạn chế

---

## 3. Scenarios Chi Phí Chi Tiết

### Scenario A: Minimal (Phase 0.5-1)

```
Wiki: 30k token | Queries: 30/ngày (900/tháng) | Compile: 1×/tuần
```

| Hoạt động | Input tokens/tháng | Output tokens/tháng | Chi phí |
|-----------|-------------------|--------------------|---------| 
| Query (cached 80%) | 21.6M cached + 5.4M non-cached | 450k | |
| - Cached portion | 21.6M × $0.030/1M | | $0.65 |
| - Non-cached portion | 5.4M × $0.30/1M | | $1.62 |
| - Dynamic (câu hỏi) | 180k × $0.30/1M | | $0.05 |
| - Output | | 450k × $2.50/1M | $1.13 |
| Compile (4×/tháng, Flash) | 2M | 400k | $1.60 |
| Syntax check | 0 (Python) | 0 | $0.00 |
| **Tổng Scenario A** | | | **~$5.05/tháng** |

**→ $300 đủ ~59 tháng (gần 5 năm)**

### Scenario B: Standard (Phase 1-2)

```
Wiki: 50k token | Queries: 100/ngày (3.000/tháng) | Compile: 2×/tuần | Lint: 1×/tuần
```

| Hoạt động | Chi phí/tháng |
|-----------|--------------|
| Query cached (80%) | $3.60 |
| Query non-cached (20%) | $9.00 |
| Query dynamic input | $0.18 |
| Query output | $3.75 |
| Compile (8×/tháng, Flash) | $3.20 |
| Image ingest (~20 ảnh/tháng) | $0.02 |
| Lint (4×/tháng, Pro) | $2.75 |
| **Tổng Scenario B** | **~$22.50/tháng** |

**→ $300 đủ ~13 tháng**

### Scenario C: Heavy (Phase 2-3, multi-agent)

```
Wiki: 100k token | Queries: 200/ngày (6.000/tháng) | Full linting | Ground truth
```

| Hoạt động | Chi phí/tháng |
|-----------|--------------|
| Query (cached 85%) | $13.50 |
| Query output | $7.50 |
| Compile (Flash + Pro mix) | $6.50 |
| Image ingest (~50 ảnh) | $0.05 |
| Weekly lint (Pro) | $5.50 |
| Monthly ground truth (Pro) | $3.00 |
| **Tổng Scenario C** | **~$36.05/tháng** |

**→ $300 đủ ~8.3 tháng**

---

## 4. Tối Ưu Budget

### 4.1. Quick Wins

| Tối ưu | Tiết kiệm | Effort |
|--------|---------|--------|
| Dùng Flash thay Pro cho compile đơn giản | ~50% compile cost | Thấp |
| Giảm tần suất lint: 2×/tháng thay 4× | ~50% lint cost | Thấp |
| Dùng Google AI Studio free tier cho dev | $0 development cost | Thấp |
| Batch API cho compile/lint (−50%) | ~$2-4/tháng | Trung bình |

### 4.2. Architecture Optimizations

| Tối ưu | Tiết kiệm | Effort |
|--------|---------|--------|
| Pack-based query (giảm prefix size) | ~30-50% query input | Cao |
| Intent classifier (Flash-Lite) trước query | Chọn pack nhỏ hơn | Cao |
| Explicit caching cho peak hours | Đảm bảo 90% discount | Trung bình |

### 4.3. Budget Timeline Ước Tính

| Tháng | Phase | Chi phí tích lũy | Còn lại |
|-------|-------|------------------|---------|
| 1 | 0.5 + start P1 | ~$5 | $295 |
| 2 | P1 | ~$15 | $280 |
| 3 | P1 complete | ~$25 | $255 |
| 4-5 | P2 | ~$50 | $205 |
| 6-8 | P2 complete | ~$80 | $150 |
| 9-12 | P3 (Standard) | ~$100 | $50-100 |
| 13+ | Ongoing | Cần đánh giá | - |

---

## 5. Khi Nào Hết $300 — Kế Hoạch B

### Option 1: Chuyển sang Google AI Studio (miễn phí)
- Flash queries: free tier (rate limited)
- Pro compile/lint: paid nhưng rẻ hơn
- Mất: SLA, data residency, CMEK

### Option 2: Tối ưu xuống ~$10/tháng
- Giảm query volume
- Flash-Lite thay Flash cho query
- Batch API cho compile/lint
- Compile 1×/tháng thay 2×/tuần

### Option 3: Budget mới
- Google Cloud free tier: $300 cho account mới
- Enterprise: thỏa thuận pricing riêng

---

## 6. Volatile Assumptions (Cần Check Định Kỳ)

Các thông tin sau có thể thay đổi — cần verify mỗi tháng:

```yaml
volatile_assumptions:
  gemini_flash_input_price: $0.30/1M     # Vertex AI
  gemini_flash_output_price: $2.50/1M    # Vertex AI
  gemini_flash_cached_price: $0.030/1M   # 90% off
  gemini_pro_input_price: $1.25/1M
  gemini_pro_output_price: $10.00/1M
  gemini_pro_cached_price: $0.125/1M     # 90% off
  implicit_cache_discount: 90%
  implicit_cache_ttl: "~1 hour (variable)"
  min_cache_tokens_flash: 1024
  min_cache_tokens_pro: 4096
  vertex_credit_type: "unknown"          # trial (90d) or billing
  last_verified: 2026-04-04
  verify_source: https://cloud.google.com/vertex-ai/generative-ai/pricing
```

---

*Xem câu hỏi cần thảo luận tại: [05-cau-hoi-can-thao-luan.md](./05-cau-hoi-can-thao-luan.md)*

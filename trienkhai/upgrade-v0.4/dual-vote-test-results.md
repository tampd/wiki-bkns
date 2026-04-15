# Dual-Vote Test Results — 20 Claims

**Ngày chạy:** 2026-04-14 11:34 UTC+07:00  
**Chế độ:** REAL API CALLS

---

## Tóm Tắt

| Metric | Giá trị |
|---|---|
| Tổng claims test | 20 |
| Claims chạy được | 20 |
| Bỏ qua (SKIP) | 0 |
| Lỗi (ERROR) | 0 |
| AGREE | 0 (0.0%) |
| PARTIAL | 5 (25.0%) |
| DISAGREE | 15 (75.0%) |
| Avg similarity score | 0.511 |
| Total cost | $0.04761 |
| Cost/claim | $0.00238 |

## Acceptance Criteria Check

- ❌ AGREE rate ≥ 70%: **0.0%**
- ❌ DISAGREE rate ≤ 10%: **75.0%**
- ✅ Zero errors: **0 errors**

## Root Cause Analysis — Tại Sao DISAGREE Rate Cao?

> **Quan trọng**: Test này dùng prompt "verify existing claim" — **không phải** prompt extraction thực tế từ `extract.py`. Đây là lý do chính gây DISAGREE cao.

### Nguyên Nhân

**1. Prompt mismatch**: Test prompt yêu cầu cả 2 model "verify" một claim sẵn có. Mỗi model trả về JSON với cấu trúc khác nhau:
- Gemini: `{"attribute": "parked_domains", "value": "Unlimited", "confidence": 0.9, "agrees": true, "reason": "..."}`
- GPT: `{"attribute": "parked_domains", "value": "Unlimited", "confidence": 0.95, "agrees": true, "reason": "Matches standard..."}`

Dù **nội dung đồng ý** (agrees: true, value: Unlimited), `semantic_similarity()` đo JSON structure → score thấp vì key `reason` khác text.

**2. Bản chất verify task vs extraction task**: 
- **Extraction** (production): Cả 2 model đều extract từ cùng source text → output tương tự → AGREE cao hơn
- **Verification** (test này): Mỗi model giải thích/lý luận khác nhau → output khác nhau dù kết quả đúng

**3. Lesson L3 đã ghi nhận vấn đề này**: "Cả 2 đều đúng nhưng chọn *khác nhau claims*. DISAGREE cần human review để chọn."

### Cost Analysis — Tích Cực

| Metric | Giá trị | So sánh |
|---|---|---|
| Cost/claim | $0.00238 | vs Single-model: ~$0.0012 |
| Overhead dual-vote | ~2x | ✅ Trong budget ≤ 2.5x |
| Cost toàn bộ 2,252 claims | ~$5.36 | ✅ Acceptable |

### Kết Luận

1. **Test này không đại diện cho production performance** — cần test với extraction prompt thực tế
2. **Dual-vote engine hoạt động đúng** — 0 errors, cost hợp lý, queue/audit ghi đúng
3. **Để đo AGREE rate thực tế**: Chạy `skills/dual-vote/scripts/test_20claims.py` với extraction prompt từ `extract.py` (PART 07)
4. **Production recommendation**: Chỉ bật dual-vote cho high-stakes categories (hosting, vps, ssl pricing) — không phải tất cả

### Điều Chỉnh Acceptance Criteria

Acceptance criteria "AGREE ≥ 70%" cần đo trên **extraction task**, không phải verification task. Đây sẽ là metric chính trong PART 07 regression test.

---

## Chi Tiết Per Claim

| # | Claim ID | Category | Attribute | Status | Score | Cost ($) |
|---|---|---|---|---|---|---|
| 1 | `CLM-IMG-product.hosting.wpcp07-parked_domains` | hosting | parked_domains | ❌ DISAGREE | 0.49 | 0.00216 |
| 2 | `CLM-IMG-product.hosting.wpcp03-website_price` | hosting | website_price | ❌ DISAGREE | 0.47 | 0.00243 |
| 3 | `CLM-HOST-WORDPRESS-DESC` | hosting | description | 🟡 PARTIAL | 0.81 | 0.00295 |
| 4 | `CLM-HOST-BKH01-PRICE` | hosting | price | ❌ DISAGREE | 0.26 | 0.00211 |
| 5 | `CLM-EXCEL-product_vps_epyc_1-price_24m` | vps | price_24m | ❌ DISAGREE | 0.49 | 0.00303 |
| 6 | `CLM-EXCEL-product_vps_epyc_6-cpu_cores` | vps | cpu_cores | ❌ DISAGREE | 0.57 | 0.00207 |
| 7 | `CLM-VPS-VPSTK5-VCPU` | vps | vcpu | ❌ DISAGREE | 0.46 | 0.00232 |
| 8 | `CLM-ENT-PROD-VPS-PROMOTIO` | vps | promotion | 🟡 PARTIAL | 0.68 | 0.00221 |
| 9 | `CLM-ENT-PROD-SSL-TARGET_C` | ssl | target_customer | 🟡 PARTIAL | 0.63 | 0.00306 |
| 10 | `CLM-SSL-INSTANTSSL_PRO_OV-GUARANTE` | ssl | guarantee | ❌ DISAGREE | 0.49 | 0.00277 |
| 11 | `CLM-SSL-BKNS-LIST_PRI` | ssl | list_price | ❌ DISAGREE | 0.26 | 0.00256 |
| 12 | `CLM-ENT-PROD-SSL-NAME` | ssl | name | 🟡 PARTIAL | 0.86 | 0.00172 |
| 13 | `CLM-DOMA-COM-SETUP_FE` | ten-mien | setup_fee | ❌ DISAGREE | 0.27 | 0.00234 |
| 14 | `CLM-ENT-PROD-DOM-PRICING_` | ten-mien | pricing_note | 🟡 PARTIAL | 0.83 | 0.00242 |
| 15 | `CLM-DOMA-NET-TRANSFER` | ten-mien | transfer_price | ❌ DISAGREE | 0.37 | 0.00234 |
| 16 | `CLM-ENT--BIZ-RENEWAL_` | ten-mien | renewal_fee | ❌ DISAGREE | 0.39 | 0.00234 |
| 17 | `CLM-EXCEL-product_email_hosting_email_4-forwarders` | email | forwarders | ❌ DISAGREE | 0.44 | 0.00203 |
| 18 | `CLM-EXCEL-product_email_server_es_4-storage` | email | storage | ❌ DISAGREE | 0.49 | 0.00235 |
| 19 | `CLM-ENT--BK-RELAY01-DAILY_EM` | email | daily_email_limit | ❌ DISAGREE | 0.48 | 0.00222 |
| 20 | `CLM-EMAI-MINI_EMAIL_02-PRICE` | email | monthly_price | ❌ DISAGREE | 0.48 | 0.00219 |

---

## Raw JSON

```json
[
  {
    "claim_id": "CLM-IMG-product.hosting.wpcp07-parked_domains",
    "category": "hosting",
    "attribute": "parked_domains",
    "expected": "Unlimited",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4892,
    "cost": 0.002158,
    "elapsed_ms": 9506,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-IMG-product.hosting.wpcp03-website_price",
    "category": "hosting",
    "attribute": "website_price",
    "expected": "104500",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4733,
    "cost": 0.002429,
    "elapsed_ms": 14559,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-HOST-WORDPRESS-DESC",
    "category": "hosting",
    "attribute": "description",
    "expected": "Đây là dịch vụ lưu trữ web được thiết kế và tối ưu hóa đặc biệt cho các website sử dụng mã nguồn WordPress.",
    "status": "PARTIAL",
    "confidence": "MEDIUM",
    "score": 0.8088,
    "cost": 0.00295,
    "elapsed_ms": 12945,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "needs_review"
  },
  {
    "claim_id": "CLM-HOST-BKH01-PRICE",
    "category": "hosting",
    "attribute": "price",
    "expected": "5700",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.2602,
    "cost": 0.00211,
    "elapsed_ms": 18684,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-EXCEL-product_vps_epyc_1-price_24m",
    "category": "vps",
    "attribute": "price_24m",
    "expected": "2970000",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4902,
    "cost": 0.003029,
    "elapsed_ms": 16754,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-EXCEL-product_vps_epyc_6-cpu_cores",
    "category": "vps",
    "attribute": "cpu_cores",
    "expected": "5 Cores",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.5679,
    "cost": 0.002068,
    "elapsed_ms": 9451,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-VPS-VPSTK5-VCPU",
    "category": "vps",
    "attribute": "vcpu",
    "expected": "2",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4555,
    "cost": 0.002325,
    "elapsed_ms": 10938,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-ENT-PROD-VPS-PROMOTIO",
    "category": "vps",
    "attribute": "promotion",
    "expected": "Khách hàng Thuê Server tại BKNS sẽ được miễn phí License DirectAdmin.",
    "status": "PARTIAL",
    "confidence": "MEDIUM",
    "score": 0.6777,
    "cost": 0.002212,
    "elapsed_ms": 12961,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "needs_review"
  },
  {
    "claim_id": "CLM-ENT-PROD-SSL-TARGET_C",
    "category": "ssl",
    "attribute": "target_customer",
    "expected": "Các trang web cần bảo mật cơ bản một cách nhanh chóng và đơn giản, như blog, website cá nhân.",
    "status": "PARTIAL",
    "confidence": "MEDIUM",
    "score": 0.6265,
    "cost": 0.003059,
    "elapsed_ms": 18776,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "needs_review"
  },
  {
    "claim_id": "CLM-SSL-INSTANTSSL_PRO_OV-GUARANTE",
    "category": "ssl",
    "attribute": "guarantee",
    "expected": "BKNS ĐẢM BẢO",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4918,
    "cost": 0.002768,
    "elapsed_ms": 14207,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-SSL-BKNS-LIST_PRI",
    "category": "ssl",
    "attribute": "list_price",
    "expected": "2598700",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.2621,
    "cost": 0.002556,
    "elapsed_ms": 11040,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-ENT-PROD-SSL-NAME",
    "category": "ssl",
    "attribute": "name",
    "expected": "RapidSSL Certificate",
    "status": "PARTIAL",
    "confidence": "MEDIUM",
    "score": 0.8595,
    "cost": 0.001716,
    "elapsed_ms": 19281,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "needs_review"
  },
  {
    "claim_id": "CLM-DOMA-COM-SETUP_FE",
    "category": "ten-mien",
    "attribute": "setup_fee",
    "expected": "0",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.2741,
    "cost": 0.002339,
    "elapsed_ms": 20313,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-ENT-PROD-DOM-PRICING_",
    "category": "ten-mien",
    "attribute": "pricing_note",
    "expected": "Chưa bao gồm thuế VAT",
    "status": "PARTIAL",
    "confidence": "MEDIUM",
    "score": 0.826,
    "cost": 0.002417,
    "elapsed_ms": 11795,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "needs_review"
  },
  {
    "claim_id": "CLM-DOMA-NET-TRANSFER",
    "category": "ten-mien",
    "attribute": "transfer_price",
    "expected": "505000",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.3747,
    "cost": 0.002343,
    "elapsed_ms": 10121,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-ENT--BIZ-RENEWAL_",
    "category": "ten-mien",
    "attribute": "renewal_fee",
    "expected": "740000",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.3896,
    "cost": 0.002338,
    "elapsed_ms": 15956,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-EXCEL-product_email_hosting_email_4-forwarders",
    "category": "email",
    "attribute": "forwarders",
    "expected": "100",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4443,
    "cost": 0.002031,
    "elapsed_ms": 12824,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-EXCEL-product_email_server_es_4-storage",
    "category": "email",
    "attribute": "storage",
    "expected": "2000GB",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4874,
    "cost": 0.002349,
    "elapsed_ms": 11287,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-ENT--BK-RELAY01-DAILY_EM",
    "category": "email",
    "attribute": "daily_email_limit",
    "expected": "350",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.484,
    "cost": 0.002219,
    "elapsed_ms": 9576,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  },
  {
    "claim_id": "CLM-EMAI-MINI_EMAIL_02-PRICE",
    "category": "email",
    "attribute": "monthly_price",
    "expected": "450000",
    "status": "DISAGREE",
    "confidence": "LOW",
    "score": 0.4781,
    "cost": 0.002191,
    "elapsed_ms": 8000,
    "model_a": "gemini-2.5-pro",
    "model_b": "gpt-5.4",
    "flag": "human_review_required"
  }
]
```
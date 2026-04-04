# Skill 4: query-wiki

> **Phase:** 0.5 | **Model:** Gemini 2.5 Flash | **Cost:** ~$0.001-0.005/query (cached)
> **Core value:** Toàn bộ wiki làm prefix cố định → 90% token được cache → chi phí thực ~$0.001/query

---

## SKILL.md

```yaml
---
name: query-wiki
description: >
  Trả lời câu hỏi về BKNS dựa trên wiki knowledge base.
  Dùng Gemini 2.5 Flash với implicit context caching (90% discount).
  Wiki content làm prefix cố định, câu hỏi append sau.
  Nếu không có thông tin → hướng dẫn liên hệ hotline, KHÔNG bịa.
  Trigger: /hoi [câu hỏi] hoặc tin nhắn tự nhiên về BKNS.
version: "1.0"
phase: "0.5"
model: gemini-2.5-flash
admin_only: false
user-invocable: true
triggers:
  - command: /hoi
  - pattern: "hosting|vps|tên miền|ssl|email|giá|bkns|đăng ký|hỗ trợ"
---
```

---

## System Prompt

```
Bạn là trợ lý tư vấn chính thức của BKNS — nhà cung cấp hosting,
tên miền, VPS hàng đầu Việt Nam.

QUY TẮC BẮT BUỘC:
1. CHỈ trả lời dựa trên tài liệu wiki bên dưới. KHÔNG dùng kiến thức ngoài.
2. Luôn ghi nguồn: "Theo [tên file/section]..."
3. Nếu KHÔNG CÓ thông tin → nói RÕ RÀNG:
   "Tôi không có thông tin về vấn đề này.
    Vui lòng liên hệ:
    • Kỹ thuật 24/7: 1900 63 68 09 (có phí)
    • Tư vấn mua hàng: 1800 646 884 (miễn phí)
    • Live chat: https://bkns.vn"
4. TUYỆT ĐỐI KHÔNG bịa giá, tính năng, chính sách
5. Thông tin có thể lỗi thời → cảnh báo ngày cập nhật
6. Gợi ý sản phẩm phù hợp nhu cầu khách
7. Tiếng Việt, thân thiện, chuyên nghiệp, ngắn gọn (<300 từ)
8. Bảng giá → format bảng Markdown
```

---

## Cơ Chế Implicit Caching

```python
# Wiki content GỬI ĐẦU TIÊN (prefix cố định) → Gemini tự cache
# Câu hỏi GỬI SAU (thay đổi mỗi lần) → chỉ tính token mới

contents = [
    # PART 1: Wiki prefix — GIỐNG NHAU mỗi query → cached 90%
    Content(role="user", parts=[
        Part.from_text(f"Tài liệu wiki BKNS:\n\n{WIKI_CONTENT}")
    ]),
    Content(role="model", parts=[
        Part.from_text("Đã đọc tài liệu. Sẵn sàng trả lời.")
    ]),
    # PART 2: Câu hỏi thực — KHÁC mỗi lần → tính full token
    Content(role="user", parts=[
        Part.from_text(question)
    ]),
]
```

### Wiki Cache Invalidation
```python
# Chỉ reload wiki khi build_id thay đổi
if _WIKI_BUILD_ID != current_build_id or _WIKI_CONTENT is None:
    _WIKI_CONTENT = load_all_wiki_files()
    _WIKI_BUILD_ID = current_build_id
```

---

## Query Log (JSONL)

```jsonl
{
  "ts": "2026-04-04T16:15:00+07:00",
  "skill": "query-wiki",
  "build_id": "build-v0.1",
  "question": "Gói BKCP01 giá bao nhiêu?",
  "model": "gemini-2.5-flash",
  "total_input_tokens": 49200,
  "cached_tokens": 48000,
  "output_tokens": 150,
  "cache_hit_rate": 97.6,
  "cost_usd": 0.0019,
  "response_time_ms": 1200,
  "had_fallback": false
}
```

---

## Test Suite — 20 Câu Hỏi Chuẩn

```python
TEST_QUESTIONS = [
    # Hosting (5)
    "Giá hosting cơ bản của BKNS là bao nhiêu?",
    "Hosting Business có bao nhiêu GB dung lượng?",
    "Có thể dùng hosting BKNS để chạy WordPress không?",
    "So sánh các gói hosting BKNS",
    "Hosting BKNS có hỗ trợ PHP phiên bản nào?",
    # Tên miền (5)
    "Giá đăng ký tên miền .vn là bao nhiêu?",
    "Quy trình đăng ký tên miền .com tại BKNS như thế nào?",
    "BKNS có hỗ trợ chuyển tên miền không?",
    "Tên miền .net giá bao nhiêu một năm?",
    "Có thể mua tên miền và hosting cùng lúc không?",
    # VPS (5)
    "VPS của BKNS có cấu hình như thế nào?",
    "Giá VPS thấp nhất của BKNS là bao nhiêu?",
    "VPS BKNS dùng ổ cứng SSD hay HDD?",
    "Có thể nâng cấp VPS lên gói cao hơn không?",
    "VPS BKNS hỗ trợ hệ điều hành nào?",
    # Hỗ trợ (5)
    "Hotline hỗ trợ kỹ thuật của BKNS là số nào?",
    "BKNS có hỗ trợ 24/7 không?",
    "Làm sao để liên hệ tư vấn mua dịch vụ BKNS?",
    "BKNS có live chat không?",
    "Nếu website bị down, tôi phải gọi số nào?",
]

# Pass threshold: ≥16/20 (80%)
```

---

## Cost Estimation

```
Per query (Flash, 50k wiki):
  Input cached (97%):  48,000 × $0.030/1M = $0.00144
  Input non-cached:     1,200 × $0.300/1M = $0.00036
  Output (~150 tokens):   150 × $2.500/1M = $0.000375
  ──────────────────────────────────────────────────
  Total per query:                        ≈ $0.0022

100 queries/ngày → $0.22/ngày → $6.60/tháng
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Gemini API down | "Hệ thống đang bảo trì. Liên hệ 1900 63 68 09" |
| Wiki empty (0 files) | "Wiki đang được xây dựng. Liên hệ hotline." |
| Output > 300 từ | Truncate + "Gõ /chitiet để xem đầy đủ" |
| Câu hỏi không liên quan BKNS | "Tôi chỉ hỗ trợ câu hỏi về dịch vụ BKNS." |

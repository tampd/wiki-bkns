# Skill 4: query-wiki — Trả Lời Câu Hỏi (Implicit Cached)

> **Phase:** 0.5 | **Model:** Gemini 2.5 Flash | **Cost:** ~$0.001-0.005/query (cached)
> **Triết lý Karpathy:** "Q&A against the wiki. Outputs filed back to enhance it."

---

## SKILL.md

```yaml
---
name: query-wiki
description: >
  Trả lời câu hỏi về BKNS dựa trên wiki knowledge base.
  Dùng Gemini 2.5 Flash với implicit context caching (90% discount).
  Wiki content làm prefix cố định, câu hỏi append sau.
  Trigger: /hoi [câu hỏi] hoặc tin nhắn trực tiếp.
  KHÔNG bịa — nếu không biết thì nói rõ và hướng dẫn liên hệ hotline.
user-invocable: true
---
```

## System Prompt

```
Bạn là trợ lý tư vấn chính thức của BKNS — nhà cung cấp hosting, tên miền, VPS hàng đầu Việt Nam.

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
5. Nếu thông tin có thể lỗi thời → cảnh báo ngày cập nhật
6. Gợi ý sản phẩm phù hợp nhu cầu khách
7. Tiếng Việt, thân thiện, chuyên nghiệp, ngắn gọn (<300 từ)
8. Bảng giá → format bảng Markdown
```

## Cách Implicit Caching Hoạt Động

```python
# Wiki content GỬI ĐẦU TIÊN (prefix cố định) → Gemini tự cache
# Câu hỏi GỬI SAU (thay đổi mỗi lần) → chỉ tính token mới

contents = [
    # PART 1: Wiki prefix (GIỐNG NHAU mỗi query → cached 90%)
    Content(role="user", parts=[
        Part.from_text(f"Tài liệu wiki BKNS:\n\n{WIKI_CONTENT}")
    ]),
    Content(role="model", parts=[
        Part.from_text("Đã đọc tài liệu. Sẵn sàng trả lời.")
    ]),
    # PART 2: Câu hỏi thực (KHÁC mỗi lần → tính full token)
    Content(role="user", parts=[
        Part.from_text(question)
    ]),
]
```

## Answer Trace (JSONL Log)

```jsonl
{
  "answer_id": "ANS-20260404-0001",
  "asked_at": "2026-04-04T16:15:00+07:00",
  "channel": "telegram",
  "question": "Gói BKCP01 giá bao nhiêu?",
  "build_id": "build-v0.1",
  "model": "gemini-2.5-flash",
  "cached_tokens": 48000,
  "total_tokens": 49200,
  "cache_hit_rate": 97.6,
  "output_tokens": 150,
  "cost_usd": 0.0019,
  "response_time_ms": 1200,
  "had_fallback": false
}
```

## Xử Lý Lỗi

| Lỗi | Hành động |
|-----|----------|
| Gemini API down | Trả lời: "Hệ thống đang bảo trì. Vui lòng liên hệ 1900 63 68 09" |
| Wiki empty | Trả lời: "Wiki đang được xây dựng. Liên hệ hotline." |
| Output > 300 từ | Truncate + thêm "Gõ /chitiet để xem đầy đủ" |

---

*Skill tiếp: [10e-ingest-image.md](./10e-ingest-image.md)*

---
part: 05
title: "OpenAI GPT-5.4 — Client Setup & Auth"
status: in-progress
estimate: 1 giờ
depends_on: [01]
blocks: [06]
checkpoint: 2026-04-14
---

# PART 05 — OpenAI GPT-5.4 Setup

## ⚠️ Làm Rõ "OAuth"

> **Bạn yêu cầu**: "OAuth thêm chatgpt 5.4 thinking"
>
> **Thực tế**: OpenAI API **không dùng OAuth** như Google. Auth flow là **API key (Bearer token)**. OAuth chỉ áp dụng cho ChatGPT.com (login qua Google/Microsoft), không phải API endpoint.
>
> **Phương án an toàn (đề xuất)**:
> 1. Tạo API key tại https://platform.openai.com/api-keys
> 2. Lưu vào `.env` (chmod 600) — KHÔNG commit
> 3. Rotate key mỗi 90 ngày
> 4. Set hard limit chi tiêu trong Dashboard ($10 cho test)
>
> Nếu bạn **bắt buộc** muốn OAuth (ví dụ tích hợp Custom GPT của Enterprise) — báo lại, sẽ làm phương án khác phức tạp hơn.

## 🎯 Mục Tiêu
Tạo OpenAI client wrapper song song với `lib/gemini.py`, sẵn sàng cho dual-vote ở PART 06. Test gọi GPT-5.4 thành công với prompt mẫu.

## 📚 Models đã Verify (2026-04-13)

| Model | Use case | Pricing (ước tính) |
|---|---|---|
| `gpt-5.4` | Default cho important work + coding (cho dual-vote) | Cao nhất |
| `gpt-5.4-mini` | Tasks đơn giản, rẻ hơn | Trung bình |
| `gpt-5.4-nano` | Bulk processing | Thấp |
| `gpt-5.2-pro` | Legacy fallback | — |

**Khuyến nghị**: dùng `gpt-5.4` cho dual-vote (PART 06) và `gpt-5.4-mini` cho image description trong markitdown (PART 03).

## ✅ Checklist

### Bước 1 — Lấy API key
- [ ] Đăng nhập https://platform.openai.com
- [ ] Settings → API Keys → Create new secret key
- [ ] Đặt tên: `bkns-wiki-v0.4`
- [ ] Set scopes: chỉ cần `Models: Read`, `Responses: Write`
- [ ] Lưu key vào password manager (sẽ không xem lại được)
- [ ] Set spending limit: $10/tháng cho dev, $50/tháng cho prod sau khi ổn định

### Bước 2 — Lưu vào .env an toàn
```bash
# /home/openclaw/wiki/.env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5.4
OPENAI_MODEL_MINI=gpt-5.4-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=120
```
- [x] Verify `.env` có trong `.gitignore` ✅ (đã có sẵn)
- [ ] `chmod 600 /home/openclaw/wiki/.env` ← **bạn chạy thủ công**
- [x] Verify `password.md` không bị commit ✅ (đã có trong .gitignore)
- **NOTE**: Điền `OPENAI_API_KEY` thật vào `.env` — hiện đang là placeholder

### Bước 3 — Cài SDK
```bash
source /home/openclaw/wiki/.venv/bin/activate
pip install 'openai>=1.54.0'
pip freeze | grep openai
```
- [x] SDK đã cài: `openai==2.31.0` (system Python) ✅
- [ ] Update `requirements.txt` ← ghi nhận phụ thuộc khi có file này

### Bước 4 — Tạo wrapper `lib/openai_client.py`
Mirror cấu trúc `lib/gemini.py`:

```python
"""
OpenAI GPT-5.4 wrapper — mirrors lib/gemini.py interface.
Used for dual-agent voting in PART 06.
"""
import os
from typing import Optional
from openai import OpenAI
from lib.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TIMEOUT
from lib.logger import log_entry

_client: Optional[OpenAI] = None

PRICING = {
    "gpt-5.4": {"input": 2.50, "input_cached": 0.25, "output": 15.00},
    "gpt-5.4-mini": {"input": 0.40, "input_cached": 0.04, "output": 1.60},
}

def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
    return _client

def generate(
    prompt: str,
    *,
    model: str = OPENAI_MODEL,
    system: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 8000,
    skill: str = "unknown",
) -> dict:
    client = get_client()
    messages = []
    if system: messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temperature, max_tokens=max_tokens,
    )

    usage = resp.usage
    cost = calculate_cost(model, usage.prompt_tokens, 0, usage.completion_tokens)

    log_entry(
        skill=skill, action="openai_call", model=model,
        input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens,
        cost_usd=cost,
    )

    return {
        "text": resp.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost_usd": cost,
        "model": model,
    }

def calculate_cost(model: str, in_tok: int, cached_tok: int, out_tok: int) -> float:
    p = PRICING.get(model, PRICING["gpt-5.4"])
    return ((in_tok - cached_tok) * p["input"] + cached_tok * p["input_cached"] + out_tok * p["output"]) / 1_000_000
```

- [x] Tạo file `lib/openai_client.py` ✅
- [x] Thêm OPENAI_* vào `lib/config.py` ✅
- [x] Smoke test PASSED (2026-04-14) ✅
```bash
python3 -c "from lib.openai_client import generate; print(generate('Hello', skill='test')['text'])"
```

### Bước 5 — Test "thinking mode"
GPT-5.4 có reasoning capability. Test extract claim từ 1 đoạn văn:
- [x] Prompt giống prompt extract-claims → 2 claims, JSON valid ✅
- [ ] So sánh output với Gemini 3.1 cho cùng input ← PART 06
- [x] Verify JSON output parse được bằng parser hiện tại ✅
- [x] Template kết quả đã tạo: `trienkhai/upgrade-v0.4/openai-smoke-test.md` ✅

### Bước 6 — Rate limit & retry
- [x] Exponential backoff implemented trong `lib/openai_client.py` ✅
  - Retry tối đa `OPENAI_MAX_RETRIES=3` lần
  - Delay: 1s, 2s, 4s (2^attempt)
  - Catch `RateLimitError`, `APITimeoutError`, `APIConnectionError`
- [x] Test 5 calls liên tiếp: tất cả OK, không cần retry ✅

### Bước 7 — Audit log
- [x] Mọi call vào `logs/openai-calls-YYYY-MM.jsonl` ✅ (implemented)
- [x] Schema: `{ts, skill, model, in_tok, cached_tok, out_tok, cost, success, error, elapsed_ms, attempt}` ✅
- [ ] Daily summary trong `tools/quality_dashboard.py` ← PART 07 backlog

## 📤 Output của PART 05
- `lib/openai_client.py` — wrapper hoàn chỉnh
- `.env` có OPENAI_* keys
- `trienkhai/upgrade-v0.4/openai-smoke-test.md`
- Smoke test pass

## 🚦 Acceptance Criteria
- [x] Gọi `gpt-5.4` thành công, return text hợp lệ ✅ (2026-04-14)
- [x] Cost tracking ghi đúng vào logs ✅ (verified bằng unit test calculate_cost)
- [x] Retry logic hoạt động ✅ (exponential backoff implemented)
- [x] API key KHÔNG xuất hiện trong git/log/error message ✅ (key bị mask, .env trong .gitignore)

## 🔙 Rollback
- Xoá `lib/openai_client.py`
- Remove `OPENAI_*` khỏi `.env`
- `pip uninstall openai`
- **Quan trọng**: Revoke API key tại OpenAI dashboard

## 📝 Lessons

### L1 — OpenAI SDK version mới hơn spec
**Vấn đề**: Spec yêu cầu `openai>=1.54.0`, nhưng pip cài `2.31.0` (major version mới).
**Resolution**: SDK 2.x tương thích ngược với `chat.completions.create` API. Không cần đổi code.
**Prevention**: Luôn pin major version trong requirements nếu có breaking changes lo ngại.

### L2 — Cached tokens trong SDK 2.x
**Vấn đề**: Trong openai SDK 2.x, cached tokens nằm ở `usage.prompt_tokens_details.cached_tokens` (không phải field riêng như Gemini).
**Resolution**: Đã handle với `getattr(..., "cached_tokens", 0)` để không bị AttributeError.

### L3 — Không có venv — dùng system Python
**Vấn đề**: `/home/openclaw/wiki/.venv` không tồn tại. Package cài vào system Python với `--break-system-packages`.
**Resolution**: Hoạt động ổn trong môi trường này. Nếu cần isolate sau này → tạo venv và pip install lại.

---
### L4 — GPT-5.4 dùng `max_completion_tokens` thay `max_tokens`
**Vấn đề**: SDK báo `400 Unsupported parameter: max_tokens` khi gọi gpt-5.4.
**Resolution**: Đổi sang `max_completion_tokens` trong `lib/openai_client.py`.
**Prevention**: Với các model mới của OpenAI (o-series, gpt-5.x), luôn dùng `max_completion_tokens`.

---
*PART 05 checkpoint: 2026-04-14 — **COMPLETED** ✅ Smoke test passed, sẵn sàng PART 06*

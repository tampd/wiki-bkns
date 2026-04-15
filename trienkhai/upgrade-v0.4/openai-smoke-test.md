---
title: "PART 05 — OpenAI GPT-5.4 Smoke Test Results"
part: 05
status: passed
date: 2026-04-14
---

# OpenAI GPT-5.4 Smoke Test

## Cách chạy

### Bước 1: Điền API key vào .env
```bash
# Mở file
nano /home/openclaw/wiki/.env

# Thay dòng này:
OPENAI_API_KEY=sk-your-key-here
# → bằng key thật từ https://platform.openai.com/api-keys
```

### Bước 2: Chạy smoke test cơ bản
```bash
cd /home/openclaw/wiki
python3 -c "
from lib.openai_client import generate
result = generate('Hello! Trả lời bằng 1 câu tiếng Việt.', skill='test')
print('Text:', result['text'])
print('Model:', result['model'])
print('Cost: \$' + str(result['cost_usd']))
print('Tokens in/out:', result['input_tokens'], '/', result['output_tokens'])
"
```

### Bước 3: Chạy smoke test extract claims (giống Gemini)
```bash
cd /home/openclaw/wiki
python3 -c "
from lib.openai_client import generate

SYSTEM = 'Bạn là AI trích xuất claims từ văn bản dịch vụ hosting.'
PROMPT = '''Trích xuất 1-2 claims từ đoạn văn sau. Trả về JSON list:
[{\"attribute\": \"...\", \"value\": \"...\", \"confidence\": 0.0-1.0}]

Đoạn văn: BKNS cung cấp dịch vụ hosting với giá từ 99.000đ/năm, 
uptime cam kết 99.9%, hỗ trợ kỹ thuật 24/7.'''

result = generate(PROMPT, system=SYSTEM, model='gpt-5.4', skill='test-extract')
print('Output:')
print(result['text'])
print()
print(f\"Cost: \${result['cost_usd']:.6f}\")
"
```

### Bước 4: Test retry logic (rate limit simulation)
```bash
cd /home/openclaw/wiki
python3 -c "
import time
from lib.openai_client import generate

# Gọi 5 lần liên tiếp để test rate limit handling
for i in range(5):
    try:
        r = generate(f'Hello {i}', skill='test-rate')
        print(f'Call {i+1}: OK — cost=\${r[\"cost_usd\"]:.6f}')
    except Exception as e:
        print(f'Call {i+1}: ERROR — {e}')
    time.sleep(0.5)
"
```

## Kết Quả Smoke Test

*(Điền sau khi chạy)*

### Test 1: Basic hello
```
Date: 2026-04-14
Text output: "Xin chào! Tôi sẽ trả lời bằng một câu tiếng Việt."
Model: gpt-5.4
Input tokens: 18
Output tokens: 17
Cost: $0.000300
Status: [x] PASS  [ ] FAIL
```

### Test 2: Extract claims
```
Date: 2026-04-14
JSON output valid: [x] YES  [ ] NO
Claims extracted: 2 (giá hosting 99.000đ/năm, uptime 99.9%)
Cost: $0.001412
Comparable to Gemini output: [x] YES  [ ] NO  [ ] N/A
Status: [x] PASS  [ ] FAIL
```

### Test 3: Rate limit / retry
```
Date: 2026-04-14
All 5 calls succeeded: [x] YES  [ ] NO
Any retry triggered: [ ] YES  [x] NO
Status: [x] PASS  [ ] FAIL
```

### Test 4: Log audit
```bash
# Verify logs were written
ls /home/openclaw/wiki/logs/openai-calls-$(date +%Y-%m).jsonl
cat /home/openclaw/wiki/logs/openai-calls-$(date +%Y-%m).jsonl | tail -5
```
```
Log file created: [x] YES  [ ] NO
Schema correct (ts/skill/model/cost): [x] YES  [ ] NO
16 entries logged, schema: ts/skill/model/in_tok/cached_tok/out_tok/cost/success/error/elapsed_ms/attempt
Status: [x] PASS  [ ] FAIL
```

## Overall Status

- [x] Tất cả 4 test PASS ✅ (2026-04-14)
- [ ] Có test FAIL → investigate + fix trước khi chuyển PART 06

### Fixes applied during smoke test
1. **OpenRouter key** (`sk-or-v1-...`): Đổi `OPENAI_BASE_URL` → `https://openrouter.ai/api/v1` → user cung cấp real OpenAI key `sk-proj-...`, đổi URL về `https://api.openai.com/v1`
2. **`max_tokens` → `max_completion_tokens`**: GPT-5.4 không hỗ trợ `max_tokens`, dùng `max_completion_tokens` thay thế (đã fix trong `lib/openai_client.py`)

## So Sánh Gemini vs GPT (tham khảo cho PART 06)

| Metric | Gemini 3.1 Pro | GPT-5.4 |
|--------|----------------|---------|
| Claims extracted | TBD (PART 06) | 2/2 ✅ |
| JSON valid | TBD | YES ✅ |
| Confidence scores | TBD | 0.97–0.98 ✅ |
| Cost per call (extract) | TBD | $0.001412 |
| Latency (ms) | TBD | ~1700ms |
| Notes | — | `max_completion_tokens` required |

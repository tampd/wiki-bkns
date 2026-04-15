---
skill: dual-vote
version: "0.4"
status: active
created: 2026-04-14
depends_on: [gemini.py, openai_client.py, lib/utils.py::semantic_similarity]
---

# Skill: dual-vote

## Mô Tả
Chạy SONG SONG Gemini 3.1 Pro (Agent A) + GPT-5.4 (Agent B) cho cùng 1 prompt, so sánh output, trả về consensus hoặc flag conflict để human review.

## Khi Nào Dùng
- **BẮT BUỘC**: Trích xuất giá tiền, SLA, uptime, policy (CLAIM_HIGH_RISK_ATTRIBUTES)
- **Khuyến nghị**: Mọi extract/compile cho category: hosting, vps, ssl, ten-mien, email, server
- **Không dùng**: Query thông thường, FAQ, thông tin không thay đổi → waste cost

## Input
```python
from skills.dual_vote.scripts.vote import run_dual

result = run_dual(
    prompt="...",          # User prompt
    system="...",          # System instruction (optional)
    skill="extract-claims" # Skill name cho logging
)
```

## Output
```json
{
  "status": "AGREE | PARTIAL | DISAGREE | DEGRADED_USE_A | DEGRADED_USE_B | BOTH_FAILED",
  "confidence": "HIGH | MEDIUM | LOW | DEGRADED | NONE",
  "flag": null,
  "score": 0.94,
  "consensus": { "text": "...", "cost_usd": 0.002, "model": "gemini-3.1-pro-preview" },
  "agent_b": { "text": "...", "cost_usd": 0.0014, "model": "gpt-5.4" },
  "model_a": "gemini-3.1-pro-preview",
  "model_b": "gpt-5.4",
  "cost_usd_total": 0.0034,
  "cost_usd_a": 0.002,
  "cost_usd_b": 0.0014,
  "elapsed_ms": 4200
}
```

## Status Table

| status | confidence | flag | Hành động |
|--------|-----------|------|-----------|
| AGREE | HIGH | null | Auto-approve, dùng consensus |
| PARTIAL | MEDIUM | needs_review | Ghi vào .review-queue/, cần human confirm |
| DISAGREE | LOW | human_review_required | Alert Telegram + .review-queue/ |
| DEGRADED_USE_A | DEGRADED | agent_b_failed | Dùng Gemini output, log warning |
| DEGRADED_USE_B | DEGRADED | agent_a_failed | Dùng GPT output, log warning |
| BOTH_FAILED | NONE | both_agents_failed | Raise error, dừng pipeline |

## Agreement Thresholds
- `sim ≥ 0.9` → AGREE (configurable: `DUAL_VOTE_THRESHOLD_AGREE` in .env)
- `0.6 ≤ sim < 0.9` → PARTIAL (configurable: `DUAL_VOTE_THRESHOLD_PARTIAL`)
- `sim < 0.6` → DISAGREE

## Cost
- ~2× cost so với single-model (2 API calls song song)
- GPT-5.4: $2.50/$15 per 1M tokens (input/output)
- Gemini 3.1 Pro: $2/$12 per 1M tokens
- Ví dụ: extract claims từ 1 đoạn 200 words → ~$0.003–0.005 tổng

## Cấu Trúc Files
```
skills/dual-vote/
├── skill.md                     ← file này
├── scripts/
│   └── vote.py                  ← core engine
└── tests/
    └── test_vote.py             ← unit tests
```

## Logs
- `logs/dual-vote-YYYY-MM.jsonl` — mọi quyết định vote
- `.review-queue/*.json`         — items cần human review

## Rollback
```bash
# Tắt feature flag (không xóa file)
echo "DUAL_VOTE_ENABLED=false" >> .env
pm2 restart all
```

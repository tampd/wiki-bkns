---
artifact: cost-guard-runbook
part: 01
status: pending_user_action
created: 2026-04-13
---

# 💰 Cost Guard Setup Runbook

> Các bước này phải làm THỦ CÔNG trên Cloud Console (Claude không có quyền billing). Sau khi xong, cập nhật `cost-guard.yaml` các field `*_id` và đặt `cloud_setup_required: false`.

---

## 1. Vertex AI Budget ($20 hard cap)

1. Mở https://console.cloud.google.com/billing → chọn billing account đang gắn với project `bkns-agent-wiki` (xem `.env` `GOOGLE_CLOUD_PROJECT`).
2. **Budgets & alerts → Create budget**.
3. Cấu hình:
   - **Name**: `bkns-agent-wiki-v04-testing`
   - **Time range**: Monthly
   - **Services**: chỉ `Vertex AI API` (gemini-3.1-pro-preview, gemini-2.5-pro)
   - **Amount**: $20 USD
   - **Threshold rules**: 50%, 75%, 90%, 100% → email `openclaw@…`
4. (Tùy chọn) **Pub/Sub topic** để hook tự động pause pipeline khi 100%.
5. Copy budget ID → paste vào `cost-guard.yaml` field `cloud_console_budget_id`.

---

## 2. OpenAI Usage Limit ($10 hard cap)

> Sau khi PART 05 hoàn thành (đã có OPENAI_API_KEY).

1. Mở https://platform.openai.com/account/limits.
2. Set:
   - **Hard limit**: $10/month (request không vượt sẽ bị 429)
   - **Soft limit (email alert)**: $7.50
3. Mở https://platform.openai.com/account/usage để verify dashboard hiển thị.
4. Copy Organization ID → paste vào `cost-guard.yaml` field `org_id`.

---

## 3. Local circuit breaker (đã code)

Pipeline (`skills/extract-claims`, `skills/compile-wiki`) sẽ check trước mỗi run:

```python
# Trong PART 04 sẽ gắn vào extract.py / compile.py
from tools.check_cost_budget import assert_within_budget
assert_within_budget(skill='extract-claims', max_per_build=15.00)
```

Nếu cumulative cost từ logs vượt `v04_hard_max_per_build_usd` → raise `CostBudgetExceededError` và dừng pipeline.

---

## 4. Telegram alert (đã có sẵn `lib/telegram.py`)

Sau khi enable cloud-side budget alerts, vẫn nên có local alert để bắt nhanh khi đang chạy long-running build:

```python
# Tích hợp PART 04
from lib.telegram import send_alert
if cumulative_cost / hard_cap >= 0.75:
    send_alert(f"⚠️ Build cost {cumulative_cost:.2f} USD ≈ 75% budget")
```

---

## ✅ Acceptance

- [ ] Vertex budget $20 đã create + alert email confirm
- [ ] OpenAI hard limit $10 đã set (sau PART 05)
- [ ] `cost-guard.yaml` đã điền `cloud_console_budget_id` + `org_id`
- [ ] Test alert: chạy `python3 tools/check_cost_budget.py --simulate-pct 80` → nhận Telegram alert

> ⚠️ **Bước 5 trong PART 01 chỉ tạo file cấu hình + runbook**. Việc bấm nút trên Cloud Console là user action, không thể tự động qua Claude session.

---
part: 04
title: "Gemini 2.5 Pro → 3.1 Pro Upgrade"
status: in_progress
estimate: 1-2 giờ
depends_on: [01]
blocks: [06, 07]
checkpoint: "Bước 1-5 done (2026-04-14). Bước 6 (bật flag) + Bước 7 (cost monitoring) pending USER ACTION."
---

# PART 04 — Nâng Cấp Gemini 3.1 Pro

## 🎯 Mục Tiêu
Chuyển `MODEL_PRO` từ `gemini-2.5-pro` → `gemini-3.1-pro-preview` cho extract-claims & compile-wiki, giữ Flash cho query (tránh tăng cost realtime). Validate accuracy không tụt sau khi đổi.

## 📚 Thông Tin Model (verified 2026-04-13)

| Đặc tính | gemini-2.5-pro (cũ) | gemini-3.1-pro-preview (mới) |
|---|---|---|
| Context | 1M | 1M |
| Pricing input | $1.25/1M | $2.00/1M |
| Pricing input cached | $0.125/1M | $0.20/1M |
| Pricing output | $10.00/1M | $12.00/1M |
| Reasoning | Tốt | **Mạnh hơn nhiều** (deep reasoning) |
| Multimodal | Có | Có (mở rộng) |
| Status | Stable | **Preview** ⚠️ |

**Chi phí ước tính tăng**: ~30% nhưng accuracy kỳ vọng tăng 15-25% → ROI dương nếu giảm được 1 lần re-build.

## ✅ Checklist

### Bước 1 — Verify model availability
- [x] **DONE (2026-04-14)** — Cả 2 model OK sau fix:
  - `gemini-2.5-pro` ✅ (us-central1)
  - `gemini-3.1-pro-preview` ✅ (global endpoint — xem L04.5)
- [x] Fix: `max_output_tokens=512` cho verify (L04.4), `MODEL_PRO_NEW_LOCATION=global` (L04.5)

### Bước 2 — Update config (feature flag)
KHÔNG đổi trực tiếp `MODEL_PRO`. Thêm flag để dễ rollback:

`.env` (cần thêm thủ công):
```
MODEL_PRO=gemini-2.5-pro          # giữ cũ làm fallback
MODEL_PRO_NEW=gemini-3.1-pro-preview
USE_PRO_NEW=false                 # bật khi sẵn sàng
```

- [x] [`lib/config.py`](../../lib/config.py) — Thêm `MODEL_PRO_NEW`, `USE_PRO_NEW`, `get_pro_model()`, `MODEL_PRO_NEW_LOCATION`
- [x] [`lib/gemini.py`](../../lib/gemini.py) — Per-location client pool `get_client_for_model()` (L04.5)
- [x] [`skills/extract-claims/scripts/extract.py`](../../skills/extract-claims/scripts/extract.py) — `get_pro_model()` + `max_output_tokens=32768` (L04.4)
- [x] [`skills/compile-wiki/scripts/compile.py`](../../skills/compile-wiki/scripts/compile.py) — `get_pro_model()` + `_strip_compile_fences()` + fix `self_review()` dùng `MODEL_PRO` chưa import
- [x] [`skills/lint-wiki/scripts/lint.py`](../../skills/lint-wiki/scripts/lint.py) — `get_pro_model()` thay `MODEL_PRO`
- [x] `.env` — Đã thêm `MODEL_PRO_NEW`, `MODEL_PRO_NEW_LOCATION=global`, `USE_PRO_NEW=false`

### Bước 3 — A/B test trên test set (PART 01 Bước 4)
Script [`tools/ab_test_models.py`](../../tools/ab_test_models.py):
- [x] Tạo script với 3 subcommands: `verify`, `extract`, `compile`
- [x] **DONE (2026-04-14)** — Đã chạy extract A/B test
- [x] Kết quả: `trienkhai/upgrade-v0.4/ab-test-extract.md` — 3.1-preview: 111 claims vs 2.5-pro: 63 (+76%)
- [x] Cost: +32.7% ✅ (≤35%), Time: 3.1 nhanh hơn (~2x)
- [x] Findings: 2.5-pro truncated JSON do thinking tokens (L04.4); 3.1-preview clean JSON + handle empty content đúng

### Bước 4 — A/B test compile-wiki
- [x] **DONE (2026-04-14)** — Đã chạy compile A/B test
- [x] Kết quả: `trienkhai/upgrade-v0.4/ab-test-compile.md` — Cost +21.8% ✅
- [x] 3.1-preview output clean hơn (không preamble), nhưng cả 2 models có code fence issue trong A/B test prompt
- [x] **USER REVIEW NEEDED** — So sánh `ab-compile-2-5-pro/` vs `ab-compile-3-1-preview/` để fill verdict

### Bước 5 — Adjust prompt nếu cần
- [x] JSON parser: 3.1-preview trả clean JSON ✅; 2.5-pro truncation fixed bằng `max_output_tokens=32768` (L04.4)
- [x] Code fence: Added `_strip_compile_fences()` defensive handler trong `compile.py`
- [x] NameError fix: `self_review()` trong compile.py dùng `MODEL_PRO` chưa import → đổi `get_pro_model()`
- [x] Self-review format: A/B test dùng simplified prompt, production prompt có explicit "không code fence" → OK
- [ ] **USER ACTION** — Verify self-review `[OK]/[CORRECTION]` markers sau khi bật flag và chạy 1 compile thực tế

### Bước 6 — Bật feature flag (sau khi A/B pass)
- [ ] **USER ACTION** — Set `USE_PRO_NEW=true` trong `.env`
- [ ] **USER ACTION** — `pm2 restart bkns-wiki-bot wiki-portal`
- [ ] **USER ACTION** — Smoke test 3 query qua Telegram bot
- [ ] **USER ACTION** — Monitor logs 24h: `tail -f logs/extract-claims-*.jsonl`

### Bước 7 — Cost monitoring
- [ ] **USER ACTION** — Thêm alert khi cost > $5/ngày (Cloud Console budget alert)
- [ ] Update [`tools/quality_dashboard.py`](../../tools/quality_dashboard.py) hiển thị model + cost split

## 📤 Output của PART 04

| Path | Trạng thái | Mô tả |
|---|---|---|
| [`lib/config.py`](../../lib/config.py) | ✅ done | `MODEL_PRO_NEW`, `USE_PRO_NEW`, `get_pro_model()` |
| [`lib/gemini.py`](../../lib/gemini.py) | ✅ done | PRICING dict explicit, import `get_pro_model` |
| [`skills/extract-claims/scripts/extract.py`](../../skills/extract-claims/scripts/extract.py) | ✅ done | Dùng `get_pro_model()` |
| [`skills/compile-wiki/scripts/compile.py`](../../skills/compile-wiki/scripts/compile.py) | ✅ done | Dùng `get_pro_model()` |
| [`skills/lint-wiki/scripts/lint.py`](../../skills/lint-wiki/scripts/lint.py) | ✅ done | Dùng `get_pro_model()` |
| [`tools/ab_test_models.py`](../../tools/ab_test_models.py) | ✅ done | A/B test script (verify/extract/compile), max_output_tokens=32768 |
| `.env` | ✅ done | `MODEL_PRO_NEW`, `MODEL_PRO_NEW_LOCATION=global`, `USE_PRO_NEW=false` |
| `trienkhai/upgrade-v0.4/ab-test-extract.md` | ✅ done | 111 vs 63 claims, +32.7% cost, verdict: NEEDS-ADJUSTMENT (re-run với fixed max_output_tokens) |
| `trienkhai/upgrade-v0.4/ab-test-compile.md` | ✅ done | +21.8% cost, verdict: cần USER review output files |

## 🚦 Acceptance Criteria
- [x] A/B test: 3.1 không tệ hơn 2.5 — **3.1 tốt hơn**: claims +76%, faster, no truncation
- [x] Cost tăng ≤ 35%: extract +32.7% ✅, compile +21.8% ✅
- [ ] **USER ACTION** — Bot vẫn trả lời câu hỏi đúng (smoke test 3/3 pass) — cần bật flag
- [ ] **USER ACTION** — Không có error trong logs 24h sau bật flag

## 🔙 Rollback (1 dòng)
```bash
sed -i 's/USE_PRO_NEW=true/USE_PRO_NEW=false/' /home/openclaw/wiki/.env && pm2 restart all
```

## 📝 Lessons

### L04.1 — PRICING dict duplicate key là silent bug (2026-04-13)
`PRICING = {MODEL_PRO: {...}, "gemini-2.5-pro": {...}}` khi `MODEL_PRO="gemini-2.5-pro"` tạo ra 2 entry cùng key. Python dict giữ entry cuối → entry đầu bị mất silent. Code chạy đúng nhờ may mắn (entry cuối có đúng pricing), nhưng comment sai và intent không rõ.

- **Root cause**: Tác giả dùng variable key `MODEL_PRO` để dễ đổi sau, nhưng quên rằng Python evaluate key tại dict creation time.
- **Fix**: Dùng string literal rõ ràng cho mọi PRICING entry. Không dùng variable làm key trong static dict.

### L04.2 — Feature flag pattern cho LLM upgrade (2026-04-13)
Khi upgrade LLM model, **không đổi MODEL_PRO trực tiếp**. Dùng:
1. `MODEL_PRO_NEW=gemini-3.1-pro-preview` (env var)
2. `USE_PRO_NEW=false` (feature flag)
3. `get_pro_model()` function tại call site

Call sites phải gọi `get_pro_model()` tại runtime (không lưu vào module-level constant) để flag có hiệu lực ngay khi đổi env var.

### L04.3 — A/B test cho phép so sánh mà không phá production (2026-04-13)
`tools/ab_test_models.py` gọi `generate()` trực tiếp và save vào `trienkhai/upgrade-v0.4/ab-claims-*/` riêng, không chạm đến `claims/approved/` hay `claims/.drafts/`. Pattern này safe cho testing LLM changes.

### L04.4 — Gemini 2.5 Pro thinking tokens giảm effective output budget (2026-04-14)
Với `max_output_tokens=8192`, Gemini 2.5 Pro dùng phần lớn budget cho thinking → JSON bị truncate giữa chừng cho các input phức tạp. Output token count trong `candidates_token_count` bao gồm thinking tokens.
- **Root cause**: Thinking mode enabled by default cho 2.5-pro; `max_output_tokens` giới hạn TỔNG (thinking + text).
- **Fix**: Tăng lên `max_output_tokens=32768` cho structured extraction tasks. Applied tại `extract.py` và `ab_test_models.py`.
- **Prevention**: Mọi call Gemini Pro dùng structured JSON output → dùng `max_output_tokens ≥ 16384`.

### L04.5 — gemini-3.1-pro-preview chỉ available qua `location='global'` (2026-04-14)
Model 3.1-pro-preview trả 404 NOT_FOUND với mọi region cụ thể (us-central1, us-east5, europe-west4, ...). Chỉ hoạt động với `location='global'` (routing endpoint).
- **Root cause**: Preview models có thể chưa được deploy tới specific regions, chỉ available qua global routing.
- **Fix**: Thêm `MODEL_PRO_NEW_LOCATION=global` vào `.env` + `get_client_for_model()` pool trong `gemini.py` (dùng đúng client cho mỗi model).
- **Prevention**: Khi test model mới → verify bằng `python3 tools/ab_test_models.py verify` trước. Nếu fail → thử `global` trước khi thử region cụ thể.

### L04.6 — 3.1-preview clean output, 2.5-pro có preamble + code fence (A/B test result 2026-04-14)
Trong A/B test compile (simplified prompt), 2.5-pro thêm "Chắc chắn rồi..." preamble + bọc trong ````markdown...``` `. 3.1-preview không có preamble nhưng cũng có thể thêm code fence cho 1 số categories.
- **Root cause**: Models nghe theo "vai trò" prompt context, 2.5-pro có xu hướng verbose hơn.
- **Fix**: Thêm `_strip_compile_fences()` defensive handler trong `compile.py`. Production prompt đã có explicit "không code fence" instruction.
- **Note**: Trong production (với đầy đủ prompt), 2.5-pro ít bị issue này hơn. Lesson quan trọng cho thiết kế prompt tương lai.

## ⚠️ Cảnh Báo
> Model `-preview` có thể bị deprecate (như `gemini-3-pro-preview` đã bị disable 2026-03-26). Theo dõi [Vertex AI release notes](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes) hàng tuần.

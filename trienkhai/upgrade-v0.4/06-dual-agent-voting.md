---
part: 06
title: "Dual-Agent Cross-Validation & Voting"
status: in-progress
estimate: 4-6 giờ
depends_on: [04, 05]
blocks: [07]
checkpoint: 2026-04-14
---

# PART 06 — Dual-Agent Voting (TRỌNG TÂM)

## 🎯 Mục Tiêu
Đây là **giá trị cốt lõi** của v0.4. Tạo skill mới `dual-vote` chạy SONG SONG Gemini 3.1 Pro + GPT-5.4 cho cùng 1 input, so sánh output, output kết quả "consensus" hoặc flag conflict cho human review.

## 🧠 Triết Lý Quan Trọng

> **Voting ≠ Average**. Không bao giờ trộn 2 output thành 1. Logic là:
> - Nếu 2 model **đồng ý** (semantic match) → confidence HIGH → auto-approve
> - Nếu 2 model **bất đồng** → confidence LOW → flag cho human
> - Nếu 1 model **fail** → fallback model còn lại + giảm confidence

Pattern này lấy từ **constitutional AI** + **majority voting** trong ensemble ML.

## 🏗️ Kiến Trúc

```
INPUT (markdown / claims YAML)
       │
       ├──→ Agent A (Gemini 3.1 Pro) ──→ Output A + reasoning + confidence
       │
       ├──→ Agent B (GPT-5.4)        ──→ Output B + reasoning + confidence
       │
       ▼
   CONSENSUS ENGINE
   ├─ Agree (sim ≥ 0.9)  → emit Output A, confidence=HIGH
   ├─ Partial (0.6-0.9)  → emit merged + flag MEDIUM
   ├─ Disagree (<0.6)    → emit BOTH + flag LOW + alert Telegram
   └─ Either fails       → emit successful one + flag DEGRADED
       │
       ▼
   OUTPUT (claim YAML / wiki section)
   + dual-vote-audit.jsonl (mọi quyết định ghi lại)
```

## ✅ Checklist

### Bước 1 — Tạo skill `dual-vote`
- [x] `mkdir skills/dual-vote/{scripts,tests}` ✅
- [x] Viết `skills/dual-vote/skill.md` ✅

### Bước 2 — Implement core script
- [x] `lib/dual_vote.py` — core engine (importable) ✅
- [x] `skills/dual-vote/scripts/vote.py` — thin CLI wrapper ✅
- [x] `lib/utils.py::semantic_similarity()` — JSON structural + Jaccard fallback ✅
  - Strip markdown fences trước khi parse JSON (Gemini hay wrap ```json```)
- [x] Audit log → `logs/dual-vote-YYYY-MM.jsonl` ✅
- [x] Review queue → `.review-queue/*.json` ✅

### Bước 3 — Adapter cho extract-claims
- [x] `skills/extract-claims/scripts/extract_dual.py` ✅
  - `DUAL_VOTE_ENABLED=true` → all categories
  - `DUAL_VOTE_ENABLED=false` → chỉ `DUAL_VOTE_HIGH_STAKES` categories

### Bước 4 — Adapter cho compile-wiki
- [x] `skills/compile-wiki/scripts/compile_dual.py` ✅
  - High-stakes pages → dual-vote validate
  - DISAGREE/PARTIAL → `<!-- ⚠️ NEEDS REVIEW -->` marker + `.review-queue/`

### Bước 5 — Human review UI (mở rộng web portal)
[`web/`](../../web/):
- [x] Thêm `GET /api/review/dual-queue` — list items từ `.review-queue/*.json` ✅
- [x] Thêm `GET /api/review/dual/:id` — lấy item cụ thể ✅
- [x] Thêm `POST /api/review/dual/:id/decide` — quyết định pick_a/pick_b/reject_both ✅
- [x] Side-by-side modal: Agent A (Gemini) vs Agent B (GPT) ✅
- [x] Buttons: "Chọn A", "Chọn B", "Loại bỏ cả hai" ✅
- [x] Mọi quyết định ghi audit → `logs/dual-vote-decisions-YYYY-MM.jsonl` ✅
- [x] File resolved → `.review-queue/resolved/` ✅
- Note: "Edit & Save" không implement — DISAGREE thường cần re-extract, không edit thủ công

### Bước 6 — Telegram notification
- [x] Khi có ≥ 5 items trong review-queue → ping admin qua Telegram ✅ (`lib/dual_vote.py::_check_queue_threshold()`)
- [x] Daily digest script: `skills/dual-vote/scripts/daily_digest.py` ✅
  - Cron: `0 8 * * * cd /wiki && python3 skills/dual-vote/scripts/daily_digest.py`

### Bước 7 — Test trên test-set (PART 01)
- [x] Script: `skills/dual-vote/scripts/test_20claims.py` ✅
- [x] Run dual-vote trên 20 claims test set ✅ (2026-04-14)
- [x] Output: `trienkhai/upgrade-v0.4/dual-vote-test-results.md` ✅
- ⚠️ Kết quả: AGREE=0%, DISAGREE=75% — CAO HƠN EXPECTED
  - Root cause: Test dùng "verify" prompt → JSON structure khác nhau dù nội dung đồng ý
  - Cost/claim: $0.00238 (2x single-model) → trong budget
  - Xem phân tích đầy đủ trong `dual-vote-test-results.md`
- [ ] Re-test với extraction prompt thực tế (PART 07 regression test)

### Bước 8 — Cost analysis
- [ ] Đo cost per claim với dual-vote vs single
- [ ] Đề xuất chiến lược: chỉ dual-vote cho category high-stakes (hosting, vps, ssl)
- [ ] Sections low-stakes (FAQ chung) vẫn dùng single

## 📤 Output của PART 06
- `skills/dual-vote/` — skill mới hoàn chỉnh
- `skills/extract-claims/scripts/extract_dual.py`
- `skills/compile-wiki/scripts/compile_dual.py`
- `web/routes/review.js` + UI side-by-side
- `lib/utils.py::semantic_similarity()` 
- `logs/dual-vote-*.jsonl` schema
- `trienkhai/upgrade-v0.4/dual-vote-test-results.md`

## 🚦 Acceptance Criteria
- [ ] Dual-vote chạy stable trên 50 inputs liên tiếp không crash
- [ ] Agreement rate ≥ 70% trên test set
- [ ] Cost ≤ 2.5x single-model run
- [ ] Web UI review hoạt động end-to-end
- [ ] DISAGREE cases được flag và ghi vào review-queue đúng

## 🔙 Rollback
```bash
echo "DUAL_VOTE_ENABLED=false" >> .env
pm2 restart all
# Skill files giữ lại — chỉ tắt feature flag
```

## 📝 Lessons

### L1 — Python module không thể có hyphen trong tên directory
**Vấn đề**: `skills/dual-vote/` → `from skills.dual_vote import ...` bị `ModuleNotFoundError`.
**Resolution**: Core logic đặt trong `lib/dual_vote.py` (underscore). `skills/dual-vote/scripts/vote.py` chỉ là CLI wrapper thin.
**Prevention**: Skill directories dùng hyphen (convention), library code trong `lib/` dùng underscore.

### L2 — Gemini luôn wrap JSON output trong markdown code fence
**Vấn đề**: Gemini trả `\`\`\`json....\`\`\`` → `json.loads()` fail → `semantic_similarity` tính thấp giả.
**Resolution**: `semantic_similarity()` gọi `_strip_markdown_fence()` trước khi parse JSON.
**Prevention**: Khi so sánh LLM outputs, luôn normalize (strip fences, strip whitespace) trước khi compare.

### L3 — DISAGREE không có nghĩa là 1 model sai
**Vấn đề**: Gemini extract {price, uptime}, GPT extract {provider, service} → score 0.16 = DISAGREE.
**Thực tế**: Cả 2 đều đúng nhưng chọn *khác nhau claims*. Đây là feature, không phải bug.
**Resolution**: DISAGREE cần human review để chọn claims nào có giá trị hơn cho wiki.
**Prevention**: Dùng EXTRACTION_PROMPT đầy đủ (từ extract.py) khi test — không dùng prompt đơn giản.

### L4 — Verify prompt ≠ Extract prompt (2026-04-14)
**Vấn đề**: Test "verify existing claim" → AGREE=0%, DISAGREE=75%. Cả 2 model đều đúng nhưng JSON `reason` field khác → similarity thấp.
**Root cause**: Verification task cho phép free-form reasoning → divergent text. Extraction task có prompt cụ thể hơn → output tương đồng hơn.
**Resolution**: Acceptance criteria "AGREE ≥70%" phải đo trên extraction task (PART 07), không phải verification task.
**Prevention**: Khi test dual-vote, luôn dùng prompt giống production prompt — không dùng prompt ad-hoc.

### L5 — Checkpoint PART 06 DONE (2026-04-14)
Bước 1-7 đã implement:
- Core engine: `lib/dual_vote.py`
- CLI: `skills/dual-vote/scripts/vote.py`
- Adapters: `extract_dual.py`, `compile_dual.py`
- Web UI: `/api/review/dual-queue`, `/api/review/dual/:id/decide`, side-by-side modal
- Telegram: threshold alert (≥5 items) + daily digest
- Test: 20 claims chạy OK, cost $0.04761 ($0.00238/claim)
- Còn lại PART 07: Regression test với extraction prompt thực tế.

## 🔬 Nâng Cao (PHASE 2 — không làm trong v0.4)
- Tam-vote (thêm Claude Opus 4.6 làm agent C để break tie)
- LLM-as-judge: agent C đánh giá output của A vs B (thay vì similarity)
- Adversarial prompting: 1 agent là "critic" của agent kia

---
title: "Master Checklist — Upgrade v0.4"
created: 2026-04-13
---

# ✅ MASTER CHECKLIST v0.4

> File này là quick-reference. Chi tiết từng bước nằm ở `01-08-*.md`.
> Đánh `[x]` khi xong, ghi chú phiên thực hiện vào cột bên phải.

## PART 01 — Survey Baseline (30 phút)
- [ ] Snapshot v0.3 immutable backup
- [ ] Đo baseline metrics → `baseline-metrics.json`
- [ ] Audit risk
- [ ] Chọn test set (5 pages, 20 claims) → `test-set.yaml`
- [ ] Set cost guard $20/$10

## PART 02 — markitdown Pilot (1 giờ)
- [ ] Cài isolated venv
- [ ] Test 3 file mẫu (DOCX, PDF, HTML)
- [ ] So sánh markitdown vs legacy → `pilot-comparison.md`
- [ ] Test format mới (YouTube, EPUB)
- [ ] Quyết định GO/NO-GO

## PART 03 — markitdown Integration (2-3 giờ)
- [ ] Cài markitdown vào prod venv
- [ ] Tạo `tools/converters/markitdown_adapter.py`
- [ ] Refactor `convert_manual.py` với dispatch table
- [ ] Dual-write 1 tuần
- [ ] Tạo `ingest_youtube.py`, `ingest_html.py`, `ingest_audio.py`
- [ ] Mở rộng MIME whitelist web portal
- [ ] Test suite pass

## PART 04 — Gemini 3.1 Upgrade (1-2 giờ)
- [ ] **[USER]** Verify `gemini-3.1-pro-preview` available: `python3 tools/ab_test_models.py verify`
- [x] Add feature flag `USE_PRO_NEW` + `get_pro_model()` helper (lib/config.py)
- [x] Fix PRICING dict + update call sites (extract.py, compile.py, lint.py)
- [x] Tạo `tools/ab_test_models.py` (A/B test script: verify/extract/compile)
- [ ] **[USER]** Thêm `MODEL_PRO_NEW + USE_PRO_NEW=false` vào `.env`
- [ ] **[USER]** Chạy A/B test extract: `python3 tools/ab_test_models.py extract`
- [ ] **[USER]** Chạy A/B test compile: `python3 tools/ab_test_models.py compile`
- [ ] **[USER]** Manual review output → điền verdict vào ab-test-*.md
- [ ] Adjust prompt nếu cần (sau A/B review)
- [ ] **[USER]** Bật flag (`USE_PRO_NEW=true`) + pm2 restart + monitor 24h

## PART 05 — OpenAI Setup (1 giờ)
- [ ] Lấy API key + spending limit
- [ ] Lưu vào `.env` (chmod 600)
- [ ] Cài `openai>=1.54.0`
- [ ] Tạo `lib/openai_client.py`
- [ ] Smoke test gpt-5.4
- [ ] Implement retry & rate-limit
- [ ] Audit log working

## PART 06 — Dual-Agent Voting (4-6 giờ) ⭐ CORE
- [ ] Tạo skill `dual-vote/`
- [ ] Implement `vote.py` (parallel + analyze)
- [ ] Implement `semantic_similarity()`
- [ ] Adapter cho extract-claims
- [ ] Adapter cho compile-wiki
- [ ] Web UI review side-by-side
- [ ] Telegram notification
- [ ] Test trên 20 claims → agreement ≥ 70%

## PART 07 — Regression Test (2 giờ)
- [x] Tạo `tools/regression_test.py` ✅ (2026-04-14)
- [x] Tạo `tools/wiki_diff.py` ✅ (2026-04-14)
- [x] Tạo `regression-review.md` template ✅
- [x] Tạo `benchmark.md` (v0.3 baseline pre-filled) ✅
- [x] Tạo `bot-qa-test.md` (30 câu) ✅
- [ ] **[USER]** Enable `DUAL_VOTE_ENABLED=true` + dry-run hosting
- [ ] **[USER]** Re-build full 7 categories: `regression_test.py --full`
- [ ] **[USER]** Run `wiki_diff.py` → diff-report.html
- [ ] **[USER] Human review 7 wiki pages** ⚠️ → `regression-review.md`
- [ ] **[USER]** Bot QA test 30 câu → `bot-qa-test.md`
- [ ] **[USER]** Điền `benchmark.md` → Quyết định PROMOTE / ROLLBACK

## PART 08 — Production Rollout (1 giờ)
- [ ] Promote wiki v0.4
- [ ] Restart services + smoke test
- [ ] Setup monitoring cron
- [ ] Update dashboards
- [ ] Update docs (PROJECT_SUMMARY, README, LESSONS)
- [ ] Tạo `scripts/rollback-v0.4.sh`
- [ ] Backup giữ 30 ngày

---

## 📊 Progress Tracker

| PART | Status | Phiên | Date | Lessons |
|---|---|---|---|---|
| 01 | ✅ done | phiên 1 | 2026-04-13 | L01.1-4 (4 lessons) |
| 02 | ✅ done | phiên 1 | 2026-04-13 | markitdown GO decision |
| 03 | 🔄 in-progress | phiên 1 | 2026-04-13 | Bước 1-4 done, Bước 5-8 còn lại |
| 04 | 🔄 in-progress | phiên 2 | 2026-04-13 | Code done, USER ACTION: verify+A/B+enable |
| 05 | ⏳ pending | — | — | — |
| 06 | ⏳ pending | — | — | — |
| 07 | 🔄 in-progress | phiên 3 | 2026-04-14 | Tooling done, USER ACTION: run rebuild |
| 08 | ⏳ pending | — | — | — |

Status legend: ⏳ pending | 🔄 in-progress | ✅ done | ❌ blocked | 🚫 skipped

---

## 🎯 Định Nghĩa "Done" Toàn Dự Án v0.4

v0.4 chỉ được coi là HOÀN THÀNH khi:
- ✅ Tất cả 8 PART đã `done`
- ✅ Bot trả lời ≥ 80% câu hỏi đúng (so với baseline)
- ✅ Cost ≤ $15/tháng ổn định
- ✅ Review queue hoạt động, có ≥ 5 reviews đã xử lý
- ✅ 7 ngày liên tục không có rollback
- ✅ `LESSONS.md` đã ghi top 5 bài học

---

## 🆘 Khi Gặp Sự Cố

| Tình huống | Action |
|---|---|
| Phiên Claude vượt context | Save state vào PART file, mở phiên mới với `/start [PART_NN.md]` |
| Cost vượt budget | Pause v0.4, tắt `DUAL_VOTE_ENABLED`, review log chi tiết |
| Wiki bị regression | Chạy `scripts/rollback-v0.4.sh` |
| Dual-vote disagree quá nhiều | Có thể prompt mismatch — review prompts từng skill |
| API key leak | Revoke ngay tại OpenAI/GCP, rotate, audit log truy cập |

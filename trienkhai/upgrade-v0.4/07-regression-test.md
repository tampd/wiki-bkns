---
part: 07
title: "Regression Test — v0.3 vs v0.4 Wiki Comparison"
status: in_progress
estimate: 2 giờ
depends_on: [03, 06]
blocks: [08]
checkpoint: 2026-04-14
---

# PART 07 — Regression Test Toàn Diện

## 🎯 Mục Tiêu
Re-build TOÀN BỘ wiki bằng pipeline v0.4 (markitdown + dual-vote + Gemini 3.1) trên cùng dataset. So sánh từng wiki page v0.3 vs v0.4 để verify accuracy không tụt và conflicts đã giảm.

## 📋 Phương Pháp

```
v0.3 snapshot (PART 01) ──┐
                           ├──→ DIFF ENGINE ──→ Report
v0.4 fresh build      ────┘
```

## ✅ Checklist

### Bước 1 — Preparation
- [x] Verify PART 01 snapshot tồn tại: `build/snapshots/v0.3-pre-upgrade-2026-04-13/` ✅
- [x] Verify tất cả flags v0.4 đã ON:
  - `USE_PRO_NEW=false` ⚠️ Vẫn false — USER ACTION: verify gemini-3.1-pro-preview quota rồi enable
  - `DUAL_VOTE_ENABLED=true` ✅ Đã enable (fixed duplicate .env 2026-04-14)
  - `markitdown adapter`: ✅ merged (tools/converters/markitdown_adapter.py)
- [x] `.env` đã sạch: duplicate `DUAL_VOTE_ENABLED` đã xóa, giá trị `true` ✅
- [ ] Backup `claims/approved/` và `wiki/products/` thêm 1 lần nữa:
  ```bash
  cp -r claims/approved claims/approved.backup-pre-v0.4-$(date +%Y%m%d)
  cp -r wiki/products wiki/products.backup-pre-v0.4-$(date +%Y%m%d)
  ```

### Bước 2 — Dry-run trên 1 category (hosting)
- [ ] **[USER ACTION]** Re-extract + compile hosting với dual-vote:
```bash
cd /home/openclaw/wiki
# Ensure flag is on
grep DUAL_VOTE_ENABLED .env
# Run dry-run (hosting only)
python3 tools/regression_test.py --dry-run --step extract
python3 tools/regression_test.py --dry-run --step compile
```
- [ ] Compare claims count: cũ vs mới (xem `trienkhai/upgrade-v0.4/regression-summary.json`)
- [ ] Note AGREE/PARTIAL/DISAGREE rate (extraction task, should be better than PART 06 verify test)
- [ ] Manual review 5 claims random từ `.review-queue/*.json`

### Bước 3 — Re-build full 7 categories
- [ ] **[USER ACTION]** Run full rebuild:
```bash
cd /home/openclaw/wiki
python3 tools/regression_test.py --full
```
- [ ] Output: `wiki-v0.4/products/<cat>/*.md` (tự động copy từ wiki/.drafts)
- [ ] Summary: `trienkhai/upgrade-v0.4/regression-summary.json`
- [ ] Điền metrics vào `trienkhai/upgrade-v0.4/benchmark.md`

### Bước 4 — Diff Engine
Script `tools/wiki_diff.py` ✅ (đã tạo 2026-04-14):
- [x] Script tạo xong: `tools/wiki_diff.py` ✅
- [ ] **[USER ACTION]** Chạy sau Bước 3:
```bash
cd /home/openclaw/wiki
python3 tools/wiki_diff.py \
  --v03 build/snapshots/v0.3-pre-upgrade-2026-04-13/wiki/products \
  --v04 wiki-v0.4/products \
  --html trienkhai/upgrade-v0.4/diff-report.html \
  --json trienkhai/upgrade-v0.4/diff-report.json
```
- [ ] Report 3 loại change: Improvements / Regressions / Neutral
- [ ] HTML side-by-side: `trienkhai/upgrade-v0.4/diff-report.html`

### Bước 5 — Human review (CRITICAL)
Template: `trienkhai/upgrade-v0.4/regression-review.md` ✅ (đã tạo 2026-04-14)
- [x] Template human review tạo xong ✅
- [ ] **[USER ACTION]** Mở `trienkhai/upgrade-v0.4/diff-report.html` trong browser
- [ ] **[USER ACTION]** Mở 7 wiki pages v0.4 trong browser: `wiki-v0.4/products/<cat>/`
- [ ] **[USER ACTION]** Check từng bảng giá → so với BKNS.VN thực tế (mở thủ công)
- [ ] **[USER ACTION]** Check thông số kỹ thuật (RAM, CPU, băng thông)
- [ ] **[USER ACTION]** Check hotline / email (CRITICAL — không được sai)
- [ ] **[USER ACTION]** Điền verdict vào `trienkhai/upgrade-v0.4/regression-review.md`

### Bước 6 — Telegram bot test
Template: `trienkhai/upgrade-v0.4/bot-qa-test.md` ✅ (đã tạo 2026-04-14, 30 câu sẵn sàng)
- [x] 30 câu hỏi đã soạn sẵn trong `trienkhai/upgrade-v0.4/bot-qa-test.md` ✅
- [ ] **[USER ACTION]** Gửi 30 câu qua Telegram bot (sau khi rebuild xong)
- [ ] **[USER ACTION]** Điền kết quả vào `bot-qa-test.md`
- [ ] **[USER ACTION]** Điền accuracy% vào `benchmark.md`

### Bước 7 — Performance benchmark
Template: `trienkhai/upgrade-v0.4/benchmark.md` ✅ (đã tạo với v0.3 baseline pre-filled)
- [x] `benchmark.md` tạo xong với v0.3 numbers sẵn ($6.50, 2252 claims, 25 conflicts) ✅
- [ ] **[USER ACTION]** Điền v0.4 numbers sau khi chạy Bước 2-3
- [ ] Track xem AGREE rate trên extraction task có tốt hơn PART 06 verify test không

### Bước 8 — Quyết định promote hay rollback
Tiêu chí PROMOTE v0.4 → production:
- [ ] Accuracy ≥ v0.3 ở ≥ 90% trường hợp test
- [ ] Không có regression critical (giá tiền sai, hotline sai)
- [ ] Cost tăng ≤ 2x
- [ ] Bot QA test ≥ 80% pass

Nếu KHÔNG đạt:
- [ ] Phân tích root cause (model nào sai? prompt nào cần chỉnh?)
- [ ] Quay lại PART tương ứng để fix
- [ ] Re-run PART 07

## 📤 Output của PART 07
- `tools/regression_test.py` ✅ tạo 2026-04-14
- `tools/wiki_diff.py` ✅ tạo 2026-04-14
- `trienkhai/upgrade-v0.4/regression-review.md` ✅ tạo 2026-04-14
- `trienkhai/upgrade-v0.4/bot-qa-test.md` ✅ tạo 2026-04-14 (30 câu)
- `trienkhai/upgrade-v0.4/benchmark.md` ✅ tạo 2026-04-14 (v0.3 baseline sẵn)
- `wiki-v0.4/` ⏳ pending USER ACTION (chạy regression_test.py --full)
- `trienkhai/upgrade-v0.4/diff-report.html` ⏳ pending USER ACTION
- `trienkhai/upgrade-v0.4/diff-report.json` ⏳ pending USER ACTION
- `trienkhai/upgrade-v0.4/regression-summary.json` ⏳ pending USER ACTION
- Quyết định GO/NO-GO ⏳ pending human review

## 🔙 Rollback
v0.3 vẫn nguyên trong snapshot. Nếu fail:
```bash
rm -rf wiki-v0.4
# Tắt flags
sed -i 's/USE_PRO_NEW=true/USE_PRO_NEW=false/' .env
sed -i 's/DUAL_VOTE_ENABLED=true/DUAL_VOTE_ENABLED=false/' .env
pm2 restart all
```

## 📝 Lessons

### L1 — Checkpoint PART 07 (2026-04-14)
**Trạng thái**: Tooling đã tạo, chờ USER ACTION chạy rebuild.

**Đã implement:**
- `tools/regression_test.py` — orchestrator (extract_dual + compile_dual, per category)
- `tools/wiki_diff.py` — diff engine v0.3 vs v0.4, HTML side-by-side, JSON report
- `regression-review.md` — human review template (7 categories × N pages)
- `benchmark.md` — v0.3 baseline pre-filled ($6.50, 2252 claims, 25 conflicts)
- `bot-qa-test.md` — 30 câu QA sẵn sàng (5 câu × 6 categories)

**Còn lại (USER ACTION):**
1. Enable `DUAL_VOTE_ENABLED=true` trong `.env`
2. Chạy `python3 tools/regression_test.py --dry-run` (hosting)
3. Review dry-run results → nếu OK, chạy `--full`
4. Chạy `python3 tools/wiki_diff.py` sau full rebuild
5. Human review `diff-report.html` + `regression-review.md`
6. Gửi 30 câu qua Telegram bot → điền `bot-qa-test.md`
7. Điền `benchmark.md` → quyết định GO/NO-GO

**Note về USE_PRO_NEW:** Regression test này chạy với Gemini 2.5 Pro (hiện tại) + GPT-5.4 (dual-vote). Để test với Gemini 3.1 Pro, cần hoàn thành PART 04 USER ACTION trước (verify + enable USE_PRO_NEW=true).

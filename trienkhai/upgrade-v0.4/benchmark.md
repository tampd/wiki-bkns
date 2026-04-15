---
artifact: benchmark
part: 07
created: 2026-04-14
status: in_progress
---

# Performance Benchmark — v0.3 vs v0.4

> Điền v0.4 metrics sau khi chạy `regression_test.py --full`
> v0.3 baseline chốt ngày 2026-04-13 (PART 01 survey)

---

## Build Metrics

| Metric | v0.3 (baseline) | v0.4 (actual) | Delta | Status |
|--------|----------------|---------------|-------|--------|
| Raw files processed | 291 | _(điền sau)_ | | |
| Claims extracted | 2,252 | _(điền sau)_ | | |
| Claims approved | 2,252 | _(điền sau)_ | | |
| Wiki pages generated | 213 | _(điền sau)_ | | |
| **Total build cost** | **$6.50** | _(điền sau)_ | | |
| Build time (full) | ~45 min | _(điền sau)_ | | |
| Tokens generated | 13,786 | _(điền sau)_ | | |

---

## Conflict & Quality Metrics

| Metric | v0.3 | v0.4 | Delta | Target | Status |
|--------|------|------|-------|--------|--------|
| Conflicts detected | 25 | _(điền)_ | | ≤ 15 | |
| Dual-vote AGREE | N/A | _(điền)_ | | ≥ 70% | |
| Dual-vote PARTIAL | N/A | _(điền)_ | | | |
| Dual-vote DISAGREE | N/A | _(điền)_ | | ≤ 30% | |
| Review queue items | 0 | _(điền)_ | | | |
| Auto-approved claims | 2,252 | _(điền)_ | | | |

---

## Cost Analysis

| Category | v0.3 extract | v0.3 compile | v0.4 extract (dual) | v0.4 compile (dual) | Total v0.4 |
|----------|-------------|-------------|---------------------|---------------------|-----------|
| hosting | | | _(điền)_ | _(điền)_ | |
| vps | | | _(điền)_ | _(điền)_ | |
| ssl | | | _(điền)_ | _(điền)_ | |
| ten-mien | | | _(điền)_ | _(điền)_ | |
| email | | | _(điền)_ | _(điền)_ | |
| server | | | _(điền)_ | _(điền)_ | |
| software | | | _(điền)_ | _(điền)_ | |
| **TOTAL** | **~$4.20** | **~$2.30** | _(điền)_ | _(điền)_ | _(điền)_ |

**Cost multiple v0.4/v0.3:** _(điền)_ x  
**Target:** ≤ 2x (hard limit $15 total cho testing)

---

## Dual-Vote Performance (Extraction Task)

> Đây là metric quan trọng nhất — khác với PART 06 test (verify task, AGREE=0%)
> Test này dùng EXTRACTION_PROMPT thực tế từ extract.py

| Category | Files | AGREE | PARTIAL | DISAGREE | AGREE% | Cost/file |
|----------|-------|-------|---------|----------|--------|-----------|
| hosting | 65 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| vps | 44 | | | | | |
| ssl | 56 | | | | | |
| ten-mien | 44 | | | | | |
| email | 24 | | | | | |
| server | 24 | | | | | |
| software | 12 | | | | | |
| **TOTAL** | **269** | | | | | |

**Expected improvement over PART 06 test:** AGREE > 30% (extraction prompt giống hơn)

---

## Wiki Diff Results (from wiki_diff.py)

| Category | Pages v0.3 | Pages v0.4 | Improvements | Regressions | Regression% |
|----------|-----------|-----------|-------------|------------|------------|
| hosting | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| vps | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| ssl | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| ten-mien | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| email | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| server | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| software | | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| **TOTAL** | **~213** | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |

**Target:** Regression < 10%

---

## Bot QA Test (30 questions)

| Category | Questions | Correct | Wrong | N/A | Accuracy% |
|----------|-----------|---------|-------|-----|-----------|
| hosting | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| vps | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| ssl | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| ten-mien | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| email | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| server | 5 | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |
| **TOTAL** | **30** | _(điền)_ | _(điền)_ | _(điền)_ | _(điền)_ |

**v0.3 baseline accuracy:** _(điền nếu đã test v0.3)_  
**Target v0.4:** ≥ 80% correct

---

## Acceptance Criteria Summary

| Criteria | Target | Actual | Status |
|----------|--------|--------|--------|
| Accuracy ≥ v0.3 ở ≥ 90% test cases | ≥ 90% | _(điền)_ | ⬜ |
| Không có regression critical (giá sai, hotline sai) | 0 | _(điền)_ | ⬜ |
| Cost tăng ≤ 2x | ≤ 2x | _(điền)_ | ⬜ |
| Bot QA ≥ 80% pass | ≥ 80% | _(điền)_ | ⬜ |
| AGREE rate extraction ≥ 70% | ≥ 70% | _(điền)_ | ⬜ |

**Quyết định:** _(PROMOTE v0.4 / ROLLBACK / CONDITIONAL-GO)_

---

## Notes & Observations

_(Điền sau khi chạy regression test)_

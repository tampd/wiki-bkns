---
artifact: ab-test-compile
part: 04
generated: 2026-04-14 03:41 UTC
model_old: gemini-2.5-pro
model_new: gemini-3.1-pro-preview
---

# A/B Test — Compile Wiki

> Chạy: 2026-04-14 03:41 UTC  
> Model cũ: `gemini-2.5-pro`  
> Model mới: `gemini-3.1-pro-preview`

## Kết Quả Theo Category

| Category | Claims in | Output (cũ) | Output (mới) | Cost cũ | Cost mới | Δ Cost% |
|---|---|---|---|---|---|---|
| hosting | 8 | 1,986 chars | 1,620 chars | $0.0092 | $0.0107 | +15.5% |
| vps | 8 | 1,350 chars | 1,699 chars | $0.0077 | $0.0118 | +53.4% |
| ssl | 8 | 1,387 chars | 1,220 chars | $0.0080 | $0.0097 | +21.8% |
| ten-mien | 8 | 1,290 chars | 601 chars | $0.0084 | $0.0084 | +0.4% |
| email | 8 | 2,052 chars | 1,768 chars | $0.0104 | $0.0126 | +21.0% |
| **TOTAL** | — | — | — | **$0.0437** | **$0.0532** | **+21.8%** |

## Manual Review Checklist

So sánh output của 2 model cho mỗi category:

### hosting
- [ ] Thông tin nào bị mất ở model mới?
- [ ] Có thông tin sai mới nào không?
- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?
- Files: `ab-compile-2-5-pro/hosting.md` vs `ab-compile-3-1-preview/hosting.md`

### vps
- [ ] Thông tin nào bị mất ở model mới?
- [ ] Có thông tin sai mới nào không?
- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?
- Files: `ab-compile-2-5-pro/vps.md` vs `ab-compile-3-1-preview/vps.md`

### ssl
- [ ] Thông tin nào bị mất ở model mới?
- [ ] Có thông tin sai mới nào không?
- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?
- Files: `ab-compile-2-5-pro/ssl.md` vs `ab-compile-3-1-preview/ssl.md`

### ten-mien
- [ ] Thông tin nào bị mất ở model mới?
- [ ] Có thông tin sai mới nào không?
- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?
- Files: `ab-compile-2-5-pro/ten-mien.md` vs `ab-compile-3-1-preview/ten-mien.md`

### email
- [ ] Thông tin nào bị mất ở model mới?
- [ ] Có thông tin sai mới nào không?
- [ ] Self-review marker `[OK]/[CORRECTION]` có đúng format không?
- Files: `ab-compile-2-5-pro/email.md` vs `ab-compile-3-1-preview/email.md`

## Acceptance Criteria

| Criteria | Result |
|---|---|
| Cost tăng ≤ 35% | ✅ (+21.8%) |
| Không mất thông tin quan trọng | _(cần manual review)_ |
| Không có thông tin sai mới | _(cần manual review)_ |

## Verdict

**Verdict**: _(chưa review — điền GO / NO-GO / NEEDS-ADJUSTMENT sau khi đọc output)_
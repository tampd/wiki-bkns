---
artifact: ab-test-extract
part: 04
generated: 2026-04-14 03:35 UTC
model_old: gemini-2.5-pro
model_new: gemini-3.1-pro-preview
---

# A/B Test — Extract Claims

> Chạy: 2026-04-14 03:35 UTC  
> Model cũ: `gemini-2.5-pro`  
> Model mới: `gemini-3.1-pro-preview`

## Kết Quả Theo Category

| Category | File | Claims (cũ) | Claims (mới) | Δ Claims | Cost cũ | Cost mới | Δ Cost% |
|---|---|---|---|---|---|---|---|
| hosting | hosting-2026-04-04.md | 4 | 0 | -4 | $0.0031 | $0.0009 | +-72.3% |
| vps | cloud-vps-amd-web-2026-04-05.md | -1 | 21 | N/A | $0.0059 | $0.0170 | +187.2% |
| ssl | ssl-tong-hop-web-2026-04-05.md | 38 | 37 | -1 | $0.0240 | $0.0295 | +22.7% |
| ten-mien | dang-ky-ten-mien-2026-04-05.md | 21 | 18 | -3 | $0.0143 | $0.0160 | +12.1% |
| email | email-hosting-web-2026-04-05.md | -1 | 35 | N/A | $0.0203 | $0.0265 | +30.2% |
| **TOTAL** | — | **63** | **111** | **48** | **$0.0677** | **$0.0898** | **+32.7%** |

## Token Usage

| Category | In (cũ) | Out (cũ) | In (mới) | Out (mới) | Elapsed cũ | Elapsed mới |
|---|---|---|---|---|---|---|
| hosting | 377 | 264 | 377 | 9 | 27412ms | 9358ms |
| vps | 782 | 494 | 782 | 1286 | 65787ms | 22710ms |
| ssl | 1193 | 2255 | 1193 | 2260 | 64892ms | 37144ms |
| ten-mien | 735 | 1337 | 735 | 1212 | 26415ms | 49919ms |
| email | 828 | 1929 | 828 | 2067 | 65928ms | 28527ms |

## Acceptance Criteria

| Criteria | Result |
|---|---|
| Claims mới ≥ claims cũ | ✅ (63 → 111) |
| Cost tăng ≤ 35% | ✅ (+32.7%) |

## Verdict

<!-- Điền sau khi review manual: GO / NO-GO / NEEDS-ADJUSTMENT -->
**Verdict**: _(chưa review)_

## Raw Output
- Claims gemini-2.5-pro: `trienkhai/upgrade-v0.4/ab-claims-2-5-pro/`
- Claims gemini-3.1-pro-preview: `trienkhai/upgrade-v0.4/ab-claims-3-1-preview/`

## Notes
*(Điền nhận xét thủ công sau khi đọc output JSON)*
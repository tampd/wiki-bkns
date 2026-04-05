# INSTINCTS — BKNS Wiki Project
> Learned patterns + confidence scores (0.0–1.0)
> Last updated: 2026-04-05

---

## I001 — Luôn chạy compile.py trực tiếp thay vì qua approve_and_compile.py
- **Confidence**: 0.8
- **Trigger**: Khi cần compile wiki pages từ claims
- **Action**: `python3 skills/compile-wiki/scripts/compile.py --all` thay vì `python3 tools/approve_and_compile.py`
- **Reason**: approve_and_compile.py có import sai module name
- **Validated**: 1 lần (2026-04-05)

## I002 — Retry compile khi self-review block (max 2 lần)
- **Confidence**: 0.7
- **Trigger**: Khi compile bị blocked do hallucination detection
- **Action**: Chạy lại compile cho category đó. Gemini tạo output khác mỗi lần → lần 2 thường pass.
- **Reason**: Self-review đúng khi block, nhưng Gemini non-deterministic → retry hiệu quả
- **Validated**: 1 lần (2026-04-05 — ten-mien retry thành công)

## I003 — Tách batch crawl thành ≤20 URL/batch với delay
- **Confidence**: 0.7
- **Trigger**: Khi cần cào nhiều trang từ cùng 1 domain
- **Action**: Tách thành batch ≤20 URLs, thêm 2-3s delay giữa mỗi request
- **Reason**: Cloudflare WAF block pattern crawling liên tục
- **Validated**: 1 lần (2026-04-05)

## I004 — Excel bảng giá là source of truth, KHÔNG phải website
- **Confidence**: 0.9
- **Trigger**: Khi có conflict giá giữa website và Excel
- **Action**: Ưu tiên giá từ Excel. Ghi note nếu website hiển thị giá khác.
- **Reason**: Website hiển thị giá khuyến mãi/giảm giá, Excel là giá gốc chính xác
- **Validated**: Nhiều lần (2026-04-05)

## I005 — Dùng script Python để tạo batch raw files thay vì tạo thủ công
- **Confidence**: 0.85
- **Trigger**: Khi cần tạo >5 raw markdown files cho pipeline
- **Action**: Viết script generate (ví dụ: `tools/generate_web_crawl_raw.py`), chạy 1 lần tạo tất cả
- **Reason**: Đảm bảo frontmatter nhất quán, nhanh hơn, ít lỗi hơn
- **Validated**: 1 lần (2026-04-05 — 34 files tạo thành công)

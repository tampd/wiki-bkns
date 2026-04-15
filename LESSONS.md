# LESSONS — BKNS Wiki Project
> Critical lessons only (importance ≥0.8, max 10 entries)
> Last updated: 2026-04-13

---

## L001 — approve_and_compile.py import lỗi module không tồn tại
- **Date**: 2026-04-05
- **Type**: experience
- **Importance**: 0.9
- **Mistake**: Script `tools/approve_and_compile.py` gọi `from skills.compile_wiki_runner import compile_category` nhưng module `skills.compile_wiki_runner` không tồn tại. Module thật nằm ở `skills/compile-wiki/scripts/compile.py`.
- **Root cause**: Tên module trong `approve_and_compile.py` bị hardcode sai, không khớp với cấu trúc thư mục thực tế (dấu `-` trong `compile-wiki` không hợp lệ cho Python import).
- **Fix**: Chạy compile trực tiếp qua `python3 skills/compile-wiki/scripts/compile.py --all` thay vì qua wrapper script.
- **Prevention**: Cần fix `approve_and_compile.py` để import đúng hoặc dùng `subprocess.run()` gọi script trực tiếp. Luôn test import path trước khi chạy pipeline dài.
- **Tags**: `pipeline`, `import-error`, `python`

## L002 — Self-review blocker: ten-mien bị blocked do hallucination detection
- **Date**: 2026-04-05
- **Type**: experience
- **Importance**: 0.85
- **Mistake**: Category `ten-mien` bị blocked lần compile đầu tiên do self-review phát hiện "1 critical hallucination".
- **Root cause**: Gemini Pro đôi khi thêm thông tin không có trong claims (ví dụ: chính sách bảo hành tên miền). Hệ thống self-review ĐÚNG khi block.
- **Fix**: Chạy lại compile lần 2 → pass (do Gemini Pro generate khác mỗi lần, lần 2 tuân thủ claims tốt hơn).
- **Prevention**: Đây là behavior mong muốn — self-review hoạt động đúng. Khi bị blocked, chỉ cần retry 1-2 lần. Nếu vẫn blocked → review claims gốc.
- **Tags**: `self-review`, `hallucination`, `compile-wiki`

## L003 — Cloudflare chặn crawl hàng loạt từ BKNS website
- **Date**: 2026-04-05
- **Type**: experience
- **Importance**: 0.85
- **Mistake**: Khi cào 71 URL liên tục bằng Tavily, Cloudflare bắt đầu chặn requests sau ~30 URLs. Nhiều trang VPS/Server trả về HTML trống (chỉ có navigation menu).
- **Root cause**: BKNS.vn sử dụng Cloudflare WAF, detect bot crawling pattern.
- **Fix**: Dữ liệu thiếu được bổ sung bằng thông tin từ Excel bảng giá (source of truth).
- **Prevention**: (1) Thêm delay giữa các requests (2) Dùng browser subagent cho trang JS-rendered (3) Không cào quá 20 URL/batch.
- **Tags**: `cloudflare`, `web-crawl`, `rate-limit`

## L004 — File cũ trong raw/website-crawl/ gây lỗi pipeline (0 claims)
- **Date**: 2026-04-05
- **Type**: experience
- **Importance**: 0.8
- **Mistake**: 2 file cũ (`hosting-2026-04-04.md`, `index-2026-04-04.md`) trong `raw/website-crawl/` bị pipeline scan và extract → 0 claims → skip. Không gây lỗi nhưng tốn thời gian xử lý.
- **Root cause**: File cào thử từ phiên trước, frontmatter có `status: pending_extract` nhưng nội dung là HTML navigation menu (không có data hữu ích).
- **Fix**: Pipeline tự skip (0 claims). Nên xóa hoặc đổi status sang `processed` cho file không cần.
- **Prevention**: Clean up raw files cũ trước khi chạy extract batch. Hoặc đổi status: `pending_extract` → `skipped` cho file rác.
- **Tags**: `pipeline`, `cleanup`, `extract`

## L005 — Giá từ Excel (source of truth) vs giá từ website có thể khác nhau
- **Date**: 2026-04-05
- **Type**: mental_model
- **Importance**: 0.9
- **Observation**: Excel bảng giá nội bộ (`Bảng giá Hosting- VPS- Email.xlsx`) là nguồn chính xác nhất. Website thường hiển thị giá đã giảm hoặc giá khuyến mãi (ví dụ: .com chỉ 25.000đ khi mua 5 năm, trong khi giá thực 379.000đ/năm).
- **Pattern**: Luôn ưu tiên giá từ Excel. Nếu conflict → ghi cả 2 giá + note "giá website có thể là giá khuyến mãi".
- **Tags**: `pricing`, `source-of-truth`, `excel`

## L006 — Helmet CSP blocks inline onclick handlers silently
- **Date**: 2026-04-05
- **Type**: experience
- **Importance**: 0.9
- **Mistake**: Upload portal buttons (view file, delete file) không hoạt động. Không có error message nào hiển thị cho user.
- **Root cause**: `helmet()` CSP mặc định `scriptSrc: ["'self'"]` KHÔNG bao gồm `'unsafe-inline'`. Tất cả `onclick="..."` attributes bị browser block silently. Chỉ thấy lỗi trong DevTools Console: "Refused to execute inline event handler because it violates CSP".
- **Fix**: Thay tất cả inline `onclick` bằng `data-action` attributes + `addEventListener()` (event delegation). KHÔNG thêm `'unsafe-inline'` vì weaken CSP.
- **Prevention**: (1) KHÔNG BAO GIỜ dùng inline event handlers khi có Helmet/CSP (2) Luôn dùng `addEventListener` hoặc event delegation (3) Test CSP compliance bằng cách check DevTools Console cho CSP violations.
- **Tags**: `csp`, `security`, `helmet`, `inline-handler`, `silent-failure`

## L007 — Code mới không có hiệu lực vì PM2 wiki-admin chưa được restart
- **Date**: 2026-04-13
- **Type**: experience
- **Importance**: 0.95
- **Mistake**: Sau khi merge `feat(review): add bulk action endpoint` (commit `a1dc75b`), endpoint `POST /api/review/bulk` đã có trên file disk nhưng frontend tại `upload.trieuphu.biz` báo "Bulk action thất bại" mỗi khi user chọn nhiều claim và bấm Duyệt/Từ chối/Flag.
- **Root cause**: PM2 daemon (`/root/.pm2`, app `wiki-admin`, PID 965697) đã chạy liên tục từ 2026-04-07 07:32 UTC, KHÔNG được reload sau khi code thay đổi. Server in-memory vẫn dùng phiên bản `web/routes/review.js` cũ (chưa có route bulk) → Express trả 404 HTML "Cannot POST /api/review/bulk" → frontend gọi `res.json()` thất bại nuốt error → toast generic "Lỗi". Verified: `curl -X POST http://127.0.0.1:3000/api/review/bulk` → HTTP 404, Content-Type `text/html`.
- **Fix**: PM2 daemon chạy dưới root → cần `sudo` + giữ PATH cho node:
  ```bash
  sudo env PATH=/home/openclaw/.nvm/versions/node/v24.14.0/bin:$PATH \
    /home/openclaw/.nvm/versions/node/v24.14.0/bin/pm2 reload wiki-admin
  ```
  (Plain `sudo pm2 ...` fails với `command not found` vì sudo strip PATH; `sudo pm2 list` cũng báo `/usr/bin/env: 'node': No such file or directory`.) Verify bằng `curl -X POST http://127.0.0.1:3000/api/review/bulk -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"action":"flag","claim_ids":["x"]}'` phải trả JSON 200 (success_count/failed_count) chứ không phải HTML 404.
- **Prevention**: (1) Mọi PR chạm `web/routes/*.js`, `web/middleware/*.js` hoặc `web/server.js` BẮT BUỘC kèm bước `sudo pm2 reload wiki-admin` trong checklist deploy. (2) Tạo script `web/restart.sh` chuẩn hoá lệnh reload + verify endpoint. (3) Frontend cần fail-loud khi server trả non-JSON: check `res.headers.get('content-type')`, nếu không phải `application/json` thì hiển thị "Endpoint không tồn tại — server cần restart" thay vì "Lỗi" generic. (4) Cân nhắc PM2 watch mode (`watch: ['routes', 'middleware', 'server.js']`) cho prod.
- **Tags**: `pm2`, `deploy`, `stale-server`, `bulk-action`, `silent-failure`, `404`, `review-queue`

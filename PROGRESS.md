# PROGRESS — BKNS Wiki Project
> Persistent session memory — KHÔNG XÓA sau /save
> Last updated: 2026-04-05

---

## Session 2026-04-05 — Cào dữ liệu web + Chạy pipeline hoàn chỉnh

### Đã hoàn thành
- [x] Cào 71 URLs từ bkns.vn, ssl.bkns.vn, server.bkns.vn (69/71 thành công)
- [x] Đọc & phân tích Excel bảng giá (5 sheets: Hosting Linux, Windows, VPS, Cloud Email, Email Hosting)
- [x] Tạo 34 raw markdown files với đúng frontmatter cho pipeline
- [x] Chạy extract-claims: 401 claims ($0.60)
- [x] Approve: 1,038 claims tổng cộng
- [x] Compile 7/7 categories (hosting, vps, ten-mien, email, ssl, server, software)
- [x] Self-review pass + auto-correct
- [x] Publish tất cả 7 wiki pages
- [x] Build snapshot v0.5 (11 files, ~12K tokens)
- [x] Ghi LESSONS.md + INSTINCTS.md

### Chi phí thực tế
| Bước | Chi phí |
|---|---|
| Extract claims | $0.60 |
| Compile + Self-review | ~$0.80 |
| **Tổng** | **~$1.40** |

### Lỗi đã gặp & fix
1. `approve_and_compile.py` import lỗi → chạy compile.py trực tiếp
2. `ten-mien` blocked do hallucination → retry thành công
3. 2 file cũ (0 claims) → auto-skip

### Wiki pages đã publish
```
wiki/products/hosting/tong-quan.md
wiki/products/vps/tong-quan.md
wiki/products/ten-mien/tong-quan.md
wiki/products/email/tong-quan.md
wiki/products/ssl/tong-quan.md
wiki/products/server/tong-quan.md
wiki/products/software/tong-quan.md
```

### Next steps
- [ ] Fix `tools/approve_and_compile.py` import path
- [ ] Cào sâu thêm trang VPS/Server bằng browser subagent (JS-rendered)
- [ ] Review và bổ sung giá chi tiết cho SSL (hiện tại chỉ có tổng hợp)
- [ ] Thiết lập cron job tự động cào + extract hàng tuần

# 10 — Bộ Skills Agent Wiki BKNS

> **Triết lý Karpathy:** "Raw data → LLM compile → Wiki → LLM query → Filing back. Mọi bước audit được."
> **Nguyên tắc:** Bot KHÔNG bịa. Bot KHÔNG ghi thẳng wiki. Bot tạo draft → admin duyệt.
> **Cập nhật:** 2026-04-04

---

## Tổng Quan Pipeline & Skills

```
bkns.vn ──→ [crawl-source] ──→ raw/
                                 │
ảnh Telegram ──→ [ingest-image] ─┘
                                 │
                                 ↓
                          [extract-claims]
                                 │
                                 ↓
                            claims/ (YAML + JSONL)
                                 │
                          ┌──────┴──────┐
                          │             │
                    [compile-wiki]  [detect-conflict]
                          │             │
                          ↓             ↓
                    wiki/.drafts/   conflicts/ → notify admin
                          │
                    [self-review] ← Bot đọc lại draft, so sánh claims
                          │
                          ↓
                    Telegram → admin preview
                          │
                    admin /duyet
                          │
                          ↓
                    wiki/ (published) → [build-snapshot]
                          │
                          ↓
                    [query-wiki] ← Flash + cached prefix
                          │
                          ↓
                    [auto-file] ← Filing câu trả lời hay
                          │
                    ┌─────┴─────┐
              [lint-wiki]  [ground-truth]
              (weekly)     (weekly)
                    │           │
                    ↓           ↓
              logs/lint/   logs/ground-truth/
                    └─────┬─────┘
                          ↓
                    Telegram report → admin review
```

## Danh Sách 10 Skills

| # | Skill | Phase | Model | Vai trò |
|---|-------|-------|-------|---------|
| 1 | `crawl-source` | 0.5 | — (script) | Thu thập dữ liệu từ bkns.vn |
| 2 | `extract-claims` | 0.5 | Pro | Trích xuất facts có cấu trúc từ raw/ |
| 3 | `compile-wiki` | 0.5 | Pro | Biên dịch claims → wiki Markdown |
| 4 | `self-review` | 0.5 | Pro | Bot tự đọc lại draft, so sánh nguồn |
| 5 | `query-wiki` | 0.5 | Flash | Trả lời câu hỏi (cached prefix) |
| 6 | `ingest-image` | 1 | Flash Vision | Extract bảng giá từ ảnh |
| 7 | `lint-wiki` | 1 | Pro | Kiểm tra mâu thuẫn, outdated |
| 8 | `ground-truth` | 1 | Flash + web | So sánh wiki vs bkns.vn live |
| 9 | `auto-file` | 2 | Flash | Filing câu trả lời hay vào wiki |
| 10 | `cross-link` | 2 | Flash | Liên kết chéo tự động |

## Quy Tắc Chung Cho Mọi Skill

### Báo Lỗi (Error Reporting)
Mọi skill khi gặp lỗi PHẢI:
1. Ghi log: `logs/errors/YYYY-MM-DD.jsonl`
2. Gửi Telegram admin: emoji + tên skill + mô tả lỗi ngắn
3. KHÔNG tiếp tục xử lý khi lỗi critical

### Phân Quyền Ghi File
- `raw/`, `logs/`, `assets/` → Bot ghi tự do
- `claims/.drafts/` → Bot ghi tự do
- `claims/approved/` → Chỉ sau review
- `wiki/.drafts/` → Bot ghi tự do
- `wiki/` (ngoài .drafts) → Chỉ sau `/duyet`

### Logging
Mọi skill ghi trace JSONL:
```jsonl
{"ts":"...","skill":"skill-name","action":"start|success|error","detail":"..."}
```

---

*Chi tiết từng skill → xem files `10a` đến `10j`*
*Pipeline diagram: xem addon.md §3*

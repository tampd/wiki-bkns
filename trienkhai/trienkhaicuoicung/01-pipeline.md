# Pipeline Tổng Thể — Luồng Dữ Liệu BKNS Agent Wiki

---

## Sơ Đồ Pipeline Đầy Đủ

```
╔══════════════════════════════════════════════════════════════════╗
║                    KARPATHY LOOP — BKNS WIKI                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  [bkns.vn]  [Telegram ảnh]  [Manual paste]                      ║
║       │             │              │                             ║
║       └─────────────┴──────────────┘                            ║
║                     │                                            ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │ INGEST LAYER│                                     ║
║              │ crawl-source│ ← /them [URL]                       ║
║              │ ingest-image│ ← gửi ảnh                          ║
║              └──────┬──────┘                                     ║
║                     │ raw/ (pending_extract)                     ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │EXTRACT LAYER│                                     ║
║              │extract-claims│ ← /extract                        ║
║              │ (Gemini Pro)│                                     ║
║              └──────┬──────┘                                     ║
║                     │ claims/.drafts/ (YAML + JSONL)             ║
║                     ▼                                            ║
║           ┌────────────────────┐                                 ║
║           │  CONFLICT DETECT   │ ← So sánh vs claims/approved/  ║
║           │  (tự động)         │ → Notify admin nếu có conflict  ║
║           └────────┬───────────┘                                 ║
║                    │                                             ║
║                    ▼                                             ║
║              ┌─────────────┐                                     ║
║              │COMPILE LAYER│                                     ║
║              │compile-wiki │ ← /compile                          ║
║              │ (Gemini Pro)│                                     ║
║              └──────┬──────┘                                     ║
║                     │ wiki/.drafts/                              ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │ SELF-REVIEW │ ← Bot tự đọc lại draft             ║
║              │ (Gemini Pro)│ → So sánh draft vs claims gốc      ║
║              │             │ → Auto-correct nếu sai             ║
║              └──────┬──────┘                                     ║
║                     │ wiki/.drafts/ (đã review)                  ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │ ADMIN /duyet│ ← Admin xem preview + approve       ║
║              └──────┬──────┘                                     ║
║                     │ wiki/ (published)                          ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │BUILD-SNAPSHOT│ ← Tự động sau /duyet              ║
║              │ (script)    │ → Hash claims + wiki → build ID    ║
║              │             │ → Git tag → cache invalidation      ║
║              └──────┬──────┘                                     ║
║                     │ build/active-build.yaml cập nhật          ║
║                     ▼                                            ║
║              ┌─────────────┐                                     ║
║              │ QUERY LAYER │                                     ║
║              │ query-wiki  │ ← /hoi hoặc tin nhắn tự nhiên      ║
║              │(Gemini Flash│                                     ║
║              │  + cached)  │                                     ║
║              └──────┬──────┘                                     ║
║                     │ logs/query-YYYY-MM-DD.jsonl               ║
║                     ▼                                            ║
║         ┌───────────────────────┐                                ║
║         │      FILING LOOP      │                                ║
║         │  auto-file (Flash)    │ ← Câu hỏi lặp ≥3 lần          ║
║         │  cross-link (Flash)   │ ← Sau compile mới             ║
║         └───────────┬───────────┘                                ║
║                     │ wiki/.drafts/faq/ (candidates)             ║
║                     ▼                                            ║
║         ┌───────────────────────┐                                ║
║         │    QUALITY LOOP       │                                ║
║         │  lint-wiki (Pro)      │ ← Cron weekly Monday 09:00    ║
║         │  ground-truth (Flash) │ ← Cron weekly Sunday 22:00    ║
║         └───────────┬───────────┘                                ║
║                     │ logs/lint/ + logs/ground-truth/            ║
║                     │ Telegram report → admin                    ║
║                     └────────────────────────────────┐           ║
║                                                      │           ║
║                          [Vòng lặp tiếp theo] ◄──────┘           ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Trạng Thái Dữ Liệu Qua Các Bước

```
raw/website-crawl/xxx.md
  status: pending_extract      → crawl-source xong
  status: extracted            → extract-claims xong
  status: compiled             → compile-wiki xong

claims/.drafts/xxx.yaml
  review_state: drafted        → vừa extract, chờ review

claims/approved/xxx.yaml
  review_state: approved       → admin đã duyệt claim

wiki/.drafts/xxx.md
  review_state: draft          → vừa compile, chờ /duyet

wiki/products/xxx.md
  review_state: approved       → admin đã /duyet, published
```

---

## Commands Admin (Telegram)

| Command | Trigger Skill | Mô tả |
|---------|---------------|-------|
| `/them [URL]` | crawl-source → ingest-raw | Thêm URL mới vào raw/ |
| `/them [text]` | ingest-raw | Paste text thủ công vào raw/ |
| `/anh` (+ ảnh) | ingest-image | Extract bảng giá từ ảnh |
| `/extract` | extract-claims | Extract claims từ raw/ pending |
| `/compile` | compile-wiki | Compile claims → wiki draft |
| `/xem-draft` | compile-wiki (list) | Xem danh sách drafts pending |
| `/duyet [file]` | compile-wiki (approve) | Approve draft → publish wiki |
| `/hoi [câu hỏi]` | query-wiki | Hỏi wiki (cũng dùng cho end users) |
| `/lint` | lint-wiki | Chạy lint kiểm tra wiki ngay |
| `/verify` | ground-truth | Verify wiki vs bkns.vn live |
| `/file-review` | auto-file | Xem FAQ candidates tuần này |
| `/crosslink` | cross-link | Chạy cross-link quét wiki |
| `/build` | build-snapshot | Tạo build snapshot thủ công |

---

## Luồng Xử Lý Lỗi Tập Trung

```
Mọi lỗi → logs/errors/YYYY-MM-DD.jsonl
        → Telegram admin: {emoji} {skill}: {mô tả ngắn}
        → KHÔNG tiếp tục xử lý nếu lỗi critical

Critical errors (dừng ngay):
  - Gemini API error > 3 lần retry
  - File không ghi được
  - Claims parse error

Warning errors (tiếp tục, log):
  - Claim thiếu field không bắt buộc
  - URL ngoài bkns.vn
  - Content hash trùng (skip im lặng)
```

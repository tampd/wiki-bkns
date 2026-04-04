# BKNS Agent Wiki — Bộ Skill Chuẩn Hóa Cuối Cùng

> **Phiên bản:** 2.0 — Chuẩn hóa 2026-04-04
> **Trạng thái:** ✅ SẴN SÀNG TRIỂN KHAI
> **Triết lý:** Karpathy LLM-Compiled Wiki — Bot KHÔNG bịa, KHÔNG ghi thẳng wiki, MỌI bước đều có audit trail

---

## MỤC LỤC

| File | Nội dung |
|------|----------|
| [00-MASTER.md](./00-MASTER.md) | Bức tranh tổng thể + ràng buộc hệ thống |
| [01-pipeline.md](./01-pipeline.md) | Pipeline tổng thể + sơ đồ luồng dữ liệu |
| [02-file-structure.md](./02-file-structure.md) | Cấu trúc thư mục + quy tắc phân quyền ghi file |
| [03-skills-registry.md](./03-skills-registry.md) | Bảng tổng hợp 10 skills + phase + model + trigger |
| [04-skill-crawl-source.md](./04-skill-crawl-source.md) | Skill 1: crawl-source |
| [05-skill-extract-claims.md](./05-skill-extract-claims.md) | Skill 2: extract-claims |
| [06-skill-compile-wiki.md](./06-skill-compile-wiki.md) | Skill 3: compile-wiki + self-review |
| [07-skill-query-wiki.md](./07-skill-query-wiki.md) | Skill 4: query-wiki (cached) |
| [08-skill-ingest-image.md](./08-skill-ingest-image.md) | Skill 5: ingest-image (Vision) |
| [09-skill-lint-wiki.md](./09-skill-lint-wiki.md) | Skill 6: lint-wiki |
| [10-skill-ground-truth.md](./10-skill-ground-truth.md) | Skill 7: ground-truth |
| [11-skill-auto-file.md](./11-skill-auto-file.md) | Skill 8: auto-file |
| [12-skill-cross-link.md](./12-skill-cross-link.md) | Skill 9: cross-link |
| [13-skill-build-snapshot.md](./13-skill-build-snapshot.md) | Skill 10: build-snapshot |
| [14-quality-gates.md](./14-quality-gates.md) | Tất cả quality gates + error handling |
| [15-automation-loops.md](./15-automation-loops.md) | Vòng lặp tự động hóa + cron jobs |

---

## PHẦN 1: BỨC TRANH TỔNG THỂ

### Dự án là gì?

**BKNS Agent Wiki** là hệ thống tri thức tự động (Knowledge Base) cho BKNS.VN, hoạt động như một "thủ thư AI" khép kín:

```
THU THẬP → TRÍCH XUẤT → BIÊN DỊCH → KIỂM TRA → PHÁT HÀNH → TRẢ LỜI → CẢI THIỆN
```

Mỗi bước đều có audit trail. Bot KHÔNG bao giờ bịa thông tin. KHÔNG bao giờ ghi thẳng vào wiki mà không qua duyệt.

### Kiến trúc cốt lõi (Karpathy Pattern)

```
KHÔNG dùng RAG / Vector DB
→ Gửi TOÀN BỘ wiki làm context prefix mỗi query
→ Tận dụng Gemini Implicit Context Caching (giảm 90% chi phí)
→ Wiki ~50-100 file ≈ 50k-100k token — vừa đủ cho 1M context window
```

### Stack kỹ thuật (ĐÃ CHỐT)

| Hạng mục | Giá trị |
|----------|---------|
| **Cloud** | Vertex AI (Gemini) |
| **Model query** | `gemini-2.5-flash` — $0.30/$2.50 per 1M in/out |
| **Model compile/lint** | `gemini-2.5-pro` — $1.25/$10 per 1M in/out |
| **Caching** | Implicit (tự động, 90% discount) |
| **Bot platform** | OpenClaw + Telegram |
| **Wiki viewer** | MkDocs Material |
| **Workspace** | `/home/openclaw/wiki/` |
| **Admin** | @phamduytam (ID: `882968821`) |

---

## PHẦN 2: NGUYÊN TẮC BẤT BIẾN

> Các nguyên tắc này KHÔNG được vi phạm dù bất kỳ lý do gì.

### 2.1 Về dữ liệu

| # | Nguyên tắc | Hệ quả |
|---|------------|--------|
| D1 | **Bot KHÔNG bịa** | Mọi fact phải có claim source |
| D2 | **Bot KHÔNG ghi thẳng wiki** | Mọi output → `.drafts/` → `/duyet` |
| D3 | **Giá tiền = risk_class: high** | Bắt buộc admin review trước khi publish |
| D4 | **1 fact = 1 claim** | Không gộp nhiều facts vào 1 claim |
| D5 | **Conflict = notify ngay** | Không tự resolve conflict về giá/specs |

### 2.2 Về automation

| # | Nguyên tắc | Hệ quả |
|---|------------|--------|
| A1 | **Self-review trước khi draft** | Bot tự kiểm tra draft vs claims gốc |
| A2 | **Audit trail đầy đủ** | JSONL trace mọi action |
| A3 | **Graceful degradation** | API down → trả lời hotline, không crash |
| A4 | **Idempotent crawl** | Hash check, không crawl lại nội dung không đổi |
| A5 | **Cache invalidation** | Wiki reload khi build thay đổi |

### 2.3 Về phân quyền

```
raw/          → Bot ghi tự do
logs/         → Bot ghi tự do
assets/       → Bot ghi tự do
claims/.drafts/ → Bot ghi tự do
wiki/.drafts/ → Bot ghi tự do

claims/approved/ → CHỈ sau admin review
wiki/ (ngoài .drafts) → CHỈ sau /duyet
```

---

## PHẦN 3: BUDGET & COST CONTROL

```
Wiki: 50k token | 100 queries/ngày

Query cached (80%):     $3.60/tháng
Query non-cached (20%): $9.00/tháng
Query output:           $3.75/tháng
Compile 8×/tháng:       $3.20/tháng
Lint 4×/tháng (Pro):    $2.75/tháng
────────────────────────────────────
TỔNG:                  ~$22.50/tháng
```

> ⚠️ **Rule tuyệt đối:** Flash cho query, Pro CHỈ cho compile/lint. Pro cho query → ~$80-120/tháng.

---

## PHẦN 4: LIÊN HỆ BKNS (GROUND TRUTH)

| Kênh | Số | Mục đích |
|------|----|---------|
| Hotline kỹ thuật 24/7 | `1900 63 68 09` | Báo lỗi, kỹ thuật (có phí) |
| Tư vấn kinh doanh | `1800 646 884` | Mua hàng, hóa đơn (miễn phí) |
| Website | `https://bkns.vn` | Live chat, tự phục vụ |

Hai số hotline này PHẢI có mặt trong mọi câu trả lời "không biết" của bot.

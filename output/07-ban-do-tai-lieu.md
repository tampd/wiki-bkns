# 07 — Bản Đồ Tài Liệu Dự Án (Document Map)

> **Mục đích:** Quy định rõ vai trò từng file, tránh trùng lặp.
> **Nguyên tắc:** Mỗi thông tin chỉ có MỘT file chủ sở hữu (SSOT). Các file khác chỉ tham chiếu.

---

## 1. Sơ Đồ Phân Vai

```
/home/openclaw/wiki/
│
├── README.md                 ← [TRỪ] Bỏ phần pricing/budget/caching chi tiết
│                                 CHỈ giữ: giới thiệu dự án, link đến các file khác
│
├── ytuongbandau.md           ← [TRỪ] Bỏ mọi số liệu pricing cụ thể
│                                 CHỈ giữ: nghiên cứu gốc, lý do kiến trúc, comparison
│                                 THAM CHIẾU: pricing → output/04
│
├── addon.md                  ← [GIỮ NGUYÊN] Hiến pháp dữ liệu — SSOT cho mọi schema/policy
│                                 Không ai copy nội dung addon.md vào file khác
│
├── bot.md                    ← [GIỮ NGUYÊN] SSOT cho workflow vận hành bot
│                                 THAM CHIẾU: schema → addon.md
│
└── output/                   ← [MỚI] Tài liệu nghiên cứu + triển khai
    │
    ├── 01-tong-hop-nghien-cuu.md     ← Đánh giá tổng quan, phát hiện
    ├── 02-ke-hoach-hanh-dong.md      ← SSOT cho lộ trình triển khai Phase 0→3
    ├── 03-skills-va-prompts.md       ← SSOT cho skill definitions, system prompts
    ├── 04-pricing-va-budget.md       ← SSOT cho MỌI con số pricing, budget
    ├── 05-cau-hoi-can-thao-luan.md   ← Câu hỏi + trả lời (archived)
    ├── 06-sai-lech-can-sua.md        ← Danh sách fix cho file gốc
    ├── 07-ban-do-tai-lieu.md         ← [FILE NÀY] Phân vai tài liệu
    └── 08-quyet-dinh-cuoi-cung.md    ← Consolidation tất cả quyết định
```

---

## 2. Ma Trận SSOT (Single Source of Truth)

| Thông tin | SSOT File | Ai copy → sai |
|-----------|-----------|---------------|
| **Giá Gemini (pricing)** | `output/04-pricing-va-budget.md` | ❌ ytuongbandau.md (cũ, sai) |
| **Budget timeline** | `output/04-pricing-va-budget.md` | ❌ README.md (cũ) |
| **Claims schema** | `addon.md` | Không copy, chỉ tham chiếu |
| **Source Authority Ladder** | `addon.md` | Không copy |
| **Build manifest spec** | `addon.md` | Không copy |
| **Bot commands** | `bot.md` → update dần | Không copy |
| **System prompts** | `output/03-skills-va-prompts.md` | Mẫu gốc |
| **Lộ trình Phase 0→3** | `output/02-ke-hoach-hanh-dong.md` | ❌ ytuongbandau.md |
| **Quyết định kiến trúc** | `output/08-quyet-dinh-cuoi-cung.md` | Tổng hợp |
| **Hotline, contact info** | Khi wiki chạy: `wiki/support/lien-he.md` | — |
| **Telegram bot token** | `output/08-quyet-dinh-cuoi-cung.md` → sau chuyển vào `.env` | — |

---

## 3. Quy Tắc Không Trùng Lặp

### 3.1. Khi cần giá Gemini
- **Đọc:** `output/04-pricing-va-budget.md` **DUY NHẤT**
- **Không đọc:** ytuongbandau.md (section 5.3) — số liệu cũ/sai

### 3.2. Khi cần schema claims/entity
- **Đọc:** `addon.md` **DUY NHẤT**
- **Không tự tạo schema mới** ở file khác

### 3.3. Khi cần biết Phase tiếp theo là gì
- **Đọc:** `output/02-ke-hoach-hanh-dong.md`
- **Không đọc:** ytuongbandau.md roadmap (phiên bản cũ)

### 3.4. Khi cần prompt cho skill
- **Đọc:** `output/03-skills-va-prompts.md`
- **Không đọc:** bot.md (có mô tả workflow nhưng không có prompt chi tiết)

---

## 4. Trạng Thái File Gốc Sau Nghiên Cứu

| File gốc | Trạng thái | Hành động cần |
|----------|-----------|--------------|
| `README.md` | 🟡 Cần cập nhật nhẹ | Sửa pricing summary, thêm link `output/` |
| `ytuongbandau.md` | 🟠 Cần sửa pricing | Đánh dấu sections cũ + link đến `04-pricing` |
| `addon.md` | 🟢 OK, không sửa | Giữ nguyên — đây là hiến pháp |
| `bot.md` | 🟢 OK tạm thời | Cập nhật khi implement Phase 1 |

---

## 5. Khi Triển Khai — Thêm Gì?

Khi bắt đầu code (Phase 0.5+), sẽ cần thêm:

```
/home/openclaw/wiki/
├── .env                      ← API keys, tokens (gitignored)
├── .gitignore                ← Bổ sung rules
├── .gitattributes            ← Git LFS config
├── agents.yaml               ← OpenClaw agent config (hoặc ~/.openclaw/)
├── skills/                    ← Custom skills
│   ├── query-wiki/
│   ├── ingest-raw/
│   └── compile-wiki/
├── raw/                       ← Dữ liệu thô
├── claims/                    ← Lớp sự thật (full schema, addon.md)
├── wiki/                      ← Wiki đã compile
├── build/                     ← Runtime snapshots
├── assets/                    ← Ảnh
├── logs/                      ← Query traces
└── mkdocs.yml                 ← MkDocs config
```

---

*Xem quyết định cuối cùng: [08-quyet-dinh-cuoi-cung.md](./08-quyet-dinh-cuoi-cung.md)*

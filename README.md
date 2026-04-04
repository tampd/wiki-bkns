# BKNS Knowledge Wiki

> **Bộ kiến thức chuẩn hóa về hệ sinh thái sản phẩm BKNS.vn**
> Được xây dựng và duy trì bởi **OpenClaw** theo phương pháp **LLM-Compiled Wiki + Gemini Implicit Context Caching**

---

## Tổng Quan Dự Án

| Thông tin | Chi tiết |
|-----------|---------|
| **Mục tiêu** | Knowledge base cho bot CSKH, bot nội bộ, và nhân viên mới của BKNS |
| **Phương pháp** | LLM-Compiled Markdown Wiki (ý tưởng Andrej Karpathy) |
| **Không dùng** | RAG, vector database |
| **Tiết kiệm token** | Gemini Implicit Context Caching (~75% savings khi query) |
| **Kênh bot** | Telegram (OpenClaw) |
| **LLM** | Gemini 2.5 Pro (compile, lint) + Gemini 2.5 Flash (query, vision extract) |
| **Ngân sách** | $300 Vertex AI — ước tính ~15–20 tháng (*cần xác nhận loại credit*) |

---

## Tại Sao Không Dùng RAG?

- Wiki BKNS ước tính ~50–150 file Markdown = **200k–500k token** sau biên dịch
- Gemini 2.5 Flash hỗ trợ **1M token context** — đủ nhét toàn bộ wiki
- **KHÔNG nhét thô mỗi query** — dùng **Gemini Implicit Context Caching**: wiki được đặt cố định ở đầu mỗi request như một prefix, Gemini tự động cache và giảm **75% chi phí** token cached
- Full-context tốt hơn RAG: không mất thông tin do chunking, suy luận đa bước chính xác hơn

---

## 3 Tính Năng Chính

### 1. 📝 Wiki Markdown Chuẩn Hóa
- Toàn bộ kiến thức BKNS được biên soạn thành Markdown có cấu trúc
- Mỗi file có metadata, nguồn trích dẫn, ngày cập nhật
- LLM (Gemini 2.5 Pro) làm "thủ thư" — tự compile, tự tổ chức, tự backlink

### 2. 📸 Quản Lý Ảnh & Bằng Chứng
- Ảnh bảng giá, note quan trọng gửi qua Telegram → tự động extract thành Markdown
- Lưu ảnh gốc full-resolution trong `assets/evidence/` (bằng chứng, Git LFS)
- Thumbnail nén trong `assets/images/` (hiển thị, Git thường)
- Gemini 2.5 Flash Vision extract bảng giá phức tạp với độ chính xác cao

### 3. ⚡ Gemini Implicit Context Caching
- Wiki được gửi như **prefix cố định** ở đầu mỗi query request
- Gemini tự động nhận diện và cache prefix lặp lại — **không cần quản lý cache thủ công**
- Tiết kiệm **~75% chi phí token input** cho các queries dùng chung wiki
- Không tốn phí lưu trữ cache (khác với Explicit Caching)

---

## Luồng Hoạt Động

```
[Nhân viên gửi ảnh bảng giá qua Telegram]
         ↓ OpenClaw nhận
[Gemini 2.5 Flash Vision] → extract bảng → Markdown
         ↓
[wiki/products/hosting/bang-gia.md] ← được cập nhật
         ↓
[wiki_content string được reload trong memory]
         ↓
[Khách hàng hỏi bot Telegram]
         ↓ Flash nhận câu hỏi
[wiki_content (prefix) + câu hỏi → Gemini 2.5 Flash]
(Implicit cache tự động giảm 75% chi phí prefix)
         ↓
[Câu trả lời] → "Theo products/hosting/bang-gia.md: Gói BKCP01 giá 26.000đ/tháng..."
```

---

## Trạng Thái

| Phase | Nội dung | Trạng thái |
|-------|----------|-----------|
| **Research** | Nghiên cứu, thiết kế kiến trúc, sửa lỗi kỹ thuật | ✅ Hoàn thành |
| **Phase 1** | Bootstrap: company/ + tên miền + hosting | ⏳ Chờ phê duyệt |
| **Phase 2** | Mở rộng: VPS + Email + SSL + ảnh bảng giá | 📋 Lên kế hoạch |
| **Phase 3** | Bán hàng: tư vấn, kịch bản, FAQ | 📋 Lên kế hoạch |
| **Phase 4** | Hoàn thiện: linting, cross-link, đo lường | 📋 Lên kế hoạch |

---

## ⚠️ Cần Xác Nhận Trước Khi Bắt Đầu

| # | Việc cần làm | Ảnh hưởng |
|---|-------------|----------|
| 1 | **Xác nhận loại $300 budget**: trial credit (hết hạn 90 ngày) hay billing credit (vô hạn)? | Timeline toàn bộ dự án |
| 2 | **Bổ sung hotline BKNS chính thức** vào `wiki/support/lien-he.md` và system prompt | Bot không thể hướng dẫn khách liên hệ đúng chỗ |
| 3 | **Xác nhận model string** của Gemini 2.5 trong OpenClaw config | agents.yaml |

---

## Tài Liệu

| File | Nội dung |
|------|---------|
| [ytuongbandau.md](./ytuongbandau.md) | 📋 Đề tài nghiên cứu đầy đủ v3: kiến trúc, caching, image mgmt, roadmap, budget (đã sửa lỗi) |

---

## Cấu Trúc Thư Mục (Dự Kiến)

```
/home/openclaw/wiki/
├── README.md            ← Bạn đang đọc file này
├── ytuongbandau.md      ← Đề tài nghiên cứu & kế hoạch (v3)
├── wiki/                ← Wiki chính (Markdown, LLM quản lý)
│   ├── index.md
│   ├── company/
│   ├── products/
│   ├── support/
│   ├── sales/
│   ├── technical/
│   └── faq/
├── raw/                 ← Dữ liệu thô chưa biên dịch
├── assets/              ← Ảnh & media (ở ROOT, không trong wiki/)
│   ├── images/          ← Thumbnail ảnh ≤100KB (Git thường)
│   └── evidence/        ← Ảnh gốc full-res (Git LFS)
└── logs/                ← Log agent, lint reports
```

---

## Công Nghệ Sử Dụng

| Công nghệ | Vai trò |
|-----------|---------|
| **Gemini 2.5 Pro** | Compile wiki, linting, reasoning phức tạp |
| **Gemini 2.5 Flash** | Query bot Telegram, extract ảnh bảng giá, classify |
| **Gemini Implicit Caching** | Cache wiki tự động, tiết kiệm ~75% token queries |
| **OpenClaw** | Orchestrator: điều phối agent, Telegram gateway, cron jobs |
| **Git + Git LFS** | Version control wiki + lưu ảnh gốc |
| **Markdown** | Format chuẩn của toàn bộ wiki |

---

*BKNS Knowledge Wiki v0.3 — Powered by OpenClaw + Gemini 2.5*
*Cập nhật: 2026-04-04 (v3 — sửa lỗi model, pricing, caching strategy, gitattributes)*


# 08 — Quyết Định Cuối Cùng (Decision Record)

> **Ngày:** 2026-04-04
> **Trạng thái:** ✅ TẤT CẢ CÂU HỎI ĐÃ TRẢ LỜI — sẵn sàng triển khai
> **Nguồn:** Tổng hợp từ 05-cau-hoi-can-thao-luan.md + phân tích bổ sung

---

## 1. Tổng Kết Quyết Định

### 1.1. Infrastructure

| Quyết định | Giá trị | Ghi chú |
|-----------|---------|---------|
| **Cloud Platform** | **Vertex AI** | Dùng $300 trial credit, không dùng AI Studio |
| **Budget** | $300 trial (90 ngày) | Ưu tiên hoàn thành nhanh, duy trì tính sau |
| **Model chính** | `gemini-2.5-pro` | Xác nhận tên model chính thức trên Vertex khi triển khai |
| **Caching** | Implicit Caching (Vertex AI) | 90% discount, tự động |

### 1.2. Bot & Channel

| Quyết định | Giá trị |
|-----------|---------|
| **Bot name** | `BKNS_Wiki_bot` |
| **Bot token** | `8790440541:AAFZLkj2l9VO_RjsB6FCmai4Ri-VK4KoIHQ` |
| **Admin Telegram** | `@phamduytam` (ID: `882968821`) |
| **Platform** | OpenClaw + Telegram |

> ⚠️ **Bảo mật:** Token trên phải chuyển vào `.env` khi triển khai, KHÔNG commit vào Git.

### 1.3. BKNS Contact Info

| Kênh | Chi tiết | Use case |
|------|---------|----------|
| **Tổng đài 24/7** | `1900 63 68 09` (mất phí) | Báo lỗi, kiểm tra hệ thống, hướng dẫn kỹ thuật |
| **Tư vấn kinh doanh** | `1800 646 884` (miễn phí) | Mua hàng, hóa đơn, dịch vụ kinh doanh |

### 1.4. Kiến Trúc & Schema

| Quyết định | Giá trị | Impact |
|-----------|---------|--------|
| **Claims schema** | **Full (Option C)** — implement 10 đối tượng từ addon.md từ đầu | Nặng hơn nhưng vững từ ngày 1 |
| **Claims format** | **Dual:** YAML (approved, human+bot readable) + JSONL (logs/traces) | Phục vụ cả con người lẫn bot learning |
| **Wiki viewer** | **MkDocs Material** | Deploy web cho nhân viên đọc |
| **Query traces** | **File log (JSONL)** | Đơn giản, không cần database |
| **Ground truth** | **Toàn bộ** (pricing + specs + contact) | Có báo cáo để admin review |
| **Onboarding** | **3 đối tượng:** nhân viên mới + khách hàng + team nội bộ | |

### 1.5. Build Activation (AI Decision — Q11)

| Quyết định | Giá trị | Lý do |
|-----------|---------|-------|
| **Build activation** | **`active-build.yaml` + Git tag** | Kết hợp cả hai: YAML cho runtime nhanh, Git tag cho audit trail |

**Chi tiết:**
- `build/active-build.yaml` — file YAML trỏ đến build snapshot hiện tại, bot đọc file này mỗi query
- Mỗi build mới → tạo Git tag `build/v1.0`, `build/v1.1`... → audit trail rõ ràng
- Rollback = đổi `active-build.yaml` trỏ về tag cũ → không cần recompile
- Đây là pattern đơn giản nhất mà vẫn đảm bảo traceability (addon.md section 14)

### 1.6. Dữ Liệu Nguồn

| Quyết định | Giá trị |
|-----------|---------|
| **Nguồn dữ liệu** | Crawl `bkns.vn` — xây wiki từ đầu |
| **Không có** dữ liệu nội bộ sẵn | FAQ, ảnh bảng giá, tài liệu nội bộ → thu thập dần |

---

## 2. Ảnh Hưởng Đến Kiến Trúc

### 2.1. Full Schema Từ Ngày 1 (Q8 = Option C)

Bạn chọn implement full addon.md schema từ đầu. Điều này thay đổi kế hoạch Phase 0.5:

**Trước (Lean MVP):**
```
Phase 0.5: Bot + 5 file wiki viết tay → query
```

**Sau (Full Schema MVP):**
```
Phase 0.5: Bot + cấu trúc đầy đủ + 5 entity + claims + wiki compiled → query
                                 ↑
                   Nặng hơn nhưng không cần refactor sau
```

#### Cấu trúc thư mục Phase 0.5 (cập nhật):

```
/home/openclaw/wiki/
├── .env                          ← Tokens, API keys
├── .gitignore
├── .gitattributes                ← Git LFS rules
├── agents.yaml                   ← OpenClaw config
│
├── raw/                          ← [addon.md §6] Dữ liệu thô
│   └── website-crawl/            ← Crawl bkns.vn
│
├── claims/                       ← [addon.md §7-8] Sự thật gốc
│   ├── registry.yaml             ← Master index claims
│   └── products/
│       ├── hosting/
│       └── ten-mien/
│
├── entities/                     ← [addon.md §10] Entity registry
│   └── registry.yaml
│
├── sources/                      ← [addon.md §9] Source registry
│   └── registry.yaml
│
├── wiki/                         ← [addon.md §11] Wiki compiled
│   ├── index.md
│   ├── company/
│   ├── products/
│   ├── support/
│   └── .drafts/                  ← Pending review
│
├── build/                        ← [addon.md §14] Runtime snapshots
│   ├── active-build.yaml
│   └── snapshots/
│
├── assets/                       ← [addon.md §—] Ảnh/media
│   ├── evidence/                 ← Git LFS, full-res
│   └── images/                   ← Compressed, web-ready
│
├── logs/                         ← Query traces (JSONL)
│
├── skills/                       ← OpenClaw custom skills
│   ├── query-wiki/
│   ├── ingest-raw/
│   └── compile-wiki/
│
├── mkdocs.yml                    ← MkDocs Material config
│
├── README.md
├── addon.md
├── bot.md
├── ytuongbandau.md
└── output/                       ← Tài liệu nghiên cứu/triển khai
```

### 2.2. MkDocs Material (Q9)

Thêm step vào Phase 1: setup MkDocs Material để nhân viên đọc wiki trên web.

```yaml
# mkdocs.yml (draft)
site_name: BKNS Knowledge Base
theme:
  name: material
  language: vi
  palette:
    - scheme: default
      primary: blue
      accent: light blue
  features:
    - search.highlight
    - navigation.instant
    - navigation.sections
docs_dir: wiki/
nav:
  - Trang chủ: index.md
  - Công ty: company/
  - Sản phẩm:
    - Hosting: products/hosting/
    - Tên miền: products/ten-mien/
  - Hỗ trợ: support/
```

### 2.3. Dual Claims Storage (Q10)

```
claims/
├── products/hosting/
│   ├── shared-hosting-pricing.yaml     ← Approved claim (human-readable)
│   └── shared-hosting-pricing.jsonl    ← Full history/trace
```

**YAML (approved, readable):**
```yaml
claim_id: CLM-HOST-001
entity: shared-hosting
attribute: pricing
value:
  basic: "36.000đ/tháng"
  business: "89.000đ/tháng"
source: SRC-BKNS-WEB-001
extracted_at: 2026-04-04
status: approved
confidence: high
approved_by: phamduytam
approved_at: 2026-04-04
```

**JSONL (append-only trace):**
```jsonl
{"ts":"2026-04-04T10:00:00Z","action":"extracted","claim_id":"CLM-HOST-001","source":"SRC-BKNS-WEB-001","raw_file":"raw/website-crawl/shared-hosting-20260404.md"}
{"ts":"2026-04-04T10:05:00Z","action":"drafted","claim_id":"CLM-HOST-001","draft_file":"wiki/.drafts/products/hosting/bang-gia.md"}
{"ts":"2026-04-04T11:00:00Z","action":"approved","claim_id":"CLM-HOST-001","by":"phamduytam","via":"telegram:/duyet CLM-HOST-001"}
```

### 2.4. Ground Truth (Q12) — Full Scope

Ground truth check sẽ verify TOÀN BỘ, không chỉ pricing:

| Loại | Tần suất | Phương pháp |
|------|----------|-------------|
| **Pricing** | Weekly | Crawl bkns.vn → compare wiki claims |
| **Specs** (RAM, CPU, SSD) | Bi-weekly | Crawl product pages → compare |
| **Contact info** | Monthly | Verify hotline, email, chat links |
| **Policies** | Monthly | Crawl terms pages |

Output: `logs/ground-truth/report-YYYY-MM-DD.md` → Telegram notification cho admin.

### 2.5. Onboarding 3 Đối Tượng (Q14)

| Đối tượng | Wiki section | Bot behavior |
|-----------|-------------|-------------|
| **Nhân viên mới** | `wiki/onboarding/nhan-vien.md` | Trả lời quy trình nội bộ, sản phẩm, chính sách |
| **Khách hàng** | `wiki/onboarding/khach-hang.md` | Hướng dẫn chọn sản phẩm, đăng ký, thanh toán |
| **Team nội bộ** | `wiki/onboarding/team-ky-thuat.md` | Kiến trúc hệ thống, deployment, troubleshooting |

---

## 3. Model Selection — Quyết Định Cuối

Bạn chọn `gemini-2.5-pro` làm model chính. Đây là model mạnh nhất nhưng **đắt nhất** ($1.25/$10 per 1M).

### 3.1. Đề Xuất Phân Vai Model (tiết kiệm budget)

| Tác vụ | Model khuyến nghị | Lý do |
|--------|-------------------|-------|
| **Query (trả lời khách)** | `gemini-2.5-flash` | Nhanh, rẻ ($0.30/$2.50), đủ cho Q&A |
| **Compile wiki** | `gemini-2.5-pro` | Cần accuracy cao khi compile claims |
| **Ingest/extract ảnh** | `gemini-2.5-flash` | Vision đủ tốt cho bảng giá |
| **Lint (kiểm tra chất lượng)** | `gemini-2.5-pro` | Cần reasoning sâu |
| **Ground truth check** | `gemini-2.5-flash` | Compare task đơn giản |

### 3.2. Budget Impact: Pro-heavy vs Flash-heavy

| Strategy | Chi phí ước tính/tháng | Budget lifetime |
|----------|----------------------|-----------------|
| **All Pro** | ~$80-120/tháng | ~2.5-3.7 tháng ❌ |
| **Pro (compile+lint) + Flash (query+ingest)** | ~$25-35/tháng | ~8.5-12 tháng ✅ |
| **All Flash** | ~$15-20/tháng | ~15-20 tháng ✅✅ |

> ⚠️ **Khuyến nghị mạnh:** Dùng **Flash cho query** (chiếm 80%+ volume) và **Pro cho compile+lint** (5-10% volume). Nếu dùng Pro cho mọi thứ, $300 chỉ đủ ~3 tháng.

---

## 4. Đánh Giá Mức Độ Khả Thi — SAU KHI TRẢ LỜI

| Tiêu chí | Trước | Sau trả lời | Status |
|----------|-------|-------------|--------|
| **Budget** | ❓ Chưa rõ loại credit | ✅ $300 trial, 90 ngày | Rõ |
| **Hotline** | ❓ Chưa có | ✅ 1900 63 68 09 + 1800 646 884 | Rõ |
| **Model** | ❓ Chưa xác nhận | ⚠️ gemini-2.5-pro (cần verify string) | Gần rõ |
| **Bot token** | ❓ Chưa có | ✅ Có sẵn | Rõ |
| **Admin** | ❓ Chưa xác nhận | ✅ @phamduytam / 882968821 | Rõ |
| **Data source** | ❓ Nội bộ hay crawl? | ✅ Crawl bkns.vn từ đầu | Rõ |
| **Schema scope** | ❓ Lean hay Full? | ✅ Full addon.md | Rõ |
| **Claims format** | ❓ | ✅ YAML + JSONL dual | Rõ |
| **Wiki viewer** | ❓ | ✅ MkDocs Material | Rõ |
| **Query log** | ❓ | ✅ JSONL file | Rõ |
| **Ground truth** | ❓ | ✅ Toàn bộ + báo cáo | Rõ |
| **Onboarding** | ❓ | ✅ 3 đối tượng | Rõ |
| **Build mechanism** | ❓ | ✅ active-build.yaml + Git tag | Rõ |
| **Platform** | ❓ | ✅ Vertex AI (dùng credit) | Rõ |

---

## 5. Kết Luận Chung

### ✅ Mức Độ Khả Thi: CAO — SẴN SÀNG TRIỂN KHAI

Tất cả 14 câu hỏi đã được trả lời. Không còn blocker nào.

**Rủi ro duy nhất còn lại:**
1. Model string `gemini-2.5-pro` cần verify trên Vertex AI khi setup
2. Budget $300 đủ ~3 tháng nếu dùng Pro cho mọi thứ → **PHẢI** dùng Flash cho query
3. Full schema từ ngày 1 (Option C) tăng thời gian Phase 0.5 từ 1 tuần → ~2 tuần

**Bước tiếp theo:** Phê duyệt → Bắt đầu Phase 0.5 (thiết lập cấu trúc + crawl bkns.vn + bot đầu tiên).

---

*Xem kế hoạch cập nhật: [02-ke-hoach-hanh-dong.md](./02-ke-hoach-hanh-dong.md)*
*Xem bản đồ tài liệu: [07-ban-do-tai-lieu.md](./07-ban-do-tai-lieu.md)*

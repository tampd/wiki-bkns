---
title: "markitdown Pilot — Comparison Report"
created: 2026-04-13
status: complete
decision: GO
---

# markitdown Pilot — Báo Cáo So Sánh

## Môi trường test
- markitdown version: **0.1.5**
- Python: 3.12 (isolated venv: `/tmp/markitdown-venv`)
- Ngày test: 2026-04-13

## Files mẫu

| # | File | Format | Size |
|---|---|---|---|
| 1 | `file1-vps.docx` — Dịch vụ Cloud VPS SSD | DOCX | 8.5 KB |
| 2 | `file2-bang-gia-vps.pdf` — Bảng giá VPS | PDF | 252 KB |
| 3 | `file3-bang-gia.xlsx` — Bảng giá Hosting/VPS/Email | XLSX | 23 KB |
| 4 | `bkns-cloud-vps-amd.html` — HTML test page | HTML | ~1 KB |

---

## Kết Quả So Sánh Chi Tiết

### File 1 — DOCX: `file1-vps.docx`

| Tiêu chí | markitdown | legacy (mammoth) | Winner |
|---|---|---|---|
| Bảng được giữ đúng | ✅ `\| --- \|` chuẩn | ❌ `\| :\-\-\- \|` (escaped) | **markitdown** |
| Danh sách lồng nhau | ✅ bullet list clean | ⚠️ bullet + backslash escape | **markitdown** |
| Heading hierarchy | ✅ headings đúng level | ✅ headings đúng level | Tie |
| Số liệu/giá tiền chính xác | ✅ `42.000đ` đúng | ✅ `42\.000đ` (escaped nhưng đúng) | Tie |
| Hình ảnh được mô tả | N/A (không có ảnh) | N/A | N/A |

**Điểm markitdown: 3/4 | legacy: 1/4**

**Ghi chú DOCX**: Legacy mammoth escape toàn bộ ký tự đặc biệt (`.`, `-`, `(`, `)`) với backslash
→ gây nhiễu cho LLM khi parse. markitdown output clean hơn đáng kể.

**Output size**: markitdown 4,513 chars vs legacy 3,705 chars (markitdown giữ nhiều context hơn)

---

### File 2 — PDF: `file2-bang-gia-vps.pdf`

| Tiêu chí | markitdown | legacy (pdfminer) | Winner |
|---|---|---|---|
| Bảng được giữ đúng | ✅ Markdown table structure | ❌ Không có bảng — text rải rác | **markitdown** |
| Danh sách lồng nhau | ✅ Grouped theo section | ❌ Line-by-line dump | **markitdown** |
| Heading hierarchy | ✅ `## 1. VPS ADM`, `## 2. VPS VM` | ⚠️ Text section header nhưng flat | **markitdown** |
| Số liệu/giá tiền chính xác | ✅ Giá gắn với gói đúng context | ⚠️ Có đủ số nhưng mất context | **markitdown** |
| Hình ảnh được mô tả | N/A (PDF không có ảnh cần mô tả) | N/A | N/A |

**Điểm markitdown: 4/4 | legacy: 0/4**

**Ghi chú PDF** — Đây là điểm cải thiện **lớn nhất**:
- pdfminer xuất 548 dòng text linearized, hoàn toàn mất cấu trúc bảng
- markitdown xuất 62 dòng có cấu trúc bảng rõ ràng, LLM có thể parse chính xác giá từng gói

**Output size**: markitdown 3,557 chars (62 lines) vs legacy 3,188 chars (548 lines — 9x nhiều dòng hơn, ít thông tin hơn)

---

### File 3 — XLSX: `file3-bang-gia.xlsx`

| Tiêu chí | markitdown | legacy | Winner |
|---|---|---|---|
| Bảng được giữ đúng | ✅ 3 sheets → 3 sections | ❌ NOT SUPPORTED | **markitdown** |
| Danh sách lồng nhau | ✅ Rows preserved | ❌ NOT SUPPORTED | **markitdown** |
| Heading hierarchy | ✅ `## VPS`, `## Hosting`, `## Email` | ❌ NOT SUPPORTED | **markitdown** |
| Số liệu/giá tiền chính xác | ✅ Đủ giá (có NaN cho ô rỗng) | ❌ NOT SUPPORTED | **markitdown** |
| Hình ảnh được mô tả | N/A | N/A | N/A |

**Điểm markitdown: 4/4 | legacy: 0/4 (format không hỗ trợ)**

**Ghi chú XLSX**:
- markitdown chuyển đổi thành công 3 sheets (VPS / Hosting / Email) với đầy đủ dữ liệu
- Có NaN cho ô merged/empty — cần post-processing cleanup trước khi đưa vào extract-claims
- Legacy pipeline hoàn toàn bỏ qua `.xlsx` files

---

### File 4 — HTML: `bkns-cloud-vps-amd.html`

```markdown
# Cloud VPS AMD – Giải pháp VPS hiệu suất cao với CPU AMD EPYC™

## Bảng giá VPS AMD

| Gói | CPU | RAM | SSD | Giá/tháng |
| --- | --- | --- | --- | --- |
| EPYC 1 | 1 Core | 1 GB | 20 GB | 165.000đ |
...
```

**Kết quả**: Perfect. Table → markdown table, headings preserved, lists preserved, href removed (plain text URLs).
Legacy: NOT SUPPORTED.

---

## Tổng Hợp Điểm

| Format | markitdown | legacy | Winner |
|---|---|---|---|
| DOCX | 3/4 | 1/4 | **markitdown** |
| PDF | 4/4 | 0/4 | **markitdown** |
| XLSX | 4/4 | 0/4 (unsupported) | **markitdown** |
| HTML | 4/4 | 0/4 (unsupported) | **markitdown** |
| **Tổng** | **15/16 (93.75%)** | **1/16 (6.25%)** | **markitdown wins** |

---

## Kiểm Tra GO/NO-GO Criteria

| Criterion | Result |
|---|---|
| markitdown ≥ legacy ở ≥ 3/5 tiêu chí | ✅ **4/4 formats — GO** |
| Output Markdown valid | ✅ Syntax chuẩn (test thủ công) |
| Không break frontmatter format hiện tại | ✅ markitdown không thêm frontmatter — `convert_manual.py` vẫn tự thêm sau conversion |

---

## Issues cần xử lý ở PART 03

1. **NaN in XLSX output**: Cells rỗng / merged → `NaN`. Cần strip `| NaN |` thành `|   |` trước khi đưa vào LLM
2. **ffmpeg absent**: Audio/video features unavailable (warning khi start). OK cho scope v0.4 (chưa xử lý audio)
3. **XLSX "Unnamed: X" headers**: Columns thiếu tên trong Excel → `Unnamed: 1`, `Unnamed: 2`. Cần identify và drop hoặc merge
4. **DOCX với custom unicode separators** (═══, ━━━): Các DOCX trong raw/manual là wiki output đã format → markitdown giữ nguyên đúng
5. **PDF table detection**: markitdown dùng `pdfplumber` cho PDF tables — tốt hơn pdfminer nhưng cần verify với PDF nhiều hình

## Rollback (nếu cần)

```bash
rm -rf /tmp/markitdown-pilot /tmp/markitdown-venv
# Không có thay đổi production
```

---

## Kết Luận

**Quyết định: GO ✅**

markitdown 0.1.5 vượt trội so với legacy pipeline trên tất cả 4 formats được test:
- DOCX: Clean output, không backslash escape noise
- PDF: Giữ cấu trúc bảng (pdfminer hoàn toàn mất cấu trúc)
- XLSX + HTML: Hai format mới hoàn toàn không được legacy hỗ trợ

**Tiếp tục sang PART 03: Refactor `convert_manual.py` → markitdown adapter.**

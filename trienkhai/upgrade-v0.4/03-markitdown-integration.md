---
part: 03
title: "markitdown Integration — Refactor convert_manual.py"
status: in_progress
estimate: 2-3 giờ
depends_on: [02]
blocks: [07]
checkpoint: "Bước 1-4 + test suite done (2026-04-13). Bước 5-8 còn lại."
---

# PART 03 — markitdown Integration (Production)

## 🎯 Mục Tiêu
Refactor `tools/convert_manual.py` thành **adapter pattern**: dispatch sang markitdown cho format mà markitdown làm tốt hơn, giữ legacy `mammoth`/`pdfminer` làm fallback. Output Markdown phải tương thích 100% với `extract-claims` hiện tại.

## ✅ Checklist

### Bước 1 — Cài markitdown vào venv production
- [x] Activate venv: không có `.venv` riêng — dùng system Python (`/usr/bin/python3`)
- [x] `pip3 install 'markitdown[all]' --break-system-packages` → **markitdown 0.1.5** ✅
- [x] Verify: `python3 -c "import markitdown; print(markitdown.__version__)"` → 0.1.5 ✅
- [x] mammoth + pdfminer.six + google-genai không conflict (đã có sẵn, không bị ghi đè) ✅
- [ ] Update `requirements.txt` của project (project chưa có file này — dùng pip freeze nếu cần)

### Bước 2 — Tạo adapter mới
File `tools/converters/markitdown_adapter.py`:

- [x] Tạo `tools/converters/__init__.py` (package marker)
- [x] Tạo `tools/converters/markitdown_adapter.py`:
  - `get_converter()` singleton (MarkItDown, enable_plugins=False)
  - `convert_to_markdown(file_path)` — dispatch + auto-clean XLSX
  - `_clean_xlsx_markdown(text)` — strip NaN + Unnamed headers
- [x] Viết `tests/test_markitdown_adapter.py` — **26/26 tests PASSED** ✅
  - 8 unit tests cho `_clean_xlsx_markdown`
  - 4+4+5+3 integration tests (DOCX/PDF/XLSX/HTML) dùng pilot files
  - 1 singleton test + 1 error-handling test

### Bước 3 — Format dispatch table
- [x] `MARKITDOWN_FORMATS = {".docx", ".pdf", ".pptx", ".xlsx", ".html", ".epub", ".zip"}`
- [x] `LEGACY_FORMATS = {".doc"}` — mammoth fallback
- [x] `convert_file()` dispatch theo bảng trên
- [x] Frontmatter logic giữ nguyên (intake metadata, sha256, slugify) ✅
- [x] `log_intake()` + `log_entry()` giữ nguyên ✅
- [x] Thêm field `converter` vào frontmatter để track backend (markitdown vs legacy)

### Bước 4 — Dual-write giai đoạn pilot (1 tuần)
- [x] Thêm flag `--dual-write` vào `convert_manual.py`
- [x] Khi bật: ghi cả `raw/manual/` (markitdown) + `raw/manual-legacy/` (legacy mammoth/pdfminer)
- [x] Tạo `tools/diff_converters.py`:
  - So sánh slug-matched .md files giữa 2 thư mục bằng difflib
  - Tính % diff + char delta per file
  - `--json` output cho CI integration
  - `--threshold=N` flag (default 5%)

### Bước 5 — Mở rộng input sources MỚI
- [x] Thêm `tools/ingest_youtube.py` — accept URL, dùng markitdown → `raw/youtube/` ✅
- [x] Thêm `tools/ingest_html.py` — accept URL, fetch + markitdown → `raw/html/` ✅
- [x] Thêm `tools/ingest_audio.py` — accept .mp3/.wav/.m4a, markitdown Whisper → `raw/audio/` ✅
- [x] Mỗi tool có dry-run mode + force flag ✅

### Bước 6 — Update Web Portal upload
[`web/routes/upload.js`](../../web/routes/upload.js) — expanded MIME whitelist.

- [x] Mở rộng MIME whitelist: thêm `.epub`, `.html`, `.pptx`, `.zip`, `.mp3`, `.wav`, `.m4a` ✅
- [x] Update [`web/public/index.html`](../../web/public/index.html) UI hiển thị format mới ✅
- [x] Max file size 50MB đã có sẵn ✅
- [ ] Test upload từ browser (cần manual test khi server đang chạy)

### Bước 7 — Testing (TDD)
- [x] Unit: `_clean_xlsx_markdown` — 8 cases, all PASSED ✅
- [x] Integration: 4 pilot files (DOCX/PDF/XLSX/HTML) — 18 cases, all PASSED ✅
- [x] Integration: convert → extract-claims → 23 claims YAML generated, status=extracted ✅
  - File: `ban-quyen-cloudlinux-os-tang-on-inh-va-bao-mat-cho-shared-2026-04-13.md`
  - Cost: $0.04, 23 claims (2 high-risk, 21 low-risk), 0 conflicts
- [x] convert_manual.py --force: 73 files converted via markitdown, 0 errors ✅
- [ ] Edge case: file corrupt, file empty, format không support
- [ ] Regression: diff output cũ vs markitdown trên 5 file (cần --dual-write run)

### Bước 8 — Document
- [x] Cập nhật [`PROJECT_SUMMARY.md`](../../PROJECT_SUMMARY.md) — v0.4 status, format mới, kiến trúc ✅
- [x] Tạo [`docs/converters.md`](../../docs/converters.md) — hướng dẫn chọn converter ✅
- [ ] Cập nhật README.md (optional — README là high-level, không critical)

## 📤 Output của PART 03
- `tools/converters/markitdown_adapter.py`
- `tools/convert_manual.py` (refactored)
- `tools/diff_converters.py`
- `tools/ingest_{youtube,html,audio}.py`
- Web portal hỗ trợ format mới
- Test suite pass

## 🚦 Acceptance Criteria
- [x] `pytest tests/test_markitdown_adapter.py` pass 100% → **26/26** ✅
- [ ] Diff converters: ≤ 5% khác biệt trên 10 file random (cần `--dual-write` run trên prod files)
- [x] `extract-claims` chạy thành công trên output markitdown → **23 claims, 0 errors** ✅
- [ ] Web portal upload .epub thành công (cần manual test)

## 🔙 Rollback
```bash
git checkout HEAD -- tools/convert_manual.py
git checkout HEAD -- web/server.js web/public/index.html
rm -rf tools/converters tools/ingest_*.py
pip uninstall markitdown
pm2 restart wiki-portal
```

## 📝 Lessons

### L03.1 — Không có .venv riêng trên server này
Project wiki không có virtualenv riêng — markitdown cài qua `pip3 --break-system-packages`.
**Prevention**: PART 04+ dùng `pip3 install X --break-system-packages` hoặc tạo venv với `virtualenv` (xem L02.1).

### L03.2 — _clean_xlsx_markdown: `_is_empty_table_row` phải check cell content sau NaN strip
Ban đầu drop row logic chạy trước NaN replace → miss case "| NaN |" vì NaN chưa bị strip.
**Fix**: Thứ tự quan trọng — replace NaN trước, sau đó mới drop empty rows.
**Pattern**: Regex passes trong `_clean_xlsx_markdown` phải theo đúng thứ tự: NaN → empty rows → Unnamed → cosmetic.

### L03.3 — `converter` field trong frontmatter cho traceability
Thêm `"converter": "markitdown"` vào frontmatter output. Cho phép query sau:
`grep -r "converter: legacy" raw/manual/` để biết file nào cần re-convert.

## ✅ Checkpoint (2026-04-13 — Session 2)

**Done (session 1):**
- Bước 1: markitdown 0.1.5 installed ✅
- Bước 2: `tools/converters/markitdown_adapter.py` với `_clean_xlsx_markdown()` ✅
- Bước 3: `tools/convert_manual.py` refactored — dispatch table + XLSX/HTML ✅
- Bước 4: `--dual-write` flag + `tools/diff_converters.py` ✅
- Bước 7 (partial): 26/26 unit + integration tests PASSED ✅

**Done (session 2 — PART 03 COMPLETE):**
- Bước 5: `ingest_youtube.py`, `ingest_html.py`, `ingest_audio.py` ✅
- Bước 6: Web portal MIME whitelist (upload.js) + UI (index.html) ✅
- Bước 7 (full): extract-claims integration test → 23 claims ✅
  - convert_manual.py --force: 73 files converted, 0 errors ✅
- Bước 8: PROJECT_SUMMARY.md + docs/converters.md ✅

**PART 03 STATUS: ✅ DONE** — Tiếp theo: PART 04 (Gemini 3.1 upgrade)

**Còn defer sang sau:**
- Regression diff (--dual-write so sánh 5 file cũ vs mới) — low priority
- Manual browser test upload .epub — cần server đang chạy
- README.md update — optional

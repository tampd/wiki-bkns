# Converters & Ingest Tools — v0.4

> Hướng dẫn chọn đúng tool để đưa tài liệu vào pipeline BKNS Wiki.

---

## Tổng Quan

Từ v0.4, pipeline hỗ trợ **15+ định dạng** nhờ markitdown backend:

| Tool | Input | Output | Thư mục |
|------|-------|--------|---------|
| `tools/convert_manual.py` | DOCX, PDF, XLSX, PPTX, EPUB, HTML (file), ZIP, DOC | `raw/manual/` | `raw/manual/` |
| `tools/ingest_youtube.py` | YouTube URL | transcript Markdown | `raw/youtube/` |
| `tools/ingest_html.py` | HTML URL | page Markdown | `raw/html/` |
| `tools/ingest_audio.py` | MP3, WAV, M4A, OGG, FLAC | transcript Markdown | `raw/audio/` |

---

## convert_manual.py — Tài Liệu Local

**Khi nào dùng**: Có file DOCX/PDF/XLSX/PPTX/EPUB trên server hoặc upload qua web portal.

```bash
# Convert tất cả file trong raw/manual/ chưa convert
python3 tools/convert_manual.py

# Overwrite output đã tồn tại
python3 tools/convert_manual.py --force

# Ghi song song legacy output để so sánh (pilot mode)
python3 tools/convert_manual.py --dual-write
```

### Format Dispatch

| Format | Backend | Ghi chú |
|--------|---------|---------|
| `.docx`, `.pdf`, `.pptx` | markitdown | Giữ bảng + danh sách |
| `.xlsx` | markitdown + `_clean_xlsx_markdown()` | Strip NaN/Unnamed tự động |
| `.html`, `.epub`, `.zip` | markitdown | HTML trực tiếp, EPUB chapter-by-chapter |
| `.doc` | mammoth (legacy) | markitdown chưa hỗ trợ binary .doc |

### Traceability

Frontmatter của mọi output đều có field `converter`:
```yaml
converter: markitdown   # hoặc "legacy"
```

Dùng để query: `grep -r "converter: legacy" raw/manual/` tìm file cần re-convert.

---

## ingest_youtube.py — YouTube Transcript

**Khi nào dùng**: Video YouTube về sản phẩm BKNS có phụ đề (auto hoặc thủ công).

```bash
python3 tools/ingest_youtube.py https://www.youtube.com/watch?v=VIDEO_ID
python3 tools/ingest_youtube.py https://youtu.be/VIDEO_ID --dry-run
python3 tools/ingest_youtube.py URL --force   # overwrite
```

**Yêu cầu**: Video phải có phụ đề. markitdown dùng `youtube-transcript-api` — không cần API key.

**Output**: `raw/youtube/YYYY-MM-DD/youtube-{VIDEO_ID}-YYYY-MM-DD.md`

---

## ingest_html.py — Trang Web

**Khi nào dùng**: Trang thông tin sản phẩm/chính sách trên website ngoài chưa được crawl.

```bash
python3 tools/ingest_html.py https://bkns.vn/chinh-sach-bao-hanh/
python3 tools/ingest_html.py URL --dry-run
python3 tools/ingest_html.py URL --force
```

**Lưu ý**: Không dùng cho crawl hàng loạt — dùng `tools/crawl_bkns.py` cho việc đó.

**Output**: `raw/html/YYYY-MM-DD/html-{slug}-YYYY-MM-DD.md`

---

## ingest_audio.py — Ghi Âm / Podcast

**Khi nào dùng**: Ghi âm cuộc họp, webinar, hoặc podcast về sản phẩm BKNS.

```bash
python3 tools/ingest_audio.py /path/to/recording.mp3
python3 tools/ingest_audio.py /path/to/audio.wav --dry-run
python3 tools/ingest_audio.py /path/to/audio.mp3 --force
```

**Backend**: markitdown dùng openai-whisper. Cần `OPENAI_API_KEY` trong `.env` để dùng Whisper API, hoặc cài `openai-whisper` package để chạy cục bộ.

**Supported formats**: `.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`

**Output**: `raw/audio/YYYY-MM-DD/audio-{slug}-YYYY-MM-DD.md`

---

## Web Portal Upload

Upload qua `http://localhost:3000` hỗ trợ tất cả format trên (v0.4+):

| Nhóm | Extensions |
|------|------------|
| Documents | `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.epub`, `.html`, `.zip` |
| Text | `.md`, `.txt` |
| Audio | `.mp3`, `.wav`, `.m4a` |
| Images | `.png`, `.jpg`, `.jpeg` |

Max file size: **50MB**. Max files/upload: **10**.

---

## So Sánh Chất Lượng (markitdown vs legacy)

Kết quả pilot (PART 02, 2026-04-13):

| Tiêu chí | markitdown | Legacy (mammoth/pdfminer) |
|----------|-----------|--------------------------|
| Bảng Markdown | ✅ Giữ nguyên cấu trúc | ❌ Escaped hoặc mất |
| Danh sách lồng nhau | ✅ Đúng indent | ⚠️ Flattened |
| PDF bảng giá | ✅ Tables intact | ❌ Text linearized |
| XLSX multi-sheet | ✅ Separate sections | N/A |
| File size overhead | ~20% lớn hơn | Cơ sở |

**Kết luận**: markitdown cho ra Markdown quality tốt hơn đáng kể cho tất cả format đã test.

---

## Troubleshooting

**markitdown trả về rỗng**:
- PDF bị scan (không có text layer) → cần OCR trước
- DOCX bị password-protect → gỡ mật khẩu trước
- File bị corrupt → thử mở bằng Word/LibreOffice trước

**Whisper lỗi** (`ingest_audio.py`):
- Chưa có `OPENAI_API_KEY` và chưa cài `openai-whisper` locally
- Cài: `pip3 install openai-whisper --break-system-packages`

**YouTube transcript không có**:
- Video không có phụ đề → không thể transcribe
- Video private/age-restricted → transcript API bị chặn

---

*Cập nhật: 2026-04-13 | PART 03 — upgrade-v0.4*

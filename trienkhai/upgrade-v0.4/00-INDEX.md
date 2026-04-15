---
title: "Upgrade v0.4 — Master Index"
version: 0.4-plan
status: draft
created: 2026-04-13
owner: openclaw
mục_tiêu: "Tăng độ chính xác wiki BKNS qua 3 thay đổi: markitdown ingestion + Gemini 3.1 Pro + GPT-5.4 cross-vote"
---

# 📚 Upgrade Plan v0.4 — BKNS Agent Wiki

> **Triết lý**: Chia thành 8 PART nhỏ tự đóng kín. Mỗi PART có thể chạy độc lập trong 1 phiên Claude Code (≤ 80% context). Không PART nào phụ thuộc state của session khác — tất cả checkpoint ghi vào file.

---

## 🎯 Mục Tiêu Cốt Lõi

| # | Mục tiêu | Lý do |
|---|---|---|
| 1 | **Mở rộng input** từ DOCX/PDF → 15+ formats (YouTube, audio, EPUB, HTML, ZIP, image+EXIF) | Tăng khối lượng dữ liệu đào tạo bot |
| 2 | **Nâng độ chính xác** từ 1 LLM tự review → 2 LLM cross-vote | Loại bỏ hallucination, giảm conflict |
| 3 | **Nâng cấp Gemini 2.5 Pro → 3.1 Pro** | Reasoning mạnh hơn, 1M context, giá thấp hơn 2.5 Pro |
| 4 | **Bảo toàn pipeline** 7 tầng hiện có ($6.50, 2,252 claims, bot live) | Không phá MVP đang chạy |

---

## 📊 Baseline (chốt ngày 2026-04-13)

| Metric | Hiện tại | Sau v0.4 (target) |
|---|---|---|
| Raw files | 291 (chỉ DOCX/PDF) | 291 + sources mới (YouTube/HTML/audio) |
| Claims approved | 2,252 | ≥ 2,500 (sau cross-vote lọc) |
| Wiki pages | 213 | 213 (không thêm/bớt — chỉ tăng accuracy) |
| LLM cho extract/compile | Gemini 2.5 Pro (đơn) | Gemini 3.1 Pro + GPT-5.4 (vote) |
| Conflict detection | 25 conflicts (manual) | Auto-flagged khi 2 model bất đồng |
| Cost/build | $6.50 | dự kiến $9-12 (do 2 model) |

---

## 🗂️ Cấu Trúc PART

| PART | File | Mô tả | Ước tính | Phụ thuộc |
|---|---|---|---|---|
| 01 | `01-survey-baseline.md` | Chốt số liệu hiện tại + audit risk | 30 phút | — |
| 02 | `02-markitdown-pilot.md` | Cài + test markitdown trên 3 file mẫu (isolated) | 1 giờ | 01 |
| 03 | `03-markitdown-integration.md` | Refactor `convert_manual.py` → markitdown adapter | 2-3 giờ | 02 |
| 04 | `04-gemini-3.1-upgrade.md` | Đổi `MODEL_PRO` + retest extract/compile | 1-2 giờ | 01 |
| 05 | `05-openai-oauth-setup.md` | Tạo OpenAI client wrapper + lưu API key an toàn | 1 giờ | 01 |
| 06 | `06-dual-agent-voting.md` | Skill `dual-vote` so sánh Gemini vs GPT, output consensus | 4-6 giờ | 04 + 05 |
| 07 | `07-regression-test.md` | Re-run 7 categories cũ, so sánh wiki v0.3 vs v0.4 | 2 giờ | 06 |
| 08 | `08-production-rollout.md` | PM2 deploy + monitor + rollback plan | 1 giờ | 07 |
| 99 | `99-CHECKLIST-MASTER.md` | Quick-reference checklist tổng hợp | — | — |

**Tổng ước tính**: 12-17 giờ làm việc, chia 4-6 phiên Claude Code.

---

## 🔄 Quy Trình Chạy (theo APEX v12.0)

Mỗi PART bắt buộc theo trình tự:

1. **Đọc PART file** → load context cho phiên đó
2. **`/spec`** (nếu PART chưa có spec đầy đủ) → bổ sung chi tiết kỹ thuật
3. **`/build`** → TDD implement
4. **`/review`** → code quality + security
5. **`/test`** → verify trên data thực
6. **Cập nhật checklist trong PART file** → đánh dấu `[x]` các step done
7. **Ghi chú "Lessons" cuối file PART** → cho phiên sau và LESSONS.md

---

## 🛡️ Nguyên Tắc An Toàn

- **Branch test**: Mọi thay đổi tạo branch `upgrade-v0.4-partXX` riêng (sau khi git init)
- **Snapshot trước**: Build snapshot v0.3 → `build/snapshots/v0.3-pre-upgrade/` (immutable backup)
- **Dual-write giai đoạn pilot**: PART 03-06 ghi song song output cũ + mới để diff
- **Rollback 1-click**: Mỗi PART có command rollback ở cuối file
- **Cost guard**: Set hard limit $20 cho v0.4 testing; trigger alert nếu vượt $15

---

## 📞 Gọi PART Tiếp Theo

Khi mở phiên mới:

```
/start Đọc trienkhai/upgrade-v0.4/00-INDEX.md và file PART_NN.md, tiếp tục từ checkpoint cuối cùng
```

---

## 🔑 Models đã Verify (web search 2026-04-13)

- **Gemini 3.1 Pro**: `gemini-3.1-pro-preview` trên Vertex AI
  - Pricing: $2/$0.20 input (cached), $12 output per 1M tokens
  - 1M context window, multimodal (text/audio/image/video/PDF/code)
- **OpenAI GPT-5.4**: `gpt-5.4` (default cho important work + coding)
  - Có biến thể `gpt-5.4-mini` rẻ hơn cho task đơn giản
  - Cần OpenAI API key (Bearer token), không phải OAuth ⚠️ — xem PART 05

---

## 📝 Ghi Chú Quan Trọng

> [!WARNING]
> **Về "OAuth ChatGPT"**: OpenAI API hiện dùng **Bearer API key**, không phải OAuth flow như Google. PART 05 sẽ giải thích kỹ và đề xuất phương án an toàn (env var + secret rotation).

> [!IMPORTANT]
> **Về "voting 2 agent"**: Đây là cross-validation pattern, không phải consensus mining. Nếu 2 model bất đồng → flag để human review (không tự động chọn). Chi tiết PART 06.

> [!NOTE]
> **Token budget mỗi PART**: Mỗi PART file ≤ 400 dòng để phiên Claude Code có thể load + thực thi mà không vượt context.

# 🧭 BKNS Agent Wiki — Hướng Dẫn Đọc Dự Án (AI Onboarding Guide)

> **Mục đích**: Cho AI khác đọc nhanh để hiểu toàn bộ dự án, kiểm tra chéo, phát hiện thiếu sót.
> **Workspace**: `/wiki/`
> **Ước tính tokens nếu đọc đúng cách**: ~15,000-20,000 tokens (thay vì 500,000+ nếu đọc hết)

---

## 📖 THỨ TỰ ĐỌC (ưu tiên từ trên xuống)

### Layer 1: Bắt buộc đọc (hiểu 80% dự án)

| # | File | Tokens ≈ | Lý do |
|---|------|----------|-------|
| 1 | `PROJECT_SUMMARY.md` | ~3,000 | **Đọc đầu tiên** — tổng kết toàn bộ dự án, kiến trúc, status, issues, roadmap |
| 2 | `.env` | ~50 | Biến môi trường, credentials, models đang dùng |
| 3 | `lib/config.py` | ~300 | Cấu hình paths, constants, logic phân luồng |
| 4 | `build/active-build.yaml` | ~50 | Build hiện tại (version, hash, token count) |
| 5 | `ecosystem.config.js` | ~50 | PM2 config cho bot daemon |

**→ Tổng Layer 1: ~3,500 tokens — hiểu 80% dự án**

---

### Layer 2: Nên đọc (hiểu logic code)

| # | File | Tokens ≈ | Nội dung |
|---|------|----------|----------|
| 6 | `lib/gemini.py` | ~800 | Vertex AI wrapper — cách gọi Gemini Pro/Flash |
| 7 | `lib/utils.py` | ~500 | YAML/Markdown helpers, frontmatter parsing |
| 8 | `lib/logger.py` | ~200 | Structured logging (JSONL) |
| 9 | `lib/telegram.py` | ~200 | Telegram notification |
| 10 | `bot/wiki_bot.py` | ~600 | Telegram bot handler — commands /hoi, /status, /build |
| 11 | `skills/extract-claims/scripts/extract.py` | ~1,200 | **Core**: extract claims từ markdown bằng Gemini Pro |
| 12 | `skills/compile-wiki/scripts/compile.py` | ~1,000 | **Core**: compile claims → wiki + self-review |
| 13 | `skills/query-wiki/scripts/query.py` | ~600 | **Core**: query wiki bằng Gemini Flash |
| 14 | `skills/build-snapshot/scripts/snapshot.py` | ~400 | Build versioning + snapshot |
| 15 | `tools/approve_and_compile.py` | ~300 | Pipeline tool: approve → compile → build |
| 16 | `tools/convert_manual.py` | ~400 | DOCX/PDF → Markdown converter |

**→ Tổng Layer 2: ~6,200 tokens — hiểu 100% logic code**

---

### Layer 3: Đọc 1 sample là đủ (hiểu format dữ liệu)

| # | Đọc file nào | Tokens ≈ | Đại diện cho |
|---|--------------|----------|--------------|
| 17 | `raw/manual/positivessl-dv-chung-chi-ssl-gia-re-2026-04-04.md` | ~300 | 72 raw markdown files |
| 18 | `claims/approved/products/ssl/` → đọc 1 file `.yaml` bất kỳ | ~50 | 809 claim YAML files |
| 19 | `wiki/products/hosting/tong-quan.md` | ~500 | 7 compiled wiki pages |
| 20 | `wiki/products/vps/tong-quan.md` | ~500 | VPS wiki (nhiều data nhất) |

**→ Tổng Layer 3: ~1,350 tokens**

---

### Layer 4: Chỉ đọc khi cần kiểm tra thiết kế gốc

| # | File | Tokens ≈ | Nội dung |
|---|------|----------|----------|
| 21 | `trienkhai/trienkhaicuoicung/00-MASTER.md` | ~800 | Master deployment plan |
| 22 | `trienkhai/trienkhaicuoicung/01-pipeline.md` | ~400 | Pipeline architecture |
| 23 | `trienkhai/trienkhaicuoicung/02-file-structure.md` | ~300 | Cấu trúc file thiết kế |
| 24 | `trienkhai/trienkhaicuoicung/03-skills-registry.md` | ~300 | Registry 10 skills |
| 25 | `trienkhai/trienkhaicuoicung/14-quality-gates.md` | ~200 | Quality gates & self-review |

**→ Tổng Layer 4: ~2,000 tokens — chỉ đọc khi cần cross-check spec vs implementation**

---

### Layer 5: SKILL.md files (mô tả chức năng mỗi skill)

| File | Tokens ≈ |
|------|----------|
| `skills/extract-claims/SKILL.md` | ~200 |
| `skills/compile-wiki/SKILL.md` | ~200 |
| `skills/query-wiki/SKILL.md` | ~200 |
| `skills/build-snapshot/SKILL.md` | ~150 |
| `skills/crawl-source/SKILL.md` | ~150 |
| `skills/ingest-image/SKILL.md` | ~150 |
| `skills/lint-wiki/SKILL.md` | ~150 |
| `skills/ground-truth/SKILL.md` | ~150 |
| `skills/auto-file/SKILL.md` | ~150 |
| `skills/cross-link/SKILL.md` | ~150 |

**→ Tổng Layer 5: ~1,650 tokens — đọc khi cần hiểu spec từng skill**

---

## 🚫 KHÔNG NÊN ĐỌC (tốn token, không có giá trị review)

| Thư mục/File | Số files | Lý do SKIP |
|--------------|----------|------------|
| `raw/manual/*.md` | 72 files | Dữ liệu thô đã convert — chỉ cần đọc 1 sample |
| `raw/crawl/` | ~varies | Crawled pages, mostly empty do Cloudflare block |
| `claims/.drafts/products/**/*.yaml` | 809 files | Trùng với approved — chỉ cần đọc 1 sample |
| `claims/approved/products/**/*.yaml` | 809 files | Claims đã approve — chỉ cần đọc 1 sample |
| `logs/*.jsonl` | ~15 files | Audit logs — dùng grep khi cần, không đọc hết |
| `build/snapshots/` | ~3 files | Concatenated wiki text — đã có wiki/products/ |
| `build/manifests/*.yaml` | 3 files | Build history — chỉ cần active-build.yaml |
| `tampd_skill/` | ~50+ files | **Không liên quan** — skill templates của hệ thống khác |
| `trienkhai/00-*.md` đến `trienkhai/07-*.md` | 8 files | Design docs cũ, đã thay thế bởi `trienkhaicuoicung/` |
| `trienkhai/10a-*.md` đến `trienkhai/10f-*.md` | 6 files | Skill specs cũ, đã implement trong skills/ |
| `wiki/.drafts/` | 7 files | Drafts đã publish lên wiki/products/ |
| `logs/wiki-bot-*.log` | 3 files | PM2 bot logs — chỉ grep khi debug |
| `Todo.md` | 1 file | Outdated — thay bằng PROJECT_SUMMARY.md |
| `addon.md`, `bot.md`, `ytuongbandau.md` | 3 files | Brainstorm notes cũ, không cần review |
| `agents.yaml` | 1 file | Agent config sơ khai, không dùng |

---

## ✅ CHECKLIST KIỂM TRA CHÉO

AI reviewer nên kiểm tra các mục sau:

### Kiến trúc & Code
- [ ] `lib/gemini.py` có handle rate limits, retries đúng không?
- [ ] `extract.py` → JSON parser có robust đủ cho edge cases?
- [ ] `compile.py` → self-review prompt có đủ strict?
- [ ] `query.py` → context caching có hoạt động?
- [ ] `wiki_bot.py` → có xử lý error gracefully? Timeout?
- [ ] `.env` → credentials có secure? Không hard-code?

### Dữ liệu
- [ ] 7 wiki pages — giá tiền, thông số có khớp nguồn gốc?
- [ ] 25 conflicts đã detect — cần resolve?
- [ ] `other` (19 claims) + `uncategorized` (12 claims) chưa compile
- [ ] Email claims bị phân loại vào hosting — có ảnh hưởng?

### Security
- [ ] `.env` không commit vào git?
- [ ] Telegram bot token có bị expose?
- [ ] Vertex AI key path có đúng?
- [ ] Bot chỉ cho admin chạy /build và /lint?

### Vận hành
- [ ] PM2 đã save → auto-restart khi reboot?
- [ ] Log rotation — JSONL logs có bị phình?
- [ ] Không có cron job nào cho lint/ground-truth

---

## 🎯 PROMPT GỢI Ý CHO AI REVIEWER

```
Bạn là AI reviewer. Hãy đọc các file sau theo thứ tự ưu tiên trong 
/wiki/ để kiểm tra chéo dự án BKNS Agent Wiki:

1. Đọc PROJECT_SUMMARY.md để hiểu tổng quan
2. Đọc .env để hiểu config
3. Đọc lib/config.py → lib/gemini.py → lib/utils.py
4. Đọc 3 core skills: extract.py → compile.py → query.py
5. Đọc bot/wiki_bot.py
6. Đọc 2 wiki pages mẫu: wiki/products/hosting/tong-quan.md + vps/tong-quan.md
7. Đọc 1 claim mẫu: bất kỳ file .yaml trong claims/approved/products/ssl/

KHÔNG ĐỌC: raw/manual/ (72 files), claims/ (809 files), logs/, 
tampd_skill/, build/snapshots/, trienkhai/00-07 (docs cũ).

Sau khi đọc, hãy:
1. Liệt kê các lỗ hổng bảo mật
2. Kiểm tra logic extract → compile → query có nhất quán không
3. Đánh giá chất lượng wiki output vs claims input
4. Đề xuất cải thiện kiến trúc
5. Phát hiện code smell hoặc bugs tiềm ẩn
```

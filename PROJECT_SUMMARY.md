# 📚 BKNS Agent Wiki — Tổng Kết Dự Án

> **Trạng thái**: Production-ready — Bot đang chạy trên PM2  
> **Build hiện tại**: v0.4 — markitdown + dual-vote (Gemini + GPT-5.4)  
> **Tổng chi phí**: $6.50 (v0.3 baseline); v0.4 pending regression test  
> **Ngày cập nhật**: 2026-04-14  
> **v0.4**: markitdown (15+ formats) + dual-vote cross-validation + Gemini 3.1 Pro ready

---

## 1. Tổng Quan Dự Án

BKNS Agent Wiki là **bot thủ thư tự động** cho BKNS.VN, sử dụng mô hình **Karpathy Pattern** (LLM-compiled knowledge, không RAG). Bot extract tri thức từ tài liệu thủ công, compile thành wiki có kiểm duyệt, và trả lời câu hỏi qua Telegram.

### Kiến trúc

```
Tài liệu / Media (DOCX/PDF/XLSX/PPTX/EPUB/HTML/ZIP/MP3/WAV/YouTube)
    ↓ convert_manual.py  [markitdown backend, v0.4+]
    ↓ ingest_youtube.py / ingest_html.py / ingest_audio.py
Markdown files (raw/manual/ | raw/youtube/ | raw/html/ | raw/audio/)
    ↓ extract-claims (Gemini Pro)
YAML claims (claims/.drafts/)
    ↓ approve (batch/manual)
Approved claims (claims/approved/)
    ↓ compile-wiki (Gemini Pro + Self-Review)
Wiki pages (wiki/products/)
    ↓ build-snapshot
Snapshot (build/snapshots/)
    ↓ query-wiki (Gemini Flash + Context Caching)
Telegram Bot ← User hỏi
```

### Kiến trúc v0.4 (Dual-Vote)

```
Tài liệu / Media (DOCX/PDF/XLSX/PPTX/EPUB/HTML/ZIP/MP3/WAV/YouTube)
    ↓ markitdown_adapter.py  [v0.4 — 15+ formats]
Markdown files (raw/)
    ↓ extract_dual.py        [Gemini Pro + GPT-5.4 → AGREE/PARTIAL/DISAGREE]
    ↓ .review-queue/         [DISAGREE → human review]
Approved claims (claims/approved/)
    ↓ compile_dual.py        [Gemini Pro + GPT-5.4 dual-vote compile]
Wiki pages (wiki/products/)
    ↓ build-snapshot
Snapshot (build/snapshots/)
    ↓ query-wiki (Gemini Flash + Context Caching)
Telegram Bot ← User hỏi
```

### Tech Stack
- **AI**: Vertex AI — Gemini 2.5 Pro (extract/compile) + Gemini 2.5 Flash (query)
- **AI (v0.4)**: Dual-vote — Gemini 2.5/3.1 Pro **+** OpenAI GPT-5.4 cross-validation
- **Bot**: Telegram long polling (Python)
- **Process Manager**: PM2 (auto-restart on crash/reboot)
- **Storage**: Local YAML/Markdown + JSONL audit logs
- **Auth**: Vertex AI service account + OpenAI API key (env var)

---

## 2. Các Phiên Làm Việc

### Phiên 1-2: Nghiên cứu & Thiết kế
- Phân tích yêu cầu BKNS
- Thiết kế kiến trúc multi-agent
- Chọn Karpathy Pattern thay vì RAG truyền thống
- Viết spec đầy đủ tại `/wiki/trienkhai/`

### Phiên 3: Scaffold & Foundation
- Tạo cấu trúc dự án tại `/wiki/`
- Implement 5 shared libraries:
  - `lib/config.py` — Environment & paths
  - `lib/gemini.py` — Vertex AI wrapper (Gemini Pro/Flash)
  - `lib/logger.py` — JSONL structured logging
  - `lib/telegram.py` — Bot notification
  - `lib/utils.py` — YAML/Markdown helpers

### Phiên 4: Skills Implementation (10 skills)
| # | Skill | Chức năng | Trạng thái |
|---|-------|-----------|------------|
| 1 | `crawl-source` | Crawl URL (bị Cloudflare block) | ⚠️ Chỉ dùng thủ công |
| 2 | `extract-claims` | Extract claims từ markdown | ✅ Hoạt động |
| 3 | `compile-wiki` | Compile claims → wiki + self-review | ✅ Hoạt động |
| 4 | `query-wiki` | Trả lời câu hỏi từ wiki | ✅ Hoạt động |
| 5 | `build-snapshot` | Đóng gói build + versioning | ✅ Hoạt động |
| 6 | `ingest-image` | Gemini Vision extract bảng giá | 🔲 Chưa test thực tế |
| 7 | `lint-wiki` | Kiểm tra chất lượng wiki | ✅ Syntax pass |
| 8 | `ground-truth` | Verify claims vs website | ⚠️ Bị block bởi Cloudflare |
| 9 | `auto-file` | Phát hiện FAQ tự động | 🔲 Chưa test thực tế |
| 10 | `cross-link` | Liên kết chéo giữa wiki pages | 🔲 Chưa test thực tế |

### Phiên 5-6 (Hiện tại): Data Ingestion & Deployment
- Convert 74 tài liệu DOCX/PDF → Markdown
- Fix JSON parser (3-strategy fallback)
- Fix `Part.from_text()` keyword arg cho Google GenAI SDK
- Extract toàn bộ 74 files → **1,326 claims**
- Compile 7 categories → 7 wiki pages
- Deploy bot qua PM2 với auto-restart

---

## 3. Trạng Thái Hiện Tại

### 📊 Số liệu hệ thống

| Metric | Giá trị |
|--------|---------|
| Tài liệu nguồn | 74 files (72 MD + 2 empty) |
| Claims trích xuất | 1,326 |
| Claims approved | 809 |
| Wiki categories | 7 (hosting, ssl, vps, ten-mien, email, server, software) |
| Wiki pages | 7 tong-quan.md + 2 system |
| Wiki tokens | ~13,786 |
| Build version | v0.6 (app version v1.1.0) |
| Bot status | ✅ PM2 online (auto-restart) |

### 📄 Chi tiết Wiki Pages

| Category | Lines | Words | Claims dùng | Self-review |
|----------|-------|-------|-------------|-------------|
| hosting | 163 | 1,265 | 192 | ✅ Pass |
| vps | 136 | 1,363 | 166 | ✅ Pass |
| ssl | 98 | 960 | 143 | ✅ Pass |
| ten-mien | 107 | 988 | 123 | ⚠️ 1 correction |
| email | 112 | 826 | 68 | ✅ Pass |
| server | 125 | 1,205 | 63 | ⚠️ 1 correction |
| software | 66 | 440 | 23 | ✅ Pass |

### 💰 Chi phí Vertex AI

| Hoạt động | Chi phí |
|-----------|---------|
| Extract claims (74 files) | $4.89 |
| Compile wiki (7 categories × 2 calls) | $1.57 |
| Query test | $0.02 |
| **Tổng** | **$6.50** |
| **Chi phí mỗi query** | **~$0.007** |

### 🤖 Telegram Bot

| Lệnh | Chức năng | Trạng thái |
|-------|-----------|------------|
| `/hoi [câu hỏi]` | Hỏi wiki | ✅ |
| Text trực tiếp | Auto-hỏi (không cần /hoi) | ✅ |
| `/status` | Xem trạng thái hệ thống | ✅ |
| `/build` | Tạo build mới (admin only) | ✅ |
| `/lint` | Kiểm tra chất lượng (admin only) | ✅ |
| `/help` | Hướng dẫn sử dụng | ✅ |

---

## 4. ⚠️ Các Vấn Đề Cần Xử Lý

### 🔴 Ưu tiên cao

> [!WARNING]
> **4.1. Claims chưa approved đầy đủ**
> 
> - Approved: 809 claims, nhưng Drafts cũng có 809 (bản copy)
> - `other` (19) và `uncategorized` (12) chưa được compile
> - **Action**: Compile thêm 2 category này hoặc gộp vào category chính

> [!WARNING]
> **4.2. Dữ liệu có thể trùng lặp**
> 
> Extract đã detect **25 conflicts** — các claims có thể mâu thuẫn nhau (ví dụ: cùng sản phẩm nhưng giá khác nhau từ các nguồn khác nhau).
> - **Action**: Chạy `grep -r "conflict" claims/.drafts/` để xem chi tiết, resolve thủ công

> [!WARNING]
> **4.3. Context Caching chưa hoạt động**
> 
> Mỗi query hiện tại cache hit = 0% → tốn ~$0.007/query. Cần enable Implicit Context Caching (Gemini API sẽ tự cache nếu cùng system instruction + cùng prefix trong 5 phút).
> - **Action**: Cần có traffic đủ dày để trigger auto-caching, hoặc tạo explicit cache

### 🟡 Ưu tiên trung bình

> [!IMPORTANT]
> **4.4. Cloudflare block → không crawl tự động**
> 
> BKNS.VN có Cloudflare protection → `crawl-source` và `ground-truth` không hoạt động.
> - **Workaround hiện tại**: Copy thủ công DOCX/PDF vào `raw/manual/`
> - **Action tương lai**: Dùng Playwright headless hoặc xin whitelist IP

> [!IMPORTANT]
> **4.5. Chất lượng compile chưa được review thủ công**
> 
> Self-review (AI) đã pass, nhưng chưa có human review.
> - **Action**: Đọc qua 7 file `wiki/products/*/tong-quan.md`, kiểm tra:
>   - Giá tiền có đúng không?
>   - Thông số kỹ thuật có khớp BKNS thực tế?
>   - Hotline/email đúng?

> [!NOTE]
> **4.6. 3 skills chưa test thực tế**
> 
> - `ingest-image`: Chưa test với screenshot bảng giá thực
> - `auto-file`: Chưa test phát hiện FAQ tự động
> - `cross-link`: Chưa chạy để liên kết wiki pages
> - **Action**: Test từng skill khi cần mở rộng

### 🟢 Ưu tiên thấp

- **Cron jobs**: Chưa setup cho ground-truth và lint tự động
- **Monitoring**: Chưa có alert khi bot crash ngoài PM2 restart
- **Git**: Chưa init git repo cho version control wiki data
- **2 file empty**: `hosting-2026-04-04.md` và `index-2026-04-04.md` extract được 0 claims (file trống/index page)

---

## 5. 🗺️ Roadmap Tiếp Theo

### Phase 1: Ổn định (1-2 ngày)
- [ ] **Test bot qua Telegram** — gửi 10-20 câu hỏi thực tế
- [ ] **Human review** 7 wiki pages — kiểm tra giá/thông số
- [ ] **Resolve 25 conflicts** — xử lý claims mâu thuẫn
- [ ] **Compile `other` + `uncategorized`** — 31 claims còn lại

### Phase 2: Mở rộng dữ liệu (1 tuần)
- [ ] Thêm tài liệu mới vào `raw/manual/` (chính sách, FAQ, hướng dẫn)
- [ ] Test `ingest-image` với screenshot bảng giá
- [ ] Chạy `cross-link` để liên kết wiki pages
- [ ] Setup cron job chạy `lint-wiki` hàng tuần

### Phase 2.5: Web Data Portal ✅ (2026-04-05)
- [x] Thiết kế giao diện web upload tài liệu (PDF, DOCX, XLSX, MD, TXT, PNG, JPG)
- [x] Backend Express server + multer upload + 6 API endpoints
- [x] Frontend UI (glassmorphism, drag & drop, file browser, pipeline trigger)
- [x] Pipeline integration (auto-trigger extract/compile)
- [x] PM2 deployment (`wiki-portal`) + Nginx reverse proxy + SSL (Let's Encrypt)
- [x] Security: Helmet, rate limiting (3 zones), HSTS, TLS 1.3
- [x] 🌐 **Live**: https://wiki.bkns.vn (credentials: xem `password.md`)
- [x] 📂 Spec: `trienkhai/trienkhaicuoicung/16-web-data-portal.md` (v2.0)

### Phase 3: Production (2-4 tuần)
- [ ] Init git repo, commit toàn bộ
- [ ] Setup Telegram alert khi build fail
- [ ] Tối ưu Context Caching (giảm cost 60-90%)
- [ ] Xem xét whitelist IP cho auto-crawl BKNS

---

## 6. 📁 Cấu Trúc File

```
/wiki/
├── .env                        # Biến môi trường (KHÔNG commit)
├── ecosystem.config.js         # PM2 config
├── bot/
│   ├── wiki_bot.py            # Telegram bot handler
│   └── manage.sh              # Start/stop/restart script
├── lib/                        # 5 shared libraries
│   ├── config.py, gemini.py, logger.py, telegram.py, utils.py
├── skills/                     # 10 skills
│   ├── crawl-source/          ├── extract-claims/
│   ├── compile-wiki/          ├── query-wiki/
│   ├── build-snapshot/        ├── ingest-image/
│   ├── lint-wiki/             ├── ground-truth/
│   ├── auto-file/             └── cross-link/
├── tools/
│   ├── convert_manual.py      # 15+ formats → Markdown (markitdown v0.4+)
│   ├── ingest_youtube.py      # YouTube URL → transcript Markdown
│   ├── ingest_html.py         # HTML URL → Markdown
│   ├── ingest_audio.py        # MP3/WAV → transcript Markdown (Whisper)
│   └── approve_and_compile.py # Batch approve pipeline
├── web/                        # Web Data Portal (NEW)
│   ├── server.js              # Express server
│   ├── middleware/auth.js     # Bearer token + bcrypt
│   ├── routes/                # upload, files, trigger, status
│   ├── lib/pipeline-runner.js # Python script runner
│   ├── public/                # HTML/CSS/JS (glassmorphism UI)
│   └── ecosystem.web.config.js # PM2 config
├── raw/manual/                 # 72 converted markdown files
├── raw/web/                    # Web portal uploads (NEW)
├── claims/
│   ├── .drafts/products/      # 809 draft claims (9 categories)
│   └── approved/products/     # 809 approved claims
├── wiki/
│   ├── products/              # 7 compiled wiki pages
│   │   ├── hosting/tong-quan.md
│   │   ├── vps/tong-quan.md
│   │   ├── ssl/tong-quan.md
│   │   ├── ten-mien/tong-quan.md
│   │   ├── email/tong-quan.md
│   │   ├── server/tong-quan.md
│   │   └── software/tong-quan.md
│   └── .drafts/               # Drafts chờ approve
├── build/
│   ├── active-build.yaml      # Build hiện tại (v0.3)
│   ├── manifests/             # 3 build manifests
│   └── snapshots/             # Wiki snapshots
└── logs/                       # JSONL structured logs
```

---

## 7. 🛠️ Các Lệnh Quản Trị

```bash
# === Bot Management ===
pm2 status                        # Xem trạng thái tất cả services
pm2 restart bkns-wiki-bot         # Restart bot
pm2 logs bkns-wiki-bot            # Xem logs realtime
pm2 logs bkns-wiki-bot --lines 50 # Xem 50 dòng gần nhất

# === Data Pipeline ===
cd /wiki
PYTHONPATH=.

# Thêm tài liệu mới
python3 tools/convert_manual.py raw/manual/ten-file-moi.docx

# Extract claims
python3 skills/extract-claims/scripts/extract.py raw/manual/ten-file.md

# Approve + Compile
python3 tools/approve_and_compile.py            # Tất cả
python3 tools/approve_and_compile.py -c hosting # 1 category

# Build snapshot mới
python3 skills/build-snapshot/scripts/snapshot.py

# Query test
python3 skills/query-wiki/scripts/query.py "Câu hỏi?"

# Lint wiki
python3 skills/lint-wiki/scripts/lint.py

# === Web Portal ===
pm2 restart wiki-portal                # Restart portal
pm2 logs wiki-portal --lines 50       # Portal logs
sudo nginx -t && sudo systemctl reload nginx  # Reload Nginx
# 🌐 https://wiki.bkns.vn (credentials: xem password.md)

# === Monitoring ===
tail -f logs/wiki-bot-pm2.log         # Bot logs
tail -f logs/web-portal-out.log       # Portal logs
tail -f logs/web-uploads.jsonl        # Upload audit
tail -f logs/pipeline-runs.jsonl      # Pipeline runs
tail -f logs/extract-claims-*.jsonl   # Extract logs
tail -f logs/compile-wiki-*.jsonl     # Compile logs
```

---

> [!TIP]
> **Quick Start cho phiên tiếp theo:**
> 1. Mở Telegram → gửi "/status" tới bot Octopus → xác nhận bot hoạt động
> 2. Gửi câu hỏi test: "Giá VPS rẻ nhất?" → kiểm tra answer
> 3. Upload thêm data: https://wiki.bkns.vn (password: bkns2026portal)
> 4. Hoặc copy thủ công DOCX/PDF vào `raw/manual/` → chạy pipeline

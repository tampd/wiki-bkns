# BKNS Wiki — Tài Liệu Bàn Giao & Chuyển Máy Chủ

**Version:** v1.1.0 (Build v0.6)
**Cập nhật:** 2026-04-16
**Maintainer:** Tampd · duytam@bkns.vn

---

## Mục lục

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Yêu cầu hệ thống](#2-yêu-cầu-hệ-thống)
3. [Cấu hình môi trường](#3-cấu-hình-môi-trường)
4. [Cài đặt từ đầu (New Server)](#4-cài-đặt-từ-đầu-new-server)
5. [Chuyển máy chủ (Migration)](#5-chuyển-máy-chủ-migration)
6. [Khởi động & quản lý processes](#6-khởi-động--quản-lý-processes)
7. [Bot Commands](#7-bot-commands)
8. [Web Admin Portal](#8-web-admin-portal)
9. [Skills Registry](#9-skills-registry)
10. [Cost Monitoring](#10-cost-monitoring)
11. [Troubleshooting](#11-troubleshooting)
12. [Backlog](#12-backlog)

---

## 1. Kiến trúc tổng quan

Pipeline 7 bước, không dùng RAG:

```
[Tài liệu / URL]
      ↓
1. Ingest           — DOCX/PDF/XLSX/PPTX/HTML/YouTube/audio → raw/*.md
                      (markitdown_adapter.py hoặc Telegram /them)
      ↓
2. Extract          — raw/*.md → claims YAML (Gemini 2.5 Pro)
                      Option: Dual-vote extract (Gemini + GPT-5.4)
      ↓
3. Review           — Auto-approve (AGREE) hoặc Web Portal (DISAGREE)
                      claims/.review-queue/ → human giải quyết
      ↓
4. Compile          — claims/approved/ → wiki/products/*.md (Gemini 2.5 Pro)
                      Self-review gate: detect hallucination, auto-correct
      ↓
5. Build snapshot   — wiki/ → BLD-YYYYMMDD-HHMMSS manifest
                      build/active-build.yaml được update
      ↓
6. Query            — câu hỏi + wiki prefix → trả lời (Gemini 2.5 Flash)
                      Implicit Caching tự động: ~$0.0004/query
      ↓
7. Human edit       — Web Portal WYSIWYG editor (Toast UI)
                      Auto-backup trước mỗi lần save
```

**Không dùng RAG.** Toàn bộ wiki (~127K tokens) nạp làm prefix cố định. Gemini Implicit Caching tự động cache prefix → tiết kiệm 75–90% chi phí input.

---

## 2. Yêu cầu hệ thống

| Thành phần | Version | Notes |
|-----------|---------|-------|
| Python | 3.10+ | pip, venv khuyến nghị |
| Node.js | 18+ | nvm khuyến nghị |
| PM2 | Latest | `npm install -g pm2` |
| Nginx | Latest | Reverse proxy + TLS |
| Git | Latest | Để clone repo |
| Disk | ≥10GB free | claims 33M + wiki 2.1M + build 11M + logs growing |
| RAM | ≥2GB | Gemini calls không nhiều, nhưng Node.js + Python cùng chạy |

**Cloud credentials bắt buộc:**
- Google Cloud service account JSON (Vertex AI / Gemini)
- Telegram Bot Token
- (Optional) OpenAI API key nếu muốn dual-vote

---

## 3. Cấu hình môi trường

Tất cả config load từ `.env` qua `lib/config.py`. Template: `.env.example`.

### Biến bắt buộc

| Biến | Mô tả |
|------|-------|
| `TELEGRAM_BOT_TOKEN` | Token Telegram bot (từ @BotFather) |
| `ADMIN_TELEGRAM_ID` | Telegram user ID của admin (số nguyên) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Đường dẫn **absolute** đến GCP service account JSON |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID |

### Biến quan trọng khi migrate

| Biến | Cũ | Mới | Notes |
|------|----|-----|-------|
| `WIKI_WORKSPACE` | `/home/openclaw/wiki` | `/path/to/new/wiki` | **Phải update khi đổi server** |
| `GOOGLE_APPLICATION_CREDENTIALS` | `/home/openclaw/...` | `/new/path/...` | Path tuyệt đối đến JSON key |

### Biến models (optional — defaults ổn)

```bash
MODEL_FLASH=gemini-2.5-flash          # Query, ingest
MODEL_PRO=gemini-2.5-pro              # Extract, compile
MODEL_PRO_NEW=gemini-3.1-pro-preview  # Chưa enable (USE_PRO_NEW=false)
MODEL_PRO_NEW_LOCATION=global         # Bắt buộc global cho 3.1 Pro
USE_PRO_NEW=false
GOOGLE_CLOUD_LOCATION=us-central1
```

### Biến dual-vote (optional)

```bash
OPENAI_API_KEY=                       # sk-proj-* (OpenAI) hoặc sk-or-v1-* (OpenRouter)
OPENAI_MODEL=gpt-5.4
OPENAI_BASE_URL=https://api.openai.com/v1
DUAL_VOTE_ENABLED=false               # false = chỉ Gemini; true = Gemini + GPT
```

### Biến cost & workspace

```bash
MAX_QUERY_COST_USD=0.01
MONTHLY_BUDGET_USD=50
WEB_PORT=3000
```

---

## 4. Cài đặt từ đầu (New Server)

### Bước 1: Clone repo

```bash
git clone git@github.com:tampd/wiki-bkns.git /opt/wiki
cd /opt/wiki
```

> Thay `/opt/wiki` bằng thư mục muốn deploy. Nhớ update `WIKI_WORKSPACE` trong `.env`.

### Bước 2: Python dependencies

```bash
# Khuyến nghị dùng venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Bước 3: Node.js dependencies (Web Portal)

```bash
cd web
npm install
cd ..
```

### Bước 4: Upload credentials

```bash
# Copy GCP service account JSON lên server
scp credentials/wiki-gcp-sa.json user@newserver:/opt/wiki/credentials/
chmod 600 /opt/wiki/credentials/wiki-gcp-sa.json
```

### Bước 5: Tạo và điền .env

```bash
cp .env.example .env
nano .env
# Điền đầy đủ: TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID,
# GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT,
# WIKI_WORKSPACE=/opt/wiki (đổi thành path thực)
```

### Bước 6: Smoke test

```bash
# Test Python config
python3 -c "from lib.config import WIKI_WORKSPACE; print('OK:', WIKI_WORKSPACE)"

# Test Gemini connection
python3 -c "from lib.gemini import GeminiClient; c = GeminiClient(); print('Gemini OK')"

# Run test suite
pytest tests/ -q
# Expected: 33 passed
```

### Bước 7: Khởi động Bot + Crons (PM2 user)

```bash
# Cài PM2 nếu chưa có
npm install -g pm2

# Khởi động
pm2 start ecosystem.config.js

# Verify
pm2 status
# Expected: bkns-wiki-bot (online), bkns-cron-daily (online), bkns-cron-promo (online)

# Save PM2 config để auto-start khi reboot
pm2 save
pm2 startup  # Làm theo hướng dẫn hiện ra
```

### Bước 8: Khởi động Web Portal (Root PM2)

```bash
# Web portal chạy dưới root PM2 (sudo required)
cd web
sudo bash -c "export PATH=$(which node | xargs dirname):\$PATH && pm2 start ecosystem.web.config.js"
sudo pm2 save

# Verify
sudo pm2 status
# Expected: wiki-portal (online, port 3000)
```

### Bước 9: Nginx + TLS

```bash
# Copy nginx config
sudo cp web/nginx-upload.trieuphu.biz.conf /etc/nginx/sites-available/wiki
# Chỉnh sửa domain và paths nếu cần
sudo ln -s /etc/nginx/sites-available/wiki /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Let's Encrypt (nếu chưa có cert)
sudo bash web/deploy-nginx.sh
```

### Bước 10: Verify production

```bash
# Bot test — gửi /status từ Telegram admin
# Expected: Build v0.6, 198 wiki files, 2252 claims

# Web portal test
curl -s https://upload.trieuphu.biz/api/status | python3 -m json.tool
# Expected: { "build": "BLD-20260415-135355", "version": "v0.6", ... }
```

---

## 5. Chuyển máy chủ (Migration)

### 5.1 Danh sách data cần chuyển

```
PHẢI CHUYỂN:
✅ claims/approved/         — 2,252 approved claims (critical data)
✅ wiki/products/           — 198 wiki pages (production content)
✅ build/                   — Build manifests + snapshots
✅ raw/manual/              — 72 source documents
✅ assets/                  — Uploaded images + evidence
✅ entities/registry.yaml   — Entity registry
✅ sources/registry.yaml    — Source traceability
✅ logs/                    — Audit logs (optional nhưng có ích)

KHÔNG CẦN CHUYỂN (có thể bỏ qua):
❌ web/node_modules/        — Chạy npm install lại trên server mới
❌ .env                     — Tạo mới từ .env.example + điền key mới
❌ bot/.last_offset         — Sẽ tự tạo lại (Telegram offset reset)
❌ claims/.drafts/          — Draft claims chưa review (có thể bỏ)
❌ trienkhai/               — Planning docs (stale, không cần)
❌ tampd_skill/             — Legacy code (không active)
```

### 5.2 Backup trên server cũ

```bash
# Backup toàn bộ data quan trọng
tar -czf bkns-wiki-backup-$(date +%Y%m%d).tar.gz \
  claims/approved/ \
  wiki/products/ \
  build/ \
  raw/manual/ \
  assets/ \
  entities/ \
  sources/ \
  logs/

# Transfer sang server mới
rsync -avz --progress \
  claims/approved/ \
  wiki/products/ \
  build/ \
  raw/manual/ \
  assets/ \
  entities/ \
  sources/ \
  user@newserver:/opt/wiki/
```

### 5.3 Update .env trên server mới

```bash
# Update các path-specific vars
WIKI_WORKSPACE=/opt/wiki                             # Đổi theo location mới
GOOGLE_APPLICATION_CREDENTIALS=/opt/wiki/credentials/sa.json
```

### 5.4 Update ecosystem.config.js

Trong `ecosystem.config.js`, đổi `cwd` và `PYTHONPATH`:

```js
cwd: '/opt/wiki',         // Đổi từ /home/openclaw/wiki
env: {
  PYTHONPATH: '/opt/wiki', // Đổi theo
}
```

Tương tự trong `web/ecosystem.web.config.js`:

```js
cwd: '/opt/wiki/web',
```

### 5.5 Validate sau migration

```bash
# 1. Test Python config
python3 -c "from lib.config import WIKI_WORKSPACE, CLAIMS_DIR; print(WIKI_WORKSPACE, CLAIMS_DIR)"

# 2. Check claims count
python3 -c "
import yaml
from pathlib import Path
ws = Path('.')
total = sum(1 for _ in (ws/'claims'/'approved').rglob('*.yaml'))
print(f'Approved claims: {total}')
"

# 3. Check wiki pages
python3 -c "
from pathlib import Path
total = sum(1 for _ in Path('wiki/products').rglob('*.md'))
print(f'Wiki pages: {total}')
"

# 4. Test query
python3 -c "
import sys; sys.path.insert(0, '.')
from skills.query_wiki.scripts.query import run_query
result = run_query('VPS BKNS có những gói nào?')
print(result[:200])
"

# 5. Run full test suite
pytest tests/ -q

# 6. Check active build
python3 -c "
import yaml
build = yaml.safe_load(open('build/active-build.yaml'))
print(f'Build: {build[\"build_id\"]}, Version: {build[\"version\"]}, Pages: {build[\"wiki_files\"]}')
"
```

### 5.6 Checklist cut-over

```
[ ] Code clone + npm install + pip install thành công
[ ] .env điền đầy đủ (đặc biệt WIKI_WORKSPACE mới)
[ ] GCP service account JSON đúng path và có quyền Vertex AI
[ ] ecosystem.config.js cwd paths đã update
[ ] pytest 33/33 pass
[ ] pm2 start → bkns-wiki-bot (online)
[ ] sudo pm2 start web → wiki-portal (online)
[ ] Nginx config đúng domain + TLS
[ ] /api/status trả về build v0.6
[ ] Telegram /status từ bot trả lời đúng
[ ] Telegram /hoi [câu hỏi test] cho kết quả hợp lý
[ ] DNS record trỏ sang IP mới
[ ] Dừng processes trên server cũ
```

---

## 6. Khởi động & quản lý processes

### 6.1 Bot + Crons (User PM2)

```bash
# Start tất cả
pm2 start ecosystem.config.js

# Xem trạng thái
pm2 status

# Restart bot sau thay đổi code
pm2 restart bkns-wiki-bot

# Xem logs bot (live)
pm2 logs bkns-wiki-bot

# Xem lỗi
pm2 logs bkns-wiki-bot --err --lines 50

# Stop tất cả
pm2 stop all
```

**3 processes quản lý bởi user PM2:**

| Tên | Script | Cron | Mô tả |
|-----|--------|------|-------|
| `bkns-wiki-bot` | `bot/wiki_bot.py --daemon` | Luôn chạy | Telegram bot |
| `bkns-cron-daily` | `tools/cron_tasks.py --task all` | 00:00 UTC (7h VN) | Health, digest, conflicts |
| `bkns-cron-promo` | `tools/cron_tasks.py --task promo-scrape` | 02:00 UTC T2 (9h VN) | Promo scrape hàng tuần |

### 6.2 Web Portal (Root PM2)

> **QUAN TRỌNG:** Web portal chạy dưới **root PM2 daemon** — dùng `sudo pm2` chứ không phải `pm2`.

```bash
# Restart web (ĐÚNG cách)
sudo bash -c "export PATH=/home/openclaw/.nvm/versions/node/v24.14.0/bin:\$PATH && pm2 reload wiki-admin"

# Hoặc nếu tên process là wiki-portal
sudo bash -c "export PATH=/home/openclaw/.nvm/versions/node/v24.14.0/bin:\$PATH && pm2 reload wiki-portal"

# Xem status web
sudo pm2 status

# KHÔNG dùng (sẽ không tìm thấy process):
# pm2 reload wiki-admin   ← thiếu sudo
# kill -9 <PID>          ← gây restart không clean
```

### 6.3 Manual (dev/debug)

```bash
# Bot single-run (xử lý messages rồi thoát)
python3 bot/wiki_bot.py

# Bot daemon mode
python3 bot/wiki_bot.py --daemon

# Web server
cd web && node server.js

# Cron tasks thủ công
python3 tools/cron_tasks.py --task health
python3 tools/cron_tasks.py --task daily-digest
python3 tools/cron_tasks.py --task dual-vote-check
python3 tools/cron_tasks.py --task conflicts
```

---

## 7. Bot Commands

| Command | Quyền | Mô tả |
|---------|-------|-------|
| `/hoi [câu hỏi]` | Tất cả | Query wiki (max 500 ký tự) |
| `/status` | Tất cả | Build version, wiki files, claims count |
| `/help` | Tất cả | Danh sách lệnh |
| `/them [URL]` | Admin only | Crawl URL → `raw/` (timeout 60s) |
| `/extract` | Admin only | Extract claims từ raw files chưa xử lý |
| `/compile [category\|--all]` | Admin only | Compile wiki |
| `/build` | Admin only | Tạo build snapshot |
| `/lint` | Admin only | Quality check wiki |

**Categories hợp lệ:** `hosting`, `vps`, `email`, `ssl`, `ten-mien`, `server`, `software`

**Workflow thêm tài liệu mới:**
```
Upload DOCX/PDF qua Web UI  →  /extract  →  review trên Web Portal  →  /compile [cat]  →  /build
       hoặc
/them [URL]                 →  /extract  →  review trên Web Portal  →  /compile [cat]  →  /build
```

---

## 8. Web Admin Portal

**URL:** https://upload.trieuphu.biz (credentials trong `password.md`, không commit vào git)

### 8.1 Giao diện

4 tabs:
- **Wiki** — Sidebar category tree, reader mode, Toast UI Editor
- **Review** — Dual-vote conflicts, bulk approve/reject
- **Upload** — File browser, upload DOCX/PDF/XLSX/PPTX/EPUB/HTML
- **Builds** — Build history + snapshot metadata

### 8.2 API chính

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| `POST` | `/api/login` | Đăng nhập → bearer token |
| `GET` | `/api/wiki/tree` | Category tree |
| `GET` | `/api/wiki/search?q=` | Full-text search |
| `GET/PUT` | `/api/wiki/:cat/:page` | Đọc/cập nhật page |
| `GET` | `/api/review/queue` | Conflict queue |
| `POST` | `/api/review/resolve/:id` | Resolve conflict |
| `POST` | `/api/review/bulk` | Bulk actions |
| `GET` | `/api/status` | System status |
| `GET` | `/api/builds` | Build history |
| `POST` | `/api/trigger` | Trigger pipeline |
| `POST` | `/api/librarian/chat` | Librarian assistant |

---

## 9. Skills Registry

14 pipeline skills trong `skills/`. Định nghĩa trong `agents.yaml`.

| Skill | Model | Trạng thái | Notes |
|-------|-------|-----------|-------|
| `extract-claims` | Gemini 2.5 Pro | ✅ Active | Core pipeline |
| `compile-wiki` | Gemini 2.5 Pro | ✅ Active | Core pipeline |
| `query-wiki` | Gemini 2.5 Flash | ✅ Active | Core pipeline |
| `build-snapshot` | None | ✅ Active | Core pipeline |
| `ingest-image` | Gemini 2.5 Flash | ✅ Tested | Chưa tích hợp cron |
| `lint-wiki` | Gemini 2.5 Pro | ✅ Active | Qua bot /lint |
| `ground-truth` | Gemini 2.5 Flash | ⚠️ Blocked | Cloudflare blocks |
| `crawl-source` | None | ⚠️ Blocked | Cloudflare blocks |
| `dual-vote` | Gemini + GPT | ✅ Code ready | `DUAL_VOTE_ENABLED=false` |
| `auto-file` | Gemini 2.5 Flash | 🔲 Disabled | Phase 2 |
| `cross-link` | Gemini 2.5 Flash | 🔲 Disabled | Phase 2 |
| `verify-claims` | None | 🔲 Pending | Chưa tích hợp |
| `audit-wiki` | None | 🔲 Pending | Chưa tích hợp |

Mỗi skill có `skills/{name}/SKILL.md` (spec) và `skills/{name}/scripts/` (code).

---

## 10. Cost Monitoring

### Log files

```
logs/gemini-calls-YYYY-MM.jsonl   — Per-call Gemini cost
logs/openai-calls-YYYY-MM.jsonl   — Per-call OpenAI cost (khi dual-vote)
logs/dual-vote-YYYY-MM.jsonl      — Dual-vote events (AGREE/PARTIAL/DISAGREE)
logs/query-YYYY-MM-DD.jsonl       — Query logs + cache hit rate
```

### Chi phí ước tính

| Hoạt động | Chi phí |
|-----------|---------|
| Extract 1 file (Gemini Pro) | ~$0.015 |
| Extract dual-vote (Gemini + GPT) | ~$0.030 |
| Compile 1 category | ~$0.10 |
| Query 1 câu (Flash + Implicit Cache) | ~$0.0004 |
| Build snapshot | Miễn phí |

**Budget tháng mặc định: $50** (config `MONTHLY_BUDGET_USD` trong `.env`).

### Kiểm tra nhanh

```bash
# Chi phí tháng hiện tại
python3 -c "
import json
from pathlib import Path
from datetime import datetime
month = datetime.now().strftime('%Y-%m')
f = Path(f'logs/gemini-calls-{month}.jsonl')
if f.exists():
    lines = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    total = sum(l.get('cost_usd', 0) for l in lines)
    print(f'Calls: {len(lines)}, Cost: \${total:.4f}')
else:
    print('No log file found')
"
```

---

## 11. Troubleshooting

| Vấn đề | Nguyên nhân | Xử lý |
|--------|-------------|-------|
| Bot không phản hồi | Token sai hoặc bot offline | `pm2 logs bkns-wiki-bot`, kiểm tra `TELEGRAM_BOT_TOKEN` |
| `/them` lỗi permission | `chat_id` ≠ `ADMIN_TELEGRAM_ID` | Kiểm tra `.env` `ADMIN_TELEGRAM_ID` |
| Gemini 429 | Rate limit | Retry tự động 3x. Nếu tiếp tục: giảm concurrency |
| `active-build.yaml` không tồn tại | Chưa chạy build | `python3 skills/build-snapshot/scripts/snapshot.py` |
| Web 500 errors | Server-side lỗi | `pm2 logs wiki-admin --err` hoặc `logs/web-errors-*.jsonl` |
| Claims không xuất hiện sau extract | File đã cached | Xóa entry trong `claims/.cache/` hoặc dùng `--force` |
| `USE_PRO_NEW=true` gây lỗi | 3.1 Pro chỉ dùng `global` location | Đảm bảo `MODEL_PRO_NEW_LOCATION=global` |
| Web portal không reload | Root PM2 daemon | Dùng `sudo pm2 reload wiki-admin` (không phải kill PID) |
| OpenAI 401 | API key hết hạn | Rotate tại platform.openai.com |
| Python import error sau migrate | PYTHONPATH sai | Check `PYTHONPATH` trong `ecosystem.config.js` |
| Claims count = 0 sau migrate | WIKI_WORKSPACE sai | Cập nhật `WIKI_WORKSPACE` trong `.env` |

---

## 12. Backlog

Tính năng chưa implement hoặc đang bị disable:

- [ ] **Enable dual-vote** (`DUAL_VOTE_ENABLED=true`) — sau khi chạy `regression_test.py --full` đầy đủ
- [ ] **Enable Gemini 3.1 Pro** (`USE_PRO_NEW=true`) — sau khi xác nhận API quota
- [ ] **auto-file skill** (Phase 2) — tự phân loại FAQ từ queries
- [ ] **cross-link skill** (Phase 2) — internal links giữa wiki pages
- [ ] **verify-claims + audit-wiki** — tích hợp vào pipeline chính
- [ ] **Monitoring dashboard** — cost + cache hit rate + query volume
- [ ] **CSP nonce-based** — khi TOAST UI Editor hỗ trợ

---

*Chi tiết kỹ thuật: xem [docs/SPEC-wiki-system.md](./docs/SPEC-wiki-system.md)*
*Operations runbook: xem [docs/runbook.md](./docs/runbook.md)*

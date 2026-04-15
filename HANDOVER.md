# BKNS Wiki — Tài liệu Bàn giao

**Version:** v1.1.0 | **Cập nhật:** 2026-04-14

---

## 1. Kiến trúc hệ thống

### Pipeline chính (7 bước)

```
[URL / File thô]
      ↓
1. crawl-source     — Thu thập HTML → Markdown (raw/website-crawl/)
      ↓
2. ingest-image     — Ảnh bảng giá → Markdown qua Gemini Flash Vision
      ↓
3. extract-claims   — Markdown thô → claims YAML (Gemini Pro)
      ↓
4. [Review thủ công] — Phê duyệt claims → claims/approved/
      ↓
5. compile-wiki     — Claims + nguồn → Wiki pages (Gemini Pro)
      ↓
6. build-snapshot   — Gộp toàn bộ wiki/ → active-build.yaml
      ↓
7. query-wiki       — Câu hỏi + wiki prefix → trả lời (Gemini Flash + Implicit Cache)
```

### Không dùng RAG
Wiki toàn bộ (~200k–500k token) được nạp làm **prefix cố định** mỗi query. Gemini tự động cache prefix → tiết kiệm ~75–90% chi phí token input. Không cần vector DB.

---

## 2. Cài đặt môi trường

```bash
# Clone / vào thư mục dự án
cd /home/openclaw/wiki

# Cài Python dependencies
pip install -r requirements.txt

# Copy và điền .env
cp .env.example .env
# Điền TELEGRAM_BOT_TOKEN, ADMIN_TELEGRAM_ID, GOOGLE_CLOUD_PROJECT, v.v.

# Cài Node dependencies (Web UI)
cd web && npm install && cd ..
```

**Yêu cầu:**
- Python 3.10+
- Node.js 18+
- PM2 (`npm install -g pm2`)
- Google Cloud credentials file (Vertex AI)

---

## 3. Cấu hình (Environment Variables)

Tất cả được load từ `.env` qua `lib/config.py`:

| Biến | Bắt buộc | Mô tả |
|------|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Có | Token Telegram bot |
| `ADMIN_TELEGRAM_ID` | Có | Telegram user ID của admin (không hardcode) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Có | Đường dẫn đến file JSON service account Vertex AI |
| `GOOGLE_CLOUD_PROJECT` | Có | GCP project ID (mặc định: `ai-test-491016`) |
| `GOOGLE_CLOUD_LOCATION` | Không | Region (mặc định: `us-central1`) |
| `MODEL_FLASH` | Không | Model Flash (mặc định: `gemini-2.5-flash`) |
| `MODEL_PRO` | Không | Model Pro (mặc định: `gemini-2.5-pro`) |
| `MODEL_PRO_NEW` | Không | Model Pro mới (mặc định: `gemini-3.1-pro-preview`) |
| `USE_PRO_NEW` | Không | Feature flag — dùng MODEL_PRO_NEW (mặc định: `false`) |
| `MODEL_PRO_NEW_LOCATION` | Không | Location cho PRO_NEW (mặc định: `global`) |
| `OPENAI_API_KEY` | Không | Chỉ cần khi `DUAL_VOTE_ENABLED=true` |
| `DUAL_VOTE_ENABLED` | Không | Bật dual-vote cross-validation (mặc định: `false`) |
| `WIKI_WORKSPACE` | Không | Override workspace root (mặc định: `/home/openclaw/wiki`) |

---

## 4. Khởi động hệ thống

### PM2 (production)

```bash
# Khởi động tất cả processes
pm2 start ecosystem.config.js

# Xem trạng thái
pm2 status

# Xem logs bot
pm2 logs bkns-wiki-bot

# Restart sau khi thay đổi code
pm2 restart bkns-wiki-bot

# Dừng
pm2 stop all
```

**PM2 processes được định nghĩa trong `ecosystem.config.js`:**
- `bkns-wiki-bot` — Telegram bot daemon (`bot/wiki_bot.py --daemon`)
- `bkns-cron-daily` — Cron hàng ngày 7h sáng VN (`tools/cron_tasks.py --task all`)

### Manual (dev/debug)

```bash
# Bot chạy một lần (xử lý messages hiện có rồi thoát)
python3 bot/wiki_bot.py

# Bot daemon mode
python3 bot/wiki_bot.py --daemon

# Web UI
cd web && node server.js
```

---

## 5. Bot Commands

| Command | Quyền | Mô tả |
|---------|-------|-------|
| `/hoi [câu hỏi]` | Tất cả | Hỏi về sản phẩm/dịch vụ BKNS |
| `/status` | Tất cả | Xem build hiện tại, số wiki files, số claims |
| `/help` | Tất cả | Xem danh sách lệnh |
| `/them [URL]` | Admin | Crawl URL mới vào `raw/`, tiếp theo chạy `/extract` |
| `/extract` | Admin | Extract claims từ tất cả raw files chưa xử lý |
| `/compile [category]` | Admin | Compile wiki cho một category (hoặc `--all`) |
| `/build` | Admin | Tạo build snapshot mới từ wiki hiện tại |
| `/lint` | Admin | Chạy syntax lint trên toàn bộ wiki |

**Categories hợp lệ cho `/compile`:** `hosting`, `vps`, `email`, `ssl`, `ten-mien`, `server`, `software`

**Workflow thêm trang mới:**
```
/them https://bkns.vn/page → /extract → [review claims thủ công] → /compile [cat] → /build
```

---

## 6. Skills Registry

Định nghĩa trong `agents.yaml`. Skills được triển khai trong `skills/`:

| Skill | Phase | Model | Mô tả |
|-------|-------|-------|-------|
| `crawl-source` | 0.5 | None | Thu thập HTML → Markdown raw |
| `extract-claims` | 0.5 | gemini-2.5-pro | Trích xuất claims từ raw files |
| `compile-wiki` | 0.5 | gemini-2.5-pro | Compile claims + nguồn → Wiki pages |
| `query-wiki` | 0.5 | gemini-2.5-flash | Trả lời câu hỏi từ wiki |
| `build-snapshot` | 1 | None | Tạo snapshot build |
| `ingest-image` | 1 | gemini-2.5-flash | Extract ảnh bảng giá → Markdown |
| `lint-wiki` | 1 | gemini-2.5-pro | Lint chất lượng wiki |
| `ground-truth` | 1 | gemini-2.5-flash | Kiểm tra thông tin cơ bản |
| `auto-file` | 2 (disabled) | gemini-2.5-flash | Tự động file FAQ |
| `cross-link` | 2 (disabled) | gemini-2.5-flash | Tạo cross-links |
| `dual-vote` | - | Gemini + GPT | Cross-validation dual-vote |

Mỗi skill có `skills/{name}/SKILL.md` (spec) và `skills/{name}/scripts/` (code).

---

## 7. Cấu trúc thư mục quan trọng

```
/home/openclaw/wiki/
├── lib/                    ← Core library
│   ├── config.py           ← Cấu hình trung tâm (env vars, paths, constants)
│   ├── gemini.py           ← Vertex AI Gemini wrapper (generate, costs, retry)
│   ├── logger.py           ← Structured JSONL logging
│   └── utils.py            ← Shared utilities (hash, slug, yaml, datetime)
├── bot/
│   └── wiki_bot.py         ← Telegram bot (commands, routing, retry)
├── skills/                 ← Pipeline skills (crawl/extract/compile/query/...)
├── web/                    ← Web review UI
│   ├── server.js           ← Express server
│   ├── routes/             ← API routes
│   └── public/             ← Frontend (app.js, index.html, style.css)
├── tests/                  ← Test suite
│   ├── test_bot.py         ← Bot unit tests (13 tests)
│   └── test_pipeline_smoke.py ← Pipeline smoke tests (7 tests)
├── raw/                    ← Dữ liệu thô chưa xử lý
│   └── website-crawl/      ← Kết quả crawl
├── claims/                 ← Claims (YAML)
│   └── approved/           ← Claims đã phê duyệt
├── wiki/                   ← Wiki pages (Markdown)
├── build/                  ← Build artifacts
│   └── active-build.yaml   ← Build hiện tại (đọc bởi query-wiki)
├── logs/                   ← Logs
│   ├── gemini-calls-YYYY-MM.jsonl  ← Cost tracking
│   ├── errors/             ← Error logs
│   └── intake/             ← Crawl audit logs
├── agents.yaml             ← Skills registry
├── ecosystem.config.js     ← PM2 config
└── requirements.txt        ← Python dependencies
```

---

## 8. Cost Monitoring

### Monthly cost log

File: `logs/gemini-calls-YYYY-MM.jsonl`

Mỗi dòng là một Gemini API call:
```json
{
  "ts": "2026-04-14T10:30:00+07:00",
  "skill": "query-wiki",
  "action": "llm_call_cached",
  "model": "gemini-2.5-flash",
  "input_tokens": 45000,
  "cached_tokens": 42000,
  "output_tokens": 350,
  "cost_usd": 0.000287,
  "elapsed_ms": 1240
}
```

### Đọc báo cáo chi phí tháng

```bash
# Tổng chi phí tháng hiện tại
python3 -c "
import json; from pathlib import Path; from datetime import datetime
month = datetime.now().strftime('%Y-%m')
f = Path(f'logs/gemini-calls-{month}.jsonl')
if f.exists():
    lines = [json.loads(l) for l in f.read_text().splitlines() if l]
    total = sum(l['cost_usd'] for l in lines)
    print(f'Total calls: {len(lines)}, Total cost: \${total:.4f}')
"
```

### Alerts
- Alert tự động khi 1 query vượt `MAX_QUERY_COST_USD` (mặc định $0.01)
- Budget tháng: $50 — nếu vượt, cần xem xét giảm tần suất hoặc model

---

## 9. Troubleshooting phổ biến

| Vấn đề | Nguyên nhân | Xử lý |
|--------|-------------|-------|
| Bot không phản hồi | Token Telegram sai hoặc bot offline | `pm2 logs bkns-wiki-bot`, kiểm tra `TELEGRAM_BOT_TOKEN` |
| `/them` trả về lỗi permission | `chat_id` không khớp `ADMIN_TELEGRAM_ID` | Kiểm tra `.env` giá trị `ADMIN_TELEGRAM_ID` |
| Gemini API error 429 | Vượt rate limit | Retry tự động 3 lần (5s interval). Nếu vẫn lỗi — giảm tần suất |
| `active-build.yaml` không tồn tại | Chưa chạy `/build` lần nào | Chạy `/build` qua bot hoặc `python3 skills/build-snapshot/scripts/snapshot.py` |
| Web UI lỗi 500 | Lỗi server-side | Xem `logs/web-errors-YYYY-MM-DD.jsonl` để biết chi tiết |
| Claims không xuất hiện sau extract | File đã được xử lý (cached) | Xóa file `.processed` hoặc dùng `--force` flag |
| `USE_PRO_NEW=true` gây lỗi | gemini-3.1-pro-preview chỉ available qua `global` location | Đảm bảo `MODEL_PRO_NEW_LOCATION=global` trong `.env` |

---

## 10. Backlog / Future improvements

- [ ] `auto-file` skill (Phase 2): Tự động phân loại FAQ từ queries — disabled pending Phase 2
- [ ] `cross-link` skill (Phase 2): Tạo cross-links giữa wiki pages — disabled pending Phase 2
- [ ] `USE_PRO_NEW=true`: Enable gemini-3.1-pro-preview sau khi xác nhận API quota
- [ ] Dual-vote cho compile: `DUAL_VOTE_ENABLED=true` sau khi regression test pass
- [ ] Scheduled crawl: Cron job crawl tự động bkns.vn thay vì chỉ manual `/them`
- [ ] `audit-wiki` và `verify-claims` skills: chưa được tích hợp vào pipeline chính
- [ ] Web UI: Chuyển từ `unsafe-inline` CSP sang nonce-based khi TOAST UI hỗ trợ
- [ ] Monitoring dashboard: Xây dựng dashboard tổng hợp cost + cache hit rate + query volume

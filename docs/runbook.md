# BKNS Wiki — Operational Runbook v1.1

> Dành cho: operator, on-call.
> Cập nhật: 2026-04-16 (phản ánh Build v0.6, Production)

---

## 1. Architecture Overview

```
Input (15+ formats)
  → markitdown_adapter.py / ingest_*.py  →  raw/*.md
  → extract.py (Gemini 2.5 Pro)          →  claims/.drafts/ YAML
  → [Review queue: Web Portal]            →  claims/approved/
  → compile.py (Gemini 2.5 Pro)          →  wiki/products/ MD
    └─ Self-review gate (hallucination detect, auto-correct)
  → build-snapshot/                       →  build/manifests/ + active-build.yaml
  → query-wiki + Telegram bot             →  câu trả lời ($0.0004/query + cache)
```

**Key flags trong `.env`:**

| Flag | Default | Mô tả |
|------|---------|-------|
| `DUAL_VOTE_ENABLED` | `false` | Bật cross-validation Gemini + GPT-5.4 |
| `USE_PRO_NEW` | `false` | Dùng Gemini 3.1 Pro thay 2.5 Pro |

**Trạng thái production hiện tại:**
- `DUAL_VOTE_ENABLED=false` — chỉ Gemini, dual-vote code sẵn sàng nhưng chưa enable
- `USE_PRO_NEW=false` — dùng Gemini 2.5 Pro (ổn định)
- Build active: **v0.6** (BLD-20260415-135355), 198 pages, 127K tokens

---

## 2. Daily Operations

### Check processes

```bash
# Bot + crons (user PM2)
pm2 status
pm2 logs bkns-wiki-bot --lines 50

# Web portal (root PM2)
sudo pm2 status
```

### Check review queue (DISAGREE claims chờ duyệt)

```bash
ls claims/.review-queue/*.json 2>/dev/null | wc -l
# Nếu > 20: xử lý thủ công qua Web Portal (tab Review)
```

### Run quality dashboard

```bash
# Full dashboard (cost + claims + lint)
python3 tools/quality_dashboard.py

# Dual-vote stats (last 1 ngày)
python3 tools/quality_dashboard.py --v04

# Dual-vote stats last 7 ngày
python3 tools/quality_dashboard.py --v04 --days 7
```

### Cron tasks (manual trigger)

```bash
python3 tools/cron_tasks.py --task health          # wiki health check
python3 tools/cron_tasks.py --task dual-vote-check # DISAGREE count alert
python3 tools/cron_tasks.py --task daily-digest    # daily summary
python3 tools/cron_tasks.py --task conflicts       # conflict scan
```

---

## 3. Build Operations

### Full rebuild (tất cả categories)

```bash
cd /wiki

# Dry-run extract + compile (hosting only)
python3 skills/extract-claims/scripts/extract.py --dry-run

# Extract tất cả pending raw files
python3 skills/extract-claims/scripts/extract.py

# Compile tất cả categories
python3 skills/compile-wiki/scripts/compile.py --all

# Tạo snapshot
python3 skills/build-snapshot/scripts/snapshot.py

# Restart bot để load build mới
pm2 restart bkns-wiki-bot
```

### Rebuild 1 category cụ thể

```bash
# Compile hosting
python3 skills/compile-wiki/scripts/compile.py --category hosting

# Compile qua bot (nếu bot đang chạy)
# Gửi Telegram: /compile hosting
```

### Diff giữa builds

```bash
# So sánh v0.5 vs v0.6
python3 tools/wiki_diff.py \
  --v03 build/snapshots/v0.5-*/wiki/products \
  --v04 wiki/products \
  --html /tmp/diff-report.html \
  --json /tmp/diff-report.json
```

---

## 4. Rollback

### Rollback về snapshot trước

```bash
# Xem danh sách snapshots
ls -la build/snapshots/

# Rollback về v0.5 (ví dụ)
SNAP_DIR="build/snapshots/v0.5-..."

# Backup current production
cp -r wiki/products wiki/products.backup-$(date +%Y%m%d)

# Restore từ snapshot
cp -r "$SNAP_DIR/wiki/products" wiki/products

# Tạo lại build manifest
python3 skills/build-snapshot/scripts/snapshot.py

# Restart bot
pm2 restart bkns-wiki-bot

# Verify
pm2 logs bkns-wiki-bot --lines 20
```

### Verify rollback thành công

```bash
python3 -c "
import yaml
build = yaml.safe_load(open('build/active-build.yaml'))
print(f'Version: {build[\"version\"]}, Files: {build[\"wiki_files\"]}')
"
pm2 status
```

---

## 5. Monitoring & Alerts

### Automatic (cron via PM2)

| Task | Schedule (UTC) | Mô tả |
|------|---------------|-------|
| `health` | 00:00 daily (7h VN) | Wiki health check |
| `dual-vote-check` | 00:00 daily | DISAGREE count alert |
| `daily-digest` | 00:00 daily | Build, cost, bot stats |
| `conflicts` | 00:00 daily | Claim conflict scan |
| `promo-scrape` | 02:00 Monday (9h VN T2) | Weekly promo scrape |

### Manual spot checks

```bash
# Cost trend (Gemini)
python3 -c "
import json, glob
total = 0.0
for f in sorted(glob.glob('logs/gemini-calls-*.jsonl'))[-1:]:
    for line in open(f):
        try: total += float(json.loads(line).get('cost_usd', 0))
        except: pass
print(f'Monthly Gemini: \${total:.4f}')
"

# Agreement rate (dual-vote, nếu enabled)
python3 tools/quality_dashboard.py --v04

# Review queue size
ls claims/.review-queue/*.json 2>/dev/null | wc -l
echo "DISAGREE conflicts pending"
```

---

## 6. Cost Management

### Budget

| Scope | Limit | Alert |
|-------|-------|-------|
| Monthly (Gemini + OpenAI) | $50 | Cron `check_cost_budget.py` daily |
| Per-query | $0.01 | Alert tự động trong `lib/gemini.py` |

### Model pricing (Vertex AI — tham khảo)

| Model | Input/1M | Output/1M |
|-------|----------|----------|
| Gemini 2.5 Flash | $0.075 | $0.30 |
| Gemini 2.5 Pro | $1.25 | $10.00 |
| Gemini 3.1 Pro Preview | $2.00 | $12.00 |
| GPT-5.4 | ~$2.50 | ~$10.00 |

### Check total spend

```bash
# Gemini spend tháng hiện tại
python3 -c "
import json
from pathlib import Path
from datetime import datetime
month = datetime.now().strftime('%Y-%m')
f = Path(f'logs/gemini-calls-{month}.jsonl')
if f.exists():
    lines = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
    total = sum(l.get('cost_usd', 0) for l in lines)
    print(f'Gemini calls: {len(lines)}, Cost: \${total:.4f}')
"

# Dual-vote spend (OpenAI + Gemini)
python3 -c "
import json, glob
total = 0.0
for f in sorted(glob.glob('logs/dual-vote-*.jsonl'))[-2:]:
    for line in open(f):
        try: total += float(json.loads(line).get('cost_usd_total', 0))
        except: pass
print(f'Dual-vote total: \${total:.4f}')
"
```

---

## 7. Enable Dual-Vote (khi sẵn sàng)

> **Hiện tại `DUAL_VOTE_ENABLED=false`.** Dual-vote code đã implement và test, nhưng chưa enable để tránh chi phí thêm và regression chưa verify đầy đủ.

### Pre-conditions trước khi enable

- [ ] `OPENAI_API_KEY` đã có và valid (test: `python3 -c "from lib.openai_client import OpenAIClient; c = OpenAIClient(); print('OK')"`)
- [ ] Budget đã điều chỉnh (dual-vote ~2x chi phí extract)
- [ ] Regression test đã chạy: `python3 tools/regression_test.py --dry-run`

### Enable dual-vote

```bash
# 1. Update .env
sed -i 's/DUAL_VOTE_ENABLED=false/DUAL_VOTE_ENABLED=true/' .env

# 2. Verify
grep DUAL_VOTE_ENABLED .env

# 3. Test trên 1 file
python3 skills/extract-claims/scripts/extract_dual.py --file raw/manual/sample.md --dry-run

# 4. Check review queue sau khi test
ls claims/.review-queue/*.json | wc -l

# 5. Full regression (optional, khuyến nghị)
python3 tools/regression_test.py --full
```

### Rollback dual-vote nếu có vấn đề

```bash
sed -i 's/DUAL_VOTE_ENABLED=true/DUAL_VOTE_ENABLED=false/' .env
pm2 restart bkns-wiki-bot
```

---

## 8. Common Issues

### Bot không trả lời

```bash
pm2 status bkns-wiki-bot
pm2 logs bkns-wiki-bot --err --lines 30
# Nếu crash: pm2 restart bkns-wiki-bot
# Nếu token sai: kiểm tra TELEGRAM_BOT_TOKEN trong .env
```

### Web portal không restart

```bash
# ĐÚNG:
sudo bash -c "export PATH=$(which node | xargs dirname):\$PATH && pm2 reload wiki-portal"

# SAI (sẽ không tìm thấy process):
pm2 reload wiki-portal
kill -9 <PID>
```

### Quá nhiều DISAGREE (> 30%)

```bash
# 1. Xem dashboard
python3 tools/quality_dashboard.py --v04

# 2. Kiểm tra logs
tail -20 logs/dual-vote-$(date +%Y-%m).jsonl | python3 -c "
import sys, json
for l in sys.stdin:
    e = json.loads(l)
    if e.get('status') == 'DISAGREE':
        print(e['skill'], e.get('score', 0), e.get('ts', ''))
"

# 3. Xem 5 file trong review-queue để tìm pattern
ls claims/.review-queue/*.json | head -5 | xargs -I{} python3 -c "
import json, sys
d = json.load(open('{}'))
print(d.get('entity_name', ''), d.get('attribute', ''), d.get('score', ''))
"
```

### Gemini API error (429 / quota)

```bash
grep "error\|429\|timeout" logs/gemini-calls-$(date +%Y-%m).jsonl | tail -20
# 429: chờ 1h hoặc switch sang gemini-2.5-flash tạm thời
# Timeout: retry tự động 3x đã configured trong lib/gemini.py
```

### OpenAI API error

```bash
# 401 (unauthorized)
grep "OPENAI_API_KEY" .env | head -c 40  # verify key present
# → Rotate key tại platform.openai.com

# 429 (rate limit)
# → Giảm concurrency hoặc tăng delay giữa calls
```

### Claims count = 0 sau migrate

```bash
# Kiểm tra WORKSPACE
python3 -c "from lib.config import CLAIMS_DIR; print(CLAIMS_DIR)"
ls "$CLAIMS_DIR/approved/" | head -5
# Nếu path sai: cập nhật WORKSPACE trong .env
```

---

## 9. Key File Locations

| File/Dir | Mô tả |
|----------|-------|
| `.env` | Feature flags, API keys — không commit |
| `build/active-build.yaml` | Active build metadata (đọc bởi query-wiki) |
| `wiki/products/` | Production wiki pages (198 files) |
| `claims/approved/` | Approved claims (2,252 files) |
| `claims/.review-queue/` | Human review queue (25 conflicts) |
| `claims/.drafts/` | Draft claims (809 pending) |
| `build/snapshots/` | Immutable build snapshots (v0.1 → v0.6) |
| `logs/gemini-calls-YYYY-MM.jsonl` | Gemini cost log |
| `logs/dual-vote-YYYY-MM.jsonl` | Dual-vote event log |
| `logs/wiki-bot-error.log` | Bot error log |
| `logs/web-portal-error.log` | Web error log |
| `ecosystem.config.js` | PM2 config (bot + crons) |
| `web/ecosystem.web.config.js` | PM2 config (web portal) |
| `web/nginx-wiki.bkns.vn.conf` | Nginx config |
| `scripts/rollback-v0.4.sh` | Rollback script (reference) |

---

## 10. Test Suite

```bash
# Chạy tất cả (33 tests, ~5-10 giây)
pytest tests/ -q

# Verbose
pytest tests/ -v

# Một test cụ thể
pytest tests/test_bot.py::TestValidateUrl -v

# Test pipeline smoke
pytest tests/test_pipeline_smoke.py -v
```

| File | Tests | Nội dung |
|------|-------|---------|
| `test_bot.py` | 13 | URL validation, error masking, /them command |
| `test_pipeline_smoke.py` | 7 | Extract, compile, query, build flow |
| `test_markitdown_adapter.py` | 6 | 15+ format converters |
| `test_tools.py` | 5 | Utility scripts |
| `test_utils.py` | 2 | Config + logger |
| **Total** | **33** | **100% pass** ✅ |

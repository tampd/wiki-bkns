# BKNS Wiki — Operational Runbook v0.4

> Dành cho: operator, on-call. Mô tả cách vận hành, monitor, và xử lý sự cố.

---

## 1. Architecture Overview (v0.4)

```
Input (15+ formats)
  → markitdown_adapter.py          convert → raw/*.md
  → extract_dual.py                Gemini + GPT-5.4 → AGREE/PARTIAL/DISAGREE
  → claims/.review-queue/          DISAGREE → human review
  → claims/approved/               approved claims
  → compile_dual.py                Gemini + GPT-5.4 → wiki pages
  → wiki/products/                 final wiki
  → build-snapshot/                immutable snapshot
  → query-wiki / Telegram bot      trả lời câu hỏi
```

**Key flags in `.env`:**
| Flag | Mô tả | Default |
|------|--------|---------|
| `DUAL_VOTE_ENABLED` | Bật dual-vote (Gemini + GPT-5.4) | `true` |
| `USE_PRO_NEW` | Dùng Gemini 3.1 Pro thay 2.5 Pro | `false` |

---

## 2. Daily Operations

### Check bot status
```bash
pm2 status
pm2 logs bkns-wiki-bot --lines 50
```

### Check review queue (DISAGREE claims chờ duyệt)
```bash
ls claims/.review-queue/*.json | wc -l
# Nếu > 20: xử lý thủ công
python3 tools/approve_claims.py --review-queue
```

### Run quality dashboard
```bash
# Full dashboard
python3 tools/quality_dashboard.py

# v0.4 dual-vote stats (last 1 day)
python3 tools/quality_dashboard.py --v04

# v0.4 stats last 7 days
python3 tools/quality_dashboard.py --v04 --days 7
```

### Cron tasks (manual trigger)
```bash
python3 tools/cron_tasks.py --task health          # health check
python3 tools/cron_tasks.py --task dual-vote-check # DISAGREE alert
python3 tools/cron_tasks.py --task daily-digest    # daily digest
python3 tools/cron_tasks.py --task conflicts       # conflict scan
```

---

## 3. Running a Build

### Full rebuild (all 7 categories) with dual-vote
```bash
cd /home/openclaw/wiki
# Ensure flags
grep DUAL_VOTE_ENABLED .env   # should be true
# Dry-run first (hosting only)
python3 tools/regression_test.py --dry-run
# If OK, full rebuild
python3 tools/regression_test.py --full
```

### Diff v0.3 vs v0.4
```bash
python3 tools/wiki_diff.py \
  --v03 build/snapshots/v0.3-pre-upgrade-2026-04-13/wiki/products \
  --v04 wiki-v0.4/products \
  --html trienkhai/upgrade-v0.4/diff-report.html \
  --json trienkhai/upgrade-v0.4/diff-report.json
# Open: diff-report.html in browser
```

---

## 4. Promote v0.4 → Production

Pre-conditions (all must pass):
- [ ] Regression test: accuracy ≥ v0.3 in ≥ 90% of cases
- [ ] No critical regression (price/hotline errors)
- [ ] Cost increase ≤ 2x ($6.50 → ≤ $13)
- [ ] Bot QA test ≥ 80% pass (see `trienkhai/upgrade-v0.4/bot-qa-test.md`)

```bash
# 1. Replace wiki
mv wiki/products wiki/products.v0.3-backup
mv wiki-v0.4/products wiki/products

# 2. Create new snapshot
python3 skills/build-snapshot/scripts/snapshot.py

# 3. Update active-build.yaml
sed -i 's/version:.*/version: v0.4/' build/active-build.yaml

# 4. Restart services
pm2 restart bkns-wiki-bot
pm2 restart wiki-portal
pm2 status

# 5. Tail logs for 5 minutes
pm2 logs bkns-wiki-bot --lines 100
```

---

## 5. Rollback v0.4 → v0.3

### Quick rollback (automated)
```bash
# Dry-run first
bash scripts/rollback-v0.4.sh --dry-run
# Execute
bash scripts/rollback-v0.4.sh
```

### Manual rollback steps
```bash
cd /home/openclaw/wiki
mv wiki/products wiki/products.v0.4-failed
cp -r wiki/products.v0.3-backup wiki/products
sed -i 's/^USE_PRO_NEW=true/USE_PRO_NEW=false/' .env
sed -i 's/^DUAL_VOTE_ENABLED=true/DUAL_VOTE_ENABLED=false/' .env
python3 skills/build-snapshot/scripts/snapshot.py --version v0.3-restored
pm2 restart all
echo "✅ Rolled back to v0.3"
```

### Verify rollback succeeded
```bash
grep "USE_PRO_NEW\|DUAL_VOTE" .env     # both should be false
pm2 status                              # all processes online
pm2 logs bkns-wiki-bot --lines 20      # no errors
```

---

## 6. Monitoring & Alerts

### Automatic (cron)
| Task | Schedule | Description |
|------|----------|-------------|
| `dual-vote-check` | Hourly | Alert if DISAGREE > 20 in last 1h |
| `daily-digest` | 08:00 | Builds, cost, review queue, bot stats |
| `health` | 07:00 | Wiki health check |
| `conflicts` | 07:00 | Claim conflict scan |

### Manual spot checks
```bash
# Cost trend
tail -50 logs/dual-vote-$(date +%Y-%m).jsonl | python3 -c "
import sys, json
entries = [json.loads(l) for l in sys.stdin if l.strip()]
total = sum(float(e.get('cost_usd_total', 0)) for e in entries)
print(f'Cost (last 50 votes): \${total:.4f}')
"

# Agreement rate today
python3 tools/quality_dashboard.py --v04
```

---

## 7. Cost Management

**Budget limit**: $20 total for v0.4 testing; alert at $15.

| Model | Input (per 1M) | Output (per 1M) |
|-------|---------------|----------------|
| Gemini 2.5 Pro | $1.25 (cached $0.31) | $10.00 |
| Gemini 3.1 Pro | $2.00 (cached $0.20) | $12.00 |
| GPT-5.4 | $2.50 | $10.00 |
| GPT-5.4-mini | $0.40 | $1.60 |

Check current spend:
```bash
# From dual-vote logs
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

## 8. Common Issues

### Bot không trả lời
```bash
pm2 status bkns-wiki-bot
pm2 logs bkns-wiki-bot --err --lines 30
# Nếu crash: pm2 restart bkns-wiki-bot
```

### Quá nhiều DISAGREE (> 30%)
1. Xem top disagreements: `python3 tools/quality_dashboard.py --v04`
2. Kiểm tra prompt có bị truncate không: `tail -10 logs/extract-dual-$(date +%Y-%m-%d).jsonl`
3. Xem 5 file trong `.review-queue/` để tìm pattern
4. Nếu do 1 category cụ thể: chạy `python3 tools/regression_test.py --step extract --category <cat>`

### Gemini API error (quota/timeout)
```bash
grep "error\|429\|timeout" logs/extract-dual-$(date +%Y-%m-%d).jsonl | tail -20
# Nếu quota: chờ 1h hoặc switch sang gemini-2.5-flash tạm thời
```

### OpenAI API error (401/429)
```bash
grep "OPENAI_API_KEY" .env | cut -c1-30  # verify key present
# 401: key hết hạn → rotate tại platform.openai.com
# 429: rate limit → cron đang chạy quá nhiều concurrent calls
```

---

## 9. Key File Locations

| File | Mô tả |
|------|-------|
| `.env` | Feature flags, API keys |
| `wiki/products/` | Production wiki pages |
| `wiki/products.v0.3-backup/` | v0.3 backup (keep 30 days) |
| `claims/approved/` | Approved claims |
| `claims/.review-queue/` | Human review queue (DISAGREE) |
| `build/snapshots/` | Immutable build snapshots |
| `logs/dual-vote-YYYY-MM.jsonl` | Dual-vote event log |
| `logs/openai-calls-YYYY-MM.jsonl` | OpenAI cost log |
| `scripts/rollback-v0.4.sh` | 1-click rollback |
| `trienkhai/upgrade-v0.4/` | Upgrade plan and artifacts |

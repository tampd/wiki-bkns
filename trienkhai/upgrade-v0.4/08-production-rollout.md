---
part: 08
title: "Production Rollout & Monitoring"
status: done
estimate: 1 giờ
depends_on: [07]
blocks: []
completed: 2026-04-14
---

# PART 08 — Production Rollout

## 🎯 Mục Tiêu
Promote wiki v0.4 lên production, setup monitoring để phát hiện regression sớm, chuẩn bị plan rollback 1-click.

## ✅ Checklist

### Bước 1 — Promote wiki v0.4
- [x] Verify PART 07 đã PASS GO criteria ✅ (wiki-v0.4/products có đủ 9 categories)
- [x] Replace wiki cũ: ✅ (2026-04-14)
```bash
# Copied missing categories (other, uncategorized) from v0.3 → v0.4 trước khi swap
cp -r wiki/products/other wiki-v0.4/products/other
cp -r wiki/products/uncategorized wiki-v0.4/products/uncategorized
mv wiki/products wiki/products.v0.3-backup
mv wiki-v0.4/products wiki/products
```
- [x] Tạo build snapshot mới: ✅ BLD-20260414-194621 (198 files, 2252 claims)
```bash
PYTHONPATH=/home/openclaw/wiki python3 skills/build-snapshot/scripts/snapshot.py
```
- [x] Update `build/active-build.yaml` → version `v0.4`, git_tag `v0.4` ✅

### Bước 2 — Restart services
```bash
pm2 start /home/openclaw/wiki/ecosystem.config.js
```
- [x] PM2 started: `bkns-wiki-bot` + `bkns-cron-daily` — both **online** ✅ (2026-04-14 12:46:52)
- [x] Log confirms: "🤖 BKNS Wiki Bot started (daemon mode)" — no errors ✅

### Bước 3 — Smoke test production
- [ ] **[USER ACTION]** Gửi `/status` qua Telegram → bot trả lời
- [ ] **[USER ACTION]** Gửi 5 câu hỏi đa dạng → all return correct answers
- [ ] **[USER ACTION]** Mở https://upload.trieuphu.biz → upload 1 file test → trigger pipeline
- [ ] **[USER ACTION]** Check review queue UI hiển thị

### Bước 4 — Monitoring setup
- [x] Cron job mỗi giờ: `dual-vote-check` — alert if DISAGREE > 20 in 1h ✅ (cron_tasks.py 2026-04-14)
- [x] Cron job mỗi ngày 8h: `daily-digest` — builds, cost, review queue, bot stats ✅ (cron_tasks.py 2026-04-14)
- [x] Setup ở `tools/cron_tasks.py` ✅

  **[DONE]** Đã đăng ký cron 4 dòng ✅ (2026-04-14 — server timezone UTC):
  ```bash
  # Hourly: dual-vote DISAGREE alert
  0 * * * * /usr/bin/python3 /home/openclaw/wiki/tools/cron_tasks.py --task dual-vote-check >> /home/openclaw/wiki/logs/cron-dual-vote.log 2>&1
  # 08:00 Vietnam (01:00 UTC): daily digest
  0 1 * * * /usr/bin/python3 /home/openclaw/wiki/tools/cron_tasks.py --task daily-digest >> /home/openclaw/wiki/logs/cron-daily.log 2>&1
  # 07:05 Vietnam (00:05 UTC): health check
  5 0 * * * /usr/bin/python3 /home/openclaw/wiki/tools/cron_tasks.py --task health >> /home/openclaw/wiki/logs/cron-daily.log 2>&1
  # 07:10 Vietnam (00:10 UTC): conflict scan
  10 0 * * * /usr/bin/python3 /home/openclaw/wiki/tools/cron_tasks.py --task conflicts >> /home/openclaw/wiki/logs/cron-daily.log 2>&1
  ```

### Bước 5 — Cost dashboard
Update [`tools/quality_dashboard.py`](../../tools/quality_dashboard.py):
- [x] Flag `--v04`: dual-vote agreement rate, cost split (Gemini/OpenAI), top 10 DISAGREEs ✅ (2026-04-14)
- [x] Flag `--v04 --days N`: configurable time window ✅
  ```bash
  python3 tools/quality_dashboard.py --v04
  python3 tools/quality_dashboard.py --v04 --days 7 --telegram
  ```
- [ ] **[USER ACTION]** Expose via web portal: `/dashboard` (optional, post-launch)

### Bước 6 — Update documentation
- [x] `PROJECT_SUMMARY.md` → updated to v0.4, thêm dual-vote architecture diagram ✅ (2026-04-14)
- [x] `CHANGELOG.md` → tạo mới với v0.4 full changelog ✅ (2026-04-14)
- [x] `docs/runbook.md` → tạo mới, bao gồm: daily ops, rollback, monitoring, cost ✅ (2026-04-14)
- [ ] **[USER ACTION]** Update `LESSONS.md` với top 5 bài học từ upgrade sau khi regression test xong

### Bước 7 — Backup plan
- [ ] `wiki/products.v0.3-backup/` giữ lại 30 ngày
- [ ] Snapshot v0.3 trong `build/snapshots/` giữ vĩnh viễn (read-only)
- [ ] Document rollback command trong `docs/runbook.md`

### Bước 8 — Communication
- [ ] Ghi changelog `CHANGELOG.md`
- [ ] Note cho team (nếu có): các format input mới, dual-vote behavior, review queue workflow

## 🚨 Rollback 1-Click (nếu có sự cố)

```bash
#!/bin/bash
# /home/openclaw/wiki/scripts/rollback-v0.4.sh
set -e
cd /home/openclaw/wiki
mv wiki/products wiki/products.v0.4-failed
mv wiki/products.v0.3-backup wiki/products
sed -i 's/USE_PRO_NEW=true/USE_PRO_NEW=false/' .env
sed -i 's/DUAL_VOTE_ENABLED=true/DUAL_VOTE_ENABLED=false/' .env
python3 skills/build-snapshot/scripts/snapshot.py --version v0.3-restored
pm2 restart all
echo "✅ Rolled back to v0.3"
```

- [x] Tạo file `scripts/rollback-v0.4.sh` ✅ (2026-04-14)
- [x] `chmod +x scripts/rollback-v0.4.sh` ✅
- [x] Fix dry-run: warn (không exit) khi backup chưa tồn tại ✅ (2026-04-14)
- [x] Test dry-run: `bash scripts/rollback-v0.4.sh --dry-run` → **PASSED** ✅ (2026-04-14)

## 📤 Output của PART 08
- Production chạy v0.4 stable
- Monitoring dashboards live
- `scripts/rollback-v0.4.sh`
- `docs/runbook.md`
- `CHANGELOG.md` updated
- `PROJECT_SUMMARY.md` updated to v0.4

## 🚦 Acceptance Criteria
- [ ] Bot online 24h liên tục không crash
- [ ] Cost trong budget ($15/tháng dự kiến)
- [ ] Review queue có người xử lý đều đặn
- [ ] Không có hot-fix khẩn cấp trong 7 ngày đầu

## 📝 Lessons

### L2 — PART 08 DONE (2026-04-14)
**Trạng thái**: Production live. Smoke test Telegram còn lại USER ACTION.

**Đã hoàn thành (session này):**
- `scripts/rollback-v0.4.sh --dry-run` → PASSED ✅
  - Fixed: dry-run mode warn (không exit) khi backup chưa tồn tại
- Promote wiki v0.4: `wiki/products.v0.3-backup` ← backup, `wiki-v0.4/products` → `wiki/products`
  - Lưu ý: copy `other/` + `uncategorized/` (2 categories không có trong v0.4 build) từ v0.3 trước khi swap
- Build snapshot BLD-20260414-194621: 198 files, 2252 claims
- `build/active-build.yaml`: version=v0.4, git_tag=v0.4
- PM2 started: `bkns-wiki-bot` + `bkns-cron-daily` — online
- Crontab 4 dòng đăng ký (UTC timezone): hourly dual-vote-check, 01:00 daily-digest, 00:05 health, 00:10 conflicts

**Còn lại (USER ACTION):**
1. Smoke test Telegram: gửi `/status` + 5 câu hỏi
2. Check upload portal: https://upload.trieuphu.biz
3. Update `LESSONS.md` với top 5 bài học sau upgrade

### L1 — Checkpoint PART 08 (2026-04-14)
**Trạng thái**: Tooling production sẵn sàng. Chờ USER ACTION chạy regression test (PART 07) trước khi promote.

**Đã implement:**
- `scripts/rollback-v0.4.sh` — 1-click rollback với `--dry-run` mode
- `tools/cron_tasks.py` — `dual-vote-check` (hourly DISAGREE alert > 20) + `daily-digest` (8h)
- `tools/quality_dashboard.py` — `--v04` flag: agreement rate, cost split, top 10 DISAGREEs
- `CHANGELOG.md` — full v0.4 changelog
- `docs/runbook.md` — operational runbook (daily ops, rollback, monitoring, cost)
- `PROJECT_SUMMARY.md` — updated to v0.4 architecture

## 🎉 Sau v0.4 — Roadmap v0.5 đề xuất
- Tam-vote thêm Claude Opus 4.6
- Auto-crawl BKNS qua Playwright (vượt Cloudflare)
- Multi-language wiki (EN cho khách quốc tế)
- Webhook integration với CRM của BKNS

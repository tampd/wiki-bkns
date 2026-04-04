# Automation Loops — Vòng Lặp Tự Động Hóa

---

## Ba Vòng Lặp Chính

### Loop 1: Data Ingestion Loop (On-demand)

```
Admin /them URL
    │
    ▼
crawl-source → raw/ → extract-claims → claims/.drafts/
                                              │
                                    (conflict detection)
                                              │
                                    Admin /compile
                                              │
                                    compile-wiki + self-review
                                              │
                                    wiki/.drafts/
                                              │
                                    Admin /duyet
                                              │
                                    wiki/ + build-snapshot
                                              │
                                    query-wiki cache invalidated ✅
```

**Trigger:** Admin gủi `/them URL`
**Thời gian:** ~15-30 phút (crawl + extract + compile + review + duyet)
**Chi phí:** ~$0.03-0.15 per URL (Pro cho extract + compile)

---

### Loop 2: Quality Assurance Loop (Automated weekly)

```
Monday 09:00 (cron)
    │
    ▼
lint-wiki Layer A (Python, $0)
    │ Issues found?
    ├─ YES: Layer B (Gemini Pro) → semantic analysis
    │           │
    │       Report → logs/lint/report-{date}.md
    │           │
    │       Telegram summary → Admin
    │
    └─ NO: "✅ Syntax OK, running Layer B..."

Sunday 22:00 (cron)
    │
    ▼
ground-truth → re-crawl bkns.vn (5 URLs)
    │
    ▼
Compare live vs wiki claims
    │ Mismatch?
    ├─ YES: ⚠️ Alert admin + auto-queue recrawl
    └─ NO: "✅ Wiki up to date"
```

**Trigger:** Cron (Monday lint, Sunday ground-truth)
**Chi phí:** ~$0.07-0.20/tuần

---

### Loop 3: Knowledge Enhancement Loop (Background)

```
After every query (background):
    │
    ▼
auto-file: check question frequency
    │ frequency ≥ 3 + answer complete?
    ├─ YES: Create FAQ candidate → wiki/.drafts/faq/
    └─ NO: skip

Friday 09:00 (cron):
    │
    ▼
Telegram digest: "{N} FAQ candidates tuần này"
    │
    ▼
Admin /file-review → /duyet → wiki/faq/

After every /duyet (auto):
    │
    ▼
cross-link: scan wiki for unlinked mentions
    │
    ▼
Changeset → Admin preview → /apply-links
```

**Trigger:** Background sau query + cron Friday
**Chi phí:** ~$0.001/query (Flash)

---

## Cron Jobs Configuration

```cron
# /etc/cron.d/bkns-wiki hoặc crontab -e

# Syntax check hàng ngày 06:00
0 6 * * * /usr/bin/python3 /home/openclaw/wiki/skills/lint-wiki/scripts/syntax_check.py >> /home/openclaw/wiki/logs/cron.log 2>&1

# Full lint Thứ Hai 09:00 (Python + Gemini Pro)
0 9 * * 1 /usr/bin/python3 /home/openclaw/wiki/skills/lint-wiki/scripts/lint.py >> /home/openclaw/wiki/logs/cron.log 2>&1

# Ground truth Chủ Nhật 22:00
0 22 * * 0 /usr/bin/python3 /home/openclaw/wiki/skills/ground-truth/scripts/ground_truth.py >> /home/openclaw/wiki/logs/cron.log 2>&1

# FAQ digest Thứ Sáu 09:00
0 9 * * 5 /usr/bin/python3 /home/openclaw/wiki/skills/auto-file/scripts/digest.py >> /home/openclaw/wiki/logs/cron.log 2>&1
```

---

## agents.yaml — OpenClaw Configuration

```yaml
name: bkns-wiki-agent
description: Agent wiki tri thức BKNS — thủ thư tự động (Karpathy pattern)

telegram:
  bot_token: ${TELEGRAM_BOT_TOKEN}
  admin_ids:
    - ${ADMIN_TELEGRAM_ID}

workspace: /home/openclaw/wiki/

models:
  default: gemini-2.5-flash
  compile: gemini-2.5-pro
  lint: gemini-2.5-pro
  ingest: gemini-2.5-flash

vertex_ai:
  project: ${VERTEX_PROJECT_ID}
  location: ${VERTEX_LOCATION}
  credentials: ${GOOGLE_APPLICATION_CREDENTIALS}

# Skills enabled theo phase
skills:
  # Phase 0.5 (core)
  - skills/query-wiki/SKILL.md
  # Phase 1 (automation)
  - skills/ingest-raw/SKILL.md
  - skills/compile-wiki/SKILL.md
  - skills/ingest-image/SKILL.md
  - skills/lint-wiki/SKILL.md
  - skills/ground-truth/SKILL.md
  # Phase 2 (intelligence)
  # - skills/auto-file/SKILL.md     # Enable khi Phase 2
  # - skills/cross-link/SKILL.md    # Enable khi Phase 2

memory:
  type: file
  path: /home/openclaw/wiki/build/active-build.yaml

logging:
  level: INFO
  path: /home/openclaw/wiki/logs/
```

---

## Tổng Kết: Vòng Lặp Karpathy Hoàn Chỉnh

```
                    ┌─────────────────────────────────────┐
                    │         KARPATHY LOOP — BKNS        │
                    │                                     │
               ┌────┴────┐                          ┌─────┴─────┐
               │  INGEST  │                          │  FILING   │
               │ crawl    │                          │ auto-file │
               │ image    │                          │ cross-link│
               └────┬────┘                          └─────┬─────┘
                    │                                     ↑
                    ▼                                     │
               ┌────┴────┐                          ┌─────┴─────┐
               │ EXTRACT  │                          │  QUERY    │
               │ claims   │                          │query-wiki │
               └────┬────┘                          └─────┬─────┘
                    │                                     ↑
                    ▼                                     │
  ┌─────────┐ ┌────┴────┐ ┌──────────┐ ┌──────┐ ┌──────┴────┐
  │CONFLICT │ │ COMPILE  │ │  SELF-   │ │/duyet│ │   BUILD   │
  │ DETECT  │ │  wiki    │→│  REVIEW  │→│admin │→│ snapshot  │
  └─────────┘ └─────────┘ └──────────┘ └──────┘ └───────────┘
                                                       │
                                          ┌────────────┴────────────┐
                                          │    QUALITY LOOP         │
                                          │  lint + ground-truth    │
                                          │  (weekly automated)     │
                                          └─────────────────────────┘

Nguyên tắc đảm bảo:
  Bot KHÔNG bịa      → Self-review so sánh draft vs claims gốc
  Bot KHÔNG ghi wiki → Mọi output → .drafts/ → /duyet
  Báo lỗi admin      → Telegram alert ở mỗi bước fail
  Tự đọc lại         → Self-review prompt (compile skill)
  Audit trail        → JSONL traces + Git commits + build tags
  Phát hiện conflict → Conflict detection + ground-truth weekly
  Tự cải thiện       → auto-file + cross-link + lint weekly
```

---

## Kill Criteria

Dừng dự án nếu bất kỳ điều kiện nào xảy ra:

| Criterion | Threshold | Hành động |
|-----------|-----------|-----------|
| Budget burn | >$50/tháng trước Phase 1 xong | Dừng, review model usage |
| Cache hit rate | <50% sau 2 tuần | Kiểm tra Vertex implicit caching |
| Bot accuracy | >30% sai trong 20 câu cơ bản | Review wiki content + system prompt |
| Vertex AI trial | Không support implicit caching | Xem xét thay thế |

# Bảng Tổng Hợp 10 Skills — BKNS Agent Wiki

---

## Tổng Quan 10 Skills

| # | Skill ID | Phase | Model | Cost/lần | Trigger | Vai trò |
|---|----------|-------|-------|----------|---------|---------|
| 1 | `crawl-source` | 0.5 | Script Python | $0 | `/them [URL]` | Thu thập trang bkns.vn → raw/ |
| 2 | `extract-claims` | 0.5 | Gemini Pro | $0.01-0.05/file | `/extract` | raw/ → claims YAML + JSONL |
| 3 | `compile-wiki` | 0.5 | Gemini Pro | $0.02-0.08/page | `/compile` | claims → wiki draft + self-review |
| 4 | `query-wiki` | 0.5 | Gemini Flash | $0.001-0.005/query | `/hoi` / tin nhắn | Trả lời câu hỏi (cached prefix) |
| 5 | `ingest-image` | 1 | Gemini Flash Vision | $0.01-0.03/ảnh | `/anh` / gửi ảnh | Extract bảng giá từ ảnh |
| 6 | `lint-wiki` | 1 | Pro + Script | $0.05-0.15/lần | `/lint` / cron weekly | Kiểm tra mâu thuẫn, outdated |
| 7 | `ground-truth` | 1 | Flash + crawl | $0.02-0.05/lần | `/verify` / cron weekly | Wiki vs website live |
| 8 | `auto-file` | 2 | Gemini Flash | $0.001/query | Tự động sau query | FAQ candidates từ queries lặp |
| 9 | `cross-link` | 2 | Gemini Flash | $0.01/lần | `/crosslink` / sau compile | Liên kết chéo tự động |
| 10 | `build-snapshot` | 1 | Script Python | $0 | Tự động sau `/duyet` | Build manifest + Git tag |

---

## Dependency Map

```
crawl-source (1)
    └─→ extract-claims (2)
            └─→ compile-wiki (3)  [bao gồm self-review]
                    └─→ [admin /duyet]
                            └─→ build-snapshot (10)
                                    └─→ query-wiki (4)
                                            └─→ auto-file (8)
                                                    └─→ cross-link (9)

ingest-image (5)
    └─→ extract-claims (2) [dùng lại]

lint-wiki (6)  ← độc lập, đọc toàn bộ wiki/
ground-truth (7) ← độc lập, crawl lại bkns.vn
```

---

## Phase Roadmap

### Phase 0.5 — Core MVP (2 tuần)
> **Mục tiêu:** Bot trả lời câu hỏi từ wiki cơ bản

- ✅ crawl-source: batch crawl 5 trang bkns.vn
- ✅ extract-claims: trích facts từ raw/
- ✅ compile-wiki: tạo 8+ wiki pages (có self-review)
- ✅ query-wiki: bot Telegram trả lời /hoi
- ✅ Test 20 queries đạt ≥80% (16/20)

**Definition of Done Phase 0.5:**
```
□ Bot trả lời /hoi trên Telegram
□ ≥8 wiki files trong wiki/ (không kể .drafts/)
□ wiki/support/lien-he.md có đúng 2 hotline
□ build/active-build.yaml → v0.1
□ Test 20 queries: ≥16/20 đúng
□ Log ghi cache hit rate + cost
□ Git tag: build/v0.1
```

### Phase 1 — Automation Pipeline (2-3 tuần)
> **Mục tiêu:** Pipeline đầy đủ từ ingest đến publish

- ✅ ingest-raw: /them URL → auto crawl
- ✅ build-snapshot: tự động sau /duyet
- ✅ ingest-image: extract ảnh bảng giá
- ✅ lint-wiki: kiểm tra weekly
- ✅ ground-truth: verify weekly
- ✅ MkDocs Material: wiki web cho nhân viên

**Definition of Done Phase 1:**
```
□ /them [URL] → raw/ → /compile → draft → /duyet → wiki/
□ /anh (ảnh bảng giá) → claims draft
□ Cron lint 09:00 Monday → Telegram report
□ Cron ground-truth Sunday 22:00 → Telegram report
□ MkDocs chạy được: mkdocs serve
□ Git tag: build/v0.2
```

### Phase 2 — Intelligence (4-6 tuần)
> **Mục tiêu:** Wiki tự cải thiện, filing câu trả lời hay

- ✅ auto-file: FAQ candidates từ queries lặp
- ✅ cross-link: liên kết chéo tự động
- ✅ Onboarding wiki 3 đối tượng
- ✅ Observability: cost dashboard

**Definition of Done Phase 2:**
```
□ FAQ candidates tự động xuất hiện sau 3 queries lặp
□ /crosslink tạo được "Xem thêm" sections
□ wiki/onboarding/ có 3 files
□ Log cost đủ để tính tổng tháng
```

---

## Cron Schedule

```
# Cron jobs (server crontab)

# Lint kiểm tra wiki — Thứ Hai 09:00
0 9 * * 1 python /home/openclaw/wiki/skills/lint-wiki/scripts/lint.py >> /home/openclaw/wiki/logs/cron.log 2>&1

# Ground truth verify — Chủ Nhật 22:00
0 22 * * 0 python /home/openclaw/wiki/skills/ground-truth/scripts/ground_truth.py >> /home/openclaw/wiki/logs/cron.log 2>&1

# Syntax check — Mỗi ngày 06:00 (script Python, không LLM)
0 6 * * * python /home/openclaw/wiki/skills/lint-wiki/scripts/syntax_check.py >> /home/openclaw/wiki/logs/cron.log 2>&1
```

---

## SKILL.md Template Chuẩn

Mỗi skill trong `skills/{name}/SKILL.md` phải có cấu trúc:

```yaml
---
name: {skill-name}
description: >
  Mô tả 1-3 câu, bao gồm: làm gì, khi nào trigger, output là gì.
version: "1.0"
phase: "0.5"              # Phase ra mắt
model: gemini-2.5-flash   # hoặc gemini-2.5-pro
admin_only: true          # false nếu end users cũng dùng được
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - python3
      install:
        uv: "requests pyyaml python-dotenv vertexai"
triggers:
  - command: /ten-lenh
  - pattern: "regex pattern nếu có"  # optional
---

# {skill-name}

## Mô tả
[Chi tiết hơn description trong frontmatter]

## Input
[Các loại input được chấp nhận]

## Output
[Output sẽ tạo ra gì, ở đâu]

## Model
[Giải thích tại sao chọn model này]

## Files
- scripts/{main}.py: logic chính
```

---

## Logging Format Chuẩn (Mọi Skill)

```jsonl
{"ts":"2026-04-04T10:30:00+07:00","skill":"skill-name","action":"start|success|error|skip","detail":"mô tả ngắn","cost_usd":0.0,"extra":{}}
```

Ghi vào: `logs/{skill-name}-{YYYY-MM-DD}.jsonl` hoặc tập trung vào `logs/errors/YYYY-MM-DD.jsonl` nếu lỗi.

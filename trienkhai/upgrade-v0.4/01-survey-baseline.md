---
part: 01
title: "Survey Baseline & Risk Audit"
status: complete
completed_at: 2026-04-13
estimate: 30 phút
actual: ~45 phút
depends_on: []
blocks: [02, 03, 04, 05]
---

# PART 01 — Survey Baseline & Risk Audit

## 🎯 Mục Tiêu
Chốt số liệu hiện tại làm benchmark, snapshot toàn bộ wiki v0.3 thành immutable backup, identify rủi ro trước khi nâng cấp.

## ✅ Checklist

### Bước 1 — Snapshot v0.3 (immutable backup)
- [x] Tạo thư mục `build/snapshots/v0.3-pre-upgrade-2026-04-13/`
- [x] Copy `wiki/products/`, `wiki/faq/`, `claims/approved/`, `build/active-build.yaml`
- [x] Tạo `MANIFEST.yaml` ghi: ngày, số file, tổng size, sha256 từng file
- [x] `chmod -R a-w` để bảo vệ snapshot khỏi sửa nhầm

```bash
SNAP=/home/openclaw/wiki/build/snapshots/v0.3-pre-upgrade-$(date +%F)
mkdir -p "$SNAP"
cp -r /home/openclaw/wiki/wiki "$SNAP/wiki"
cp -r /home/openclaw/wiki/claims/approved "$SNAP/claims-approved"
cp /home/openclaw/wiki/build/active-build.yaml "$SNAP/active-build.yaml"
find "$SNAP" -type f -exec sha256sum {} \; > "$SNAP/MANIFEST.sha256"
chmod -R a-w "$SNAP"
```

### Bước 2 — Đo baseline metrics
Chạy và lưu vào `trienkhai/upgrade-v0.4/baseline-metrics.json`:

- [x] Số raw files: `find raw/manual -type f | wc -l` → expect 291
- [x] Số claims approved: `find claims/approved -name "*.yaml" | wc -l` → expect 2,252
- [x] Số wiki pages: `find wiki -name "*.md" -not -path "*/_templates/*" | wc -l` → expect 213
- [x] Tổng tokens wiki: chạy `tools/quality_dashboard.py` (hoặc viết script đếm)
- [x] Tổng cost đến nay: parse `logs/extract-claims-*.jsonl` + `logs/compile-wiki-*.jsonl`
- [x] Số conflicts hiện có: `grep -c "conflict" claims/.drafts/**/*.yaml`

### Bước 3 — Audit rủi ro nâng cấp
Đánh dấu file/skill có nguy cơ break khi đổi LLM:

- [x] [`lib/gemini.py`](../../lib/gemini.py) — wrapper Vertex AI, dùng `genai.Client(vertexai=True)`
  - Risk: API có thể thay đổi giữa 2.5 → 3.1 (kiểm tra `Part.from_text` signature)
- [x] [`skills/extract-claims/scripts/extract.py`](../../skills/extract-claims/scripts/extract.py) (751 dòng) — dùng MODEL_PRO
  - Risk: prompt template có thể cần tinh chỉnh cho 3.1
- [x] [`skills/compile-wiki/scripts/compile.py`](../../skills/compile-wiki/scripts/compile.py) (910 dòng) — dùng MODEL_PRO + self-review
  - Risk: temperature/top_p có thể cần điều chỉnh
- [x] [`tools/convert_manual.py`](../../tools/convert_manual.py) — dùng `mammoth` + `pdfminer`
  - Risk: sẽ thay bằng markitdown (PART 03)
- [x] `.env` — cần thêm `MODEL_PRO_NEW`, `OPENAI_API_KEY`, `OPENAI_MODEL` (PART 04, 05)

### Bước 4 — Identify "ground truth" cho test
Chọn **5 wiki pages** và **20 claims** đại diện làm test set:
- [x] 5 categories khác nhau (hosting, vps, ssl, ten-mien, email)
- [x] Mỗi category: 1 page + 4 claims (mix easy/hard)
- [x] Lưu test set vào `trienkhai/upgrade-v0.4/test-set.yaml` với expected values
- [x] Đặc biệt: chọn các claim **đã human-verified** (giá tiền, thông số) để làm benchmark accuracy

### Bước 5 — Cost guard setup
- [x] Tạo `cost-guard.yaml` (config ngưỡng $20 vertex + $10 openai, alert 50/75/90/100%)
- [x] Tạo `tools/check_cost_budget.py` (CLI + import API `assert_within_budget`) — smoke-test pass: 0% spent kể từ 2026-04-13
- [x] Tạo `cost-guard-runbook.md` chi tiết các bước Cloud Console
- [ ] **USER ACTION** — Set hard limit Vertex AI $20 (Cloud Console → Billing → Budget), điền `cloud_console_budget_id` vào cost-guard.yaml
- [ ] **USER ACTION** — Set hard limit OpenAI $10 sau khi PART 05 xong (platform.openai.com/account/limits), điền `org_id`

## 📤 Output của PART 01
File phải tồn tại sau khi xong:
- `build/snapshots/v0.3-pre-upgrade-2026-04-13/` (read-only)
- `trienkhai/upgrade-v0.4/baseline-metrics.json`
- `trienkhai/upgrade-v0.4/test-set.yaml`
- `trienkhai/upgrade-v0.4/risk-audit.md` (kết luận audit)

## 🔙 Rollback
PART 01 chỉ tạo file mới + snapshot, không sửa code production → không cần rollback.

## 📤 Output thực tế (đã tạo)

| Path | Mô tả |
|---|---|
| `build/snapshots/v0.3-pre-upgrade-2026-04-13/` | Read-only, 2,478 files, 1.99 MB, MANIFEST.yaml + MANIFEST.sha256 |
| `trienkhai/upgrade-v0.4/baseline-metrics.json` | 291 raw / 2,252 claims / 213 pages / 160K tokens / cumulative $35.77 |
| `trienkhai/upgrade-v0.4/risk-audit.md` | Audit code surface, SDK compat, failure modes, rollback plan, GO/NO-GO criteria |
| `trienkhai/upgrade-v0.4/test-set.yaml` | 5 pages × 4 claims (8 verified ground-truth + 12 normal), seed=42, accept ≥90% exact match |
| `trienkhai/upgrade-v0.4/cost-guard.yaml` | Budget config $20+$10, v04_start_date 2026-04-13 |
| `trienkhai/upgrade-v0.4/cost-guard-runbook.md` | Hướng dẫn user setup Cloud Console + OpenAI dashboard |
| `tools/check_cost_budget.py` | CLI + import API `assert_within_budget` |

## 📝 Lessons

### L01.1 — Cumulative log cost ≠ baseline-per-build
Khi tính `cumulative cost` từ tất cả `logs/extract-claims-*.jsonl + logs/compile-wiki-*.jsonl` trong tháng → ra **$35.77**, không phải **$6.50** mà INDEX nói.

- **Why**: INDEX nói "$6.50/build" — đây là chi phí **một** build session (vd ngày 04-04). Cumulative $35.77 phản ánh nhiều phiên rebuild + expand category trong 5 ngày (04-04 → 04-08).
- **How to apply**: Khi tạo cost-guard, **track theo `v04_start_date`** (filter `ts >= 2026-04-13` trong log entries), không filter theo tháng. Đã implement ở `tools/check_cost_budget.py:cumulative_cost_since()`.

### L01.2 — Snapshot `chmod -R a-w` bao gồm cả parent dir
Sau khi `chmod -R a-w` thì cả thư mục snapshot cũng read-only → không thể `mkdir` hay `touch` mới. Đây là behavior mong muốn (immutable) — verify bằng `touch test.txt` → permission denied.

- **Why**: Snapshot là bằng chứng baseline, không được sửa. Nếu cần restore, runbook phải có `sudo chmod -R u+w` ở đầu (đã ghi trong MANIFEST.yaml).
- **How to apply**: PART 03+ khi cần đối chiếu output mới với snapshot, **đọc-only** — không git restore từ snapshot, dùng `cp -r` rồi mới sửa.

### L01.3 — `cd` trong Bash session persist giữa các tool calls
Khi chạy `cd "$SNAP"` trong Bash tool, working dir thay đổi cho call sau. Lệnh tiếp theo dùng `$SNAP` relative path → fail vì cwd đã ở trong snapshot rồi.

- **Why**: Spec ghi rõ "The working directory persists between commands". Tốn 1 lần fail vì chủ quan.
- **How to apply**: Trong PART 02-08, **dùng absolute paths** trong tất cả Bash commands hoặc luôn `cd /home/openclaw/wiki &&` đầu mỗi command để reset.

### L01.4 — Cloud Console actions không thể tự động qua Claude
Vertex billing budget + OpenAI usage limit là user actions trên web console. Tạo runbook chi tiết, đánh dấu `USER ACTION` rõ trong checklist, nhưng **không tự ý gọi billing API** (sẽ cần OAuth credentials user chưa cấp + ảnh hưởng shared infra).

- **Why**: Theo CLAUDE.md "carefully consider reversibility and blast radius" — billing budget mismatch có thể gây alert spam hoặc miss spike.
- **How to apply**: Mọi PART tiếp theo có "Cloud Console" / "DNS" / "PM2" / "git push" → tạo runbook + flag user action, không tự thực thi.

---

## ✅ Bước tiếp theo

- PART 02: cài + test markitdown trên 3 file mẫu (1 docx, 1 pdf, 1 xlsx) — branch `upgrade-v0.4-part02`.
- User cần làm Cloud Console budget setup (Bước 5 USER ACTION) trước khi chạy PART 04 (start LLM calls thực).

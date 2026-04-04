# Skill 5: ingest-image — Extract Bảng Giá Từ Ảnh

> **Phase:** 1 | **Model:** Gemini 2.5 Flash (Vision) | **Cost:** ~$0.01-0.03/ảnh

---

## SKILL.md

```yaml
---
name: ingest-image
description: >
  Nhận ảnh bảng giá/screenshot từ Telegram, lưu evidence, 
  dùng Gemini Flash Vision extract thành claims draft.
  Ảnh gốc → Git LFS. Thumbnail → assets/images/.
  Trigger: admin gửi ảnh kèm /anh hoặc gửi ảnh trực tiếp.
user-invocable: true
---
```

## Workflow

```
BƯỚC 1: Nhận ảnh từ Telegram
  ├─ Lưu gốc: assets/evidence/{category}/{name}-original.{ext} (Git LFS)
  └─ Tạo thumbnail: assets/images/{name}-thumb.{ext}

BƯỚC 2: Gemini Flash Vision extract
  ├─ Prompt: "Extract TOÀN BỘ bảng giá. Giữ nguyên số liệu.
  │   Nếu ô mờ → ghi [KHÔNG RÕ]. KHÔNG suy luận."
  └─ Output: JSON claims array (giống extract-claims format)

BƯỚC 3: Tạo Evidence record
  └─ evidence_id, kind=image, paths, hash, human_verified=false

BƯỚC 4: Tạo claims draft từ extract
  ├─ claims/.drafts/ (YAML + JSONL)
  ├─ evidence_refs → evidence_id
  └─ risk_class = high (ảnh luôn cần review)

BƯỚC 5: Hỏi admin xác nhận
  └─ "📷 Đây có phải bảng giá [Hosting]? Tôi extract được {N} mục giá.
      Preview: [bảng tóm tắt]. Gõ /duyet-anh để xác nhận."

BƯỚC 6: Self-review
  ├─ Bot đọc lại extract, kiểm tra số có hợp lý không
  ├─ Giá = 0 hoặc âm → cảnh báo
  └─ So sánh với claims approved hiện có → detect conflicts
```

## Vision Extract Prompt

```
Extract TOÀN BỘ bảng giá trong ảnh thành JSON claims.

QUY TẮC:
1. Giữ nguyên số liệu: giá, RAM, CPU, SSD, bandwidth
2. Chuẩn hóa đơn vị: tiền → VND, dung lượng → GB/TB
3. Nếu ô mờ/không đọc được → value: "[KHÔNG RÕ]", confidence: "low"
4. KHÔNG suy luận giá trị bị che
5. Mỗi dòng bảng giá = 1 claim object riêng

OUTPUT: JSON array claims (cùng format extract-claims)
```

---

# Skill 6: lint-wiki — Kiểm Tra Chất Lượng Wiki

> **Phase:** 1 | **Model:** Gemini 2.5 Pro | **Cost:** ~$0.05-0.15/lần
> **Schedule:** Cron 09:00 Thứ Hai hàng tuần + manual /lint

---

## SKILL.md

```yaml
---
name: lint-wiki
description: >
  Kiểm tra toàn bộ wiki tìm: mâu thuẫn giá, thông tin lỗi thời,
  thiếu nguồn, orphan files, nội dung bất hợp lý.
  Dùng Gemini Pro cho reasoning sâu.
  Output: báo cáo Markdown + Telegram summary.
  Trigger: /lint hoặc cron weekly.
user-invocable: true
---
```

## Lint Gồm 2 Layer

### Layer A: Script Python (cost=$0, chạy trước)

```python
def syntax_lint(wiki_dir):
    """Kiểm tra cú pháp — KHÔNG cần LLM"""
    issues = []
    for f in Path(wiki_dir).rglob("*.md"):
        content = f.read_text()
        # 1. Frontmatter check
        if not content.startswith('---'):
            issues.append({"file": str(f), "type": "missing_frontmatter", "severity": "error"})
            continue
        try:
            fm = yaml.safe_load(content.split('---')[1])
            for field in ['title', 'category', 'updated']:
                if field not in fm:
                    issues.append({"file": str(f), "type": f"missing_{field}", "severity": "warning"})
            # Freshness check
            if 'updated' in fm:
                age = (datetime.now() - datetime.strptime(str(fm['updated']), '%Y-%m-%d')).days
                if age > 30:
                    issues.append({"file": str(f), "type": "stale", "age_days": age, "severity": "info"})
        except: 
            issues.append({"file": str(f), "type": "invalid_frontmatter", "severity": "error"})
        # 2. Broken images
        for m in re.finditer(r'!\[.*?\]\((.*?)\)', content):
            img = m.group(1)
            if not img.startswith('http') and not (f.parent / img).exists():
                issues.append({"file": str(f), "type": "broken_image", "path": img, "severity": "error"})
        # 3. Empty body
        body = content.split('---', 2)[-1].strip()
        if len(body) < 50:
            issues.append({"file": str(f), "type": "empty_file", "severity": "warning"})
    return issues
```

### Layer B: Gemini Pro (semantic lint)

```
Bạn là kiểm toán viên wiki BKNS. Đọc toàn bộ wiki và kiểm tra:

🔴 MÂU THUẪN GIÁ: Cùng sản phẩm, giá khác ở file khác nhau?
🟡 THÔNG TIN LỖI THỜI: updated > 30 ngày, ngày đã qua hạn?
🟠 THIẾU NGUỒN: Bảng giá không có source URL?
🔵 ORPHAN FILES: File không ai link đến?
💡 ĐỀ XUẤT TOP 5 CẢI THIỆN

Output: Báo cáo → logs/lint/report-{date}.md
```

## Lint Report → Telegram

```
📊 Báo Cáo Lint — 2026-04-07
━━━━━━━━━━━━━━━━━━━━
🔴 Mâu thuẫn giá: 0 ✅
🟡 Cần verify (>30 ngày): 2 files
🟠 Thiếu nguồn: 1 file  
🔵 Orphan: 0 ✅
📝 Đề xuất: 3 items

Chi tiết: logs/lint/report-2026-04-07.md
/lint-fix để xem actions
```

---

# Skill 7: ground-truth — So Sánh Wiki vs Website Live

> **Phase:** 1 | **Model:** Flash + crawl script | **Cost:** ~$0.02-0.05/lần
> **Schedule:** Cron weekly + manual /verify

---

## SKILL.md

```yaml
---
name: ground-truth
description: >
  Crawl lại bkns.vn, so sánh dữ liệu live vs wiki claims.
  Phát hiện giá thay đổi, sản phẩm mới/bỏ, thông tin lỗi thời.
  Output: báo cáo diff + Telegram alert nếu outdated.
  Trigger: /verify hoặc cron weekly.
user-invocable: true
---
```

## Workflow

```
1. Crawl lại bkns.vn (reuse crawl-source)
2. Extract facts từ crawl mới (reuse extract-claims, KHÔNG lưu)
3. So sánh extracted facts vs claims/approved/:
   ├─ MATCH → ✅ OK
   ├─ MISMATCH → ⚠️ "Giá BKCP01: wiki=26.000đ, live=28.000đ"
   ├─ NEW → 📌 "Sản phẩm mới phát hiện: [tên]"
   └─ MISSING → ❓ "Sản phẩm trong wiki không còn trên web"
4. Tạo report: logs/ground-truth/report-{date}.md
5. Telegram alert nếu có MISMATCH hoặc MISSING
```

## Ground Truth Comparison Prompt

```
So sánh dữ liệu wiki (cũ) vs dữ liệu website (mới):

WIKI CLAIMS: {wiki_claims_json}
LIVE DATA: {live_extracted_json}

Tìm:
1. GIÁ THAY ĐỔI: [entity] wiki={X} → live={Y}
2. SẢN PHẨM MỚI: có trên live nhưng không có trong wiki
3. SẢN PHẨM BỊ XÓA: có trong wiki nhưng không còn trên live
4. SPECS THAY ĐỔI: RAM/CPU/SSD khác

Output JSON: {"matches": N, "mismatches": [...], "new": [...], "missing": [...]}
```

---

*Skills tiếp: [10f-remaining-skills.md](./10f-remaining-skills.md) — auto-file, cross-link, build-snapshot*

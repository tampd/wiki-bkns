# Skill 6: lint-wiki

> **Phase:** 1 | **Model:** Python Script (Layer A, $0) + Gemini Pro (Layer B, ~$0.05-0.15)
> **Schedule:** Cron 09:00 Thứ Hai + manual `/lint`

---

## SKILL.md

```yaml
---
name: lint-wiki
description: >
  Kiểm tra toàn bộ wiki tìm: mâu thuẫn giá giữa các file, thông tin lỗi thời
  (>30 ngày), thiếu nguồn, orphan files, nội dung bất hợp lý.
  Layer A (Python, $0) chạy trước. Layer B (Gemini Pro) cho semantic check.
  Output: báo cáo Markdown + Telegram summary.
  Trigger: /lint hoặc cron weekly Monday 09:00.
version: "1.0"
phase: "1"
model: gemini-2.5-pro
admin_only: true
user-invocable: true
triggers:
  - command: /lint
  - cron: "0 9 * * 1"
---
```

---

## Layer A: Syntax Check (Python, $0)

Chạy TRƯỚC Layer B. Nhanh, không tốn token.

```python
def syntax_lint(wiki_dir: Path) -> list[dict]:
    """Kiểm tra cú pháp + freshness — không cần LLM"""
    issues = []
    all_files = set()
    linked_files = set()

    for f in Path(wiki_dir).rglob("*.md"):
        if ".drafts" in str(f):
            continue
        all_files.add(str(f.relative_to(wiki_dir)))
        content = f.read_text(encoding="utf-8")

        # 1. Frontmatter tồn tại
        if not content.startswith("---"):
            issues.append({"file": str(f), "type": "missing_frontmatter",
                           "severity": "error"})
            continue

        # 2. Frontmatter parse được + có required fields
        try:
            fm = yaml.safe_load(content.split("---")[1])
            for field in ["title", "category", "updated"]:
                if field not in fm:
                    issues.append({"file": str(f), "type": f"missing_{field}",
                                   "severity": "warning"})

            # 3. Freshness check (>30 ngày)
            if "updated" in fm:
                age = (date.today() - date.fromisoformat(str(fm["updated"]))).days
                if age > 30:
                    issues.append({"file": str(f), "type": "stale",
                                   "age_days": age, "severity": "info"})
        except Exception:
            issues.append({"file": str(f), "type": "invalid_frontmatter",
                           "severity": "error"})

        # 4. Broken images
        for m in re.finditer(r'!\[.*?\]\((.*?)\)', content):
            img = m.group(1)
            if not img.startswith("http") and not (f.parent / img).exists():
                issues.append({"file": str(f), "type": "broken_image",
                               "path": img, "severity": "error"})

        # 5. Empty body
        body = content.split("---", 2)[-1].strip() if "---" in content else content
        if len(body) < 50:
            issues.append({"file": str(f), "type": "empty_file",
                           "severity": "warning"})

        # 6. Track links (cho orphan detection)
        for m in re.finditer(r'\[.*?\]\((.*?\.md)\)', content):
            linked_files.add(m.group(1).lstrip("./"))

    # 7. Orphan files
    for f in all_files:
        if f != "index.md" and f not in linked_files:
            issues.append({"file": f, "type": "orphan",
                           "severity": "info"})

    return issues
```

---

## Layer B: Semantic Lint (Gemini Pro)

Chỉ chạy nếu Layer A không có lỗi critical.

```
Bạn là kiểm toán viên wiki BKNS. Đọc toàn bộ wiki và kiểm tra:

🔴 MÂU THUẪN GIÁ:
   Cùng sản phẩm, giá khác nhau ở file khác nhau?
   → Liệt kê: "[FILE A] {product}: {price_A} vs [FILE B]: {price_B}"

🟡 THÔNG TIN LỖI THỜI:
   updated > 30 ngày? Ngày đã qua hạn?
   → Liệt kê file + ngày updated

🟠 THIẾU NGUỒN:
   Bảng giá không có source URL hoặc claim reference?
   → Liệt kê file + section

🔵 ORPHAN FILES:
   File không ai link đến (từ index.md hoặc file khác)?

💡 TOP 5 ĐỀ XUẤT CẢI THIỆN:
   Nội dung còn thiếu, không rõ ràng, cần bổ sung gì?

WIKI CONTENT: {full_wiki_content}

Output: Báo cáo Markdown có sections rõ ràng.
```

---

## Lint Report Output

```markdown
# Báo Cáo Lint Wiki — 2026-04-07

## Tóm Tắt

🔴 Mâu thuẫn giá: 0 ✅
🟡 Cần verify (>30 ngày): 2 files
🟠 Thiếu nguồn: 1 file
🔵 Orphan: 0 ✅
⚠️ Syntax errors: 0 ✅

## Chi Tiết

### 🟡 Cần Verify
- `products/vps/tong-quan.md` — updated: 2026-02-15 (49 ngày trước)
- `products/email/tong-quan.md` — updated: 2026-03-01 (35 ngày trước)

### 🟠 Thiếu Nguồn
- `products/ssl/tong-quan.md` — Section "Bảng Giá" thiếu source reference

### 💡 Đề Xuất
1. Bổ sung FAQ cho trang hosting (câu hỏi phổ biến chưa có wiki)
2. ...
```

---

## Telegram Summary

```
📊 Báo Cáo Lint — 2026-04-07
━━━━━━━━━━━━━━━━━━━━
🔴 Mâu thuẫn giá: 0 ✅
🟡 Cần verify: 2 files
🟠 Thiếu nguồn: 1 file
🔵 Orphan: 0 ✅
⚠️ Syntax: 0 ✅

Chi tiết: logs/lint/report-2026-04-07.md
/lint-fix để xem suggested actions
```

---

## Error Handling

| Lỗi | Hành động |
|-----|----------|
| Wiki rỗng (0 files) | Skip Layer B, báo "Wiki chưa có files" |
| Gemini Pro timeout | Dùng Layer A results, báo "Layer B skip (API timeout)" |
| Report file ghi lỗi | Log error, gửi Telegram plain text |

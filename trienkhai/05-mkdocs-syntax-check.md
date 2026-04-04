# Bước 5: MkDocs Material + Syntax Check Cron

> **Phase:** 1
> **Ước lượng:** 2-3 giờ
> **Prerequisite:** Bước 4 hoàn thành, có ≥10 wiki files
> **Output:** Wiki web cho nhân viên + syntax check tự động mỗi sáng

---

## CHECKLIST

- [ ] 5.1 Cài MkDocs Material
- [ ] 5.2 Cấu hình mkdocs.yml
- [ ] 5.3 Build + deploy (localhost hoặc subdomain)
- [ ] 5.4 Script syntax-check.py (Python, không LLM)
- [ ] 5.5 Setup cron job 06:00 daily
- [ ] 5.6 Test: tạo lỗi → verify alert Telegram

---

## 5.1 Cài MkDocs Material

```bash
pip install mkdocs-material mkdocs-awesome-pages-plugin

# Verify
mkdocs --version
```

---

## 5.2 mkdocs.yml

```yaml
# mkdocs.yml — BKNS Knowledge Base
site_name: BKNS Knowledge Base
site_description: Hệ thống tri thức nội bộ BKNS.VN
site_url: http://localhost:8000  # Thay bằng subdomain khi deploy

theme:
  name: material
  language: vi
  palette:
    - scheme: default
      primary: blue
      accent: light blue
      toggle:
        icon: material/brightness-7
        name: Chuyển sang dark mode
    - scheme: slate
      primary: blue
      accent: light blue
      toggle:
        icon: material/brightness-4
        name: Chuyển sang light mode
  features:
    - search.highlight
    - search.suggest
    - navigation.instant
    - navigation.sections
    - navigation.top
    - content.code.copy

docs_dir: wiki/
site_dir: site/

# Loại trừ .drafts/ khỏi build
exclude_docs: |
  .drafts/**

nav:
  - Trang chủ: index.md
  - Công ty: company/gioi-thieu.md
  - Sản phẩm:
    - Hosting: products/hosting/tong-quan.md
    - VPS: products/vps/tong-quan.md
    - Tên miền: products/ten-mien/tong-quan.md
    - Email Hosting: products/email/tong-quan.md
    - SSL Certificate: products/ssl/tong-quan.md
  - Hỗ trợ: support/lien-he.md

plugins:
  - search:
      lang: vi
      separator: '[\s\-\.]+'

markdown_extensions:
  - tables
  - admonition
  - attr_list
  - def_list
  - toc:
      permalink: true
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences

extra:
  social:
    - icon: fontawesome/solid/globe
      link: https://bkns.vn
      name: BKNS Website
```

---

## 5.3 Build + Deploy

### Phát triển (local)

```bash
cd /home/openclaw/wiki
mkdocs serve --dev-addr=0.0.0.0:8000
# Truy cập: http://[VPS_IP]:8000
```

### Production build

```bash
mkdocs build
# Output trong site/ (không commit site/ vào git)
```

### Deploy với nginx (tùy chọn)

```nginx
# /etc/nginx/sites-available/wiki.bkns.internal
server {
    listen 80;
    server_name wiki.bkns.internal;  # Hoặc IP VPS
    root /home/openclaw/wiki/site;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

```bash
# Auto-rebuild khi wiki thay đổi (thêm vào review.py approve flow)
mkdocs build && echo "[MkDocs] Rebuilt OK"
```

> 💡 **Khuyến nghị Phase 1:** Chỉ cần `mkdocs serve` trên port 8000. Deploy production sau khi có đủ content.

---

## 5.4 Script syntax-check.py

```python
#!/usr/bin/env python3
"""
syntax-check.py: kiểm tra cú pháp wiki — KHÔNG cần LLM, cost = $0
Chạy: python tools/syntax_check.py
Hoặc tự động qua cron: 06:00 daily
"""
import os
import re
import yaml
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

REQUIRED_FRONTMATTER = ["title", "category", "updated", "source", "confidence"]
VALID_CATEGORIES = ["hosting", "vps", "ten-mien", "email", "ssl", "company", "support", "index", "onboarding", "faq"]
VALID_CONFIDENCE = ["high", "medium", "low"]

def check_wiki_files(wiki_dir: Path) -> list[dict]:
    """Kiểm tra tất cả file wiki, trả về danh sách issues."""
    issues = []
    
    for root, dirs, files in os.walk(wiki_dir):
        # Bỏ qua .drafts/
        dirs[:] = [d for d in sorted(dirs) if d != ".drafts"]
        
        for fname in files:
            if not fname.endswith(".md"):
                continue
            
            fpath = Path(root) / fname
            rel_path = fpath.relative_to(wiki_dir)
            
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                issues.append({
                    "file": str(rel_path),
                    "level": "error",
                    "type": "read_error",
                    "msg": str(e),
                })
                continue
            
            # 1. Frontmatter check
            if not content.startswith("---"):
                issues.append({
                    "file": str(rel_path),
                    "level": "error",
                    "type": "missing_frontmatter",
                    "msg": "Thiếu frontmatter YAML (---)",
                })
                continue
            
            fm_str = content.split("---", 2)[1] if content.count("---") >= 2 else ""
            try:
                fm = yaml.safe_load(fm_str) or {}
            except yaml.YAMLError as e:
                issues.append({
                    "file": str(rel_path),
                    "level": "error",
                    "type": "invalid_yaml",
                    "msg": f"YAML frontmatter lỗi: {e}",
                })
                continue
            
            # 2. Required fields
            for field in REQUIRED_FRONTMATTER:
                if field not in fm or not fm[field]:
                    issues.append({
                        "file": str(rel_path),
                        "level": "warning",
                        "type": "missing_field",
                        "msg": f"Thiếu field '{field}' trong frontmatter",
                    })
            
            # 3. Category validation
            category = fm.get("category", "")
            if category and category not in VALID_CATEGORIES:
                issues.append({
                    "file": str(rel_path),
                    "level": "warning",
                    "type": "invalid_category",
                    "msg": f"Category không hợp lệ: '{category}'. Hợp lệ: {VALID_CATEGORIES}",
                })
            
            # 4. Confidence validation
            confidence = fm.get("confidence", "")
            if confidence and confidence not in VALID_CONFIDENCE:
                issues.append({
                    "file": str(rel_path),
                    "level": "warning",
                    "type": "invalid_confidence",
                    "msg": f"Confidence không hợp lệ: '{confidence}'",
                })
            
            # 5. Empty content check
            body = content.split("---", 2)[-1].strip() if content.count("---") >= 2 else content.strip()
            if len(body) < 100:
                issues.append({
                    "file": str(rel_path),
                    "level": "warning",
                    "type": "too_short",
                    "msg": f"Nội dung quá ngắn ({len(body)} chars) — cần bổ sung",
                })
            
            # 6. Broken image links (relative paths only)
            for match in re.finditer(r'!\[.*?\]\(([^)]+)\)', content):
                img_src = match.group(1)
                if img_src.startswith(("http://", "https://", "data:")):
                    continue
                abs_img = (fpath.parent / img_src).resolve()
                if not abs_img.exists():
                    issues.append({
                        "file": str(rel_path),
                        "level": "warning",
                        "type": "broken_image",
                        "msg": f"Ảnh không tồn tại: {img_src}",
                    })
            
            # 7. Outdated check (updated > 60 ngày)
            updated_str = fm.get("updated", "")
            if updated_str:
                try:
                    updated_date = datetime.strptime(str(updated_str), "%Y-%m-%d")
                    age_days = (datetime.now() - updated_date).days
                    if age_days > 60:
                        issues.append({
                            "file": str(rel_path),
                            "level": "info",
                            "type": "outdated",
                            "msg": f"Chưa cập nhật {age_days} ngày (updated: {updated_str})",
                        })
                except:
                    pass
    
    return issues

def send_telegram_alert(message: str):
    """Gửi alert qua Telegram nếu có issues."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    
    if not token or not admin_id:
        print("[WARN] Telegram credentials not set")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(url, json={
            "chat_id": admin_id,
            "text": message,
            "parse_mode": "Markdown",
        }, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")

def format_report(issues: list[dict]) -> str:
    """Format report để gửi Telegram."""
    if not issues:
        return "✅ *Syntax Check* — Wiki OK, không có lỗi"
    
    errors = [i for i in issues if i["level"] == "error"]
    warnings = [i for i in issues if i["level"] == "warning"]
    infos = [i for i in issues if i["level"] == "info"]
    
    lines = [f"⚠️ *Syntax Check Report* — {datetime.now().strftime('%Y-%m-%d')}"]
    
    if errors:
        lines.append(f"\n🔴 *Lỗi nghiêm trọng ({len(errors)}):*")
        for i in errors[:5]:
            lines.append(f"• `{i['file']}`: {i['msg']}")
        if len(errors) > 5:
            lines.append(f"  _(và {len(errors)-5} lỗi khác)_")
    
    if warnings:
        lines.append(f"\n🟡 *Cảnh báo ({len(warnings)}):*")
        for i in warnings[:5]:
            lines.append(f"• `{i['file']}`: {i['msg']}")
        if len(warnings) > 5:
            lines.append(f"  _(và {len(warnings)-5} cảnh báo khác)_")
    
    if infos:
        lines.append(f"\n🔵 *Thông tin ({len(infos)}):*")
        for i in infos[:3]:
            lines.append(f"• `{i['file']}`: {i['msg']}")
    
    return "\n".join(lines)

def main():
    wiki_dir = WIKI_ROOT / "wiki"
    print(f"[SYNTAX-CHECK] Checking {wiki_dir}...")
    
    issues = check_wiki_files(wiki_dir)
    
    # Lưu log
    log_file = WIKI_ROOT / "logs" / f"syntax-check-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({
            "ts": datetime.now(timezone.utc).isoformat(),
            "total_issues": len(issues),
            "errors": len([i for i in issues if i["level"] == "error"]),
            "warnings": len([i for i in issues if i["level"] == "warning"]),
            "issues": issues,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[DONE] {len(issues)} issues found. Log: {log_file}")
    
    # Chỉ alert nếu có lỗi/cảnh báo
    if issues:
        report = format_report(issues)
        print(report)
        
        # Gửi Telegram alert (chỉ nếu có errors/warnings, không gửi nếu chỉ có info)
        actionable = [i for i in issues if i["level"] in ("error", "warning")]
        if actionable:
            send_telegram_alert(report)
    else:
        print("✅ Wiki OK — no issues")

if __name__ == "__main__":
    main()
```

---

## 5.5 Setup Cron Job

```bash
# Mở crontab
crontab -e

# Thêm dòng này:
0 6 * * * cd /home/openclaw/wiki && /usr/bin/python3 tools/syntax_check.py >> /home/openclaw/wiki/logs/syntax-check-cron.log 2>&1
```

### Kiểm tra cron đã set

```bash
crontab -l | grep syntax
```

---

## 5.6 Test Syntax Check

```bash
# Test bình thường
python tools/syntax_check.py

# Test với lỗi giả: tạo file thiếu frontmatter
echo "# Test file without frontmatter" > wiki/test-broken.md
python tools/syntax_check.py
# → Phải thấy warning "Thiếu frontmatter"

# Xóa file test
rm wiki/test-broken.md
```

---

## DEFINITION OF DONE — PHASE 1 (MkDocs + Syntax Check)

- [ ] `mkdocs serve` chạy OK, wiki hiển thị đầy đủ
- [ ] `mkdocs build` không lỗi
- [ ] `syntax_check.py` chạy OK, không có false positives
- [ ] Cron `0 6 * * *` đã set
- [ ] Test với file lỗi: Telegram alert đến đúng
- [ ] Commit mkdocs.yml + tools/syntax_check.py

```bash
git add mkdocs.yml tools/syntax_check.py
git commit -m "feat(phase-1): MkDocs Material + syntax check cron

- mkdocs.yml: Material theme, Vietnamese, navigation
- syntax_check.py: frontmatter, images, outdated, empty content
- cron: daily 06:00 with Telegram alerts"
```

---

## TIẾP THEO

→ [06-phase2-intelligence.md](06-phase2-intelligence.md) — Vision extract + Lint + Ground Truth

# Bước 4: Pipeline Ingest + Compile + /duyet

> **Phase:** 1
> **Ước lượng:** 4-6 giờ
> **Prerequisite:** Phase 0.5 hoàn thành (bot query chạy)
> **Output:** Bot tự nhận URL/text → compile → draft → admin /duyet → publish

---

## CHECKLIST

- [ ] 4.1 Skill ingest-raw: nhận URL + text từ Telegram
- [ ] 4.2 Skill compile-wiki: raw → claims → wiki draft (auto)
- [ ] 4.3 Command /duyet: admin approve draft → publish
- [ ] 4.4 Command /xem-draft: xem danh sách draft pending
- [ ] 4.5 Update agents.yaml (bật skills mới)
- [ ] 4.6 Test end-to-end pipeline
- [ ] 4.7 Build snapshot v0.2

---

## 4.1 Skill ingest-raw

### skills/ingest-raw/SKILL.md

```yaml
---
name: ingest-raw
description: Nhận URL hoặc text thô từ admin Telegram, lưu vào raw/ để compile sau. Dùng khi cần thêm tài liệu mới vào wiki.
version: "1.0"
phase: "1"
admin_only: true
triggers:
  - command: /them
---

# ingest-raw

## Mô tả
Crawl URL hoặc nhận text paste, lưu vào raw/ với metadata.
Sau khi ingest, bot hỏi admin có muốn compile ngay không.

## Input
- /them [URL]: crawl webpage
- /them text: sau đó paste nội dung trong message tiếp theo

## Output
- File trong raw/website-crawl/ hoặc raw/manual/
- Notification Telegram + nút "Compile ngay"
```

### skills/ingest-raw/scripts/ingest.py

```python
#!/usr/bin/env python3
"""
ingest-raw skill: nhận URL hoặc text → lưu raw/
"""
import os
import sys
import re
import requests
import html2text
import yaml
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

RAW_DIR = WIKI_ROOT / "raw"
TODAY = datetime.now(timezone.utc).strftime("%Y%m%d")

def is_url(text: str) -> bool:
    return text.strip().startswith(("http://", "https://"))

def crawl_url(url: str) -> tuple[str, str]:
    """Crawl URL → (markdown_content, suggested_category)"""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BKNSWikiBot/1.0)"}
    
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0
    content = converter.handle(resp.text)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Guess category từ URL
    url_lower = url.lower()
    if "hosting" in url_lower:
        category = "hosting"
    elif "vps" in url_lower:
        category = "vps"
    elif "ten-mien" in url_lower or "domain" in url_lower:
        category = "ten-mien"
    elif "email" in url_lower:
        category = "email"
    elif "ssl" in url_lower:
        category = "ssl"
    elif "ho-tro" in url_lower or "support" in url_lower:
        category = "support"
    else:
        category = "general"
    
    return content, category

def save_raw(content: str, source_url: str, category: str, raw_type: str = "website-crawl") -> Path:
    """Lưu content vào raw/"""
    subdir = RAW_DIR / raw_type
    subdir.mkdir(parents=True, exist_ok=True)
    
    # Tạo tên file từ category + date
    filename = f"{category}-{TODAY}.md"
    filepath = subdir / filename
    
    # Tránh ghi đè: thêm suffix nếu đã tồn tại
    counter = 1
    while filepath.exists():
        filename = f"{category}-{TODAY}-{counter:02d}.md"
        filepath = subdir / filename
        counter += 1
    
    header = f"""---
source_url: {source_url}
crawled_at: {datetime.now(timezone.utc).isoformat()}
content_type: {raw_type}
category: {category}
status: pending_extract
---

"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)
    
    return filepath

def main():
    """Entry point từ OpenClaw với args: [url_or_text]"""
    input_text = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else sys.stdin.read().strip()
    
    if not input_text:
        print("Vui lòng cung cấp URL hoặc text. Ví dụ: /them https://bkns.vn/hosting")
        sys.exit(0)
    
    if is_url(input_text):
        url = input_text.split()[0]  # Lấy URL đầu tiên
        print(f"🔍 Đang crawl: {url}")
        
        try:
            content, category = crawl_url(url)
            filepath = save_raw(content, url, category, "website-crawl")
            
            print(f"✅ Đã lưu vào {filepath.relative_to(WIKI_ROOT)}")
            print(f"   Category: {category} | ~{len(content)//4} tokens")
            print(f"\nGõ /compile để biên dịch vào wiki, hoặc /xem-draft để xem pending drafts.")
        
        except Exception as e:
            print(f"❌ Lỗi crawl: {e}")
            print("Bạn có thể paste nội dung thủ công bằng /them [nội dung text]")
    
    else:
        # Treat as raw text paste
        content = input_text
        category = "manual"
        filepath = save_raw(content, "manual-input", category, "manual")
        
        print(f"✅ Đã lưu text vào {filepath.relative_to(WIKI_ROOT)}")
        print(f"\nGõ /compile để biên dịch vào wiki.")

if __name__ == "__main__":
    main()
```

---

## 4.2 Skill compile-wiki

### skills/compile-wiki/SKILL.md

```yaml
---
name: compile-wiki
description: Biên dịch file raw/ pending thành wiki draft. Gọi khi admin muốn compile tài liệu mới, hoặc sau khi /them URL thành công.
version: "1.0"
phase: "1"
admin_only: true
triggers:
  - command: /compile
---

# compile-wiki

## Mô tả
Lấy file raw/ có status=pending_extract, dùng Gemini Pro compile thành wiki draft trong wiki/.drafts/

## Input
- /compile: compile tất cả pending
- /compile [filename]: compile 1 file cụ thể

## Output
- Wiki draft trong wiki/.drafts/[category]/
- Claims YAML + JSONL trong claims/
- Telegram notification với preview

## Model
- gemini-2.5-pro (cần accuracy cao cho compile)
```

### skills/compile-wiki/scripts/compile.py

```python
#!/usr/bin/env python3
"""
compile-wiki skill: raw → claims → wiki draft
"""
import os
import sys
import json
import yaml
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

COMPILE_PROMPT = """Bạn là thủ thư biên tập wiki BKNS. Nhiệm vụ: từ tài liệu thô, tạo 2 output:

1. CLAIMS YAML: Danh sách facts có cấu trúc (cho database claims/)
2. WIKI MARKDOWN: Trang wiki Markdown cho người đọc

INPUT DOCUMENT:
{raw_content}

---

OUTPUT FORMAT:
Trả về 2 phần, phân cách bởi dòng "---WIKI---":

Phần 1 (trước ---WIKI---): YAML array các claims
Phần 2 (sau ---WIKI---): Markdown wiki page

QUY TẮC CLAIMS:
- Mỗi fact = 1 claim riêng biệt
- Giữ nguyên số liệu, đơn vị
- confidence: high (từ bảng giá rõ ràng) / medium (mô tả chung) / low (suy diễn)
- entity_id từ danh sách: ENT-PROD-HOSTING|VPS|DOMAIN|EMAIL|SSL|ENT-COMPANY-001

QUY TẮC WIKI:
- Frontmatter: title, category, updated, source, confidence
- Không bịa thông tin không có trong tài liệu
- Đánh dấu thiếu: > ⚠️ Cần bổ sung: [gì]
- Ngắn gọn, dễ đọc, dùng bảng cho pricing

Ngày hôm nay: {today}
"""

def get_pending_raw_files(specific_file: str = None) -> list[Path]:
    """Lấy danh sách file raw/ cần compile."""
    if specific_file:
        f = WIKI_ROOT / specific_file
        return [f] if f.exists() else []
    
    raw_dirs = [
        WIKI_ROOT / "raw" / "website-crawl",
        WIKI_ROOT / "raw" / "manual",
    ]
    
    pending = []
    for d in raw_dirs:
        for f in d.glob("*.md"):
            with open(f, "r", encoding="utf-8") as fp:
                content = fp.read()
            if "status: pending_extract" in content:
                pending.append(f)
    
    return pending

def compile_raw_file(raw_file: Path) -> dict:
    """Compile 1 file raw → claims + wiki draft."""
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # Parse header
    parts = raw_text.split("---\n", 2)
    if len(parts) >= 3:
        header = yaml.safe_load(parts[1])
        content = parts[2]
    else:
        header = {}
        content = raw_text
    
    source_url = header.get("source_url", "unknown")
    category = header.get("category", "general")
    
    model = GenerativeModel(model_name=os.getenv("MODEL_COMPILE", "gemini-2.5-pro"))
    prompt = COMPILE_PROMPT.format(
        raw_content=content[:60000],
        today=TODAY,
    )
    
    response = model.generate_content(prompt)
    output = response.text
    
    # Split claims + wiki
    if "---WIKI---" in output:
        claims_yaml_str, wiki_md = output.split("---WIKI---", 1)
    else:
        # Fallback: toàn bộ là wiki
        claims_yaml_str = ""
        wiki_md = output
    
    # Parse claims
    claims = []
    try:
        claims = yaml.safe_load(claims_yaml_str.strip()) or []
        if not isinstance(claims, list):
            claims = [claims] if claims else []
    except Exception as e:
        print(f"  [WARN] Claims parse error: {e}")
    
    # Thêm metadata cho claims
    now = datetime.now(timezone.utc).isoformat()
    for claim in claims:
        claim["source_url"] = source_url
        claim["extracted_at"] = now
        claim["raw_file"] = str(raw_file)
        claim["status"] = "pending"
    
    # Lưu claims
    save_claims(claims, category, raw_file)
    
    # Lưu wiki draft
    draft_path = save_wiki_draft(wiki_md.strip(), category, source_url)
    
    # Update raw file status
    update_raw_status(raw_file, "compiled", str(draft_path))
    
    return {
        "claims_count": len(claims),
        "draft_path": draft_path,
        "category": category,
    }

def save_claims(claims: list, category: str, raw_file: Path):
    entity_map = {
        "hosting": "ENT-PROD-HOSTING",
        "vps": "ENT-PROD-VPS",
        "ten-mien": "ENT-PROD-DOMAIN",
        "email": "ENT-PROD-EMAIL",
        "ssl": "ENT-PROD-SSL",
    }
    
    for claim in claims:
        claim_id = claim.get("claim_id", f"CLM-{category.upper()}-{datetime.now().strftime('%H%M%S')}")
        claim["claim_id"] = claim_id
        
        subdir = category if category in entity_map else "general"
        claims_dir = WIKI_ROOT / "claims" / "products" / subdir
        claims_dir.mkdir(parents=True, exist_ok=True)
        
        safe_id = claim_id.lower().replace("-", "_")
        yaml_file = claims_dir / f"{safe_id}.yaml"
        jsonl_file = claims_dir / f"{safe_id}.jsonl"
        
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(claim, f, allow_unicode=True, default_flow_style=False)
        
        trace = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": "compiled",
            "claim_id": claim_id,
            "raw_file": str(raw_file),
        }
        with open(jsonl_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")

def save_wiki_draft(wiki_md: str, category: str, source_url: str) -> Path:
    draft_dir = WIKI_ROOT / "wiki" / ".drafts" / "products" / category
    if category in ("support", "company"):
        draft_dir = WIKI_ROOT / "wiki" / ".drafts" / category
    draft_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"draft-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    draft_path = draft_dir / filename
    
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(wiki_md)
    
    return draft_path

def update_raw_status(raw_file: Path, status: str, draft_path: str):
    with open(raw_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("status: pending_extract", f"status: {status}")
    content = content.replace("---\n\n", f"---\ncompiled_to: {draft_path}\n\n", 1)
    
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    specific = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else None
    
    pending = get_pending_raw_files(specific)
    
    if not pending:
        print("✅ Không có file pending. Dùng /them [URL] để thêm tài liệu mới.")
        return
    
    print(f"📚 Tìm thấy {len(pending)} file cần compile...")
    
    for raw_file in pending:
        print(f"\n⚙️ Đang compile: {raw_file.name}...")
        try:
            result = compile_raw_file(raw_file)
            draft_rel = Path(result["draft_path"]).relative_to(WIKI_ROOT)
            print(f"✅ Xong: {len(result['claims_count']) if isinstance(result['claims_count'], list) else result['claims_count']} claims + draft tại {draft_rel}")
            print(f"\nDraft sẵn sàng review. Gõ /duyet {draft_rel.name} để publish.")
        except Exception as e:
            print(f"❌ Lỗi compile {raw_file.name}: {e}")

if __name__ == "__main__":
    main()
```

---

## 4.3 Command /duyet + /xem-draft

### skills/compile-wiki/scripts/review.py

```python
#!/usr/bin/env python3
"""
/duyet và /xem-draft commands
/duyet [filename]: approve draft → move to wiki/
/xem-draft: list pending drafts
"""
import os
import sys
import json
import shutil
import yaml
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

ADMIN_ID = os.getenv("ADMIN_TELEGRAM_ID", "")

def list_drafts() -> str:
    """Liệt kê tất cả draft pending."""
    drafts_dir = WIKI_ROOT / "wiki" / ".drafts"
    
    if not drafts_dir.exists():
        return "📭 Không có draft nào đang chờ review."
    
    drafts = list(drafts_dir.rglob("*.md"))
    
    if not drafts:
        return "📭 Không có draft nào đang chờ review."
    
    lines = [f"📋 **{len(drafts)} draft đang chờ review:**\n"]
    for d in drafts:
        rel = d.relative_to(drafts_dir)
        size = d.stat().st_size
        mtime = datetime.fromtimestamp(d.stat().st_mtime).strftime("%m-%d %H:%M")
        lines.append(f"• `{rel.name}` ({mtime}, {size} bytes)")
    
    lines.append(f"\nDùng `/duyet <tên_file>` để approve.")
    return "\n".join(lines)

def approve_draft(filename: str, approved_by: str) -> str:
    """Approve draft: move từ .drafts/ → wiki/ chính thức."""
    drafts_dir = WIKI_ROOT / "wiki" / ".drafts"
    
    # Tìm file
    matches = list(drafts_dir.rglob(filename))
    if not matches:
        return f"❌ Không tìm thấy draft: {filename}"
    
    draft_path = matches[0]
    
    # Đọc frontmatter để xác định đích
    with open(draft_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    category = "general"
    title = filename
    try:
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            category = fm.get("category", "general")
            title = fm.get("title", filename)
    except:
        pass
    
    # Xác định thư mục đích
    cat_map = {
        "hosting": "products/hosting",
        "vps": "products/vps",
        "ten-mien": "products/ten-mien",
        "email": "products/email",
        "ssl": "products/ssl",
        "support": "support",
        "company": "company",
    }
    target_dir = WIKI_ROOT / "wiki" / cat_map.get(category, "general")
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Tên file target (dùng tên có nghĩa)
    safe_title = title.lower().replace(" ", "-").replace("/", "-")[:50]
    target_path = target_dir / f"{safe_title}.md"
    
    # Tránh ghi đè file cũ: backup hoặc versioning
    if target_path.exists():
        backup = target_path.with_suffix(f".backup-{datetime.now().strftime('%Y%m%d')}.md")
        shutil.move(str(target_path), str(backup))
    
    # Move draft → wiki
    shutil.move(str(draft_path), str(target_path))
    
    # Update frontmatter: thêm approved info
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Insert approved metadata vào frontmatter
    now = datetime.now(timezone.utc).isoformat()
    content = content.replace(
        "---\n",
        f"---\napproved_by: {approved_by}\napproved_at: {now}\n",
        1
    )
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # Log approval
    log_file = WIKI_ROOT / "logs" / f"approvals-{datetime.now().strftime('%Y-%m')}.jsonl"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": now,
            "action": "approved",
            "draft": filename,
            "published": str(target_path.relative_to(WIKI_ROOT)),
            "category": category,
            "approved_by": approved_by,
        }, ensure_ascii=False) + "\n")
    
    rel_target = target_path.relative_to(WIKI_ROOT)
    return f"""✅ **Draft đã được duyệt!**

📄 Published: `{rel_target}`
📁 Category: {category}
👤 Approved by: {approved_by}

🔄 Wiki sẽ được reload khi có query tiếp theo.
💡 Gõ `/compile` để tiếp tục compile các draft khác."""

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if command == "list" or not command:
        print(list_drafts())
    elif command == "approve" and args:
        filename = args[0]
        approved_by = args[1] if len(args) > 1 else "admin"
        print(approve_draft(filename, approved_by))
    else:
        print("Usage: review.py list | review.py approve <filename> [approved_by]")

if __name__ == "__main__":
    main()
```

---

## 4.4 Update agents.yaml (bật skills mới)

```yaml
# agents.yaml — thêm skills mới
skills:
  - skills/query-wiki/SKILL.md
  - skills/ingest-raw/SKILL.md      # Thêm dòng này
  - skills/compile-wiki/SKILL.md    # Thêm dòng này
```

---

## 4.5 Test End-to-End Pipeline

```bash
# Test thủ công
echo "=== Test ingest URL ==="
python skills/ingest-raw/scripts/ingest.py "https://bkns.vn/hosting"

echo "=== Test compile ==="
python skills/compile-wiki/scripts/compile.py

echo "=== Xem drafts ==="
python skills/compile-wiki/scripts/review.py list

echo "=== Test duyet (thay tên file thực) ==="
# python skills/compile-wiki/scripts/review.py approve "draft-20260404-120000.md" "phamduytam"
```

---

## 4.6 Build Snapshot v0.2

```bash
cd /home/openclaw/wiki

# Rebuild wiki token count
WIKI_FILES=$(find wiki/ -name "*.md" -not -path "wiki/.drafts/*" | wc -l)
WIKI_CHARS=$(find wiki/ -name "*.md" -not -path "wiki/.drafts/*" -exec cat {} \; | wc -c)
WIKI_TOKENS=$(echo "scale=0; $WIKI_CHARS / 4" | bc)

cat > build/active-build.yaml << EOF
build_id: v0.2
build_date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
description: Phase 1 - Automation pipeline active
wiki_files: $WIKI_FILES
wiki_token_estimate: $WIKI_TOKENS
git_tag: build/v0.2
status: active
EOF

mkdir -p build/snapshots/v0.2
cp build/active-build.yaml build/snapshots/v0.2/manifest.yaml

git add skills/ingest-raw/ skills/compile-wiki/ build/ agents.yaml
git commit -m "feat(phase-1): ingest + compile + review pipeline

- ingest-raw: /them [URL] → raw/
- compile-wiki: /compile → draft in wiki/.drafts/
- review: /duyet → publish to wiki/
- agents.yaml: skills enabled
- Build v0.2"

git tag build/v0.2
```

---

## DEFINITION OF DONE — PHASE 1 (Pipeline)

- [ ] `/them [URL]` → file xuất hiện trong `raw/website-crawl/`
- [ ] `/compile` → draft xuất hiện trong `wiki/.drafts/`
- [ ] `/xem-draft` → liệt kê đúng drafts
- [ ] `/duyet [filename]` → file move sang `wiki/products/...`
- [ ] Claim YAML + JSONL được tạo khi compile
- [ ] Build v0.2 + git tag

---

## TIẾP THEO

→ [05-mkdocs-syntax-check.md](05-mkdocs-syntax-check.md) — MkDocs viewer + syntax check cron

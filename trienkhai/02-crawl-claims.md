# Bước 2: Crawl bkns.vn + Tạo Claims

> **Phase:** 0.5 — Tuần 1
> **Ước lượng:** 3-4 giờ
> **Prerequisite:** Bước 1 hoàn thành, Python + pip
> **Output:** raw/ + claims/ + entities updated

---

## CHECKLIST

- [ ] 2.1 Cài dependencies crawl
- [ ] 2.2 Script crawl bkns.vn → raw/
- [ ] 2.3 Script extract claims từ raw → claims/ YAML + JSONL
- [ ] 2.4 Update sources/registry.yaml (last_crawled)
- [ ] 2.5 Update entities/registry.yaml (nếu cần)
- [ ] 2.6 Update claims/registry.yaml
- [ ] 2.7 Commit raw + claims

---

## 2.1 Cài Dependencies

```bash
cd /home/openclaw/wiki
pip install requests html2text pyyaml python-dotenv vertexai google-cloud-aiplatform
```

---

## 2.2 Script Crawl bkns.vn

Tạo file `tools/crawl_bkns.py`:

```python
#!/usr/bin/env python3
"""
Crawl bkns.vn và lưu vào raw/website-crawl/
Chạy: python tools/crawl_bkns.py
"""
import os
import re
import requests
import html2text
from datetime import datetime, timezone
from pathlib import Path

WIKI_ROOT = Path("/home/openclaw/wiki")
RAW_DIR = WIKI_ROOT / "raw" / "website-crawl"
TODAY = datetime.now(timezone.utc).strftime("%Y%m%d")

# Danh sách trang cần crawl
PAGES = [
    {
        "id": "company-home",
        "url": "https://bkns.vn",
        "source_id": "SRC-BKNS-WEB-001",
        "category": "company",
    },
    {
        "id": "hosting",
        "url": "https://bkns.vn/hosting",
        "source_id": "SRC-BKNS-WEB-HOSTING",
        "category": "hosting",
    },
    {
        "id": "vps",
        "url": "https://bkns.vn/vps",
        "source_id": "SRC-BKNS-WEB-VPS",
        "category": "vps",
    },
    {
        "id": "ten-mien",
        "url": "https://bkns.vn/ten-mien",
        "source_id": "SRC-BKNS-WEB-DOMAIN",
        "category": "ten-mien",
    },
    {
        "id": "support",
        "url": "https://bkns.vn/ho-tro",
        "source_id": "SRC-BKNS-WEB-SUPPORT",
        "category": "support",
    },
]

def crawl_page(page: dict) -> str | None:
    """Crawl một trang, trả về Markdown text."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; BKNSWikiBot/1.0; +internal)"
    }
    try:
        resp = requests.get(page["url"], headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        
        # HTML → Markdown
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0
        md_content = converter.handle(resp.text)
        
        # Giảm xuống tối đa 50 dòng trống liên tiếp
        md_content = re.sub(r'\n{4,}', '\n\n\n', md_content)
        
        return md_content
    except Exception as e:
        print(f"[ERROR] Cannot crawl {page['url']}: {e}")
        return None

def save_raw(page: dict, content: str):
    """Lưu content với metadata header vào raw/website-crawl/"""
    filename = f"{page['id']}-{TODAY}.md"
    filepath = RAW_DIR / filename
    
    header = f"""---
source_id: {page['source_id']}
source_url: {page['url']}
crawled_at: {datetime.now(timezone.utc).isoformat()}
content_type: webpage
category: {page['category']}
status: pending_extract
---

"""
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + content)
    
    print(f"[OK] Saved: {filepath} ({len(content)} chars)")
    return filepath

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    results = []
    for page in PAGES:
        print(f"[CRAWL] {page['url']}...")
        content = crawl_page(page)
        if content:
            filepath = save_raw(page, content)
            results.append({"page": page["id"], "file": str(filepath), "ok": True})
        else:
            results.append({"page": page["id"], "ok": False})
    
    print(f"\n[DONE] {sum(r['ok'] for r in results)}/{len(PAGES)} pages crawled")
    print("Tiếp theo: chạy tools/extract_claims.py")

if __name__ == "__main__":
    main()
```

```bash
mkdir -p tools
python tools/crawl_bkns.py
```

> ⚠️ Nếu bkns.vn block bot (403/cloudflare), thay bằng requests_html hoặc playwright headless, hoặc crawl thủ công + paste vào raw/manual/.

---

## 2.3 Script Extract Claims

Tạo file `tools/extract_claims.py`:

```python
#!/usr/bin/env python3
"""
Extract claims từ raw/ → claims/ YAML + JSONL
Sử dụng Gemini Flash để extract
Chạy: python tools/extract_claims.py
"""
import os
import json
import yaml
import glob
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/home/openclaw/wiki/.env")

import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part

WIKI_ROOT = Path("/home/openclaw/wiki")

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

EXTRACT_PROMPT = """Bạn là chuyên gia extract dữ liệu có cấu trúc. Từ tài liệu thô về BKNS bên dưới, hãy extract TẤT CẢ facts quan trọng theo format YAML.

Mỗi claim phải bao gồm:
- claim_id: CLM-[CATEGORY]-[NNN] (VD: CLM-HOST-001)
- entity_id: [entity từ danh sách]
- attribute: loại thông tin (pricing / specs / policy / contact / description)
- value: giá trị cụ thể (giữ nguyên đơn vị tiền tệ, thông số kỹ thuật)
- source_url: URL nguồn
- confidence: high / medium / low
- notes: ghi chú nếu có (optional)

Entities hợp lệ:
- ENT-COMPANY-001 (BKNS company info)
- ENT-PROD-HOSTING (shared hosting)
- ENT-PROD-VPS (VPS)
- ENT-PROD-DOMAIN (tên miền)
- ENT-PROD-EMAIL (email hosting)
- ENT-PROD-SSL (SSL)

QUY TẮC:
1. KHÔNG tự suy diễn giá, thông số không có trong tài liệu
2. Nếu giá có range → ghi cả range
3. Nếu không chắc chắn → confidence: low
4. Mỗi gói sản phẩm = 1 claim riêng
5. Thông tin liên hệ = claim riêng (attribute: contact)

Output: YAML array thuần túy, không có markdown fence, không giải thích.

DOCUMENT:
{content}
"""

def extract_claims_from_raw(raw_file: Path) -> list[dict]:
    """Extract claims từ 1 file raw."""
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # Tách header khỏi content
    parts = raw_text.split("---\n", 2)
    if len(parts) >= 3:
        header_yaml = parts[1]
        content = parts[2]
        header = yaml.safe_load(header_yaml)
    else:
        content = raw_text
        header = {}
    
    source_url = header.get("source_url", "unknown")
    category = header.get("category", "general")
    
    model = GenerativeModel(model_name=os.getenv("MODEL_INGEST", "gemini-2.5-flash"))
    
    prompt = EXTRACT_PROMPT.format(content=content[:50000])  # Giới hạn 50k chars
    
    try:
        response = model.generate_content(prompt)
        claims_yaml = response.text.strip()
        
        # Parse YAML
        claims = yaml.safe_load(claims_yaml)
        if not isinstance(claims, list):
            claims = [claims] if claims else []
        
        # Thêm metadata
        now = datetime.now(timezone.utc).isoformat()
        for claim in claims:
            claim["source_url"] = source_url
            claim["extracted_at"] = now
            claim["raw_file"] = str(raw_file)
            claim["status"] = "pending"
            claim["reviewed_by"] = None
            claim["approved_at"] = None
        
        return claims
    
    except Exception as e:
        print(f"[ERROR] Extract failed for {raw_file}: {e}")
        return []

def save_claim(claim: dict, category: str):
    """Lưu claim vào YAML + JSONL."""
    claim_id = claim.get("claim_id", "CLM-UNKNOWN-001")
    
    # Xác định thư mục từ entity
    entity_map = {
        "ENT-PROD-HOSTING": "hosting",
        "ENT-PROD-VPS": "vps",
        "ENT-PROD-DOMAIN": "ten-mien",
        "ENT-PROD-EMAIL": "email",
        "ENT-PROD-SSL": "ssl",
        "ENT-COMPANY-001": "company",
    }
    entity_id = claim.get("entity_id", "")
    subdir = entity_map.get(entity_id, category)
    
    claims_dir = WIKI_ROOT / "claims" / "products" / subdir
    if subdir == "company":
        claims_dir = WIKI_ROOT / "claims" / "company"
    claims_dir.mkdir(parents=True, exist_ok=True)
    
    # Tên file từ claim_id
    safe_id = claim_id.lower().replace("-", "_")
    yaml_file = claims_dir / f"{safe_id}.yaml"
    jsonl_file = claims_dir / f"{safe_id}.jsonl"
    
    # Lưu YAML (approved version — dùng khi status = approved)
    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(claim, f, allow_unicode=True, default_flow_style=False)
    
    # Append JSONL trace
    trace = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": "extracted",
        "claim_id": claim_id,
        "source_url": claim.get("source_url"),
        "raw_file": claim.get("raw_file"),
        "confidence": claim.get("confidence"),
    }
    with open(jsonl_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace, ensure_ascii=False) + "\n")
    
    print(f"  [CLAIM] {claim_id} → {yaml_file}")

def main():
    raw_files = list((WIKI_ROOT / "raw" / "website-crawl").glob("*.md"))
    raw_files += list((WIKI_ROOT / "raw" / "manual").glob("*.md"))
    
    if not raw_files:
        print("[ERROR] Không tìm thấy file trong raw/. Chạy crawl trước.")
        return
    
    all_claims = []
    
    for raw_file in raw_files:
        print(f"\n[EXTRACT] {raw_file.name}...")
        
        # Đọc category từ header
        with open(raw_file, "r") as f:
            text = f.read()
        parts = text.split("---\n", 2)
        category = "general"
        if len(parts) >= 3:
            try:
                header = yaml.safe_load(parts[1])
                category = header.get("category", "general")
            except:
                pass
        
        claims = extract_claims_from_raw(raw_file)
        print(f"  → {len(claims)} claims extracted")
        
        for claim in claims:
            save_claim(claim, category)
            all_claims.append(claim)
    
    # Update claims/registry.yaml
    registry_file = WIKI_ROOT / "claims" / "registry.yaml"
    registry = {"claims": []}
    for claim in all_claims:
        registry["claims"].append({
            "claim_id": claim.get("claim_id"),
            "entity_id": claim.get("entity_id"),
            "attribute": claim.get("attribute"),
            "status": "pending",
            "created_at": claim.get("extracted_at", "").split("T")[0],
        })
    
    with open(registry_file, "w", encoding="utf-8") as f:
        yaml.dump(registry, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\n[DONE] {len(all_claims)} claims extracted")
    print(f"[DONE] Registry updated: {registry_file}")
    print("\nTiếp theo: Review claims trong claims/ rồi chạy tools/compile_wiki.py")

if __name__ == "__main__":
    main()
```

```bash
python tools/extract_claims.py
```

---

## 2.4 Ví Dụ Claim YAML Output

Sau khi chạy extract, file `claims/products/hosting/clm_host_001.yaml` trông như sau:

```yaml
claim_id: CLM-HOST-001
entity_id: ENT-PROD-HOSTING
attribute: pricing
value:
  basic:
    name: "Hosting Basic"
    price_monthly: "36.000đ/tháng"
    price_yearly: "432.000đ/năm"
    storage: "1GB SSD"
    bandwidth: "Unlimited"
  business:
    name: "Hosting Business"
    price_monthly: "89.000đ/tháng"
    price_yearly: "1.068.000đ/năm"
    storage: "5GB SSD"
    bandwidth: "Unlimited"
source_url: https://bkns.vn/hosting
extracted_at: "2026-04-04T10:00:00Z"
raw_file: raw/website-crawl/hosting-20260404.md
status: pending
confidence: high
reviewed_by: null
approved_at: null
notes: "Giá chưa bao gồm VAT"
```

---

## 2.5 Kiểm Tra Thủ Công Sau Extract

Trước khi chuyển sang compile, review nhanh:

```bash
# Xem tất cả claims đã tạo
ls claims/products/*/

# Xem 1 claim cụ thể
cat claims/products/hosting/clm_host_001.yaml

# Đếm số claims
find claims/ -name "*.yaml" -not -name "registry.yaml" | wc -l
```

> ⚠️ **Quan trọng:** Tại bước này claims có `status: pending`. Bot KHÔNG dùng pending claims cho wiki. Cần admin approve (bước sau trong Phase 1). Ở Phase 0.5, bạn compile thủ công từ claims.

---

## 2.6 Commit

```bash
cd /home/openclaw/wiki

# Update sources registry (last_crawled dates)
# (Cập nhật thủ công trong sources/registry.yaml)

git add raw/website-crawl/ claims/ sources/registry.yaml entities/registry.yaml
git commit -m "feat(data): crawl bkns.vn + extract claims

- Crawled: company, hosting, VPS, ten-mien, support
- Extracted: [N] claims (pending review)
- Sources registry: last_crawled updated
- Claims registry: updated"

git tag data/v0.1-raw
```

---

## DEFINITION OF DONE

- [ ] `raw/website-crawl/` có ≥5 file .md
- [ ] `claims/products/` có ≥10 claim YAML files
- [ ] `claims/registry.yaml` có ≥10 entries
- [ ] Mỗi claim có: claim_id, entity_id, attribute, value, source_url, confidence
- [ ] Không có file YAML lỗi (test: `python -c "import yaml; yaml.safe_load(open('claims/products/hosting/clm_host_001.yaml'))"`)

---

## TIẾP THEO

→ [03-bot-query.md](03-bot-query.md) — Build query-wiki skill + Telegram bot

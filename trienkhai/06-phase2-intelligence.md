# Bước 6: Phase 2 — Vision + Lint + Ground Truth

> **Phase:** 2
> **Ước lượng:** 6-8 giờ (chia thành 3 session nhỏ)
> **Prerequisite:** Phase 1 hoàn thành, wiki có ≥20 files
> **Output:** Bot nhận ảnh bảng giá + lint tự động + ground truth checker

---

## CHIA SESSION — Thực hiện từng phần riêng biệt

| Session | Nội dung | Thời gian |
|---------|----------|-----------|
| **6A** | ingest-image: vision extract từ ảnh | 2-3 giờ |
| **6B** | lint-wiki: kiểm tra mâu thuẫn LLM | 2-3 giờ |
| **6C** | ground-truth-check: crawl + compare | 2-3 giờ |

---

# SESSION 6A: ingest-image — Vision Extract

## CHECKLIST 6A

- [ ] 6A.1 Skill ingest-image: SKILL.md
- [ ] 6A.2 Script image_ingest.py (Vision + Git LFS)
- [ ] 6A.3 Test với ảnh bảng giá thực

### skills/ingest-image/SKILL.md

```yaml
---
name: ingest-image
description: Nhận ảnh bảng giá từ Telegram, extract thành Markdown table dùng Gemini Vision, tạo claim draft cho admin review.
version: "1.0"
phase: "2"
admin_only: true
triggers:
  - type: image
    caption_pattern: ".*bang.gia.*|.*price.*|.*gia.*"
  - command: /anh
---

# ingest-image

## Mô tả
Nhận ảnh (screenshot bảng giá, catalog, specs) → Vision extract → Claim draft → /duyet

## Input
- Gửi ảnh kèm caption "bảng giá" hoặc /anh
- Hỗ trợ: JPG, PNG, WebP

## Output  
- Original → assets/evidence/price-screens/ (Git LFS)
- Thumbnail → assets/images/
- Claim draft → wiki/.drafts/ (chờ /duyet)
```

### skills/ingest-image/scripts/image_ingest.py

```python
#!/usr/bin/env python3
"""
ingest-image skill: ảnh → Vision extract → claim draft
"""
import os
import sys
import json
import yaml
import base64
import shutil
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

WIKI_ROOT = Path("/home/openclaw/wiki")
load_dotenv(WIKI_ROOT / ".env")

import vertexai
from vertexai.generative_models import GenerativeModel, Part, Image

vertexai.init(
    project=os.getenv("VERTEX_PROJECT_ID"),
    location=os.getenv("VERTEX_LOCATION", "us-central1"),
)

VISION_EXTRACT_PROMPT = """Extract toàn bộ nội dung có cấu trúc từ ảnh này.

YÊU CẦU:
1. Giữ nguyên đơn vị tiền tệ (chuẩn hóa về "đ" hoặc "VND")
2. Giữ nguyên tên gói, mã gói, thông số kỹ thuật
3. Nếu có nhiều bảng → nhiều section với heading riêng
4. Ô không đọc được → ghi **[KHÔNG RÕ]**
5. KHÔNG suy diễn giá trị bị che/mờ
6. Sau mỗi bảng, thêm dòng metadata

OUTPUT FORMAT:
---
extracted_from: [tên ảnh]
extracted_at: [timestamp]
---

## [Tên bảng/section]
| Cột 1 | Cột 2 | ... |
|-------|-------|-----|
| ... | ... | ... |

*Nguồn: extract từ ảnh, cần verify với bkns.vn*
"""

def compress_image(src_path: Path, dest_path: Path, max_size: int = 800):
    """Tạo thumbnail nhỏ hơn. Cần pillow."""
    try:
        from PIL import Image as PILImage
        img = PILImage.open(src_path)
        img.thumbnail((max_size, max_size), PILImage.LANCZOS)
        img.save(dest_path, optimize=True, quality=85)
    except ImportError:
        # Nếu không có pillow, copy nguyên bản
        shutil.copy2(src_path, dest_path)

def extract_from_image(image_path: Path) -> str:
    """Dùng Gemini Vision extract content từ ảnh."""
    model = GenerativeModel(
        model_name=os.getenv("MODEL_INGEST", "gemini-2.5-flash")
    )
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Detect MIME type
    ext = image_path.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", 
                ".png": "image/png", ".webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")
    
    image_part = Part.from_data(data=image_data, mime_type=mime_type)
    
    response = model.generate_content([image_part, VISION_EXTRACT_PROMPT])
    return response.text

def ingest_image(image_path: Path, category: str = "general") -> dict:
    """
    Full pipeline: lưu evidence → extract → tạo draft claim
    Returns dict với paths và extracted content
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    stem = f"img-{category}-{timestamp}"
    
    # 1. Lưu original vào evidence (Git LFS)
    evidence_dir = WIKI_ROOT / "assets" / "evidence" / "price-screens"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{stem}{image_path.suffix}"
    shutil.copy2(image_path, evidence_path)
    
    # 2. Tạo thumbnail
    images_dir = WIKI_ROOT / "assets" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = images_dir / f"{stem}-thumb.jpg"
    compress_image(image_path, thumb_path)
    
    print(f"  [IMG] Saved evidence: {evidence_path.relative_to(WIKI_ROOT)}")
    print(f"  [IMG] Thumbnail: {thumb_path.relative_to(WIKI_ROOT)}")
    
    # 3. Vision extract
    print("  [VISION] Extracting content...")
    extracted_content = extract_from_image(image_path)
    
    # 4. Tạo claim draft YAML
    claim = {
        "claim_id": f"CLM-IMG-{timestamp}",
        "entity_id": f"ENT-PROD-{category.upper().replace('-', '_')}",
        "attribute": "pricing_from_image",
        "value": extracted_content,
        "source_type": "image",
        "evidence_file": str(evidence_path.relative_to(WIKI_ROOT)),
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "confidence": "medium",  # Ảnh cần verify
        "notes": "Extracted từ ảnh — cần verify với bkns.vn trước khi approve",
    }
    
    # 5. Lưu draft wiki
    draft_dir = WIKI_ROOT / "wiki" / ".drafts" / "products" / category
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_path = draft_dir / f"img-extract-{timestamp}.md"
    
    thumb_rel = thumb_path.relative_to(WIKI_ROOT / "wiki") if False else f"../../assets/images/{stem}-thumb.jpg"
    
    draft_content = f"""---
title: Bảng giá từ ảnh — {category} ({timestamp})
category: {category}
updated: {datetime.now().strftime('%Y-%m-%d')}
source: image-extract
confidence: medium
evidence: {str(evidence_path.relative_to(WIKI_ROOT))}
---

> ⚠️ **Cần verify:** Nội dung này được extract từ ảnh bằng AI. Vui lòng kiểm tra lại với bkns.vn trước khi approve.

## Extracted Content

{extracted_content}

---
*Ảnh gốc: {evidence_path.name} | Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft_content)
    
    # 6. Lưu claim YAML
    claims_dir = WIKI_ROOT / "claims" / "products" / category
    claims_dir.mkdir(parents=True, exist_ok=True)
    claim_file = claims_dir / f"clm_img_{timestamp}.yaml"
    
    with open(claim_file, "w", encoding="utf-8") as f:
        yaml.dump(claim, f, allow_unicode=True, default_flow_style=False)
    
    return {
        "evidence": str(evidence_path),
        "thumbnail": str(thumb_path),
        "draft": str(draft_path),
        "claim_file": str(claim_file),
        "extracted_preview": extracted_content[:300],
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: image_ingest.py <image_path> [category]")
        print("Categories: hosting, vps, ten-mien, email, ssl")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    category = sys.argv[2] if len(sys.argv) > 2 else "general"
    
    if not image_path.exists():
        print(f"❌ File không tồn tại: {image_path}")
        sys.exit(1)
    
    print(f"📸 Processing image: {image_path.name}")
    result = ingest_image(image_path, category)
    
    draft_rel = Path(result["draft"]).relative_to(WIKI_ROOT)
    
    print(f"""
✅ Ảnh đã được xử lý!

📋 Nội dung extract:
{result['extracted_preview']}...

📄 Draft tại: {draft_rel}
🔍 Cần verify với bkns.vn trước khi duyệt.

Gõ /duyet {Path(result['draft']).name} để approve sau khi verify.
""")

if __name__ == "__main__":
    main()
```

---

# SESSION 6B: lint-wiki — Kiểm Tra Mâu Thuẫn

## CHECKLIST 6B

- [ ] 6B.1 Skill lint-wiki: SKILL.md
- [ ] 6B.2 Script lint.py (Gemini Pro)
- [ ] 6B.3 Cron Monday 09:00

### skills/lint-wiki/scripts/lint.py

```python
#!/usr/bin/env python3
"""
lint-wiki: dùng Gemini Pro kiểm tra mâu thuẫn trong wiki
Chạy: python skills/lint-wiki/scripts/lint.py
"""
import os
import sys
import json
import requests
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

LINT_PROMPT = """Bạn là kiểm toán viên chất lượng wiki BKNS. Đọc toàn bộ wiki và kiểm tra kỹ:

## 1. MÂU THUẪN GIÁ [🔴 Critical — phải sửa ngay]
- Tìm TẤT CẢ giá tiền được đề cập
- Nếu cùng sản phẩm/gói có giá khác nhau ở 2+ file → báo cáo
- Format: [File A: giá X] vs [File B: giá Y] cho [Sản phẩm Z]

## 2. THÔNG TIN CÓ THỂ LỖI THỜI [🟡 Warning]  
- File có ngày `updated:` > 30 ngày trước hôm nay ({today})
- Giá/thông số kỹ thuật không có ngày verify
- Chính sách có thể đã thay đổi

## 3. THIẾU NGUỒN TRÍCH DẪN [🟠 Medium]
- Bảng giá không có `source:` URL
- Claim về pricing/specs không có citation

## 4. ORPHAN FILES [🔵 Info]
- File không được link từ index.md hoặc file nào khác

## 5. ĐỀ XUẤT CẢI THIỆN [💡 Top 5]
- Nội dung thiếu nhất
- Cấu trúc cần cải thiện

---

WIKI CONTENT:
{wiki_content}

---

OUTPUT FORMAT (bắt buộc):
# Báo Cáo Lint — {today}

## 🔴 Mâu thuẫn giá (sửa ngay)
[liệt kê hoặc ✅ Không phát hiện mâu thuẫn]

## 🟡 Thông tin cần verify
[liệt kê file + lý do]

## 🟠 Thiếu nguồn trích dẫn
[liệt kê hoặc ✅ OK]

## 🔵 Orphan files
[liệt kê hoặc ✅ OK]

## 💡 Đề xuất cải thiện (top 5)
1. ...
"""

def load_wiki_for_lint() -> str:
    """Load wiki content cho lint (bao gồm cả metadata)."""
    wiki_dir = WIKI_ROOT / "wiki"
    texts = []
    
    for root, dirs, files in os.walk(wiki_dir):
        dirs[:] = [d for d in sorted(dirs) if d != ".drafts"]
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            fpath = Path(root) / fname
            rel_path = fpath.relative_to(wiki_dir)
            with open(fpath, "r", encoding="utf-8") as f:
                texts.append(f"\n\n=== FILE: {rel_path} ===\n{f.read()}")
    
    return "\n".join(texts)

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if not token or not admin_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": admin_id,
            "text": message[:4000],  # Telegram limit
            "parse_mode": "Markdown",
        }, timeout=10)
    except Exception as e:
        print(f"[WARN] Telegram send failed: {e}")

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[LINT] Running wiki lint for {today}...")
    
    wiki_content = load_wiki_for_lint()
    token_estimate = len(wiki_content) // 4
    print(f"[LINT] Wiki size: ~{token_estimate} tokens")
    
    model = GenerativeModel(model_name=os.getenv("MODEL_LINT", "gemini-2.5-pro"))
    
    prompt = LINT_PROMPT.format(wiki_content=wiki_content, today=today)
    
    response = model.generate_content(prompt)
    report = response.text
    
    # Lưu report
    log_dir = WIKI_ROOT / "logs" / "lint"
    log_dir.mkdir(parents=True, exist_ok=True)
    report_file = log_dir / f"report-{today}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Log token usage
    usage = response.usage_metadata
    cached = getattr(usage, 'cached_content_token_count', 0)
    total = getattr(usage, 'prompt_token_count', 0)
    
    with open(WIKI_ROOT / "logs" / "lint-log.jsonl", "a") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "date": today,
            "total_tokens": total,
            "cached_tokens": cached,
            "report_file": str(report_file),
        }, ensure_ascii=False) + "\n")
    
    print(f"[LINT] Report saved: {report_file}")
    print(f"[LINT] Tokens: {total} (cached: {cached})")
    
    # Gửi summary qua Telegram
    # Lấy 20 dòng đầu báo cáo
    summary = "\n".join(report.split("\n")[:20])
    telegram_msg = f"📊 *Wiki Lint Report — {today}*\n\n{summary}\n\n_Full report: logs/lint/report-{today}.md_"
    send_telegram(telegram_msg)
    
    print("[LINT] Done. Report sent to Telegram.")

if __name__ == "__main__":
    main()
```

### Cron cho lint (Monday 09:00)

```bash
# Thêm vào crontab:
0 9 * * 1 cd /home/openclaw/wiki && /usr/bin/python3 skills/lint-wiki/scripts/lint.py >> /home/openclaw/wiki/logs/lint-cron.log 2>&1
```

---

# SESSION 6C: ground-truth-check — Cross-check với bkns.vn

## CHECKLIST 6C

- [ ] 6C.1 Script ground_truth.py (crawl + LLM compare)
- [ ] 6C.2 Cron weekly
- [ ] 6C.3 Test với 1 sản phẩm

### tools/ground_truth.py

```python
#!/usr/bin/env python3
"""
ground-truth-check: crawl lại bkns.vn, so sánh với claims hiện tại
Chạy: python tools/ground_truth.py
"""
import os
import re
import json
import yaml
import requests
import html2text
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

COMPARE_PROMPT = """Bạn là kiểm tra viên độc lập. So sánh dữ liệu wiki hiện tại với dữ liệu mới crawl từ website bkns.vn.

WIKI HIỆN TẠI (claims đã approve):
{current_claims}

DỮ LIỆU MỚI TỪ WEBSITE:
{fresh_data}

NHIỆM VỤ:
1. Tìm MỌI sự khác biệt về GIÁ (dù nhỏ)
2. Tìm thông số kỹ thuật đã thay đổi
3. Tìm sản phẩm mới hoặc đã ngừng kinh doanh
4. Tìm thay đổi chính sách quan trọng

OUTPUT FORMAT:
## Kết quả Ground Truth Check — {today}

### 🔴 GIÁ THAY ĐỔI (cần cập nhật wiki ngay):
[Liệt kê: Sản phẩm X: Wiki ghi Y → Thực tế Z]
Hoặc: ✅ Không phát hiện thay đổi giá

### 🟠 THÔNG SỐ KỸ THUẬT THAY ĐỔI:
[Liệt kê hoặc ✅ OK]

### 🟡 SẢN PHẨM MỚI/NGỪNG:
[Liệt kê hoặc ✅ Không có]

### 🔵 THAY ĐỔI CHÍNH SÁCH:
[Liệt kê hoặc ✅ Không có]

### KHUYẾN NGHỊ:
[Hành động cần làm]

Ngày hôm nay: {today}
"""

CHECK_PAGES = [
    {"url": "https://bkns.vn/hosting", "category": "hosting", "entity": "ENT-PROD-HOSTING"},
    {"url": "https://bkns.vn/vps", "category": "vps", "entity": "ENT-PROD-VPS"},
    {"url": "https://bkns.vn/ten-mien", "category": "ten-mien", "entity": "ENT-PROD-DOMAIN"},
]

def crawl_fresh(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BKNSGroundTruth/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "utf-8"
        converter = html2text.HTML2Text()
        converter.ignore_images = True
        converter.body_width = 0
        content = converter.handle(resp.text)
        return re.sub(r'\n{4,}', '\n\n\n', content)[:30000]
    except Exception as e:
        return f"[ERROR crawling {url}: {e}]"

def load_approved_claims(entity_id: str) -> str:
    """Load claims đã approve cho entity."""
    claims_dir = WIKI_ROOT / "claims"
    
    category_map = {
        "ENT-PROD-HOSTING": "products/hosting",
        "ENT-PROD-VPS": "products/vps",
        "ENT-PROD-DOMAIN": "products/ten-mien",
    }
    
    subdir = category_map.get(entity_id, "products")
    claims_path = WIKI_ROOT / "claims" / subdir
    
    approved = []
    if claims_path.exists():
        for f in claims_path.glob("*.yaml"):
            if f.name == "registry.yaml":
                continue
            try:
                claim = yaml.safe_load(open(f, "r", encoding="utf-8"))
                if claim and claim.get("status") == "approved":
                    approved.append(claim)
            except:
                pass
    
    return yaml.dump(approved, allow_unicode=True, default_flow_style=False) if approved else "Chưa có claims approved"

def send_telegram(message: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if not token or not admin_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": admin_id,
            "text": message[:4000],
            "parse_mode": "Markdown",
        }, timeout=10)
    except Exception as e:
        print(f"[WARN] Telegram: {e}")

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[GROUND-TRUTH] Running check for {today}...")
    
    model = GenerativeModel(model_name=os.getenv("MODEL_INGEST", "gemini-2.5-flash"))
    
    all_reports = [f"# Ground Truth Report — {today}\n"]
    has_critical = False
    
    for page in CHECK_PAGES:
        print(f"  [CHECK] {page['url']}...")
        
        fresh_data = crawl_fresh(page["url"])
        current_claims = load_approved_claims(page["entity"])
        
        prompt = COMPARE_PROMPT.format(
            current_claims=current_claims,
            fresh_data=fresh_data,
            today=today,
        )
        
        response = model.generate_content(prompt)
        report_section = f"\n## {page['category'].upper()}\n{response.text}"
        all_reports.append(report_section)
        
        if "🔴" in response.text:
            has_critical = True
    
    full_report = "\n".join(all_reports)
    
    # Lưu report
    log_dir = WIKI_ROOT / "logs" / "ground-truth"
    log_dir.mkdir(parents=True, exist_ok=True)
    report_file = log_dir / f"report-{today}.md"
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(full_report)
    
    print(f"[GROUND-TRUTH] Report saved: {report_file}")
    
    # Gửi Telegram
    prefix = "🚨 *CẢNH BÁO: Phát hiện thay đổi giá!*\n\n" if has_critical else "✅ *Ground Truth Check*\n\n"
    summary = "\n".join(full_report.split("\n")[:30])
    send_telegram(f"{prefix}{summary}\n\n_Full: logs/ground-truth/report-{today}.md_")

if __name__ == "__main__":
    main()
```

### Cron weekly (Sunday 08:00)

```bash
# Thêm vào crontab:
0 8 * * 0 cd /home/openclaw/wiki && /usr/bin/python3 tools/ground_truth.py >> /home/openclaw/wiki/logs/ground-truth-cron.log 2>&1
```

---

## Commit Phase 2

```bash
cd /home/openclaw/wiki

git add skills/ingest-image/ skills/lint-wiki/ tools/ground_truth.py
git commit -m "feat(phase-2): intelligence layer

- ingest-image: Vision extract từ ảnh bảng giá → draft
- lint-wiki: LLM kiểm tra mâu thuẫn (weekly cron Mon 09:00)
- ground-truth-check: crawl bkns.vn weekly (Sun 08:00)
- agents.yaml: enable new skills"

git tag phase/2-complete
```

---

## DEFINITION OF DONE — PHASE 2

- [ ] `/anh` + ảnh bảng giá → draft tạo thành công
- [ ] `lint.py` chạy OK, report có cấu trúc đúng
- [ ] `ground_truth.py` chạy OK, so sánh được claims vs website
- [ ] Cron lint (Mon 09:00) + ground truth (Sun 08:00) đã set
- [ ] Telegram alerts hoạt động cho cả 3 skills

---

## TIẾP THEO

→ [07-phase3-enterprise.md](07-phase3-enterprise.md) — Onboarding + Auto-file + Observability

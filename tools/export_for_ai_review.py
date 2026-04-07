#!/usr/bin/env python3
"""
BKNS Wiki — Export for AI Review

Exports a structured review package that can be fed to
Claude, GPT, or NotebookLM for cross-verification.

Usage:
    python3 tools/export_for_ai_review.py                    # Export all
    python3 tools/export_for_ai_review.py --category hosting # Specific
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import CLAIMS_APPROVED_DIR, WIKI_DIR, WORKSPACE
from lib.utils import ensure_dir, read_text_safe

VN_TZ = timezone(timedelta(hours=7))
EXPORT_DIR = WORKSPACE / "exports"
CATEGORIES = ["hosting", "vps", "email", "ssl", "ten-mien", "server", "software"]


def export_category(category: str) -> dict:
    """Export a single category's data for AI review."""
    cat_dir = f"products/{category}"
    
    # Collect claims
    claims_dir = CLAIMS_APPROVED_DIR / cat_dir
    claims = []
    if claims_dir.exists():
        for f in sorted(claims_dir.glob("*.yaml")):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    claim = yaml.safe_load(fh)
                if claim:
                    claims.append(claim)
            except Exception:
                continue
    
    # Collect wiki pages
    wiki_dir = WIKI_DIR / cat_dir
    pages = {}
    if wiki_dir.exists():
        for f in sorted(wiki_dir.rglob("*.md")):
            rel = str(f.relative_to(wiki_dir))
            pages[rel] = read_text_safe(str(f))
    
    return {"claims": claims, "pages": pages}


def generate_review_prompt(category: str, data: dict) -> str:
    """Generate a comprehensive review prompt for the AI reviewer."""
    gt_claims = [c for c in data["claims"] if c.get("confidence") == "ground_truth"]
    llm_claims = [c for c in data["claims"] if c.get("confidence") != "ground_truth"]
    
    prompt = f"""# BKNS Wiki Cross-Verification Request — {category.upper()}

## Vai trò
Bạn là chuyên gia kiểm duyệt nội dung cho wiki sản phẩm hosting/VPS/domain Việt Nam.
Nhiệm vụ: tìm MỌI sai sót, mâu thuẫn, và thông tin bịa đặt (hallucination) trong wiki draft.

## Nguồn dữ liệu
- **Ground Truth Claims ({len(gt_claims)})**: Dữ liệu chính xác 100% từ Excel bảng giá nội bộ BKNS
- **LLM-Extracted Claims ({len(llm_claims)})**: Dữ liệu trích xuất bởi AI từ tài liệu — CÓ THỂ SAI
- **Wiki Pages ({len(data['pages'])})**: Trang wiki đã compile — CẦN KIỂM TRA

## Checklist Kiểm Tra

### 1. Kiểm tra giá (QUAN TRỌNG NHẤT)
- Mỗi giá trong wiki phải khớp với Ground Truth claims
- Liệt kê mọi giá sai kèm giá đúng từ claims

### 2. Thông số kỹ thuật
- CPU, RAM, SSD có đúng cho từng gói không?
- Có claim nào tự bịa specs không?

### 3. Chính sách
- SLA, hoàn tiền, hỗ trợ — có đúng với claims không?
- Có thông tin chính sách nào BỊA ĐẶT (không có trong claims)?

### 4. Tính nhất quán
- Cùng sản phẩm ở 2 trang khác nhau → giá/specs phải giống
- Tên sản phẩm phải viết đúng format

### 5. Thông tin thiếu
- Claims nào CHƯA ĐƯỢC compile vào wiki?
- Có gói sản phẩm nào bị bỏ sót?

## OUTPUT FORMAT
```json
{{
  "accuracy_score": 0-100,
  "issues": [
    {{
      "type": "price_error|spec_error|hallucination|inconsistency|missing",
      "severity": "critical|high|medium|low",
      "page": "bang-gia.md",
      "detail": "...",
      "fix": "..."
    }}
  ],
  "summary": "Nhận xét tổng thể"
}}
```

---

## GROUND TRUTH CLAIMS (Source of Truth)

"""
    
    for c in gt_claims:
        prompt += f"- {c.get('entity_name', '')}: {c.get('attribute', '')} = {c.get('value', '')} {c.get('unit', '')} [{c.get('claim_id', '')}]\n"
    
    prompt += f"\n## LLM-EXTRACTED CLAIMS (Check these)\n\n"
    for c in llm_claims[:100]:  # Limit to avoid too-long prompt
        prompt += f"- {c.get('entity_name', '')}: {c.get('attribute', '')} = {c.get('value', '')} {c.get('unit', '')} (confidence: {c.get('confidence', '')})\n"
    
    prompt += f"\n## WIKI PAGES TO VERIFY\n\n"
    for page_name, page_content in data["pages"].items():
        prompt += f"### {page_name}\n\n{page_content}\n\n---\n\n"
    
    return prompt


def main():
    parser = argparse.ArgumentParser(description="Export BKNS Wiki for AI Review")
    parser.add_argument("--category", choices=CATEGORIES + ["all"], default="all")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()
    
    ensure_dir(EXPORT_DIR)
    
    categories = CATEGORIES if args.category == "all" else [args.category]
    
    for cat in categories:
        print(f"📦 Exporting {cat}...")
        data = export_category(cat)
        
        if not data["claims"] and not data["pages"]:
            print(f"   ⏭️ No data for {cat}")
            continue
        
        # Generate review prompt
        prompt = generate_review_prompt(cat, data)
        
        # Save
        out_file = EXPORT_DIR / f"review-{cat}.md"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(prompt)
        
        print(f"   ✅ {len(data['claims'])} claims + {len(data['pages'])} pages → {out_file}")
        
        # Also save claims as YAML for structured import
        claims_file = EXPORT_DIR / f"claims-{cat}.yaml"
        with open(claims_file, "w", encoding="utf-8") as f:
            yaml.dump(data["claims"], f, allow_unicode=True, default_flow_style=False)
        
        print(f"   📄 Claims YAML → {claims_file}")
    
    print(f"\n{'═' * 50}")
    print(f"📦 Export complete: {EXPORT_DIR}/")
    print(f"   → Upload review-*.md to Claude/GPT/NotebookLM for cross-verification")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BKNS Wiki — Extract Claims from Product Screenshots

Uses Gemini Vision to extract structured pricing & spec data
directly from product screenshot images (bkns.vn).

Usage:
    python3 tools/extract_from_images.py               # Extract all images
    python3 tools/extract_from_images.py --dry-run      # Preview only
    python3 tools/extract_from_images.py --dir hosting_gia_re  # Specific folder
"""
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.config import CLAIMS_APPROVED_DIR, WORKSPACE, MODEL_FLASH
from lib.gemini import generate_with_image
from lib.utils import ensure_dir, now_iso, today_str

VN_TZ = timezone(timedelta(hours=7))
IMAGES_DIR = WORKSPACE / "raw" / "images"

# Map folder names to hosting sub-categories
FOLDER_TO_CATEGORY = {
    "hosting_gia_re": ("products/hosting", "Hosting Giá Rẻ"),
    "hosting_wordpress": ("products/hosting", "WordPress Hosting"),
    "hosting_seo": ("products/hosting", "SEO Hosting"),
    "hosting_mien_phi": ("products/hosting", "Hosting Miễn Phí"),
    "Hosting_windows": ("products/hosting", "Hosting Windows"),
    "NVME_hosting": ("products/hosting", "NVMe Hosting"),
    "Reseller_hosting": ("products/hosting", "Reseller Hosting"),
}

EXTRACT_PROMPT = """Bạn là chuyên gia phân tích sản phẩm hosting.

Từ ảnh chụp màn hình bảng giá sản phẩm BKNS, hãy trích xuất TẤT CẢ thông tin dưới dạng JSON.

QUY TẮC:
- Mỗi gói sản phẩm = 1 object
- Giá ghi bằng số (VND), không format
- Thông số: CPU, RAM, SSD/Disk, Bandwidth, Domain count, etc.
- Ghi nhận giá khuyến mãi nếu khác giá gốc
- Ghi nhận chu kỳ thanh toán tối thiểu nếu có
- Đây là ảnh từ website bkns.vn — giá có thể đã được giảm

OUTPUT JSON array:
[
  {{
    "plan_code": "BKH01",
    "plan_name": "Hosting Giá Rẻ BKH01",
    "product_line": "{product_line}",
    "monthly_price": 19000,
    "monthly_price_note": "Giá hiển thị trên web, có thể đã bao gồm giảm giá",
    "min_period": "1 tháng",
    "specs": {{
      "cpu_cores": "1 Core",
      "ram": "1 GB",
      "storage": "1 GB SSD",
      "bandwidth": "Unlimited",
      "domain_count": 1
    }},
    "features": ["Backup hàng ngày", "Miễn phí SSL", "CloudLinux"],
    "yearly_price": null,
    "yearly_price_note": null
  }}
]

Trả về TẤT CẢ gói sản phẩm trong ảnh. Không bỏ sót."""


def extract_image(image_path: Path, product_line: str) -> list[dict]:
    """Extract product data from a single image using Gemini Vision."""
    prompt = EXTRACT_PROMPT.format(product_line=product_line)
    
    try:
        result = generate_with_image(
            image_path=str(image_path),
            prompt=prompt,
            model=MODEL_FLASH,
            skill="extract-images",
            temperature=0.1,
            max_output_tokens=8192,
        )
    except Exception as e:
        print(f"  ⚠️ Vision API error: {e}")
        return []
    
    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except (json.JSONDecodeError, AttributeError):
        pass
    
    return []


def _safe_id(s: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", s.lower()).strip("_")


def products_to_claims(products: list[dict], category: str, image_source: str) -> list[dict]:
    """Convert extracted products to claim YAML format."""
    claims = []
    ts = datetime.now(VN_TZ).isoformat()
    
    for p in products:
        plan_code = _safe_id(p.get("plan_code", "unknown"))
        plan_name = p.get("plan_name", p.get("plan_code", ""))
        product_line = _safe_id(p.get("product_line", ""))
        entity_id = f"product.hosting.{plan_code}"
        
        # Price claim
        if p.get("monthly_price"):
            claims.append({
                "claim_id": f"CLM-IMG-{entity_id}-website_price",
                "entity_id": entity_id,
                "entity_type": "product_plan",
                "entity_name": plan_name,
                "attribute": "website_price",
                "value": p["monthly_price"],
                "confidence": "high",
                "review_state": "approved",
                "risk_class": "verified",
                "source_ids": [f"IMG-{image_source}"],
                "observed_at": ts,
                "valid_from": today_str(),
                "approved_at": ts,
                "approved_by": "image-extraction",
                "unit": "VND",
                "qualifiers": {
                    "period": "1 tháng",
                    "source": "bkns.vn website screenshot",
                    "note": p.get("monthly_price_note", "Giá trên website"),
                },
                "compiler_note": f"Extracted from website screenshot ({image_source}), {plan_name}",
            })
        
        # Spec claims
        specs = p.get("specs", {})
        for attr, val in specs.items():
            if val is not None:
                claims.append({
                    "claim_id": f"CLM-IMG-{entity_id}-{attr}",
                    "entity_id": entity_id,
                    "entity_type": "product_plan",
                    "entity_name": plan_name,
                    "attribute": attr,
                    "value": val,
                    "confidence": "high",
                    "review_state": "approved",
                    "risk_class": "verified",
                    "source_ids": [f"IMG-{image_source}"],
                    "observed_at": ts,
                    "valid_from": today_str(),
                    "approved_at": ts,
                    "approved_by": "image-extraction",
                    "compiler_note": f"From bkns.vn screenshot ({image_source})",
                })
        
        # Feature claims
        features = p.get("features", [])
        if features:
            claims.append({
                "claim_id": f"CLM-IMG-{entity_id}-features",
                "entity_id": entity_id,
                "entity_type": "product_plan",
                "entity_name": plan_name,
                "attribute": "features",
                "value": ", ".join(features),
                "confidence": "high",
                "review_state": "approved",
                "risk_class": "verified",
                "source_ids": [f"IMG-{image_source}"],
                "observed_at": ts,
                "valid_from": today_str(),
                "approved_at": ts,
                "approved_by": "image-extraction",
                "compiler_note": f"Features from bkns.vn screenshot ({image_source})",
            })
        
        # Min period claim
        if p.get("min_period"):
            claims.append({
                "claim_id": f"CLM-IMG-{entity_id}-min_period",
                "entity_id": entity_id,
                "entity_type": "product_plan",
                "entity_name": plan_name,
                "attribute": "min_payment_period",
                "value": p["min_period"],
                "confidence": "high",
                "review_state": "approved",
                "risk_class": "verified",
                "source_ids": [f"IMG-{image_source}"],
                "observed_at": ts,
                "valid_from": today_str(),
                "approved_at": ts,
                "approved_by": "image-extraction",
                "compiler_note": f"Minimum payment period from bkns.vn ({image_source})",
            })
    
    return claims


def write_claims(claims: list[dict], category: str, dry_run: bool = False) -> int:
    """Write claims to YAML files."""
    cat_dir = CLAIMS_APPROVED_DIR / category
    ensure_dir(cat_dir)
    count = 0
    
    for claim in claims:
        safe_id = _safe_id(claim["claim_id"])
        if safe_id.startswith("clm_"):
            safe_id = safe_id[4:]
        filename = f"clm_{safe_id}.yaml"
        filepath = cat_dir / filename
        
        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.dump(claim, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        count += 1
    
    return count


def main():
    parser = argparse.ArgumentParser(description="Extract claims from product screenshots")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--dir", help="Specific image directory name")
    args = parser.parse_args()
    
    total_claims = 0
    total_products = 0
    
    folders = {}
    if args.dir:
        if args.dir in FOLDER_TO_CATEGORY:
            folders = {args.dir: FOLDER_TO_CATEGORY[args.dir]}
        else:
            print(f"❌ Unknown folder: {args.dir}")
            print(f"   Available: {', '.join(FOLDER_TO_CATEGORY.keys())}")
            return
    else:
        folders = FOLDER_TO_CATEGORY
    
    for folder_name, (category, product_line) in folders.items():
        folder = IMAGES_DIR / folder_name
        if not folder.exists():
            continue
        
        images = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.png"))
        if not images:
            continue
        
        print(f"\n📸 {product_line} ({len(images)} images)")
        
        for img in images:
            print(f"  🖼️  {img.name}...", end=" ", flush=True)
            
            products = extract_image(img, product_line)
            print(f"→ {len(products)} products")
            
            if products:
                claims = products_to_claims(products, category, img.stem)
                written = write_claims(claims, category, dry_run=args.dry_run)
                total_claims += written
                total_products += len(products)
                
                for p in products:
                    price = p.get("monthly_price", "?")
                    print(f"    → {p.get('plan_code', '?')}: {price:,}đ/tháng" if isinstance(price, int) else f"    → {p.get('plan_code', '?')}: {price}")
    
    print(f"\n{'═' * 50}")
    print(f"📊 Total: {total_products} products → {total_claims} claims")
    if args.dry_run:
        print(f"   (dry-run mode — no files written)")
    else:
        print(f"   ✅ Written to {CLAIMS_APPROVED_DIR}/")


if __name__ == "__main__":
    main()

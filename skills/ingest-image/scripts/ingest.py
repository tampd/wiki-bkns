#!/usr/bin/env python3
"""
BKNS Agent Wiki — ingest-image
Trích xuất dữ liệu từ ảnh (bảng giá, screenshot) → claims YAML.

Usage:
    python3 scripts/ingest.py /path/to/image.png
    python3 scripts/ingest.py --dir assets/evidence/price-screens/
"""
import sys
import json
import re
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import EVIDENCE_DIR, CLAIMS_DRAFTS_DIR, MODEL_FLASH
from lib.gemini import generate_with_image
from lib.logger import log_entry
from lib.telegram import notify_skill, notify_error
from lib.utils import (
    now_iso, today_str, generate_claim_id, ensure_dir,
    write_yaml, sha256_file,
)


IMAGE_PROMPT = """Bạn là chuyên gia OCR + data extraction cho BKNS.

Ảnh này chứa thông tin sản phẩm/dịch vụ BKNS (bảng giá, panel, tài liệu).

NHIỆM VỤ: Trích xuất MỌI thông tin có giá trị từ ảnh.

QUY TẮC:
1. ✅ Đọc CHÍNH XÁC số liệu từ ảnh (giá, thông số)
2. ❌ KHÔNG suy luận — chỉ extract những gì nhìn thấy rõ
3. ✅ Mỗi fact = 1 claim riêng
4. ✅ Nếu giá → ghi đơn vị (VND/tháng, VND/năm)
5. ✅ Nếu không đọc rõ → confidence = low

OUTPUT (JSON array):
[
  {{
    "entity_id": "product.hosting.plan_name",
    "entity_type": "product_plan",
    "entity_name": "Plan Name",
    "attribute": "monthly_price",
    "value": 26000,
    "unit": "VND",
    "qualifiers": {{"billing_cycle": "month"}},
    "confidence": "high",
    "risk_class": "high",
    "compiler_note": "Đọc từ bảng giá trong ảnh"
  }}
]"""


def ingest_image(image_path: str, category: str = "uncategorized") -> dict:
    """Extract structured data from image.

    Args:
        image_path: Path to image file
        category: Product category for claims

    Returns:
        Result dict
    """
    path = Path(image_path)
    if not path.exists():
        return {"status": "error", "detail": f"File not found: {image_path}"}

    log_entry("ingest-image", "start", f"Processing: {path.name}")

    # Copy evidence
    ensure_dir(EVIDENCE_DIR)
    evidence_name = f"{today_str()}-{path.name}"
    evidence_path = EVIDENCE_DIR / evidence_name
    shutil.copy2(str(path), str(evidence_path))

    # Call Vision API
    try:
        result = generate_with_image(
            image_path=str(path),
            prompt=IMAGE_PROMPT,
            model=MODEL_FLASH,
            skill="ingest-image",
            temperature=0.1,
        )
    except Exception as e:
        error_msg = f"Vision API error: {str(e)}"
        log_entry("ingest-image", "error", error_msg, severity="high")
        notify_error("ingest-image", error_msg)
        return {"status": "error", "detail": error_msg}

    # Parse claims
    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        claims = json.loads(match.group(0)) if match else []
    except (json.JSONDecodeError, AttributeError):
        claims = []

    if not claims:
        log_entry("ingest-image", "skip", "No claims extracted from image")
        return {"status": "skip", "detail": "Không đọc được dữ liệu từ ảnh"}

    # Save claims
    saved = 0
    image_hash = sha256_file(path)

    for claim_data in claims:
        claim_id = generate_claim_id(
            claim_data.get("entity_id", "unknown"),
            claim_data.get("attribute", "unknown"),
        )

        claim = {
            "claim_id": claim_id,
            "entity_id": claim_data.get("entity_id", ""),
            "entity_type": claim_data.get("entity_type", ""),
            "entity_name": claim_data.get("entity_name", ""),
            "attribute": claim_data.get("attribute", ""),
            "value": claim_data.get("value", ""),
            "unit": claim_data.get("unit", ""),
            "qualifiers": claim_data.get("qualifiers", {}),
            "source_ids": [f"IMG-{path.stem}"],
            "observed_at": now_iso(),
            "valid_from": today_str(),
            "confidence": claim_data.get("confidence", "medium"),
            "review_state": "drafted",
            "risk_class": claim_data.get("risk_class", "high"),
            "compiler_note": claim_data.get("compiler_note", ""),
            "evidence_image": str(evidence_path),
            "evidence_hash": image_hash,
        }

        cat_dir = CLAIMS_DRAFTS_DIR / "products" / category
        ensure_dir(cat_dir)
        fname = claim_id.lower().replace("-", "_") + ".yaml"
        write_yaml(claim, cat_dir / fname)
        saved += 1

    cost = result.get("cost_usd", 0)

    notify_skill("ingest-image",
                  f"Trích {saved} claims từ ảnh `{path.name}`\n"
                  f"Evidence: `{evidence_path}`\nCost: ${cost:.4f}",
                  severity="success")

    log_entry("ingest-image", "success",
              f"Extracted {saved} claims from {path.name}",
              cost_usd=cost)

    return {
        "status": "success",
        "claims_count": saved,
        "cost_usd": cost,
        "evidence": str(evidence_path),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Image Ingest")
    parser.add_argument("path", help="Image file or directory")
    parser.add_argument("--category", "-c", default="uncategorized")
    args = parser.parse_args()

    p = Path(args.path)
    if p.is_dir():
        for img in sorted(p.glob("*.png")) + sorted(p.glob("*.jpg")):
            print(f"\nProcessing: {img.name}")
            result = ingest_image(str(img), args.category)
            print(f"  → {result['status']}")
    else:
        result = ingest_image(str(p), args.category)
        print(f"Result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BKNS Agent Wiki — ground-truth
Xác minh wiki content vs live website data.

Usage:
    python3 scripts/verify.py           # Verify all categories
    python3 scripts/verify.py hosting   # Verify specific category
"""
import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from lib.config import (
    WIKI_DIR, RAW_CRAWL_DIR, LOGS_GROUND_TRUTH_DIR, MODEL_FLASH,
)
from lib.gemini import generate
from lib.logger import log_entry
from lib.telegram import send_report, notify_error
from lib.utils import (
    read_text_safe, today_str, now_iso, ensure_dir,
)


VERIFY_PROMPT = """Bạn là fact-checker cho BKNS Wiki.

WIKI HIỆN TẠI:
{wiki_content}

DỮ LIỆU LIVE (vừa crawl):
{live_content}

NHIỆM VỤ: So sánh wiki vs live data, tìm khác biệt.

KIỂM TRA:
1. Giá có thay đổi?
2. Gói sản phẩm mới/bị xóa?
3. Hotline/email có đổi?
4. Thông số kỹ thuật khác?
5. Chính sách thay đổi?

OUTPUT (JSON):
{{
  "status": "match" | "mismatch" | "partial",
  "changes": [
    {{
      "type": "price_change" | "new_product" | "removed" | "spec_change" | "contact_change",
      "entity": "entity name",
      "attribute": "attribute name",
      "wiki_value": "current wiki value",
      "live_value": "live website value",
      "severity": "critical" | "high" | "medium" | "low",
      "action": "update" | "investigate" | "ignore"
    }}
  ],
  "confidence": 0.0-1.0,
  "summary": "Tóm tắt kết quả"
}}

Nếu match → changes = []."""


def verify_category(category: str) -> dict:
    """Verify wiki content against latest crawl data.

    Args:
        category: Product category (hosting, vps, etc.)

    Returns:
        Verification result dict
    """
    log_entry("ground-truth", "start", f"Verifying: {category}")

    # Load wiki content
    wiki_path = WIKI_DIR / "products" / category / "tong-quan.md"
    wiki_content = read_text_safe(str(wiki_path))
    if not wiki_content:
        return {"status": "skip", "detail": f"No wiki page for {category}"}

    # Load latest crawl
    raw_files = sorted(RAW_CRAWL_DIR.glob(f"{category}-*.md"), reverse=True)
    if not raw_files:
        return {"status": "skip",
                "detail": f"No raw data for {category}. Run /them first."}

    live_content = read_text_safe(str(raw_files[0]))

    if not live_content or len(live_content) < 100:
        return {"status": "skip", "detail": "Live data quá ít hoặc bị Cloudflare block"}

    # Compare via Gemini
    prompt = VERIFY_PROMPT.format(
        wiki_content=wiki_content[:20000],
        live_content=live_content[:20000],
    )

    try:
        result = generate(
            prompt=prompt,
            model=MODEL_FLASH,
            skill="ground-truth",
            temperature=0.1,
            max_output_tokens=4096,
        )
    except Exception as e:
        error_msg = f"Verify error: {str(e)}"
        log_entry("ground-truth", "error", error_msg, severity="high")
        return {"status": "error", "detail": error_msg}

    # Parse result
    text = result["text"].strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        verification = json.loads(match.group(0)) if match else {}
    except (json.JSONDecodeError, AttributeError):
        verification = {"status": "error", "changes": [], "summary": "Parse error"}

    verification["cost_usd"] = result.get("cost_usd", 0)
    verification["category"] = category

    # Log result
    ensure_dir(LOGS_GROUND_TRUTH_DIR)
    log_path = LOGS_GROUND_TRUTH_DIR / f"{category}-{today_str()}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(verification, f, ensure_ascii=False, indent=2)

    # Alert if mismatches found
    changes = verification.get("changes", [])
    critical = [c for c in changes if c.get("severity") == "critical"]

    if critical:
        notify_error("ground-truth",
                      f"⚠️ {len(critical)} critical changes in {category}:\n" +
                      "\n".join(f"• {c['type']}: {c.get('attribute', '')} "
                                f"({c.get('wiki_value', '')} → {c.get('live_value', '')})"
                                for c in critical[:3]))
    elif changes:
        send_report(f"Ground Truth: {category}",
                     f"Status: {verification.get('status')}\n"
                     f"Changes: {len(changes)}\n"
                     f"Summary: {verification.get('summary', '')}")

    log_entry("ground-truth", "success",
              f"Verified {category}: {verification.get('status')} "
              f"({len(changes)} changes)",
              cost_usd=verification.get("cost_usd", 0))

    return verification


def verify_all() -> list[dict]:
    """Verify all product categories."""
    categories = ["hosting", "vps", "ten-mien", "email", "ssl"]
    results = []

    for cat in categories:
        print(f"\nVerifying: {cat}...")
        result = verify_category(cat)
        results.append(result)
        status = result.get("status", "unknown")
        print(f"  → {status}: {result.get('summary', result.get('detail', ''))}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BKNS Ground Truth")
    parser.add_argument("category", nargs="?", help="Category to verify")
    args = parser.parse_args()

    if args.category:
        result = verify_category(args.category)
        print(f"\nResult: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        verify_all()


if __name__ == "__main__":
    main()
